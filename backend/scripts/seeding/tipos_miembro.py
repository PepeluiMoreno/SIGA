"""Seeding de tipos de miembro."""

import asyncio
from sqlalchemy import select

from app.core.database import async_session
from app.models import TipoMiembro


TIPOS_MIEMBRO = [
    {"nombre": "Miembro",      "descripcion": "Miembro de pleno derecho",         "requiere_cuota": True,  "puede_votar": True,  "orden": 1},
    {"nombre": "Simpatizante", "descripcion": "Simpatizante de la organización",  "requiere_cuota": False, "puede_votar": False, "orden": 2},
    {"nombre": "Honorífico",   "descripcion": "Miembro honorífico",               "requiere_cuota": False, "puede_votar": False, "orden": 3},
]


async def seed_tipos_miembro():
    async with async_session() as db:
        for data in TIPOS_MIEMBRO:
            result = await db.execute(
                select(TipoMiembro).where(TipoMiembro.nombre == data["nombre"])
            )
            if not result.scalar_one_or_none():
                db.add(TipoMiembro(**data, activo=True))
                print(f"  + TipoMiembro: {data['nombre']}")
            else:
                print(f"  = TipoMiembro ya existe: {data['nombre']}")
        await db.commit()
        print("Tipos de miembro completados.")


if __name__ == "__main__":
    asyncio.run(seed_tipos_miembro())
