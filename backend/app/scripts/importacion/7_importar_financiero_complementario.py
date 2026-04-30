"""
Script para importar datos financieros complementarios desde MySQL.

Importa las tablas:
- DONACIONCONCEPTOS → concepto_donacion (catálogo)
- DONACION → donaciones
- REMESAS_SEPAXML → remesas
- ORDENES_COBRO → ordenes_cobro

Este script debe ejecutarse DESPUÉS de importar cuotas anuales.
"""
import asyncio
import uuid
import csv
import tempfile
from decimal import Decimal
from typing import Optional
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from app.core.database import get_database_url
from app.scripts.importacion.mysql_helper import get_mysql_connection


class ImportadorFinancieroComplementario:
    """Importa datos financieros complementarios desde MySQL."""

    def __init__(self):
        self.cache_miembros: dict[int, str] = {}  # CODUSER → UUID
        self.cache_conceptos: dict[str, str] = {}  # codigo → UUID
        self.cache_remesas: dict[str, str] = {}  # referencia → UUID
        self.cache_cuotas: dict[tuple, str] = {}  # (miembro_id, ejercicio) → cuota_id
        self.cache_agrupaciones: dict[str, str] = {}  # codigo → UUID
        self.estado_donacion_recibida: str = ""  # UUID del estado RECIBIDA
        self.estado_remesa_procesada: str = ""  # UUID del estado PROCESADA para remesas
        self.estado_remesa_generada: str = ""  # UUID del estado GENERADA para remesas
        self.estado_orden_pendiente: str = ""  # UUID del estado PENDIENTE para órdenes
        self.estado_orden_procesada: str = ""  # UUID del estado PROCESADA para órdenes
        self.estado_orden_fallida: str = ""  # UUID del estado FALLIDA para órdenes
        self.stats = {
            'conceptos': 0,
            'donaciones': 0,
            'donaciones_omitidas': 0,
            'remesas': 0,
            'ordenes_cobro': 0,
            'ordenes_omitidas': 0
        }

    def parse_fecha(self, fecha_val) -> Optional[date]:
        """Parsea fecha desde MySQL."""
        if not fecha_val:
            return None
        if isinstance(fecha_val, datetime):
            return fecha_val.date()
        if isinstance(fecha_val, date):
            return fecha_val
        try:
            fecha_str = str(fecha_val).strip()
            if fecha_str in ('', 'NULL', '0000-00-00', 'None'):
                return None
            if 'T' in fecha_str:
                fecha_str = fecha_str.split('T')[0]
            if ' ' in fecha_str:
                fecha_str = fecha_str.split(' ')[0]
            return datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except (ValueError, AttributeError):
            return None

    async def cargar_caches(self, session: AsyncSession):
        """Carga caches necesarios."""
        print("\nCargando caches...", flush=True)

        # Cargar miembros
        result = await session.execute(
            text("SELECT old_id, new_uuid FROM temp_id_mapping WHERE tabla = 'MIEMBRO'")
        )
        for row in result:
            self.cache_miembros[int(row[0])] = str(row[1])

        # Cargar agrupaciones
        result = await session.execute(
            text("SELECT codigo, id FROM agrupaciones_territoriales")
        )
        for row in result:
            self.cache_agrupaciones[str(row[0])] = str(row[1])

        # Cargar cuotas para relacionar órdenes de cobro
        result = await session.execute(
            text("SELECT miembro_id, ejercicio, id FROM cuotas_anuales")
        )
        for row in result:
            key = (str(row[0]), int(row[1]))
            self.cache_cuotas[key] = str(row[2])

        # Cargar estado RECIBIDA para donaciones
        result = await session.execute(
            text("SELECT id FROM estados_donacion WHERE codigo = 'RECIBIDA'")
        )
        row = result.fetchone()
        if row:
            self.estado_donacion_recibida = str(row[0])

        # Cargar estados de remesas
        result = await session.execute(
            text("SELECT id, codigo FROM estados_remesa WHERE codigo IN ('PROCESADA', 'GENERADA')")
        )
        for row in result:
            if row[1] == 'PROCESADA':
                self.estado_remesa_procesada = str(row[0])
            elif row[1] == 'GENERADA':
                self.estado_remesa_generada = str(row[0])

        # Cargar estados de órdenes de cobro
        result = await session.execute(
            text("SELECT id, codigo FROM estados_orden_cobro WHERE codigo IN ('PENDIENTE', 'PROCESADA', 'FALLIDA')")
        )
        for row in result:
            if row[1] == 'PENDIENTE':
                self.estado_orden_pendiente = str(row[0])
            elif row[1] == 'PROCESADA':
                self.estado_orden_procesada = str(row[0])
            elif row[1] == 'FALLIDA':
                self.estado_orden_fallida = str(row[0])

        print(f"  [OK] Caches cargados:")
        print(f"    Miembros: {len(self.cache_miembros)}")
        print(f"    Agrupaciones: {len(self.cache_agrupaciones)}")
        print(f"    Cuotas: {len(self.cache_cuotas)}")
        print(f"    Estado donacion RECIBIDA: {self.estado_donacion_recibida[:8] if self.estado_donacion_recibida else 'N/A'}...")
        print(f"    Estado remesa PROCESADA: {self.estado_remesa_procesada[:8] if self.estado_remesa_procesada else 'N/A'}...")
        print(f"    Estados orden cobro: {bool(self.estado_orden_pendiente and self.estado_orden_procesada)}")

    async def importar_donaciones_conceptos(self, session: AsyncSession):
        """Importa DONACIONCONCEPTOS."""
        print("\nImportando conceptos de donación...", flush=True)

        async with get_mysql_connection() as mysql_conn:
            async with mysql_conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT CONCEPTO, NOMBRECONCEPTO, FECHACREACIONCONCEPTO, OBSERVACIONES
                    FROM donacionconceptos
                """)
                rows = await cursor.fetchall()

                for row in rows:
                    codigo_orig = str(row[0]).strip() if row[0] else None
                    nombre = str(row[1]).strip() if row[1] else None

                    if not codigo_orig:
                        continue

                    # Truncar código a 20 caracteres máximo
                    codigo = codigo_orig[:20] if len(codigo_orig) > 20 else codigo_orig

                    # Verificar si existe
                    result = await session.execute(
                        text("SELECT id FROM donaciones_conceptos WHERE codigo = :codigo"),
                        {"codigo": codigo}
                    )
                    existe = result.fetchone()

                    if existe:
                        self.cache_conceptos[codigo] = str(existe[0])
                        continue

                    concepto_id = str(uuid.uuid4())
                    await session.execute(
                        text("""
                            INSERT INTO donaciones_conceptos (id, codigo, nombre, activo, fecha_creacion, eliminado)
                            VALUES (:id, :codigo, :nombre, true, :fecha_creacion, false)
                        """),
                        {
                            "id": concepto_id,
                            "codigo": codigo,
                            "nombre": nombre or f"Concepto {codigo}",
                            "fecha_creacion": datetime.now()
                        }
                    )
                    # Guardar mapeo con código original Y truncado
                    self.cache_conceptos[codigo_orig] = concepto_id
                    self.cache_conceptos[codigo] = concepto_id
                    self.stats['conceptos'] += 1

        print(f"  [OK] {self.stats['conceptos']} conceptos importados")

    async def importar_donaciones(self, session: AsyncSession):
        """Importa DONACION."""
        print("\nImportando donaciones...", flush=True)

        async with get_mysql_connection() as mysql_conn:
            async with mysql_conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT
                        CODDONACION, NUMDOCUMENTOMIEMBRO, TIPODOCUMENTOMIEMBRO,
                        APE1, APE2, NOM, EMAIL, CODAGRUPACION,
                        IMPORTEDONACION, GASTOSDONACION, FECHAINGRESO,
                        FECHAANOTACION, MODOINGRESO, CONCEPTO, OBSERVACIONES
                    FROM donacion
                    ORDER BY CODDONACION
                """)

                batch = []
                processed = 0

                while True:
                    rows = await cursor.fetchmany(500)
                    if not rows:
                        break

                    for row in rows:
                        fecha_donacion = self.parse_fecha(row[10])  # FECHAINGRESO

                        if not fecha_donacion:
                            self.stats['donaciones_omitidas'] += 1
                            continue

                        importe = Decimal(str(row[8])) if row[8] else Decimal('0.00')
                        gastos = Decimal(str(row[9])) if row[9] else Decimal('0.00')  # GASTOSDONACION
                        concepto_cod = str(row[13]).strip() if row[13] else None
                        concepto_id = self.cache_conceptos.get(concepto_cod)

                        # Datos del donante (para referencia, no relacionamos con miembro)
                        nombre_donante = f"{row[5] or ''} {row[3] or ''} {row[4] or ''}".strip()
                        documento = str(row[1]).strip() if row[1] else None

                        donacion_id = str(uuid.uuid4())
                        batch.append({
                            "id": donacion_id,
                            "concepto_id": concepto_id,
                            "estado_id": self.estado_donacion_recibida,
                            "fecha": fecha_donacion,
                            "importe": importe,
                            "gastos": gastos,
                            "donante_nombre": nombre_donante or None,
                            "donante_dni": documento,
                            "observaciones": str(row[14]).strip() if row[14] else None,
                            "certificado_emitido": False,
                            "anonima": False,
                            "fecha_creacion": datetime.now(),
                            "eliminado": False
                        })

                    # Insertar lote
                    if batch:
                        for params in batch:
                            await session.execute(
                                text("""
                                    INSERT INTO donaciones (
                                        id, concepto_id, estado_id, fecha, importe, gastos,
                                        donante_nombre, donante_dni, observaciones,
                                        certificado_emitido, anonima,
                                        fecha_creacion, eliminado
                                    ) VALUES (
                                        :id, :concepto_id, :estado_id, :fecha, :importe, :gastos,
                                        :donante_nombre, :donante_dni, :observaciones,
                                        :certificado_emitido, :anonima,
                                        :fecha_creacion, :eliminado
                                    )
                                """),
                                params
                            )
                        self.stats['donaciones'] += len(batch)
                        batch = []

                    processed += len(rows)
                    if processed % 500 == 0:
                        print(f"  Procesadas {processed} donaciones...", flush=True)

                await session.flush()

        print(f"  [OK] {self.stats['donaciones']} donaciones importadas")
        if self.stats['donaciones_omitidas'] > 0:
            print(f"  [INFO] {self.stats['donaciones_omitidas']} omitidas (sin fecha válida)")

    async def importar_remesas(self, session: AsyncSession):
        """Importa REMESAS_SEPAXML."""
        print("\nImportando remesas SEPA...", flush=True)

        if not self.estado_remesa_procesada:
            print("  [WARN] No se encontró estado PROCESADA para remesas. Omitiendo...")
            return

        async with get_mysql_connection() as mysql_conn:
            async with mysql_conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT
                        NOMARCHIVOSEPAXML, ANIOCUOTA, FECHA_CREACION_ARCHIVO_SEPA,
                        FECHAORDENCOBRO, FECHAPAGO, IMPORTEREMESA, IMPORTEGASTOSREMESA,
                        NUMRECIBOS, OBSERVACIONES
                    FROM remesas_sepaxml
                    ORDER BY FECHA_CREACION_ARCHIVO_SEPA
                """)
                rows = await cursor.fetchall()

                for row in rows:
                    referencia = str(row[0]).strip() if row[0] else None

                    if not referencia:
                        continue

                    # Truncar referencia si es muy larga (máx 100)
                    referencia = referencia[:100] if len(referencia) > 100 else referencia

                    # Verificar si existe
                    result = await session.execute(
                        text("SELECT id FROM remesas WHERE referencia = :referencia"),
                        {"referencia": referencia}
                    )
                    existe = result.fetchone()

                    if existe:
                        self.cache_remesas[referencia] = str(existe[0])
                        continue

                    fecha_creacion_remesa = self.parse_fecha(row[2])
                    fecha_cobro = self.parse_fecha(row[4]) or self.parse_fecha(row[3])  # FECHAPAGO o FECHAORDENCOBRO
                    importe_total = Decimal(str(row[5])) if row[5] else Decimal('0.00')
                    gastos = Decimal(str(row[6])) if row[6] else Decimal('0.00')
                    num_ordenes = int(row[7]) if row[7] else 0

                    # Determinar estado según si tiene fecha de cobro
                    estado_id = self.estado_remesa_procesada if fecha_cobro else self.estado_remesa_generada

                    remesa_id = str(uuid.uuid4())
                    await session.execute(
                        text("""
                            INSERT INTO remesas (
                                id, referencia, fecha_creacion, fecha_envio, fecha_cobro,
                                importe_total, gastos, num_ordenes, estado_id,
                                archivo_sepa, observaciones, eliminado
                            ) VALUES (
                                :id, :referencia, :fecha_creacion, :fecha_envio, :fecha_cobro,
                                :importe_total, :gastos, :num_ordenes, :estado_id,
                                :archivo_sepa, :observaciones, :eliminado
                            )
                        """),
                        {
                            "id": remesa_id,
                            "referencia": referencia,
                            "fecha_creacion": fecha_creacion_remesa or date.today(),
                            "fecha_envio": fecha_creacion_remesa,  # Asumimos enviada en fecha creación
                            "fecha_cobro": fecha_cobro or date.today(),  # Requerido, usar hoy si no hay
                            "importe_total": importe_total,
                            "gastos": gastos,
                            "num_ordenes": num_ordenes,
                            "estado_id": estado_id,
                            "archivo_sepa": referencia,  # El nombre del archivo es la referencia
                            "observaciones": str(row[8]).strip() if row[8] else None,
                            "eliminado": False
                        }
                    )
                    self.cache_remesas[referencia] = remesa_id
                    self.stats['remesas'] += 1

        print(f"  [OK] {self.stats['remesas']} remesas importadas")

    async def importar_ordenes_cobro(self, session: AsyncSession):
        """Importa ORDENES_COBRO."""
        print("\nImportando órdenes de cobro...", flush=True)

        if not self.estado_orden_pendiente or not self.estado_orden_procesada:
            print("  [WARN] No se encontraron estados para órdenes de cobro. Omitiendo...")
            return

        async with get_mysql_connection() as mysql_conn:
            async with mysql_conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT
                        CODmiembro, ANIOCUOTA, NOMARCHIVOSEPAXML,
                        IMPORTECUOTAANIOmiembro, IMPORTECUOTAANIOPAGADA, ESTADOCUOTA,
                        FECHAORDENCOBRO, FECHAPAGO
                    FROM ordenes_cobro
                    ORDER BY ANIOCUOTA, CODmiembro
                """)

                batch = []
                processed = 0

                while True:
                    rows = await cursor.fetchmany(1000)
                    if not rows:
                        break

                    for row in rows:
                        codmiembro = int(row[0]) if row[0] else None
                        ejercicio = int(row[1]) if row[1] else None
                        referencia_remesa = str(row[2]).strip()[:100] if row[2] else None

                        if not codmiembro or not ejercicio:
                            self.stats['ordenes_omitidas'] += 1
                            continue

                        # Obtener miembro_id
                        miembro_id = self.cache_miembros.get(codmiembro)
                        if not miembro_id:
                            self.stats['ordenes_omitidas'] += 1
                            continue

                        # Obtener cuota_id (requerido - NOT NULL)
                        cuota_id = self.cache_cuotas.get((miembro_id, ejercicio))
                        if not cuota_id:
                            self.stats['ordenes_omitidas'] += 1
                            continue

                        # Obtener remesa_id (requerido - NOT NULL)
                        remesa_id = self.cache_remesas.get(referencia_remesa) if referencia_remesa else None
                        if not remesa_id:
                            self.stats['ordenes_omitidas'] += 1
                            continue

                        importe = Decimal(str(row[3])) if row[3] else Decimal('0.00')
                        estado_mysql = str(row[5]).strip().upper() if row[5] else ''
                        fecha_pago = self.parse_fecha(row[7])

                        # Mapear estado a UUID (ABONADA = procesada, NOABONADA-DEVUELTA = fallida)
                        if estado_mysql == 'ABONADA':
                            estado_id = self.estado_orden_procesada
                        elif 'DEVUELTA' in estado_mysql or 'NOABONADA' in estado_mysql:
                            estado_id = self.estado_orden_fallida
                        else:
                            estado_id = self.estado_orden_pendiente

                        fecha_orden = self.parse_fecha(row[6])  # FECHAORDENCOBRO
                        orden_id = str(uuid.uuid4())
                        batch.append({
                            "id": orden_id,
                            "remesa_id": remesa_id,
                            "cuota_id": cuota_id,
                            "importe": importe,
                            "estado_id": estado_id,
                            "fecha_procesamiento": fecha_pago,
                            "fecha_creacion": fecha_orden or datetime.now(),
                            "eliminado": False
                        })

                    # Insertar lote
                    if batch:
                        for params in batch:
                            await session.execute(
                                text("""
                                    INSERT INTO ordenes_cobro (
                                        id, remesa_id, cuota_id, importe, estado_id,
                                        fecha_procesamiento, fecha_creacion, eliminado
                                    ) VALUES (
                                        :id, :remesa_id, :cuota_id, :importe, :estado_id,
                                        :fecha_procesamiento, :fecha_creacion, :eliminado
                                    )
                                """),
                                params
                            )
                        self.stats['ordenes_cobro'] += len(batch)
                        batch = []

                    processed += len(rows)
                    if processed % 1000 == 0:
                        print(f"  Procesadas {processed} órdenes...", flush=True)

                await session.flush()

        print(f"  [OK] {self.stats['ordenes_cobro']} órdenes de cobro importadas")
        if self.stats['ordenes_omitidas'] > 0:
            print(f"  [INFO] {self.stats['ordenes_omitidas']} omitidas (sin miembro/cuota/remesa)")


async def main():
    """Función principal."""

    print("\n" + "="*80)
    print("IMPORTACIÓN DE DATOS FINANCIEROS COMPLEMENTARIOS")
    print("="*80 + "\n")

    # Conectar a PostgreSQL
    print("Conectando a PostgreSQL...")
    database_url = get_database_url()
    engine = create_async_engine(
        database_url,
        echo=False,
        connect_args={"server_settings": {"jit": "off"}, "statement_cache_size": 0}
    )
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            importador = ImportadorFinancieroComplementario()

            # Cargar caches
            await importador.cargar_caches(session)

            # Importar conceptos de donación
            await importador.importar_donaciones_conceptos(session)

            # Importar donaciones
            await importador.importar_donaciones(session)

            # Importar remesas
            await importador.importar_remesas(session)

            # Importar órdenes de cobro
            await importador.importar_ordenes_cobro(session)

            # Commit
            await session.commit()

            print("\n" + "="*80)
            print("[OK] IMPORTACIÓN COMPLETADA")
            print("="*80)
            print(f"\nResumen:")
            print(f"  Conceptos donación: {importador.stats['conceptos']}")
            print(f"  Donaciones: {importador.stats['donaciones']} (omitidas: {importador.stats['donaciones_omitidas']})")
            print(f"  Remesas SEPA: {importador.stats['remesas']}")
            print(f"  Órdenes cobro: {importador.stats['ordenes_cobro']} (omitidas: {importador.stats['ordenes_omitidas']})")

        except Exception as e:
            await session.rollback()
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
