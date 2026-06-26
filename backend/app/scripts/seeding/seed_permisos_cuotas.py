"""Asigna las transacciones CUOT_* y TM_MOTIVO_DEFAULT (flujo 1) al rol TESORERO.

Idempotente.

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_permisos_cuotas
"""
import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select

from app.core.database import async_session
from app.modules.acceso.models.rol import Rol
from app.modules.acceso.models.transaccion import Transaccion
from app.modules.acceso.models.rol_transaccion import RolTransaccion


# D1.6: las acciones críticas son solo del TESORERO (matriz).
# Si en el futuro hay TESORERO_AGRUPACION, este rol seguirá sin acceso a estas operaciones.
TRANSACCIONES_TESORERO_CUOTAS = [
    "CUOT_MOTIVO_LIST",
    "ECO_CUOTA_MOTIVO_REDUCCION_GESTIONAR",
    "ECO_CUOTA_CONFIGURAR",
    "ECO_CUOTA_GENERAR",
    "ECO_CUOTA_LISTAR",
    "TM_MOTIVO_DEFAULT",
]


async def seed():
    async with async_session() as session:
        rol = (await session.execute(
            select(Rol).where(Rol.codigo == "TESORERO")
        )).scalars().first()
        if not rol:
            print("✗ Rol TESORERO no encontrado. Ejecuta antes seed_roles_organizacionales.")
            return

        trans_r = await session.execute(
            select(Transaccion).where(Transaccion.codigo.in_(TRANSACCIONES_TESORERO_CUOTAS))
        )
        trans_by_codigo = {t.codigo: t for t in trans_r.scalars().all()}

        existentes_r = await session.execute(
            select(RolTransaccion.transaccion_id).where(RolTransaccion.rol_id == rol.id)
        )
        existentes = {row[0] for row in existentes_r.all()}

        creadas = 0
        now = datetime.utcnow()
        for codigo in TRANSACCIONES_TESORERO_CUOTAS:
            t = trans_by_codigo.get(codigo)
            if not t:
                print(f"  ⚠ Transacción {codigo} no existe en BD (se omite).")
                continue
            if t.id in existentes:
                continue
            session.add(RolTransaccion(
                id=uuid.uuid4(),
                rol_id=rol.id,
                transaccion_id=t.id,
                fecha_creacion=now,
                eliminado=False,
            ))
            creadas += 1

        await session.commit()
        print(f"✓ TESORERO: +{creadas} transacciones del flujo 1 (cuotas) enlazadas.")


if __name__ == "__main__":
    asyncio.run(seed())
