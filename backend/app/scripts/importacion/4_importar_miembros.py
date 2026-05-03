"""
Script para importar miembros desde MySQL usando CSV + COPY.

Este enfoque es mucho más rápido y robusto que insertar uno por uno.

Proceso:
1. Extraer datos de MySQL
2. Generar CSV temporal
3. Usar COPY de PostgreSQL para inserción masiva
4. Encriptar DNIs e IBANs en lote

Este script debe ejecutarse DESPUÉS de importar agrupaciones.
"""
import asyncio
import uuid
import csv
import tempfile
import os
from typing import Optional
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from app.core.database import get_database_url
from app.infrastructure.services.encriptacion_service import get_encriptacion_service
from app.modules.membresia.models.miembro import Miembro, TipoMiembro
from app.modules.membresia.models.estado_miembro import EstadoMiembro
from app.scripts.importacion.mysql_helper import get_mysql_connection


class ImportadorMiembrosCSV:
    """Importa miembros usando CSV y COPY de PostgreSQL."""

    def __init__(self):
        self.mapeo_miembros: dict[int, str] = {}  # CODUSER → UUID (como string)
        self.servicio_encriptacion = get_encriptacion_service()
        self.tipo_miembro_miembro_id: Optional[str] = None
        self.tipo_miembro_simpatizante_id: Optional[str] = None
        self.tipo_miembro_voluntario_id: Optional[str] = None
        self.estado_activo_id: Optional[str] = None
        self.estado_baja_id: Optional[str] = None
        self.cache_agrupaciones: dict[str, str] = {}  # CODAGRUPACION → UUID (como string)
        self.cache_paises: dict[str, str] = {}  # Código → UUID
        self.cache_provincias: dict[int, str] = {}  # CODPROV → UUID

    @staticmethod
    def normalizar_nombre(nombre: Optional[str]) -> Optional[str]:
        """Normaliza nombres: primera letra mayúscula."""
        if not nombre:
            return None
        nombre_str = str(nombre).strip()
        if not nombre_str or nombre_str.upper() in ('NULL', 'NONE'):
            return None
        return nombre_str.title()

    async def cargar_caches(self, session: AsyncSession):
        """Carga todos los caches necesarios."""
        print("\nCargando caches...", flush=True)

        # Cargar tipos de miembro
        result = await session.execute(select(TipoMiembro).where(TipoMiembro.codigo == 'miembro'))
        tipo = result.scalar_one_or_none()
        if tipo:
            self.tipo_miembro_miembro_id = str(tipo.id)

        result = await session.execute(select(TipoMiembro).where(TipoMiembro.codigo == 'SIMPATIZANTE'))
        tipo = result.scalar_one_or_none()
        if tipo:
            self.tipo_miembro_simpatizante_id = str(tipo.id)

        result = await session.execute(select(TipoMiembro).where(TipoMiembro.codigo == 'VOLUNTARIO'))
        tipo = result.scalar_one_or_none()
        if tipo:
            self.tipo_miembro_voluntario_id = str(tipo.id)

        # Cargar estados
        result = await session.execute(select(EstadoMiembro).where(EstadoMiembro.codigo == 'ACTIVO'))
        estado = result.scalar_one_or_none()
        if estado:
            self.estado_activo_id = str(estado.id)

        result = await session.execute(select(EstadoMiembro).where(EstadoMiembro.codigo == 'BAJA'))
        estado = result.scalar_one_or_none()
        if estado:
            self.estado_baja_id = str(estado.id)

        # Cargar agrupaciones
        result = await session.execute(
            text("SELECT old_id, new_uuid FROM temp_id_mapping WHERE tabla = 'AGRUPACION'")
        )
        for row in result:
            self.cache_agrupaciones[str(row[0])] = str(row[1])

        # Cargar paises
        result = await session.execute(
            text("SELECT codigo, id FROM paises")
        )
        for row in result:
            self.cache_paises[str(row[0]).upper()] = str(row[1])

        # Cargar provincias
        result = await session.execute(
            text("SELECT old_id, new_uuid FROM temp_id_mapping WHERE tabla = 'PROVINCIA'")
        )
        for row in result:
            self.cache_provincias[int(row[0])] = str(row[1])

        print(f"  [OK] Caches cargados:")
        print(f"    Agrupaciones: {len(self.cache_agrupaciones)}")
        print(f"    Países: {len(self.cache_paises)}")
        print(f"    Provincias: {len(self.cache_provincias)}")

    def mapear_tipo_miembro(self, tipomiembro: Optional[str]) -> str:
        """Mapea TIPOMIEMBRO de MySQL a tipo_miembro_id."""
        if not tipomiembro:
            return self.tipo_miembro_miembro_id

        tipo_lower = str(tipomiembro).lower().strip()
        if 'miembro' in tipo_lower or 'administrador' in tipo_lower:
            return self.tipo_miembro_miembro_id
        elif 'simpatizante' in tipo_lower:
            return self.tipo_miembro_simpatizante_id
        elif 'voluntario' in tipo_lower:
            return self.tipo_miembro_voluntario_id
        return self.tipo_miembro_miembro_id

    def parse_fecha(self, fecha_str) -> Optional[str]:
        """Parsea fecha a formato ISO string."""
        if not fecha_str:
            return None
        if isinstance(fecha_str, date):
            if fecha_str.year == 0 or fecha_str.year == 1:
                return None
            return fecha_str.isoformat()
        try:
            fecha_str_clean = str(fecha_str).strip()
            if fecha_str_clean in ('', 'NULL', '0000-00-00', 'None'):
                return None
            if '-' in fecha_str_clean:
                parts = fecha_str_clean.split('-')
                if len(parts) == 3 and int(parts[0]) > 1:
                    return fecha_str_clean[:10]
        except (ValueError, AttributeError, IndexError):
            pass
        return None

    async def generar_csv_desde_mysql(self, csv_path: str):
        """Genera CSV desde MySQL."""
        print("\nGenerando CSV desde MySQL...", flush=True)

        registros = 0
        errores = 0

        async with get_mysql_connection() as mysql_conn:
            async with mysql_conn.cursor() as cursor:
                query = """
                    SELECT
                        m.CODUSER, m.CODPAISDOC, m.TIPOMIEMBRO, m.NUMDOCUMENTOMIEMBRO,
                        m.TIPODOCUMENTOMIEMBRO, m.APE1, m.APE2, m.NOM, m.FECHANAC,
                        m.TELFIJOCASA, m.TELFIJOTRABAJO, m.TELMOVIL, m.PROFESION,
                        m.ESTUDIOS, m.EMAIL, m.EMAILERROR, m.COLABORA, m.CODPAISDOM,
                        m.DIRECCION, m.CP, m.LOCALIDAD, m.CODPROV, m.COMENTARIOmiembro,
                        m.OBSERVACIONES, s.CUENTAIBAN, s.CODAGRUPACION, s.FECHABAJA
                    FROM MIEMBRO m
                    LEFT JOIN miembro s ON m.CODUSER = s.CODUSER
                    ORDER BY m.CODUSER
                """
                await cursor.execute(query)

                with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)

                    while True:
                        rows = await cursor.fetchmany(500)
                        if not rows:
                            break

                        for row in rows:
                            try:
                                coduser = row[0]
                                miembro_uuid = str(uuid.uuid4())
                                self.mapeo_miembros[coduser] = miembro_uuid

                                # Procesar campos
                                tipo_miembro_id = self.mapear_tipo_miembro(row[2])

                                # Teléfonos: prioridad móvil > fijo_casa > fijo_trabajo
                                telefonos = []
                                if row[11]:  # telmovil
                                    tel = str(row[11]).strip()[:20]
                                    if tel:
                                        telefonos.append(tel)
                                if row[9]:  # telfijocasa
                                    tel = str(row[9]).strip()[:20]
                                    if tel:
                                        telefonos.append(tel)
                                if row[10]:  # telfijotrabajo
                                    tel = str(row[10]).strip()[:20]
                                    if tel:
                                        telefonos.append(tel)

                                telefono = telefonos[0] if len(telefonos) > 0 else None
                                telefono2 = telefonos[1] if len(telefonos) > 1 else None

                                # Países
                                pais_doc = str(row[1]).upper() if row[1] else None
                                pais_documento_id = self.cache_paises.get(pais_doc) if pais_doc else None

                                pais_dom = str(row[17]).upper() if row[17] else None
                                pais_domicilio_id = self.cache_paises.get(pais_dom) if pais_dom else None

                                # Provincia
                                provincia_id = self.cache_provincias.get(row[21]) if row[21] else None

                                # Agrupación
                                agrupacion_id = self.cache_agrupaciones.get(str(row[25])) if row[25] else None

                                # Fechas
                                fecha_nacimiento = self.parse_fecha(row[8])
                                fecha_baja = self.parse_fecha(row[26])

                                # Detectar baja por EMAILERROR
                                if not fecha_baja and row[15] and str(row[15]).upper().strip() == 'BAJA':
                                    fecha_baja = date.today().isoformat()

                                estado_id = self.estado_baja_id if fecha_baja else self.estado_activo_id
                                activo = 't' if not fecha_baja else 'f'

                                # Voluntario
                                es_voluntario = 'f'
                                if row[16]:
                                    colabora_str = str(row[16]).strip().lower()
                                    es_voluntario = 't' if colabora_str and colabora_str not in ('null', 'no', 'none', '') else 'f'

                                # DNI/IBAN (sin encriptar)
                                numero_documento = None
                                if row[3]:
                                    doc = str(row[3]).strip().replace(' ', '').replace('-', '')
                                    if doc and doc.upper() != 'NULL':
                                        numero_documento = doc

                                iban = None
                                if row[24]:
                                    ib = str(row[24]).strip().replace(' ', '')
                                    if ib and ib.upper() != 'NULL':
                                        iban = ib

                                # Observaciones
                                obs = []
                                if row[22]:
                                    obs.append(str(row[22]).strip())
                                if row[23]:
                                    obs.append(str(row[23]).strip())
                                observaciones = ' | '.join(obs) if obs else None

                                # Escribir fila CSV
                                writer.writerow([
                                    miembro_uuid,  # id
                                    self.normalizar_nombre(row[7]) or 'Sin nombre',  # nombre
                                    self.normalizar_nombre(row[5]) or 'Sin apellido',  # apellido1
                                    self.normalizar_nombre(row[6]),  # apellido2
                                    fecha_nacimiento,  # fecha_nacimiento
                                    tipo_miembro_id,  # tipo_miembro_id
                                    estado_id,  # estado_id
                                    str(row[4]).strip() if row[4] else None,  # tipo_documento
                                    numero_documento,  # numero_documento
                                    pais_documento_id,  # pais_documento_id
                                    str(row[18]).strip() if row[18] else None,  # direccion
                                    str(row[19]).strip() if row[19] else None,  # codigo_postal
                                    str(row[20]).strip() if row[20] else None,  # localidad
                                    provincia_id,  # provincia_id
                                    pais_domicilio_id,  # pais_domicilio_id
                                    telefono,  # telefono
                                    telefono2,  # telefono2
                                    str(row[14]).strip() if row[14] else None,  # email
                                    agrupacion_id,  # agrupacion_id
                                    iban,  # iban
                                    fecha_baja,  # fecha_baja
                                    None,  # motivo_baja_texto
                                    observaciones,  # observaciones
                                    activo,  # activo
                                    es_voluntario,  # es_voluntario
                                    None,  # disponibilidad
                                    None,  # horas_disponibles_semana
                                    str(row[12]).strip() if (es_voluntario == 't' and row[12]) else None,  # profesion
                                    str(row[13]).strip() if (es_voluntario == 't' and row[13]) else None,  # nivel_estudios
                                    None,  # experiencia_voluntariado
                                    str(row[16]).strip() if row[16] else None,  # intereses
                                    None,  # observaciones_voluntariado
                                    'f',  # puede_conducir (default False)
                                    'f',  # vehiculo_propio (default False)
                                    'f',  # disponibilidad_viajar (default False)
                                ])

                                registros += 1
                                if registros % 500 == 0:
                                    print(f"  Procesados {registros} registros...", flush=True)

                            except Exception as e:
                                errores += 1
                                if errores < 10:
                                    print(f"  [WARN] Error en CODUSER={coduser}: {e}", flush=True)

        print(f"  [OK] CSV generado: {registros} registros (errores: {errores})", flush=True)
        return registros

    async def importar_csv_a_postgres(self, session: AsyncSession, csv_path: str):
        """Importa CSV a PostgreSQL usando inserción por lotes."""
        print("\nImportando CSV a PostgreSQL...", flush=True)

        # Leer CSV e insertar en lotes
        import csv as csv_module

        registros_importados = 0
        lote = []
        TAMANO_LOTE = 500

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv_module.reader(f)

            for row in reader:
                lote.append(row)

                if len(lote) >= TAMANO_LOTE:
                    await self._insertar_lote(session, lote)
                    registros_importados += len(lote)
                    print(f"  Importados {registros_importados} registros...", flush=True)
                    lote = []

            # Insertar último lote
            if lote:
                await self._insertar_lote(session, lote)
                registros_importados += len(lote)

        print(f"  [OK] {registros_importados} registros importados", flush=True)

    async def _insertar_lote(self, session: AsyncSession, lote: list):
        """Inserta un lote de registros."""
        insert_sql = text("""
            INSERT INTO miembros (
                id, nombre, apellido1, apellido2, fecha_nacimiento,
                tipo_miembro_id, estado_id, tipo_documento, numero_documento,
                pais_documento_id, direccion, codigo_postal, localidad,
                provincia_id, pais_domicilio_id, telefono, telefono2, email,
                agrupacion_id, iban, fecha_baja, motivo_baja_texto, observaciones,
                activo, es_voluntario, disponibilidad, horas_disponibles_semana,
                profesion, nivel_estudios, experiencia_voluntariado, intereses,
                observaciones_voluntariado, puede_conducir, vehiculo_propio,
                disponibilidad_viajar
            ) VALUES (
                :id, :nombre, :apellido1, :apellido2, :fecha_nacimiento,
                :tipo_miembro_id, :estado_id, :tipo_documento, :numero_documento,
                :pais_documento_id, :direccion, :codigo_postal, :localidad,
                :provincia_id, :pais_domicilio_id, :telefono, :telefono2, :email,
                :agrupacion_id, :iban, :fecha_baja, :motivo_baja_texto, :observaciones,
                :activo, :es_voluntario, :disponibilidad, :horas_disponibles_semana,
                :profesion, :nivel_estudios, :experiencia_voluntariado, :intereses,
                :observaciones_voluntariado, :puede_conducir, :vehiculo_propio,
                :disponibilidad_viajar
            )
        """)

        for row in lote:
            # Convertir fechas de string a date objects
            fecha_nacimiento = None
            if row[4]:
                try:
                    fecha_nacimiento = datetime.strptime(row[4], '%Y-%m-%d').date()
                except ValueError:
                    pass

            fecha_baja = None
            if row[20]:
                try:
                    fecha_baja = datetime.strptime(row[20], '%Y-%m-%d').date()
                except ValueError:
                    pass

            params = {
                'id': row[0],
                'nombre': row[1],
                'apellido1': row[2],
                'apellido2': row[3] if row[3] else None,
                'fecha_nacimiento': fecha_nacimiento,
                'tipo_miembro_id': row[5],
                'estado_id': row[6],
                'tipo_documento': row[7] if row[7] else None,
                'numero_documento': row[8] if row[8] else None,
                'pais_documento_id': row[9] if row[9] else None,
                'direccion': row[10] if row[10] else None,
                'codigo_postal': row[11] if row[11] else None,
                'localidad': row[12] if row[12] else None,
                'provincia_id': row[13] if row[13] else None,
                'pais_domicilio_id': row[14] if row[14] else None,
                'telefono': row[15] if row[15] else None,
                'telefono2': row[16] if row[16] else None,
                'email': row[17] if row[17] else None,
                'agrupacion_id': row[18] if row[18] else None,
                'iban': row[19] if row[19] else None,
                'fecha_baja': fecha_baja,
                'motivo_baja_texto': row[21] if row[21] else None,
                'observaciones': row[22] if row[22] else None,
                'activo': row[23] == 't',
                'es_voluntario': row[24] == 't',
                'disponibilidad': row[25] if row[25] else None,
                'horas_disponibles_semana': int(row[26]) if row[26] else None,
                'profesion': row[27] if row[27] else None,
                'nivel_estudios': row[28] if row[28] else None,
                'experiencia_voluntariado': row[29] if row[29] else None,
                'intereses': row[30] if row[30] else None,
                'observaciones_voluntariado': row[31] if row[31] else None,
                'puede_conducir': row[32] == 't',
                'vehiculo_propio': row[33] == 't',
                'disponibilidad_viajar': row[34] == 't',
            }
            await session.execute(insert_sql, params)

        await session.flush()

    async def guardar_mapeo_temporal(self, session: AsyncSession):
        """Guarda mapeo CODUSER → UUID."""
        print("\nGuardando mapeo temporal...", flush=True)

        for coduser, uuid_str in self.mapeo_miembros.items():
            await session.execute(
                text("""
                    INSERT INTO temp_id_mapping (tabla, old_id, new_uuid)
                    VALUES ('MIEMBRO', :old_id, :new_uuid)
                    ON CONFLICT (tabla, old_id) DO UPDATE SET new_uuid = EXCLUDED.new_uuid
                """),
                {"old_id": coduser, "new_uuid": uuid_str}
            )

        await session.flush()
        print(f"  [OK] {len(self.mapeo_miembros)} mapeos guardados", flush=True)

    async def encriptar_dnis_en_lote(self, session: AsyncSession):
        """Encripta DNIs en lote."""
        print("\nEncriptando DNIs...", flush=True)

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
                    print(f"  Encriptados {encriptados}...", flush=True)
            except ValueError:
                errores += 1

        await session.flush()
        print(f"  [OK] {encriptados} DNIs encriptados (errores: {errores})", flush=True)

    async def encriptar_ibans_en_lote(self, session: AsyncSession):
        """Encripta IBANs en lote."""
        print("\nEncriptando IBANs...", flush=True)

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
                    print(f"  Encriptados {encriptados}...", flush=True)
            except Exception:
                errores += 1

        await session.flush()
        print(f"  [OK] {encriptados} IBANs encriptados (errores: {errores})", flush=True)


async def main():
    """Función principal."""
    import sys

    print("\n" + "="*80, flush=True)
    print("IMPORTACION DE MIEMBROS (CSV + COPY)", flush=True)
    print("="*80 + "\n", flush=True)

    # Conectar a PostgreSQL
    database_url = get_database_url()
    engine = create_async_engine(
        database_url,
        echo=False,
        connect_args={"server_settings": {"jit": "off"}, "statement_cache_size": 0}
    )
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Crear archivo CSV temporal
    csv_path = os.path.join(tempfile.gettempdir(), 'miembros_import.csv')

    try:
        async with async_session() as session:
            importador = ImportadorMiembrosCSV()

            # Cargar caches
            await importador.cargar_caches(session)

            # Generar CSV desde MySQL
            total_registros = await importador.generar_csv_desde_mysql(csv_path)

            # Importar CSV a PostgreSQL
            await importador.importar_csv_a_postgres(session, csv_path)

            # Guardar mapeos
            await importador.guardar_mapeo_temporal(session)

            # Encriptar datos sensibles
            await importador.encriptar_dnis_en_lote(session)
            await importador.encriptar_ibans_en_lote(session)

            # Commit
            await session.commit()

            print("\n" + "="*80, flush=True)
            print("[OK] IMPORTACION COMPLETADA", flush=True)
            print("="*80, flush=True)
            print(f"\nMiembros importados: {total_registros}", flush=True)

    except Exception as e:
        print(f"\n[ERROR] {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise
    finally:
        # Limpiar archivo temporal
        if os.path.exists(csv_path):
            os.remove(csv_path)
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
