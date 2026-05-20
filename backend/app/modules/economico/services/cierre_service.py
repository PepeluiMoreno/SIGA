"""Servicio de cierre contable y documentos anuales según PCESFL 2013.

Implementa:
- Cálculo de saldos por cuenta del ejercicio
- Balance estructurado según PCESFL (Activo no corriente / Activo corriente /
  Patrimonio Neto / Pasivo no corriente / Pasivo corriente)
- Cuenta de Resultados PCESFL (Excedente del ejercicio, no Beneficio/Pérdida)
- Asiento de regularización: salda cuentas grupo 6 y 7 contra 129
- Asiento de cierre: salda balance completo contra 129
- Asiento de apertura del ejercicio siguiente

Cumplimiento: Ley 50/2002 art. 34; Código de Comercio art. 25.1; PCESFL norma 18ª.
"""

from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.contabilidad import (
    CuentaContable,
    AsientoContable,
    ApunteContable,
    TipoAsientoContable,
    EstadoAsientoContable,
)
from .contabilidad_service import ContabilidadService


# ─── Mapeo PCESFL 2013 ────────────────────────────────────────────────────────

# Códigos de cuenta (prefijos) agrupados por sección del Balance PCESFL
MAPA_BALANCE: Dict[str, Dict[str, Tuple[str, ...]]] = {
    "activo_no_corriente": {
        "I_inmovilizado_intangible": ("200", "201", "202", "203", "204", "205", "206"),
        "II_bienes_patrimonio_historico": ("213", "214"),
        "III_inmovilizado_material": ("210", "211", "212", "215", "216", "217", "218", "219"),
        "IV_inversiones_inmobiliarias": ("220", "221"),
        "V_inversiones_financieras_lp": (
            "240", "241", "242", "243", "244", "245", "246", "247", "248", "249",
            "250", "251", "252", "253", "254", "255", "256", "257", "258", "259",
        ),
    },
    "activo_corriente": {
        "II_existencias": ("300", "301", "302", "310", "320", "330", "350", "390"),
        "III_deudores": (
            "430", "431", "432", "433", "434", "435", "436", "437", "438", "439",
            "440", "441", "446", "447",
            "470", "471", "472",
            "480", "490", "493",
        ),
        "IV_inversiones_financieras_cp": (
            "530", "531", "532", "533", "534", "535", "536", "537", "538", "539",
            "540", "541", "542", "543", "544", "545", "546", "547", "548", "549",
        ),
        "VI_efectivo": ("570", "571", "572", "573", "574", "575", "576", "577"),
    },
    "patrimonio_neto": {
        "I_dotacion_fondo_social": ("100", "101", "102", "103", "104", "105"),
        "II_reservas": ("110", "111", "112", "113", "114", "115", "116", "117", "118", "119"),
        "III_excedentes_ejercicios_anteriores": ("120", "121"),
        "IV_excedente_ejercicio": ("129",),
        "V_subvenciones_donaciones_legados": ("130", "131", "132"),
    },
    "pasivo_no_corriente": {
        "I_provisiones_lp": ("140", "141", "142", "143", "144", "145"),
        "II_deudas_lp": (
            "150", "151", "152", "153", "154", "155", "156", "157", "158", "159",
            "160", "161", "162", "163", "164", "165", "166", "167", "168", "169",
            "170", "171", "172", "173", "174", "175", "176", "177", "178", "179",
            "180", "181", "182", "185",
        ),
    },
    "pasivo_corriente": {
        "II_provisiones_cp": ("499",),
        "III_deudas_cp": (
            "500", "501", "502", "503", "504", "505", "506", "507", "508", "509",
            "510", "511", "512", "513", "514", "515", "516", "517", "518", "519",
            "520", "521", "522", "523", "524", "525", "526", "527", "528", "529",
            "550", "551", "552", "553", "554", "555", "556", "557", "558", "559",
        ),
        "IV_acreedores_comerciales": (
            "400", "401", "402", "403", "404", "405", "406", "407", "408", "409",
            "410", "411", "412", "413", "414", "415", "416", "417", "418", "419",
            "475", "476", "477", "479", "485",
        ),
    },
}

# Códigos de cuenta agrupados por sección de la Cuenta de Resultados PCESFL
MAPA_RESULTADOS: Dict[str, Tuple[str, ...]] = {
    "ingresos_actividad_propia": (
        "721", "722", "723", "724", "725",  # Cuotas socios
        "726", "727", "728",
        "730", "731",                          # Promociones, patrocinios
        "740", "741", "742", "743", "744", "745", "746", "747", "748", "749",  # Subvenciones
        "750", "752", "753", "754", "755",
    ),
    "gastos_actividad_propia": (
        "620", "621", "622", "623", "624", "625", "626", "627", "628", "629",
        "631", "632", "633", "634", "635", "636",
        "640", "641", "642", "643", "644", "649",
        "650", "651", "652", "653", "654", "655", "656", "659",
        "680", "681", "682",
    ),
    "ayudas_monetarias": ("650", "651", "652", "653", "654"),
    "ingresos_mercantil": ("700", "701", "702", "703", "704", "705", "706", "707", "708", "709"),
    "gastos_mercantil": ("600", "601", "602", "606", "607", "608", "609", "610", "611", "612"),
    "ingresos_financieros": (
        "760", "761", "762", "763", "764", "765", "766", "767", "768", "769",
    ),
    "gastos_financieros": (
        "660", "661", "662", "663", "664", "665", "666", "667", "668", "669",
    ),
    "impuesto": ("630", "633"),
}


def _prefijo_codigo(codigo: str) -> str:
    """Devuelve los 3 primeros dígitos del código contable."""
    return (codigo or "")[:3]


class CierreEjercicioService:
    """Servicio para cerrar el ejercicio y generar documentos anuales PCESFL."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.contabilidad = ContabilidadService(session)

    # ── Cálculo de saldos ────────────────────────────────────────────────────

    async def calcular_saldos_cuentas(
        self,
        ejercicio: int,
        fecha_fin: Optional[date] = None,
        incluir_borradores: bool = False,
    ) -> Dict[str, Decimal]:
        """Saldo neto (debe - haber) por código de cuenta del ejercicio.

        Solo cuenta asientos CONFIRMADOS por defecto (incluir_borradores=False).
        """
        q = (
            select(
                CuentaContable.codigo,
                func.coalesce(func.sum(ApunteContable.debe), Decimal("0")).label("debe"),
                func.coalesce(func.sum(ApunteContable.haber), Decimal("0")).label("haber"),
            )
            .join(ApunteContable, CuentaContable.id == ApunteContable.cuenta_id)
            .join(AsientoContable, ApunteContable.asiento_id == AsientoContable.id)
            .where(AsientoContable.ejercicio == ejercicio)
            .group_by(CuentaContable.codigo)
        )
        if not incluir_borradores:
            q = q.where(AsientoContable.estado == EstadoAsientoContable.CONFIRMADO)
        if fecha_fin:
            q = q.where(AsientoContable.fecha <= fecha_fin)

        result = await self.session.execute(q)
        return {
            row.codigo: (row.debe or Decimal("0")) - (row.haber or Decimal("0"))
            for row in result.all()
        }

    # ── Balance PCESFL ───────────────────────────────────────────────────────

    async def calcular_balance_pcesfl(
        self, ejercicio: int, fecha_fin: Optional[date] = None
    ) -> Dict[str, Dict[str, Decimal]]:
        """Balance estructurado según PCESFL 2013.

        Devuelve dict con secciones { 'activo_no_corriente': {...}, ... } y un
        nodo 'totales' con totales por bloque. Activo total debe == Pasivo+PN.
        """
        saldos = await self.calcular_saldos_cuentas(ejercicio, fecha_fin)

        balance: Dict[str, Dict[str, Decimal]] = {}
        for seccion, subsecciones in MAPA_BALANCE.items():
            balance[seccion] = {}
            for subseccion, prefijos in subsecciones.items():
                total = Decimal("0")
                for codigo, saldo in saldos.items():
                    prefijo = _prefijo_codigo(codigo)
                    if prefijo in prefijos:
                        # ACTIVO: saldo positivo (debe > haber); PASIVO/PN: invertimos
                        if seccion.startswith("activo"):
                            total += saldo
                        else:
                            total += -saldo  # pasivo/PN tienen saldo acreedor (haber > debe)
                balance[seccion][subseccion] = total

        # Totales agregados
        balance["totales"] = {
            "total_activo_no_corriente": sum(balance["activo_no_corriente"].values()),
            "total_activo_corriente": sum(balance["activo_corriente"].values()),
            "total_activo": sum(balance["activo_no_corriente"].values())
                + sum(balance["activo_corriente"].values()),
            "total_patrimonio_neto": sum(balance["patrimonio_neto"].values()),
            "total_pasivo_no_corriente": sum(balance["pasivo_no_corriente"].values()),
            "total_pasivo_corriente": sum(balance["pasivo_corriente"].values()),
            "total_pasivo_y_pn": sum(balance["patrimonio_neto"].values())
                + sum(balance["pasivo_no_corriente"].values())
                + sum(balance["pasivo_corriente"].values()),
        }
        balance["totales"]["diferencia"] = (
            balance["totales"]["total_activo"] - balance["totales"]["total_pasivo_y_pn"]
        )
        return balance

    # ── Cuenta de Resultados PCESFL ──────────────────────────────────────────

    async def calcular_cuenta_resultados(
        self, ejercicio: int, fecha_fin: Optional[date] = None
    ) -> Dict[str, Decimal]:
        """Cuenta de Resultados PCESFL (formato Excedente del ejercicio).

        Convención: ingresos son haber > debe (saldo negativo en (debe-haber)),
        los devolvemos como positivos. Gastos son debe > haber → positivos directos.
        """
        saldos = await self.calcular_saldos_cuentas(ejercicio, fecha_fin)

        def sumar(prefijos: Tuple[str, ...], como_ingreso: bool) -> Decimal:
            total = Decimal("0")
            for codigo, saldo in saldos.items():
                if _prefijo_codigo(codigo) in prefijos:
                    total += -saldo if como_ingreso else saldo
            return total

        ingresos_propios = sumar(MAPA_RESULTADOS["ingresos_actividad_propia"], como_ingreso=True)
        gastos_propios = sumar(MAPA_RESULTADOS["gastos_actividad_propia"], como_ingreso=False)
        ingresos_merc = sumar(MAPA_RESULTADOS["ingresos_mercantil"], como_ingreso=True)
        gastos_merc = sumar(MAPA_RESULTADOS["gastos_mercantil"], como_ingreso=False)
        ingresos_fin = sumar(MAPA_RESULTADOS["ingresos_financieros"], como_ingreso=True)
        gastos_fin = sumar(MAPA_RESULTADOS["gastos_financieros"], como_ingreso=False)
        impuesto = sumar(MAPA_RESULTADOS["impuesto"], como_ingreso=False)

        excedente_actividad_propia = ingresos_propios - gastos_propios
        excedente_mercantil = ingresos_merc - gastos_merc
        resultado_financiero = ingresos_fin - gastos_fin
        excedente_antes_impuestos = (
            excedente_actividad_propia + excedente_mercantil + resultado_financiero
        )
        excedente_ejercicio = excedente_antes_impuestos - impuesto

        return {
            "ingresos_actividad_propia": ingresos_propios,
            "gastos_actividad_propia": gastos_propios,
            "excedente_actividad_propia": excedente_actividad_propia,
            "ingresos_mercantil": ingresos_merc,
            "gastos_mercantil": gastos_merc,
            "excedente_mercantil": excedente_mercantil,
            "ingresos_financieros": ingresos_fin,
            "gastos_financieros": gastos_fin,
            "resultado_financiero": resultado_financiero,
            "excedente_antes_impuestos": excedente_antes_impuestos,
            "impuesto_sobre_beneficios": impuesto,
            "excedente_ejercicio": excedente_ejercicio,
        }

    # ── Asiento de regularización ────────────────────────────────────────────

    async def generar_asiento_regularizacion(self, ejercicio: int) -> AsientoContable:
        """Salda cuentas de grupo 6 (gastos) y 7 (ingresos) contra la cta 129.

        Se aplica al final del ejercicio antes del asiento de cierre. Calcula
        el excedente del ejercicio y lo deja en la cuenta 129.

        D9.3: pre-validación bloqueante — todos los asientos del ejercicio deben
        estar en estado CONFIRMADO (sin borradores).
        """
        # D9.3 — Pre-validación: no quedan asientos en BORRADOR del ejercicio
        borradores_r = await self.session.execute(
            select(func.count(AsientoContable.id))
            .where(AsientoContable.ejercicio == ejercicio)
            .where(AsientoContable.estado == EstadoAsientoContable.BORRADOR)
        )
        n_borradores = borradores_r.scalar() or 0
        if n_borradores:
            raise ValueError(
                f"No se puede regularizar el ejercicio {ejercicio}: hay {n_borradores} "
                f"asientos en estado BORRADOR. Confírmalos o anúlalos antes del cierre (D9.3)."
            )

        # Verificar que no exista ya un asiento de regularización
        existe = await self.session.execute(
            select(AsientoContable).where(
                and_(
                    AsientoContable.ejercicio == ejercicio,
                    AsientoContable.tipo_asiento == TipoAsientoContable.REGULARIZACION,
                    AsientoContable.estado != EstadoAsientoContable.ANULADO,
                )
            )
        )
        if existe.scalars().first():
            raise ValueError(
                f"Ya existe un asiento de regularización para el ejercicio {ejercicio}"
            )

        saldos = await self.calcular_saldos_cuentas(ejercicio)

        # Buscar cuenta 129 (excedente del ejercicio)
        cuenta_129 = await self.contabilidad.obtener_cuenta_por_codigo("129")
        if not cuenta_129:
            raise ValueError(
                "Cuenta 129 (Excedente del ejercicio) no existe en el plan de cuentas"
            )

        # Crear asiento de regularización
        asiento = await self.contabilidad.crear_asiento(
            ejercicio=ejercicio,
            fecha=date(ejercicio, 12, 31),
            glosa=f"Regularización de resultados ejercicio {ejercicio}",
            tipo_asiento=TipoAsientoContable.REGULARIZACION,
        )

        total_ingresos = Decimal("0")
        total_gastos = Decimal("0")

        # Para cada cuenta del ejercicio: si es grupo 6 (gasto) o 7 (ingreso)
        for codigo, saldo in saldos.items():
            if saldo == 0:
                continue
            prefijo = _prefijo_codigo(codigo)
            grupo = prefijo[0] if prefijo else ""
            if grupo not in ("6", "7"):
                continue

            cuenta = await self.contabilidad.obtener_cuenta_por_codigo(codigo)
            if not cuenta:
                continue

            if grupo == "7":
                # Cuenta de ingreso (saldo acreedor → saldo negativo en debe-haber)
                # Para saldarla: ponemos en el DEBE el valor absoluto, va al HABER de 129
                importe = abs(saldo)
                if importe == 0:
                    continue
                await self.contabilidad.añadir_apunte(
                    asiento_id=asiento.id,
                    cuenta_id=cuenta.id,
                    debe=importe,
                    concepto=f"Regularización {codigo}",
                )
                total_ingresos += importe
            elif grupo == "6":
                # Cuenta de gasto (saldo deudor → saldo positivo en debe-haber)
                # Para saldarla: ponemos en el HABER el valor absoluto, va al DEBE de 129
                importe = saldo
                if importe == 0:
                    continue
                await self.contabilidad.añadir_apunte(
                    asiento_id=asiento.id,
                    cuenta_id=cuenta.id,
                    haber=importe,
                    concepto=f"Regularización {codigo}",
                )
                total_gastos += importe

        # Apunte de cierre en cuenta 129 con el excedente neto
        excedente = total_ingresos - total_gastos
        if excedente > 0:
            # Beneficio: 129 al haber (saldo acreedor)
            await self.contabilidad.añadir_apunte(
                asiento_id=asiento.id,
                cuenta_id=cuenta_129.id,
                haber=excedente,
                concepto=f"Excedente positivo ejercicio {ejercicio}",
            )
        elif excedente < 0:
            # Pérdida: 129 al debe (saldo deudor)
            await self.contabilidad.añadir_apunte(
                asiento_id=asiento.id,
                cuenta_id=cuenta_129.id,
                debe=abs(excedente),
                concepto=f"Excedente negativo ejercicio {ejercicio}",
            )
        # Si excedente == 0 puede haber sumas iguales — el asiento ya cuadra

        return await self.contabilidad.confirmar_asiento(asiento.id)

    # ── Asiento de cierre ────────────────────────────────────────────────────

    async def generar_asiento_cierre(self, ejercicio: int) -> AsientoContable:
        """Cierra el balance: salda todas las cuentas de activo, pasivo y PN con
        apunte inverso. Tras este asiento todas las cuentas quedan a cero.

        D8.4: la conciliación bancaria del ejercicio debe estar completa. Si hay
        `ApunteCaja` con `conciliado=false` y `fecha` en ese ejercicio, se rechaza
        el cierre con la lista de pendientes.
        """
        # D8.4 — pre-validación bloqueante: conciliación completa
        from ..models.tesoreria import ApunteCaja
        from datetime import date as _date
        pendientes_r = await self.session.execute(
            select(func.count(ApunteCaja.id))
            .where(ApunteCaja.conciliado.is_(False))
            .where(ApunteCaja.fecha >= _date(ejercicio, 1, 1))
            .where(ApunteCaja.fecha <= _date(ejercicio, 12, 31))
        )
        n_pendientes = pendientes_r.scalar() or 0
        if n_pendientes:
            raise ValueError(
                f"No se puede cerrar el ejercicio {ejercicio}: hay {n_pendientes} apuntes "
                f"sin conciliar. Completa la conciliación bancaria antes del cierre (D8.4)."
            )

        existe = await self.session.execute(
            select(AsientoContable).where(
                and_(
                    AsientoContable.ejercicio == ejercicio,
                    AsientoContable.tipo_asiento == TipoAsientoContable.CIERRE,
                    AsientoContable.estado != EstadoAsientoContable.ANULADO,
                )
            )
        )
        if existe.scalars().first():
            raise ValueError(
                f"Ya existe un asiento de cierre para el ejercicio {ejercicio}"
            )

        saldos = await self.calcular_saldos_cuentas(ejercicio)

        asiento = await self.contabilidad.crear_asiento(
            ejercicio=ejercicio,
            fecha=date(ejercicio, 12, 31),
            glosa=f"Asiento de cierre ejercicio {ejercicio}",
            tipo_asiento=TipoAsientoContable.CIERRE,
        )

        for codigo, saldo in saldos.items():
            if saldo == 0:
                continue
            grupo = _prefijo_codigo(codigo)[0] if codigo else ""
            # Solo cuentas de balance (1,2,3,4,5) — las 6 y 7 ya se regularizaron
            if grupo not in ("1", "2", "3", "4", "5"):
                continue

            cuenta = await self.contabilidad.obtener_cuenta_por_codigo(codigo)
            if not cuenta:
                continue

            if saldo > 0:
                # Saldo deudor → al cerrar va al haber
                await self.contabilidad.añadir_apunte(
                    asiento_id=asiento.id,
                    cuenta_id=cuenta.id,
                    haber=saldo,
                    concepto=f"Cierre {codigo}",
                )
            else:
                # Saldo acreedor → al cerrar va al debe
                await self.contabilidad.añadir_apunte(
                    asiento_id=asiento.id,
                    cuenta_id=cuenta.id,
                    debe=abs(saldo),
                    concepto=f"Cierre {codigo}",
                )

        return await self.contabilidad.confirmar_asiento(asiento.id)

    # ── Asiento de apertura ──────────────────────────────────────────────────

    async def generar_asiento_apertura(self, ejercicio_nuevo: int) -> AsientoContable:
        """Reabre el balance del ejercicio nuevo con los saldos del cierre anterior
        invertidos (mismo balance, asiento simétrico)."""
        ejercicio_anterior = ejercicio_nuevo - 1

        # Buscar el asiento de cierre del ejercicio anterior
        cierre_r = await self.session.execute(
            select(AsientoContable)
            .where(
                and_(
                    AsientoContable.ejercicio == ejercicio_anterior,
                    AsientoContable.tipo_asiento == TipoAsientoContable.CIERRE,
                    AsientoContable.estado == EstadoAsientoContable.CONFIRMADO,
                )
            )
            .order_by(AsientoContable.fecha.desc())
        )
        cierre = cierre_r.scalars().first()
        if not cierre:
            raise ValueError(
                f"No hay asiento de cierre confirmado para el ejercicio {ejercicio_anterior}"
            )

        # No duplicar apertura
        apertura_existe = await self.session.execute(
            select(AsientoContable).where(
                and_(
                    AsientoContable.ejercicio == ejercicio_nuevo,
                    AsientoContable.tipo_asiento == TipoAsientoContable.APERTURA,
                    AsientoContable.estado != EstadoAsientoContable.ANULADO,
                )
            )
        )
        if apertura_existe.scalars().first():
            raise ValueError(
                f"Ya existe un asiento de apertura para el ejercicio {ejercicio_nuevo}"
            )

        asiento = await self.contabilidad.crear_asiento(
            ejercicio=ejercicio_nuevo,
            fecha=date(ejercicio_nuevo, 1, 1),
            glosa=f"Asiento de apertura ejercicio {ejercicio_nuevo}",
            tipo_asiento=TipoAsientoContable.APERTURA,
        )

        # Invertir cada apunte del cierre
        for ap in cierre.apuntes:
            await self.contabilidad.añadir_apunte(
                asiento_id=asiento.id,
                cuenta_id=ap.cuenta_id,
                debe=ap.haber,   # invertido
                haber=ap.debe,   # invertido
                concepto=f"Apertura ejercicio {ejercicio_nuevo}",
            )

        return await self.contabilidad.confirmar_asiento(asiento.id)

    # ── Estado del cierre (checklist) ────────────────────────────────────────

    async def verificar_estado_cierre(self, ejercicio: int) -> Dict[str, bool]:
        """Checklist del estado del cierre para la UI."""
        # ¿Hay asientos en BORRADOR del ejercicio?
        borradores_r = await self.session.execute(
            select(func.count(AsientoContable.id)).where(
                and_(
                    AsientoContable.ejercicio == ejercicio,
                    AsientoContable.estado == EstadoAsientoContable.BORRADOR,
                )
            )
        )
        num_borradores = borradores_r.scalar() or 0

        # ¿Balance cuadra?
        sumas_r = await self.session.execute(
            select(
                func.coalesce(func.sum(ApunteContable.debe), Decimal("0")),
                func.coalesce(func.sum(ApunteContable.haber), Decimal("0")),
            )
            .join(AsientoContable, ApunteContable.asiento_id == AsientoContable.id)
            .where(AsientoContable.ejercicio == ejercicio)
            .where(AsientoContable.estado == EstadoAsientoContable.CONFIRMADO)
        )
        sumas = sumas_r.first()
        total_debe = (sumas[0] if sumas else Decimal("0")) or Decimal("0")
        total_haber = (sumas[1] if sumas else Decimal("0")) or Decimal("0")

        # ¿Regularización hecha?
        regul_r = await self.session.execute(
            select(func.count(AsientoContable.id)).where(
                and_(
                    AsientoContable.ejercicio == ejercicio,
                    AsientoContable.tipo_asiento == TipoAsientoContable.REGULARIZACION,
                    AsientoContable.estado == EstadoAsientoContable.CONFIRMADO,
                )
            )
        )

        # ¿Cierre hecho?
        cierre_r = await self.session.execute(
            select(func.count(AsientoContable.id)).where(
                and_(
                    AsientoContable.ejercicio == ejercicio,
                    AsientoContable.tipo_asiento == TipoAsientoContable.CIERRE,
                    AsientoContable.estado == EstadoAsientoContable.CONFIRMADO,
                )
            )
        )

        # ¿Apertura del siguiente?
        apert_r = await self.session.execute(
            select(func.count(AsientoContable.id)).where(
                and_(
                    AsientoContable.ejercicio == ejercicio + 1,
                    AsientoContable.tipo_asiento == TipoAsientoContable.APERTURA,
                    AsientoContable.estado == EstadoAsientoContable.CONFIRMADO,
                )
            )
        )

        # ¿Conciliación bancaria completa? (D8.4 — bloquea el cierre)
        from ..models.tesoreria import ApunteCaja
        from datetime import date as _date
        sinconc_r = await self.session.execute(
            select(func.count(ApunteCaja.id))
            .where(ApunteCaja.conciliado.is_(False))
            .where(ApunteCaja.fecha >= _date(ejercicio, 1, 1))
            .where(ApunteCaja.fecha <= _date(ejercicio, 12, 31))
        )
        num_sin_conciliar = int(sinconc_r.scalar() or 0)

        return {
            "todos_confirmados": num_borradores == 0,
            "num_borradores": int(num_borradores),
            "balance_cuadra": total_debe == total_haber,
            "total_debe": float(total_debe),
            "total_haber": float(total_haber),
            "regularizacion_hecha": (regul_r.scalar() or 0) > 0,
            "cierre_hecho": (cierre_r.scalar() or 0) > 0,
            "apertura_siguiente_hecha": (apert_r.scalar() or 0) > 0,
            "conciliacion_completa": num_sin_conciliar == 0,
            "num_apuntes_sin_conciliar": num_sin_conciliar,
        }
