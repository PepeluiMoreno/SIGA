"""Asigna las transacciones REM_*, RCB_* (flujos 3 y 4) al rol TESORERO.

Idempotente: solo inserta las que aún no estén enlazadas.

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_permisos_tesorero
"""
import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select

from app.core.database import async_session
from app.modules.acceso.models.rol import Rol
from app.modules.acceso.models.transaccion import Transaccion
from app.modules.acceso.models.rol_transaccion import RolTransaccion


TRANSACCIONES_TESORERO = [
    # Flujo 3 — Generación de remesa
    "ECO_REMESA_LISTAR", "ECO_REMESA_PREVISUALIZAR", "ECO_REMESA_CREAR", "ECO_REMESA_GENERAR_XML", "ECO_REMESA_ENVIAR", "ECO_REMESA_ANULAR",
    # Flujo 4 — Liquidación de remesa
    "ECO_REMESA_PROCESAR_RESPUESTA", "ECO_REMESA_REENVIAR",
    # Recibos asociados
    "ECO_RECIBO_LISTAR", "ECO_RECIBO_NOTIFICAR_FALLIDOS",
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
            select(Transaccion).where(Transaccion.codigo.in_(TRANSACCIONES_TESORERO))
        )
        trans_by_codigo = {t.codigo: t for t in trans_r.scalars().all()}

        existentes_r = await session.execute(
            select(RolTransaccion.transaccion_id).where(RolTransaccion.rol_id == rol.id)
        )
        existentes = {row[0] for row in existentes_r.all()}

        creadas = 0
        now = datetime.utcnow()
        for codigo in TRANSACCIONES_TESORERO:
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
        print(f"✓ TESORERO: +{creadas} transacciones enlazadas (de {len(TRANSACCIONES_TESORERO)} previstas).")


if __name__ == "__main__":
    asyncio.run(seed())
