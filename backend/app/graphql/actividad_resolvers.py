"""Resolvers custom para Actividades, Tareas y Participaciones."""
from __future__ import annotations

import uuid
from datetime import date, time
from decimal import Decimal
from typing import Optional

import strawberry

from app.modules.actividades.services.actividad_service import ActividadService
from app.graphql.types_auto import ActividadType, TareaType, ParticipacionType, GrupoTrabajoType
from app.graphql.permissions import RequireTransaction


# ─── Tipos de input (sin cambios) ──────────────────────────────────────────

@strawberry.input
class ActividadCreateData:
    nombre: str
    tipo_actividad_id: uuid.UUID
    estado_id: uuid.UUID
    descripcion: Optional[str] = None
    padre_id: Optional[uuid.UUID] = None
    es_recurrente: bool = False
    periodicidad: Optional[str] = None
    caracter: str = "PUNTUAL"
    campania_id: Optional[uuid.UUID] = None
    grupo_id: Optional[uuid.UUID] = None
    responsable_id: Optional[uuid.UUID] = None
    fecha_inicio: Optional[date] = None
    hora_inicio: Optional[time] = None
    fecha_fin: Optional[date] = None
    hora_fin: Optional[time] = None
    duracion_horas: Optional[Decimal] = None
    duracion_dias: Optional[int] = None
    lugar: Optional[str] = None
    direccion: Optional[str] = None
    localidad: Optional[str] = None
    provincia: Optional[str] = None
    aforo: Optional[int] = None
    es_online: bool = False
    url_online: Optional[str] = None
    presupuesto_estimado: Decimal = Decimal('0.00')


@strawberry.input
class ActividadUpdateData:
    id: uuid.UUID
    nombre: Optional[str] = None
    tipo_actividad_id: Optional[uuid.UUID] = None
    estado_id: Optional[uuid.UUID] = None
    descripcion: Optional[str] = None
    padre_id: Optional[uuid.UUID] = None
    es_recurrente: Optional[bool] = None
    periodicidad: Optional[str] = None
    caracter: Optional[str] = None
    campania_id: Optional[uuid.UUID] = None
    grupo_id: Optional[uuid.UUID] = None
    responsable_id: Optional[uuid.UUID] = None
    fecha_inicio: Optional[date] = None
    hora_inicio: Optional[time] = None
    fecha_fin: Optional[date] = None
    hora_fin: Optional[time] = None
    duracion_horas: Optional[Decimal] = None
    duracion_dias: Optional[int] = None
    lugar: Optional[str] = None
    direccion: Optional[str] = None
    localidad: Optional[str] = None
    provincia: Optional[str] = None
    aforo: Optional[int] = None
    es_online: Optional[bool] = None
    url_online: Optional[str] = None
    presupuesto_estimado: Optional[Decimal] = None
    presupuesto_ejecutado: Optional[Decimal] = None
    eliminado: Optional[bool] = None


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
    actividad_id: Optional[uuid.UUID] = None
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


@strawberry.input
class ParticipacionCreateData:
    actividad_id: uuid.UUID
    rol: str = 'asistente'
    miembro_id: Optional[uuid.UUID] = None
    nombre_externo: Optional[str] = None
    email_externo: Optional[str] = None
    confirmado: bool = False
    asistio: Optional[bool] = None
    horas_aportadas: Decimal = Decimal('0.00')


# ─── Mutations ───────────────────────────────────────────────────────────────

@strawberry.type
class ActividadResolverMutation:

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_CREATE")])
    async def crear_actividad(self, info: strawberry.Info, data: ActividadCreateData) -> ActividadType:
        return await ActividadService(info.context.session).crear_actividad(data)

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_EDIT")])
    async def actualizar_actividad(self, info: strawberry.Info, data: ActividadUpdateData) -> ActividadType:
        return await ActividadService(info.context.session).actualizar_actividad(data)

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_EDIT")])
    async def crear_tarea(self, info: strawberry.Info, data: TareaCreateData) -> TareaType:
        return await ActividadService(info.context.session).crear_tarea(data)

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_EDIT")])
    async def actualizar_tarea(self, info: strawberry.Info, data: TareaUpdateData) -> TareaType:
        return await ActividadService(info.context.session).actualizar_tarea(data)

    @strawberry.mutation(permission_classes=[RequireTransaction("PART_MANAGE")])
    async def crear_participacion(self, info: strawberry.Info, data: ParticipacionCreateData) -> ParticipacionType:
        return await ActividadService(info.context.session).crear_participacion(data)

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_EDIT")])
    async def transicionar_actividad(
        self, info: strawberry.Info,
        id: uuid.UUID, estado_id: uuid.UUID, notas: Optional[str] = None,
    ) -> ActividadType:
        return await ActividadService(info.context.session).transicionar_actividad(id, estado_id, notas)

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_APPROVE")])
    async def aprobar_actividad(
        self, info: strawberry.Info,
        id: uuid.UUID, estado_id: uuid.UUID, notas: Optional[str] = None,
    ) -> ActividadType:
        aprobado_por_id = getattr(info.context, 'user_id', None)
        return await ActividadService(info.context.session).aprobar_actividad(
            id, estado_id, aprobado_por_id=aprobado_por_id, notas=notas,
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("TEAM_CREATE")])
    async def crear_grupo_trabajo_seguro(
        self, info: strawberry.Info,
        nombre: str,
        tipo_grupo_id: Optional[uuid.UUID] = None,
        descripcion: Optional[str] = None,
        objetivo: Optional[str] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        coordinador_id: Optional[uuid.UUID] = None,
        agrupacion_id: Optional[uuid.UUID] = None,
        campania_id: Optional[uuid.UUID] = None,
    ) -> GrupoTrabajoType:
        return await ActividadService(info.context.session).crear_grupo_trabajo(
            nombre=nombre, tipo_grupo_id=tipo_grupo_id, descripcion=descripcion,
            objetivo=objetivo, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin,
            coordinador_id=coordinador_id, agrupacion_id=agrupacion_id, campania_id=campania_id,
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_EDIT")])
    async def cerrar_actividad(
        self, info: strawberry.Info,
        id: uuid.UUID,
        valoracion: Optional[str] = None,
        objetivos_cumplidos: Optional[bool] = None,
        asistencia_real: Optional[int] = None,
        presupuesto_ejecutado: Optional[Decimal] = None,
        estado_id: Optional[uuid.UUID] = None,
    ) -> ActividadType:
        return await ActividadService(info.context.session).cerrar_actividad(
            id, valoracion=valoracion, objetivos_cumplidos=objetivos_cumplidos,
            asistencia_real=asistencia_real, presupuesto_ejecutado=presupuesto_ejecutado,
            estado_id=estado_id,
        )
