import asyncio
from logging.config import fileConfig
import os

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from app.core.database import Base
from app.models import *  # noqa: F401,F403

config = context.config

# Construir URL desde variables de entorno (usa Session Pooler para migraciones - IPv4 compatible)
db_user = os.getenv("DB_USER", "postgres")
db_password = os.getenv("DB_PASSWORD", "")
db_host = os.getenv("DB_SESSION_HOST", os.getenv("DB_HOST", "localhost"))
db_port = os.getenv("DB_SESSION_PORT", "5432")
db_name = os.getenv("DB_NAME", "postgres")

database_url = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
config.set_main_option("sqlalchemy.url", database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Tablas a excluir de la detección automática de Alembic
# Estas tablas existen en la BD pero no están en los modelos actuales
EXCLUDED_TABLES = {
    'temp_id_mapping',  # Tabla auxiliar para migración MySQL → PostgreSQL
    'organizaciones',  # Pendiente de decisión arquitectónica
    'tipos_organizacion',  # Pendiente de decisión arquitectónica
}


def include_object(object, name, type_, reflected, compare_to):
    """Filtrar objetos para excluir tablas auxiliares."""
    if type_ == "table" and name in EXCLUDED_TABLES:
        return False
    return True


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    # No pasamos target_metadata aquí para evitar que los DDL events de
    # los modelos (Enum con create_type=True) interfieran con las migraciones.
    # target_metadata solo es necesario para autogenerate.
    context.configure(
        connection=connection,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={
            "statement_cache_size": 0,  # Necesario para Supabase Transaction/Session Pooler
            "prepared_statement_cache_size": 0,
        }
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
