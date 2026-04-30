"""Ejecuta todos los seeders en orden."""

import asyncio
import sys
from pathlib import Path

# Anadir el directorio raiz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.seeding.roles import seed_roles
from scripts.seeding.tipos_miembro import seed_tipos_miembro
from scripts.seeding.agrupaciones import seed_agrupaciones
from scripts.seeding.transacciones import seed_transacciones, seed_permisos
from scripts.seeding.miembros import seed_miembros
from scripts.seeding.presupuesto import seed_planificacion_y_partidas
from scripts.seeding.actividades import seed_all_actividades


async def main():
    print("=" * 50)
    print("SEEDING SIGA DATABASE")
    print("=" * 50)

    print("\n[1/8] Roles...")
    await seed_roles()

    print("\n[2/8] Tipos de miembro...")
    await seed_tipos_miembro()

    print("\n[3/8] Agrupaciones territoriales...")
    await seed_agrupaciones()

    print("\n[4/8] Transacciones...")
    await seed_transacciones()

    print("\n[5/8] Permisos rol-transaccion...")
    await seed_permisos()

    print("\n[6/8] Miembros ficticios...")
    await seed_miembros()

    print("\n[7/8] Planificacion y partidas presupuestarias...")
    await seed_planificacion_y_partidas()

    print("\n[8/8] Propuestas y actividades...")
    await seed_all_actividades()

    print("\n" + "=" * 50)
    print("SEEDING COMPLETADO")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
