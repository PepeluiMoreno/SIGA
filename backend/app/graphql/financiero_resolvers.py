"""Resolvers custom para operaciones de negocio de tesorería y contabilidad."""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

import strawberry
from sqlalchemy import select

from app.modules.economico.models.contabilidad import TipoCuentaContable, TipoAsientoContable
from app.modules.economico.models.cuotas import CuotaAnual
from app.modules.economico.models.tesoreria import TipoMovimientoTesoreria
from app.modules.economico.services.tesoreria_service import TesoreriaService
from app.modules.economico.services.contabilidad_service import ContabilidadService
from app.graphql.types_auto import CuotaAnualType


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------

@strawberry.input
class CrearCuentaBancariaInput:
    nombre: str
    iban: str
    banco_nombre: str
    bic_swift: Optional[str] = None
    agrupacion_id: Optional[uuid.UUID] = None
    observaciones: Optional[str] = None


@strawberry.input
class CrearMovimientoTesoreriaInput:
    cuenta_id: uuid.UUID
    fecha: date
    importe: float
    tipo: str
    concepto: str
    referencia_externa: Optional[str] = None
    entidad_origen_tipo: Optional[str] = None
    entidad_origen_id: Optional[uuid.UUID] = None
    observaciones: Optional[str] = None


@strawberry.input
class CrearConciliacionBancariaInput:
    cuenta_id: uuid.UUID
    fecha_inicio: date
    fecha_fin: date
    saldo_inicial_extracto: float
    saldo_final_extracto: float


@strawberry.input
class CrearCuentaContableInput:
    codigo: str
    nombre: str
    tipo: str
    nivel: int
    padre_id: Optional[uuid.UUID] = None
    es_dotacion: bool = False
    descripcion: Optional[str] = None


@strawberry.input
class CrearAsientoContableInput:
    ejercicio: int
    numero_asiento: int
    fecha: date
    glosa: str
    tipo_asiento: str = "GESTION"
    observaciones: Optional[str] = None


@strawberry.input
class CrearApunteContableInput:
    asiento_id: uuid.UUID
    cuenta_id: uuid.UUID
    debe: float = 0.0
    haber: float = 0.0
    concepto: str = ""
    actividad_id: Optional[uuid.UUID] = None
    observaciones: Optional[str] = None


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------

@strawberry.type
class FinancieroQuery:

    @strawberry.field
    async def cuenta_por_codigo(self, info: strawberry.Info, codigo: str) -> Optional[uuid.UUID]:
        """Devuelve el id de la cuenta contable por su código contable."""
        service = ContabilidadService(info.context.session)
        cuenta = await service.obtener_cuenta_por_codigo(codigo)
        return cuenta.id if cuenta else None

    @strawberry.field
    async def saldo_cuenta(
        self,
        info: strawberry.Info,
        cuenta_id: uuid.UUID,
        ejercicio: Optional[int] = None,
        fecha_fin: Optional[date] = None,
    ) -> float:
        """Calcula el saldo de una cuenta contable."""
        service = ContabilidadService(info.context.session)
        saldo = await service.calcular_saldo_cuenta(cuenta_id, fecha_fin=fecha_fin, ejercicio=ejercicio)
        return float(saldo)

    @strawberry.field
    async def cuotas_por_miembro(
        self,
        info: strawberry.Info,
        miembro_id: uuid.UUID,
    ) -> list[CuotaAnualType]:
        """Devuelve el historial de cuotas de un miembro ordenadas por ejercicio descendente."""
        session = info.context.session
        stmt = (
            select(CuotaAnual)
            .where(CuotaAnual.miembro_id == miembro_id)
            .order_by(CuotaAnual.ejercicio.desc())
        )
        result = await session.execute(stmt)
        return result.scalars().all()


# ---------------------------------------------------------------------------
# Mutation
# ---------------------------------------------------------------------------

@strawberry.type
class FinancieroMutation:

    # ── Tesorería ────────────────────────────────────────────────────────────

    @strawberry.mutation
    async def crear_cuenta_bancaria(self, info: strawberry.Info, data: CrearCuentaBancariaInput) -> uuid.UUID:
        service = TesoreriaService(info.context.session)
        cuenta = await service.crear_cuenta_bancaria(
            nombre=data.nombre,
            iban=data.iban,
            banco_nombre=data.banco_nombre,
            bic_swift=data.bic_swift,
            agrupacion_id=data.agrupacion_id,
            observaciones=data.observaciones,
        )
        return cuenta.id

    @strawberry.mutation
    async def crear_movimiento_tesoreria(self, info: strawberry.Info, data: CrearMovimientoTesoreriaInput) -> uuid.UUID:
        service = TesoreriaService(info.context.session)
        movimiento = await service.registrar_movimiento(
            cuenta_id=data.cuenta_id,
            fecha=data.fecha,
            importe=Decimal(str(data.importe)),
            tipo=TipoMovimientoTesoreria(data.tipo),
            concepto=data.concepto,
            referencia_externa=data.referencia_externa,
            entidad_origen_tipo=data.entidad_origen_tipo,
            entidad_origen_id=data.entidad_origen_id,
            observaciones=data.observaciones,
        )
        return movimiento.id

    @strawberry.mutation
    async def marcar_movimiento_conciliado(
        self, info: strawberry.Info, movimiento_id: uuid.UUID, fecha_conciliacion: Optional[date] = None
    ) -> bool:
        service = TesoreriaService(info.context.session)
        await service.marcar_movimiento_conciliado(movimiento_id, fecha_conciliacion)
        return True

    @strawberry.mutation
    async def crear_conciliacion_bancaria(self, info: strawberry.Info, data: CrearConciliacionBancariaInput) -> uuid.UUID:
        service = TesoreriaService(info.context.session)
        conciliacion = await service.crear_conciliacion_bancaria(
            cuenta_id=data.cuenta_id,
            fecha_inicio=data.fecha_inicio,
            fecha_fin=data.fecha_fin,
            saldo_inicial_extracto=Decimal(str(data.saldo_inicial_extracto)),
            saldo_final_extracto=Decimal(str(data.saldo_final_extracto)),
        )
        return conciliacion.id

    @strawberry.mutation
    async def confirmar_conciliacion(self, info: strawberry.Info, conciliacion_id: uuid.UUID) -> bool:
        service = TesoreriaService(info.context.session)
        await service.confirmar_conciliacion(conciliacion_id)
        return True

    # ── Contabilidad ─────────────────────────────────────────────────────────

    @strawberry.mutation
    async def crear_cuenta_contable(self, info: strawberry.Info, data: CrearCuentaContableInput) -> uuid.UUID:
        service = ContabilidadService(info.context.session)
        cuenta = await service.crear_cuenta_contable(
            codigo=data.codigo,
            nombre=data.nombre,
            tipo=TipoCuentaContable(data.tipo),
            nivel=data.nivel,
            padre_id=data.padre_id,
            es_dotacion=data.es_dotacion,
            descripcion=data.descripcion,
        )
        return cuenta.id

    @strawberry.mutation
    async def crear_asiento_contable(self, info: strawberry.Info, data: CrearAsientoContableInput) -> uuid.UUID:
        service = ContabilidadService(info.context.session)
        asiento = await service.crear_asiento(
            ejercicio=data.ejercicio,
            numero_asiento=data.numero_asiento,
            fecha=data.fecha,
            glosa=data.glosa,
            tipo_asiento=TipoAsientoContable(data.tipo_asiento),
            observaciones=data.observaciones,
        )
        return asiento.id

    @strawberry.mutation
    async def crear_apunte_contable(self, info: strawberry.Info, data: CrearApunteContableInput) -> uuid.UUID:
        service = ContabilidadService(info.context.session)
        apunte = await service.crear_apunte(
            asiento_id=data.asiento_id,
            cuenta_id=data.cuenta_id,
            debe=Decimal(str(data.debe)),
            haber=Decimal(str(data.haber)),
            concepto=data.concepto,
            actividad_id=data.actividad_id,
            observaciones=data.observaciones,
        )
        return apunte.id

    @strawberry.mutation
    async def confirmar_asiento(self, info: strawberry.Info, asiento_id: uuid.UUID) -> bool:
        service = ContabilidadService(info.context.session)
        await service.confirmar_asiento(asiento_id)
        return True

    @strawberry.mutation
    async def anular_asiento(self, info: strawberry.Info, asiento_id: uuid.UUID) -> bool:
        service = ContabilidadService(info.context.session)
        await service.anular_asiento(asiento_id)
        return True

    @strawberry.mutation
    async def generar_balance(self, info: strawberry.Info, ejercicio: int, fecha_fin: date) -> uuid.UUID:
        service = ContabilidadService(info.context.session)
        balance = await service.generar_balance(ejercicio=ejercicio, fecha_fin=fecha_fin)
        return balance.id
