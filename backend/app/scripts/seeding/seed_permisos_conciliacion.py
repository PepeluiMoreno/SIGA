"""Asigna las transacciones CON_* (flujo 8) al rol TESORERO. Idempotente.

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_permisos_conciliacion
"""
import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select

from app.core.database import async_session
from app.modules.acceso.models.rol import Rol
from app.modules.acceso.models.transaccion import Transaccion
from app.modules.acceso.models.rol_transaccion import RolTransaccion


TRANSACCIONES = [
    "ECO_CONCILIACION_LISTAR", "ECO_CONCILIACION_IMPORTAR_EXTRACTO", "ECO_CONCILIACION_CONCILIAR_APUNTE", "ECO_CONCILIACION_CONFIRMAR_PERIODO",
]


async def seed():
    async with async_session() as session:
        rol = (await session.execute(select(Rol).where(Rol.codigo == "TESORERO"))).scalars().first()
        if not rol:
            print("✗ Rol TESORERO no encontrado.")
            return
        trans_r = await session.execute(
            select(Transaccion).where(Transaccion.codigo.in_(TRANSACCIONES))
        )
        trans_by_codigo = {t.codigo: t for t in trans_r.scalars().all()}
        existentes_r = await session.execute(
            select(RolTransaccion.transaccion_id).where(RolTransaccion.rol_id == rol.id)
        )
        existentes = {row[0] for row in existentes_r.all()}
        creadas = 0
        now = datetime.utcnow()
        for codigo in TRANSACCIONES:
            t = trans_by_codigo.get(codigo)
            if not t or t.id in existentes:
                continue
            session.add(RolTransaccion(
                id=uuid.uuid4(), rol_id=rol.id, transaccion_id=t.id,
                fecha_creacion=now, eliminado=False,
            ))
            creadas += 1
        await session.commit()
        print(f"✓ TESORERO: +{creadas} transacciones del flujo 8 (conciliación) enlazadas.")


if __name__ == "__main__":
    asyncio.run(seed())
