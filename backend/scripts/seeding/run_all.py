"""Ejecuta todos los seeders en orden."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.seeding.roles import seed_roles
from scripts.seeding.tipos_miembro import seed_tipos_miembro
from scripts.seeding.estados_miembro import seed_estados_miembro
from scripts.seeding.agrupaciones import seed_agrupaciones
from scripts.seeding.transacciones import seed_transacciones, seed_permisos
from scripts.seeding.miembros import seed_miembros


async def main():
    print("=" * 50)
    print("SEEDING SIGA DATABASE")
    print("=" * 50)

    print("\n[1/7] Roles...")
    await seed_roles()

    print("\n[2/7] Tipos de miembro...")
    await seed_tipos_miembro()

    print("\n[3/7] Estados de miembro...")
    await seed_estados_miembro()

    print("\n[4/7] Agrupaciones territoriales...")
    await seed_agrupaciones()

    print("\n[5/7] Transacciones...")
    await seed_transacciones()

    print("\n[6/7] Permisos rol-transaccion...")
    await seed_permisos()

    print("\n[7/7] Miembros ficticios...")
    await seed_miembros()

    print("\n" + "=" * 50)
    print("SEEDING COMPLETADO")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
