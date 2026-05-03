"""
Script para importar cuotas anuales desde MySQL usando CSV + batch inserts.

Importa la tabla:
- CUOTAANIOmiembro → cuotas_anuales

IMPORTANTE:
- Relaciona miembros con sus cuotas por ejercicio
- Calcula estado basado en datos de pago
- Mapea modo de ingreso (SEPA, TRANSFERENCIA, etc.)
- Relaciona con importe_cuota_anio_id correspondiente

Este script debe ejecutarse DESPUÉS de importar miembros e importes de cuota.
"""
import asyncio
import uuid
import csv
import tempfile
import os
from decimal import Decimal
from typing import Optional
from datetime import date, datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from app.core.database import get_database_url
from app.modules.economico.models.cuotas import CuotaAnual, ImporteCuotaAnio, ModoIngreso
from app.modules.core.models.estados import EstadoCuota
from app.modules.miembros.models.miembro import Miembro
from app.scripts.importacion.mysql_helper import get_mysql_connection


class ImportadorCuotasAnualesCSV:
    """Importa cuotas anuales usando CSV y batch inserts."""

    def __init__(self):
        self.estados: dict[str, str] = {}  # codigo → UUID as string
        self.cache_miembros: dict[int, str] = {}  # CODUSER → UUID as string
        self.cache_agrupaciones: dict[str, str] = {}  # codigo → UUID as string
        self.cache_importes_cuota: dict[tuple[int, str], str] = {}  # (ejercicio, tipo_miembro_id) → importe_cuota_anio_id as string
        self.miembro_tipo: dict[str, str] = {}  # miembro_id → tipo_miembro_id
        self.miembro_provincia: dict[str, str] = {}  # miembro_id → provincia_id
        self.provincia_agrupacion: dict[str, str] = {}  # provincia_id → agrupacion_id (provincial)

    async def cargar_caches(self, session: AsyncSession):
        """Carga todos los caches necesarios."""
        print("\nCargando caches...", flush=True)

        # Cargar estados de cuota
        result = await session.execute(select(EstadoCuota))
        estados = result.scalars().all()
        for estado in estados:
            self.estados[estado.codigo] = str(estado.id)

        # Cargar mapeo de miembros
        result = await session.execute(
            text("SELECT old_id, new_uuid FROM temp_id_mapping WHERE tabla = 'MIEMBRO'")
        )
        for row in result:
            self.cache_miembros[int(row[0])] = str(row[1])

        # Cargar tipo de miembro para cada miembro
        result = await session.execute(
            text("SELECT id, tipo_miembro_id FROM miembros")
        )
        for row in result:
            self.miembro_tipo[str(row[0])] = str(row[1])

        # Cargar agrupaciones por código (not using temp_id_mapping because it has numeric IDs)
        result = await session.execute(
            text("SELECT codigo, id FROM agrupaciones_territoriales")
        )
        for row in result:
            self.cache_agrupaciones[str(row[0])] = str(row[1])

        # Cargar importes de cuota
        result = await session.execute(
            select(ImporteCuotaAnio.id, ImporteCuotaAnio.ejercicio, ImporteCuotaAnio.tipo_miembro_id)
        )
        for row in result:
            key = (int(row[1]), str(row[2]))
            self.cache_importes_cuota[key] = str(row[0])

        # Cargar provincia de cada miembro
        result = await session.execute(
            text("SELECT id, provincia_id FROM miembros WHERE provincia_id IS NOT NULL")
        )
        for row in result:
            self.miembro_provincia[str(row[0])] = str(row[1])

        # Cargar agrupación provincial por provincia
        result = await session.execute(
            text("""
                SELECT provincia_id, id, tipo
                FROM agrupaciones_territoriales
                WHERE provincia_id IS NOT NULL
                AND tipo IN ('PROVINCIAL', 'AUTONOMICA')
                ORDER BY provincia_id, tipo DESC
            """)
        )
        for row in result:
            provincia_id = str(row[0])
            # Solo guardar si no existe ya (prioriza PROVINCIAL sobre AUTONOMICA por el ORDER BY DESC)
            if provincia_id not in self.provincia_agrupacion:
                self.provincia_agrupacion[provincia_id] = str(row[1])

        print(f"  [OK] Caches cargados:")
        print(f"    Estados: {len(self.estados)}")
        print(f"    Miembros: {len(self.cache_miembros)}")
        print(f"    Agrupaciones: {len(self.cache_agrupaciones)}")
        print(f"    Importes cuota: {len(self.cache_importes_cuota)}")
        print(f"    Provincias con agrupación: {len(self.provincia_agrupacion)}")

    def mapear_modo_ingreso(self, modo_mysql: Optional[str]) -> Optional[str]:
        """Mapea MODOINGRESO de MySQL a ModoIngreso enum."""
        if not modo_mysql:
            return None

        modo_upper = str(modo_mysql).upper().strip()
        mapeo = {
            'SEPA': 'SEPA',
            'TRANSFERENCIA': 'TRANSFERENCIA',
            'PAYPAL': 'PAYPAL',
            'EFECTIVO': 'EFECTIVO',
            'TARJETA': 'TARJETA'
        }
        return mapeo.get(modo_upper)

    def calcular_estado_cuota(
        self,
        importe: Decimal,
        importe_pagado: Decimal,
        fecha_vencimiento: Optional[date]
    ) -> str:
        """
        Calcula el código de estado de cuota basado en importes y fechas.

        Lógica:
        - Si importe_pagado >= importe → PAGADA
        - Si importe_pagado > 0 pero < importe → PARCIAL
        - Si importe_pagado == 0 y fecha_vencimiento pasada → VENCIDA
        - Si importe_pagado == 0 y fecha_vencimiento futura → PENDIENTE
        """
        if importe_pagado >= importe:
            return 'PAGADA'

        if importe_pagado > Decimal('0.00'):
            return 'PARCIAL'

        # Si no hay pago
        if fecha_vencimiento and fecha_vencimiento < date.today():
            return 'VENCIDA'

        return 'PENDIENTE'

    def parse_fecha(self, fecha_val) -> Optional[str]:
        """Parsea fecha a formato ISO string, manejando datetime objects de MySQL."""
        if not fecha_val:
            return None

        # Handle datetime objects directly (from MySQL)
        if isinstance(fecha_val, datetime):
            if fecha_val.year == 0 or fecha_val.year == 1:
                return None
            return fecha_val.date().isoformat()

        # Handle date objects
        if isinstance(fecha_val, date):
            if fecha_val.year == 0 or fecha_val.year == 1:
                return None
            return fecha_val.isoformat()

        # Handle strings
        try:
            fecha_str = str(fecha_val).strip()
            if fecha_str in ('', 'NULL', '0000-00-00', 'None'):
                return None
            # Handle both date and datetime string formats
            if 'T' in fecha_str:
                # Format: "2020-01-01T00:00:00" -> take only date part
                fecha_str = fecha_str.split('T')[0]
            if ' ' in fecha_str:
                # Format: "2020-01-01 00:00:00" -> take only date part
                fecha_str = fecha_str.split(' ')[0]
            if '-' in fecha_str:
                parts = fecha_str.split('-')
                if len(parts) == 3 and int(parts[0]) > 1:
                    return fecha_str[:10]
        except (ValueError, AttributeError, IndexError):
            pass
        return None

    async def generar_csv_desde_mysql(self, csv_path: str):
        """Genera CSV desde MySQL."""
        print("\nGenerando CSV desde MySQL...", flush=True)

        registros = 0
        errores = 0
        omitidos_sin_miembro = 0
        omitidos_sin_agrupacion = 0

        async with get_mysql_connection() as mysql_conn:
            async with mysql_conn.cursor() as cursor:
                query = """
                    SELECT
                        ANIOCUOTA, CODmiembro, CODCUOTA, CODAGRUPACION,
                        IMPORTECUOTAANIOEL, NOMBRECUOTA, IMPORTECUOTAANIOmiembro,
                        IMPORTECUOTAANIOPAGADA, IMPORTEGASTOSABONOCUOTA,
                        FECHAPAGO, FECHAANOTACION, MODOINGRESO, CUENTAPAGO,
                        ESTADOCUOTA, ORDENARCOBROBANCO, OBSERVACIONES, NOMARCHIVOSEPAXML
                    FROM CUOTAANIOmiembro
                    ORDER BY ANIOCUOTA, CODmiembro
                """
                await cursor.execute(query)

                with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)

                    while True:
                        rows = await cursor.fetchmany(1000)
                        if not rows:
                            break

                        for row in rows:
                            try:
                                ejercicio = int(row[0]) if row[0] else None
                                coduser = int(row[1]) if row[1] else None

                                if not ejercicio or not coduser:
                                    errores += 1
                                    continue

                                # Obtener UUID del miembro
                                miembro_id = self.cache_miembros.get(coduser)
                                if not miembro_id:
                                    omitidos_sin_miembro += 1
                                    continue

                                # Obtener tipo de miembro
                                tipo_miembro_id = self.miembro_tipo.get(miembro_id)
                                if not tipo_miembro_id:
                                    omitidos_sin_miembro += 1
                                    continue

                                # Obtener agrupación
                                codagrupacion = str(row[3]).lstrip('0') if row[3] else None  # Strip leading zeros
                                # Handle special case: if all zeros, result is empty string
                                if codagrupacion == '':
                                    codagrupacion = '0'
                                agrupacion_id = self.cache_agrupaciones.get(codagrupacion) if codagrupacion else None

                                # Si no existe la agrupación, usar la agrupación provincial del miembro
                                if not agrupacion_id:
                                    provincia_id = self.miembro_provincia.get(miembro_id)
                                    if provincia_id:
                                        agrupacion_id = self.provincia_agrupacion.get(provincia_id)

                                # Si aún no hay agrupación, omitir
                                if not agrupacion_id:
                                    omitidos_sin_agrupacion += 1
                                    continue

                                # Obtener importe_cuota_anio_id
                                importe_cuota_anio_id = self.cache_importes_cuota.get((ejercicio, tipo_miembro_id))

                                # Importes
                                importe = Decimal(str(row[6])) if row[6] else Decimal('0.00')  # IMPORTECUOTAANIOmiembro
                                importe_pagado = Decimal(str(row[7])) if row[7] else Decimal('0.00')  # IMPORTECUOTAANIOPAGADA
                                gastos_gestion = Decimal(str(row[8])) if row[8] else Decimal('0.00')  # IMPORTEGASTOSABONOCUOTA

                                # Fechas
                                fecha_pago = self.parse_fecha(row[9])  # FECHAPAGO
                                fecha_vencimiento = self.parse_fecha(row[10])  # FECHAANOTACION (se usa como vencimiento)

                                # Modo de ingreso
                                modo_ingreso = self.mapear_modo_ingreso(row[11])  # MODOINGRESO

                                # Calcular estado
                                fecha_venc_obj = datetime.strptime(fecha_vencimiento, '%Y-%m-%d').date() if fecha_vencimiento else None
                                estado_codigo = self.calcular_estado_cuota(importe, importe_pagado, fecha_venc_obj)
                                estado_id = self.estados.get(estado_codigo, self.estados.get('PENDIENTE'))

                                # Observaciones
                                observaciones = str(row[15]).strip() if row[15] else None

                                # Referencia de pago
                                referencia_pago = str(row[14]).strip() if row[14] else None  # ORDENARCOBROBANCO

                                # Generar UUID para la cuota
                                cuota_uuid = str(uuid.uuid4())

                                # Escribir fila CSV
                                writer.writerow([
                                    cuota_uuid,  # id
                                    miembro_id,  # miembro_id
                                    ejercicio,  # ejercicio
                                    agrupacion_id,  # agrupacion_id
                                    importe_cuota_anio_id,  # importe_cuota_anio_id
                                    str(importe),  # importe
                                    str(importe_pagado),  # importe_pagado
                                    str(gastos_gestion),  # gastos_gestion
                                    estado_id,  # estado_id
                                    modo_ingreso,  # modo_ingreso
                                    fecha_pago,  # fecha_pago
                                    fecha_vencimiento,  # fecha_vencimiento
                                    observaciones,  # observaciones
                                    referencia_pago,  # referencia_pago
                                ])

                                registros += 1
                                if registros % 1000 == 0:
                                    print(f"  Procesados {registros} registros...", flush=True)

                            except Exception as e:
                                errores += 1
                                if errores < 10:
                                    print(f"  [WARN] Error en row: {e}", flush=True)

        print(f"  [OK] CSV generado: {registros} registros (errores: {errores})", flush=True)
        print(f"  [INFO] Omitidos sin miembro: {omitidos_sin_miembro}", flush=True)
        print(f"  [INFO] Omitidos sin agrupación: {omitidos_sin_agrupacion}", flush=True)
        return registros

    async def importar_csv_a_postgres(self, session: AsyncSession, csv_path: str):
        """Importa CSV a PostgreSQL usando inserción por lotes."""
        print("\nImportando CSV a PostgreSQL...", flush=True)

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
            INSERT INTO cuotas_anuales (
                id, miembro_id, ejercicio, agrupacion_id, importe_cuota_anio_id,
                importe, importe_pagado, gastos_gestion, estado_id, modo_ingreso,
                fecha_pago, fecha_vencimiento, observaciones, referencia_pago,
                fecha_creacion, eliminado
            ) VALUES (
                :id, :miembro_id, :ejercicio, :agrupacion_id, :importe_cuota_anio_id,
                :importe, :importe_pagado, :gastos_gestion, :estado_id, :modo_ingreso,
                :fecha_pago, :fecha_vencimiento, :observaciones, :referencia_pago,
                :fecha_creacion, :eliminado
            )
        """)

        for row in lote:
            # Convertir fechas de string a date objects
            fecha_pago = None
            if row[10]:
                try:
                    fecha_pago = datetime.strptime(row[10], '%Y-%m-%d').date()
                except ValueError:
                    pass

            fecha_vencimiento = None
            if row[11]:
                try:
                    fecha_vencimiento = datetime.strptime(row[11], '%Y-%m-%d').date()
                except ValueError:
                    pass

            params = {
                'id': row[0],
                'miembro_id': row[1],
                'ejercicio': int(row[2]),
                'agrupacion_id': row[3],
                'importe_cuota_anio_id': row[4] if row[4] else None,
                'importe': Decimal(row[5]),
                'importe_pagado': Decimal(row[6]),
                'gastos_gestion': Decimal(row[7]),
                'estado_id': row[8],
                'modo_ingreso': row[9] if row[9] else None,
                'fecha_pago': fecha_pago,
                'fecha_vencimiento': fecha_vencimiento,
                'observaciones': row[12] if row[12] else None,
                'referencia_pago': row[13] if row[13] else None,
                'fecha_creacion': datetime.now(),
                'eliminado': False,
            }
            await session.execute(insert_sql, params)

        await session.flush()


async def main():
    """Función principal."""
    print("\n" + "="*80, flush=True)
    print("IMPORTACION DE CUOTAS ANUALES (CSV + BATCH INSERT)", flush=True)
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
    csv_path = os.path.join(tempfile.gettempdir(), 'cuotas_anuales_import.csv')

    try:
        async with async_session() as session:
            importador = ImportadorCuotasAnualesCSV()

            # Cargar caches
            await importador.cargar_caches(session)

            # Generar CSV desde MySQL
            total_registros = await importador.generar_csv_desde_mysql(csv_path)

            # Importar CSV a PostgreSQL
            await importador.importar_csv_a_postgres(session, csv_path)

            # Commit
            await session.commit()

            print("\n" + "="*80, flush=True)
            print("[OK] IMPORTACION COMPLETADA", flush=True)
            print("="*80, flush=True)
            print(f"\nCuotas anuales importadas: {total_registros}", flush=True)

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
