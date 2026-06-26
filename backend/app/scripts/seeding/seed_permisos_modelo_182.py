"""Asigna las transacciones M182_* (flujo 11) al rol TESORERO. Idempotente.

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_permisos_modelo_182
"""
import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select

from app.core.database import async_session
from app.modules.acceso.models.rol import Rol
from app.modules.acceso.models.transaccion import Transaccion
from app.modules.acceso.models.rol_transaccion import RolTransaccion


TRANSACCIONES = ["ECO_MODELO182_GENERAR", "ECO_MODELO182_REGISTRAR", "ECO_MODELO182_LISTAR"]


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
        print(f"✓ TESORERO: +{creadas} transacciones del flujo 11 (Modelo 182) enlazadas.")


if __name__ == "__main__":
    asyncio.run(seed())
