"""Resolvers para la papelera: restaurar entidades soft-deleted."""
from __future__ import annotations

import uuid
from datetime import datetime

import strawberry
from sqlalchemy import select

from app.modules.membresia.models.miembro import Miembro
from app.modules.actividades.models.accion import Accion
from app.modules.actividades.models.grupo import GrupoTrabajo
from app.modules.actividades.models.campana import Campania
from app.graphql.types_auto import MiembroType, AccionType, GrupoTrabajoType, CampaniaType


@strawberry.type
class PapeleraResolverMutation:

    @strawberry.mutation
    async def restaurar_miembro(self, info: strawberry.Info, id: uuid.UUID) -> MiembroType:
        session = info.context.session
        result = await session.execute(select(Miembro).where(Miembro.id == id))
        obj = result.scalar_one()
        obj.eliminado = False
        obj.fecha_eliminacion = None
        await session.commit()
        result = await session.execute(select(Miembro).where(Miembro.id == id))
        return result.scalar_one()

    @strawberry.mutation
    async def restaurar_accion(self, info: strawberry.Info, id: uuid.UUID) -> AccionType:
        session = info.context.session
        result = await session.execute(select(Accion).where(Accion.id == id))
        obj = result.scalar_one()
        obj.eliminado = False
        obj.fecha_eliminacion = None
        await session.commit()
        result = await session.execute(select(Accion).where(Accion.id == id))
        return result.scalar_one()

    @strawberry.mutation
    async def restaurar_grupo_trabajo(self, info: strawberry.Info, id: uuid.UUID) -> GrupoTrabajoType:
        session = info.context.session
        result = await session.execute(select(GrupoTrabajo).where(GrupoTrabajo.id == id))
        obj = result.scalar_one()
        obj.eliminado = False
        obj.fecha_eliminacion = None
        await session.commit()
        result = await session.execute(select(GrupoTrabajo).where(GrupoTrabajo.id == id))
        return result.scalar_one()

    @strawberry.mutation
    async def restaurar_campania(self, info: strawberry.Info, id: uuid.UUID) -> CampaniaType:
        session = info.context.session
        result = await session.execute(select(Campania).where(Campania.id == id))
        obj = result.scalar_one()
        obj.eliminado = False
        obj.fecha_eliminacion = None
        await session.commit()
        result = await session.execute(select(Campania).where(Campania.id == id))
        return result.scalar_one()
