"""Servicio de tesorería para gestión de cuentas bancarias y movimientos."""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.tesoreria import (
    CuentaBancaria,
    MovimientoTesoreria,
    ConciliacionBancaria,
    TipoMovimientoTesoreria,
)


class TesoreriaService:
    """Servicio para gestionar tesorería: cuentas bancarias y movimientos."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def crear_cuenta_bancaria(
        self,
        nombre: str,
        iban: str,
        banco_nombre: str,
        bic_swift: Optional[str] = None,
        agrupacion_id: Optional[UUID] = None,
        observaciones: Optional[str] = None,
    ) -> CuentaBancaria:
        """Crea una nueva cuenta bancaria."""
        cuenta = CuentaBancaria(
            nombre=nombre,
            iban=iban,
            bic_swift=bic_swift,
            banco_nombre=banco_nombre,
            agrupacion_id=agrupacion_id,
            observaciones=observaciones,
        )
        self.session.add(cuenta)
        await self.session.commit()
        await self.session.refresh(cuenta)
        return cuenta

    async def obtener_cuenta_bancaria(self, cuenta_id: UUID) -> Optional[CuentaBancaria]:
        """Obtiene una cuenta bancaria por ID."""
        result = await self.session.execute(
            select(CuentaBancaria).where(CuentaBancaria.id == cuenta_id)
        )
        return result.scalars().first()

    async def listar_cuentas_bancarias(
        self, activas_solo: bool = True
    ) -> List[CuentaBancaria]:
        """Lista todas las cuentas bancarias."""
        query = select(CuentaBancaria)
        if activas_solo:
            query = query.where(CuentaBancaria.activa == True)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def registrar_movimiento(
        self,
        cuenta_id: UUID,
        fecha: date,
        importe: Decimal,
        tipo: TipoMovimientoTesoreria,
        concepto: str,
        referencia_externa: Optional[str] = None,
        entidad_origen_tipo: Optional[str] = None,
        entidad_origen_id: Optional[UUID] = None,
        observaciones: Optional[str] = None,
    ) -> MovimientoTesoreria:
        """Registra un movimiento de tesorería."""
        # Obtener la cuenta
        cuenta = await self.obtener_cuenta_bancaria(cuenta_id)
        if not cuenta:
            raise ValueError(f"Cuenta bancaria {cuenta_id} no encontrada")

        # Crear el movimiento
        movimiento = MovimientoTesoreria(
            cuenta_id=cuenta_id,
            fecha=fecha,
            importe=importe,
            tipo=tipo,
            concepto=concepto,
            referencia_externa=referencia_externa,
            entidad_origen_tipo=entidad_origen_tipo,
            entidad_origen_id=entidad_origen_id,
            observaciones=observaciones,
        )

        # Actualizar saldo de la cuenta
        if tipo == TipoMovimientoTesoreria.INGRESO:
            cuenta.saldo_actual += importe
        elif tipo == TipoMovimientoTesoreria.GASTO:
            cuenta.saldo_actual -= importe
        elif tipo == TipoMovimientoTesoreria.TRASPASO:
            # Los traspasos se registran en dos movimientos (uno negativo, uno positivo)
            pass

        self.session.add(movimiento)
        self.session.add(cuenta)
        await self.session.commit()
        await self.session.refresh(movimiento)
        return movimiento

    async def obtener_movimientos_por_cuenta(
        self,
        cuenta_id: UUID,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
    ) -> List[MovimientoTesoreria]:
        """Obtiene los movimientos de una cuenta en un período."""
        query = select(MovimientoTesoreria).where(
            MovimientoTesoreria.cuenta_id == cuenta_id
        )

        if fecha_inicio:
            query = query.where(MovimientoTesoreria.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.where(MovimientoTesoreria.fecha <= fecha_fin)

        query = query.order_by(MovimientoTesoreria.fecha)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def obtener_movimientos_no_conciliados(
        self, cuenta_id: UUID
    ) -> List[MovimientoTesoreria]:
        """Obtiene los movimientos no conciliados de una cuenta."""
        result = await self.session.execute(
            select(MovimientoTesoreria).where(
                and_(
                    MovimientoTesoreria.cuenta_id == cuenta_id,
                    MovimientoTesoreria.conciliado == False,
                )
            )
        )
        return result.scalars().all()

    async def marcar_movimiento_conciliado(
        self, movimiento_id: UUID, fecha_conciliacion: Optional[date] = None
    ) -> MovimientoTesoreria:
        """Marca un movimiento como conciliado."""
        movimiento = await self.session.execute(
            select(MovimientoTesoreria).where(MovimientoTesoreria.id == movimiento_id)
        )
        movimiento = movimiento.scalars().first()

        if not movimiento:
            raise ValueError(f"Movimiento {movimiento_id} no encontrado")

        movimiento.conciliado = True
        movimiento.fecha_conciliacion = fecha_conciliacion or date.today()

        self.session.add(movimiento)
        await self.session.commit()
        await self.session.refresh(movimiento)
        return movimiento

    async def crear_conciliacion_bancaria(
        self,
        cuenta_id: UUID,
        fecha_inicio: date,
        fecha_fin: date,
        saldo_inicial_extracto: Decimal,
        saldo_final_extracto: Decimal,
    ) -> ConciliacionBancaria:
        """Crea un registro de conciliación bancaria."""
        # Obtener la cuenta
        cuenta = await self.obtener_cuenta_bancaria(cuenta_id)
        if not cuenta:
            raise ValueError(f"Cuenta bancaria {cuenta_id} no encontrada")

        # Obtener movimientos del período
        movimientos = await self.obtener_movimientos_por_cuenta(
            cuenta_id, fecha_inicio, fecha_fin
        )

        # Calcular saldos del sistema
        saldo_inicial_sistema = cuenta.saldo_actual
        for mov in movimientos:
            if mov.tipo == TipoMovimientoTesoreria.INGRESO:
                saldo_inicial_sistema -= mov.importe
            elif mov.tipo == TipoMovimientoTesoreria.GASTO:
                saldo_inicial_sistema += mov.importe

        saldo_final_sistema = cuenta.saldo_actual

        # Calcular diferencia
        diferencia = saldo_final_extracto - saldo_final_sistema

        # Crear conciliación
        conciliacion = ConciliacionBancaria(
            cuenta_id=cuenta_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            saldo_inicial_extracto=saldo_inicial_extracto,
            saldo_final_extracto=saldo_final_extracto,
            saldo_inicial_sistema=saldo_inicial_sistema,
            saldo_final_sistema=saldo_final_sistema,
            diferencia=diferencia,
        )

        self.session.add(conciliacion)
        await self.session.commit()
        await self.session.refresh(conciliacion)
        return conciliacion

    async def confirmar_conciliacion(
        self, conciliacion_id: UUID
    ) -> ConciliacionBancaria:
        """Confirma una conciliación bancaria."""
        result = await self.session.execute(
            select(ConciliacionBancaria).where(ConciliacionBancaria.id == conciliacion_id)
        )
        conciliacion = result.scalars().first()

        if not conciliacion:
            raise ValueError(f"Conciliación {conciliacion_id} no encontrada")

        if not conciliacion.esta_equilibrada:
            raise ValueError(
                f"La conciliación no está equilibrada. Diferencia: {conciliacion.diferencia}"
            )

        conciliacion.conciliado = True
        conciliacion.fecha_conciliacion = date.today()

        # Marcar todos los movimientos del período como conciliados
        movimientos = await self.obtener_movimientos_por_cuenta(
            conciliacion.cuenta_id,
            conciliacion.fecha_inicio,
            conciliacion.fecha_fin,
        )

        for mov in movimientos:
            if not mov.conciliado:
                mov.conciliado = True
                mov.fecha_conciliacion = date.today()
                self.session.add(mov)

        self.session.add(conciliacion)
        await self.session.commit()
        await self.session.refresh(conciliacion)
        return conciliacion

    async def obtener_saldo_cuenta(self, cuenta_id: UUID) -> Decimal:
        """Obtiene el saldo actual de una cuenta."""
        cuenta = await self.obtener_cuenta_bancaria(cuenta_id)
        if not cuenta:
            raise ValueError(f"Cuenta bancaria {cuenta_id} no encontrada")
        return cuenta.saldo_actual
