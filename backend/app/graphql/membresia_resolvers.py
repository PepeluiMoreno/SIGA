"""Resolvers custom para membresía.

strawchemy excluye las columnas FK UUID de los inputs auto-generados.
Este módulo define MiembroCreateInput y MiembroUpdateInput completos
(con todos los FK UUID fields) y los resolvers que los usan.
"""
from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

import strawberry
from sqlalchemy import select

from app.modules.membresia.models.miembro import Miembro
from app.modules.acceso.services.acceso_service import AccesoService
from app.graphql.types_auto import MiembroType


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------

@strawberry.input
class MiembroCreateInput:
    nombre: str
    apellido1: str
    tipo_miembro_id: Optional[uuid.UUID] = None
    estado_id: Optional[uuid.UUID] = None
    apellido2: Optional[str] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    pais_documento_id: Optional[uuid.UUID] = None
    pais_nacimiento_id: Optional[uuid.UUID] = None
    direccion: Optional[str] = None
    codigo_postal: Optional[str] = None
    localidad: Optional[str] = None
    provincia_id: Optional[uuid.UUID] = None
    pais_domicilio_id: Optional[uuid.UUID] = None
    telefono: Optional[str] = None
    telefono2: Optional[str] = None
    email: Optional[str] = None
    agrupacion_id: Optional[uuid.UUID] = None
    iban: Optional[str] = None
    swift_bic: Optional[str] = None
    referencia_pago: Optional[str] = None
    forma_pago_id: Optional[uuid.UUID] = None
    es_socio_honor: bool = False
    fecha_alta: Optional[date] = None
    fecha_baja: Optional[date] = None
    motivo_baja_id: Optional[uuid.UUID] = None
    motivo_baja_texto: Optional[str] = None
    observaciones: Optional[str] = None
    solicita_supresion_datos: bool = False
    fecha_solicitud_supresion: Optional[date] = None
    fecha_limite_retencion: Optional[date] = None
    datos_anonimizados: bool = False
    fecha_anonimizacion: Optional[date] = None
    activo: bool = True
    es_voluntario: bool = False
    disponibilidad: Optional[str] = None
    horas_disponibles_semana: Optional[int] = None
    profesion: Optional[str] = None
    nivel_estudios: Optional[str] = None
    experiencia_voluntariado: Optional[str] = None
    intereses: Optional[str] = None
    observaciones_voluntariado: Optional[str] = None
    puede_conducir: bool = False
    vehiculo_propio: bool = False
    disponibilidad_viajar: bool = False


@strawberry.input
class MiembroUpdateInput:
    id: uuid.UUID
    nombre: Optional[str] = None
    apellido1: Optional[str] = None
    tipo_miembro_id: Optional[uuid.UUID] = None
    estado_id: Optional[uuid.UUID] = None
    apellido2: Optional[str] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    pais_documento_id: Optional[uuid.UUID] = None
    pais_nacimiento_id: Optional[uuid.UUID] = None
    direccion: Optional[str] = None
    codigo_postal: Optional[str] = None
    localidad: Optional[str] = None
    provincia_id: Optional[uuid.UUID] = None
    pais_domicilio_id: Optional[uuid.UUID] = None
    telefono: Optional[str] = None
    telefono2: Optional[str] = None
    email: Optional[str] = None
    agrupacion_id: Optional[uuid.UUID] = None
    iban: Optional[str] = None
    swift_bic: Optional[str] = None
    referencia_pago: Optional[str] = None
    forma_pago_id: Optional[uuid.UUID] = None
    es_socio_honor: Optional[bool] = None
    fecha_alta: Optional[date] = None
    fecha_baja: Optional[date] = None
    motivo_baja_id: Optional[uuid.UUID] = None
    motivo_baja_texto: Optional[str] = None
    observaciones: Optional[str] = None
    solicita_supresion_datos: Optional[bool] = None
    fecha_solicitud_supresion: Optional[date] = None
    fecha_limite_retencion: Optional[date] = None
    datos_anonimizados: Optional[bool] = None
    fecha_anonimizacion: Optional[date] = None
    activo: Optional[bool] = None
    es_voluntario: Optional[bool] = None
    disponibilidad: Optional[str] = None
    horas_disponibles_semana: Optional[int] = None
    profesion: Optional[str] = None
    nivel_estudios: Optional[str] = None
    experiencia_voluntariado: Optional[str] = None
    intereses: Optional[str] = None
    observaciones_voluntariado: Optional[str] = None
    puede_conducir: Optional[bool] = None
    vehiculo_propio: Optional[bool] = None
    disponibilidad_viajar: Optional[bool] = None


# ---------------------------------------------------------------------------
# Mixin de mutaciones
# ---------------------------------------------------------------------------

_MIEMBRO_FIELDS = [
    'nombre', 'apellido1', 'apellido2', 'sexo', 'fecha_nacimiento',
    'tipo_miembro_id', 'estado_id', 'tipo_documento', 'numero_documento',
    'pais_documento_id', 'pais_nacimiento_id', 'direccion', 'codigo_postal',
    'localidad', 'provincia_id', 'pais_domicilio_id', 'telefono', 'telefono2',
    'email', 'agrupacion_id', 'iban', 'swift_bic', 'referencia_pago', 'forma_pago_id', 'es_socio_honor',
    'fecha_alta', 'fecha_baja', 'motivo_baja_id', 'motivo_baja_texto',
    'observaciones', 'solicita_supresion_datos', 'fecha_solicitud_supresion',
    'fecha_limite_retencion', 'datos_anonimizados', 'fecha_anonimizacion',
    'activo', 'es_voluntario', 'disponibilidad', 'horas_disponibles_semana',
    'profesion', 'nivel_estudios', 'experiencia_voluntariado', 'intereses',
    'observaciones_voluntariado', 'puede_conducir', 'vehiculo_propio',
    'disponibilidad_viajar',
]


async def _fetch_miembro(session, miembro_id: uuid.UUID):
    """Recarga el miembro con todas las relaciones selectin."""
    stmt = select(Miembro).where(Miembro.id == miembro_id)
    result = await session.execute(stmt)
    return result.scalar_one()


@strawberry.type
class MembresiaResolverMutation:

    @strawberry.mutation
    async def crear_miembro(
        self,
        info: strawberry.Info,
        data: MiembroCreateInput,
    ) -> 'MiembroType':
        session = info.context.session

        kwargs = {field: getattr(data, field) for field in _MIEMBRO_FIELDS}
        miembro = Miembro(**kwargs)
        session.add(miembro)
        await session.commit()

        return await _fetch_miembro(session, miembro.id)

    @strawberry.mutation
    async def crear_miembro_con_acceso(
        self,
        info: strawberry.Info,
        data: MiembroCreateInput,
        email: str,
        password: str,
        tipo_vinculacion_id: Optional[uuid.UUID] = None,
        activo_usuario: bool = True,
    ) -> 'MiembroType':
        """Crea un miembro y su usuario de acceso en una única transacción atómica."""
        session = info.context.session

        kwargs = {field: getattr(data, field) for field in _MIEMBRO_FIELDS}
        miembro = Miembro(**kwargs)
        session.add(miembro)
        await session.flush()

        svc = AccesoService(session)
        await svc.crear_usuario(
            email=email,
            password=password,
            activo=activo_usuario,
            miembro_id=miembro.id,
            tipo_vinculacion_id=tipo_vinculacion_id,
        )

        await session.commit()
        return await _fetch_miembro(session, miembro.id)

    @strawberry.mutation
    async def actualizar_miembro(
        self,
        info: strawberry.Info,
        data: MiembroUpdateInput,
    ) -> 'MiembroType':
        session = info.context.session

        miembro = await _fetch_miembro(session, data.id)

        for field in _MIEMBRO_FIELDS:
            val = getattr(data, field, None)
            if val is not None or field not in (
                'nombre', 'apellido1', 'tipo_miembro_id', 'estado_id'
            ):
                setattr(miembro, field, val)

        await session.commit()

        return await _fetch_miembro(session, miembro.id)
