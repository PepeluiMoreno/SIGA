"""
Seed del catálogo de tipos de vinculación con la organización.
"""
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.database import get_database_url
from app.modules.membresia.models.tipo_vinculacion import TipoVinculacion


# (nombre, codigo, ambito, area_responsable, requiere_satelite, permite_cuenta) — alineado
# con el catálogo canónico (ver migración p2 y 1_crear_catalogos_base.crear_tipos_vinculacion).
# permite_cuenta: el contacto con ese vínculo puede ser dotado de cuenta de usuario.
# Solo AFILIACIONES con la organización (se almacenan como Vinculacion). NO se
# incluyen FIRMANTE ni SIMPATIZANTE: "firmante/participante/donante" son
# condiciones DERIVADAS de los registros del contacto, no vínculos. Las
# relaciones contacto↔contacto (representante legal, familiar…) viven en el
# modelo `Relacion`, no aquí.
TIPOS = [
    ("Socio",              "SOCIO",              "territorial", "MEMBRESIA_SOCIO_GESTIONAR",      True,  True),
    ("Voluntario",         "VOLUNTARIO",         "territorial", "MEMBRESIA_VOLUNTARIO_GESTIONAR", True,  True),
    ("Donante",            "DONANTE",            "central",     "TESORERIA_DONANTES",             False, False),
    ("Contratado/a",       "EMPLEADO",           "central",     "RECURSOS_HUMANOS",               True,  True),
    ("Organización amiga", "ORGANIZACION_AMIGA", "central",     "SECRETARIA_CONVENIOS",           False, False),
]


async def seed(session: AsyncSession):
    print("\n— Tipos de vinculación —")
    for nombre, codigo, ambito, area, requiere_satelite, permite_cuenta in TIPOS:
        res = await session.execute(
            select(TipoVinculacion).where(TipoVinculacion.codigo == codigo)
        )
        if res.scalars().first():
            print(f"  · ya existe: {codigo}")
            continue
        session.add(TipoVinculacion(
            nombre=nombre, codigo=codigo, ambito=ambito,
            area_responsable=area, requiere_satelite=requiere_satelite,
            permite_cuenta=permite_cuenta,
        ))
        print(f"  + creado:    {codigo}")
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
