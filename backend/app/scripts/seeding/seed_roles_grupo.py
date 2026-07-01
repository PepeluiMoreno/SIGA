"""Siembra los roles de grupo de trabajo (Coordinador / Colaborador / Especialista).

Sin estos roles no se pueden componer grupos de trabajo (el selector de rol al
añadir un miembro queda vacío) ni designar coordinador. Idempotente por nombre.

El rol Coordinador lleva es_coordinador=True: es el que designa al coordinador del
grupo (la figura se adjudica a uno de sus miembros).

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_roles_grupo
"""
import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select

from app.core.database import async_session
from app.modules.actividades.models.grupo import RolGrupo


ROLES = [
    # (nombre, descripcion, es_coordinador, puede_editar, puede_aprobar_gastos)
    ("Coordinador",  "Responsable del grupo de trabajo",   True,  True,  True),
    ("Colaborador",  "Miembro del grupo de trabajo",       False, False, False),
    ("Especialista", "Aporta una competencia concreta",    False, False, False),
]


async def seed():
    async with async_session() as session:
        existentes = {
            r.nombre for r in (await session.execute(select(RolGrupo))).scalars().all()
        }
        creados = 0
        for nombre, desc, coord, editar, aprobar in ROLES:
            if nombre in existentes:
                continue
            session.add(RolGrupo(
                id=uuid.uuid4(), nombre=nombre, descripcion=desc,
                es_coordinador=coord, puede_editar=editar, puede_aprobar_gastos=aprobar,
                activo=True, fecha_creacion=datetime.utcnow(),
            ))
            creados += 1
        await session.commit()
        print(f"Roles de grupo: +{creados} creados ({len(ROLES) - creados} ya existían).")


if __name__ == "__main__":
    asyncio.run(seed())
