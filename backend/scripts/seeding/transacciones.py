"""Seeding de transacciones y permisos del sistema.

Las transacciones se sincronizan desde initial_data/transacciones.json
(misma fuente que usa el bootstrap en cada arranque).
"""

import asyncio
from sqlalchemy import select

from app.core.database import async_session
from app.models import Rol, RolTransaccion, Transaccion
from app.scripts.bootstrap import sync_transacciones


async def seed_transacciones():
    """Sincroniza transacciones desde initial_data/transacciones.json."""
    async with async_session() as db:
        transacciones = await sync_transacciones(db)
        await db.commit()
        print(f"  Transacciones sincronizadas: {len(transacciones)}")


async def seed_permisos():
    """Asigna todas las transacciones al rol SUPERADMIN (si existe)."""
    async with async_session() as db:
        # El bootstrap ya enlaza SUPERADMIN con todas las transacciones.
        # Este paso es idempotente por si se ejecuta antes del primer arranque.
        superadmin = (await db.execute(
            select(Rol).where(Rol.codigo == "SUPERADMIN")
        )).scalar_one_or_none()

        if not superadmin:
            print("  ! Rol SUPERADMIN no encontrado; los permisos los asigna el bootstrap en el arranque.")
            return

        transacciones = (await db.execute(select(Transaccion))).scalars().all()
        nuevas = 0
        for tx in transacciones:
            existe = (await db.execute(
                select(RolTransaccion).where(
                    RolTransaccion.rol_id == superadmin.id,
                    RolTransaccion.transaccion_id == tx.id,
                )
            )).scalar_one_or_none()
            if not existe:
                db.add(RolTransaccion(rol_id=superadmin.id, transaccion_id=tx.id))
                nuevas += 1

        await db.commit()
        print(f"  Permisos SUPERADMIN: {nuevas} nuevos enlazados ({len(transacciones)} total).")


if __name__ == "__main__":
    asyncio.run(seed_transacciones())
