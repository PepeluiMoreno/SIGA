"""Asigna las transacciones DON_* (flujo 6) a los roles. Idempotente.

Reparto (D6.4):
- TESORERO: ECO_DONACION_LISTAR, ECO_DONACION_REGISTRAR, ECO_DONACION_EMITIR_CERTIFICADO (matriz y agrupación).

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_permisos_donaciones
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
    "TESORERO": ["ECO_DONACION_LISTAR", "ECO_DONACION_REGISTRAR", "ECO_DONACION_EMITIR_CERTIFICADO"],
}


async def seed():
    async with async_session() as session:
        creadas = 0
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
                creadas += 1
        await session.commit()
        print(f"✓ Flujo 6 (Donaciones): +{creadas} transacciones enlazadas.")


if __name__ == "__main__":
    asyncio.run(seed())
