"""Resolvers custom para Campañas."""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

import strawberry
from sqlalchemy import select

from app.modules.actividades.services.campania_service import CampaniaService
from app.graphql.types_auto import CampaniaType, PlantillaCampaniaType, PlantillaActividadType, PlantillaTareaType
from app.graphql.permissions import RequireTransaction
from app.modules.actividades.models.campana import PlantillaActividad, PlantillaTarea


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
    foto_url: Optional[str] = None
    objetivo_principal: Optional[str] = None
    es_recurrente: Optional[bool] = None
    periodicidad: Optional[str] = None


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
    foto_url: Optional[str] = None
    objetivo_principal: Optional[str] = None
    es_recurrente: Optional[bool] = None
    periodicidad: Optional[str] = None


@strawberry.input
class MetaInput:
    tipo_meta_id: uuid.UUID
    valor_planificado: Optional[Decimal] = None
    notas: Optional[str] = None
    orden: int = 0


@strawberry.input
class PartidaInput:
    concepto: str
    importe_estimado: Optional[Decimal] = None
    tipo_partida: str = 'gasto'
    orden: int = 0


@strawberry.input
class ResultadoMetaInput:
    meta_id: uuid.UUID
    valor_real: Decimal


@strawberry.input
class ResultadoPartidaInput:
    partida_id: uuid.UUID
    importe_real: Decimal


@strawberry.input
class PlantillaCreateInput:
    tipo_campania_id: uuid.UUID
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


@strawberry.input
class PlantillaUpdateInput:
    plantilla_id: uuid.UUID
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


@strawberry.input
class PlantillaMetaItemInput:
    tipo_meta_id: uuid.UUID
    valor_sugerido: Optional[Decimal] = None
    notas: Optional[str] = None
    orden: int = 0


@strawberry.input
class PlantillaPartidaItemInput:
    concepto: str
    importe_estimado: Optional[Decimal] = None
    tipo_partida: str = 'gasto'
    orden: int = 0


@strawberry.input
class PlantillaActividadItemInput:
    plantilla_id: uuid.UUID
    nombre: str
    descripcion: Optional[str] = None
    duracion_dias: int = 0
    orden: int = 0
    tipo_actividad_id: Optional[uuid.UUID] = None


@strawberry.input
class PlantillaActividadUpdateItemInput:
    actividad_id: uuid.UUID
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    duracion_dias: Optional[int] = None
    orden: Optional[int] = None
    tipo_actividad_id: Optional[uuid.UUID] = None


@strawberry.input
class PlantillaTareaItemInput:
    actividad_id: uuid.UUID
    titulo: str
    descripcion: Optional[str] = None
    horas_estimadas: Optional[Decimal] = None
    orden: int = 0
    habilidad_id: Optional[uuid.UUID] = None
    nivel_habilidad_id: Optional[uuid.UUID] = None


@strawberry.input
class PlantillaTareaUpdateItemInput:
    tarea_id: uuid.UUID
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    horas_estimadas: Optional[Decimal] = None
    orden: Optional[int] = None
    habilidad_id: Optional[uuid.UUID] = None
    nivel_habilidad_id: Optional[uuid.UUID] = None


@strawberry.input
class ClonarCampaniaInput:
    campania_id: uuid.UUID
    nombre: str
    offset_dias: int = 0
    incluir_metas: bool = True
    incluir_partidas: bool = True
    incluir_canales: bool = True
    incluir_actividades: bool = True
    incluir_subcampanias: bool = False
    padre_id: Optional[uuid.UUID] = None


@strawberry.input
class PropagarACampaniasInput:
    campania_id: uuid.UUID
    campos: list[str]


@strawberry.type
class NotificacionCampaniaPreview:
    asunto: str
    cuerpo_html: str
    total_destinatarios: int


@strawberry.type
class ResultadoEnvioNotificacion:
    enviados: int
    fallidos: int
    sin_email: int
    total: int
    simulado: bool = False
    mensaje: Optional[str] = None


@strawberry.type
class CampaniaResolverMutation:

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_CREAR")])
    async def crear_campania(self, info: strawberry.Info, data: CampaniaCreateInput) -> CampaniaType:
        kwargs = {k: getattr(data, k) for k in [
            'fecha_inicio_plan', 'fecha_fin_plan', 'responsable_id', 'agrupacion_id',
            'lema', 'descripcion_corta', 'descripcion_larga', 'url_externa', 'foto_url',
            'objetivo_principal', 'es_recurrente', 'periodicidad',
        ] if getattr(data, k) is not None}
        campania = await CampaniaService(info.context.session).crear(
            nombre=data.nombre, tipo_campania_id=data.tipo_campania_id,
            estado_id=data.estado_id, **kwargs,
        )
        if data.responsable_id is not None:
            from app.modules.acceso.services.ambito_territorial import ensure_rol_coordinador_campania
            await ensure_rol_coordinador_campania(info.context.session, data.responsable_id)
        return campania

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def actualizar_campania(self, info: strawberry.Info, data: CampaniaUpdateInput) -> CampaniaType:
        campos = {k: getattr(data, k) for k in [
            'nombre', 'tipo_campania_id', 'estado_id', 'fecha_inicio_plan', 'fecha_fin_plan',
            'responsable_id', 'agrupacion_id', 'lema', 'descripcion_corta', 'descripcion_larga',
            'url_externa', 'foto_url', 'objetivo_principal', 'es_recurrente', 'periodicidad',
        ]}
        campania = await CampaniaService(info.context.session).actualizar(data.campania_id, campos)
        if campos.get('responsable_id') is not None:
            from app.modules.acceso.services.ambito_territorial import ensure_rol_coordinador_campania
            await ensure_rol_coordinador_campania(info.context.session, campos['responsable_id'])
        return campania

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def transicionar_campania(
        self, info: strawberry.Info, id: uuid.UUID, estado_id: uuid.UUID, notas: Optional[str] = None,
    ) -> CampaniaType:
        return await CampaniaService(info.context.session).transicionar_estado(id, estado_id, notas)

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_APROBAR")])
    async def aprobar_campania(
        self, info: strawberry.Info, id: uuid.UUID, estado_id: uuid.UUID, notas: Optional[str] = None,
    ) -> CampaniaType:
        return await CampaniaService(info.context.session).aprobar(
            id, estado_id, aprobado_por_id=getattr(info.context, 'user_id', None), notas=notas,
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def previsualizar_notificacion_campania(
        self, info: strawberry.Info, campania_id: uuid.UUID, plantilla_codigo: Optional[str] = None,
    ) -> NotificacionCampaniaPreview:
        r = await CampaniaService(info.context.session).previsualizar_notificacion(campania_id, plantilla_codigo)
        return NotificacionCampaniaPreview(**r)

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def enviar_notificacion_campania(
        self, info: strawberry.Info, campania_id: uuid.UUID, asunto: str, cuerpo_html: str,
    ) -> ResultadoEnvioNotificacion:
        r = await CampaniaService(info.context.session).enviar_notificacion(campania_id, asunto, cuerpo_html)
        return ResultadoEnvioNotificacion(**r)

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def cerrar_campania(
        self, info: strawberry.Info, id: uuid.UUID, estado_id: uuid.UUID,
        presupuesto_ejecutado: Decimal, resultados_metas: list[ResultadoMetaInput],
        resultados_partidas: list[ResultadoPartidaInput], valoracion: Optional[str] = None,
    ) -> CampaniaType:
        return await CampaniaService(info.context.session).cerrar(
            id, estado_id=estado_id, presupuesto_ejecutado=presupuesto_ejecutado,
            resultados_metas=[{"meta_id": r.meta_id, "valor_real": r.valor_real} for r in resultados_metas],
            resultados_partidas=[{"partida_id": r.partida_id, "importe_real": r.importe_real} for r in resultados_partidas],
            valoracion=valoracion,
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def guardar_metas_campania(
        self, info: strawberry.Info, campania_id: uuid.UUID, metas: list[MetaInput],
    ) -> CampaniaType:
        return await CampaniaService(info.context.session).guardar_metas(
            campania_id, [{"tipo_meta_id": m.tipo_meta_id, "valor_planificado": m.valor_planificado,
                           "notas": m.notas, "orden": m.orden} for m in metas],
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def guardar_canales_campania(
        self, info: strawberry.Info, campania_id: uuid.UUID, canal_ids: list[uuid.UUID],
    ) -> CampaniaType:
        return await CampaniaService(info.context.session).guardar_canales(campania_id, canal_ids)

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def guardar_partidas_campania(
        self, info: strawberry.Info, campania_id: uuid.UUID, partidas: list[PartidaInput],
    ) -> CampaniaType:
        return await CampaniaService(info.context.session).guardar_partidas(
            campania_id, [{"concepto": p.concepto, "importe_estimado": p.importe_estimado,
                           "tipo_partida": p.tipo_partida, "orden": p.orden} for p in partidas],
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def aplicar_plantilla(
        self, info: strawberry.Info, campania_id: uuid.UUID, plantilla_id: uuid.UUID,
    ) -> CampaniaType:
        return await CampaniaService(info.context.session).aplicar_plantilla(campania_id, plantilla_id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def crear_plantilla(self, info: strawberry.Info, data: PlantillaCreateInput) -> PlantillaCampaniaType:
        return await CampaniaService(info.context.session).crear_plantilla(
            data.tipo_campania_id, data.nombre, data.descripcion, data.activo,
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def crear_plantilla_desde_campania(
        self, info: strawberry.Info, campania_id: uuid.UUID, nombre: str,
        descripcion: Optional[str] = None,
    ) -> PlantillaCampaniaType:
        """Guarda una campaña existente como plantilla reutilizable (mismo tipo de campaña)."""
        return await CampaniaService(info.context.session).crear_plantilla_desde_campania(
            campania_id, nombre, descripcion,
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def actualizar_plantilla(self, info: strawberry.Info, data: PlantillaUpdateInput) -> PlantillaCampaniaType:
        return await CampaniaService(info.context.session).actualizar_plantilla(
            data.plantilla_id, {"nombre": data.nombre, "descripcion": data.descripcion, "activo": data.activo},
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def guardar_metas_plantilla(
        self, info: strawberry.Info, plantilla_id: uuid.UUID, metas: list[PlantillaMetaItemInput],
    ) -> PlantillaCampaniaType:
        return await CampaniaService(info.context.session).guardar_metas_plantilla(
            plantilla_id, [{"tipo_meta_id": m.tipo_meta_id, "valor_sugerido": m.valor_sugerido,
                            "notas": m.notas, "orden": m.orden} for m in metas],
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def guardar_partidas_plantilla(
        self, info: strawberry.Info, plantilla_id: uuid.UUID, partidas: list[PlantillaPartidaItemInput],
    ) -> PlantillaCampaniaType:
        return await CampaniaService(info.context.session).guardar_partidas_plantilla(
            plantilla_id, [{"concepto": p.concepto, "importe_estimado": p.importe_estimado,
                            "tipo_partida": p.tipo_partida, "orden": p.orden} for p in partidas],
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def crear_plantilla_actividad(
        self, info: strawberry.Info, data: PlantillaActividadItemInput,
    ) -> PlantillaActividadType:
        session = info.context.session
        act = PlantillaActividad(
            plantilla_id=data.plantilla_id, nombre=data.nombre, descripcion=data.descripcion,
            duracion_dias=data.duracion_dias, orden=data.orden, tipo_actividad_id=data.tipo_actividad_id,
        )
        session.add(act)
        await session.commit()
        await session.refresh(act)
        return act

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def actualizar_plantilla_actividad(
        self, info: strawberry.Info, data: PlantillaActividadUpdateItemInput,
    ) -> PlantillaActividadType:
        session = info.context.session
        act = (await session.execute(select(PlantillaActividad).where(PlantillaActividad.id == data.actividad_id))).scalar_one()
        for campo in ('nombre', 'descripcion', 'duracion_dias', 'orden', 'tipo_actividad_id'):
            v = getattr(data, campo, None)
            if v is not None:
                setattr(act, campo, v)
        await session.commit()
        await session.refresh(act)
        return act

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def crear_plantilla_tarea(
        self, info: strawberry.Info, data: PlantillaTareaItemInput,
    ) -> PlantillaTareaType:
        session = info.context.session
        tarea = PlantillaTarea(
            actividad_id=data.actividad_id, titulo=data.titulo, descripcion=data.descripcion,
            horas_estimadas=data.horas_estimadas, orden=data.orden,
            habilidad_id=data.habilidad_id, nivel_habilidad_id=data.nivel_habilidad_id,
        )
        session.add(tarea)
        await session.commit()
        await session.refresh(tarea)
        return tarea

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def actualizar_plantilla_tarea(
        self, info: strawberry.Info, data: PlantillaTareaUpdateItemInput,
    ) -> PlantillaTareaType:
        session = info.context.session
        tarea = (await session.execute(select(PlantillaTarea).where(PlantillaTarea.id == data.tarea_id))).scalar_one()
        for campo in ('titulo', 'descripcion', 'horas_estimadas', 'orden', 'habilidad_id', 'nivel_habilidad_id'):
            v = getattr(data, campo, None)
            if v is not None:
                setattr(tarea, campo, v)
        await session.commit()
        await session.refresh(tarea)
        return tarea


@strawberry.type
class CampaniaClonarMutation:

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def clonar_campania(self, info: strawberry.Info, data: ClonarCampaniaInput) -> CampaniaType:
        return await CampaniaService(info.context.session).clonar(
            campania_id=data.campania_id, nombre=data.nombre, offset_dias=data.offset_dias,
            incluir_metas=data.incluir_metas, incluir_partidas=data.incluir_partidas,
            incluir_canales=data.incluir_canales, incluir_actividades=data.incluir_actividades,
            incluir_subcampanias=data.incluir_subcampanias, padre_id=data.padre_id,
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_EDITAR")])
    async def propagar_a_subcampanias(
        self, info: strawberry.Info, data: PropagarACampaniasInput,
    ) -> list[CampaniaType]:
        return await CampaniaService(info.context.session).propagar_a_subcampanias(
            data.campania_id, data.campos,
        )
