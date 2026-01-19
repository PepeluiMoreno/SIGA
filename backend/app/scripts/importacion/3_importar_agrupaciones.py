"""
Script para importar agrupaciones territoriales desde el dump SQL.

Importa las tablas:
- AGRUPACIONTERRITORIAL -> agrupaciones_territoriales
- AGRUPACIONTERRITORIAL_estatal_y_internacional -> agrupaciones_territoriales (merge)

Este script debe ejecutarse DESPUES de importar datos geograficos.

IMPORTANTE: Encripta los IBANs antes de almacenarlos.
"""
import asyncio
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from app.core.database import get_database_url
from app.infrastructure.services.encriptacion_service import get_encriptacion_service
from app.domains.geografico.models.direccion import AgrupacionTerritorial, Provincia
from app.scripts.importacion.sql_dump_parser import SQLDumpParser


# Ruta al archivo dump SQL
DUMP_FILE_PATH = r"C:\Users\Jose\dev\AIEL\data\europalaica_com_2026_01_01 apertura de año.sql"


class MapeadorAgrupaciones:
    """Mapea agrupaciones territoriales de MySQL a PostgreSQL."""

    def __init__(self):
        self.mapeo_agrupaciones: dict[str, uuid.UUID] = {}  # CODAGRUPACION -> UUID
        self.servicio_encriptacion = get_encriptacion_service()
        self.pais_espana_id: Optional[uuid.UUID] = None

    def mapear_tipo_agrupacion(self, ambito: str) -> str:
        """Mapea el campo AMBITO de MySQL a tipo de agrupacion (string)."""

        mapeo = {
            'estatal': 'ESTATAL',
            'autonomico': 'AUTONOMICA',
            'provincial': 'PROVINCIAL',
            'local': 'LOCAL',
            'internacional': 'INTERNACIONAL'
        }

        ambito_lower = ambito.lower().strip() if ambito else 'local'
        return mapeo.get(ambito_lower, 'LOCAL')

    def calcular_estado(self, estado_mysql: Optional[str]) -> bool:
        """Calcula si la agrupacion esta activa basado en el campo ESTADO de MySQL."""

        if not estado_mysql:
            return True

        estado_lower = estado_mysql.lower().strip()
        return estado_lower in ['activa', 'activo']

    async def obtener_provincia_por_cp(self, session: AsyncSession, codigo_postal: Optional[str]) -> Optional[uuid.UUID]:
        """Obtiene el UUID de una provincia basandose en el codigo postal."""

        if not codigo_postal:
            return None

        # Extraer codigo de provincia del CP (primeros 2 digitos)
        cp_limpio = str(codigo_postal).strip().zfill(5)
        codigo_prov = cp_limpio[:2]

        result = await session.execute(
            select(Provincia).where(
                Provincia.codigo == codigo_prov,
                Provincia.pais_id == select(Provincia.pais_id).where(Provincia.codigo == codigo_prov).limit(1).scalar_subquery()
            ).limit(1)
        )
        provincia = result.scalar_one_or_none()
        return provincia.id if provincia else None

    async def obtener_pais_espana(self, session: AsyncSession) -> uuid.UUID:
        """Obtiene el UUID del pais España."""
        if self.pais_espana_id:
            return self.pais_espana_id

        from app.domains.geografico.models.direccion import Pais
        result = await session.execute(
            select(Pais).where(Pais.codigo == 'ES')
        )
        pais = result.scalar_one_or_none()
        if pais:
            self.pais_espana_id = pais.id
            return pais.id

        # Si no existe, tomar el primer pais disponible
        result = await session.execute(select(Pais).limit(1))
        pais = result.scalar_one_or_none()
        if pais:
            self.pais_espana_id = pais.id
            return pais.id

        raise ValueError("No hay paises en la base de datos")

    async def importar_agrupaciones_principales(self, session: AsyncSession, parser: SQLDumpParser):
        """Importa la tabla AGRUPACIONTERRITORIAL."""

        print("\nImportando agrupaciones territoriales principales...")

        importadas = 0
        omitidas = 0

        for row in parser.extraer_inserts('AGRUPACIONTERRITORIAL'):
            # Estructura: 23 campos segun el CREATE TABLE
            if len(row) < 23:
                print(f"  [WARN] Fila invalida (longitud {len(row)}), se omite")
                omitidas += 1
                continue

            # Indices basados en INSERT INTO statement
            codigo = row[0]  # CODAGRUPACION
            nombre = row[1]  # NOMAGRUPACION
            cif = row[2]  # CIF
            gestion_cuotas = row[3]  # GESTIONCUOTAS
            titular_cuenta = row[4]  # TITULARCUENTASBANCOS
            iban1 = row[5]  # CUENTAAGRUPIBAN1
            nombre_iban1 = row[6]  # NOMBREIBAN1
            iban2 = row[7]  # CUENTAAGRUPIBAN2
            nombre_iban2 = row[8]  # NOMBREIBAN2
            tel_fijo = row[9]  # TELFIJOTRABAJO
            tel_mov = row[10]  # TELMOV
            web = row[11]  # WEB
            email = row[12]  # EMAIL
            email_coord = row[13]  # EMAILCOORD
            email_sec = row[14]  # EMAILSECRETARIO
            email_tes = row[15]  # EMAILTESORERO
            ambito = row[16]  # AMBITO
            estado = row[17]  # ESTADO
            codpais_dom = row[18]  # CODPAISDOM
            direccion = row[19]  # DIRECCION
            cp = row[20]  # CP
            localidad = row[21]  # LOCALIDAD
            observaciones = row[22]  # OBSERVACIONES

            codigo_str = str(codigo).strip() if codigo else None

            if not codigo_str:
                print(f"  [WARN] Agrupacion sin CODAGRUPACION, se omite")
                omitidas += 1
                continue

            # Verificar si ya existe
            if codigo_str in self.mapeo_agrupaciones:
                continue

            # Mapear tipo
            tipo = self.mapear_tipo_agrupacion(str(ambito) if ambito else 'local')

            # Calcular estado activo
            activo = self.calcular_estado(str(estado) if estado else None)

            # Obtener provincia UUID desde CP
            provincia_id = await self.obtener_provincia_por_cp(session, str(cp) if cp else None)

            # Encriptar IBANs si existen
            iban1_encriptado = None
            iban2_encriptado = None

            if iban1:
                iban1_limpio = str(iban1).strip().replace(' ', '')
                if iban1_limpio and len(iban1_limpio) > 5:
                    try:
                        iban1_encriptado = self.servicio_encriptacion.encriptar_iban(iban1_limpio)
                    except Exception as e:
                        print(f"  [WARN] Error encriptando IBAN1 para {codigo_str}: {e}")

            if iban2:
                iban2_limpio = str(iban2).strip().replace(' ', '')
                if iban2_limpio and len(iban2_limpio) > 5:
                    try:
                        iban2_encriptado = self.servicio_encriptacion.encriptar_iban(iban2_limpio)
                    except Exception as e:
                        print(f"  [WARN] Error encriptando IBAN2 para {codigo_str}: {e}")

            # Obtener pais_id desde provincia o España por defecto
            pais_id = None
            if provincia_id:
                result_prov = await session.execute(
                    select(Provincia).where(Provincia.id == provincia_id)
                )
                provincia_obj = result_prov.scalar_one_or_none()
                if provincia_obj:
                    pais_id = provincia_obj.pais_id

            if not pais_id:
                pais_id = await self.obtener_pais_espana(session)

            # Crear agrupacion con solo los campos que existen en el modelo
            agrupacion = AgrupacionTerritorial(
                codigo=codigo_str,
                nombre=str(nombre).strip() if nombre else f"Agrupacion {codigo_str}",
                tipo=tipo,
                provincia_id=provincia_id,
                pais_id=pais_id,
                email=str(email).strip() if email else None,
                telefono=str(tel_fijo).strip() if tel_fijo else str(tel_mov).strip() if tel_mov else None,
                web=str(web).strip() if web else None,
                activo=activo
            )

            session.add(agrupacion)
            self.mapeo_agrupaciones[codigo_str] = agrupacion.id
            importadas += 1

            if importadas % 20 == 0:
                await session.flush()
                print(f"  Procesadas {importadas} agrupaciones...")

        print(f"  [OK] {importadas} agrupaciones principales importadas")
        if omitidas > 0:
            print(f"  [WARN] {omitidas} registros omitidos")

    async def importar_agrupaciones_especiales(self, session: AsyncSession, parser: SQLDumpParser):
        """Importa la tabla AGRUPACIONTERRITORIAL_estatal_y_internacional."""

        print("\nImportando agrupaciones estatales e internacionales...")

        importadas = 0
        omitidas = 0

        for row in parser.extraer_inserts('AGRUPACIONTERRITORIAL_estatal_y_internacional'):
            # Misma estructura que la tabla principal
            if len(row) < 23:
                omitidas += 1
                continue

            codigo = row[0]
            nombre = row[1]
            cif = row[2]
            gestion_cuotas = row[3]
            titular_cuenta = row[4]
            iban1 = row[5]
            nombre_iban1 = row[6]
            iban2 = row[7]
            nombre_iban2 = row[8]
            tel_fijo = row[9]
            tel_mov = row[10]
            web = row[11]
            email = row[12]
            email_coord = row[13]
            email_sec = row[14]
            email_tes = row[15]
            ambito = row[16]
            estado = row[17]
            codpais_dom = row[18]
            direccion = row[19]
            cp = row[20]
            localidad = row[21]
            observaciones = row[22]

            codigo_str = str(codigo).strip() if codigo else None

            if not codigo_str:
                omitidas += 1
                continue

            # Si ya existe de la tabla principal, skip
            if codigo_str in self.mapeo_agrupaciones:
                continue

            # Mapear tipo (forzar ESTATAL o INTERNACIONAL)
            tipo = self.mapear_tipo_agrupacion(str(ambito) if ambito else 'estatal')

            # Calcular estado activo
            activo = self.calcular_estado(str(estado) if estado else None)

            # Obtener provincia UUID desde CP
            provincia_id = await self.obtener_provincia_por_cp(session, str(cp) if cp else None)

            # Encriptar IBANs
            iban1_encriptado = None
            iban2_encriptado = None

            if iban1:
                iban1_limpio = str(iban1).strip().replace(' ', '')
                if iban1_limpio and len(iban1_limpio) > 5:
                    try:
                        iban1_encriptado = self.servicio_encriptacion.encriptar_iban(iban1_limpio)
                    except Exception:
                        pass

            if iban2:
                iban2_limpio = str(iban2).strip().replace(' ', '')
                if iban2_limpio and len(iban2_limpio) > 5:
                    try:
                        iban2_encriptado = self.servicio_encriptacion.encriptar_iban(iban2_limpio)
                    except Exception:
                        pass

            # Obtener pais_id desde provincia o España por defecto
            pais_id = None
            if provincia_id:
                result_prov = await session.execute(
                    select(Provincia).where(Provincia.id == provincia_id)
                )
                provincia_obj = result_prov.scalar_one_or_none()
                if provincia_obj:
                    pais_id = provincia_obj.pais_id

            if not pais_id:
                pais_id = await self.obtener_pais_espana(session)

            # Crear agrupacion con solo los campos que existen en el modelo
            agrupacion = AgrupacionTerritorial(
                codigo=codigo_str,
                nombre=str(nombre).strip() if nombre else f"Agrupacion {codigo_str}",
                tipo=tipo,
                provincia_id=provincia_id,
                pais_id=pais_id,
                email=str(email).strip() if email else None,
                telefono=str(tel_fijo).strip() if tel_fijo else str(tel_mov).strip() if tel_mov else None,
                web=str(web).strip() if web else None,
                activo=activo
            )

            session.add(agrupacion)
            self.mapeo_agrupaciones[codigo_str] = agrupacion.id
            importadas += 1

        print(f"  [OK] {importadas} agrupaciones especiales importadas")
        if omitidas > 0:
            print(f"  [WARN] {omitidas} registros omitidos")

    async def guardar_mapeo_temporal(self, session: AsyncSession):
        """Guarda el mapeo de codigos de agrupacion en temp_id_mapping."""

        print("\nGuardando mapeo de agrupaciones...")

        for codigo, uuid_val in self.mapeo_agrupaciones.items():
            # Usar hash del codigo como old_id para temp_id_mapping
            await session.execute(
                text("""
                INSERT INTO temp_id_mapping (tabla, old_id, new_uuid)
                VALUES ('AGRUPACION', :old_id, :new_uuid)
                ON CONFLICT (tabla, old_id) DO UPDATE SET new_uuid = EXCLUDED.new_uuid
                """),
                {"old_id": abs(hash(codigo)) % (10 ** 8), "new_uuid": uuid_val}
            )

        print(f"  [OK] {len(self.mapeo_agrupaciones)} mapeos guardados")

    async def establecer_jerarquia(self, session: AsyncSession):
        """Establece la jerarquia de agrupaciones basandose en los codigos."""

        print("\nEstableciendo jerarquia de agrupaciones...")

        actualizadas = 0
        sin_padre = 0

        # Recorrer todas las agrupaciones importadas
        for codigo_str, uuid_agrup in self.mapeo_agrupaciones.items():
            try:
                codigo = int(codigo_str)
            except (ValueError, TypeError):
                continue

            # Buscar padre segun codigo
            codigo_padre = None

            # Logica de jerarquia:
            # - Provinciales (ej: 104000) -> padre autonomica (100000)
            # - Autonomicas (ej: 100000) -> padre estatal (0)
            # - Locales (ej: 104001) -> padre provincial (104000)

            if codigo == 0 or codigo >= 70000000:
                # Estatal/Internacional no tienen padre
                sin_padre += 1
                continue

            elif codigo >= 100000:
                # Puede ser autonomica o provincial
                if codigo % 100000 == 0:
                    # Es autonomica (100000, 200000, etc.) -> padre es estatal (0)
                    codigo_padre = '0'
                else:
                    # Es provincial o local -> buscar autonomica
                    base_autonomica = (codigo // 100000) * 100000
                    codigo_padre = str(base_autonomica)

            # Buscar UUID del padre
            if codigo_padre and codigo_padre in self.mapeo_agrupaciones:
                uuid_padre = self.mapeo_agrupaciones[codigo_padre]

                # Actualizar agrupacion con su padre
                await session.execute(
                    text("""
                    UPDATE agrupaciones_territoriales
                    SET agrupacion_padre_id = :padre_id
                    WHERE id = :agrupacion_id
                    """),
                    {"padre_id": uuid_padre, "agrupacion_id": uuid_agrup}
                )
                actualizadas += 1
            else:
                sin_padre += 1

        print(f"  [OK] {actualizadas} relaciones de jerarquia establecidas")
        print(f"  [INFO] {sin_padre} agrupaciones sin padre (nivel superior)")


async def main():
    """Funcion principal."""

    print("\n" + "="*80)
    print("IMPORTACION DE AGRUPACIONES TERRITORIALES")
    print("="*80 + "\n")

    # Crear parser del dump SQL
    print("Cargando dump SQL...")
    try:
        parser = SQLDumpParser(DUMP_FILE_PATH)
        print(f"  [OK] Dump cargado: {DUMP_FILE_PATH}")
    except FileNotFoundError as e:
        print(f"  [ERROR] Archivo dump no encontrado: {e}")
        print("\n  Ajusta DUMP_FILE_PATH en el script con la ruta correcta.")
        return

    # Conectar a PostgreSQL
    print("\nConectando a PostgreSQL...")
    database_url = get_database_url()
    engine = create_async_engine(
        database_url,
        echo=False,
        connect_args={"statement_cache_size": 0}
    )
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            mapeador = MapeadorAgrupaciones()

            # Importar agrupaciones principales
            await mapeador.importar_agrupaciones_principales(session, parser)

            # Importar agrupaciones especiales
            await mapeador.importar_agrupaciones_especiales(session, parser)

            # Establecer jerarquia
            await mapeador.establecer_jerarquia(session)

            # Guardar mapeos
            await mapeador.guardar_mapeo_temporal(session)

            # Commit
            await session.commit()

            print("\n" + "="*80)
            print("[OK] IMPORTACION COMPLETADA")
            print("="*80)
            print(f"\nAgrupaciones importadas: {len(mapeador.mapeo_agrupaciones)}")

        except Exception as e:
            await session.rollback()
            print(f"\n[ERROR]: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
