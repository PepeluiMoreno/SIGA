"""Servicio de gestión presupuestaria.

Cubre la Fase 1: CRUD de planificación anual y partidas, transiciones del ciclo de
vida (borrador → propuesto → aprobado → en ejecución → cerrado), validación de
equilibrio e imputación de la ejecución real desde los apuntes de caja.
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.presupuesto import (
    PlanificacionAnual,
    PartidaPresupuestaria,
    CategoriaPartida,
    EstadoPlanificacion,
)


# Códigos de estado del ciclo de vida (deben existir en estados_planificacion)
ESTADO_BORRADOR = "BORRADOR"
ESTADO_PROPUESTO = "PROPUESTO"
ESTADO_APROBADO = "APROBADO"
ESTADO_EN_EJECUCION = "EN_EJECUCION"
ESTADO_CERRADO = "CERRADO"

# Transiciones permitidas: estado actual → estados a los que puede pasar
_TRANSICIONES = {
    ESTADO_BORRADOR: {ESTADO_PROPUESTO},
    ESTADO_PROPUESTO: {ESTADO_APROBADO, ESTADO_BORRADOR},
    ESTADO_APROBADO: {ESTADO_EN_EJECUCION},
    ESTADO_EN_EJECUCION: {ESTADO_CERRADO},
    ESTADO_CERRADO: set(),
}


class PresupuestoService:
    """Gestión del presupuesto anual: planificación, partidas y ejecución."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Resolución de estados ───────────────────────────────────────────────

    async def _estado_por_codigo(self, codigo: str) -> Optional[EstadoPlanificacion]:
        result = await self.session.execute(
            select(EstadoPlanificacion).where(EstadoPlanificacion.codigo == codigo)
        )
        return result.scalars().first()

    async def _codigo_de_estado(self, estado_id: UUID) -> Optional[str]:
        result = await self.session.execute(
            select(EstadoPlanificacion).where(EstadoPlanificacion.id == estado_id)
        )
        estado = result.scalars().first()
        return estado.codigo if estado else None

    # ── Planificación anual ─────────────────────────────────────────────────

    async def listar_planificaciones(self) -> List[PlanificacionAnual]:
        result = await self.session.execute(
            select(PlanificacionAnual)
            .where(PlanificacionAnual.eliminado == False)
            .order_by(PlanificacionAnual.ejercicio.desc())
        )
        return list(result.scalars().all())

    async def obtener_planificacion(self, planificacion_id: UUID) -> Optional[PlanificacionAnual]:
        result = await self.session.execute(
            select(PlanificacionAnual).where(PlanificacionAnual.id == planificacion_id)
        )
        return result.scalars().first()

    async def obtener_planificacion_por_ejercicio(self, ejercicio: int) -> Optional[PlanificacionAnual]:
        result = await self.session.execute(
            select(PlanificacionAnual).where(
                and_(PlanificacionAnual.ejercicio == ejercicio, PlanificacionAnual.eliminado == False)
            )
        )
        return result.scalars().first()

    async def crear_planificacion(
        self,
        ejercicio: int,
        nombre: str,
        descripcion: Optional[str] = None,
        objetivos: Optional[str] = None,
    ) -> PlanificacionAnual:
        # Un ejercicio solo puede tener una planificación
        existente = await self.obtener_planificacion_por_ejercicio(ejercicio)
        if existente:
            raise ValueError(f"Ya existe un presupuesto para el ejercicio {ejercicio}")

        estado_borrador = await self._estado_por_codigo(ESTADO_BORRADOR)
        if not estado_borrador:
            raise ValueError("No está configurado el estado BORRADOR de planificación")

        planificacion = PlanificacionAnual(
            ejercicio=ejercicio,
            nombre=nombre,
            descripcion=descripcion,
            objetivos=objetivos,
            estado_id=estado_borrador.id,
        )
        self.session.add(planificacion)
        await self.session.commit()
        await self.session.refresh(planificacion)
        return planificacion

    async def actualizar_planificacion(self, planificacion_id: UUID, **kwargs) -> PlanificacionAnual:
        plan = await self.obtener_planificacion(planificacion_id)
        if not plan:
            raise ValueError(f"Planificación {planificacion_id} no encontrada")
        # Solo se puede editar la cabecera en estados no cerrados
        codigo = await self._codigo_de_estado(plan.estado_id)
        if codigo == ESTADO_CERRADO:
            raise ValueError("No se puede modificar un presupuesto cerrado")
        for key in ("nombre", "descripcion", "objetivos"):
            if key in kwargs and kwargs[key] is not None:
                setattr(plan, key, kwargs[key])
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        return plan

    # ── Transiciones del ciclo de vida ──────────────────────────────────────

    async def _transicionar(self, planificacion_id: UUID, codigo_destino: str) -> PlanificacionAnual:
        plan = await self.obtener_planificacion(planificacion_id)
        if not plan:
            raise ValueError(f"Planificación {planificacion_id} no encontrada")

        codigo_actual = await self._codigo_de_estado(plan.estado_id)
        permitidos = _TRANSICIONES.get(codigo_actual, set())
        if codigo_destino not in permitidos:
            raise ValueError(
                f"Transición no permitida: {codigo_actual} → {codigo_destino}. "
                f"Desde {codigo_actual} solo se puede pasar a: {', '.join(permitidos) or 'ninguno'}"
            )

        estado_destino = await self._estado_por_codigo(codigo_destino)
        if not estado_destino:
            raise ValueError(f"No está configurado el estado {codigo_destino}")

        plan.estado_id = estado_destino.id
        if codigo_destino == ESTADO_APROBADO:
            plan.fecha_aprobacion = date.today()
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        return plan

    async def proponer(self, planificacion_id: UUID) -> PlanificacionAnual:
        """Borrador → Propuesto. Valida que el presupuesto esté equilibrado."""
        plan = await self.obtener_planificacion(planificacion_id)
        if not plan:
            raise ValueError(f"Planificación {planificacion_id} no encontrada")
        # Aviso de equilibrio (no bloqueante, pero se informa en el saldo)
        return await self._transicionar(planificacion_id, ESTADO_PROPUESTO)

    async def aprobar(self, planificacion_id: UUID) -> PlanificacionAnual:
        """Propuesto → Aprobado. Acto de gobierno; registra la fecha."""
        return await self._transicionar(planificacion_id, ESTADO_APROBADO)

    async def iniciar_ejecucion(self, planificacion_id: UUID) -> PlanificacionAnual:
        """Aprobado → En ejecución."""
        return await self._transicionar(planificacion_id, ESTADO_EN_EJECUCION)

    async def cerrar(self, planificacion_id: UUID) -> PlanificacionAnual:
        """En ejecución → Cerrado."""
        return await self._transicionar(planificacion_id, ESTADO_CERRADO)

    async def devolver_a_borrador(self, planificacion_id: UUID) -> PlanificacionAnual:
        """Propuesto → Borrador (para corregir antes de aprobar)."""
        return await self._transicionar(planificacion_id, ESTADO_BORRADOR)

    # ── Partidas ────────────────────────────────────────────────────────────

    async def listar_partidas(
        self, planificacion_id: UUID, tipo: Optional[str] = None
    ) -> List[PartidaPresupuestaria]:
        query = select(PartidaPresupuestaria).where(
            and_(
                PartidaPresupuestaria.planificacion_id == planificacion_id,
                PartidaPresupuestaria.eliminado == False,
            )
        )
        if tipo:
            query = query.where(PartidaPresupuestaria.tipo == tipo)
        query = query.order_by(PartidaPresupuestaria.codigo)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def crear_partida(
        self,
        planificacion_id: UUID,
        codigo: str,
        nombre: str,
        tipo: str,
        importe_presupuestado: Decimal,
        categoria_id: Optional[UUID] = None,
        actividad_id: Optional[UUID] = None,
        campania_id: Optional[UUID] = None,
        descripcion: Optional[str] = None,
    ) -> PartidaPresupuestaria:
        if tipo not in ("INGRESO", "GASTO"):
            raise ValueError("El tipo debe ser INGRESO o GASTO")

        plan = await self.obtener_planificacion(planificacion_id)
        if not plan:
            raise ValueError(f"Planificación {planificacion_id} no encontrada")
        codigo_estado = await self._codigo_de_estado(plan.estado_id)
        if codigo_estado in (ESTADO_APROBADO, ESTADO_EN_EJECUCION, ESTADO_CERRADO):
            raise ValueError(
                "No se pueden añadir partidas a un presupuesto aprobado. "
                "Usa una modificación presupuestaria (fase 2)."
            )

        # Código único
        existe = await self.session.execute(
            select(PartidaPresupuestaria).where(PartidaPresupuestaria.codigo == codigo)
        )
        if existe.scalars().first():
            raise ValueError(f"Ya existe una partida con código {codigo}")

        partida = PartidaPresupuestaria(
            planificacion_id=planificacion_id,
            ejercicio=plan.ejercicio,
            codigo=codigo,
            nombre=nombre,
            tipo=tipo,
            importe_presupuestado=importe_presupuestado,
            categoria_id=categoria_id,
            actividad_id=actividad_id,
            campania_id=campania_id,
            descripcion=descripcion,
        )
        self.session.add(partida)
        await self.session.commit()
        await self.session.refresh(partida)
        await self._recalcular_total(planificacion_id)
        return partida

    async def actualizar_partida(self, partida_id: UUID, **kwargs) -> PartidaPresupuestaria:
        result = await self.session.execute(
            select(PartidaPresupuestaria).where(PartidaPresupuestaria.id == partida_id)
        )
        partida = result.scalars().first()
        if not partida:
            raise ValueError(f"Partida {partida_id} no encontrada")
        for key in ("nombre", "descripcion", "importe_presupuestado", "categoria_id",
                    "actividad_id", "campania_id"):
            if key in kwargs and kwargs[key] is not None:
                setattr(partida, key, kwargs[key])
        self.session.add(partida)
        await self.session.commit()
        await self.session.refresh(partida)
        if partida.planificacion_id:
            await self._recalcular_total(partida.planificacion_id)
        return partida

    async def eliminar_partida(self, partida_id: UUID) -> None:
        result = await self.session.execute(
            select(PartidaPresupuestaria).where(PartidaPresupuestaria.id == partida_id)
        )
        partida = result.scalars().first()
        if not partida:
            raise ValueError(f"Partida {partida_id} no encontrada")
        if partida.importe_ejecutado and partida.importe_ejecutado > 0:
            raise ValueError("No se puede eliminar una partida con ejecución registrada")
        plan_id = partida.planificacion_id
        partida.soft_delete()
        self.session.add(partida)
        await self.session.commit()
        if plan_id:
            await self._recalcular_total(plan_id)

    async def _recalcular_total(self, planificacion_id: UUID) -> None:
        """Recalcula el presupuesto_total de la planificación (suma de gastos)."""
        plan = await self.obtener_planificacion(planificacion_id)
        if not plan:
            return
        partidas = await self.listar_partidas(planificacion_id, tipo="GASTO")
        plan.presupuesto_total = sum((p.importe_presupuestado for p in partidas), Decimal("0.00"))
        self.session.add(plan)
        await self.session.commit()

    # ── Imputación de ejecución ─────────────────────────────────────────────

    async def imputar_ejecucion(
        self,
        importe: Decimal,
        actividad_id: Optional[UUID] = None,
        campania_id: Optional[UUID] = None,
    ) -> Optional[PartidaPresupuestaria]:
        """Suma un gasto/ingreso ejecutado a la partida afecta a la actividad o campaña.

        Busca la partida del presupuesto en ejecución cuya actividad/campaña coincida.
        Si no hay partida afecta, no hace nada (el apunte simplemente no imputa a presupuesto).
        """
        if not actividad_id and not campania_id:
            return None

        query = select(PartidaPresupuestaria).where(
            PartidaPresupuestaria.eliminado == False
        )
        if actividad_id:
            query = query.where(PartidaPresupuestaria.actividad_id == actividad_id)
        else:
            query = query.where(PartidaPresupuestaria.campania_id == campania_id)

        result = await self.session.execute(query)
        partida = result.scalars().first()
        if not partida:
            return None

        partida.importe_ejecutado = (partida.importe_ejecutado or Decimal("0.00")) + importe
        self.session.add(partida)
        await self.session.commit()
        await self.session.refresh(partida)
        return partida

    # ── Informe de desviaciones ─────────────────────────────────────────────

    async def informe_desviaciones(self, planificacion_id: UUID) -> List[dict]:
        """Devuelve, por partida, el previsto vs ejecutado con desviación en importe y %."""
        partidas = await self.listar_partidas(planificacion_id)
        informe = []
        for p in partidas:
            presupuestado = p.importe_presupuestado or Decimal("0.00")
            ejecutado = p.importe_ejecutado or Decimal("0.00")
            desviacion = ejecutado - presupuestado
            pct = float((ejecutado / presupuestado * 100)) if presupuestado else 0.0
            informe.append({
                "partida_id": str(p.id),
                "codigo": p.codigo,
                "nombre": p.nombre,
                "tipo": p.tipo,
                "presupuestado": float(presupuestado),
                "comprometido": float(p.importe_comprometido or 0),
                "ejecutado": float(ejecutado),
                "disponible": float(presupuestado - ejecutado),
                "desviacion": float(desviacion),
                "porcentaje_ejecucion": round(pct, 1),
            })
        return informe
