"""Script para resetear la tabla de versiones de Alembic y recrear todas las tablas."""

import asyncio
from sqlalchemy import text
from app.core.database import engine


async def reset_database():
    """Elimina todas las tablas y la tabla de versiones de Alembic."""
    async with engine.begin() as conn:
        # Eliminar la tabla de versiones de Alembic
        print("Eliminando tabla alembic_version...")
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))

        # Eliminar todas las tablas (usa CASCADE para eliminar dependencias)
        print("Eliminando todas las tablas...")
        await conn.execute(text("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
        """))

        print("* Base de datos limpiada correctamente")
        print("\nAhora ejecuta:")
        print("  python -m alembic revision --autogenerate -m 'Migracion inicial'")
        print("  python -m alembic upgrade head")


if __name__ == "__main__":
    asyncio.run(reset_database())
