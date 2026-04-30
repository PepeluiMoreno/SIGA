"""Seeding de tipos de miembro."""

import asyncio
from sqlalchemy import select

from app.core.database import async_session
from app.models import TipoMiembro


TIPOS_MIEMBRO = [
    {"codigo": "miembro", "nombre": "miembro", "requiere_cuota": True},
    {"codigo": "SIMPATIZANTE", "nombre": "Simpatizante", "requiere_cuota": False},
]


async def seed_tipos_miembro():
    async with async_session() as db:
        for tipo_data in TIPOS_MIEMBRO:
            result = await db.execute(
                select(TipoMiembro).where(TipoMiembro.codigo == tipo_data["codigo"])
            )
            if not result.scalar_one_or_none():
                tipo = TipoMiembro(**tipo_data, activo=True)
                db.add(tipo)
                print(f"  + TipoMiembro: {tipo_data['codigo']}")
            else:
                print(f"  = TipoMiembro ya existe: {tipo_data['codigo']}")

        await db.commit()
        print("Tipos de miembro completados.")


if __name__ == "__main__":
    asyncio.run(seed_tipos_miembro())
