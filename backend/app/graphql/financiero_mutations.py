"""Mutations GraphQL financieras con lógica de negocio compleja.

Complementan las mutations CRUD automáticas de strawchemy con operaciones
que requieren lógica de servicio: confirmar asientos, conciliar apuntes,
generar balances, registrar apuntes con lógica contable automática.
"""
import strawberry
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from ..modules.economico.services.tesoreria_service import TesoreriaService
from ..modules.economico.services.contabilidad_service import ContabilidadService
from ..modules.economico.services.registro_contable import RegistroContable
from ..modules.economico.models.tesoreria import TipoApunte, OrigenApunte, MetodoConciliacion
from ..modules.economico.models.contabilidad import TipoAsientoContable


@strawberry.type
class FinancieroMutation:
    """Mutations financieras con lógica de negocio (no solo CRUD)."""

    # ─── Tesorería ────────────────────────────────────────────────────────────

    @strawberry.mutation
    async def registrar_apunte_caja(
        self,
        info: strawberry.Info,
        cuenta_id: UUID,
        fecha: date,
        importe: float,
        tipo: str,
        concepto: str,
        origen: Optional[str] = None,
        entidad_origen_tipo: Optional[str] = None,
        entidad_origen_id: Optional[UUID] = None,
        referencia_externa: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> str:
        """Registra un apunte de caja y, si está en versión COMPLETA, genera el asiento contable."""
        session = info.context.session
        service = TesoreriaService(session)

        tipo_apunte = TipoApunte(tipo)
        origen_apunte = OrigenApunte(origen) if origen else None

        apunte = await service.registrar_apunte(
            cuenta_id=cuenta_id,
            fecha=fecha,
            importe=Decimal(str(importe)),
            tipo=tipo_apunte,
            concepto=concepto,
            origen=origen_apunte,
            entidad_origen_tipo=entidad_origen_tipo,
            entidad_origen_id=entidad_origen_id,
            referencia_externa=referencia_externa,
            observaciones=observaciones,
        )

        registro = RegistroContable(session)
        await registro.generar_asiento_para_apunte(apunte)

        return str(apunte.id)

    @strawberry.mutation
    async def marcar_apunte_conciliado(
        self,
        info: strawberry.Info,
        apunte_id: UUID,
        fecha_conciliacion: Optional[date] = None,
    ) -> bool:
        session = info.context.session
        service = TesoreriaService(session)
        await service.marcar_apunte_conciliado(apunte_id, fecha_conciliacion)
        return True

    @strawberry.mutation
    async def conciliar_apunte_con_extracto(
        self,
        info: strawberry.Info,
        apunte_id: UUID,
        extracto_id: UUID,
        metodo: str = "MANUAL",
    ) -> str:
        session = info.context.session
        service = TesoreriaService(session)
        usuario_id = getattr(info.context.user, 'id', None)
        conciliacion = await service.conciliar_apunte_con_extracto(
            apunte_id=apunte_id,
            extracto_id=extracto_id,
            metodo=MetodoConciliacion(metodo),
            usuario_id=usuario_id,
        )
        return str(conciliacion.id)

    @strawberry.mutation
    async def confirmar_conciliacion_periodo(
        self, info: strawberry.Info, conciliacion_id: UUID
    ) -> bool:
        session = info.context.session
        service = TesoreriaService(session)
        await service.confirmar_conciliacion_periodo(conciliacion_id)
        return True

    # ─── Contabilidad ─────────────────────────────────────────────────────────

    @strawberry.mutation
    async def confirmar_asiento_contable(
        self, info: strawberry.Info, asiento_id: UUID
    ) -> bool:
        """Confirma un asiento BORRADOR. Falla si debe ≠ haber."""
        session = info.context.session
        service = ContabilidadService(session)
        await service.confirmar_asiento(asiento_id)
        return True

    @strawberry.mutation
    async def anular_asiento_contable(
        self, info: strawberry.Info, asiento_id: UUID
    ) -> bool:
        session = info.context.session
        service = ContabilidadService(session)
        await service.anular_asiento(asiento_id)
        return True

    @strawberry.mutation
    async def generar_balance_contable(
        self,
        info: strawberry.Info,
        ejercicio: int,
        fecha_fin: Optional[date] = None,
    ) -> str:
        """Genera y persiste un balance de sumas y saldos. Devuelve el ID del balance."""
        session = info.context.session
        service = ContabilidadService(session)
        balance = await service.generar_balance(ejercicio, fecha_fin)
        return str(balance.id)

    # ─── Liquidación automática ────────────────────────────────────────────────

    @strawberry.mutation
    async def liquidar_remesa(
        self,
        info: strawberry.Info,
        remesa_id: UUID,
        cuenta_bancaria_id: UUID,
        fecha_cobro: Optional[date] = None,
    ) -> str:
        """Liquida una remesa SEPA: marca órdenes como Procesadas, actualiza cuotas
        a Cobradas y genera ApunteCaja (+ asiento contable si modo COMPLETA).
        Devuelve el ID del ApunteCaja generado."""
        session = info.context.session
        service = TesoreriaService(session)
        apunte = await service.liquidar_remesa(remesa_id, cuenta_bancaria_id, fecha_cobro)
        return str(apunte.id)

    @strawberry.mutation
    async def registrar_pago_cuota_manual(
        self,
        info: strawberry.Info,
        cuota_id: UUID,
        cuenta_bancaria_id: UUID,
        importe: float,
        modo_ingreso: str,
        fecha_pago: Optional[date] = None,
        referencia: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> str:
        """Registra un pago manual de cuota, actualiza su estado y genera
        ApunteCaja (+ asiento contable si modo COMPLETA).
        Devuelve el ID del ApunteCaja generado."""
        session = info.context.session
        service = TesoreriaService(session)
        apunte = await service.registrar_pago_cuota_manual(
            cuota_id=cuota_id,
            cuenta_bancaria_id=cuenta_bancaria_id,
            importe=Decimal(str(importe)),
            modo_ingreso=modo_ingreso,
            fecha_pago=fecha_pago,
            referencia=referencia,
            observaciones=observaciones,
        )
        return str(apunte.id)
