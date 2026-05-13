"""Resolvers custom para Acciones, Tareas y Participaciones.

Strawchemy excluye automáticamente las columnas FK de los inputs de create,
por lo que necesitamos resolvers explícitos que acepten IDs de FK.
"""
from __future__ import annotations

import uuid
from datetime import date, time
from decimal import Decimal
from typing import Optional

import strawberry
from sqlalchemy import select

from app.modules.actividades.models.accion import Accion, Participacion
from app.modules.actividades.models.tarea import Tarea
from app.graphql.types_auto import AccionType, TareaType, ParticipacionType


# ─────────────────────────────────────────────────────────────────────────────
# Accion
# ─────────────────────────────────────────────────────────────────────────────

@strawberry.input
class AccionCreateData:
    nombre: str
    tipo_accion_id: uuid.UUID
    estado_id: uuid.UUID
    descripcion: Optional[str] = None
    fecha_inicio: Optional[date] = None
    hora_inicio: Optional[time] = None
    fecha_fin: Optional[date] = None
    hora_fin: Optional[time] = None
    lugar: Optional[str] = None
    direccion: Optional[str] = None
    aforo: Optional[int] = None
    es_online: bool = False
    url_online: Optional[str] = None
    presupuesto_estimado: Decimal = Decimal('0.00')
    iniciativa_id: Optional[uuid.UUID] = None
    grupo_id: Optional[uuid.UUID] = None
    responsable_id: Optional[uuid.UUID] = None


@strawberry.input
class AccionUpdateData:
    id: uuid.UUID
    nombre: Optional[str] = None
    tipo_accion_id: Optional[uuid.UUID] = None
    estado_id: Optional[uuid.UUID] = None
    descripcion: Optional[str] = None
    fecha_inicio: Optional[date] = None
    hora_inicio: Optional[time] = None
    fecha_fin: Optional[date] = None
    hora_fin: Optional[time] = None
    lugar: Optional[str] = None
    direccion: Optional[str] = None
    aforo: Optional[int] = None
    es_online: Optional[bool] = None
    url_online: Optional[str] = None
    presupuesto_estimado: Optional[Decimal] = None
    presupuesto_ejecutado: Optional[Decimal] = None
    iniciativa_id: Optional[uuid.UUID] = None
    grupo_id: Optional[uuid.UUID] = None
    responsable_id: Optional[uuid.UUID] = None
    eliminado: Optional[bool] = None


# ─────────────────────────────────────────────────────────────────────────────
# Tarea
# ─────────────────────────────────────────────────────────────────────────────

@strawberry.input
class TareaCreateData:
    titulo: str
    estado_id: uuid.UUID
    descripcion: Optional[str] = None
    prioridad: int = 2
    orden: int = 0
    responsable_id: Optional[uuid.UUID] = None
    horas_estimadas: Optional[Decimal] = None
    horas_reales: Optional[Decimal] = None
    fecha_limite: Optional[date] = None
    accion_id: Optional[uuid.UUID] = None
    grupo_id: Optional[uuid.UUID] = None


@strawberry.input
class TareaUpdateData:
    id: uuid.UUID
    titulo: Optional[str] = None
    estado_id: Optional[uuid.UUID] = None
    descripcion: Optional[str] = None
    prioridad: Optional[int] = None
    orden: Optional[int] = None
    responsable_id: Optional[uuid.UUID] = None
    horas_estimadas: Optional[Decimal] = None
    horas_reales: Optional[Decimal] = None
    fecha_limite: Optional[date] = None


# ─────────────────────────────────────────────────────────────────────────────
# Participacion
# ─────────────────────────────────────────────────────────────────────────────

@strawberry.input
class ParticipacionCreateData:
    accion_id: uuid.UUID
    rol: str = 'asistente'
    miembro_id: Optional[uuid.UUID] = None
    nombre_externo: Optional[str] = None
    email_externo: Optional[str] = None
    confirmado: bool = False
    asistio: Optional[bool] = None
    horas_aportadas: Decimal = Decimal('0.00')


# ─────────────────────────────────────────────────────────────────────────────
# Mutation mixin
# ─────────────────────────────────────────────────────────────────────────────

def _apply(obj, data, fields):
    for f in fields:
        v = getattr(data, f, None)
        if v is not None:
            setattr(obj, f, v)


@strawberry.type
class AccionResolverMutation:

    @strawberry.mutation
    async def crear_accion(self, info: strawberry.Info, data: AccionCreateData) -> AccionType:
        session = info.context.session
        accion = Accion(
            nombre=data.nombre,
            tipo_accion_id=data.tipo_accion_id,
            estado_id=data.estado_id,
            descripcion=data.descripcion,
            fecha_inicio=data.fecha_inicio,
            hora_inicio=data.hora_inicio,
            fecha_fin=data.fecha_fin,
            hora_fin=data.hora_fin,
            lugar=data.lugar,
            direccion=data.direccion,
            aforo=data.aforo,
            es_online=data.es_online,
            url_online=data.url_online,
            presupuesto_estimado=data.presupuesto_estimado,
            iniciativa_id=data.iniciativa_id,
            grupo_id=data.grupo_id,
            responsable_id=data.responsable_id,
        )
        session.add(accion)
        await session.commit()
        result = await session.execute(select(Accion).where(Accion.id == accion.id))
        return result.scalar_one()

    @strawberry.mutation
    async def actualizar_accion(self, info: strawberry.Info, data: AccionUpdateData) -> AccionType:
        session = info.context.session
        result = await session.execute(select(Accion).where(Accion.id == data.id))
        accion = result.scalar_one()
        _apply(accion, data, [
            'nombre', 'tipo_accion_id', 'estado_id', 'descripcion',
            'fecha_inicio', 'hora_inicio', 'fecha_fin', 'hora_fin',
            'lugar', 'direccion', 'aforo', 'es_online', 'url_online',
            'presupuesto_estimado', 'presupuesto_ejecutado',
            'iniciativa_id', 'grupo_id', 'responsable_id', 'eliminado',
        ])
        if data.eliminado is True and not accion.fecha_eliminacion:
            from datetime import datetime
            accion.fecha_eliminacion = datetime.utcnow()
        await session.commit()
        result = await session.execute(select(Accion).where(Accion.id == accion.id))
        return result.scalar_one()

    @strawberry.mutation
    async def crear_tarea(self, info: strawberry.Info, data: TareaCreateData) -> TareaType:
        session = info.context.session
        tarea = Tarea(
            titulo=data.titulo,
            estado_id=data.estado_id,
            descripcion=data.descripcion,
            prioridad=data.prioridad,
            orden=data.orden,
            responsable_id=data.responsable_id,
            horas_estimadas=data.horas_estimadas,
            horas_reales=data.horas_reales,
            fecha_limite=data.fecha_limite,
            accion_id=data.accion_id,
            grupo_id=data.grupo_id,
        )
        session.add(tarea)
        await session.commit()
        result = await session.execute(select(Tarea).where(Tarea.id == tarea.id))
        return result.scalar_one()

    @strawberry.mutation
    async def actualizar_tarea(self, info: strawberry.Info, data: TareaUpdateData) -> TareaType:
        session = info.context.session
        result = await session.execute(select(Tarea).where(Tarea.id == data.id))
        tarea = result.scalar_one()
        _apply(tarea, data, [
            'titulo', 'estado_id', 'descripcion', 'prioridad', 'orden',
            'responsable_id', 'horas_estimadas', 'horas_reales', 'fecha_limite',
        ])
        await session.commit()
        result = await session.execute(select(Tarea).where(Tarea.id == tarea.id))
        return result.scalar_one()

    @strawberry.mutation
    async def crear_participacion(self, info: strawberry.Info, data: ParticipacionCreateData) -> ParticipacionType:
        session = info.context.session

        # Validar duplicados antes de insertar
        if data.miembro_id is not None:
            existe = await session.execute(
                select(Participacion).where(
                    Participacion.accion_id == data.accion_id,
                    Participacion.miembro_id == data.miembro_id,
                )
            )
            if existe.scalar_one_or_none() is not None:
                raise ValueError("Este miembro ya está registrado como participante de la acción")
        elif data.email_externo:
            existe = await session.execute(
                select(Participacion).where(
                    Participacion.accion_id == data.accion_id,
                    Participacion.email_externo == data.email_externo,
                )
            )
            if existe.scalar_one_or_none() is not None:
                raise ValueError("Ya existe un participante externo con ese email en la acción")

        p = Participacion(
            accion_id=data.accion_id,
            rol=data.rol,
            miembro_id=data.miembro_id,
            nombre_externo=data.nombre_externo,
            email_externo=data.email_externo,
            confirmado=data.confirmado,
            asistio=data.asistio,
            horas_aportadas=data.horas_aportadas,
        )
        session.add(p)
        await session.commit()
        result = await session.execute(select(Participacion).where(Participacion.id == p.id))
        return result.scalar_one()
