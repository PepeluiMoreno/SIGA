"""Asigna las transacciones CIERRE_* (flujo 9) a los roles. Idempotente.

D9.2: CIERRE_EJECUTAR solo TESORERO matriz.
D9.1: CIERRE_CONSULTAR a TESORERO + cualquier rol AUDITOR si existiera.

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_permisos_cierre
"""
import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select

from app.core.database import async_session
from app.modules.acceso.models.rol import Rol
from app.modules.acceso.models.transaccion import Transaccion
from app.modules.acceso.models.rol_transaccion import RolTransaccion


REPARTO = {
    "TESORERO": ["CIERRE_EJECUTAR", "CIERRE_CONSULTAR"],
    # Si en el futuro hay rol AUDITOR, se le asignará CIERRE_CONSULTAR aquí.
}


async def seed():
    async with async_session() as session:
        creadas_totales = 0
        now = datetime.utcnow()
        for rol_codigo, trans_codes in REPARTO.items():
            rol = (await session.execute(select(Rol).where(Rol.codigo == rol_codigo))).scalars().first()
            if not rol:
                print(f"  ⚠ Rol {rol_codigo} no existe.")
                continue
            trans_r = await session.execute(
                select(Transaccion).where(Transaccion.codigo.in_(trans_codes))
            )
            trans_by_codigo = {t.codigo: t for t in trans_r.scalars().all()}
            existentes_r = await session.execute(
                select(RolTransaccion.transaccion_id).where(RolTransaccion.rol_id == rol.id)
            )
            existentes = {row[0] for row in existentes_r.all()}
            for codigo in trans_codes:
                t = trans_by_codigo.get(codigo)
                if not t or t.id in existentes:
                    continue
                session.add(RolTransaccion(
                    id=uuid.uuid4(), rol_id=rol.id, transaccion_id=t.id,
                    fecha_creacion=now, eliminado=False,
                ))
                creadas_totales += 1
        await session.commit()
        print(f"✓ Flujo 9 (cierre): +{creadas_totales} transacciones enlazadas.")


if __name__ == "__main__":
    asyncio.run(seed())
