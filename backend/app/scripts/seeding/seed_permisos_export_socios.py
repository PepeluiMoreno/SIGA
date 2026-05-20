"""Asigna la transacción SOC_EXPORT (exportar listado de miembros a Excel) a los
roles de presidencia. Idempotente.

Reparto: SUPERADMIN, PRESIDENTE, VICEPRESIDENTE. No se concede a coordinadores
— el backlog restringe la exportación a presidencia de ámbito territorial o
superior.

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_permisos_export_socios
"""
import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select

from app.core.database import async_session
from app.modules.acceso.models.rol import Rol
from app.modules.acceso.models.transaccion import Transaccion
from app.modules.acceso.models.rol_transaccion import RolTransaccion


ROLES = ["SUPERADMIN", "PRESIDENTE", "VICEPRESIDENTE"]
TRANSACCION = "SOC_EXPORT"


async def seed():
    async with async_session() as session:
        t = (await session.execute(
            select(Transaccion).where(Transaccion.codigo == TRANSACCION)
        )).scalar_one_or_none()
        if not t:
            print(f"  ⚠ Transacción {TRANSACCION} no existe.")
            return

        roles = (await session.execute(
            select(Rol).where(Rol.codigo.in_(ROLES))
        )).scalars().all()

        now = datetime.utcnow()
        creadas = 0
        for rol in roles:
            ya = (await session.execute(
                select(RolTransaccion).where(
                    RolTransaccion.rol_id == rol.id,
                    RolTransaccion.transaccion_id == t.id,
                )
            )).scalar_one_or_none()
            if ya:
                continue
            session.add(RolTransaccion(
                id=uuid.uuid4(), rol_id=rol.id, transaccion_id=t.id,
                fecha_creacion=now, eliminado=False,
            ))
            creadas += 1

        await session.commit()
        print(f"✓ SOC_EXPORT: +{creadas} transacciones enlazadas a roles de presidencia.")


if __name__ == "__main__":
    asyncio.run(seed())
