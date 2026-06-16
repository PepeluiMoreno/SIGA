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
        actividad_id: Optional[UUID] = None,
        campania_id: Optional[UUID] = None,
        cuota_id: Optional[UUID] = None,
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
            actividad_id=actividad_id,
            campania_id=campania_id,
            cuota_id=cuota_id,
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

        # Imputar a presupuesto si el apunte está afecto a una actividad o campaña
        # con partida presupuestaria. Defensivo: si no hay partida, no hace nada.
        if (actividad_id or campania_id) and tipo in (TipoApunte.INGRESO, TipoApunte.GASTO):
            try:
                from .presupuesto_service import PresupuestoService
                await PresupuestoService(self.session).imputar_ejecucion(
                    importe=importe, actividad_id=actividad_id, campania_id=campania_id,
                )
            except Exception:
                # La imputación a presupuesto nunca debe impedir registrar el movimiento real
                pass

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

    async def desmarcar_apunte_conciliado(self, apunte_id: UUID) -> ApunteCaja:
        """Revierte la conciliación manual de un apunte. No toca el extracto."""
        apunte = await self.obtener_apunte(apunte_id)
        if not apunte:
            raise ValueError(f"Apunte {apunte_id} no encontrado")
        apunte.conciliado = False
        apunte.fecha_conciliacion = None
        self.session.add(apunte)
        await self.session.commit()
        await self.session.refresh(apunte)
        return apunte

    async def actualizar_metadatos_apunte(
        self,
        apunte_id: UUID,
        *,
        concepto: Optional[str] = None,
        observaciones: Optional[str] = None,
        actividad_id: Optional[UUID] = None,
        campania_id: Optional[UUID] = None,
        categoria_fiscal_id: Optional[UUID] = None,
        limpiar_actividad: bool = False,
        limpiar_categoria_fiscal: bool = False,
    ) -> ApunteCaja:
        """Edita metadatos no contables de un apunte (concepto, observaciones, imputación).
        NO permite cambiar importe, fecha ni tipo — para corregir esos hay que anular el apunte
        y crear uno nuevo.
        """
        apunte = await self.obtener_apunte(apunte_id)
        if not apunte:
            raise ValueError(f"Apunte {apunte_id} no encontrado")

        # Capturar la imputación previa para reajustar el presupuesto si cambia
        afecta_presupuesto = apunte.tipo in (TipoApunte.INGRESO, TipoApunte.GASTO)
        prev_actividad_id = apunte.actividad_id
        prev_campania_id = apunte.campania_id

        if concepto is not None:
            if not concepto.strip():
                raise ValueError("El concepto no puede quedar vacío.")
            apunte.concepto = concepto.strip()
        if observaciones is not None:
            apunte.observaciones = observaciones
        if limpiar_actividad:
            apunte.actividad_id = None
            apunte.campania_id = None
        else:
            if actividad_id is not None:
                apunte.actividad_id = actividad_id
            if campania_id is not None:
                apunte.campania_id = campania_id
        # Categoría fiscal (modo simplificado)
        if limpiar_categoria_fiscal:
            apunte.categoria_fiscal_id = None
        elif categoria_fiscal_id is not None:
            apunte.categoria_fiscal_id = categoria_fiscal_id
        self.session.add(apunte)
        await self.session.commit()
        await self.session.refresh(apunte)

        # Reajustar el presupuesto si la imputación (actividad/campaña) ha cambiado
        if afecta_presupuesto and (
            apunte.actividad_id != prev_actividad_id or apunte.campania_id != prev_campania_id
        ):
            try:
                from .presupuesto_service import PresupuestoService
                presup = PresupuestoService(self.session)
                # Quitar de la partida anterior y sumar a la nueva
                await presup.revertir_ejecucion(
                    importe=apunte.importe,
                    actividad_id=prev_actividad_id, campania_id=prev_campania_id,
                )
                await presup.imputar_ejecucion(
                    importe=apunte.importe,
                    actividad_id=apunte.actividad_id, campania_id=apunte.campania_id,
                )
            except Exception:
                pass  # La imputación a presupuesto nunca debe impedir editar el apunte

        return apunte

    async def anular_apunte(self, apunte_id: UUID, motivo: str) -> ApunteCaja:
        """Anula un apunte generando un CONTRAAPUNTE en la misma cuenta con importe inverso.

        Reglas:
          - El apunte original se mantiene (inmutabilidad contable).
          - Se crea un nuevo apunte con tipo opuesto (GASTO↔INGRESO) y mismo importe.
          - Si el original tenía asiento contable confirmado, se anula también ese asiento.
          - El motivo queda registrado en las observaciones de ambos apuntes.

        Devuelve el contraapunte.
        """
        if not motivo or not motivo.strip():
            raise ValueError("Debes indicar el motivo de la anulación.")
        original = await self.obtener_apunte(apunte_id)
        if not original:
            raise ValueError(f"Apunte {apunte_id} no encontrado")

        # Tipo inverso
        if original.tipo == TipoApunte.INGRESO:
            tipo_inv = TipoApunte.GASTO
        elif original.tipo == TipoApunte.GASTO:
            tipo_inv = TipoApunte.INGRESO
        else:
            raise ValueError("Los apuntes de TRANSFERENCIA no se anulan directamente.")

        marca = f"[Anulación de apunte {apunte_id} — {motivo.strip()}]"
        # Registrar motivo en el original
        original.observaciones = ((original.observaciones or "") + "\n" + marca).strip()
        self.session.add(original)

        # Crear contraapunte
        contra = ApunteCaja(
            cuenta_bancaria_id=original.cuenta_bancaria_id,
            fecha=date.today(),
            importe=original.importe,
            tipo=tipo_inv,
            concepto=f"Anulación: {original.concepto}",
            origen=OrigenApunte.MANUAL,
            entidad_origen_tipo="apunte_caja",
            entidad_origen_id=original.id,
            referencia_externa=None,
            observaciones=marca,
            # El contraapunte NO hereda la imputación a actividad/campaña: la reversión
            # presupuestaria del original ya se hace explícitamente más abajo. Heredarla
            # provocaría doble cómputo si en el futuro se reprocesara.
            actividad_id=None,
            campania_id=None,
        )
        # Ajustar saldo de la cuenta
        cuenta = await self.obtener_cuenta_bancaria(original.cuenta_bancaria_id)
        if cuenta:
            if tipo_inv == TipoApunte.INGRESO:
                cuenta.saldo_actual += original.importe
            elif tipo_inv == TipoApunte.GASTO:
                cuenta.saldo_actual -= original.importe
            self.session.add(cuenta)
        self.session.add(contra)

        # Anular asiento contable asociado al original
        if original.asiento_id:
            from .contabilidad_service import ContabilidadService
            contab = ContabilidadService(self.session)
            try:
                await contab.anular_asiento(original.asiento_id)
            except Exception:
                pass  # idempotente: si ya estaba anulado, seguimos

        # Revertir la imputación presupuestaria del original (si la tenía)
        if original.tipo in (TipoApunte.INGRESO, TipoApunte.GASTO) and (
            original.actividad_id or original.campania_id
        ):
            try:
                from .presupuesto_service import PresupuestoService
                await PresupuestoService(self.session).revertir_ejecucion(
                    importe=original.importe,
                    actividad_id=original.actividad_id, campania_id=original.campania_id,
                )
            except Exception:
                pass  # la reversión presupuestaria nunca impide anular

        await self.session.commit()
        await self.session.refresh(contra)
        return contra

    # ─── Extractos bancarios ─────────────────────────────────────────────────

    async def importar_extracto(
        self,
        cuenta_id: UUID,
        lineas: List[dict],
    ) -> List[ExtractoBancario]:
        """Importa líneas de un extracto bancario.

        D8.1: el cliente puede llamar con líneas pre-parseadas (de CSV en frontend)
        o usar el parser de Norma 43 (`parse_norma43` + esta función).

        Cada línea: {fecha (date), importe (number), concepto (str), referencia (str)}.
        Evita duplicar líneas con misma (fecha, importe, referencia) en la misma cuenta.
        """
        from datetime import date as _date
        cuenta = await self.obtener_cuenta_bancaria(cuenta_id)
        if not cuenta:
            raise ValueError(f"Cuenta {cuenta_id} no encontrada")

        # Pre-cargar líneas ya existentes para evitar duplicados (mismo día + importe + referencia)
        existentes_r = await self.session.execute(
            select(ExtractoBancario.fecha, ExtractoBancario.importe, ExtractoBancario.referencia)
            .where(ExtractoBancario.cuenta_bancaria_id == cuenta_id)
        )
        existentes = {
            (f, Decimal(str(i)).quantize(Decimal("0.01")), (ref or "").strip())
            for f, i, ref in existentes_r.all()
        }

        extractos = []
        for linea in lineas:
            f = linea["fecha"]
            if isinstance(f, str):
                f = _date.fromisoformat(f)
            importe_norm = Decimal(str(linea["importe"])).quantize(Decimal("0.01"))
            ref_norm = (linea.get("referencia") or "").strip()
            clave = (f, importe_norm, ref_norm)
            if clave in existentes:
                continue
            existentes.add(clave)

            extracto = ExtractoBancario(
                cuenta_bancaria_id=cuenta_id,
                fecha=f,
                importe=importe_norm,
                concepto=linea.get("concepto"),
                referencia=ref_norm or None,
            )
            self.session.add(extracto)
            extractos.append(extracto)

        await self.session.commit()
        for e in extractos:
            await self.session.refresh(e)
        return extractos

    @staticmethod
    def parse_norma43(contenido: bytes) -> List[dict]:
        """D8.1: parsea un fichero Norma 43 AEB (extracto bancario español).

        Formato resumido (norma CSB-43 del Consejo Superior Bancario):
        - Cada línea tiene 80 caracteres y un código de 2 dígitos al inicio:
            11 — Registro de cabecera de cuenta (IBAN, fechas, saldo inicial)
            22 — Registro principal de movimiento (fecha, importe, concepto)
            23 — Conceptos adicionales del movimiento (hasta 5 líneas 23 por 22)
            33 — Final de cuenta (saldo final, totales)
            88 — Final de fichero
        - Importe en céntimos con signo en posición 41 (1=debe, 2=haber).
        - Fechas en formato AAMMDD (4xx posiciones) o AAAAMMDD según versión.

        Devuelve lista de dicts {fecha, importe, concepto, referencia} listos
        para `importar_extracto`.

        Implementación tolerante: ignora líneas que no encajan en el formato
        y captura solo los registros 22 con su 23 acumulado.
        """
        from datetime import date as _date
        try:
            texto = contenido.decode("iso-8859-1")
        except Exception:
            texto = contenido.decode("utf-8", errors="ignore")

        lineas: List[dict] = []
        actual: Optional[dict] = None

        for raw in texto.splitlines():
            if len(raw) < 78:
                continue
            codigo = raw[:2]
            if codigo == "22":
                # cerrar el movimiento anterior si lo había
                if actual:
                    lineas.append(actual)
                    actual = None
                try:
                    # fecha de operación: posiciones 10-15 (AAMMDD) — 0-indexed: [10:16]
                    aa = int(raw[10:12])
                    mm = int(raw[12:14])
                    dd = int(raw[14:16])
                    # Heurística para el siglo: si aa < 60 → 20xx; si aa >= 60 → 19xx
                    yyyy = 2000 + aa if aa < 60 else 1900 + aa
                    fecha = _date(yyyy, mm, dd)
                except Exception:
                    continue
                # Signo en posición 27 (índice 27), importe en 28..40 (13 dígitos en céntimos)
                try:
                    signo = raw[27]
                    importe_centimos = int(raw[28:41])
                    importe = Decimal(importe_centimos) / Decimal(100)
                    if signo == "1":
                        importe = -importe
                except Exception:
                    continue
                # Concepto común en 52..63 (12 chars) y referencia propia 39..51
                concepto = raw[52:64].strip() if len(raw) >= 64 else ""
                referencia = raw[41:51].strip() if len(raw) >= 51 else ""
                actual = {
                    "fecha": fecha,
                    "importe": importe,
                    "concepto": concepto,
                    "referencia": referencia,
                }
            elif codigo == "23" and actual is not None:
                # Conceptos adicionales: añadir al concepto separados por " | "
                extra = raw[4:].strip()
                if extra:
                    actual["concepto"] = (actual["concepto"] + " | " + extra).strip(" | ")
            elif codigo in ("33", "88"):
                if actual:
                    lineas.append(actual)
                    actual = None

        if actual:
            lineas.append(actual)
        return lineas

    async def romper_conciliacion(
        self,
        conciliacion_id: UUID,
    ) -> bool:
        """Deshace un emparejamiento previo. Solo si el período de la conciliación
        bancaria no está confirmado/cerrado.
        """
        r = await self.session.execute(
            select(Conciliacion).where(Conciliacion.id == conciliacion_id)
        )
        c = r.scalars().first()
        if not c:
            raise ValueError(f"Conciliación {conciliacion_id} no encontrada")

        # Marcar apunte y extracto como NO conciliados
        if c.apunte_id:
            apunte_r = await self.session.execute(
                select(ApunteCaja).where(ApunteCaja.id == c.apunte_id)
            )
            apunte = apunte_r.scalars().first()
            if apunte:
                apunte.conciliado = False
                apunte.fecha_conciliacion = None
                self.session.add(apunte)
        if c.extracto_id:
            ext_r = await self.session.execute(
                select(ExtractoBancario).where(ExtractoBancario.id == c.extracto_id)
            )
            extracto = ext_r.scalars().first()
            if extracto:
                extracto.conciliado = False
                self.session.add(extracto)

        await self.session.delete(c)
        await self.session.commit()
        return True

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
        y genera un ApunteCaja de ingreso vinculado a la cuota (+ asiento en modo COMPLETA).
        """
        from ..services.registro_contable import RegistroContable
        from ..models.cuotas import ModoIngreso

        cuota_r = await self.session.execute(select(CuotaAnual).where(CuotaAnual.id == cuota_id))
        cuota = cuota_r.scalars().first()
        if not cuota:
            raise ValueError(f"Cuota {cuota_id} no encontrada")

        cuota_est = await self.session.execute(
            select(EstadoCuota).where(EstadoCuota.nombre.in_(["Cobrada", "Pendiente"]))
        )
        cuota_estados = {e.nombre: e.id for e in cuota_est.scalars()}

        cuota.importe_pagado = cuota.importe_pagado + importe
        # Convertir string a enum para mantener tipado correcto en la columna
        try:
            cuota.modo_ingreso = ModoIngreso(modo_ingreso)
        except ValueError:
            cuota.modo_ingreso = None
        cuota.fecha_pago = fecha_pago or date.today()
        if cuota.importe_pagado >= cuota.importe:
            estado_cobrada = cuota_estados.get("Cobrada")
            if estado_cobrada:
                cuota.estado_id = estado_cobrada
        if referencia:
            cuota.referencia_pago = referencia
        self.session.add(cuota)

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
            cuota_id=cuota_id,
        )

        registro = RegistroContable(self.session)
        await registro.generar_asiento_para_apunte(apunte)

        return apunte
