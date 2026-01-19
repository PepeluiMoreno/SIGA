"""Mutaciones GraphQL para AIEL."""

import strawberry
from typing import Optional
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..core.database import get_session
from ..domains import *


# === INPUT TYPES ===

@strawberry.input
class PaisInput:
    codigo_iso: str
    nombre: str
    codigo_telefono: Optional[str] = None
    activo: bool = True


@strawberry.input
class ProvinciaInput:
    codigo_iso: str
    nombre: str
    pais_id: uuid.UUID
    activo: bool = True


@strawberry.input
class MunicipioInput:
    codigo_ine: str
    nombre: str
    provincia_id: uuid.UUID
    activo: bool = True


@strawberry.input
class AgrupacionTerritorialInput:
    codigo: str
    nombre: str
    tipo: str
    provincia_id: Optional[uuid.UUID] = None
    activo: bool = True


@strawberry.input
class TipoMiembroInput:
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    requiere_cuota: bool = True
    puede_votar: bool = False
    activo: bool = True


@strawberry.input
class EstadoCuotaInput:
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


@strawberry.input
class EstadoCampaniaInput:
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


@strawberry.input
class EstadoTareaInput:
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


@strawberry.input
class EstadoParticipanteInput:
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


@strawberry.input
class EstadoActividadInput:
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


@strawberry.input
class EstadoPropuestaInput:
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


@strawberry.input
class TipoGrupoInput:
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


@strawberry.input
class RolGrupoInput:
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


@strawberry.input
class TipoCampaniaInput:
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


@strawberry.input
class TipoActividadInput:
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


@strawberry.input
class CategoriaCompetenciaInput:
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


@strawberry.input
class CompetenciaInput:
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    categoria_id: uuid.UUID
    activo: bool = True


@strawberry.input
class NivelCompetenciaInput:
    codigo: str
    nombre: str
    orden: int
    activo: bool = True


# === MUTATION RESOLVERS ===

@strawberry.type
class Mutation:

    @strawberry.mutation
    async def crear_pais(self, input: PaisInput) -> str:
        """Crea un nuevo país."""
        async for session in get_session():
            pais = Pais(
                codigo_iso=input.codigo_iso,
                nombre=input.nombre,
                codigo_telefono=input.codigo_telefono,
                activo=input.activo
            )
            session.add(pais)
            await session.commit()
            await session.refresh(pais)
            return str(pais.id)

    @strawberry.mutation
    async def crear_provincia(self, input: ProvinciaInput) -> str:
        """Crea una nueva provincia."""
        async for session in get_session():
            provincia = Provincia(
                codigo_iso=input.codigo_iso,
                nombre=input.nombre,
                pais_id=input.pais_id,
                activo=input.activo
            )
            session.add(provincia)
            await session.commit()
            await session.refresh(provincia)
            return str(provincia.id)

    @strawberry.mutation
    async def crear_municipio(self, input: MunicipioInput) -> str:
        """Crea un nuevo municipio."""
        async for session in get_session():
            municipio = Municipio(
                codigo_ine=input.codigo_ine,
                nombre=input.nombre,
                provincia_id=input.provincia_id,
                activo=input.activo
            )
            session.add(municipio)
            await session.commit()
            await session.refresh(municipio)
            return str(municipio.id)

    @strawberry.mutation
    async def crear_agrupacion_territorial(self, input: AgrupacionTerritorialInput) -> str:
        """Crea una nueva agrupación territorial."""
        async for session in get_session():
            agrupacion = AgrupacionTerritorial(
                codigo=input.codigo,
                nombre=input.nombre,
                tipo=input.tipo,
                provincia_id=input.provincia_id,
                activo=input.activo
            )
            session.add(agrupacion)
            await session.commit()
            await session.refresh(agrupacion)
            return str(agrupacion.id)

    @strawberry.mutation
    async def crear_tipo_miembro(self, input: TipoMiembroInput) -> str:
        """Crea un nuevo tipo de miembro."""
        async for session in get_session():
            tipo = TipoMiembro(
                codigo=input.codigo,
                nombre=input.nombre,
                descripcion=input.descripcion,
                requiere_cuota=input.requiere_cuota,
                puede_votar=input.puede_votar,
                activo=input.activo
            )
            session.add(tipo)
            await session.commit()
            await session.refresh(tipo)
            return str(tipo.id)

    @strawberry.mutation
    async def crear_estado_cuota(self, input: EstadoCuotaInput) -> str:
        """Crea un nuevo estado de cuota."""
        async for session in get_session():
            estado = EstadoCuota(
                codigo=input.codigo,
                nombre=input.nombre,
                descripcion=input.descripcion,
                activo=input.activo
            )
            session.add(estado)
            await session.commit()
            await session.refresh(estado)
            return str(estado.id)

    @strawberry.mutation
    async def crear_estado_campania(self, input: EstadoCampaniaInput) -> str:
        """Crea un nuevo estado de campaña."""
        async for session in get_session():
            estado = EstadoCampania(
                codigo=input.codigo,
                nombre=input.nombre,
                descripcion=input.descripcion,
                activo=input.activo
            )
            session.add(estado)
            await session.commit()
            await session.refresh(estado)
            return str(estado.id)

    @strawberry.mutation
    async def crear_estado_tarea(self, input: EstadoTareaInput) -> str:
        """Crea un nuevo estado de tarea."""
        async for session in get_session():
            estado = EstadoTarea(
                codigo=input.codigo,
                nombre=input.nombre,
                descripcion=input.descripcion,
                activo=input.activo
            )
            session.add(estado)
            await session.commit()
            await session.refresh(estado)
            return str(estado.id)

    @strawberry.mutation
    async def crear_estado_participante(self, input: EstadoParticipanteInput) -> str:
        """Crea un nuevo estado de participante."""
        async for session in get_session():
            estado = EstadoParticipante(
                codigo=input.codigo,
                nombre=input.nombre,
                descripcion=input.descripcion,
                activo=input.activo
            )
            session.add(estado)
            await session.commit()
            await session.refresh(estado)
            return str(estado.id)

    @strawberry.mutation
    async def crear_estado_actividad(self, input: EstadoActividadInput) -> str:
        """Crea un nuevo estado de actividad."""
        async for session in get_session():
            estado = EstadoActividad(
                codigo=input.codigo,
                nombre=input.nombre,
                descripcion=input.descripcion,
                activo=input.activo
            )
            session.add(estado)
            await session.commit()
            await session.refresh(estado)
            return str(estado.id)

    @strawberry.mutation
    async def crear_estado_propuesta(self, input: EstadoPropuestaInput) -> str:
        """Crea un nuevo estado de propuesta."""
        async for session in get_session():
            estado = EstadoPropuesta(
                codigo=input.codigo,
                nombre=input.nombre,
                descripcion=input.descripcion,
                activo=input.activo
            )
            session.add(estado)
            await session.commit()
            await session.refresh(estado)
            return str(estado.id)

    @strawberry.mutation
    async def crear_tipo_grupo(self, input: TipoGrupoInput) -> str:
        """Crea un nuevo tipo de grupo."""
        async for session in get_session():
            tipo = TipoGrupo(
                codigo=input.codigo,
                nombre=input.nombre,
                descripcion=input.descripcion,
                activo=input.activo
            )
            session.add(tipo)
            await session.commit()
            await session.refresh(tipo)
            return str(tipo.id)

    @strawberry.mutation
    async def crear_rol_grupo(self, input: RolGrupoInput) -> str:
        """Crea un nuevo rol de grupo."""
        async for session in get_session():
            rol = RolGrupo(
                codigo=input.codigo,
                nombre=input.nombre,
                descripcion=input.descripcion,
                activo=input.activo
            )
            session.add(rol)
            await session.commit()
            await session.refresh(rol)
            return str(rol.id)

    @strawberry.mutation
    async def crear_tipo_campania(self, input: TipoCampaniaInput) -> str:
        """Crea un nuevo tipo de campaña."""
        async for session in get_session():
            tipo = TipoCampania(
                codigo=input.codigo,
                nombre=input.nombre,
                descripcion=input.descripcion,
                activo=input.activo
            )
            session.add(tipo)
            await session.commit()
            await session.refresh(tipo)
            return str(tipo.id)

    @strawberry.mutation
    async def crear_tipo_actividad(self, input: TipoActividadInput) -> str:
        """Crea un nuevo tipo de actividad."""
        async for session in get_session():
            tipo = TipoActividad(
                codigo=input.codigo,
                nombre=input.nombre,
                descripcion=input.descripcion,
                activo=input.activo
            )
            session.add(tipo)
            await session.commit()
            await session.refresh(tipo)
            return str(tipo.id)

    @strawberry.mutation
    async def crear_categoria_competencia(self, input: CategoriaCompetenciaInput) -> str:
        """Crea una nueva categoría de competencia."""
        async for session in get_session():
            categoria = CategoriaCompetencia(
                codigo=input.codigo,
                nombre=input.nombre,
                descripcion=input.descripcion,
                activo=input.activo
            )
            session.add(categoria)
            await session.commit()
            await session.refresh(categoria)
            return str(categoria.id)

    @strawberry.mutation
    async def crear_competencia(self, input: CompetenciaInput) -> str:
        """Crea una nueva competencia."""
        async for session in get_session():
            competencia = Competencia(
                codigo=input.codigo,
                nombre=input.nombre,
                descripcion=input.descripcion,
                categoria_id=input.categoria_id,
                activo=input.activo
            )
            session.add(competencia)
            await session.commit()
            await session.refresh(competencia)
            return str(competencia.id)

    @strawberry.mutation
    async def crear_nivel_competencia(self, input: NivelCompetenciaInput) -> str:
        """Crea un nuevo nivel de competencia."""
        async for session in get_session():
            nivel = NivelCompetencia(
                codigo=input.codigo,
                nombre=input.nombre,
                orden=input.orden,
                activo=input.activo
            )
            session.add(nivel)
            await session.commit()
            await session.refresh(nivel)
            return str(nivel.id)
