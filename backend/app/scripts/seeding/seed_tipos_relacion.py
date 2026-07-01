"""Seed del catálogo de tipos de relación entre contactos (modelo `Relacion`).

Relaciones dirigidas contacto ↔ contacto (no con la organización). El tipo lleva
el nombre directo (A→B) y el inverso (B→A).
"""
import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import get_database_url
from app.modules.membresia.models.relacion import TipoRelacion


# (codigo, nombre_directo (A→B), nombre_inverso (B→A))
TIPOS = [
    ("REPRESENTANTE_LEGAL", "Representante legal de", "Representado por"),
    ("APODERADO",           "Apoderado de",          "Apodera a"),
    ("EMPLEADO_DE",         "Empleado de",           "Empleador de"),
    ("MIEMBRO_JUNTA_DE",    "Miembro de la junta de", "Tiene en su junta a"),
    ("FAMILIAR",            "Familiar de",           "Familiar de"),
    ("TUTOR_DE",            "Tutor/a de",            "Tutelado por"),
]


async def seed(session: AsyncSession):
    print("\n— Tipos de relación —")
    for codigo, directo, inverso in TIPOS:
        res = await session.execute(
            select(TipoRelacion).where(TipoRelacion.codigo == codigo)
        )
        if res.scalars().first():
            print(f"  · ya existe: {codigo}")
            continue
        session.add(TipoRelacion(codigo=codigo, nombre_directo=directo, nombre_inverso=inverso))
        print(f"  + creado:    {codigo}")
    await session.flush()


async def run():
    engine = create_async_engine(get_database_url())
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        await seed(session)
        await session.commit()
    await engine.dispose()
    print("\nSeed tipos_relacion completado.")


if __name__ == "__main__":
    asyncio.run(run())
