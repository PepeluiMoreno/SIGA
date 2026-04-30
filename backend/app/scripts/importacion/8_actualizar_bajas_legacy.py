"""
Script para actualizar miembros con datos de bajas legacy.

Actualiza:
1. miembrosfallecidos → motivo_baja_id = FALLECIMIENTO
2. miembroeliminado5anios → datos_anonimizados = true

Este script debe ejecutarse DESPUÉS de importar miembros.
"""
import asyncio
import uuid
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.core.database import get_database_url
from .mysql_helper import get_mysql_connection


class ActualizadorBajasLegacy:
    """Actualiza miembros con datos de bajas legacy."""

    def __init__(self):
        self.cache_miembros: dict[int, str] = {}  # CODUSER → UUID
        self.motivo_fallecimiento_id: str = ""
        self.motivo_voluntaria_id: str = ""
        self.stats = {
            'fallecidos_actualizados': 0,
            'eliminados_actualizados': 0,
            'no_encontrados': 0
        }

    async def cargar_caches(self, session: AsyncSession):
        """Carga caches necesarios."""
        print("\nCargando caches...", flush=True)

        # Cargar mapeo de miembros
        result = await session.execute(
            text("SELECT old_id, new_uuid FROM temp_id_mapping WHERE tabla = 'MIEMBRO'")
        )
        for row in result:
            self.cache_miembros[int(row[0])] = str(row[1])

        # Cargar motivo FALLECIMIENTO
        result = await session.execute(
            text("SELECT id FROM motivos_baja WHERE codigo = 'FALLECIMIENTO'")
        )
        row = result.fetchone()
        if row:
            self.motivo_fallecimiento_id = str(row[0])

        # Cargar motivo VOLUNTARIA (por defecto para eliminados)
        result = await session.execute(
            text("SELECT id FROM motivos_baja WHERE codigo = 'VOLUNTARIA'")
        )
        row = result.fetchone()
        if row:
            self.motivo_voluntaria_id = str(row[0])

        print(f"  [OK] Miembros mapeados: {len(self.cache_miembros)}")
        print(f"  [OK] Motivo FALLECIMIENTO: {self.motivo_fallecimiento_id[:8]}...")
        print(f"  [OK] Motivo VOLUNTARIA: {self.motivo_voluntaria_id[:8]}...")

    async def actualizar_fallecidos(self, session: AsyncSession):
        """Actualiza miembros de miembrosfallecidos con motivo FALLECIMIENTO."""
        print("\nActualizando fallecidos...", flush=True)

        if not self.motivo_fallecimiento_id:
            print("  [ERROR] No se encontró motivo FALLECIMIENTO")
            return

        async with get_mysql_connection() as mysql_conn:
            async with mysql_conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT CODUSER, FECHABAJA, OBSERVACIONES
                    FROM miembrosfallecidos
                """)
                rows = await cursor.fetchall()

                for row in rows:
                    coduser = int(row[0]) if row[0] else None
                    fecha_baja = row[1]
                    observaciones = str(row[2]).strip() if row[2] else None

                    if not coduser:
                        continue

                    miembro_id = self.cache_miembros.get(coduser)
                    if not miembro_id:
                        self.stats['no_encontrados'] += 1
                        continue

                    # Actualizar con motivo de baja (sin concatenar observaciones largas)
                    await session.execute(
                        text("""
                            UPDATE miembros
                            SET motivo_baja_id = :motivo_id
                            WHERE id = :miembro_id
                        """),
                        {
                            "motivo_id": self.motivo_fallecimiento_id,
                            "miembro_id": miembro_id
                        }
                    )
                    self.stats['fallecidos_actualizados'] += 1

        print(f"  [OK] {self.stats['fallecidos_actualizados']} fallecidos actualizados")

    async def actualizar_eliminados_5anios(self, session: AsyncSession):
        """Actualiza miembros de miembroeliminado5anios como anonimizados."""
        print("\nActualizando eliminados (5 años)...", flush=True)

        async with get_mysql_connection() as mysql_conn:
            async with mysql_conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT CODUSER, FECHABAJA, FECHAELIMINAR5, OBSERVACIONES
                    FROM miembroeliminado5anios
                """)
                rows = await cursor.fetchall()

                for row in rows:
                    coduser = int(row[0]) if row[0] else None
                    fecha_baja = row[1]
                    fecha_eliminar = row[2]
                    observaciones = str(row[3]).strip() if row[3] else None

                    if not coduser:
                        continue

                    miembro_id = self.cache_miembros.get(coduser)
                    if not miembro_id:
                        self.stats['no_encontrados'] += 1
                        continue

                    # Calcular fecha de anonimización (fecha_eliminar o ahora)
                    fecha_anonimizacion = None
                    if fecha_eliminar:
                        if isinstance(fecha_eliminar, datetime):
                            fecha_anonimizacion = fecha_eliminar.date()
                        elif isinstance(fecha_eliminar, date):
                            fecha_anonimizacion = fecha_eliminar

                    # Marcar como anonimizado (ya pasaron 5+ años)
                    await session.execute(
                        text("""
                            UPDATE miembros
                            SET datos_anonimizados = true,
                                fecha_anonimizacion = COALESCE(:fecha_anon, CURRENT_DATE),
                                motivo_baja_id = COALESCE(motivo_baja_id, :motivo_voluntaria)
                            WHERE id = :miembro_id
                        """),
                        {
                            "fecha_anon": fecha_anonimizacion,
                            "motivo_voluntaria": self.motivo_voluntaria_id,
                            "miembro_id": miembro_id
                        }
                    )
                    self.stats['eliminados_actualizados'] += 1

        print(f"  [OK] {self.stats['eliminados_actualizados']} eliminados marcados como anonimizados")


async def main():
    """Función principal."""

    print("\n" + "="*80)
    print("ACTUALIZACIÓN DE BAJAS LEGACY")
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
            actualizador = ActualizadorBajasLegacy()

            # Cargar caches
            await actualizador.cargar_caches(session)

            # Actualizar fallecidos
            await actualizador.actualizar_fallecidos(session)

            # Actualizar eliminados
            await actualizador.actualizar_eliminados_5anios(session)

            # Commit
            await session.commit()

            # Refrescar vista materializada
            print("\nRefrescando vista materializada...", flush=True)
            await session.execute(text("REFRESH MATERIALIZED VIEW vista_miembros_segmentacion"))
            await session.commit()

            print("\n" + "="*80)
            print("[OK] ACTUALIZACIÓN COMPLETADA")
            print("="*80)
            print(f"\nResumen:")
            print(f"  Fallecidos actualizados: {actualizador.stats['fallecidos_actualizados']}")
            print(f"  Eliminados marcados anonimizados: {actualizador.stats['eliminados_actualizados']}")
            print(f"  No encontrados: {actualizador.stats['no_encontrados']}")

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
