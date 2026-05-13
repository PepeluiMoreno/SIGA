"""Mutaciones personalizadas para el módulo geográfico/organizativo."""
import uuid
from datetime import date
from typing import Optional

import strawberry
from sqlalchemy import select
from app.modules.core.geografico import AgrupacionTerritorial
from .types_auto import AgrupacionTerritorialType


# ── Inputs con FK UUID explícitos ────────────────────────────────────────────

@strawberry.input
class AgrupacionTerritorialCreateInput:
    nombre: str
    nombre_corto: Optional[str] = None
    tipo_id: Optional[uuid.UUID] = None
    agrupacion_padre_id: Optional[uuid.UUID] = None
    pais_id: Optional[uuid.UUID] = None
    provincia_id: Optional[uuid.UUID] = None
    municipio_id: Optional[uuid.UUID] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    web: Optional[str] = None
    descripcion: Optional[str] = None
    nif: Optional[str] = None
    fecha_constitucion: Optional[date] = None
    registro_oficial: Optional[str] = None
    activo: bool = True


@strawberry.input
class AgrupacionTerritorialUpdateInput:
    id: uuid.UUID
    nombre: Optional[str] = None
    nombre_corto: Optional[str] = None
    tipo_id: Optional[uuid.UUID] = strawberry.UNSET
    agrupacion_padre_id: Optional[uuid.UUID] = strawberry.UNSET
    pais_id: Optional[uuid.UUID] = strawberry.UNSET
    provincia_id: Optional[uuid.UUID] = strawberry.UNSET
    municipio_id: Optional[uuid.UUID] = strawberry.UNSET
    email: Optional[str] = None
    telefono: Optional[str] = None
    web: Optional[str] = None
    descripcion: Optional[str] = None
    nif: Optional[str] = None
    fecha_constitucion: Optional[date] = strawberry.UNSET
    registro_oficial: Optional[str] = None
    activo: Optional[bool] = None


_AG_FIELDS = [
    'nombre', 'nombre_corto', 'tipo_id', 'agrupacion_padre_id',
    'pais_id', 'provincia_id', 'municipio_id',
    'email', 'telefono', 'web', 'descripcion',
    'nif', 'fecha_constitucion', 'registro_oficial', 'activo',
]


async def _fetch_agrupacion(session, ag_id: uuid.UUID) -> AgrupacionTerritorial:
    stmt = select(AgrupacionTerritorial).where(AgrupacionTerritorial.id == ag_id)
    result = await session.execute(stmt)
    return result.scalar_one()


# ── Mutations ─────────────────────────────────────────────────────────────────

@strawberry.type
class GeograficoMutation:

    @strawberry.mutation
    async def crear_agrupacion_territorial(
        self, info: strawberry.Info, data: AgrupacionTerritorialCreateInput
    ) -> AgrupacionTerritorialType:
        session = info.context.session
        kwargs = {f: getattr(data, f) for f in _AG_FIELDS if getattr(data, f, None) is not None}
        # Preserve explicit None for optional FK fields passed as None
        for fk in ('tipo_id', 'agrupacion_padre_id', 'pais_id', 'provincia_id', 'municipio_id',
                   'fecha_constitucion'):
            if hasattr(data, fk):
                kwargs[fk] = getattr(data, fk)
        ag = AgrupacionTerritorial(**kwargs)
        session.add(ag)
        await session.commit()
        return await _fetch_agrupacion(session, ag.id)

    @strawberry.mutation
    async def actualizar_agrupacion_territorial(
        self, info: strawberry.Info, data: AgrupacionTerritorialUpdateInput
    ) -> AgrupacionTerritorialType:
        session = info.context.session
        ag = await _fetch_agrupacion(session, data.id)

        for field in _AG_FIELDS:
            val = getattr(data, field, strawberry.UNSET)
            if val is strawberry.UNSET:
                continue
            setattr(ag, field, val)

        await session.commit()
        return await _fetch_agrupacion(session, ag.id)

    @strawberry.mutation
    async def archivar_agrupacion_territorial(
        self, info: strawberry.Info, id: uuid.UUID
    ) -> AgrupacionTerritorialType:
        """Soft-delete de una unidad organizativa."""
        session = info.context.session
        ag = await _fetch_agrupacion(session, id)

        hijos = await session.execute(
            select(AgrupacionTerritorial).where(
                AgrupacionTerritorial.agrupacion_padre_id == id,
                AgrupacionTerritorial.eliminado == False,
            )
        )
        if hijos.scalars().first():
            raise ValueError("No se puede eliminar una unidad con sub-unidades activas.")

        ag.soft_delete()
        await session.commit()
        await session.refresh(ag)
        return ag
