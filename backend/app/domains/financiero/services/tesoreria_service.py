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


class TesoreriaService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def crear_cuenta_bancaria(
        self,
        nombre: str,
        iban: str,
        banco: Optional[str] = None,
        titular: Optional[str] = None,
        descripcion: Optional[str] = None,
    ) -> CuentaBancaria:
        cuenta = CuentaBancaria(
            nombre=nombre,
            iban=iban,
            banco=banco,
            titular=titular,
            descripcion=descripcion,
        )
        self.session.add(cuenta)
        await self.session.commit()
        await self.session.refresh(cuenta)
        return cuenta

    async def obtener_cuenta(self, cuenta_id: UUID) -> Optional[CuentaBancaria]:
        result = await self.session.execute(
            select(CuentaBancaria).where(CuentaBancaria.id == cuenta_id)
        )
        return result.scalars().first()

    async def listar_cuentas(self, activas_solo: bool = True) -> List[CuentaBancaria]:
        query = select(CuentaBancaria)
        if activas_solo:
            query = query.where(CuentaBancaria.activo == True)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def registrar_apunte(
        self,
        cuenta_id: UUID,
        tipo: TipoApunte,
        importe: Decimal,
        fecha: date,
        concepto: str,
        estado_id: UUID,
        origen: Optional[OrigenApunte] = None,
        origen_id: Optional[UUID] = None,
        asiento_id: Optional[UUID] = None,
        observaciones: Optional[str] = None,
    ) -> ApunteCaja:
        cuenta = await self.obtener_cuenta(cuenta_id)
        if not cuenta:
            raise ValueError(f"Cuenta bancaria {cuenta_id} no encontrada")

        apunte = ApunteCaja(
            cuenta_bancaria_id=cuenta_id,
            tipo=tipo,
            importe=importe,
            fecha=fecha,
            concepto=concepto,
            estado_id=estado_id,
            origen=origen,
            origen_id=origen_id,
            asiento_id=asiento_id,
            observaciones=observaciones,
        )

        # Actualizar saldo
        if tipo == TipoApunte.INGRESO:
            cuenta.saldo_actual += importe
        elif tipo == TipoApunte.GASTO:
            cuenta.saldo_actual -= importe
        # TRANSFERENCIA: se gestiona en dos apuntes separados (origen/destino)

        self.session.add(apunte)
        self.session.add(cuenta)
        await self.session.commit()
        await self.session.refresh(apunte)
        return apunte

    async def listar_apuntes(
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

    async def apuntes_no_conciliados(self, cuenta_id: UUID) -> List[ApunteCaja]:
        """Apuntes pendientes de conciliación en una cuenta."""
        # Obtener IDs ya conciliados
        conciliados = await self.session.execute(
            select(Conciliacion.apunte_id)
        )
        ids_conciliados = {r for r in conciliados.scalars().all()}

        result = await self.session.execute(
            select(ApunteCaja).where(
                and_(
                    ApunteCaja.cuenta_bancaria_id == cuenta_id,
                    ApunteCaja.id.not_in(ids_conciliados),
                )
            )
        )
        return list(result.scalars().all())

    async def importar_extracto(
        self,
        cuenta_id: UUID,
        lineas: List[dict],
    ) -> List[ExtractoBancario]:
        """Importa líneas de extracto bancario (CSV/MT940).

        Cada elemento de lineas: {fecha, importe, concepto, referencia}
        """
        cuenta = await self.obtener_cuenta(cuenta_id)
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

    async def conciliar(
        self,
        apunte_id: UUID,
        extracto_id: UUID,
        metodo_id: UUID,
        usuario_id: Optional[UUID] = None,
    ) -> Conciliacion:
        conciliacion = Conciliacion(
            apunte_id=apunte_id,
            extracto_id=extracto_id,
            metodo=MetodoConciliacion.MANUAL if usuario_id else MetodoConciliacion.AUTOMATICO,
            usuario_id=usuario_id,
        )

        # Marcar extracto como conciliado
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

    async def obtener_saldo(self, cuenta_id: UUID) -> Decimal:
        cuenta = await self.obtener_cuenta(cuenta_id)
        if not cuenta:
            raise ValueError(f"Cuenta bancaria {cuenta_id} no encontrada")
        return cuenta.saldo_actual
