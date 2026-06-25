"""Reparto de las transacciones del CRM de contactos (CONTACTO_*). Idempotente.

Un contacto es el "lead" del CRM (persona/entidad relacionada, socio potencial o
no): su CRUD NO es de membresía, por eso tiene su propio namespace CONTACTO_*.

Reparto acordado:
- Crear/editar/baja de contactos -> Secretaría (SECRETARIO) + Extensión (EXTENSION,
  captación de socios).
- Listar/ver -> amplio (Secretaría, Tesorería, Coordinación, Presidencia, Extensión).

SUPERADMIN recibe todas vía bootstrap (no se reparte aquí).

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_permisos_contactos
"""
import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select

from app.core.database import async_session
from app.modules.acceso.models.rol import Rol
from app.modules.acceso.models.transaccion import Transaccion
from app.modules.acceso.models.rol_transaccion import RolTransaccion


_GESTION = ["SECRETARIO", "EXTENSION"]
_LECTURA = ["SECRETARIO", "EXTENSION", "TESORERO", "COORDINADOR", "COORD_PROV",
            "COORD_LOCAL", "COORDINADOR_CAMPANA", "PRESIDENTE", "VICEPRESIDENTE"]

# transaccion_codigo -> roles que la reciben
_REPARTO = {
    "CONTACTO_CREATE": _GESTION,
    "CONTACTO_EDIT":   _GESTION,
    "CONTACTO_DELETE": _GESTION,
    "CONTACTO_LIST":   _LECTURA,
    "CONTACTO_VIEW":   _LECTURA,
}


async def seed():
    async with async_session() as session:
        trans = {
            t.codigo: t for t in (await session.execute(
                select(Transaccion).where(Transaccion.codigo.in_(list(_REPARTO.keys())))
            )).scalars().all()
        }
        codigos_rol = sorted({r for roles in _REPARTO.values() for r in roles})
        roles = {
            r.codigo: r for r in (await session.execute(
                select(Rol).where(Rol.codigo.in_(codigos_rol))
            )).scalars().all()
        }

        now = datetime.utcnow()
        creadas = 0
        faltan_t, faltan_r = [], set()
        for tcod, rcods in _REPARTO.items():
            t = trans.get(tcod)
            if t is None:
                faltan_t.append(tcod)
                continue
            for rcod in rcods:
                rol = roles.get(rcod)
                if rol is None:
                    faltan_r.add(rcod)
                    continue
                ya = (await session.execute(
                    select(RolTransaccion).where(
                        RolTransaccion.rol_id == rol.id,
                        RolTransaccion.transaccion_id == t.id,
                    )
                )).scalar_one_or_none()
                if ya:
                    continue
                session.add(RolTransaccion(
                    id=uuid.uuid4(), rol_id=rol.id, transaccion_id=t.id,
                    fecha_creacion=now, eliminado=False,
                ))
                creadas += 1

        await session.commit()
        if faltan_t:
            print(f"  ⚠ transacciones no encontradas (¿falta reiniciar backend para sincronizar?): {faltan_t}")
        if faltan_r:
            print(f"  ⚠ roles no encontrados (¿falta seed_roles_organizacionales?): {sorted(faltan_r)}")
        print(f"✓ CRM contactos: +{creadas} enlaces rol-transacción.")


if __name__ == "__main__":
    asyncio.run(seed())
