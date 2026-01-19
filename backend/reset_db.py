"""Reset completo de la base de datos."""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import os
from dotenv import load_dotenv

load_dotenv()

# Construir URL
db_user = os.getenv("DB_USER", "postgres")
db_password = os.getenv("DB_PASSWORD", "")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME", "postgres")

database_url = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Crear engine con statement_cache_size=0 para evitar problemas con pgbouncer
engine = create_async_engine(
    database_url,
    echo=False,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    }
)

async def reset_database():
    """Elimina todas las tablas incluyendo alembic_version."""
    async with engine.begin() as conn:
        print("Eliminando tabla alembic_version...")
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))

        print("Obteniendo lista de tablas...")
        result = await conn.execute(text("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
        """))
        tables = [row[0] for row in result]

        if tables:
            print(f"Eliminando {len(tables)} tablas...")
            for table in tables:
                print(f"  - Eliminando {table}")
                await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
        else:
            print("No hay tablas para eliminar")

        print("\nObteniendo lista de tipos ENUM...")
        result = await conn.execute(text("""
            SELECT t.typname
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            GROUP BY t.typname
        """))
        enums = [row[0] for row in result]

        if enums:
            print(f"Eliminando {len(enums)} tipos ENUM...")
            for enum in enums:
                print(f"  - Eliminando {enum}")
                await conn.execute(text(f'DROP TYPE IF EXISTS "{enum}" CASCADE'))
        else:
            print("No hay tipos ENUM para eliminar")

        print("\nBase de datos limpiada correctamente!")
        print("\nProximos pasos:")
        print("  1. python -m alembic revision --autogenerate -m 'Migracion inicial DDD'")
        print("  2. python -m alembic upgrade head")
        print("  3. python -m app.scripts.inicializar_sistema")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(reset_database())
