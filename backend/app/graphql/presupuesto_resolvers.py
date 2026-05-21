"""Resolvers GraphQL del módulo de presupuestos (Fases 1 y 2)."""

import uuid
from decimal import Decimal
from datetime import date
from typing import List, Optional

import strawberry

from app.graphql.permissions import RequireTransaction
from app.modules.economico.services.presupuesto_service import PresupuestoService
from app.modules.economico.models.presupuesto import TipoModificacionPresupuestaria


@strawberry.type
class PartidaPresupuestariaDetailType:
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
    importe_inicial: float
    importe_modificaciones: float
    esta_sobreejecutada: bool
    esta_agotada: bool

    @staticmethod
    def from_model(p) -> "PartidaPresupuestariaDetailType":
        return PartidaPresupuestariaDetailType(
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
            importe_inicial=float(p.importe_inicial or 0),
            importe_modificaciones=float(p.importe_modificaciones),
            esta_sobreejecutada=p.esta_sobreejecutada,
            esta_agotada=p.esta_agotada,
        )


@strawberry.type
class PlanificacionAnualDetailType:
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
    control_disponibilidad: bool
    es_prorroga: bool
    ejercicio_origen_prorroga: Optional[int]

    @staticmethod
    def from_model(pl) -> "PlanificacionAnualDetailType":
        return PlanificacionAnualDetailType(
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
            control_disponibilidad=pl.control_disponibilidad,
            es_prorroga=pl.es_prorroga,
            ejercicio_origen_prorroga=pl.ejercicio_origen_prorroga,
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


@strawberry.type
class ModificacionPresupuestariaType:
    id: uuid.UUID
    tipo: str
    partida_destino_id: uuid.UUID
    partida_origen_id: Optional[uuid.UUID]
    importe: float
    fecha: date
    motivo: str

    @staticmethod
    def from_model(m) -> "ModificacionPresupuestariaType":
        return ModificacionPresupuestariaType(
            id=m.id,
            tipo=m.tipo.value if hasattr(m.tipo, "value") else m.tipo,
            partida_destino_id=m.partida_destino_id,
            partida_origen_id=m.partida_origen_id,
            importe=float(m.importe or 0),
            fecha=m.fecha,
            motivo=m.motivo,
        )


@strawberry.type
class AlertaPresupuestariaType:
    partida_id: str
    codigo: str
    nombre: str
    tipo_alerta: str
    mensaje: str


@strawberry.type
class ComparativaInteranualType:
    codigo: str
    nombre: str
    tipo: str
    importe_actual: float
    importe_anterior: float
    variacion: float
    variacion_porcentaje: Optional[float]


@strawberry.type
class LiquidacionPresupuestariaType:
    ejercicio: int
    existe: bool
    ingresos_previstos: float = 0.0
    ingresos_ejecutados: float = 0.0
    gastos_previstos: float = 0.0
    gastos_ejecutados: float = 0.0
    resultado_previsto: float = 0.0
    resultado_ejecutado: float = 0.0
    grado_ejecucion_gastos: float = 0.0


@strawberry.input
class RegistrarModificacionInput:
    planificacion_id: uuid.UUID
    tipo: str  # TRANSFERENCIA | AMPLIACION | SUPLEMENTO
    partida_destino_id: uuid.UUID
    importe: float
    motivo: str
    partida_origen_id: Optional[uuid.UUID] = None


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
    async def planificaciones(self, info: strawberry.Info) -> List[PlanificacionAnualDetailType]:
        service = PresupuestoService(info.context.session)
        items = await service.listar_planificaciones()
        return [PlanificacionAnualDetailType.from_model(p) for p in items]

    @strawberry.field(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CONSULTAR")])
    async def planificacion(
        self, info: strawberry.Info, planificacion_id: uuid.UUID
    ) -> Optional[PlanificacionAnualDetailType]:
        service = PresupuestoService(info.context.session)
        p = await service.obtener_planificacion(planificacion_id)
        return PlanificacionAnualDetailType.from_model(p) if p else None

    @strawberry.field(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CONSULTAR")])
    async def partidas_presupuestarias(
        self, info: strawberry.Info, planificacion_id: uuid.UUID, tipo: Optional[str] = None
    ) -> List[PartidaPresupuestariaDetailType]:
        service = PresupuestoService(info.context.session)
        items = await service.listar_partidas(planificacion_id, tipo=tipo)
        return [PartidaPresupuestariaDetailType.from_model(p) for p in items]

    @strawberry.field(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CONSULTAR")])
    async def informe_desviaciones(
        self, info: strawberry.Info, planificacion_id: uuid.UUID
    ) -> List[DesviacionPartidaType]:
        service = PresupuestoService(info.context.session)
        filas = await service.informe_desviaciones(planificacion_id)
        return [DesviacionPartidaType(**f) for f in filas]

    @strawberry.field(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CONSULTAR")])
    async def modificaciones_presupuestarias(
        self, info: strawberry.Info, planificacion_id: uuid.UUID
    ) -> List[ModificacionPresupuestariaType]:
        service = PresupuestoService(info.context.session)
        items = await service.listar_modificaciones(planificacion_id)
        return [ModificacionPresupuestariaType.from_model(m) for m in items]

    @strawberry.field(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CONSULTAR")])
    async def alertas_presupuestarias(
        self, info: strawberry.Info, planificacion_id: uuid.UUID
    ) -> List[AlertaPresupuestariaType]:
        service = PresupuestoService(info.context.session)
        filas = await service.alertas(planificacion_id)
        return [AlertaPresupuestariaType(**f) for f in filas]

    @strawberry.field(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CONSULTAR")])
    async def comparativa_interanual(
        self, info: strawberry.Info, ejercicio: int
    ) -> List[ComparativaInteranualType]:
        service = PresupuestoService(info.context.session)
        filas = await service.comparativa_interanual(ejercicio)
        return [ComparativaInteranualType(**f) for f in filas]

    @strawberry.field(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CONSULTAR")])
    async def liquidacion_presupuestaria(
        self, info: strawberry.Info, ejercicio: int
    ) -> LiquidacionPresupuestariaType:
        service = PresupuestoService(info.context.session)
        d = await service.liquidacion_presupuestaria(ejercicio)
        return LiquidacionPresupuestariaType(**d)


@strawberry.type
class PresupuestoMutation:

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CREAR")])
    async def crear_planificacion(
        self, info: strawberry.Info, data: CrearPlanificacionInput
    ) -> PlanificacionAnualDetailType:
        service = PresupuestoService(info.context.session)
        p = await service.crear_planificacion(
            ejercicio=data.ejercicio, nombre=data.nombre,
            descripcion=data.descripcion, objetivos=data.objetivos,
        )
        return PlanificacionAnualDetailType.from_model(p)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CREAR")])
    async def crear_partida(
        self, info: strawberry.Info, data: CrearPartidaInput
    ) -> PartidaPresupuestariaDetailType:
        service = PresupuestoService(info.context.session)
        p = await service.crear_partida(
            planificacion_id=data.planificacion_id,
            codigo=data.codigo, nombre=data.nombre, tipo=data.tipo,
            importe_presupuestado=Decimal(str(data.importe_presupuestado)),
            categoria_id=data.categoria_id, actividad_id=data.actividad_id,
            campania_id=data.campania_id, descripcion=data.descripcion,
        )
        return PartidaPresupuestariaDetailType.from_model(p)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CREAR")])
    async def actualizar_partida(
        self, info: strawberry.Info, data: ActualizarPartidaInput
    ) -> PartidaPresupuestariaDetailType:
        service = PresupuestoService(info.context.session)
        cambios = {}
        for k in ("nombre", "descripcion", "categoria_id", "actividad_id", "campania_id"):
            v = getattr(data, k)
            if v is not None:
                cambios[k] = v
        if data.importe_presupuestado is not None:
            cambios["importe_presupuestado"] = Decimal(str(data.importe_presupuestado))
        p = await service.actualizar_partida(data.id, **cambios)
        return PartidaPresupuestariaDetailType.from_model(p)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CREAR")])
    async def eliminar_partida(self, info: strawberry.Info, partida_id: uuid.UUID) -> bool:
        service = PresupuestoService(info.context.session)
        await service.eliminar_partida(partida_id)
        return True

    # ── Transiciones del ciclo de vida ──────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CREAR")])
    async def proponer_presupuesto(
        self, info: strawberry.Info, planificacion_id: uuid.UUID
    ) -> PlanificacionAnualDetailType:
        service = PresupuestoService(info.context.session)
        p = await service.proponer(planificacion_id)
        return PlanificacionAnualDetailType.from_model(p)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_APROBAR")])
    async def aprobar_presupuesto(
        self, info: strawberry.Info, planificacion_id: uuid.UUID
    ) -> PlanificacionAnualDetailType:
        service = PresupuestoService(info.context.session)
        p = await service.aprobar(planificacion_id)
        return PlanificacionAnualDetailType.from_model(p)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_APROBAR")])
    async def iniciar_ejecucion_presupuesto(
        self, info: strawberry.Info, planificacion_id: uuid.UUID
    ) -> PlanificacionAnualDetailType:
        service = PresupuestoService(info.context.session)
        p = await service.iniciar_ejecucion(planificacion_id)
        return PlanificacionAnualDetailType.from_model(p)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_APROBAR")])
    async def cerrar_presupuesto(
        self, info: strawberry.Info, planificacion_id: uuid.UUID
    ) -> PlanificacionAnualDetailType:
        service = PresupuestoService(info.context.session)
        p = await service.cerrar(planificacion_id)
        return PlanificacionAnualDetailType.from_model(p)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CREAR")])
    async def devolver_presupuesto_a_borrador(
        self, info: strawberry.Info, planificacion_id: uuid.UUID
    ) -> PlanificacionAnualDetailType:
        service = PresupuestoService(info.context.session)
        p = await service.devolver_a_borrador(planificacion_id)
        return PlanificacionAnualDetailType.from_model(p)

    # ── Fase 2 ───────────────────────────────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_APROBAR")])
    async def registrar_modificacion_presupuestaria(
        self, info: strawberry.Info, data: RegistrarModificacionInput
    ) -> ModificacionPresupuestariaType:
        service = PresupuestoService(info.context.session)
        usuario_id = info.context.current_user.id if info.context.current_user else None
        m = await service.registrar_modificacion(
            planificacion_id=data.planificacion_id,
            tipo=TipoModificacionPresupuestaria[data.tipo],
            partida_destino_id=data.partida_destino_id,
            importe=Decimal(str(data.importe)),
            motivo=data.motivo,
            partida_origen_id=data.partida_origen_id,
            registrada_por_id=usuario_id,
        )
        return ModificacionPresupuestariaType.from_model(m)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_APROBAR")])
    async def establecer_control_disponibilidad(
        self, info: strawberry.Info, planificacion_id: uuid.UUID, activo: bool
    ) -> PlanificacionAnualDetailType:
        service = PresupuestoService(info.context.session)
        plan = await service.obtener_planificacion(planificacion_id)
        if not plan:
            raise ValueError("Planificación no encontrada")
        plan.control_disponibilidad = activo
        service.session.add(plan)
        await service.session.commit()
        await service.session.refresh(plan)
        return PlanificacionAnualDetailType.from_model(plan)

    # ── Fase 3 ───────────────────────────────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_CREAR")])
    async def clonar_presupuesto(
        self, info: strawberry.Info, ejercicio_origen: int, ejercicio_nuevo: int,
        nombre: Optional[str] = None,
    ) -> PlanificacionAnualDetailType:
        service = PresupuestoService(info.context.session)
        p = await service.clonar_planificacion(ejercicio_origen, ejercicio_nuevo, nombre=nombre)
        return PlanificacionAnualDetailType.from_model(p)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_PRESUPUESTO_APROBAR")])
    async def prorrogar_presupuesto(
        self, info: strawberry.Info, ejercicio_origen: int, ejercicio_nuevo: int
    ) -> PlanificacionAnualDetailType:
        service = PresupuestoService(info.context.session)
        p = await service.prorrogar(ejercicio_origen, ejercicio_nuevo)
        return PlanificacionAnualDetailType.from_model(p)
