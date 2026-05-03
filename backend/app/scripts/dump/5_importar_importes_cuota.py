"""
Script para importar importes de cuota desde MySQL.

Importa la tabla:
- IMPORTEDESCUOTAANIO → importes_cuota_anio

IMPORTANTE:
Este script genera un registro por cada combinación de (ejercicio, tipo_miembro),
ya que el nuevo modelo soporta cuotas diferentes por tipo de miembro.

En el dump MySQL solo hay un importe por ejercicio, así que se replica
para todos los tipos de miembro que requieren cuota.

Este script debe ejecutarse DESPUÉS de crear catálogos base y antes de importar cuotas anuales.
"""
import asyncio
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.database import get_database_url
from app.modules.economico.models.cuotas import ImporteCuotaAnio
from app.modules.miembros.models.miembro import TipoMiembro
from .mysql_helper import get_mysql_connection


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

    async def importar_importes_cuota(self, session: AsyncSession):
        """
        Importa la tabla IMPORTEDESCUOTAANIO y genera registros para cada tipo de miembro.
        """

        print("\nImportando importes de cuota por ano desde MySQL...")

        # Estructura de IMPORTEDESCUOTAANIO:
        # ANIOCUOTA, CODCUOTA, IMPORTECUOTAANIOEL, NOMBRECUOTA, DESCRIPCIONCUOTA

        importados = 0

        async with get_mysql_connection() as mysql_conn:
            async with mysql_conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT ANIOCUOTA, CODCUOTA, IMPORTECUOTAANIOEL, NOMBRECUOTA, DESCRIPCIONCUOTA
                    FROM IMPORTEDESCUOTAANIO
                    ORDER BY ANIOCUOTA
                """)
                rows = await cursor.fetchall()

                for row in rows:
                    ejercicio = row[0]  # ANIOCUOTA
                    codcuota = row[1]  # CODCUOTA
                    importe_val = row[2]  # IMPORTECUOTAANIOEL
                    nombre_cuota = row[3]  # NOMBRECUOTA
                    descripcion = row[4]  # DESCRIPCIONCUOTA

                    # Convertir a tipos correctos
                    try:
                        ejercicio_int = int(ejercicio) if ejercicio else None
                        if not ejercicio_int:
                            continue

                        importe = Decimal(str(importe_val)) if importe_val else Decimal('0.00')

                    except Exception as e:
                        print(f"  [WARN] Error procesando fila: {row} - {e}")
                        continue

                    # Para cada tipo de miembro con cuota, crear un registro
                    for tipo_miembro in self.tipos_miembro_con_cuota:
                        # Verificar si ya existe
                        result = await session.execute(
                            select(ImporteCuotaAnio).where(
                                ImporteCuotaAnio.ejercicio == ejercicio_int,
                                ImporteCuotaAnio.tipo_miembro_id == tipo_miembro.id
                            )
                        )
                        existe = result.scalar_one_or_none()

                        if existe:
                            continue

                        # Crear registro de importe
                        nombre_final = f"{nombre_cuota} - {tipo_miembro.nombre}" if nombre_cuota else f"Cuota {tipo_miembro.nombre} {ejercicio_int}"
                        obs = f"Importado desde IMPORTEDESCUOTAANIO (código: {codcuota}, importe: {importe}€)"
                        if descripcion:
                            obs += f" | {descripcion}"

                        importe_cuota = ImporteCuotaAnio(
                            ejercicio=ejercicio_int,
                            tipo_miembro_id=tipo_miembro.id,
                            importe=importe,
                            nombre_cuota=nombre_final,
                            activo=True,  # Todos los importes cargados se consideran activos
                            observaciones=obs,
                            fecha_creacion=datetime.utcnow(),  # Explicit timestamp for import
                            eliminado=False  # Explicit soft delete flag
                        )

                        session.add(importe_cuota)
                        importados += 1

                        if importados % 20 == 0:
                            print(f"  Procesados {importados} registros...")

        await session.flush()

        print(f"  [OK] {importados} importes de cuota importados")

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

        #     print(f"  [OK] {len(importes_simpatizante)} importes de simpatizantes ajustados")

        print("  [INFO] No se aplicaron ajustes especiales")


async def main():
    """Función principal."""

    print("\n" + "="*80)
    print("IMPORTACION DE IMPORTES DE CUOTA")
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
            mapeador = MapeadorImportesCuota()

            # Cargar tipos de miembro con cuota
            await mapeador.cargar_tipos_miembro_con_cuota(session)

            # Importar importes de cuota
            await mapeador.importar_importes_cuota(session)

            # Ajustar importes especiales (opcional)
            await mapeador.ajustar_importes_especiales(session)

            # Commit
            await session.commit()

            print("\n" + "="*80)
            print("[OK] IMPORTACION COMPLETADA")
            print("="*80)

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
