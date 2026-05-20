"""Servicio de contabilidad para gestión de asientos y plan de cuentas (PCESFL 2013)."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.contabilidad import (
    CuentaContable,
    AsientoContable,
    ApunteContable,
    TipoCuentaContable,
    TipoAsientoContable,
    EstadoAsientoContable,
)
from ..core.feature_flags import is_version_completa


class ContabilidadService:
    """Servicio para gestionar contabilidad: plan de cuentas y asientos (PCESFL 2013)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ─── Plan de cuentas ─────────────────────────────────────────────────────

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
        # Validar código único
        existing = await self.session.execute(
            select(CuentaContable).where(CuentaContable.codigo == codigo)
        )
        if existing.scalars().first():
            raise ValueError(f"Ya existe una cuenta con código {codigo}")

        # Solo las cuentas de nivel más profundo (hojas) permiten asientos
        permite_asiento = (nivel >= 3 and padre_id is not None)

        cuenta = CuentaContable(
            codigo=codigo,
            nombre=nombre,
            tipo=tipo,
            nivel=nivel,
            padre_id=padre_id,
            es_dotacion=es_dotacion,
            descripcion=descripcion,
            permite_asiento=permite_asiento,
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

    async def listar_plan_cuentas(
        self,
        tipo: Optional[TipoCuentaContable] = None,
        nivel: Optional[int] = None,
        activas_solo: bool = True,
    ) -> List[CuentaContable]:
        query = select(CuentaContable)
        filtros = []
        if tipo:
            filtros.append(CuentaContable.tipo == tipo)
        if nivel is not None:
            filtros.append(CuentaContable.nivel == nivel)
        if activas_solo:
            filtros.append(CuentaContable.activa == True)
        if filtros:
            query = query.where(and_(*filtros))
        query = query.order_by(CuentaContable.codigo)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def listar_cuentas_raiz(self) -> List[CuentaContable]:
        """Devuelve las cuentas sin padre (grupos de nivel 1)."""
        result = await self.session.execute(
            select(CuentaContable)
            .where(and_(CuentaContable.padre_id == None, CuentaContable.activa == True))
            .order_by(CuentaContable.codigo)
        )
        return list(result.scalars().all())

    async def tiene_apuntes_confirmados(self, cuenta_id: UUID) -> bool:
        """¿Esta cuenta tiene apuntes en asientos CONFIRMADOS?

        Si los tiene, no se puede modificar su código, tipo ni padre, ni eliminarla
        (rompería la integridad contable). Solo se puede renombrar y desactivar.
        """
        r = await self.session.execute(
            select(func.count(ApunteContable.id))
            .join(AsientoContable, ApunteContable.asiento_id == AsientoContable.id)
            .where(ApunteContable.cuenta_id == cuenta_id)
            .where(AsientoContable.estado == EstadoAsientoContable.CONFIRMADO)
        )
        return (r.scalar() or 0) > 0

    async def ejercicio_cerrado(self, ejercicio: int) -> bool:
        """¿El ejercicio ya tiene un asiento de CIERRE confirmado?

        Si lo tiene, no se debe permitir crear asientos nuevos en ese ejercicio:
        los importes ya se han depositado en Cuentas Anuales (Ley 50/2002 art.34,
        LO 8/2007 para partidos políticos). Cualquier modificación rompería la
        imagen fiel y obligaría a reformular las cuentas.
        """
        r = await self.session.execute(
            select(func.count(AsientoContable.id))
            .where(AsientoContable.ejercicio == ejercicio)
            .where(AsientoContable.tipo_asiento == TipoAsientoContable.CIERRE)
            .where(AsientoContable.estado == EstadoAsientoContable.CONFIRMADO)
        )
        return (r.scalar() or 0) > 0

    # ─── Asientos contables ───────────────────────────────────────────────────

    async def siguiente_numero_asiento(self, ejercicio: int) -> int:
        """Devuelve el siguiente número de asiento disponible para el ejercicio."""
        result = await self.session.execute(
            select(func.max(AsientoContable.numero_asiento)).where(
                AsientoContable.ejercicio == ejercicio
            )
        )
        max_num = result.scalar()
        return (max_num or 0) + 1

    async def crear_asiento(
        self,
        ejercicio: int,
        fecha: date,
        glosa: str,
        tipo_asiento: TipoAsientoContable = TipoAsientoContable.GESTION,
        observaciones: Optional[str] = None,
    ) -> AsientoContable:
        """Crea un nuevo asiento en estado BORRADOR.

        Rechaza si el ejercicio ya está cerrado (tiene asiento CIERRE confirmado),
        salvo que el asiento sea precisamente de APERTURA (caso legítimo: la
        apertura del ejercicio siguiente arrastra saldos del cerrado).
        """
        if tipo_asiento != TipoAsientoContable.APERTURA and await self.ejercicio_cerrado(ejercicio):
            raise ValueError(
                f"El ejercicio {ejercicio} está cerrado (tiene asiento de CIERRE confirmado). "
                f"No se pueden crear nuevos asientos."
            )
        numero_asiento = await self.siguiente_numero_asiento(ejercicio)
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
        result = await self.session.execute(
            select(AsientoContable).where(AsientoContable.id == asiento_id)
        )
        return result.scalars().first()

    async def listar_asientos(
        self,
        ejercicio: Optional[int] = None,
        estado: Optional[EstadoAsientoContable] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
    ) -> List[AsientoContable]:
        query = select(AsientoContable)
        filtros = []
        if ejercicio:
            filtros.append(AsientoContable.ejercicio == ejercicio)
        if estado:
            filtros.append(AsientoContable.estado == estado)
        if fecha_inicio:
            filtros.append(AsientoContable.fecha >= fecha_inicio)
        if fecha_fin:
            filtros.append(AsientoContable.fecha <= fecha_fin)
        if filtros:
            query = query.where(and_(*filtros))
        query = query.order_by(AsientoContable.fecha, AsientoContable.numero_asiento)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # ─── Apuntes (líneas de asiento) ─────────────────────────────────────────

    async def añadir_apunte(
        self,
        asiento_id: UUID,
        cuenta_id: UUID,
        debe: Decimal = Decimal("0.00"),
        haber: Decimal = Decimal("0.00"),
        concepto: str = "",
        actividad_id: Optional[UUID] = None,
    ) -> ApunteContable:
        """Añade un apunte (línea debe/haber) a un asiento en BORRADOR."""
        # Validaciones
        if debe < Decimal('0') or haber < Decimal('0'):
            raise ValueError("Debe y haber deben ser positivos o cero")
        if debe > Decimal('0') and haber > Decimal('0'):
            raise ValueError("Un apunte no puede tener debe y haber simultáneamente")
        if debe == Decimal('0') and haber == Decimal('0'):
            raise ValueError("Un apunte debe tener debe o haber")

        asiento = await self.obtener_asiento(asiento_id)
        if not asiento:
            raise ValueError(f"Asiento {asiento_id} no encontrado")
        if asiento.estado != EstadoAsientoContable.BORRADOR:
            raise ValueError("Solo se pueden añadir apuntes a asientos en BORRADOR")

        cuenta = await self.obtener_cuenta_contable(cuenta_id)
        if not cuenta:
            raise ValueError(f"Cuenta contable {cuenta_id} no encontrada")
        if not cuenta.permite_asiento:
            raise ValueError(f"La cuenta {cuenta.codigo} no permite asientos directos")

        apunte = ApunteContable(
            asiento_id=asiento_id,
            cuenta_id=cuenta_id,
            debe=debe,
            haber=haber,
            concepto=concepto,
            actividad_id=actividad_id,
        )
        self.session.add(apunte)
        await self.session.commit()
        await self.session.refresh(apunte)
        return apunte

    async def listar_apuntes_cuenta(
        self,
        cuenta_id: UUID,
        ejercicio: Optional[int] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
    ) -> List[ApunteContable]:
        """Devuelve los apuntes de una cuenta (libro mayor)."""
        query = (
            select(ApunteContable)
            .join(AsientoContable, ApunteContable.asiento_id == AsientoContable.id)
            .where(ApunteContable.cuenta_id == cuenta_id)
            .where(AsientoContable.estado == EstadoAsientoContable.CONFIRMADO)
        )
        # Aplicar filtros adicionales sobre AsientoContable en el mismo join
        if ejercicio:
            query = query.where(AsientoContable.ejercicio == ejercicio)
        if fecha_inicio:
            query = query.where(AsientoContable.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.where(AsientoContable.fecha <= fecha_fin)

        query = query.order_by(AsientoContable.fecha, AsientoContable.numero_asiento)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # ─── Confirmación y anulación ─────────────────────────────────────────────

    async def confirmar_asiento(self, asiento_id: UUID) -> AsientoContable:
        """Confirma un asiento — debe estar cuadrado (debe == haber)."""
        asiento = await self.obtener_asiento(asiento_id)
        if not asiento:
            raise ValueError(f"Asiento {asiento_id} no encontrado")
        asiento.confirmar()  # Lanza ValueError si no cuadra
        self.session.add(asiento)
        await self.session.commit()
        await self.session.refresh(asiento)
        return asiento

    async def anular_asiento(self, asiento_id: UUID) -> AsientoContable:
        """Anula un asiento y genera el asiento de contrapartida."""
        asiento = await self.obtener_asiento(asiento_id)
        if not asiento:
            raise ValueError(f"Asiento {asiento_id} no encontrado")
        asiento.anular()
        self.session.add(asiento)
        await self.session.commit()
        await self.session.refresh(asiento)
        return asiento

    # ─── Cálculo de saldos ───────────────────────────────────────────────────

    async def calcular_saldo_cuenta(
        self,
        cuenta_id: UUID,
        ejercicio: Optional[int] = None,
        fecha_fin: Optional[date] = None,
    ) -> Decimal:
        """Calcula el saldo acumulado de una cuenta (debe - haber) sobre asientos CONFIRMADOS."""
        # Un único join a AsientoContable con todos los filtros juntos
        query = (
            select(
                func.coalesce(func.sum(ApunteContable.debe), Decimal('0')).label('total_debe'),
                func.coalesce(func.sum(ApunteContable.haber), Decimal('0')).label('total_haber'),
            )
            .join(AsientoContable, ApunteContable.asiento_id == AsientoContable.id)
            .where(ApunteContable.cuenta_id == cuenta_id)
            .where(AsientoContable.estado == EstadoAsientoContable.CONFIRMADO)
        )
        if ejercicio:
            query = query.where(AsientoContable.ejercicio == ejercicio)
        if fecha_fin:
            query = query.where(AsientoContable.fecha <= fecha_fin)

        result = await self.session.execute(query)
        row = result.first()
        return (row.total_debe or Decimal('0')) - (row.total_haber or Decimal('0'))

    # ─── Balance de sumas y saldos (al vuelo, no se persiste) ─────────────────

    async def calcular_balance_sumas_y_saldos(
        self,
        ejercicio: int,
        fecha_corte: Optional[date] = None,
        solo_con_saldo: bool = True,
    ) -> list[dict]:
        """Calcula el balance de sumas y saldos del ejercicio a una fecha de corte.

        Este balance NO se persiste — es una proyección en vivo del libro mayor
        a una fecha dada. Se usa para verificar cuadre (Σ debe = Σ haber) y como
        base para el balance PCESFL del cierre.

        Devuelve una lista de dicts con: codigo, nombre, tipo, total_debe,
        total_haber, saldo (positivo = deudor, negativo = acreedor).
        """
        if fecha_corte is None:
            fecha_corte = date.today()

        query = (
            select(
                CuentaContable.codigo,
                CuentaContable.nombre,
                CuentaContable.tipo,
                func.coalesce(func.sum(ApunteContable.debe), Decimal('0')).label('total_debe'),
                func.coalesce(func.sum(ApunteContable.haber), Decimal('0')).label('total_haber'),
            )
            .select_from(CuentaContable)
            .outerjoin(ApunteContable, ApunteContable.cuenta_id == CuentaContable.id)
            .outerjoin(
                AsientoContable,
                (AsientoContable.id == ApunteContable.asiento_id)
                & (AsientoContable.ejercicio == ejercicio)
                & (AsientoContable.estado == EstadoAsientoContable.CONFIRMADO)
                & (AsientoContable.fecha <= fecha_corte),
            )
            .group_by(CuentaContable.codigo, CuentaContable.nombre, CuentaContable.tipo)
            .order_by(CuentaContable.codigo)
        )
        result = await self.session.execute(query)
        filas = []
        for r in result.all():
            saldo = (r.total_debe or Decimal('0')) - (r.total_haber or Decimal('0'))
            if solo_con_saldo and r.total_debe == 0 and r.total_haber == 0:
                continue
            filas.append({
                "codigo": r.codigo,
                "nombre": r.nombre,
                "tipo": r.tipo.value if hasattr(r.tipo, "value") else str(r.tipo),
                "total_debe": r.total_debe or Decimal('0'),
                "total_haber": r.total_haber or Decimal('0'),
                "saldo": saldo,
            })
        return filas

    async def resumen_cuentas_por_tipo(
        self, ejercicio: int, fecha_fin: Optional[date] = None
    ) -> dict:
        """Suma de saldos agrupada por tipo de cuenta (para dashboard)."""
        if fecha_fin is None:
            fecha_fin = date.today()

        query = (
            select(
                CuentaContable.tipo,
                func.coalesce(func.sum(ApunteContable.debe), Decimal('0')).label('total_debe'),
                func.coalesce(func.sum(ApunteContable.haber), Decimal('0')).label('total_haber'),
            )
            .join(ApunteContable, CuentaContable.id == ApunteContable.cuenta_id)
            .join(AsientoContable, ApunteContable.asiento_id == AsientoContable.id)
            .where(AsientoContable.ejercicio == ejercicio)
            .where(AsientoContable.estado == EstadoAsientoContable.CONFIRMADO)
            .where(AsientoContable.fecha <= fecha_fin)
            .group_by(CuentaContable.tipo)
        )
        result = await self.session.execute(query)
        return {
            row.tipo.value: {
                "debe": row.total_debe,
                "haber": row.total_haber,
                "saldo": row.total_debe - row.total_haber,
            }
            for row in result.all()
        }
