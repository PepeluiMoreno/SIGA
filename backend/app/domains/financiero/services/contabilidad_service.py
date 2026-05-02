"""Servicio de contabilidad de partida doble. Solo versión COMPLETA."""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.contabilidad.plan_cuentas import CuentaContable
from ..models.contabilidad.asiento import Asiento, LineaAsiento
from ..core.feature_flags import require_version_completa


class ContabilidadService:

    def __init__(self, session: AsyncSession):
        require_version_completa("ContabilidadService")
        self.session = session

    # -------------------------------------------------------------------------
    # Plan de cuentas
    # -------------------------------------------------------------------------

    async def crear_cuenta(
        self,
        codigo: str,
        nombre: str,
        nivel: int,
        es_imputable: bool = False,
        padre_id: Optional[UUID] = None,
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
            nivel=nivel,
            es_imputable=es_imputable,
            padre_id=padre_id,
            descripcion=descripcion,
        )
        self.session.add(cuenta)
        await self.session.commit()
        await self.session.refresh(cuenta)
        return cuenta

    async def obtener_cuenta(self, cuenta_id: UUID) -> Optional[CuentaContable]:
        result = await self.session.execute(
            select(CuentaContable).where(CuentaContable.id == cuenta_id)
        )
        return result.scalars().first()

    async def obtener_cuenta_por_codigo(self, codigo: str) -> Optional[CuentaContable]:
        result = await self.session.execute(
            select(CuentaContable).where(CuentaContable.codigo == codigo)
        )
        return result.scalars().first()

    async def listar_cuentas(
        self,
        activas_solo: bool = True,
        solo_imputables: bool = False,
        limit: int = 200,
        offset: int = 0,
    ) -> List[CuentaContable]:
        query = select(CuentaContable)
        if activas_solo:
            query = query.where(CuentaContable.activo == True)
        if solo_imputables:
            query = query.where(CuentaContable.es_imputable == True)
        query = query.order_by(CuentaContable.codigo).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def importar_plan_cuentas(self, cuentas: List[dict]) -> int:
        """Importa plan de cuentas desde JSON.

        Cada elemento: {codigo, nombre, nivel, es_imputable, padre_codigo, descripcion}
        """
        creadas = 0
        for item in cuentas:
            padre_id = None
            if item.get("padre_codigo"):
                padre = await self.obtener_cuenta_por_codigo(item["padre_codigo"])
                if padre:
                    padre_id = padre.id

            existing = await self.obtener_cuenta_por_codigo(item["codigo"])
            if not existing:
                await self.crear_cuenta(
                    codigo=item["codigo"],
                    nombre=item["nombre"],
                    nivel=item["nivel"],
                    es_imputable=item.get("es_imputable", False),
                    padre_id=padre_id,
                    descripcion=item.get("descripcion"),
                )
                creadas += 1
        return creadas

    # -------------------------------------------------------------------------
    # Asientos
    # -------------------------------------------------------------------------

    async def _siguiente_numero_asiento(self, ejercicio: int) -> int:
        result = await self.session.execute(
            select(func.max(Asiento.numero)).where(Asiento.ejercicio == ejercicio)
        )
        maximo = result.scalar()
        return (maximo or 0) + 1

    async def crear_asiento(
        self,
        ejercicio: int,
        fecha: date,
        descripcion: str,
        lineas: List[dict],
        observaciones: Optional[str] = None,
    ) -> Asiento:
        """Crea un asiento contable con sus líneas.

        lineas: [{cuenta_id, importe_debe, importe_haber, concepto}]
        Valida que el asiento cuadre antes de persistir.
        """
        # Validar cuadre
        total_debe = sum(Decimal(str(l.get("importe_debe") or 0)) for l in lineas)
        total_haber = sum(Decimal(str(l.get("importe_haber") or 0)) for l in lineas)
        if total_debe != total_haber:
            raise ValueError(
                f"El asiento no cuadra: debe={total_debe}, haber={total_haber}"
            )

        numero = await self._siguiente_numero_asiento(ejercicio)

        asiento = Asiento(
            numero=numero,
            ejercicio=ejercicio,
            fecha=fecha,
            descripcion=descripcion,
            observaciones=observaciones,
        )
        self.session.add(asiento)
        await self.session.flush()  # obtener ID antes de insertar líneas

        for linea in lineas:
            cuenta = await self.obtener_cuenta(linea["cuenta_id"])
            if not cuenta:
                raise ValueError(f"Cuenta {linea['cuenta_id']} no encontrada")
            if not cuenta.es_imputable:
                raise ValueError(f"La cuenta {cuenta.codigo} no es imputable")

            la = LineaAsiento(
                asiento_id=asiento.id,
                cuenta_id=linea["cuenta_id"],
                importe_debe=linea.get("importe_debe"),
                importe_haber=linea.get("importe_haber"),
                concepto=linea.get("concepto", descripcion),
            )
            self.session.add(la)

        await self.session.commit()
        await self.session.refresh(asiento)
        return asiento

    async def obtener_asiento(self, asiento_id: UUID) -> Optional[Asiento]:
        result = await self.session.execute(
            select(Asiento).where(Asiento.id == asiento_id)
        )
        return result.scalars().first()

    async def listar_asientos(
        self,
        ejercicio: int,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Asiento]:
        query = select(Asiento).where(Asiento.ejercicio == ejercicio)
        if fecha_inicio:
            query = query.where(Asiento.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.where(Asiento.fecha <= fecha_fin)
        query = query.order_by(Asiento.fecha, Asiento.numero).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # -------------------------------------------------------------------------
    # Saldos
    # -------------------------------------------------------------------------

    async def saldo_cuenta(
        self,
        cuenta_id: UUID,
        ejercicio: Optional[int] = None,
        fecha_fin: Optional[date] = None,
    ) -> Decimal:
        """Saldo de una cuenta: suma(debe) - suma(haber)."""
        query = select(LineaAsiento).where(LineaAsiento.cuenta_id == cuenta_id)

        if ejercicio or fecha_fin:
            query = query.join(Asiento)
            if ejercicio:
                query = query.where(Asiento.ejercicio == ejercicio)
            if fecha_fin:
                query = query.where(Asiento.fecha <= fecha_fin)

        result = await self.session.execute(query)
        lineas = result.scalars().all()

        return sum(
            (l.importe_debe or Decimal("0")) - (l.importe_haber or Decimal("0"))
            for l in lineas
        )

    async def balance_comprobacion(
        self,
        ejercicio: int,
        fecha_fin: Optional[date] = None,
    ) -> List[dict]:
        """Balance de comprobación: saldo de cada cuenta imputable del ejercicio."""
        cuentas = await self.listar_cuentas(solo_imputables=True)
        resultado = []
        for cuenta in cuentas:
            saldo = await self.saldo_cuenta(cuenta.id, ejercicio=ejercicio, fecha_fin=fecha_fin)
            if saldo != Decimal("0"):
                resultado.append({
                    "cuenta_id": cuenta.id,
                    "codigo": cuenta.codigo,
                    "nombre": cuenta.nombre,
                    "saldo": saldo,
                })
        return resultado
