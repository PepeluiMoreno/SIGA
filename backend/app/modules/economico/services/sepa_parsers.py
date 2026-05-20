"""Parsers de los ficheros que el banco devuelve tras enviar una remesa SEPA.

Tipos soportados:

- **pain.002** (Payment Status Report): notifica el estado de cada transacción
  (cobrada, devuelta, rechazada). Para órdenes devueltas incluye el código SEPA
  R-Reason (AM04 fondos insuficientes, MD01 sin mandato, etc.) y la fecha.
- **camt.054** (Bank to Customer Debit/Credit Notification): notifica los
  ingresos/cargos individuales en la cuenta del acreedor con su EndToEndId
  y referencia bancaria. Útil para confirmar cobros exitosos y para reconciliar
  contra el extracto bancario.

Convención de emparejamiento:
- `EndToEndId` = "{referencia_remesa}-{nseq:03d}" (D4.1)
- El parser extrae esa cadena y deja que la capa de servicio (`RemesaService`)
  haga la resolución a `OrdenCobro` real.

No depende de ningún paquete externo: usa `xml.etree.ElementTree` de la stdlib.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional
from xml.etree import ElementTree as ET


# --- Resultados del parseo ----------------------------------------------------


@dataclass
class LineaPain002:
    """Una transacción del fichero pain.002 con su estado y posible rechazo."""
    end_to_end_id: str
    estado: str  # ACCP | ACSC | RJCT | PDNG | …
    es_rechazada: bool
    codigo_rechazo: Optional[str] = None
    motivo_rechazo: Optional[str] = None
    fecha_rechazo: Optional[date] = None


@dataclass
class ResultadoPain002:
    """Conjunto de líneas extraídas de un fichero pain.002."""
    msg_id_original: Optional[str] = None
    fecha_creacion: Optional[date] = None
    lineas: list[LineaPain002] = field(default_factory=list)

    @property
    def rechazadas(self) -> list[LineaPain002]:
        return [l for l in self.lineas if l.es_rechazada]


@dataclass
class LineaCamt054:
    """Una línea de cobro individual del fichero camt.054."""
    end_to_end_id: str
    importe: Decimal
    referencia_bancaria: Optional[str] = None  # AcctSvcrRef
    fecha_valor: Optional[date] = None


@dataclass
class ResultadoCamt054:
    """Resumen de un fichero camt.054: bruto de la entrada y desglose por orden."""
    fecha_liquidacion: Optional[date] = None
    importe_bruto: Decimal = Decimal("0.00")
    moneda: str = "EUR"
    cargos: list[LineaCamt054] = field(default_factory=list)


# --- Utilidades ---------------------------------------------------------------


def _strip_ns(tag: str) -> str:
    """Devuelve el local-name eliminando el namespace `{...}` si existe."""
    if tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def _find(elem: ET.Element, *path: str) -> Optional[ET.Element]:
    """Busca recursivamente la primera coincidencia ignorando namespaces."""
    if not path:
        return elem
    head, *tail = path
    for child in elem:
        if _strip_ns(child.tag) == head:
            if not tail:
                return child
            r = _find(child, *tail)
            if r is not None:
                return r
    return None


def _findall(elem: ET.Element, name: str) -> list[ET.Element]:
    """Devuelve todos los descendientes con ese local-name (cualquier nivel)."""
    out: list[ET.Element] = []
    for child in elem.iter():
        if _strip_ns(child.tag) == name:
            out.append(child)
    return out


def _text(elem: Optional[ET.Element], *path: str) -> Optional[str]:
    if elem is None:
        return None
    n = _find(elem, *path) if path else elem
    if n is None or n.text is None:
        return None
    return n.text.strip() or None


def _parse_date(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    # Acepta YYYY-MM-DD y YYYY-MM-DDTHH:MM:SS…
    try:
        return date.fromisoformat(s[:10])
    except ValueError:
        return None


# --- Pain.002 -----------------------------------------------------------------


def parse_pain002(xml_bytes: bytes) -> ResultadoPain002:
    """Extrae el estado de cada transacción del fichero pain.002.

    Soporta variantes pain.002.001.0x (estructura ISO 20022). Las transacciones
    pueden venir agrupadas en uno o varios `OrgnlPmtInfAndSts` que a su vez
    contienen `TxInfAndSts`. Las rechazadas tienen `TxSts=RJCT` y un nodo
    `StsRsnInf` con el código R (`Cd`) y motivo (`AddtlInf`).
    """
    root = ET.fromstring(xml_bytes)

    grp_hdr = _find(root, "CstmrPmtStsRpt", "GrpHdr") or _find(root, "GrpHdr")
    fecha_creacion = _parse_date(_text(grp_hdr, "CreDtTm")) if grp_hdr is not None else None

    msg_id_original = (
        _text(root, "OrgnlGrpInfAndSts", "OrgnlMsgId")
        or _text(root, "CstmrPmtStsRpt", "OrgnlGrpInfAndSts", "OrgnlMsgId")
    )

    lineas: list[LineaPain002] = []
    for tx in _findall(root, "TxInfAndSts"):
        end_to_end = _text(tx, "OrgnlEndToEndId")
        estado = _text(tx, "TxSts") or "PDNG"
        es_rechazada = estado.upper() == "RJCT"
        codigo = None
        motivo = None
        sts_rsn = _find(tx, "StsRsnInf")
        if sts_rsn is not None:
            rsn = _find(sts_rsn, "Rsn")
            if rsn is not None:
                codigo = _text(rsn, "Cd") or _text(rsn, "Prtry")
            motivo = _text(sts_rsn, "AddtlInf")
        fecha_r = _parse_date(_text(tx, "AccptncDtTm"))

        if not end_to_end:
            continue
        lineas.append(LineaPain002(
            end_to_end_id=end_to_end,
            estado=estado,
            es_rechazada=es_rechazada,
            codigo_rechazo=codigo,
            motivo_rechazo=motivo,
            fecha_rechazo=fecha_r,
        ))

    return ResultadoPain002(
        msg_id_original=msg_id_original,
        fecha_creacion=fecha_creacion,
        lineas=lineas,
    )


# --- camt.054 -----------------------------------------------------------------


def parse_camt054(xml_bytes: bytes) -> ResultadoCamt054:
    """Extrae los cargos individuales y el bruto de un fichero camt.054.

    Estructura ISO 20022: `BkToCstmrDbtCdtNtfctn / Ntfctn / Ntry`. Cada `Ntry`
    es un movimiento bancario (puede ser el ingreso bruto del lote). El detalle
    por orden está en `NtryDtls/TxDtls/Refs/EndToEndId` con su `Amt`.
    """
    root = ET.fromstring(xml_bytes)

    fecha_liq = None
    importe_bruto = Decimal("0.00")
    moneda = "EUR"

    # Tomamos el primer Ntry como el ingreso bruto del lote
    primer_ntry = _find(root, "BkToCstmrDbtCdtNtfctn", "Ntfctn", "Ntry") or _find(root, "Ntry")
    if primer_ntry is not None:
        # Fecha valor
        val_dt = _find(primer_ntry, "ValDt", "Dt") or _find(primer_ntry, "BookgDt", "Dt")
        if val_dt is not None and val_dt.text:
            fecha_liq = _parse_date(val_dt.text)
        amt = _find(primer_ntry, "Amt")
        if amt is not None and amt.text:
            try:
                importe_bruto = Decimal(amt.text)
            except (ValueError, ArithmeticError):
                pass
            moneda = amt.attrib.get("Ccy", "EUR")

    cargos: list[LineaCamt054] = []
    for tx in _findall(root, "TxDtls"):
        end_to_end = _text(tx, "Refs", "EndToEndId")
        ref_bancaria = _text(tx, "Refs", "AcctSvcrRef")
        amt_el = _find(tx, "Amt") or _find(tx, "AmtDtls", "InstdAmt", "Amt")
        if not end_to_end or amt_el is None or not amt_el.text:
            continue
        try:
            importe = Decimal(amt_el.text)
        except (ValueError, ArithmeticError):
            continue
        cargos.append(LineaCamt054(
            end_to_end_id=end_to_end,
            importe=importe,
            referencia_bancaria=ref_bancaria,
            fecha_valor=fecha_liq,
        ))

    return ResultadoCamt054(
        fecha_liquidacion=fecha_liq,
        importe_bruto=importe_bruto,
        moneda=moneda,
        cargos=cargos,
    )


# --- Códigos SEPA (R-Reasons EPC131-08) ---------------------------------------

# Subconjunto operativo más frecuente. Usado por el frontend para mostrar
# texto legible y por el servicio para decidir si una orden es re-presentable.
CODIGOS_SEPA_REASONS: dict[str, dict] = {
    "AM04": {"motivo": "Fondos insuficientes",                    "representable": True},
    "AC04": {"motivo": "Cuenta cerrada",                          "representable": False},
    "AC01": {"motivo": "Formato de cuenta incorrecto",            "representable": False},
    "AC06": {"motivo": "Cuenta bloqueada",                        "representable": False},
    "AC13": {"motivo": "Deudor no autorizado (cuenta consumidor)", "representable": False},
    "MD01": {"motivo": "Mandato no válido o inexistente",         "representable": False},
    "MD02": {"motivo": "Información del mandato incorrecta",      "representable": False},
    "MD07": {"motivo": "Cliente fallecido",                       "representable": False},
    "MS02": {"motivo": "Solicitud de devolución por el deudor",   "representable": False},
    "MS03": {"motivo": "Motivo no especificado",                  "representable": True},
    "RC01": {"motivo": "BIC del banco deudor incorrecto",         "representable": False},
    "RR01": {"motivo": "Identificación deudor no proporcionada",  "representable": False},
}


def es_representable(codigo: str) -> bool:
    """¿Una orden fallida con este código se puede reenviar en otra remesa?"""
    return CODIGOS_SEPA_REASONS.get((codigo or "").upper(), {}).get("representable", False)


def motivo_sepa(codigo: str) -> str:
    """Texto legible del código R; cadena vacía si desconocido."""
    return CODIGOS_SEPA_REASONS.get((codigo or "").upper(), {}).get("motivo", "")
