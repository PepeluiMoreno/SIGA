"""
Script para importar datos financieros complementarios desde el dump MySQL.

Importa las tablas:
- DONACION → donaciones
- DONACIONCONCEPTOS → donacion_conceptos
- REMESAS_SEPAXML → remesas
- ORDENES_COBRO + históricas → ordenes_cobro

Este script debe ejecutarse DESPUÉS de importar cuotas anuales.
"""
import asyncio
import uuid
import pymysql
from decimal import Decimal
from typing import Optional
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.database import get_database_url
from app.domains.financiero.models.donaciones import Donacion, ConceptoDonacion
from app.domains.financiero.models.remesas import Remesa, OrdenCobro
from app.domains.miembros.models.miembro import Miembro


# Configuración de conexión MySQL (ajustar según necesidad)
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Ajustar
    'database': 'europalaica_com',
    'charset': 'utf8mb4'
}


class MapeadorFinancieroComplementario:
    """Mapea datos financieros complementarios de MySQL a PostgreSQL."""

    def __init__(self):
        self.cache_miembros: dict[int, uuid.UUID] = {}
        self.cache_conceptos: dict[int, uuid.UUID] = {}
        self.cache_remesas: dict[int, uuid.UUID] = {}

    def convertir_fecha(self, valor) -> Optional[date]:
        """Convierte un valor de MySQL a date de Python."""
        if not valor:
            return None
        if isinstance(valor, date):
            return valor
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, str):
            try:
                return date.fromisoformat(valor)
            except:
                pass
        return None

    async def obtener_uuid_miembro(self, session: AsyncSession, coduser: int) -> Optional[uuid.UUID]:
        """Obtiene el UUID de un miembro desde temp_id_mapping o caché."""
        if coduser in self.cache_miembros:
            return self.cache_miembros[coduser]

        result = await session.execute(
            """
            SELECT new_uuid FROM temp_id_mapping
            WHERE tabla = 'MIEMBRO' AND old_id = :old_id
            """,
            {"old_id": coduser}
        )
        row = result.fetchone()

        if row:
            self.cache_miembros[coduser] = row[0]
            return row[0]

        return None

    async def importar_conceptos_donacion(self, session: AsyncSession, mysql_conn):
        """Importa la tabla DONACIONCONCEPTOS."""

        print("\nImportando conceptos de donación...")

        cursor = mysql_conn.cursor(pymysql.cursors.DictCursor)

        # Verificar si la tabla existe
        cursor.execute("SHOW TABLES LIKE 'DONACIONCONCEPTOS'")
        if not cursor.fetchone():
            print("  ⚠ Tabla DONACIONCONCEPTOS no existe, se omite")
            cursor.close()
            return

        cursor.execute("""
            SELECT
                CODCONCEPTO,
                CONCEPTO,
                ACTIVO
            FROM DONACIONCONCEPTOS
            ORDER BY CODCONCEPTO
        """)

        importados = 0

        for row in cursor:
            codconcepto = row['CODCONCEPTO']

            # Verificar si ya existe
            result = await session.execute(
                select(ConceptoDonacion).where(ConceptoDonacion.codigo == str(codconcepto))
            )
            existe = result.scalar_one_or_none()

            if existe:
                self.cache_conceptos[codconcepto] = existe.id
                continue

            concepto = ConceptoDonacion(
                codigo=str(codconcepto),
                nombre=row['CONCEPTO'].strip() if row['CONCEPTO'] else f"Concepto {codconcepto}",
                activo=bool(row['ACTIVO']) if row['ACTIVO'] is not None else True
            )

            session.add(concepto)
            await session.flush()

            self.cache_conceptos[codconcepto] = concepto.id
            importados += 1

        cursor.close()

        print(f"  ✓ {importados} conceptos de donación importados")

    async def importar_donaciones(self, session: AsyncSession, mysql_conn):
        """Importa la tabla DONACION."""

        print("\nImportando donaciones...")

        cursor = mysql_conn.cursor(pymysql.cursors.DictCursor)

        # Verificar si la tabla existe
        cursor.execute("SHOW TABLES LIKE 'DONACION'")
        if not cursor.fetchone():
            print("  ⚠ Tabla DONACION no existe, se omite")
            cursor.close()
            return

        cursor.execute("""
            SELECT
                CODUSER,
                CODCONCEPTO,
                FECHADONACION,
                IMPORTE,
                OBSERVACIONES
            FROM DONACION
            ORDER BY FECHADONACION
        """)

        importadas = 0
        omitidas = 0

        for row in cursor:
            # Obtener UUID del miembro
            miembro_id = await self.obtener_uuid_miembro(session, row['CODUSER']) if row['CODUSER'] else None

            # Obtener UUID del concepto
            concepto_id = self.cache_conceptos.get(row['CODCONCEPTO']) if row['CODCONCEPTO'] else None

            # Procesar fecha
            fecha_donacion = self.convertir_fecha(row['FECHADONACION'])

            if not fecha_donacion:
                omitidas += 1
                continue

            # Procesar importe
            importe = Decimal(str(row['IMPORTE'])) if row['IMPORTE'] else Decimal('0.00')

            donacion = Donacion(
                miembro_id=miembro_id,
                concepto_id=concepto_id,
                fecha=fecha_donacion,
                importe=importe,
                observaciones=row['OBSERVACIONES'].strip() if row['OBSERVACIONES'] else None
            )

            session.add(donacion)
            importadas += 1

            if importadas % 100 == 0:
                print(f"  Procesadas {importadas} donaciones...")

        cursor.close()

        await session.flush()

        print(f"  ✓ {importadas} donaciones importadas")
        if omitidas > 0:
            print(f"  ⚠ {omitidas} donaciones omitidas (sin fecha válida)")

    async def importar_remesas(self, session: AsyncSession, mysql_conn):
        """Importa la tabla REMESAS_SEPAXML."""

        print("\nImportando remesas SEPA...")

        cursor = mysql_conn.cursor(pymysql.cursors.DictCursor)

        # Verificar si la tabla existe
        cursor.execute("SHOW TABLES LIKE 'REMESAS_SEPAXML'")
        if not cursor.fetchone():
            print("  ⚠ Tabla REMESAS_SEPAXML no existe, se omite")
            cursor.close()
            return

        cursor.execute("""
            SELECT
                CODREMESA,
                FECHAEMISION,
                FECHACOBRO,
                NUMEROREMESA,
                IMPORTETOTAL,
                ESTADO,
                OBSERVACIONES
            FROM REMESAS_SEPAXML
            ORDER BY CODREMESA
        """)

        importadas = 0

        for row in cursor:
            codremesa = row['CODREMESA']

            # Verificar si ya existe por número de remesa
            numero_remesa = row['NUMEROREMESA'].strip() if row['NUMEROREMESA'] else None

            if numero_remesa:
                result = await session.execute(
                    select(Remesa).where(Remesa.numero_remesa == numero_remesa)
                )
                existe = result.scalar_one_or_none()

                if existe:
                    self.cache_remesas[codremesa] = existe.id
                    continue

            # Procesar fechas
            fecha_emision = self.convertir_fecha(row['FECHAEMISION'])
            fecha_cobro = self.convertir_fecha(row['FECHACOBRO'])

            # Procesar importe
            importe_total = Decimal(str(row['IMPORTETOTAL'])) if row['IMPORTETOTAL'] else Decimal('0.00')

            remesa = Remesa(
                numero_remesa=numero_remesa or f"REM-{codremesa}",
                fecha_emision=fecha_emision or date.today(),
                fecha_cobro=fecha_cobro,
                importe_total=importe_total,
                estado=row['ESTADO'].strip() if row['ESTADO'] else 'PENDIENTE',
                observaciones=row['OBSERVACIONES'].strip() if row['OBSERVACIONES'] else None
            )

            session.add(remesa)
            await session.flush()

            self.cache_remesas[codremesa] = remesa.id
            importadas += 1

        cursor.close()

        print(f"  ✓ {importadas} remesas importadas")

    async def importar_ordenes_cobro(self, session: AsyncSession, mysql_conn):
        """
        Importa todas las tablas de órdenes de cobro (actuales e históricas).

        Tablas a consolidar:
        - ORDENES_COBRO
        - ORDEN_COBRO_2013
        - ORDEN_COBRO_2014_05_19
        - ... (todas las variantes históricas)
        """

        print("\nImportando órdenes de cobro...")

        cursor = mysql_conn.cursor()

        # Obtener todas las tablas que empiezan con 'ORDEN'
        cursor.execute("SHOW TABLES LIKE 'ORDEN%'")
        tablas_ordenes = [row[0] for row in cursor.fetchall()]

        print(f"  Tablas de órdenes encontradas: {len(tablas_ordenes)}")

        importadas = 0
        omitidas = 0

        for tabla in tablas_ordenes:
            print(f"  Procesando {tabla}...")

            cursor_dict = mysql_conn.cursor(pymysql.cursors.DictCursor)

            try:
                # Intentar leer con campos estándar
                cursor_dict.execute(f"""
                    SELECT
                        CODUSER,
                        ANIO,
                        FECHAEMISION,
                        IMPORTE,
                        REFERENCIAPAGO,
                        ESTADO
                    FROM {tabla}
                    LIMIT 1000
                """)

                for row in cursor_dict:
                    # Obtener UUID del miembro
                    miembro_id = await self.obtener_uuid_miembro(session, row['CODUSER']) if row['CODUSER'] else None

                    if not miembro_id:
                        omitidas += 1
                        continue

                    # Procesar fecha
                    fecha_emision = self.convertir_fecha(row['FECHAEMISION'])

                    # Procesar importe
                    importe = Decimal(str(row['IMPORTE'])) if row['IMPORTE'] else Decimal('0.00')

                    # NOTA: El modelo OrdenCobro necesita cuota_id, pero como consolidamos tablas históricas,
                    # algunas órdenes pueden no tener cuota asociada directa.
                    # Se puede omitir cuota_id si es opcional, o buscar la cuota por miembro+año

                    # Buscar cuota correspondiente
                    from app.domains.financiero.models.cuotas import CuotaAnual

                    result = await session.execute(
                        select(CuotaAnual).where(
                            CuotaAnual.miembro_id == miembro_id,
                            CuotaAnual.ejercicio == row['ANIO']
                        )
                    )
                    cuota = result.scalar_one_or_none()

                    if not cuota:
                        omitidas += 1
                        continue

                    orden = OrdenCobro(
                        cuota_id=cuota.id,
                        fecha_emision=fecha_emision or date.today(),
                        importe=importe,
                        referencia=row['REFERENCIAPAGO'].strip() if row['REFERENCIAPAGO'] else None,
                        estado=row['ESTADO'].strip() if row['ESTADO'] else 'PENDIENTE'
                    )

                    session.add(orden)
                    importadas += 1

                    if importadas % 200 == 0:
                        await session.flush()

            except Exception as e:
                print(f"    ⚠ Error procesando {tabla}: {e}")

            cursor_dict.close()

        cursor.close()

        await session.flush()

        print(f"  ✓ {importadas} órdenes de cobro importadas")
        if omitidas > 0:
            print(f"  ⚠ {omitidas} órdenes omitidas (sin miembro o cuota)")


async def main():
    """Función principal."""

    print("\n" + "="*80)
    print("IMPORTACIÓN DE DATOS FINANCIEROS COMPLEMENTARIOS")
    print("="*80 + "\n")

    # Conectar a MySQL
    print("Conectando a MySQL...")
    try:
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        print("  ✓ Conexión MySQL establecida")
    except Exception as e:
        print(f"  ✗ Error conectando a MySQL: {e}")
        print("\n  Ajusta MYSQL_CONFIG en el script con las credenciales correctas.")
        return

    # Conectar a PostgreSQL
    print("\nConectando a PostgreSQL...")
    database_url = get_database_url()
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            mapeador = MapeadorFinancieroComplementario()

            # Importar conceptos de donación
            await mapeador.importar_conceptos_donacion(session, mysql_conn)

            # Importar donaciones
            await mapeador.importar_donaciones(session, mysql_conn)

            # Importar remesas
            await mapeador.importar_remesas(session, mysql_conn)

            # Importar órdenes de cobro
            await mapeador.importar_ordenes_cobro(session, mysql_conn)

            # Commit
            await session.commit()

            print("\n" + "="*80)
            print("✓ IMPORTACIÓN COMPLETADA")
            print("="*80)

        except Exception as e:
            await session.rollback()
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            mysql_conn.close()
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
