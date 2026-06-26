"""Asigna las transacciones JUST_* (flujo 7) a los roles correspondientes. Idempotente.

Reparto:
- TESORERO: todas (ECO_JUSTIFICANTE_PRESENTAR, ECO_JUSTIFICANTE_ACEPTAR, ECO_JUSTIFICANTE_APROBAR, ECO_JUSTIFICANTE_PAGAR, ECO_JUSTIFICANTE_LISTAR).
- COORDINADOR/COORD_PROV/COORD_LOCAL/PRESIDENTE/VICEPRESIDENTE/SECRETARIO:
  presentar, aceptar (son responsables habituales de actividades), listar.

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_permisos_justificantes
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
    "TESORERO": ["ECO_JUSTIFICANTE_PRESENTAR", "ECO_JUSTIFICANTE_ACEPTAR", "ECO_JUSTIFICANTE_APROBAR", "ECO_JUSTIFICANTE_PAGAR", "ECO_JUSTIFICANTE_LISTAR"],
    "COORDINADOR":   ["ECO_JUSTIFICANTE_PRESENTAR", "ECO_JUSTIFICANTE_ACEPTAR", "ECO_JUSTIFICANTE_LISTAR"],
    "PRESIDENTE":    ["ECO_JUSTIFICANTE_PRESENTAR", "ECO_JUSTIFICANTE_ACEPTAR", "ECO_JUSTIFICANTE_LISTAR"],
    "VICEPRESIDENTE":["ECO_JUSTIFICANTE_PRESENTAR", "ECO_JUSTIFICANTE_ACEPTAR", "ECO_JUSTIFICANTE_LISTAR"],
    "SECRETARIO":    ["ECO_JUSTIFICANTE_PRESENTAR", "ECO_JUSTIFICANTE_ACEPTAR", "ECO_JUSTIFICANTE_LISTAR"],
}


async def seed():
    async with async_session() as session:
        roles_r = await session.execute(
            select(Rol).where(Rol.codigo.in_(list(REPARTO.keys())))
        )
        roles_by_codigo = {r.codigo: r for r in roles_r.scalars().all()}

        todas_trans = set()
        for codes in REPARTO.values():
            todas_trans.update(codes)
        trans_r = await session.execute(
            select(Transaccion).where(Transaccion.codigo.in_(list(todas_trans)))
        )
        trans_by_codigo = {t.codigo: t for t in trans_r.scalars().all()}

        creadas_totales = 0
        now = datetime.utcnow()
        for rol_codigo, trans_codes in REPARTO.items():
            rol = roles_by_codigo.get(rol_codigo)
            if not rol:
                print(f"  ⚠ Rol {rol_codigo} no existe.")
                continue
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
        print(f"✓ Flujo 7 (justificantes): +{creadas_totales} transacciones enlazadas a roles.")


if __name__ == "__main__":
    asyncio.run(seed())
