"""Asigna las transacciones de Voluntariado a los roles que pueden incorporar voluntarios
por delegación: Presidencia y Coordinadores (territoriales y de campaña). Idempotente.

Reparto (Fase 1 — restricción por rol; el scoping territorial es Fase 2):
- PRESIDENTE / VICEPRESIDENTE: ámbito general.
- COORDINADOR / COORD_PROV / COORD_LOCAL: territoriales (en Fase 2 se limita a su agrupación).
- COORDINADOR_CAMPANA: ámbito de su campaña.

Transacciones (códigos reales del catálogo):
- MEMBRESIA_VOLUNTARIO_LISTAR                       — listar voluntarios.
- VOL_VIEW                       — ver perfil de voluntario.
- MEMBRESIA_VOLUNTARIO_GESTIONAR — gestionar el perfil (disponibilidad) por delegación.
- MEMBRESIA_VOLUNTARIO_GESTIONAR                     — asignar habilidad a un miembro (delegación).
- HAB_LIST                       — ver el catálogo de habilidades (para elegir al asignar).
(HAB_ASSIGN_OWN = "declarar habilidades propias" es del propio socio; no se reparte aquí.)

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_permisos_voluntariado
"""
import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select

from app.core.database import async_session
from app.modules.acceso.models.rol import Rol
from app.modules.acceso.models.transaccion import Transaccion
from app.modules.acceso.models.rol_transaccion import RolTransaccion


_TRANS = ["MEMBRESIA_VOLUNTARIO_LISTAR", "VOL_VIEW", "MEMBRESIA_VOLUNTARIO_GESTIONAR", "MEMBRESIA_VOLUNTARIO_GESTIONAR", "HAB_LIST"]

REPARTO = {
    "PRESIDENTE":          _TRANS,
    "VICEPRESIDENTE":      _TRANS,
    "COORDINADOR":         _TRANS,
    "COORD_PROV":          _TRANS,
    "COORD_LOCAL":         _TRANS,
    "COORDINADOR_CAMPANA": _TRANS,
}


async def seed(session=None):
    own = session is None
    if own:
        session = async_session()
        await session.__aenter__()
    try:
        roles_r = await session.execute(
            select(Rol).where(Rol.codigo.in_(list(REPARTO.keys())))
        )
        roles_by_codigo = {r.codigo: r for r in roles_r.scalars().all()}

        todas = set()
        for codes in REPARTO.values():
            todas.update(codes)
        trans_r = await session.execute(
            select(Transaccion).where(Transaccion.codigo.in_(list(todas)))
        )
        trans_by_codigo = {t.codigo: t for t in trans_r.scalars().all()}

        creadas = 0
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
                creadas += 1
        await session.commit()
        print(f"✓ Voluntariado: +{creadas} transacciones enlazadas a roles.")
    finally:
        if own:
            await session.__aexit__(None, None, None)


if __name__ == "__main__":
    asyncio.run(seed())
