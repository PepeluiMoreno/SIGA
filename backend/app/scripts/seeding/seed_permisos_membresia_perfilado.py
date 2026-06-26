"""Asigna a los perfiles las transacciones de Membresía según el modelo de
propiedad POR DIMENSIÓN perfilado. Idempotente.

Reparto acordado. La dimensión territorial NO son roles distintos: SECRETARIO y
TESORERO son el mismo rol tanto a nivel general como territorial, y su ámbito lo
fija el `agrupacion_id` del nombramiento sobre el que se asigna, no un código de
rol "_TERRITORIAL".
- Identidad, registro, situación (alta/baja/suspensión), solicitudes y libro de
  socios -> Secretaría (SECRETARIO).
- Económico del socio (cuota/IBAN/forma de pago) -> Tesorería (TESORERO).
- Voluntariado (disponibilidad/habilidades) -> Coordinación (COORDINADOR,
  COORD_PROV, COORD_LOCAL, COORDINADOR_CAMPANA).

SUPERADMIN recibe todas vía bootstrap (no se reparte aquí).

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_permisos_membresia_perfilado
"""
import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select

from app.core.database import async_session
from app.modules.acceso.models.rol import Rol
from app.modules.acceso.models.transaccion import Transaccion
from app.modules.acceso.models.rol_transaccion import RolTransaccion


_SECRETARIA = ["SECRETARIO"]
_TESORERIA = ["TESORERO"]
_COORDINACION = ["COORDINADOR", "COORDINADOR_CAMPANA"]

# transaccion_codigo -> roles que la reciben
_REPARTO = {
    # Secretaría: identidad / registro / situación / solicitudes / libro
    "SOC_EDIT":             _SECRETARIA,
    "SOC_DEACTIVATE":       _SECRETARIA,
    "SOC_REACTIVATE":       _SECRETARIA,
    "SOC_BLOCK":            _SECRETARIA,
    "SOL_APPROVE":          _SECRETARIA,
    "SOL_REJECT":           _SECRETARIA,
    "LIBRO_SOCIOS_GENERAR": _SECRETARIA,
    "LIBRO_SOCIOS_VER":     _SECRETARIA + _TESORERIA + ["PRESIDENTE", "VICEPRESIDENTE"],
    # Tesorería: dimensión económica del socio (editar y VER datos bancarios)
    "MEMBRESIA_MIEMBRO_EDITAR_DATOS_ECONOMICOS":   _TESORERIA,
    "MEMBRESIA_MIEMBRO_VER_IBAN":        _TESORERIA,
    # Coordinación / voluntariado
    "AVAIL_EDIT":           _COORDINACION,
    "MEMBRESIA_VOLUNTARIO_GESTIONAR":           _COORDINACION,
    "HAB_VALIDATE":         _COORDINACION,
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
            print(f"  ⚠ transacciones no encontradas (¿falta bootstrap/seed?): {faltan_t}")
        if faltan_r:
            print(f"  ⚠ roles no encontrados: {sorted(faltan_r)}")
        print(f"✓ Membresía (perfilado): +{creadas} enlaces rol-transacción.")


if __name__ == "__main__":
    asyncio.run(seed())
