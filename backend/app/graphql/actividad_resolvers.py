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
    plataforma_telematica_id: Optional[uuid.UUID] = None
    datos_conexion_telematica: Optional[str] = None
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
    plataforma_telematica_id: Optional[uuid.UUID] = None
    datos_conexion_telematica: Optional[str] = None
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


@strawberry.type
class ActividadResolverMutation:

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_CREATE")])
    async def crear_actividad(self, info: strawberry.Info, data: ActividadCreateData) -> ActividadType:
        return await ActividadService(info.context.session).crear(
            nombre=data.nombre, tipo_actividad_id=data.tipo_actividad_id,
            estado_id=data.estado_id, caracter=data.caracter,
            descripcion=data.descripcion, padre_id=data.padre_id,
            es_recurrente=data.es_recurrente, periodicidad=data.periodicidad,
            campania_id=data.campania_id, grupo_id=data.grupo_id,
            responsable_id=data.responsable_id, fecha_inicio=data.fecha_inicio,
            hora_inicio=data.hora_inicio, fecha_fin=data.fecha_fin, hora_fin=data.hora_fin,
            duracion_horas=data.duracion_horas, duracion_dias=data.duracion_dias,
            lugar=data.lugar, direccion=data.direccion, localidad=data.localidad,
            provincia=data.provincia, aforo=data.aforo,
            es_online=data.es_online, url_online=data.url_online,
            plataforma_telematica_id=data.plataforma_telematica_id,
            datos_conexion_telematica=data.datos_conexion_telematica,
            presupuesto_estimado=data.presupuesto_estimado,
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_EDIT")])
    async def actualizar_actividad(self, info: strawberry.Info, data: ActividadUpdateData) -> ActividadType:
        campos = {k: getattr(data, k) for k in [
            'nombre', 'tipo_actividad_id', 'estado_id', 'descripcion',
            'padre_id', 'es_recurrente', 'periodicidad', 'caracter', 'campania_id',
            'grupo_id', 'responsable_id', 'fecha_inicio', 'hora_inicio',
            'fecha_fin', 'hora_fin', 'duracion_horas', 'duracion_dias',
            'lugar', 'direccion', 'localidad', 'provincia', 'aforo',
            'es_online', 'url_online',
            'plataforma_telematica_id', 'datos_conexion_telematica',
            'presupuesto_estimado',
            'presupuesto_ejecutado', 'eliminado',
        ]}
        return await ActividadService(info.context.session).actualizar(data.id, campos)

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_EDIT")])
    async def crear_tarea(self, info: strawberry.Info, data: TareaCreateData) -> TareaType:
        return await ActividadService(info.context.session).crear_tarea(
            titulo=data.titulo, estado_id=data.estado_id, descripcion=data.descripcion,
            prioridad=data.prioridad, orden=data.orden, responsable_id=data.responsable_id,
            horas_estimadas=data.horas_estimadas, horas_reales=data.horas_reales,
            fecha_limite=data.fecha_limite, actividad_id=data.actividad_id, grupo_id=data.grupo_id,
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_EDIT")])
    async def actualizar_tarea(self, info: strawberry.Info, data: TareaUpdateData) -> TareaType:
        campos = {k: getattr(data, k) for k in [
            'titulo', 'estado_id', 'descripcion', 'prioridad', 'orden',
            'responsable_id', 'horas_estimadas', 'horas_reales', 'fecha_limite',
        ]}
        return await ActividadService(info.context.session).actualizar_tarea(data.id, campos)

    @strawberry.mutation(permission_classes=[RequireTransaction("PART_MANAGE")])
    async def crear_participacion(self, info: strawberry.Info, data: ParticipacionCreateData) -> ParticipacionType:
        return await ActividadService(info.context.session).crear_participacion(
            actividad_id=data.actividad_id, rol=data.rol, miembro_id=data.miembro_id,
            nombre_externo=data.nombre_externo, email_externo=data.email_externo,
            confirmado=data.confirmado, asistio=data.asistio,
            horas_aportadas=data.horas_aportadas,
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_EDIT")])
    async def transicionar_actividad(
        self, info: strawberry.Info,
        id: uuid.UUID, estado_id: uuid.UUID, notas: Optional[str] = None,
    ) -> ActividadType:
        return await ActividadService(info.context.session).transicionar_estado(id, estado_id, notas)

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_APPROVE")])
    async def aprobar_actividad(
        self, info: strawberry.Info,
        id: uuid.UUID, estado_id: uuid.UUID, notas: Optional[str] = None,
    ) -> ActividadType:
        return await ActividadService(info.context.session).aprobar(
            id, estado_id,
            aprobado_por_id=getattr(info.context, 'user_id', None),
            notas=notas,
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("TEAM_CREATE")])
    async def crear_grupo_trabajo_seguro(
        self, info: strawberry.Info, nombre: str,
        tipo_grupo_id: Optional[uuid.UUID] = None,
        descripcion: Optional[str] = None, objetivo: Optional[str] = None,
        fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None,
        coordinador_id: Optional[uuid.UUID] = None,
        agrupacion_id: Optional[uuid.UUID] = None,
        campania_id: Optional[uuid.UUID] = None,
    ) -> GrupoTrabajoType:
        return await ActividadService(info.context.session).crear_grupo_trabajo(
            nombre=nombre, tipo_grupo_id=tipo_grupo_id, descripcion=descripcion,
            objetivo=objetivo, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin,
            coordinador_id=coordinador_id, agrupacion_id=agrupacion_id,
            campania_id=campania_id,
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("ACT_EDIT")])
    async def cerrar_actividad(
        self, info: strawberry.Info, id: uuid.UUID,
        valoracion: Optional[str] = None, objetivos_cumplidos: Optional[bool] = None,
        asistencia_real: Optional[int] = None, presupuesto_ejecutado: Optional[Decimal] = None,
        estado_id: Optional[uuid.UUID] = None,
    ) -> ActividadType:
        return await ActividadService(info.context.session).cerrar(
            id, estado_id=estado_id, valoracion=valoracion,
            objetivos_cumplidos=objetivos_cumplidos,
            asistencia_real=asistencia_real, presupuesto_ejecutado=presupuesto_ejecutado,
        )
