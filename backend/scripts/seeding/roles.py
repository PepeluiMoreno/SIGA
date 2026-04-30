"""Seeding de roles del sistema."""

import asyncio
from sqlalchemy import select

from app.core.database import async_session
from app.models import Rol


ROLES = [
    {"codigo": "miembro", "nombre": "miembro", "descripcion": "Miembro asociado de Europa Laica"},
    {"codigo": "SIMPATIZANTE", "nombre": "Simpatizante", "descripcion": "Usuario simpatizante (no miembro)"},
    {"codigo": "PRESIDENTE", "nombre": "Presidente/Vicepresidente/Secretaría", "descripcion": "Gestión ejecutiva de la asociación"},
    {"codigo": "TESORERO", "nombre": "Tesorero", "descripcion": "Gestión financiera y de cuotas"},
    {"codigo": "COORDINADOR", "nombre": "Coordinador", "descripcion": "Coordinación de agrupaciones territoriales"},
    {"codigo": "GESTOR_SIMPS", "nombre": "Gestor de Simpatizantes", "descripcion": "Gestión de comunicaciones con simpatizantes"},
    {"codigo": "Admin", "nombre": "Administrador", "descripcion": "Control total del sistema"},
    {"codigo": "MANTENIMIENTO", "nombre": "Mantenimiento", "descripcion": "Acceso técnico para mantenimiento del sistema"},
]


async def seed_roles():
    async with async_session() as db:
        for rol_data in ROLES:
            # Verificar si existe
            result = await db.execute(
                select(Rol).where(Rol.codigo == rol_data["codigo"])
            )
            if not result.scalar_one_or_none():
                rol = Rol(**rol_data, activo=True)
                db.add(rol)
                print(f"  + Rol: {rol_data['codigo']}")
            else:
                print(f"  = Rol ya existe: {rol_data['codigo']}")

        await db.commit()
        print("Roles completados.")


if __name__ == "__main__":
    asyncio.run(seed_roles())
