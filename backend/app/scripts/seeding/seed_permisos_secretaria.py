"""Asigna las transacciones SEC_* (módulo Secretaría) al rol SECRETARIO.

El secretario es el responsable del módulo de secretaría: reuniones, actas,
acuerdos, certificados, libro de socios, convenios y delegaciones. Idempotente:
solo inserta los enlaces que aún no existan.

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_permisos_secretaria
"""
import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select

from app.core.database import async_session
from app.modules.acceso.models.rol import Rol
from app.modules.acceso.models.transaccion import Transaccion
from app.modules.acceso.models.rol_transaccion import RolTransaccion


ROL_DESTINO = "SECRETARIO"


async def seed():
    async with async_session() as session:
        rol = (await session.execute(
            select(Rol).where(Rol.codigo == ROL_DESTINO)
        )).scalars().first()
        if not rol:
            print(f"  ⚠ rol {ROL_DESTINO} no existe; se omite. Ejecuta antes seed_roles_organizacionales.")
            return

        # Todas las transacciones del módulo secretaría (prefijo SEC_).
        sec_trans = (await session.execute(
            select(Transaccion).where(Transaccion.codigo.like("SEC_%"))
        )).scalars().all()
        if not sec_trans:
            print("  ⚠ no hay transacciones SEC_* en BD (¿falta sincronizar el catálogo?).")
            return

        existentes = {row[0] for row in (await session.execute(
            select(RolTransaccion.transaccion_id).where(RolTransaccion.rol_id == rol.id)
        )).all()}

        now = datetime.utcnow()
        creadas = 0
        for t in sec_trans:
            if t.id in existentes:
                continue
            session.add(RolTransaccion(
                id=uuid.uuid4(), rol_id=rol.id, transaccion_id=t.id,
                fecha_creacion=now, eliminado=False,
            ))
            creadas += 1

        await session.commit()
        print(f"  ✓ {ROL_DESTINO}: +{creadas} transacciones de secretaría enlazadas (de {len(sec_trans)}).")


if __name__ == "__main__":
    asyncio.run(seed())
