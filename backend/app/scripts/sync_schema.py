"""Crea las tablas que falten en la BD según los modelos (checkfirst=True).

Uso puntual para reconciliar un entorno cuyo esquema quedó desfasado
respecto a los modelos (p.ej. migraciones aplicadas a medias). NO altera
tablas existentes ni borra nada: solo crea las tablas (y tipos ENUM)
que aún no existan, con todas sus columnas, índices y FK.

    python -m app.scripts.sync_schema

Las columnas que falten en tablas que YA existen no las añade create_all;
para eso se complementa con un ALTER TABLE ADD COLUMN IF NOT EXISTS aparte.
"""
import asyncio

from app.core.database import engine, Base
import app.modules  # noqa: F401 — registra todos los modelos en el metadata


async def main() -> None:
    # Importar el paquete de modelos asegura que todas las tablas estén
    # registradas en Base.metadata antes del create_all.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    print("[sync_schema] create_all(checkfirst=True) completado")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
