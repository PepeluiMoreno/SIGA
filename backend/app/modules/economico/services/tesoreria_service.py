"""Servicio de tesorería para gestión de cuentas bancarias y movimientos."""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.tesoreria import (
    CuentaBancaria,
    ApunteCaja,
    TipoApunte,
    OrigenApunte,
    ExtractoBancario,
    Conciliacion,
    MetodoConciliacion,
    ConciliacionBancaria,
)
from ..models.remesas import Remesa, OrdenCobro
from ..models.cuotas import CuotaAnual
from app.modules.configuracion.models.estados import EstadoCuota, EstadoRemesa, EstadoOrdenCobro


class TesoreriaService:
    """Servicio para gestionar tesorería: cuentas bancarias y movimientos."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ─── Cuentas bancarias ────────────────────────────────────────────────────

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
        """Crea una nueva cuenta bancaria."""
        # Validar IBAN único
        existing = await self.session.execute(
            select(CuentaBancaria).where(CuentaBancaria.iban == iban)
        )
        if existing.scalars().first():
            raise ValueError(f"Ya existe una cuenta con IBAN {iban[-4:]}")

        cuenta = CuentaBancaria(
            nombre=nombre,
            iban=iban,
            banco_nombre=banco_nombre,
            bic_swift=bic_swift,
            titular=titular,
            agrupacion_id=agrupacion_id,
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
        self, activas_solo: bool = True
    ) -> List[CuentaBancaria]:
        query = select(CuentaBancaria)
        if activas_solo:
            query = query.where(CuentaBancaria.activa == True)
        query = query.order_by(CuentaBancaria.nombre)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def actualizar_cuenta_bancaria(
        self, cuenta_id: UUID, **kwargs
    ) -> CuentaBancaria:
        cuenta = await self.obtener_cuenta_bancaria(cuenta_id)
        if not cuenta:
            raise ValueError(f"Cuenta {cuenta_id} no encontrada")
        for key, value in kwargs.items():
            if hasattr(cuenta, key) and value is not None:
                setattr(cuenta, key, value)
        self.session.add(cuenta)
        await self.session.commit()
        await self.session.refresh(cuenta)
        return cuenta

    async def desactivar_cuenta_bancaria(self, cuenta_id: UUID) -> CuentaBancaria:
        cuenta = await self.obtener_cuenta_bancaria(cuenta_id)
        if not cuenta:
            raise ValueError(f"Cuenta {cuenta_id} no encontrada")
        cuenta.activa = False
        self.session.add(cuenta)
        await self.session.commit()
        await self.session.refresh(cuenta)
        return cuenta

    # ─── Apuntes de caja ─────────────────────────────────────────────────────

    async def registrar_apunte(
        self,
        cuenta_id: UUID,
        fecha: date,
        importe: Decimal,
        tipo: TipoApunte,
        concepto: str,
        origen: Optional[OrigenApunte] = None,
        entidad_origen_tipo: Optional[str] = None,
        entidad_origen_id: Optional[UUID] = None,
        referencia_externa: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> ApunteCaja:
        """Registra un movimiento de caja y actualiza el saldo de la cuenta."""
        cuenta = await self.obtener_cuenta_bancaria(cuenta_id)
        if not cuenta:
            raise ValueError(f"Cuenta bancaria {cuenta_id} no encontrada")
        if not cuenta.activa:
            raise ValueError(f"La cuenta {cuenta.nombre} está inactiva")
        if importe <= Decimal('0'):
            raise ValueError("El importe debe ser positivo")

        apunte = ApunteCaja(
            cuenta_bancaria_id=cuenta_id,
            fecha=fecha,
            importe=importe,
            tipo=tipo,
            concepto=concepto,
            origen=origen,
            entidad_origen_tipo=entidad_origen_tipo,
            entidad_origen_id=entidad_origen_id,
            referencia_externa=referencia_externa,
            observaciones=observaciones,
        )

        # Actualizar saldo
        if tipo == TipoApunte.INGRESO:
            cuenta.saldo_actual += importe
        elif tipo == TipoApunte.GASTO:
            cuenta.saldo_actual -= importe
        # TRANSFERENCIA: se gestiona en dos apuntes separados (uno en cada cuenta)

        self.session.add(apunte)
        self.session.add(cuenta)
        await self.session.commit()
        await self.session.refresh(apunte)
        return apunte

    # Alias para compatibilidad con el nombre antiguo
    async def registrar_movimiento(
        self,
        cuenta_id: UUID,
        fecha: date,
        importe: Decimal,
        tipo: TipoApunte,
        concepto: str,
        referencia_externa: Optional[str] = None,
        entidad_origen_tipo: Optional[str] = None,
        entidad_origen_id: Optional[UUID] = None,
        observaciones: Optional[str] = None,
    ) -> ApunteCaja:
        return await self.registrar_apunte(
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

    async def obtener_apunte(self, apunte_id: UUID) -> Optional[ApunteCaja]:
        result = await self.session.execute(
            select(ApunteCaja).where(ApunteCaja.id == apunte_id)
        )
        return result.scalars().first()

    async def listar_apuntes(
        self,
        cuenta_id: Optional[UUID] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        tipo: Optional[TipoApunte] = None,
        conciliado: Optional[bool] = None,
    ) -> List[ApunteCaja]:
        query = select(ApunteCaja)
        filtros = []
        if cuenta_id:
            filtros.append(ApunteCaja.cuenta_bancaria_id == cuenta_id)
        if fecha_inicio:
            filtros.append(ApunteCaja.fecha >= fecha_inicio)
        if fecha_fin:
            filtros.append(ApunteCaja.fecha <= fecha_fin)
        if tipo:
            filtros.append(ApunteCaja.tipo == tipo)
        if conciliado is not None:
            filtros.append(ApunteCaja.conciliado == conciliado)
        if filtros:
            query = query.where(and_(*filtros))
        query = query.order_by(ApunteCaja.fecha.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def apuntes_pendientes_conciliacion(self, cuenta_id: UUID) -> List[ApunteCaja]:
        return await self.listar_apuntes(cuenta_id=cuenta_id, conciliado=False)

    async def marcar_apunte_conciliado(
        self, apunte_id: UUID, fecha_conciliacion: Optional[date] = None
    ) -> ApunteCaja:
        apunte = await self.obtener_apunte(apunte_id)
        if not apunte:
            raise ValueError(f"Apunte {apunte_id} no encontrado")
        apunte.conciliado = True
        apunte.fecha_conciliacion = fecha_conciliacion or date.today()
        self.session.add(apunte)
        await self.session.commit()
        await self.session.refresh(apunte)
        return apunte

    # ─── Extractos bancarios ─────────────────────────────────────────────────

    async def importar_extracto(
        self,
        cuenta_id: UUID,
        lineas: List[dict],
    ) -> List[ExtractoBancario]:
        """Importa líneas de un extracto bancario (CSV/Norma43/MT940)."""
        cuenta = await self.obtener_cuenta_bancaria(cuenta_id)
        if not cuenta:
            raise ValueError(f"Cuenta {cuenta_id} no encontrada")

        extractos = []
        for linea in lineas:
            extracto = ExtractoBancario(
                cuenta_bancaria_id=cuenta_id,
                fecha=linea['fecha'],
                importe=Decimal(str(linea['importe'])),
                concepto=linea.get('concepto'),
                referencia=linea.get('referencia'),
            )
            self.session.add(extracto)
            extractos.append(extracto)

        await self.session.commit()
        for e in extractos:
            await self.session.refresh(e)
        return extractos

    async def listar_extractos(
        self,
        cuenta_id: UUID,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        conciliados: Optional[bool] = None,
    ) -> List[ExtractoBancario]:
        query = select(ExtractoBancario).where(
            ExtractoBancario.cuenta_bancaria_id == cuenta_id
        )
        if fecha_inicio:
            query = query.where(ExtractoBancario.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.where(ExtractoBancario.fecha <= fecha_fin)
        if conciliados is not None:
            query = query.where(ExtractoBancario.conciliado == conciliados)
        query = query.order_by(ExtractoBancario.fecha.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # ─── Conciliación ────────────────────────────────────────────────────────

    async def conciliar_apunte_con_extracto(
        self,
        apunte_id: UUID,
        extracto_id: UUID,
        metodo: MetodoConciliacion = MetodoConciliacion.MANUAL,
        usuario_id: Optional[UUID] = None,
    ) -> Conciliacion:
        """Vincula un apunte de caja con una línea de extracto bancario."""
        apunte = await self.obtener_apunte(apunte_id)
        if not apunte:
            raise ValueError(f"Apunte {apunte_id} no encontrado")

        conciliacion = Conciliacion(
            apunte_id=apunte_id,
            extracto_id=extracto_id,
            metodo=metodo,
            usuario_id=usuario_id,
        )
        # Marcar ambos como conciliados
        apunte.conciliado = True
        apunte.fecha_conciliacion = date.today()

        extracto_result = await self.session.execute(
            select(ExtractoBancario).where(ExtractoBancario.id == extracto_id)
        )
        extracto = extracto_result.scalars().first()
        if extracto:
            extracto.conciliado = True

        self.session.add(conciliacion)
        self.session.add(apunte)
        if extracto:
            self.session.add(extracto)
        await self.session.commit()
        await self.session.refresh(conciliacion)
        return conciliacion

    async def crear_conciliacion_periodo(
        self,
        cuenta_id: UUID,
        fecha_inicio: date,
        fecha_fin: date,
        saldo_inicial_extracto: Decimal,
        saldo_final_extracto: Decimal,
    ) -> ConciliacionBancaria:
        """Crea un registro de cierre de conciliación por período."""
        cuenta = await self.obtener_cuenta_bancaria(cuenta_id)
        if not cuenta:
            raise ValueError(f"Cuenta {cuenta_id} no encontrada")

        # Calcular saldo del sistema en el período
        result = await self.session.execute(
            select(
                func.sum(
                    ApunteCaja.importe
                ).filter(ApunteCaja.tipo == TipoApunte.INGRESO)
            ).where(
                and_(
                    ApunteCaja.cuenta_bancaria_id == cuenta_id,
                    ApunteCaja.fecha >= fecha_inicio,
                    ApunteCaja.fecha <= fecha_fin,
                )
            )
        )
        total_ingresos = result.scalar() or Decimal('0')

        result = await self.session.execute(
            select(
                func.sum(ApunteCaja.importe)
            ).where(
                and_(
                    ApunteCaja.cuenta_bancaria_id == cuenta_id,
                    ApunteCaja.fecha >= fecha_inicio,
                    ApunteCaja.fecha <= fecha_fin,
                    ApunteCaja.tipo == TipoApunte.GASTO,
                )
            )
        )
        total_gastos = result.scalar() or Decimal('0')

        movimiento_neto = total_ingresos - total_gastos
        saldo_inicial_sistema = cuenta.saldo_actual - movimiento_neto
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

    async def confirmar_conciliacion_periodo(
        self, conciliacion_id: UUID
    ) -> ConciliacionBancaria:
        """Confirma una conciliación bancaria (diferencia debe ser 0)."""
        result = await self.session.execute(
            select(ConciliacionBancaria).where(ConciliacionBancaria.id == conciliacion_id)
        )
        conciliacion = result.scalars().first()
        if not conciliacion:
            raise ValueError(f"Conciliación {conciliacion_id} no encontrada")
        if not conciliacion.esta_equilibrada:
            raise ValueError(
                f"No se puede confirmar: diferencia de {conciliacion.diferencia} €"
            )
        conciliacion.conciliado = True
        conciliacion.fecha_conciliacion = date.today()
        self.session.add(conciliacion)
        await self.session.commit()
        await self.session.refresh(conciliacion)
        return conciliacion

    async def listar_conciliaciones_periodo(
        self, cuenta_id: UUID
    ) -> List[ConciliacionBancaria]:
        result = await self.session.execute(
            select(ConciliacionBancaria)
            .where(ConciliacionBancaria.cuenta_bancaria_id == cuenta_id)
            .order_by(ConciliacionBancaria.fecha_fin.desc())
        )
        return list(result.scalars().all())

    # ─── Saldos y KPIs ───────────────────────────────────────────────────────

    async def obtener_saldo_cuenta(self, cuenta_id: UUID) -> Decimal:
        cuenta = await self.obtener_cuenta_bancaria(cuenta_id)
        if not cuenta:
            raise ValueError(f"Cuenta {cuenta_id} no encontrada")
        return cuenta.saldo_actual

    async def obtener_saldo_total(self) -> Decimal:
        """Suma de saldos de todas las cuentas activas."""
        result = await self.session.execute(
            select(func.sum(CuentaBancaria.saldo_actual)).where(
                CuentaBancaria.activa == True
            )
        )
        return result.scalar() or Decimal('0')

    async def calcular_totales_periodo(
        self, cuenta_id: UUID, fecha_inicio: date, fecha_fin: date
    ) -> dict:
        """Calcula ingresos, gastos y saldo neto de un período."""
        apuntes = await self.listar_apuntes(
            cuenta_id=cuenta_id, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin
        )
        ingresos = sum(a.importe for a in apuntes if a.tipo == TipoApunte.INGRESO)
        gastos = sum(a.importe for a in apuntes if a.tipo == TipoApunte.GASTO)
        return {
            "ingresos": ingresos,
            "gastos": gastos,
            "saldo_neto": ingresos - gastos,
            "num_movimientos": len(apuntes),
        }

    # ─── Liquidación automática de remesas (SEPA → ApunteCaja → Asiento) ────

    async def liquidar_remesa(
        self,
        remesa_id: UUID,
        cuenta_bancaria_id: UUID,
        fecha_cobro: Optional[date] = None,
    ) -> ApunteCaja:
        """Liquida una remesa SEPA: marca las órdenes como Procesadas, actualiza
        las cuotas a Cobradas y genera un ApunteCaja de ingreso por el importe neto.

        El ApunteCaja, al ser creado, dispara automáticamente el asiento contable
        de partida doble si VERSION=COMPLETA.
        """
        from ..services.registro_contable import RegistroContable

        result = await self.session.execute(select(Remesa).where(Remesa.id == remesa_id))
        remesa = result.scalars().first()
        if not remesa:
            raise ValueError(f"Remesa {remesa_id} no encontrada")

        # Cargar estados
        est_result = await self.session.execute(
            select(EstadoRemesa).where(EstadoRemesa.nombre.in_(["Procesada"]))
        )
        estado_remesa_procesada = est_result.scalars().first()

        oc_est = await self.session.execute(
            select(EstadoOrdenCobro).where(EstadoOrdenCobro.nombre.in_(["Procesada", "Pendiente"]))
        )
        oc_estados = {e.nombre: e.id for e in oc_est.scalars()}

        cuota_est = await self.session.execute(
            select(EstadoCuota).where(EstadoCuota.nombre.in_(["Cobrada", "Pendiente"]))
        )
        cuota_estados = {e.nombre: e.id for e in cuota_est.scalars()}

        estado_oc_procesada = oc_estados.get("Procesada")
        estado_cuota_cobrada = cuota_estados.get("Cobrada")

        # Liquidar órdenes pendientes
        ordenes = await self.session.execute(
            select(OrdenCobro)
            .where(OrdenCobro.remesa_id == remesa_id)
            .where(OrdenCobro.estado_id == oc_estados.get("Pendiente"))
        )
        importe_total = Decimal("0.00")
        for orden in ordenes.scalars():
            if estado_oc_procesada:
                orden.estado_id = estado_oc_procesada
            orden.fecha_procesamiento = fecha_cobro or date.today()
            self.session.add(orden)

            # Actualizar cuota vinculada
            cuota_r = await self.session.execute(
                select(CuotaAnual).where(CuotaAnual.id == orden.cuota_id)
            )
            cuota = cuota_r.scalars().first()
            if cuota:
                cuota.importe_pagado = cuota.importe_pagado + orden.importe
                if cuota.importe_pagado >= cuota.importe and estado_cuota_cobrada:
                    cuota.estado_id = estado_cuota_cobrada
                cuota.fecha_pago = fecha_cobro or date.today()
                self.session.add(cuota)

            importe_total += orden.importe

        # Marcar remesa como Procesada
        if estado_remesa_procesada:
            remesa.estado_id = estado_remesa_procesada.id
        self.session.add(remesa)

        if importe_total <= Decimal("0.00"):
            await self.session.commit()
            raise ValueError("No hay órdenes pendientes en esta remesa o importe es 0")

        # Crear apunte de caja → dispara asiento si COMPLETA
        apunte = await self.registrar_apunte(
            cuenta_id=cuenta_bancaria_id,
            fecha=fecha_cobro or date.today(),
            importe=importe_total,
            tipo=TipoApunte.INGRESO,
            concepto=f"Liquidación remesa SEPA {remesa.referencia}",
            origen=OrigenApunte.REMESA,
            entidad_origen_tipo="remesa",
            entidad_origen_id=remesa_id,
        )

        registro = RegistroContable(self.session)
        await registro.generar_asiento_para_apunte(apunte)

        return apunte

    async def registrar_pago_cuota_manual(
        self,
        cuota_id: UUID,
        cuenta_bancaria_id: UUID,
        importe: Decimal,
        modo_ingreso: str,
        fecha_pago: Optional[date] = None,
        referencia: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> ApunteCaja:
        """Registra un pago manual de cuota, actualiza el estado de la cuota
        y genera un ApunteCaja de ingreso (+ asiento en modo COMPLETA).
        """
        from ..services.registro_contable import RegistroContable

        cuota_r = await self.session.execute(select(CuotaAnual).where(CuotaAnual.id == cuota_id))
        cuota = cuota_r.scalars().first()
        if not cuota:
            raise ValueError(f"Cuota {cuota_id} no encontrada")

        cuota_est = await self.session.execute(
            select(EstadoCuota).where(EstadoCuota.nombre.in_(["Cobrada", "Pendiente"]))
        )
        cuota_estados = {e.nombre: e.id for e in cuota_est.scalars()}

        cuota.importe_pagado = cuota.importe_pagado + importe
        cuota.modo_ingreso = modo_ingreso
        cuota.fecha_pago = fecha_pago or date.today()
        if cuota.importe_pagado >= cuota.importe:
            estado_cobrada = cuota_estados.get("Cobrada")
            if estado_cobrada:
                cuota.estado_id = estado_cobrada
        if referencia:
            cuota.referencia_pago = referencia
        self.session.add(cuota)

        # Miembro nombre para el concepto
        miembro = cuota.miembro
        nombre_miembro = f"{miembro.nombre} {miembro.apellido1}" if miembro else str(cuota.miembro_id)

        apunte = await self.registrar_apunte(
            cuenta_id=cuenta_bancaria_id,
            fecha=fecha_pago or date.today(),
            importe=importe,
            tipo=TipoApunte.INGRESO,
            concepto=f"Cuota {cuota.ejercicio} - {nombre_miembro}",
            origen=OrigenApunte.CUOTA,
            entidad_origen_tipo="cuota_anual",
            entidad_origen_id=cuota_id,
            referencia_externa=referencia,
            observaciones=observaciones,
        )

        registro = RegistroContable(self.session)
        await registro.generar_asiento_para_apunte(apunte)

        return apunte
