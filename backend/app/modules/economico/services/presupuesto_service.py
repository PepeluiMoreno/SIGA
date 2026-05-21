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
    ModificacionPresupuestaria,
    TipoModificacionPresupuestaria,
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

    # ── Fase 3: clonado, prórroga, comparativa, liquidación ──────────────────

    async def calcular_ratio_cuota(
        self,
        ejercicio_origen: int,
        ejercicio_nuevo: int,
    ) -> Optional[Decimal]:
        """Devuelve el ratio cuota_nuevo/cuota_origen o None si alguno no está definido.

        Suma todos los importes de ImporteCuotaAnio de cada ejercicio (puede haber varios
        tipos de miembro). Si el total origen es cero devuelve None.
        """
        from sqlalchemy import func
        from ..models.cuotas import ImporteCuotaAnio

        async def _total(ejercicio: int) -> Decimal:
            result = await self.session.execute(
                select(func.sum(ImporteCuotaAnio.importe)).where(
                    ImporteCuotaAnio.ejercicio == ejercicio
                )
            )
            return result.scalar_one_or_none() or Decimal("0")

        total_origen = await _total(ejercicio_origen)
        total_nuevo  = await _total(ejercicio_nuevo)

        if not total_origen:
            return None
        if not total_nuevo:
            return None
        return (total_nuevo / total_origen).quantize(Decimal("0.0001"))

    async def clonar_planificacion(
        self,
        ejercicio_origen: int,
        ejercicio_nuevo: int,
        nombre: Optional[str] = None,
        es_prorroga: bool = False,
        factor: Optional[Decimal] = None,
    ) -> PlanificacionAnual:
        """Crea el presupuesto de un ejercicio copiando las partidas de otro.

        Si se indica `factor`, escala todos los importes presupuestados por ese valor
        (p. ej. el ratio de variación de cuota entre ejercicios).

        Las partidas se copian con su importe presupuestado como punto de partida; el
        ejecutado y comprometido arrancan a cero. El nuevo nace en BORRADOR.
        Si es_prorroga=True, queda marcado como prórroga del ejercicio origen.
        """
        origen = await self.obtener_planificacion_por_ejercicio(ejercicio_origen)
        if not origen:
            raise ValueError(f"No existe presupuesto del ejercicio {ejercicio_origen} para copiar")
        if await self.obtener_planificacion_por_ejercicio(ejercicio_nuevo):
            raise ValueError(f"Ya existe un presupuesto para el ejercicio {ejercicio_nuevo}")

        estado_borrador = await self._estado_por_codigo(ESTADO_BORRADOR)
        if not estado_borrador:
            raise ValueError("No está configurado el estado BORRADOR")

        nuevo = PlanificacionAnual(
            ejercicio=ejercicio_nuevo,
            nombre=nombre or (f"Prórroga {ejercicio_nuevo}" if es_prorroga else f"Presupuesto {ejercicio_nuevo}"),
            descripcion=origen.descripcion,
            objetivos=origen.objetivos,
            estado_id=estado_borrador.id,
            es_prorroga=es_prorroga,
            ejercicio_origen_prorroga=ejercicio_origen if es_prorroga else None,
        )
        self.session.add(nuevo)
        await self.session.commit()
        await self.session.refresh(nuevo)

        # Copiar las partidas (importe presupuestado como base; ejecución a cero)
        _factor = (factor or Decimal("1")).quantize(Decimal("0.0001"))
        partidas_origen = await self.listar_partidas(origen.id)
        for po in partidas_origen:
            importe = (po.importe_presupuestado * _factor).quantize(Decimal("0.01"))
            self.session.add(PartidaPresupuestaria(
                planificacion_id=nuevo.id,
                ejercicio=ejercicio_nuevo,
                codigo=f"{ejercicio_nuevo}-{po.codigo.split('-', 1)[-1]}" if "-" in po.codigo else f"{ejercicio_nuevo}-{po.codigo}",
                nombre=po.nombre,
                tipo=po.tipo,
                importe_presupuestado=importe,
                categoria_id=po.categoria_id,
                actividad_id=po.actividad_id,
                campania_id=po.campania_id,
                descripcion=po.descripcion,
            ))
        await self.session.commit()
        await self._recalcular_total(nuevo.id)
        return nuevo

    async def prorrogar(self, ejercicio_origen: int, ejercicio_nuevo: int) -> PlanificacionAnual:
        """Prorroga el presupuesto del ejercicio anterior al nuevo (caso especial de clonado).

        Se usa cuando el presupuesto del nuevo ejercicio no se aprueba a tiempo: rige el
        anterior hasta que se apruebe el definitivo.
        """
        origen = await self.obtener_planificacion_por_ejercicio(ejercicio_origen)
        if not origen:
            raise ValueError(f"No existe presupuesto del ejercicio {ejercicio_origen} para prorrogar")
        codigo_estado = await self._codigo_de_estado(origen.estado_id)
        if codigo_estado not in (ESTADO_APROBADO, ESTADO_EN_EJECUCION, ESTADO_CERRADO):
            raise ValueError("Solo se puede prorrogar un presupuesto que llegó a aprobarse")
        return await self.clonar_planificacion(
            ejercicio_origen, ejercicio_nuevo, es_prorroga=True
        )

    async def comparativa_interanual(self, ejercicio: int) -> List[dict]:
        """Compara las partidas de un ejercicio con las del anterior, emparejadas por
        categoría + nombre. Devuelve filas con importe de ambos años y variación."""
        actual = await self.obtener_planificacion_por_ejercicio(ejercicio)
        anterior = await self.obtener_planificacion_por_ejercicio(ejercicio - 1)
        if not actual:
            return []

        partidas_act = await self.listar_partidas(actual.id)
        partidas_ant = await self.listar_partidas(anterior.id) if anterior else []

        def clave(p):
            return (p.tipo, (p.nombre or "").strip().lower())
        mapa_ant = {clave(p): p for p in partidas_ant}

        filas = []
        for p in partidas_act:
            ant = mapa_ant.get(clave(p))
            imp_act = float(p.importe_presupuestado or 0)
            imp_ant = float(ant.importe_presupuestado or 0) if ant else 0.0
            variacion = imp_act - imp_ant
            pct = (variacion / imp_ant * 100) if imp_ant else None
            filas.append({
                "codigo": p.codigo, "nombre": p.nombre, "tipo": p.tipo,
                "importe_actual": imp_act, "importe_anterior": imp_ant,
                "variacion": variacion,
                "variacion_porcentaje": round(pct, 1) if pct is not None else None,
            })
        return filas

    async def liquidacion_presupuestaria(self, ejercicio: int) -> dict:
        """Liquidación del presupuesto de un ejercicio (previsto vs ejecutado), lista para
        incorporar a la Memoria de cuentas anuales. Resumen global y por categoría."""
        plan = await self.obtener_planificacion_por_ejercicio(ejercicio)
        if not plan:
            return {"ejercicio": ejercicio, "existe": False}

        partidas = await self.listar_partidas(plan.id)
        ingresos_prev = sum((p.importe_presupuestado for p in partidas if p.tipo == "INGRESO"), Decimal("0"))
        ingresos_ejec = sum((p.importe_ejecutado for p in partidas if p.tipo == "INGRESO"), Decimal("0"))
        gastos_prev = sum((p.importe_presupuestado for p in partidas if p.tipo == "GASTO"), Decimal("0"))
        gastos_ejec = sum((p.importe_ejecutado for p in partidas if p.tipo == "GASTO"), Decimal("0"))

        return {
            "ejercicio": ejercicio,
            "existe": True,
            "ingresos_previstos": float(ingresos_prev),
            "ingresos_ejecutados": float(ingresos_ejec),
            "gastos_previstos": float(gastos_prev),
            "gastos_ejecutados": float(gastos_ejec),
            "resultado_previsto": float(ingresos_prev - gastos_prev),
            "resultado_ejecutado": float(ingresos_ejec - gastos_ejec),
            "grado_ejecucion_gastos": round(float(gastos_ejec / gastos_prev * 100), 1) if gastos_prev else 0.0,
        }

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
            # Congelar el presupuesto inicial: el vigente de cada partida se copia al inicial.
            # A partir de aquí, los cambios solo vía modificaciones presupuestarias.
            partidas = await self.listar_partidas(planificacion_id)
            for p in partidas:
                p.importe_inicial = p.importe_presupuestado
                self.session.add(p)
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
        Tras imputar, dispara el aviso de desviación si la partida queda desviada
        (control blando: avisa, no bloquea).
        """
        partida = await self._ajustar_ejecucion(importe, actividad_id, campania_id)
        if partida is not None:
            await self.avisar_desviacion(partida)
        return partida

    async def revertir_ejecucion(
        self,
        importe: Decimal,
        actividad_id: Optional[UUID] = None,
        campania_id: Optional[UUID] = None,
    ) -> Optional[PartidaPresupuestaria]:
        """Resta un importe previamente imputado (al reasignar o anular un apunte)."""
        return await self._ajustar_ejecucion(-importe, actividad_id, campania_id)

    async def _ajustar_ejecucion(
        self,
        delta: Decimal,
        actividad_id: Optional[UUID] = None,
        campania_id: Optional[UUID] = None,
    ) -> Optional[PartidaPresupuestaria]:
        """Suma `delta` (positivo o negativo) a la ejecución de la partida afecta.

        Regla de afectación (única, compartida por imputar y revertir): si hay
        actividad_id, manda la actividad; si no, la campaña.
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

        nuevo = (partida.importe_ejecutado or Decimal("0.00")) + delta
        # La ejecución no baja de cero (defensa ante descuadres)
        partida.importe_ejecutado = nuevo if nuevo > 0 else Decimal("0.00")
        self.session.add(partida)
        await self.session.commit()
        await self.session.refresh(partida)
        return partida

    # ── Modificaciones presupuestarias (Fase 2) ─────────────────────────────

    async def _obtener_partida(self, partida_id: UUID) -> Optional[PartidaPresupuestaria]:
        result = await self.session.execute(
            select(PartidaPresupuestaria).where(PartidaPresupuestaria.id == partida_id)
        )
        return result.scalars().first()

    async def listar_modificaciones(self, planificacion_id: UUID) -> List[ModificacionPresupuestaria]:
        result = await self.session.execute(
            select(ModificacionPresupuestaria)
            .where(
                and_(
                    ModificacionPresupuestaria.planificacion_id == planificacion_id,
                    ModificacionPresupuestaria.eliminado == False,
                )
            )
            .order_by(ModificacionPresupuestaria.fecha.desc())
        )
        return list(result.scalars().all())

    async def registrar_modificacion(
        self,
        planificacion_id: UUID,
        tipo: TipoModificacionPresupuestaria,
        partida_destino_id: UUID,
        importe: Decimal,
        motivo: str,
        partida_origen_id: Optional[UUID] = None,
        registrada_por_id: Optional[UUID] = None,
    ) -> ModificacionPresupuestaria:
        """Registra una modificación y ajusta el importe vigente de las partidas.

        - TRANSFERENCIA: resta de origen, suma a destino (requiere partida_origen_id).
          El presupuesto global no cambia (suma cero).
        - AMPLIACION / SUPLEMENTO: suma a destino. El presupuesto global crece.

        Solo sobre presupuestos APROBADO o EN_EJECUCION (el borrador se edita directo).
        """
        if importe is None or importe <= Decimal("0"):
            raise ValueError("El importe de la modificación debe ser positivo")
        if not motivo or not motivo.strip():
            raise ValueError("La modificación requiere un motivo")

        plan = await self.obtener_planificacion(planificacion_id)
        if not plan:
            raise ValueError(f"Planificación {planificacion_id} no encontrada")
        codigo_estado = await self._codigo_de_estado(plan.estado_id)
        if codigo_estado not in (ESTADO_APROBADO, ESTADO_EN_EJECUCION):
            raise ValueError(
                "Las modificaciones presupuestarias solo aplican a presupuestos aprobados "
                "o en ejecución. En borrador, edita las partidas directamente."
            )

        destino = await self._obtener_partida(partida_destino_id)
        if not destino:
            raise ValueError("Partida de destino no encontrada")

        origen = None
        if tipo == TipoModificacionPresupuestaria.TRANSFERENCIA:
            if not partida_origen_id:
                raise ValueError("Una transferencia requiere partida de origen")
            origen = await self._obtener_partida(partida_origen_id)
            if not origen:
                raise ValueError("Partida de origen no encontrada")
            if origen.id == destino.id:
                raise ValueError("Origen y destino no pueden ser la misma partida")
            if importe > origen.saldo_disponible_ejecucion:
                raise ValueError(
                    "La transferencia supera el disponible de la partida de origen "
                    f"({float(origen.saldo_disponible_ejecucion):.2f} €)"
                )
            origen.importe_presupuestado -= importe
            self.session.add(origen)

        destino.importe_presupuestado += importe
        self.session.add(destino)

        modificacion = ModificacionPresupuestaria(
            planificacion_id=planificacion_id,
            tipo=tipo,
            partida_destino_id=partida_destino_id,
            partida_origen_id=partida_origen_id if origen else None,
            importe=importe,
            motivo=motivo.strip(),
            registrada_por_id=registrada_por_id,
        )
        self.session.add(modificacion)
        await self.session.commit()
        await self.session.refresh(modificacion)
        await self._recalcular_total(planificacion_id)
        return modificacion

    # ── Alertas (Fase 2) ─────────────────────────────────────────────────────

    async def alertas(self, planificacion_id: UUID) -> List[dict]:
        """Devuelve las partidas con alerta: sobreejecutadas o agotadas."""
        partidas = await self.listar_partidas(planificacion_id)
        salida = []
        for p in partidas:
            if p.esta_sobreejecutada:
                salida.append({
                    "partida_id": str(p.id), "codigo": p.codigo, "nombre": p.nombre,
                    "tipo_alerta": "SOBREEJECUTADA",
                    "mensaje": f"Ejecutado {float(p.importe_ejecutado):.2f} € sobre "
                               f"{float(p.importe_presupuestado):.2f} € presupuestados",
                })
            elif p.esta_agotada:
                salida.append({
                    "partida_id": str(p.id), "codigo": p.codigo, "nombre": p.nombre,
                    "tipo_alerta": "AGOTADA",
                    "mensaje": "Presupuesto vigente totalmente consumido",
                })
        return salida

    # ── Aviso de desviación presupuestaria (Fase 2 — enganche preparado) ──────
    #
    # PENDIENTE DE CONEXIÓN: requiere el sistema de notificaciones del frontend
    # (rama feature/notificaciones), aún no construido. Este método ya resuelve
    # QUÉ avisar y A QUIÉN (usuarios con permiso ECO_PRESUPUESTO_APROBAR), pero el
    # envío real está desactivado tras el flag `_NOTIFICACIONES_ACTIVAS`. Cuando el
    # sistema de notificaciones exista, basta con poner el flag a True (y crear el
    # tipo de notificación 'PRESUPUESTO_DESVIACION' en su seed). No hay que tocar la
    # lógica de detección ni el punto de llamada en tesorería.

    _NOTIFICACIONES_ACTIVAS = False  # se activará con la rama feature/notificaciones

    async def _usuarios_control_presupuestario(self) -> List[UUID]:
        """Resuelve los usuarios con permiso de control presupuestario
        (ECO_PRESUPUESTO_APROBAR), destinatarios del aviso de desviación."""
        from app.modules.acceso.models.usuario import Usuario, UsuarioRol
        from app.modules.acceso.models.rol_transaccion import RolTransaccion
        from app.modules.acceso.models.transaccion import Transaccion

        result = await self.session.execute(
            select(UsuarioRol.usuario_id)
            .join(RolTransaccion, RolTransaccion.rol_id == UsuarioRol.rol_id)
            .join(Transaccion, Transaccion.id == RolTransaccion.transaccion_id)
            .where(Transaccion.codigo == "ECO_PRESUPUESTO_APROBAR")
            .distinct()
        )
        return [row[0] for row in result.all()]

    async def avisar_desviacion(self, partida: PartidaPresupuestaria) -> None:
        """Avisa a los responsables de control presupuestario de una desviación.

        Control BLANDO: nunca bloquea nada; solo notifica para que el responsable
        decida si tramita una modificación presupuestaria. Hoy preparado y desactivado.
        """
        if not partida or not (partida.esta_sobreejecutada or partida.esta_agotada):
            return

        titulo = "Desviación presupuestaria"
        estado = "sobreejecutada" if partida.esta_sobreejecutada else "agotada"
        mensaje = (
            f"La partida «{partida.nombre}» ({partida.codigo}) está {estado}: "
            f"ejecutado {float(partida.importe_ejecutado):.2f} € sobre "
            f"{float(partida.importe_presupuestado):.2f} € vigentes. "
            f"Valora si procede una modificación presupuestaria."
        )

        if not self._NOTIFICACIONES_ACTIVAS:
            # Enganche preparado: cuando exista el sistema de notificaciones, activar.
            return

        # — Código listo para cuando _NOTIFICACIONES_ACTIVAS = True —
        from app.infrastructure.services.notificacion_service import NotificacionService
        destinatarios = await self._usuarios_control_presupuestario()
        if not destinatarios:
            return
        notif = NotificacionService(self.session)
        for usuario_id in destinatarios:
            try:
                await notif.crear_notificacion(
                    tipo_codigo="PRESUPUESTO_DESVIACION",
                    usuario_id=usuario_id,
                    titulo=titulo,
                    mensaje=mensaje,
                    canal="INAPP",
                    entidad_tipo="partida_presupuestaria",
                    entidad_id=str(partida.id),
                )
            except Exception:
                pass  # un fallo de aviso nunca afecta al registro del gasto

    # ── Control de disponibilidad (Fase 2) ───────────────────────────────────

    async def comprobar_disponibilidad(
        self, importe: Decimal, actividad_id: Optional[UUID] = None,
        campania_id: Optional[UUID] = None,
    ) -> dict:
        """Comprueba si un gasto cabe en el disponible de su partida afecta.

        Devuelve {ok, bloquea, disponible, mensaje}. `bloquea` es True solo si la
        planificación tiene control_disponibilidad activo y el gasto excede el disponible.
        Si no hay partida afecta, ok=True (no aplica).
        """
        if not actividad_id and not campania_id:
            return {"ok": True, "bloquea": False, "disponible": None, "mensaje": None}

        query = select(PartidaPresupuestaria).where(PartidaPresupuestaria.eliminado == False)
        query = query.where(
            PartidaPresupuestaria.actividad_id == actividad_id if actividad_id
            else PartidaPresupuestaria.campania_id == campania_id
        )
        partida = (await self.session.execute(query)).scalars().first()
        if not partida:
            return {"ok": True, "bloquea": False, "disponible": None, "mensaje": None}

        disponible = partida.saldo_disponible_ejecucion
        if importe <= disponible:
            return {"ok": True, "bloquea": False, "disponible": float(disponible), "mensaje": None}

        plan = await self.obtener_planificacion(partida.planificacion_id) if partida.planificacion_id else None
        bloquea = bool(plan and plan.control_disponibilidad)
        mensaje = (
            f"El gasto ({float(importe):.2f} €) supera el disponible de la partida "
            f"'{partida.nombre}' ({float(disponible):.2f} €)."
        )
        return {"ok": False, "bloquea": bloquea, "disponible": float(disponible), "mensaje": mensaje}

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
