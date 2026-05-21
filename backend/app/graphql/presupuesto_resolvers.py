"""Resolvers GraphQL del módulo de presupuestos (Fase 1)."""

import uuid
from decimal import Decimal
from datetime import date
from typing import List, Optional

import strawberry

from app.graphql.permissions import RequireTransaction
from app.modules.economico.services.presupuesto_service import PresupuestoService


@strawberry.type
class PartidaPresupuestariaType:
    id: uuid.UUID
    codigo: str
    nombre: str
    descripcion: Optional[str]
    ejercicio: int
    tipo: str
    categoria_id: Optional[uuid.UUID]
    actividad_id: Optional[uuid.UUID]
    campania_id: Optional[uuid.UUID]
    importe_presupuestado: float
    importe_comprometido: float
    importe_ejecutado: float
    importe_disponible: float
    porcentaje_ejecutado: float

    @staticmethod
    def from_model(p) -> "PartidaPresupuestariaType":
        return PartidaPresupuestariaType(
            id=p.id,
            codigo=p.codigo,
            nombre=p.nombre,
            descripcion=p.descripcion,
            ejercicio=p.ejercicio,
            tipo=p.tipo,
            categoria_id=p.categoria_id,
            actividad_id=p.actividad_id,
            campania_id=p.campania_id,
            importe_presupuestado=float(p.importe_presupuestado or 0),
            importe_comprometido=float(p.importe_comprometido or 0),
            importe_ejecutado=float(p.importe_ejecutado or 0),
            importe_disponible=float(p.importe_disponible),
            porcentaje_ejecutado=round(p.porcentaje_ejecutado, 1),
        )


@strawberry.type
class PlanificacionAnualType:
    id: uuid.UUID
    ejercicio: int
    nombre: str
    descripcion: Optional[str]
    objetivos: Optional[str]
    estado_id: uuid.UUID
    fecha_aprobacion: Optional[date]
    presupuesto_total: float
    presupuesto_ingresos: float
    presupuesto_gastos: float
    saldo_presupuestado: float
    gastos_ejecutados: float
    porcentaje_ejecucion: float

    @staticmethod
    def from_model(pl) -> "PlanificacionAnualType":
        return PlanificacionAnualType(
            id=pl.id,
            ejercicio=pl.ejercicio,
            nombre=pl.nombre,
            descripcion=pl.descripcion,
            objetivos=pl.objetivos,
            estado_id=pl.estado_id,
            fecha_aprobacion=pl.fecha_aprobacion,
            presupuesto_total=float(pl.presupuesto_total or 0),
            presupuesto_ingresos=float(pl.presupuesto_ingresos or 0),
            presupuesto_gastos=float(pl.presupuesto_gastos or 0),
            saldo_presupuestado=float(pl.saldo_presupuestado or 0),
            gastos_ejecutados=float(pl.gastos_ejecutados or 0),
            porcentaje_ejecucion=round(pl.porcentaje_ejecucion, 1),
        )


@strawberry.type
class DesviacionPartidaType:
    partida_id: str
    codigo: str
    nombre: str
    tipo: str
    presupuestado: float
    comprometido: float
    ejecutado: float
    disponible: float
    desviacion: float
    porcentaje_ejecucion: float


@strawberry.input
class CrearPlanificacionInput:
    ejercicio: int
    nombre: str
    descripcion: Optional[str] = None
    objetivos: Optional[str] = None


@strawberry.input
class CrearPartidaInput:
    planificacion_id: uuid.UUID
    codigo: str
    nombre: str
    tipo: str  # INGRESO | GASTO
    importe_presupuestado: float
    categoria_id: Optional[uuid.UUID] = None
    actividad_id: Optional[uuid.UUID] = None
    campania_id: Optional[uuid.UUID] = None
    descripcion: Optional[str] = None


@strawberry.input
class ActualizarPartidaInput:
    id: uuid.UUID
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    importe_presupuestado: Optional[float] = None
    categoria_id: Optional[uuid.UUID] = None
    actividad_id: Optional[uuid.UUID] = None
    campania_id: Optional[uuid.UUID] = None


@strawberry.type
class PresupuestoQuery:

    @strawberry.field(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CONSULTAR")])
    async def planificaciones(self, info: strawberry.Info) -> List[PlanificacionAnualType]:
        service = PresupuestoService(info.context.session)
        items = await service.listar_planificaciones()
        return [PlanificacionAnualType.from_model(p) for p in items]

    @strawberry.field(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CONSULTAR")])
    async def planificacion(
        self, info: strawberry.Info, planificacion_id: uuid.UUID
    ) -> Optional[PlanificacionAnualType]:
        service = PresupuestoService(info.context.session)
        p = await service.obtener_planificacion(planificacion_id)
        return PlanificacionAnualType.from_model(p) if p else None

    @strawberry.field(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CONSULTAR")])
    async def partidas_presupuestarias(
        self, info: strawberry.Info, planificacion_id: uuid.UUID, tipo: Optional[str] = None
    ) -> List[PartidaPresupuestariaType]:
        service = PresupuestoService(info.context.session)
        items = await service.listar_partidas(planificacion_id, tipo=tipo)
        return [PartidaPresupuestariaType.from_model(p) for p in items]

    @strawberry.field(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CONSULTAR")])
    async def informe_desviaciones(
        self, info: strawberry.Info, planificacion_id: uuid.UUID
    ) -> List[DesviacionPartidaType]:
        service = PresupuestoService(info.context.session)
        filas = await service.informe_desviaciones(planificacion_id)
        return [DesviacionPartidaType(**f) for f in filas]


@strawberry.type
class PresupuestoMutation:

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CREAR")])
    async def crear_planificacion(
        self, info: strawberry.Info, data: CrearPlanificacionInput
    ) -> PlanificacionAnualType:
        service = PresupuestoService(info.context.session)
        p = await service.crear_planificacion(
            ejercicio=data.ejercicio, nombre=data.nombre,
            descripcion=data.descripcion, objetivos=data.objetivos,
        )
        return PlanificacionAnualType.from_model(p)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CREAR")])
    async def crear_partida(
        self, info: strawberry.Info, data: CrearPartidaInput
    ) -> PartidaPresupuestariaType:
        service = PresupuestoService(info.context.session)
        p = await service.crear_partida(
            planificacion_id=data.planificacion_id,
            codigo=data.codigo, nombre=data.nombre, tipo=data.tipo,
            importe_presupuestado=Decimal(str(data.importe_presupuestado)),
            categoria_id=data.categoria_id, actividad_id=data.actividad_id,
            campania_id=data.campania_id, descripcion=data.descripcion,
        )
        return PartidaPresupuestariaType.from_model(p)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CREAR")])
    async def actualizar_partida(
        self, info: strawberry.Info, data: ActualizarPartidaInput
    ) -> PartidaPresupuestariaType:
        service = PresupuestoService(info.context.session)
        cambios = {}
        for k in ("nombre", "descripcion", "categoria_id", "actividad_id", "campania_id"):
            v = getattr(data, k)
            if v is not None:
                cambios[k] = v
        if data.importe_presupuestado is not None:
            cambios["importe_presupuestado"] = Decimal(str(data.importe_presupuestado))
        p = await service.actualizar_partida(data.id, **cambios)
        return PartidaPresupuestariaType.from_model(p)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CREAR")])
    async def eliminar_partida(self, info: strawberry.Info, partida_id: uuid.UUID) -> bool:
        service = PresupuestoService(info.context.session)
        await service.eliminar_partida(partida_id)
        return True

    # ── Transiciones del ciclo de vida ──────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CREAR")])
    async def proponer_presupuesto(
        self, info: strawberry.Info, planificacion_id: uuid.UUID
    ) -> PlanificacionAnualType:
        service = PresupuestoService(info.context.session)
        p = await service.proponer(planificacion_id)
        return PlanificacionAnualType.from_model(p)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_APROBAR")])
    async def aprobar_presupuesto(
        self, info: strawberry.Info, planificacion_id: uuid.UUID
    ) -> PlanificacionAnualType:
        service = PresupuestoService(info.context.session)
        p = await service.aprobar(planificacion_id)
        return PlanificacionAnualType.from_model(p)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_APROBAR")])
    async def iniciar_ejecucion_presupuesto(
        self, info: strawberry.Info, planificacion_id: uuid.UUID
    ) -> PlanificacionAnualType:
        service = PresupuestoService(info.context.session)
        p = await service.iniciar_ejecucion(planificacion_id)
        return PlanificacionAnualType.from_model(p)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_APROBAR")])
    async def cerrar_presupuesto(
        self, info: strawberry.Info, planificacion_id: uuid.UUID
    ) -> PlanificacionAnualType:
        service = PresupuestoService(info.context.session)
        p = await service.cerrar(planificacion_id)
        return PlanificacionAnualType.from_model(p)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CREAR")])
    async def devolver_presupuesto_a_borrador(
        self, info: strawberry.Info, planificacion_id: uuid.UUID
    ) -> PlanificacionAnualType:
        service = PresupuestoService(info.context.session)
        p = await service.devolver_a_borrador(planificacion_id)
        return PlanificacionAnualType.from_model(p)
