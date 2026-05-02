"""Servicio de tesorería."""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.tesoreria.cuenta_bancaria import CuentaBancaria
from ..models.tesoreria.apunte import ApunteCaja, TipoApunte, OrigenApunte
from ..models.tesoreria.conciliacion import ExtractoBancario, Conciliacion, MetodoConciliacion
from ..models.tesoreria.conciliacion_bancaria import ConciliacionBancaria


class TesoreriaService:

    def __init__(self, session: AsyncSession):
        self.session = session

    # -------------------------------------------------------------------------
    # Cuentas bancarias
    # -------------------------------------------------------------------------

    async def crear_cuenta_bancaria(
        self,
        nombre: str,
        iban: str,
        banco_nombre: Optional[str] = None,
        bic_swift: Optional[str] = None,
        titular: Optional[str] = None,
        agrupacion_id: Optional[UUID] = None,
        descripcion: Optional[str] = None,
    ) -> CuentaBancaria:
        cuenta = CuentaBancaria(
            nombre=nombre,
            iban=iban,
            banco=banco_nombre,
            bic_swift=bic_swift,
            titular=titular,
            descripcion=descripcion,
        )
        self.session.add(cuenta)
        await self.session.commit()
        await self.session.refresh(cuenta)
        return cuenta

    async def obtener_cuenta_bancaria(self, cuenta_id: UUID) -> Optional[CuentaBancaria]:
        result = await self.session.execute(
            select(CuentaBancaria).where(CuentaBancaria.id == cuenta_id)
        )
        return result.scalars().first()

    async def listar_cuentas_bancarias(
        self, activas_solo: bool = True, limit: int = 50, offset: int = 0
    ) -> List[CuentaBancaria]:
        query = select(CuentaBancaria)
        if activas_solo:
            query = query.where(CuentaBancaria.activo == True)
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # -------------------------------------------------------------------------
    # Apuntes de caja (movimientos)
    # -------------------------------------------------------------------------

    async def registrar_movimiento(
        self,
        cuenta_id: UUID,
        fecha: date,
        importe: Decimal,
        tipo: TipoApunte,
        concepto: str,
        estado_id: UUID,
        referencia_externa: Optional[str] = None,
        entidad_origen_tipo: Optional[OrigenApunte] = None,
        entidad_origen_id: Optional[UUID] = None,
        asiento_id: Optional[UUID] = None,
        observaciones: Optional[str] = None,
    ) -> ApunteCaja:
        cuenta = await self.obtener_cuenta_bancaria(cuenta_id)
        if not cuenta:
            raise ValueError(f"Cuenta bancaria {cuenta_id} no encontrada")

        apunte = ApunteCaja(
            cuenta_bancaria_id=cuenta_id,
            tipo=tipo,
            importe=importe,
            fecha=fecha,
            concepto=concepto,
            estado_id=estado_id,
            origen=entidad_origen_tipo,
            origen_id=entidad_origen_id,
            asiento_id=asiento_id,
            observaciones=observaciones,
        )

        if tipo == TipoApunte.INGRESO:
            cuenta.saldo_actual += importe
        elif tipo == TipoApunte.GASTO:
            cuenta.saldo_actual -= importe

        self.session.add(apunte)
        self.session.add(cuenta)
        await self.session.commit()
        await self.session.refresh(apunte)
        return apunte

    async def obtener_movimientos_por_cuenta(
        self,
        cuenta_id: UUID,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ApunteCaja]:
        query = select(ApunteCaja).where(ApunteCaja.cuenta_bancaria_id == cuenta_id)
        if fecha_inicio:
            query = query.where(ApunteCaja.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.where(ApunteCaja.fecha <= fecha_fin)
        query = query.order_by(ApunteCaja.fecha.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def obtener_movimientos_no_conciliados(
        self, cuenta_id: UUID
    ) -> List[ApunteCaja]:
        conciliados = await self.session.execute(select(Conciliacion.apunte_id))
        ids_conciliados = set(conciliados.scalars().all())
        result = await self.session.execute(
            select(ApunteCaja).where(
                and_(
                    ApunteCaja.cuenta_bancaria_id == cuenta_id,
                    ApunteCaja.id.not_in(ids_conciliados),
                )
            )
        )
        return list(result.scalars().all())

    async def marcar_movimiento_conciliado(
        self,
        apunte_id: UUID,
        extracto_id: UUID,
        usuario_id: Optional[UUID] = None,
    ) -> Conciliacion:
        conciliacion = Conciliacion(
            apunte_id=apunte_id,
            extracto_id=extracto_id,
            metodo=MetodoConciliacion.MANUAL if usuario_id else MetodoConciliacion.AUTOMATICO,
            usuario_id=usuario_id,
        )
        result = await self.session.execute(
            select(ExtractoBancario).where(ExtractoBancario.id == extracto_id)
        )
        extracto = result.scalars().first()
        if extracto:
            extracto.conciliado = True
            self.session.add(extracto)
        self.session.add(conciliacion)
        await self.session.commit()
        await self.session.refresh(conciliacion)
        return conciliacion

    async def importar_extracto(
        self, cuenta_id: UUID, lineas: List[dict]
    ) -> List[ExtractoBancario]:
        """Importa líneas de extracto bancario (CSV/MT940).

        Cada elemento de lineas: {fecha, importe, concepto, referencia}
        """
        cuenta = await self.obtener_cuenta_bancaria(cuenta_id)
        if not cuenta:
            raise ValueError(f"Cuenta bancaria {cuenta_id} no encontrada")
        extractos = []
        for linea in lineas:
            extracto = ExtractoBancario(
                cuenta_bancaria_id=cuenta_id,
                fecha=linea["fecha"],
                importe=linea["importe"],
                concepto=linea.get("concepto"),
                referencia=linea.get("referencia"),
            )
            self.session.add(extracto)
            extractos.append(extracto)
        await self.session.commit()
        return extractos

    # -------------------------------------------------------------------------
    # Conciliación bancaria por período
    # -------------------------------------------------------------------------

    async def crear_conciliacion_bancaria(
        self,
        cuenta_id: UUID,
        fecha_inicio: date,
        fecha_fin: date,
        saldo_inicial_extracto: Decimal,
        saldo_final_extracto: Decimal,
    ) -> ConciliacionBancaria:
        cuenta = await self.obtener_cuenta_bancaria(cuenta_id)
        if not cuenta:
            raise ValueError(f"Cuenta bancaria {cuenta_id} no encontrada")

        movimientos = await self.obtener_movimientos_por_cuenta(
            cuenta_id, fecha_inicio, fecha_fin, limit=10000
        )

        # Calcular saldo sistema en el período
        saldo_inicial_sistema = cuenta.saldo_actual
        for mov in movimientos:
            if mov.tipo == TipoApunte.INGRESO:
                saldo_inicial_sistema -= mov.importe
            elif mov.tipo == TipoApunte.GASTO:
                saldo_inicial_sistema += mov.importe
        saldo_final_sistema = cuenta.saldo_actual

        diferencia = saldo_final_extracto - saldo_final_sistema

        conciliacion = ConciliacionBancaria(
            cuenta_bancaria_id=cuenta_id,
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
        self.session.add(conciliacion)
        await self.session.commit()
        await self.session.refresh(conciliacion)
        return conciliacion

    async def obtener_saldo_cuenta(self, cuenta_id: UUID) -> Decimal:
        cuenta = await self.obtener_cuenta_bancaria(cuenta_id)
        if not cuenta:
            raise ValueError(f"Cuenta bancaria {cuenta_id} no encontrada")
        return cuenta.saldo_actual
