"""
Seed del catálogo de tipos de vinculación con la organización.
"""
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.database import get_database_url
from app.modules.acceso.models.usuario import TipoVinculacion


# (nombre, requiere_entidad)
TIPOS = [
    ("Socio",                                      False),
    ("Simpatizante",                               False),
    ("Trabajador autónomo",                        False),
    ("Socio de asociación amiga",                  True),   # pide nombre de la asociación
    ("Empleado de servicio externo contratado",    True),   # pide nombre de la empresa
    ("Sistema",                                    False),
]


async def seed(session: AsyncSession):
    print("\n— Tipos de vinculación —")
    for nombre, requiere_entidad in TIPOS:
        res = await session.execute(
            select(TipoVinculacion).where(TipoVinculacion.nombre == nombre)
        )
        if res.scalars().first():
            print(f"  · ya existe: {nombre}")
            continue
        session.add(TipoVinculacion(nombre=nombre, requiere_entidad=requiere_entidad))
        print(f"  + creado:    {nombre}")
    await session.flush()


async def run():
    url = get_database_url()
    engine = create_async_engine(url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        await seed(session)
        await session.commit()
    await engine.dispose()
    print("\nSeed tipos_vinculacion completado.")


if __name__ == "__main__":
    asyncio.run(run())
