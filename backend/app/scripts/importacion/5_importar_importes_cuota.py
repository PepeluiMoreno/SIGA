"""
Script para importar importes de cuota desde el dump MySQL.

Importa la tabla:
- IMPORTEDESCUOTAANIO → importes_cuota_anio

IMPORTANTE:
Este script genera un registro por cada combinación de (ejercicio, tipo_miembro),
ya que el nuevo modelo soporta cuotas diferentes por tipo de miembro.

En el dump MySQL solo hay un importe por ejercicio, así que se replica
para todos los tipos de miembro que requieren cuota.

Este script debe ejecutarse DESPUÉS de crear catálogos base.
"""
import asyncio
import uuid
import pymysql
from decimal import Decimal
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.database import get_database_url
from app.domains.financiero.models.cuotas import ImporteCuotaAnio
from app.domains.miembros.models.miembro import TipoMiembro


# Configuración de conexión MySQL (ajustar según necesidad)
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Ajustar
    'database': 'europalaica_com',
    'charset': 'utf8mb4'
}


class MapeadorImportesCuota:
    """Mapea importes de cuota de MySQL a PostgreSQL."""

    def __init__(self):
        self.tipos_miembro_con_cuota: list[TipoMiembro] = []

    async def cargar_tipos_miembro_con_cuota(self, session: AsyncSession):
        """Carga todos los tipos de miembro que requieren cuota."""

        result = await session.execute(
            select(TipoMiembro).where(TipoMiembro.requiere_cuota == True)
        )
        self.tipos_miembro_con_cuota = result.scalars().all()

        print(f"\nTipos de miembro que requieren cuota:")
        for tipo in self.tipos_miembro_con_cuota:
            print(f"  - {tipo.codigo}: {tipo.nombre}")

    async def importar_importes_cuota(self, session: AsyncSession, mysql_conn):
        """
        Importa la tabla IMPORTEDESCUOTAANIO y genera registros para cada tipo de miembro.
        """

        print("\nImportando importes de cuota por año...")

        cursor = mysql_conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT
                ANIO,
                IMPORTE,
                ACTIVO
            FROM IMPORTEDESCUOTAANIO
            ORDER BY ANIO
        """)

        importados = 0

        for row in cursor:
            ejercicio = row['ANIO']
            importe = Decimal(str(row['IMPORTE'])) if row['IMPORTE'] else Decimal('0.00')
            activo = bool(row['ACTIVO']) if row['ACTIVO'] is not None else True

            # Para cada tipo de miembro con cuota, crear un registro
            for tipo_miembro in self.tipos_miembro_con_cuota:
                # Verificar si ya existe
                result = await session.execute(
                    select(ImporteCuotaAnio).where(
                        ImporteCuotaAnio.ejercicio == ejercicio,
                        ImporteCuotaAnio.tipo_miembro_id == tipo_miembro.id
                    )
                )
                existe = result.scalar_one_or_none()

                if existe:
                    print(f"  ⚠ Importe para ejercicio {ejercicio} y tipo {tipo_miembro.codigo} ya existe, se omite")
                    continue

                # Crear registro de importe
                importe_cuota = ImporteCuotaAnio(
                    ejercicio=ejercicio,
                    tipo_miembro_id=tipo_miembro.id,
                    importe=importe,
                    nombre_cuota=f"Cuota {tipo_miembro.nombre} {ejercicio}",
                    activo=activo,
                    observaciones=f"Importado desde IMPORTEDESCUOTAANIO (importe general: {importe}€)"
                )

                session.add(importe_cuota)
                importados += 1

                if importados % 20 == 0:
                    print(f"  Procesados {importados} registros...")

        cursor.close()

        await session.flush()

        print(f"  ✓ {importados} importes de cuota importados")

    async def ajustar_importes_especiales(self, session: AsyncSession):
        """
        OPCIONAL: Ajustar importes para tipos de miembro específicos.

        Por ejemplo, si se desea que los estudiantes tengan un importe reducido,
        o que los parados tengan una cuota menor.

        Este método se puede personalizar según las reglas de negocio.
        """

        print("\nAjustando importes especiales (si aplica)...")

        # Ejemplo: Reducir cuota para simpatizantes al 50%
        # Descomentar y personalizar según necesidad

        # result = await session.execute(
        #     select(TipoMiembro).where(TipoMiembro.codigo == 'SIMPATIZANTE')
        # )
        # tipo_simpatizante = result.scalar_one_or_none()

        # if tipo_simpatizante:
        #     result = await session.execute(
        #         select(ImporteCuotaAnio).where(
        #             ImporteCuotaAnio.tipo_miembro_id == tipo_simpatizante.id
        #         )
        #     )
        #     importes_simpatizante = result.scalars().all()

        #     for importe_cuota in importes_simpatizante:
        #         importe_cuota.importe = importe_cuota.importe * Decimal('0.5')
        #         importe_cuota.nombre_cuota = f"Cuota Simpatizante {importe_cuota.ejercicio} (reducida)"
        #         importe_cuota.observaciones += " | Cuota reducida al 50%"

        #     print(f"  ✓ {len(importes_simpatizante)} importes de simpatizantes ajustados")

        print("  ℹ No se aplicaron ajustes especiales")


async def main():
    """Función principal."""

    print("\n" + "="*80)
    print("IMPORTACIÓN DE IMPORTES DE CUOTA")
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
            mapeador = MapeadorImportesCuota()

            # Cargar tipos de miembro con cuota
            await mapeador.cargar_tipos_miembro_con_cuota(session)

            # Importar importes de cuota
            await mapeador.importar_importes_cuota(session, mysql_conn)

            # Ajustar importes especiales (opcional)
            await mapeador.ajustar_importes_especiales(session)

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
