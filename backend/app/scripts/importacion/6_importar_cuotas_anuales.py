"""
Script para importar cuotas anuales desde el dump MySQL.

Importa la tabla:
- CUOTAANIOSOCIO → cuotas_anuales

IMPORTANTE:
- Relaciona miembros con sus cuotas por ejercicio
- Calcula estado basado en datos de pago
- Mapea modo de ingreso (SEPA, TRANSFERENCIA, etc.)
- Relaciona con importe_cuota_anio_id correspondiente

Este script debe ejecutarse DESPUÉS de importar miembros e importes de cuota.
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
from app.domains.financiero.models.cuotas import CuotaAnual, ImporteCuotaAnio, ModoIngreso
from app.domains.core.models.estados import EstadoCuota
from app.domains.miembros.models.miembro import Miembro


# Configuración de conexión MySQL (ajustar según necesidad)
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Ajustar
    'database': 'europalaica_com',
    'charset': 'utf8mb4'
}


class MapeadorCuotasAnuales:
    """Mapea cuotas anuales de MySQL a PostgreSQL."""

    def __init__(self):
        self.estados: dict[str, uuid.UUID] = {}
        self.cache_miembros: dict[int, uuid.UUID] = {}
        self.cache_agrupaciones: dict[str, uuid.UUID] = {}
        self.cache_importes_cuota: dict[tuple[int, uuid.UUID], uuid.UUID] = {}  # (ejercicio, tipo_miembro_id) → importe_cuota_anio_id

    async def cargar_estados_cuota(self, session: AsyncSession):
        """Carga los UUIDs de los estados de cuota."""

        result = await session.execute(select(EstadoCuota))
        estados = result.scalars().all()

        for estado in estados:
            self.estados[estado.codigo] = estado.id

        print("\nEstados de cuota cargados:")
        for codigo, uuid_val in self.estados.items():
            print(f"  {codigo}: {uuid_val}")

    def mapear_modo_ingreso(self, modo_mysql: Optional[str]) -> Optional[str]:
        """
        Mapea el campo MODOINGRESO de MySQL a ModoIngreso enum.

        Valores en MySQL: 'SEPA', 'TRANSFERENCIA', 'PAYPAL', 'EFECTIVO', 'TARJETA'
        """

        if not modo_mysql:
            return None

        modo_upper = modo_mysql.upper().strip()

        mapeo = {
            'SEPA': ModoIngreso.SEPA.value,
            'TRANSFERENCIA': ModoIngreso.TRANSFERENCIA.value,
            'PAYPAL': ModoIngreso.PAYPAL.value,
            'EFECTIVO': ModoIngreso.EFECTIVO.value,
            'TARJETA': ModoIngreso.TARJETA.value
        }

        return mapeo.get(modo_upper, None)

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

    async def obtener_uuid_agrupacion(self, session: AsyncSession, codigo_agrupacion: Optional[str]) -> Optional[uuid.UUID]:
        """Obtiene el UUID de una agrupación por su código o caché."""

        if not codigo_agrupacion:
            return None

        if codigo_agrupacion in self.cache_agrupaciones:
            return self.cache_agrupaciones[codigo_agrupacion]

        result = await session.execute(
            """
            SELECT id FROM agrupaciones_territoriales
            WHERE codigo = :codigo
            """,
            {"codigo": codigo_agrupacion}
        )
        row = result.fetchone()

        if row:
            self.cache_agrupaciones[codigo_agrupacion] = row[0]
            return row[0]

        return None

    async def obtener_importe_cuota_anio_id(
        self,
        session: AsyncSession,
        ejercicio: int,
        tipo_miembro_id: uuid.UUID
    ) -> Optional[uuid.UUID]:
        """
        Obtiene el importe_cuota_anio_id correspondiente al ejercicio y tipo de miembro.
        """

        cache_key = (ejercicio, tipo_miembro_id)

        if cache_key in self.cache_importes_cuota:
            return self.cache_importes_cuota[cache_key]

        result = await session.execute(
            select(ImporteCuotaAnio).where(
                ImporteCuotaAnio.ejercicio == ejercicio,
                ImporteCuotaAnio.tipo_miembro_id == tipo_miembro_id
            )
        )
        importe_cuota = result.scalar_one_or_none()

        if importe_cuota:
            self.cache_importes_cuota[cache_key] = importe_cuota.id
            return importe_cuota.id

        return None

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

    async def importar_cuotas_anuales(self, session: AsyncSession, mysql_conn):
        """Importa la tabla CUOTAANIOSOCIO."""

        print("\nImportando cuotas anuales...")

        cursor = mysql_conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT
                CODUSER,
                ANIO,
                CODAGRUPACION,
                IMPORTE,
                IMPORTEPAGADO,
                GASTOSGESTION,
                MODOINGRESO,
                FECHAPAGO,
                FECHAVENCIMIENTO,
                OBSERVACIONES
            FROM CUOTAANIOSOCIO
            ORDER BY CODUSER, ANIO
        """)

        importadas = 0
        omitidas_sin_miembro = 0
        omitidas_sin_agrupacion = 0

        for row in cursor:
            coduser = row['CODUSER']
            ejercicio = row['ANIO']

            # Obtener UUID del miembro
            miembro_id = await self.obtener_uuid_miembro(session, coduser)

            if not miembro_id:
                omitidas_sin_miembro += 1
                continue

            # Obtener tipo de miembro para relacionar con importe_cuota_anio
            result = await session.execute(
                select(Miembro).where(Miembro.id == miembro_id)
            )
            miembro = result.scalar_one_or_none()

            if not miembro:
                omitidas_sin_miembro += 1
                continue

            # Obtener UUID de agrupación
            codigo_agrupacion = row['CODAGRUPACION'].strip() if row['CODAGRUPACION'] else None
            agrupacion_id = await self.obtener_uuid_agrupacion(session, codigo_agrupacion)

            if not agrupacion_id:
                # Intentar usar agrupación del miembro si existe
                agrupacion_id = miembro.agrupacion_id

            if not agrupacion_id:
                omitidas_sin_agrupacion += 1
                continue

            # Obtener importe_cuota_anio_id
            importe_cuota_anio_id = await self.obtener_importe_cuota_anio_id(
                session,
                ejercicio,
                miembro.tipo_miembro_id
            )

            # Procesar importes
            importe = Decimal(str(row['IMPORTE'])) if row['IMPORTE'] else Decimal('0.00')
            importe_pagado = Decimal(str(row['IMPORTEPAGADO'])) if row['IMPORTEPAGADO'] else Decimal('0.00')
            gastos_gestion = Decimal(str(row['GASTOSGESTION'])) if row['GASTOSGESTION'] else Decimal('0.00')

            # Procesar fechas
            fecha_pago = self.convertir_fecha(row['FECHAPAGO'])
            fecha_vencimiento = self.convertir_fecha(row['FECHAVENCIMIENTO'])

            # Calcular estado
            codigo_estado = self.calcular_estado_cuota(importe, importe_pagado, fecha_vencimiento)
            estado_id = self.estados.get(codigo_estado, self.estados.get('PENDIENTE'))

            # Mapear modo de ingreso
            modo_ingreso = self.mapear_modo_ingreso(row['MODOINGRESO'])

            # Crear cuota anual
            cuota = CuotaAnual(
                miembro_id=miembro_id,
                ejercicio=ejercicio,
                agrupacion_id=agrupacion_id,
                importe_cuota_anio_id=importe_cuota_anio_id,
                importe=importe,
                importe_pagado=importe_pagado,
                gastos_gestion=gastos_gestion,
                estado_id=estado_id,
                modo_ingreso=modo_ingreso,
                fecha_pago=fecha_pago,
                fecha_vencimiento=fecha_vencimiento,
                observaciones=row['OBSERVACIONES'].strip() if row['OBSERVACIONES'] else None
            )

            session.add(cuota)
            importadas += 1

            if importadas % 500 == 0:
                print(f"  Procesadas {importadas} cuotas...")
                await session.flush()  # Flush periódico para grandes volúmenes

        cursor.close()

        await session.flush()

        print(f"  ✓ {importadas} cuotas anuales importadas")
        if omitidas_sin_miembro > 0:
            print(f"  ⚠ {omitidas_sin_miembro} cuotas omitidas (miembro no encontrado)")
        if omitidas_sin_agrupacion > 0:
            print(f"  ⚠ {omitidas_sin_agrupacion} cuotas omitidas (agrupación no encontrada)")


async def main():
    """Función principal."""

    print("\n" + "="*80)
    print("IMPORTACIÓN DE CUOTAS ANUALES")
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
            mapeador = MapeadorCuotasAnuales()

            # Cargar estados de cuota
            await mapeador.cargar_estados_cuota(session)

            # Importar cuotas anuales
            await mapeador.importar_cuotas_anuales(session, mysql_conn)

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
