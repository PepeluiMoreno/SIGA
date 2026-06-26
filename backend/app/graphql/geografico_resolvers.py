"""Mutaciones personalizadas para el módulo geográfico/organizativo."""
import uuid
from datetime import date
from typing import Optional

import strawberry
from sqlalchemy import select
from app.modules.core.geografico import UnidadOrganizativa, NivelOrganizativo
from .types_auto import UnidadOrganizativaType, NivelOrganizativoType
from .permissions import RequireTransaction
from app.modules.acceso.services.ambito_territorial import assert_unidad_en_ambito


# ── NivelOrganizativo: inputs y helpers ──────────────────────────────────────

@strawberry.input
class NivelOrganizativoCreateInput:
    nombre: str
    naturaleza: str
    vinculo: str
    activo: bool = True
    nivel: Optional[int] = None
    padre_tipo_id: Optional[uuid.UUID] = None
    ambito_geografico_id: Optional[uuid.UUID] = None
    denominacion_singular: Optional[str] = None
    denominacion_plural: Optional[str] = None
    estructura_distribuida: bool = False
    unidad_id: Optional[uuid.UUID] = None


@strawberry.input
class NivelOrganizativoUpdateInput:
    id: uuid.UUID
    nombre: Optional[str] = strawberry.UNSET
    naturaleza: Optional[str] = strawberry.UNSET
    vinculo: Optional[str] = strawberry.UNSET
    activo: Optional[bool] = strawberry.UNSET
    nivel: Optional[int] = strawberry.UNSET
    padre_tipo_id: Optional[uuid.UUID] = strawberry.UNSET
    ambito_geografico_id: Optional[uuid.UUID] = strawberry.UNSET
    denominacion_singular: Optional[str] = strawberry.UNSET
    denominacion_plural: Optional[str] = strawberry.UNSET
    estructura_distribuida: Optional[bool] = strawberry.UNSET
    unidad_id: Optional[uuid.UUID] = strawberry.UNSET


_NV_FIELDS = ['nombre', 'naturaleza', 'vinculo', 'activo', 'nivel', 'padre_tipo_id',
              'ambito_geografico_id', 'denominacion_singular', 'denominacion_plural',
              'estructura_distribuida', 'unidad_id']


async def _fetch_nivel(session, nivel_id: uuid.UUID) -> NivelOrganizativo:
    stmt = select(NivelOrganizativo).where(NivelOrganizativo.id == nivel_id)
    result = await session.execute(stmt)
    return result.scalar_one()


# ── UnidadOrganizativa: inputs y helpers ─────────────────────────────────────

@strawberry.input
class UnidadOrganizativaCreateInput:
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
class UnidadOrganizativaUpdateInput:
    # Todos los campos opcionales con UNSET por defecto: omitir un campo = no
    # tocarlo (update parcial seguro; editar una sección no borra las demás).
    id: uuid.UUID
    nombre: Optional[str] = strawberry.UNSET
    nombre_corto: Optional[str] = strawberry.UNSET
    tipo_id: Optional[uuid.UUID] = strawberry.UNSET
    agrupacion_padre_id: Optional[uuid.UUID] = strawberry.UNSET
    pais_id: Optional[uuid.UUID] = strawberry.UNSET
    provincia_id: Optional[uuid.UUID] = strawberry.UNSET
    municipio_id: Optional[uuid.UUID] = strawberry.UNSET
    email: Optional[str] = strawberry.UNSET
    telefono: Optional[str] = strawberry.UNSET
    web: Optional[str] = strawberry.UNSET
    descripcion: Optional[str] = strawberry.UNSET
    nif: Optional[str] = strawberry.UNSET
    fecha_constitucion: Optional[date] = strawberry.UNSET
    registro_oficial: Optional[str] = strawberry.UNSET
    activo: Optional[bool] = strawberry.UNSET


_AG_FIELDS = [
    'nombre', 'nombre_corto', 'tipo_id', 'agrupacion_padre_id',
    'pais_id', 'provincia_id', 'municipio_id',
    'email', 'telefono', 'web', 'descripcion',
    'nif', 'fecha_constitucion', 'registro_oficial', 'activo',
]


async def _fetch_agrupacion(session, ag_id: uuid.UUID) -> UnidadOrganizativa:
    stmt = select(UnidadOrganizativa).where(UnidadOrganizativa.id == ag_id)
    result = await session.execute(stmt)
    return result.scalar_one()


# ── Mutations ─────────────────────────────────────────────────────────────────

@strawberry.type
class GeograficoMutation:

    @strawberry.mutation
    async def crear_nivel_organizativo(
        self, info: strawberry.Info, data: NivelOrganizativoCreateInput
    ) -> NivelOrganizativoType:
        session = info.context.session
        # Fase 2: un sub-nivel propio de una unidad (distribuida) solo lo crea quien
        # tiene esa unidad en su ámbito. Plantillas globales (unidad_id NULL): sin filtro.
        usuario = info.context.user
        if usuario and data.unidad_id is not None:
            await assert_unidad_en_ambito(session, usuario.id, data.unidad_id)
        kwargs = {f: getattr(data, f) for f in _NV_FIELDS}
        nivel = NivelOrganizativo(**kwargs)
        session.add(nivel)
        await session.commit()
        return await _fetch_nivel(session, nivel.id)

    @strawberry.mutation
    async def actualizar_nivel_organizativo(
        self, info: strawberry.Info, data: NivelOrganizativoUpdateInput
    ) -> NivelOrganizativoType:
        session = info.context.session
        nivel = await _fetch_nivel(session, data.id)
        # Fase 2: editar un sub-nivel propio de una unidad exige tenerla en el ámbito.
        usuario = info.context.user
        if usuario and nivel.unidad_id is not None:
            await assert_unidad_en_ambito(session, usuario.id, nivel.unidad_id)
        for field in _NV_FIELDS:
            val = getattr(data, field, strawberry.UNSET)
            if val is strawberry.UNSET:
                continue
            setattr(nivel, field, val)
        await session.commit()
        return await _fetch_nivel(session, nivel.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CFG_TERRITORIO_CREAR")])
    async def crear_unidad_organizativa(
        self, info: strawberry.Info, data: UnidadOrganizativaCreateInput
    ) -> UnidadOrganizativaType:
        session = info.context.session
        kwargs = {f: getattr(data, f) for f in _AG_FIELDS if getattr(data, f, None) is not None}
        # Preserve explicit None for optional FK fields passed as None
        for fk in ('tipo_id', 'agrupacion_padre_id', 'pais_id', 'provincia_id', 'municipio_id',
                   'fecha_constitucion'):
            if hasattr(data, fk):
                kwargs[fk] = getattr(data, fk)
        ag = UnidadOrganizativa(**kwargs)
        session.add(ag)
        await session.commit()
        return await _fetch_agrupacion(session, ag.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CFG_TERRITORIO_EDITAR")])
    async def actualizar_unidad_organizativa(
        self, info: strawberry.Info, data: UnidadOrganizativaUpdateInput
    ) -> UnidadOrganizativaType:
        session = info.context.session
        # Fase 2: solo se edita una unidad dentro del propio ámbito (global ⇒ libre).
        usuario = info.context.user
        if usuario:
            await assert_unidad_en_ambito(session, usuario.id, data.id)
        ag = await _fetch_agrupacion(session, data.id)

        for field in _AG_FIELDS:
            val = getattr(data, field, strawberry.UNSET)
            if val is strawberry.UNSET:
                continue
            setattr(ag, field, val)

        await session.commit()
        return await _fetch_agrupacion(session, ag.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CFG_TERRITORIO_ELIMINAR")])
    async def archivar_unidad_organizativa(
        self, info: strawberry.Info, id: uuid.UUID
    ) -> UnidadOrganizativaType:
        """Soft-delete de una unidad organizativa."""
        session = info.context.session
        ag = await _fetch_agrupacion(session, id)

        hijos = await session.execute(
            select(UnidadOrganizativa).where(
                UnidadOrganizativa.agrupacion_padre_id == id,
                UnidadOrganizativa.eliminado == False,
            )
        )
        if hijos.scalars().first():
            raise ValueError("No se puede eliminar una unidad con sub-unidades activas.")

        ag.soft_delete()
        await session.commit()
        await session.refresh(ag)
        return ag
