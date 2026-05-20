"""Asigna las transacciones RCB_* (flujo 2) al rol TESORERO. Idempotente.

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_permisos_recibos
"""
import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select

from app.core.database import async_session
from app.modules.acceso.models.rol import Rol
from app.modules.acceso.models.transaccion import Transaccion
from app.modules.acceso.models.rol_transaccion import RolTransaccion


TRANSACCIONES_TESORERO_RECIBOS = [
    "RCB_LIST",            # ya existía
    "RCB_EMIT_LOTE",
    "RCB_MARCAR_COBRADO",
    "RCB_ANULAR",
    "RCB_DESCARGAR_PDF",
    "RCB_ENVIAR_EMAIL",
    "RCB_FAIL_NOTIFY",     # flujo 4 (comunicar fallidos)
]


async def seed():
    async with async_session() as session:
        rol = (await session.execute(
            select(Rol).where(Rol.codigo == "TESORERO")
        )).scalars().first()
        if not rol:
            print("✗ Rol TESORERO no encontrado.")
            return
        trans_r = await session.execute(
            select(Transaccion).where(Transaccion.codigo.in_(TRANSACCIONES_TESORERO_RECIBOS))
        )
        trans_by_codigo = {t.codigo: t for t in trans_r.scalars().all()}
        existentes_r = await session.execute(
            select(RolTransaccion.transaccion_id).where(RolTransaccion.rol_id == rol.id)
        )
        existentes = {row[0] for row in existentes_r.all()}
        creadas = 0
        now = datetime.utcnow()
        for codigo in TRANSACCIONES_TESORERO_RECIBOS:
            t = trans_by_codigo.get(codigo)
            if not t or t.id in existentes:
                continue
            session.add(RolTransaccion(
                id=uuid.uuid4(), rol_id=rol.id, transaccion_id=t.id,
                fecha_creacion=now, eliminado=False,
            ))
            creadas += 1
        await session.commit()
        print(f"✓ TESORERO: +{creadas} transacciones del flujo 2 (recibos) enlazadas.")


if __name__ == "__main__":
    asyncio.run(seed())
