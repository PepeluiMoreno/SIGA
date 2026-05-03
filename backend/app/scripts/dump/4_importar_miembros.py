"""
Script para importar miembros desde MySQL directamente.

Importa las tablas:
- MIEMBRO → miembros
- miembro → información adicional (IBAN, agrupación)
- MIEMBROELIMINADO5ANIOS → miembros (con fecha_baja)
- miembroSFALLECIDOS → miembros (con motivo_baja='Fallecido')

IMPORTANTE:
- Encripta DNI/NIE e IBANs antes de almacenarlos
- Prioridad de teléfonos: móvil > fijo_casa > fijo_trabajo
- Profesión/estudios solo si es_voluntario=True
- Agrupación obtenida de tabla miembro
- Provincia inferida por código postal

Este script debe ejecutarse DESPUÉS de importar agrupaciones.
"""
import asyncio
import uuid
import re
from typing import Optional, Dict, Tuple
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from app.core.database import get_database_url
from app.infrastructure.services.encriptacion_service import get_encriptacion_service
from app.modules.miembros.models.miembro import Miembro, TipoMiembro
from app.modules.miembros.models.estado_miembro import EstadoMiembro
from app.modules.geografico.models.direccion import Provincia
from .mysql_helper import get_mysql_connection


class MapeadorMiembrosMySQL:
    """Mapea miembros de MySQL a PostgreSQL."""

    def __init__(self):
        self.mapeo_miembros: dict[int, uuid.UUID] = {}  # CODUSER → UUID
        self.servicio_encriptacion = get_encriptacion_service()
        self.tipo_miembro_miembro_id: Optional[uuid.UUID] = None
        self.tipo_miembro_simpatizante_id: Optional[uuid.UUID] = None
        self.tipo_miembro_voluntario_id: Optional[uuid.UUID] = None
        self.estado_activo_id: Optional[uuid.UUID] = None
        self.estado_baja_id: Optional[uuid.UUID] = None
        self.cache_provincias_por_cp: dict[str, uuid.UUID] = {}
        self.cache_agrupaciones: dict[str, uuid.UUID] = {}  # CODAGRUPACION → UUID

    @staticmethod
    def normalizar_nombre(nombre: Optional[str]) -> Optional[str]:
        """
        Normaliza nombres y apellidos: primera letra mayúscula, resto minúsculas.
        Ejemplos: 'JOSE LUIS' -> 'Jose Luis', 'GARCÍA' -> 'García'
        """
        if not nombre:
            return None

        nombre_str = str(nombre).strip()
        if not nombre_str or nombre_str.upper() in ('NULL', 'NONE'):
            return None

        # Convertir a minúsculas y capitalizar cada palabra
        return nombre_str.title()

    async def cargar_tipos_miembro(self, session: AsyncSession):
        """Carga los UUIDs de tipos de miembro."""
        print("\nCargando tipos de miembro...", flush=True)

        result = await session.execute(
            select(TipoMiembro).where(TipoMiembro.codigo == 'miembro')
        )
        tipo_miembro = result.scalar_one_or_none()
        if tipo_miembro:
            self.tipo_miembro_miembro_id = tipo_miembro.id

        result = await session.execute(
            select(TipoMiembro).where(TipoMiembro.codigo == 'SIMPATIZANTE')
        )
        tipo_simpatizante = result.scalar_one_or_none()
        if tipo_simpatizante:
            self.tipo_miembro_simpatizante_id = tipo_simpatizante.id

        result = await session.execute(
            select(TipoMiembro).where(TipoMiembro.codigo == 'VOLUNTARIO')
        )
        tipo_voluntario = result.scalar_one_or_none()
        if tipo_voluntario:
            self.tipo_miembro_voluntario_id = tipo_voluntario.id

        print(f"  Tipos de miembro cargados:")
        print(f"    miembro: {self.tipo_miembro_miembro_id}")
        print(f"    SIMPATIZANTE: {self.tipo_miembro_simpatizante_id}")
        print(f"    VOLUNTARIO: {self.tipo_miembro_voluntario_id}")

    async def cargar_estados_miembro(self, session: AsyncSession):
        """Carga los UUIDs de estados de miembro."""
        print("\nCargando estados de miembro...", flush=True)

        result = await session.execute(
            select(EstadoMiembro).where(EstadoMiembro.codigo == 'ACTIVO')
        )
        estado_activo = result.scalar_one_or_none()
        if estado_activo:
            self.estado_activo_id = estado_activo.id

        result = await session.execute(
            select(EstadoMiembro).where(EstadoMiembro.codigo == 'BAJA')
        )
        estado_baja = result.scalar_one_or_none()
        if estado_baja:
            self.estado_baja_id = estado_baja.id

        print(f"  Estados de miembro cargados:")
        print(f"    ACTIVO: {self.estado_activo_id}")
        print(f"    BAJA: {self.estado_baja_id}")

    async def cargar_cache_agrupaciones(self, session: AsyncSession):
        """Carga el cache de agrupaciones."""
        print("\nCargando cache de agrupaciones...", flush=True)

        result = await session.execute(
            text("""
                SELECT old_id, new_uuid
                FROM temp_id_mapping
                WHERE tabla = 'AGRUPACION'
            """)
        )

        for row in result:
            old_id = row[0]
            new_uuid = row[1]
            self.cache_agrupaciones[str(old_id)] = uuid.UUID(new_uuid) if isinstance(new_uuid, str) else new_uuid

        print(f"  [OK] {len(self.cache_agrupaciones)} agrupaciones en cache", flush=True)

    def mapear_tipo_miembro(self, tipomiembro: Optional[str]) -> uuid.UUID:
        """Mapea TIPOMIEMBRO de MySQL a tipo_miembro_id de PostgreSQL."""
        if not tipomiembro:
            return self.tipo_miembro_miembro_id

        tipo_lower = str(tipomiembro).lower().strip()

        if 'miembro' in tipo_lower or 'administrador' in tipo_lower:
            return self.tipo_miembro_miembro_id
        elif 'simpatizante' in tipo_lower:
            return self.tipo_miembro_simpatizante_id
        elif 'voluntario' in tipo_lower:
            return self.tipo_miembro_voluntario_id
        else:
            return self.tipo_miembro_miembro_id

    def procesar_telefonos(self, movil, fijo_casa, fijo_trabajo) -> Tuple[Optional[str], Optional[str]]:
        """
        Procesa teléfonos según prioridad: móvil > fijo_casa > fijo_trabajo.
        Retorna (telefono, telefono2).
        """
        telefonos = []

        if movil and str(movil).strip():
            telefonos.append(str(movil).strip())
        if fijo_casa and str(fijo_casa).strip():
            telefonos.append(str(fijo_casa).strip())
        if fijo_trabajo and str(fijo_trabajo).strip():
            telefonos.append(str(fijo_trabajo).strip())

        telefono = telefonos[0] if len(telefonos) > 0 else None
        telefono2 = telefonos[1] if len(telefonos) > 1 else None

        return telefono, telefono2

    async def obtener_uuid_pais(self, session: AsyncSession, codigo_pais) -> Optional[uuid.UUID]:
        """Obtiene el UUID de un país desde temp_id_mapping o por código ISO."""
        if not codigo_pais:
            return None

        # Si es un string (código ISO), buscar directamente en paises
        if isinstance(codigo_pais, str):
            from app.modules.geografico.models.direccion import Pais
            result = await session.execute(
                select(Pais).where(Pais.codigo == str(codigo_pais).strip().upper())
            )
            pais = result.scalar_one_or_none()
            return pais.id if pais else None

        # Si es un entero, buscar en temp_id_mapping
        result = await session.execute(
            text("""
                SELECT new_uuid FROM temp_id_mapping
                WHERE tabla = 'PAIS' AND old_id = :old_id
            """),
            {"old_id": codigo_pais}
        )
        row = result.fetchone()
        return uuid.UUID(row[0]) if row else None

    async def obtener_uuid_provincia(self, session: AsyncSession, codprov: Optional[int]) -> Optional[uuid.UUID]:
        """Obtiene el UUID de una provincia desde temp_id_mapping."""
        if not codprov:
            return None

        # Buscar en temp_id_mapping
        result = await session.execute(
            text("""
                SELECT new_uuid FROM temp_id_mapping
                WHERE tabla = 'PROVINCIA' AND old_id = :old_id
            """),
            {"old_id": codprov}
        )
        row = result.fetchone()
        return uuid.UUID(row[0]) if row else None

    async def obtener_uuid_agrupacion(self, session: AsyncSession, codagrupacion: Optional[str]) -> Optional[uuid.UUID]:
        """Obtiene el UUID de una agrupación desde cache o temp_id_mapping."""
        if not codagrupacion:
            return None

        codigo_str = str(codagrupacion).strip()

        # Intentar desde cache
        if codigo_str in self.cache_agrupaciones:
            return self.cache_agrupaciones[codigo_str]

        # Si no está en cache, buscar en temp_id_mapping
        result = await session.execute(
            text("""
                SELECT new_uuid FROM temp_id_mapping
                WHERE tabla = 'AGRUPACION' AND old_id = :old_id
            """),
            {"old_id": codigo_str}
        )
        row = result.fetchone()
        if row:
            uuid_agrup = uuid.UUID(row[0]) if isinstance(row[0], str) else row[0]
            self.cache_agrupaciones[codigo_str] = uuid_agrup
            return uuid_agrup

        return None

    def determinar_es_voluntario(self, colabora: Optional[str]) -> bool:
        """Determina si un miembro es voluntario basándose en el campo COLABORA."""
        if not colabora:
            return False

        colabora_str = str(colabora).strip().lower()
        return len(colabora_str) > 0 and colabora_str not in ('null', 'no', 'none', '')

    def parse_fecha(self, fecha_str) -> Optional[date]:
        """Parsea una fecha de MySQL."""
        if not fecha_str:
            return None

        if isinstance(fecha_str, date):
            if fecha_str.year == 1 or fecha_str.year == 0:  # Fecha inválida
                return None
            return fecha_str

        try:
            fecha_str_clean = str(fecha_str).strip()
            if fecha_str_clean in ('', 'NULL', '0000-00-00', 'None'):
                return None

            # Intentar parsear
            if '-' in fecha_str_clean:
                parts = fecha_str_clean.split('-')
                if len(parts) == 3:
                    year = int(parts[0])
                    if year == 0 or year == 1:
                        return None
                    return date(year, int(parts[1]), int(parts[2]))
        except (ValueError, AttributeError, IndexError):
            return None

        return None

    async def importar_miembros(self, pg_session: AsyncSession):
        """Importa miembros desde MySQL."""
        print("\nImportando miembros desde MySQL...", flush=True)

        importados = 0
        omitidos = 0
        errores = 0

        async with get_mysql_connection() as mysql_conn:
            async with mysql_conn.cursor() as cursor:
                # Query que hace JOIN entre MIEMBRO y miembro para obtener toda la información
                query = """
                    SELECT
                        m.CODUSER,
                        m.CODPAISDOC,
                        m.TIPOMIEMBRO,
                        m.NUMDOCUMENTOMIEMBRO,
                        m.TIPODOCUMENTOMIEMBRO,
                        m.APE1,
                        m.APE2,
                        m.NOM,
                        m.SEXO,
                        m.FECHANAC,
                        m.TELFIJOCASA,
                        m.TELFIJOTRABAJO,
                        m.TELMOVIL,
                        m.PROFESION,
                        m.ESTUDIOS,
                        m.EMAIL,
                        m.EMAILERROR,
                        m.COLABORA,
                        m.CODPAISDOM,
                        m.DIRECCION,
                        m.CP,
                        m.LOCALIDAD,
                        m.CODPROV,
                        m.COMENTARIOmiembro,
                        m.OBSERVACIONES,
                        s.CUENTAIBAN,
                        s.CODAGRUPACION,
                        s.FECHABAJA
                    FROM MIEMBRO m
                    LEFT JOIN miembro s ON m.CODUSER = s.CODUSER
                    ORDER BY m.CODUSER
                """

                await cursor.execute(query)

                while True:
                    rows = await cursor.fetchmany(100)  # Procesar en lotes de 100
                    if not rows:
                        break

                    for row in rows:
                        try:
                            coduser = row[0]
                            codpaisdoc = row[1]
                            tipomiembro = row[2]
                            numdocumentomiembro = row[3]
                            tipodocumentomiembro = row[4]
                            ape1 = row[5]
                            ape2 = row[6]
                            nom = row[7]
                            sexo = row[8]  # H=Hombre, M=Mujer
                            fechanac = row[9]
                            telfijocasa = row[10]
                            telfijotrabajo = row[11]
                            telmovil = row[12]
                            profesion = row[13]
                            estudios = row[14]
                            email = row[15]
                            emailerror = row[16]
                            colabora = row[17]
                            codpaisdom = row[18]
                            direccion = row[19]
                            cp = row[20]
                            localidad = row[21]
                            codprov = row[22]
                            comentariomiembro = row[23]
                            observaciones = row[24]
                            cuentaiban = row[25]
                            codagrupacion = row[26]
                            fechabaja = row[27]

                            # Mapear tipo de miembro
                            tipo_miembro_id = self.mapear_tipo_miembro(tipomiembro)

                            # Procesar teléfonos
                            telefono, telefono2 = self.procesar_telefonos(telmovil, telfijocasa, telfijotrabajo)

                            # Obtener país del documento
                            pais_documento_id = await self.obtener_uuid_pais(pg_session, codpaisdoc)

                            # Obtener provincia
                            provincia_id = await self.obtener_uuid_provincia(pg_session, codprov)

                            # Obtener país de domicilio
                            pais_domicilio_id = await self.obtener_uuid_pais(pg_session, codpaisdom)

                            # Obtener agrupación
                            agrupacion_id = await self.obtener_uuid_agrupacion(pg_session, codagrupacion)

                            # Determinar si es voluntario
                            es_voluntario = self.determinar_es_voluntario(colabora)

                            # Guardar DNI/NIE sin encriptar (se encriptará después)
                            numero_documento_limpio = None
                            if numdocumentomiembro:
                                doc_limpio = str(numdocumentomiembro).strip().replace(' ', '').replace('-', '')
                                if doc_limpio and doc_limpio.upper() != 'NULL':
                                    numero_documento_limpio = doc_limpio

                            # Guardar IBAN sin encriptar (se encriptará después)
                            iban_limpio = None
                            if cuentaiban:
                                iban_str = str(cuentaiban).strip().replace(' ', '')
                                if iban_str and iban_str.upper() != 'NULL':
                                    iban_limpio = iban_str

                            # Procesar fechas
                            fecha_nacimiento = self.parse_fecha(fechanac)
                            fecha_baja_parsed = self.parse_fecha(fechabaja)

                            # Detectar baja por EMAILERROR
                            if not fecha_baja_parsed and emailerror and str(emailerror).upper().strip() == 'BAJA':
                                fecha_baja_parsed = date.today()

                            # Determinar estado
                            estado_id = self.estado_baja_id if fecha_baja_parsed else self.estado_activo_id

                            # Procesar observaciones
                            obs_completas = []
                            if comentariomiembro:
                                obs_completas.append(str(comentariomiembro).strip())
                            if observaciones:
                                obs_completas.append(str(observaciones).strip())
                            observaciones_texto = ' | '.join(obs_completas) if obs_completas else None

                            # Procesar sexo (H=Hombre, M=Mujer)
                            sexo_valor = str(sexo).strip().upper() if sexo else None
                            if sexo_valor not in ('H', 'M'):
                                sexo_valor = None

                            # Crear miembro
                            miembro = Miembro(
                                nombre=self.normalizar_nombre(nom) or "Sin nombre",
                                apellido1=self.normalizar_nombre(ape1) or "Sin apellido",
                                apellido2=self.normalizar_nombre(ape2),
                                sexo=sexo_valor,
                                fecha_nacimiento=fecha_nacimiento,
                                tipo_miembro_id=tipo_miembro_id,
                                estado_id=estado_id,
                                tipo_documento=str(tipodocumentomiembro).strip() if tipodocumentomiembro else None,
                                numero_documento=numero_documento_limpio,
                                pais_documento_id=pais_documento_id,
                                direccion=str(direccion).strip() if direccion else None,
                                codigo_postal=str(cp).strip() if cp else None,
                                localidad=str(localidad).strip() if localidad else None,
                                provincia_id=provincia_id,
                                pais_domicilio_id=pais_domicilio_id,
                                telefono=telefono[:20] if telefono and len(telefono) > 20 else telefono,  # Truncar si es muy largo
                                telefono2=telefono2[:20] if telefono2 and len(telefono2) > 20 else telefono2,  # Truncar si es muy largo
                                email=str(email).strip() if email else None,
                                agrupacion_id=agrupacion_id,
                                iban=iban_limpio,
                                fecha_baja=fecha_baja_parsed,
                                motivo_baja=None,
                                observaciones=observaciones_texto,
                                activo=(fecha_baja_parsed is None),
                                es_voluntario=es_voluntario,
                                profesion=str(profesion).strip() if (es_voluntario and profesion) else None,
                                nivel_estudios=str(estudios).strip() if (es_voluntario and estudios) else None,
                                observaciones_voluntariado=str(colabora).strip() if colabora else None,
                                intereses=str(colabora).strip() if colabora else None
                            )

                            pg_session.add(miembro)
                            self.mapeo_miembros[coduser] = miembro.id
                            importados += 1

                            if importados % 100 == 0:
                                await pg_session.flush()
                                print(f"  Procesados {importados} miembros...", flush=True)

                        except Exception as e:
                            errores += 1
                            if errores < 10:
                                print(f"  [ERROR] CODUSER={coduser}: {e}", flush=True)
                            omitidos += 1

        # Flush final
        await pg_session.flush()
        print(f"  [OK] {importados} miembros importados", flush=True)
        if omitidos > 0:
            print(f"  [WARN] {omitidos} miembros omitidos (errores: {errores})", flush=True)

    async def guardar_mapeo_temporal(self, session: AsyncSession):
        """Guarda el mapeo CODUSER → UUID en temp_id_mapping."""
        print("\nGuardando mapeo temporal de miembros...", flush=True)

        for coduser, uuid_val in self.mapeo_miembros.items():
            await session.execute(
                text("""
                    INSERT INTO temp_id_mapping (tabla, old_id, new_uuid)
                    VALUES ('MIEMBRO', :old_id, :new_uuid)
                    ON CONFLICT (tabla, old_id) DO UPDATE SET new_uuid = EXCLUDED.new_uuid
                """),
                {"old_id": coduser, "new_uuid": uuid_val}
            )

        print(f"  [OK] {len(self.mapeo_miembros)} mapeos guardados", flush=True)

    async def encriptar_dnis_en_lote(self, session: AsyncSession):
        """Encripta todos los DNIs/NIEs en lote."""
        print("\nEncriptando DNIs en lote...", flush=True)

        result = await session.execute(
            select(Miembro).where(
                Miembro.numero_documento.isnot(None),
                Miembro.numero_documento != ''
            )
        )
        miembros = result.scalars().all()

        encriptados = 0
        errores = 0

        for miembro in miembros:
            try:
                miembro.numero_documento = self.servicio_encriptacion.encriptar_dni(miembro.numero_documento)
                encriptados += 1

                if encriptados % 100 == 0:
                    await session.flush()
                    print(f"  Encriptados {encriptados} DNIs...", flush=True)
            except ValueError as e:
                # DNI inválido, dejar sin encriptar
                errores += 1
                if errores < 10:
                    print(f"  [WARN] DNI inválido (ID={miembro.id}): {e}", flush=True)

        await session.flush()
        print(f"  [OK] {encriptados} DNIs encriptados", flush=True)
        if errores > 0:
            print(f"  [WARN] {errores} DNIs con errores (dejados sin encriptar)", flush=True)

    async def encriptar_ibans_en_lote(self, session: AsyncSession):
        """Encripta todos los IBANs en lote."""
        print("\nEncriptando IBANs en lote...", flush=True)

        result = await session.execute(
            select(Miembro).where(
                Miembro.iban.isnot(None),
                Miembro.iban != ''
            )
        )
        miembros = result.scalars().all()

        encriptados = 0
        errores = 0

        for miembro in miembros:
            try:
                miembro.iban = self.servicio_encriptacion.encriptar_iban(miembro.iban)
                encriptados += 1

                if encriptados % 100 == 0:
                    await session.flush()
                    print(f"  Encriptados {encriptados} IBANs...", flush=True)
            except (ValueError, Exception) as e:
                # IBAN inválido, dejar sin encriptar
                errores += 1
                if errores < 10:
                    print(f"  [WARN] IBAN inválido (ID={miembro.id}): {e}", flush=True)

        await session.flush()
        print(f"  [OK] {encriptados} IBANs encriptados", flush=True)
        if errores > 0:
            print(f"  [WARN] {errores} IBANs con errores (dejados sin encriptar)", flush=True)


async def main():
    """Función principal."""
    import sys

    print("\n" + "="*80, flush=True)
    print("IMPORTACION DE MIEMBROS DESDE MYSQL", flush=True)
    print("="*80 + "\n", flush=True)
    sys.stdout.flush()

    # Conectar a PostgreSQL
    print("Conectando a PostgreSQL...", flush=True)
    sys.stdout.flush()
    database_url = get_database_url()
    engine = create_async_engine(
        database_url,
        echo=False,
        connect_args={"server_settings": {"jit": "off"}, "statement_cache_size": 0}
    )
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    print("  [OK] SessionMaker creado", flush=True)
    sys.stdout.flush()

    async with async_session() as session:
        try:
            print("\nCreando mapeador...", flush=True)
            sys.stdout.flush()
            mapeador = MapeadorMiembrosMySQL()
            print("  [OK] Mapeador creado", flush=True)
            sys.stdout.flush()

            # Cargar tipos de miembro
            await mapeador.cargar_tipos_miembro(session)

            # Cargar estados de miembro
            await mapeador.cargar_estados_miembro(session)

            # Cargar cache de agrupaciones
            await mapeador.cargar_cache_agrupaciones(session)

            # Importar miembros desde MySQL
            await mapeador.importar_miembros(session)

            # Guardar mapeos
            await mapeador.guardar_mapeo_temporal(session)

            # Encriptar DNIs en lote
            await mapeador.encriptar_dnis_en_lote(session)

            # Encriptar IBANs en lote
            await mapeador.encriptar_ibans_en_lote(session)

            # Commit
            await session.commit()

            print("\n" + "="*80, flush=True)
            print("[OK] IMPORTACION COMPLETADA", flush=True)
            print("="*80, flush=True)
            print(f"\nMiembros importados: {len(mapeador.mapeo_miembros)}", flush=True)

        except Exception as e:
            await session.rollback()
            print(f"\n[ERROR] {e}", flush=True)
            import traceback
            traceback.print_exc()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
