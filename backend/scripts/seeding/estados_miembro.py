"""Seeding de estados de miembro."""

import asyncio
from sqlalchemy import select

from app.core.database import async_session
from app.models import EstadoMiembro


ESTADOS = [
    {"nombre": "Activo",                  "descripcion": "Miembro activo en la organización",         "color": "#28A745", "orden": 1},
    {"nombre": "Pendiente de aprobación", "descripcion": "Alta solicitada, pendiente de revisión",    "color": "#FFC107", "orden": 2},
    {"nombre": "Suspendido",              "descripcion": "Miembro temporalmente suspendido",           "color": "#FD7E14", "orden": 3},
    {"nombre": "Baja",                    "descripcion": "Miembro dado de baja definitiva",            "color": "#6C757D", "orden": 4},
]


async def seed_estados_miembro():
    async with async_session() as db:
        for data in ESTADOS:
            result = await db.execute(
                select(EstadoMiembro).where(EstadoMiembro.nombre == data["nombre"])
            )
            if not result.scalar_one_or_none():
                db.add(EstadoMiembro(**data))
                print(f"  + Estado: {data['nombre']}")
            else:
                print(f"  = Estado ya existe: {data['nombre']}")
        await db.commit()
        print("Estados de miembro completados.")


if __name__ == "__main__":
    asyncio.run(seed_estados_miembro())
