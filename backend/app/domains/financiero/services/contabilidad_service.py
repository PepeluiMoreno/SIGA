"""Servicio de contabilidad para gestión de asientos y plan de cuentas."""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.contabilidad import (
    CuentaContable,
    AsientoContable,
    ApunteContable,
    BalanceContable,
    TipoCuentaContable,
    TipoAsientoContable,
    EstadoAsientoContable,
)


class ContabilidadService:
    """Servicio para gestionar contabilidad: plan de cuentas y asientos."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def crear_cuenta_contable(
        self,
        codigo: str,
        nombre: str,
        tipo: TipoCuentaContable,
        nivel: int,
        padre_id: Optional[UUID] = None,
        es_dotacion: bool = False,
        descripcion: Optional[str] = None,
    ) -> CuentaContable:
        """Crea una nueva cuenta contable."""
        # Validar que el código sea único
        result = await self.session.execute(
            select(CuentaContable).where(CuentaContable.codigo == codigo)
        )
        if result.scalars().first():
            raise ValueError(f"Ya existe una cuenta con código {codigo}")

        cuenta = CuentaContable(
            codigo=codigo,
            nombre=nombre,
            tipo=tipo,
            nivel=nivel,
            padre_id=padre_id,
            es_dotacion=es_dotacion,
            descripcion=descripcion,
            permite_asiento=(nivel == 3),  # Solo cuentas de nivel 3 permiten asientos
        )
        self.session.add(cuenta)
        await self.session.commit()
        await self.session.refresh(cuenta)
        return cuenta

    async def obtener_cuenta_contable(self, cuenta_id: UUID) -> Optional[CuentaContable]:
        """Obtiene una cuenta contable por ID."""
        result = await self.session.execute(
            select(CuentaContable).where(CuentaContable.id == cuenta_id)
        )
        return result.scalars().first()

    async def obtener_cuenta_por_codigo(self, codigo: str) -> Optional[CuentaContable]:
        """Obtiene una cuenta contable por código."""
        result = await self.session.execute(
            select(CuentaContable).where(CuentaContable.codigo == codigo)
        )
        return result.scalars().first()

    async def listar_cuentas_contables(
        self, tipo: Optional[TipoCuentaContable] = None, activas_solo: bool = True
    ) -> List[CuentaContable]:
        """Lista las cuentas contables."""
        query = select(CuentaContable)
        if tipo:
            query = query.where(CuentaContable.tipo == tipo)
        if activas_solo:
            query = query.where(CuentaContable.activa == True)
        query = query.order_by(CuentaContable.codigo)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def crear_asiento(
        self,
        ejercicio: int,
        numero_asiento: int,
        fecha: date,
        glosa: str,
        tipo_asiento: TipoAsientoContable = TipoAsientoContable.GESTION,
        observaciones: Optional[str] = None,
    ) -> AsientoContable:
        """Crea un nuevo asiento contable."""
        asiento = AsientoContable(
            ejercicio=ejercicio,
            numero_asiento=numero_asiento,
            fecha=fecha,
            glosa=glosa,
            tipo_asiento=tipo_asiento,
            estado=EstadoAsientoContable.BORRADOR,
            observaciones=observaciones,
        )
        self.session.add(asiento)
        await self.session.commit()
        await self.session.refresh(asiento)
        return asiento

    async def obtener_asiento(self, asiento_id: UUID) -> Optional[AsientoContable]:
        """Obtiene un asiento contable por ID."""
        result = await self.session.execute(
            select(AsientoContable).where(AsientoContable.id == asiento_id)
        )
        return result.scalars().first()

    async def crear_apunte(
        self,
        asiento_id: UUID,
        cuenta_id: UUID,
        debe: Decimal = Decimal("0.00"),
        haber: Decimal = Decimal("0.00"),
        concepto: str = "",
        actividad_id: Optional[UUID] = None,
        observaciones: Optional[str] = None,
    ) -> ApunteContable:
        """Crea un apunte contable dentro de un asiento."""
        # Validar que no sea debe y haber a la vez
        if debe > 0 and haber > 0:
            raise ValueError("Un apunte no puede tener debe y haber simultáneamente")

        if debe == 0 and haber == 0:
            raise ValueError("Un apunte debe tener debe o haber")

        # Validar que la cuenta existe y permite asientos
        cuenta = await self.obtener_cuenta_contable(cuenta_id)
        if not cuenta:
            raise ValueError(f"Cuenta contable {cuenta_id} no encontrada")

        if not cuenta.permite_asiento:
            raise ValueError(f"La cuenta {cuenta.codigo} no permite asientos")

        apunte = ApunteContable(
            asiento_id=asiento_id,
            cuenta_id=cuenta_id,
            debe=debe,
            haber=haber,
            concepto=concepto,
            actividad_id=actividad_id,
            observaciones=observaciones,
        )
        self.session.add(apunte)
        await self.session.commit()
        await self.session.refresh(apunte)
        return apunte

    async def confirmar_asiento(self, asiento_id: UUID) -> AsientoContable:
        """Confirma un asiento contable (debe estar cuadrado)."""
        asiento = await self.obtener_asiento(asiento_id)
        if not asiento:
            raise ValueError(f"Asiento {asiento_id} no encontrado")

        asiento.confirmar()
        self.session.add(asiento)
        await self.session.commit()
        await self.session.refresh(asiento)
        return asiento

    async def anular_asiento(self, asiento_id: UUID) -> AsientoContable:
        """Anula un asiento contable."""
        asiento = await self.obtener_asiento(asiento_id)
        if not asiento:
            raise ValueError(f"Asiento {asiento_id} no encontrado")

        asiento.anular()
        self.session.add(asiento)
        await self.session.commit()
        await self.session.refresh(asiento)
        return asiento

    async def obtener_asientos_por_periodo(
        self,
        ejercicio: int,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        estado: Optional[EstadoAsientoContable] = None,
    ) -> List[AsientoContable]:
        """Obtiene asientos de un período."""
        query = select(AsientoContable).where(AsientoContable.ejercicio == ejercicio)

        if fecha_inicio:
            query = query.where(AsientoContable.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.where(AsientoContable.fecha <= fecha_fin)
        if estado:
            query = query.where(AsientoContable.estado == estado)

        query = query.order_by(AsientoContable.fecha, AsientoContable.numero_asiento)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def calcular_saldo_cuenta(
        self,
        cuenta_id: UUID,
        fecha_fin: Optional[date] = None,
        ejercicio: Optional[int] = None,
    ) -> Decimal:
        """Calcula el saldo de una cuenta en una fecha determinada."""
        query = select(ApunteContable).where(
            and_(
                ApunteContable.cuenta_id == cuenta_id,
            )
        )

        if fecha_fin:
            query = query.join(AsientoContable).where(
                AsientoContable.fecha <= fecha_fin
            )

        if ejercicio:
            query = query.join(AsientoContable).where(
                AsientoContable.ejercicio == ejercicio
            )

        result = await self.session.execute(query)
        apuntes = result.scalars().all()

        saldo = Decimal("0.00")
        for apunte in apuntes:
            saldo += apunte.debe - apunte.haber

        return saldo

    async def generar_balance(
        self, ejercicio: int, fecha_fin: date
    ) -> BalanceContable:
        """Genera un balance de sumas y saldos."""
        # Obtener todos los asientos confirmados del período
        asientos = await self.obtener_asientos_por_periodo(
            ejercicio=ejercicio,
            fecha_fin=fecha_fin,
            estado=EstadoAsientoContable.CONFIRMADO,
        )

        total_debe = Decimal("0.00")
        total_haber = Decimal("0.00")

        for asiento in asientos:
            total_debe += asiento.total_debe
            total_haber += asiento.total_haber

        balance = BalanceContable(
            ejercicio=ejercicio,
            total_debe=total_debe,
            total_haber=total_haber,
        )

        self.session.add(balance)
        await self.session.commit()
        await self.session.refresh(balance)
        return balance

    async def obtener_apuntes_por_cuenta(
        self,
        cuenta_id: UUID,
        ejercicio: Optional[int] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
    ) -> List[ApunteContable]:
        """Obtiene los apuntes de una cuenta."""
        query = select(ApunteContable).where(ApunteContable.cuenta_id == cuenta_id)

        if ejercicio or fecha_inicio or fecha_fin:
            query = query.join(AsientoContable)

            if ejercicio:
                query = query.where(AsientoContable.ejercicio == ejercicio)
            if fecha_inicio:
                query = query.where(AsientoContable.fecha >= fecha_inicio)
            if fecha_fin:
                query = query.where(AsientoContable.fecha <= fecha_fin)

        query = query.order_by(AsientoContable.fecha)
        result = await self.session.execute(query)
        return result.scalars().all()
