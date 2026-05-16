"""Resolvers para la papelera: restaurar entidades soft-deleted."""
from __future__ import annotations

import uuid
from datetime import datetime

import strawberry
from sqlalchemy import select

from app.modules.membresia.models.miembro import Miembro
from app.modules.actividades.models.actividad import Actividad
from app.modules.actividades.models.grupo import GrupoTrabajo
from app.modules.actividades.models.campana import Campania
from app.graphql.types_auto import MiembroType, ActividadType, GrupoTrabajoType, CampaniaType
from app.graphql.permissions import RequireTransaction


@strawberry.type
class PapeleraResolverMutation:

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_MIEMBRO_EDITAR")])
    async def restaurar_miembro(self, info: strawberry.Info, id: uuid.UUID) -> MiembroType:
        session = info.context.session
        result = await session.execute(select(Miembro).where(Miembro.id == id))
        obj = result.scalar_one()
        obj.eliminado = False
        obj.fecha_eliminacion = None
        await session.commit()
        result = await session.execute(select(Miembro).where(Miembro.id == id))
        return result.scalar_one()

    @strawberry.mutation(permission_classes=[RequireTransaction("EVENTO_EDITAR")])
    async def restaurar_actividad(self, info: strawberry.Info, id: uuid.UUID) -> ActividadType:
        session = info.context.session
        result = await session.execute(select(Actividad).where(Actividad.id == id))
        obj = result.scalar_one()
        obj.eliminado = False
        obj.fecha_eliminacion = None
        await session.commit()
        result = await session.execute(select(Actividad).where(Actividad.id == id))
        return result.scalar_one()

    @strawberry.mutation(permission_classes=[RequireTransaction("GRUPO_EDITAR")])
    async def restaurar_grupo_trabajo(self, info: strawberry.Info, id: uuid.UUID) -> GrupoTrabajoType:
        session = info.context.session
        result = await session.execute(select(GrupoTrabajo).where(GrupoTrabajo.id == id))
        obj = result.scalar_one()
        obj.eliminado = False
        obj.fecha_eliminacion = None
        await session.commit()
        result = await session.execute(select(GrupoTrabajo).where(GrupoTrabajo.id == id))
        return result.scalar_one()

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def restaurar_campania(self, info: strawberry.Info, id: uuid.UUID) -> CampaniaType:
        session = info.context.session
        result = await session.execute(select(Campania).where(Campania.id == id))
        obj = result.scalar_one()
        obj.eliminado = False
        obj.fecha_eliminacion = None
        await session.commit()
        result = await session.execute(select(Campania).where(Campania.id == id))
        return result.scalar_one()
