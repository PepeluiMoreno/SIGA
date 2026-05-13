"""Resolvers custom para Campañas."""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

import strawberry
from sqlalchemy import select

from app.modules.actividades.models.campana import Campania
from app.graphql.types_auto import CampaniaType


@strawberry.input
class CampaniaCreateInput:
    nombre: str
    tipo_campania_id: uuid.UUID
    estado_id: uuid.UUID
    fecha_inicio_plan: Optional[date] = None
    fecha_fin_plan: Optional[date] = None
    responsable_id: Optional[uuid.UUID] = None
    agrupacion_id: Optional[uuid.UUID] = None
    lema: Optional[str] = None
    descripcion_corta: Optional[str] = None
    descripcion_larga: Optional[str] = None
    url_externa: Optional[str] = None
    objetivo_principal: Optional[str] = None
    meta_firmas: Optional[int] = None
    meta_recaudacion: Optional[Decimal] = None
    meta_participantes: Optional[int] = None


@strawberry.input
class CampaniaUpdateInput:
    campania_id: uuid.UUID
    nombre: Optional[str] = None
    tipo_campania_id: Optional[uuid.UUID] = None
    estado_id: Optional[uuid.UUID] = None
    fecha_inicio_plan: Optional[date] = None
    fecha_fin_plan: Optional[date] = None
    responsable_id: Optional[uuid.UUID] = None
    agrupacion_id: Optional[uuid.UUID] = None
    lema: Optional[str] = None
    descripcion_corta: Optional[str] = None
    descripcion_larga: Optional[str] = None
    url_externa: Optional[str] = None
    objetivo_principal: Optional[str] = None
    meta_firmas: Optional[int] = None
    meta_recaudacion: Optional[Decimal] = None
    meta_participantes: Optional[int] = None


async def _fetch_campania(session, campania_id: uuid.UUID) -> Campania:
    stmt = select(Campania).where(Campania.id == campania_id)
    result = await session.execute(stmt)
    return result.scalar_one()


@strawberry.type
class CampaniaResolverMutation:

    @strawberry.mutation
    async def crear_campania(
        self,
        info: strawberry.Info,
        data: CampaniaCreateInput,
    ) -> CampaniaType:
        session = info.context.session
        campania = Campania(
            nombre=data.nombre,
            tipo_campania_id=data.tipo_campania_id,
            estado_id=data.estado_id,
            fecha_inicio_plan=data.fecha_inicio_plan,
            fecha_fin_plan=data.fecha_fin_plan,
            responsable_id=data.responsable_id,
            agrupacion_id=data.agrupacion_id,
            lema=data.lema,
            descripcion_corta=data.descripcion_corta,
            descripcion_larga=data.descripcion_larga,
            url_externa=data.url_externa,
            objetivo_principal=data.objetivo_principal,
            meta_firmas=data.meta_firmas,
            meta_recaudacion=data.meta_recaudacion,
            meta_participantes=data.meta_participantes,
        )
        session.add(campania)
        await session.commit()
        return await _fetch_campania(session, campania.id)

    @strawberry.mutation
    async def actualizar_campania(
        self,
        info: strawberry.Info,
        data: CampaniaUpdateInput,
    ) -> CampaniaType:
        session = info.context.session
        campania = await _fetch_campania(session, data.campania_id)
        campos = [
            'nombre', 'tipo_campania_id', 'estado_id',
            'fecha_inicio_plan', 'fecha_fin_plan',
            'responsable_id', 'agrupacion_id',
            'lema', 'descripcion_corta', 'descripcion_larga', 'url_externa',
            'objetivo_principal', 'meta_firmas', 'meta_recaudacion', 'meta_participantes',
        ]
        for campo in campos:
            valor = getattr(data, campo, None)
            if valor is not None:
                setattr(campania, campo, valor)
        await session.commit()
        return await _fetch_campania(session, campania.id)
