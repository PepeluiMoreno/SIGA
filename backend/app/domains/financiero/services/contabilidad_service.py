"""Servicio de contabilidad de partida doble. Solo versión COMPLETA."""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.contabilidad.plan_cuentas import CuentaContable, TipoCuentaContable
from ..models.contabilidad.asiento import (
    AsientoContable, ApunteContable,
    TipoAsientoContable, EstadoAsientoContable,
)
from ..core.feature_flags import require_version_completa


class ContabilidadService:

    def __init__(self, session: AsyncSession):
        require_version_completa("ContabilidadService")
        self.session = session

    # -------------------------------------------------------------------------
    # Plan de cuentas
    # -------------------------------------------------------------------------

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
        result = await self.session.execute(
            select(CuentaContable).where(CuentaContable.codigo == codigo)
        )
        if result.scalars().first():
            raise ValueError(f"Ya existe una cuenta con código '{codigo}'")

        cuenta = CuentaContable(
            codigo=codigo,
            nombre=nombre,
            tipo=tipo,
            nivel=nivel,
            padre_id=padre_id,
            es_dotacion=es_dotacion,
            permite_asiento=(nivel >= 3),
            descripcion=descripcion,
        )
        self.session.add(cuenta)
        await self.session.commit()
        await self.session.refresh(cuenta)
        return cuenta

    async def obtener_cuenta_contable(self, cuenta_id: UUID) -> Optional[CuentaContable]:
        result = await self.session.execute(
            select(CuentaContable).where(CuentaContable.id == cuenta_id)
        )
        return result.scalars().first()

    async def obtener_cuenta_por_codigo(self, codigo: str) -> Optional[CuentaContable]:
        result = await self.session.execute(
            select(CuentaContable).where(CuentaContable.codigo == codigo)
        )
        return result.scalars().first()

    async def listar_cuentas_contables(
        self,
        tipo: Optional[TipoCuentaContable] = None,
        activas_solo: bool = True,
        solo_imputables: bool = False,
        limit: int = 200,
        offset: int = 0,
    ) -> List[CuentaContable]:
        query = select(CuentaContable)
        if activas_solo:
            query = query.where(CuentaContable.activo == True)
        if tipo:
            query = query.where(CuentaContable.tipo == tipo)
        if solo_imputables:
            query = query.where(CuentaContable.permite_asiento == True)
        query = query.order_by(CuentaContable.codigo).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def importar_plan_cuentas(self, cuentas: List[dict]) -> int:
        """Importa plan de cuentas desde JSON.

        Cada elemento: {codigo, nombre, tipo, nivel, es_dotacion, padre_codigo, descripcion}
        """
        existentes: dict[str, CuentaContable] = {}
        result = await self.session.execute(select(CuentaContable))
        for c in result.scalars().all():
            existentes[c.codigo] = c

        creadas = 0
        for item in cuentas:
            if item["codigo"] in existentes:
                continue
            padre_id = None
            if item.get("padre_codigo"):
                padre = existentes.get(item["padre_codigo"])
                if padre:
                    padre_id = padre.id
            cuenta = CuentaContable(
                codigo=item["codigo"],
                nombre=item["nombre"],
                tipo=TipoCuentaContable(item["tipo"]),
                nivel=item["nivel"],
                padre_id=padre_id,
                es_dotacion=item.get("es_dotacion", False),
                permite_asiento=item.get("nivel", 1) >= 3,
                descripcion=item.get("descripcion"),
            )
            self.session.add(cuenta)
            existentes[cuenta.codigo] = cuenta
            creadas += 1
        await self.session.commit()
        return creadas

    # -------------------------------------------------------------------------
    # Asientos
    # -------------------------------------------------------------------------

    async def _siguiente_numero_asiento(self, ejercicio: int) -> int:
        result = await self.session.execute(
            select(func.max(AsientoContable.numero_asiento)).where(
                AsientoContable.ejercicio == ejercicio
            )
        )
        return (result.scalar() or 0) + 1

    async def crear_asiento(
        self,
        ejercicio: int,
        fecha: date,
        glosa: str,
        lineas: List[dict],
        tipo_asiento: TipoAsientoContable = TipoAsientoContable.GESTION,
        observaciones: Optional[str] = None,
    ) -> AsientoContable:
        """Crea un asiento contable con sus apuntes y lo confirma si cuadra.

        lineas: [{cuenta_id, debe, haber, concepto, actividad_id}]
        """
        total_debe = sum(Decimal(str(l.get("debe") or 0)) for l in lineas)
        total_haber = sum(Decimal(str(l.get("haber") or 0)) for l in lineas)
        if total_debe != total_haber:
            raise ValueError(
                f"El asiento no cuadra: debe={total_debe}, haber={total_haber}"
            )

        numero = await self._siguiente_numero_asiento(ejercicio)

        asiento = AsientoContable(
            ejercicio=ejercicio,
            numero_asiento=numero,
            fecha=fecha,
            glosa=glosa,
            tipo_asiento=tipo_asiento,
            estado=EstadoAsientoContable.BORRADOR,
            observaciones=observaciones,
        )
        self.session.add(asiento)
        await self.session.flush()

        for linea in lineas:
            cuenta = await self.obtener_cuenta_contable(linea["cuenta_id"])
            if not cuenta:
                raise ValueError(f"Cuenta {linea['cuenta_id']} no encontrada")
            if not cuenta.permite_asiento:
                raise ValueError(f"La cuenta {cuenta.codigo} no permite asientos")

            apunte = ApunteContable(
                asiento_id=asiento.id,
                cuenta_id=linea["cuenta_id"],
                debe=linea.get("debe"),
                haber=linea.get("haber"),
                concepto=linea.get("concepto", glosa),
                actividad_id=linea.get("actividad_id"),
            )
            self.session.add(apunte)

        asiento.confirmar()
        await self.session.commit()
        await self.session.refresh(asiento)
        return asiento

    async def obtener_asiento(self, asiento_id: UUID) -> Optional[AsientoContable]:
        result = await self.session.execute(
            select(AsientoContable).where(AsientoContable.id == asiento_id)
        )
        return result.scalars().first()

    async def anular_asiento(self, asiento_id: UUID) -> AsientoContable:
        asiento = await self.obtener_asiento(asiento_id)
        if not asiento:
            raise ValueError(f"Asiento {asiento_id} no encontrado")
        asiento.anular()
        self.session.add(asiento)
        await self.session.commit()
        await self.session.refresh(asiento)
        return asiento

    async def listar_asientos(
        self,
        ejercicio: int,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        tipo_asiento: Optional[TipoAsientoContable] = None,
        estado: Optional[EstadoAsientoContable] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[AsientoContable]:
        query = select(AsientoContable).where(AsientoContable.ejercicio == ejercicio)
        if fecha_inicio:
            query = query.where(AsientoContable.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.where(AsientoContable.fecha <= fecha_fin)
        if tipo_asiento:
            query = query.where(AsientoContable.tipo_asiento == tipo_asiento)
        if estado:
            query = query.where(AsientoContable.estado == estado)
        query = query.order_by(AsientoContable.fecha, AsientoContable.numero_asiento)
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # -------------------------------------------------------------------------
    # Saldos y balances
    # -------------------------------------------------------------------------

    async def calcular_saldo_cuenta(
        self,
        cuenta_id: UUID,
        ejercicio: Optional[int] = None,
        fecha_fin: Optional[date] = None,
    ) -> Decimal:
        """Saldo de una cuenta: suma(debe) - suma(haber) sobre asientos CONFIRMADOS."""
        query = (
            select(ApunteContable)
            .join(AsientoContable)
            .where(
                ApunteContable.cuenta_id == cuenta_id,
                AsientoContable.estado == EstadoAsientoContable.CONFIRMADO,
            )
        )
        if ejercicio:
            query = query.where(AsientoContable.ejercicio == ejercicio)
        if fecha_fin:
            query = query.where(AsientoContable.fecha <= fecha_fin)

        result = await self.session.execute(query)
        apuntes = result.scalars().all()
        return sum(
            (a.debe or Decimal("0")) - (a.haber or Decimal("0"))
            for a in apuntes
        )

    async def balance_comprobacion(
        self,
        ejercicio: int,
        fecha_fin: Optional[date] = None,
    ) -> List[dict]:
        """Balance de comprobación: saldo de cada cuenta imputable con movimiento."""
        cuentas = await self.listar_cuentas_contables(solo_imputables=True)
        resultado = []
        for cuenta in cuentas:
            saldo = await self.calcular_saldo_cuenta(
                cuenta.id, ejercicio=ejercicio, fecha_fin=fecha_fin
            )
            if saldo != Decimal("0"):
                resultado.append({
                    "cuenta_id": cuenta.id,
                    "codigo": cuenta.codigo,
                    "nombre": cuenta.nombre,
                    "tipo": cuenta.tipo,
                    "saldo": saldo,
                })
        return resultado
