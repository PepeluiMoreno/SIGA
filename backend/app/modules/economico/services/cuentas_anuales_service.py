"""Servicio para el flujo 10 — Cuentas Anuales.

Genera un snapshot de las CCAA del ejercicio cerrado, permite editar la
Memoria mientras está en BORRADOR, y avanza por los estados BORRADOR →
APROBADAS (por junta) → DEPOSITADAS (ante registro).
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.cuentas_anuales import CuentasAnuales, memoria_vacia, APARTADOS_MEMORIA
from ..models.contabilidad.asiento import AsientoContable, TipoAsientoContable, EstadoAsientoContable
from .cierre_service import CierreEjercicioService


class CuentasAnualesService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def obtener(self, ccaa_id: UUID) -> Optional[CuentasAnuales]:
        r = await self.session.execute(
            select(CuentasAnuales).where(CuentasAnuales.id == ccaa_id)
        )
        return r.scalars().first()

    async def obtener_por_ejercicio(self, ejercicio: int) -> Optional[CuentasAnuales]:
        r = await self.session.execute(
            select(CuentasAnuales).where(CuentasAnuales.ejercicio == ejercicio)
        )
        return r.scalars().first()

    async def listar(self) -> list[CuentasAnuales]:
        r = await self.session.execute(
            select(CuentasAnuales).order_by(CuentasAnuales.ejercicio.desc())
        )
        return list(r.scalars().all())

    # ── A1 — Generar CCAA del ejercicio ─────────────────────────────────────

    async def generar(self, ejercicio: int) -> CuentasAnuales:
        """Crea las CCAA del ejercicio en BORRADOR con snapshot de balance y
        cuenta de resultados calculados desde la contabilidad cerrada.

        Pre-condición: el ejercicio debe tener un asiento de CIERRE confirmado.
        """
        # No duplicar si ya existen
        existente = await self.obtener_por_ejercicio(ejercicio)
        if existente:
            raise ValueError(
                f"Ya existen Cuentas Anuales del ejercicio {ejercicio} "
                f"(estado: {existente.estado})."
            )

        # Pre-condición: el ejercicio debe estar cerrado contablemente
        cierre_r = await self.session.execute(
            select(AsientoContable).where(
                and_(
                    AsientoContable.ejercicio == ejercicio,
                    AsientoContable.tipo_asiento == TipoAsientoContable.CIERRE,
                    AsientoContable.estado == EstadoAsientoContable.CONFIRMADO,
                )
            )
        )
        if not cierre_r.scalars().first():
            raise ValueError(
                f"No se pueden generar Cuentas Anuales: el ejercicio {ejercicio} no está cerrado. "
                f"Completa primero el flujo 9 (Cierre de ejercicio)."
            )

        # Calcular snapshots
        cierre = CierreEjercicioService(self.session)
        balance = await cierre.calcular_balance_pcesfl(ejercicio)
        resultados = await cierre.calcular_cuenta_resultados(ejercicio)
        excedente = Decimal(str(resultados.get("excedente_ejercicio", 0)))

        ccaa = CuentasAnuales(
            ejercicio=ejercicio,
            estado="BORRADOR",
            balance_pcesfl=_decimals_a_float(balance),
            cuenta_resultados=_decimals_a_float(resultados),
            memoria=memoria_vacia(),
            excedente=excedente,
        )
        self.session.add(ccaa)
        await self.session.commit()
        await self.session.refresh(ccaa)
        return ccaa

    # ── A2 — Editar Memoria ─────────────────────────────────────────────────

    async def actualizar_memoria(
        self, ccaa_id: UUID, apartado: str, texto: str
    ) -> CuentasAnuales:
        """Actualiza un apartado de la Memoria. Solo permitido en BORRADOR."""
        ccaa = await self.obtener(ccaa_id)
        if not ccaa:
            raise ValueError(f"CCAA {ccaa_id} no encontradas")
        if not ccaa.es_borrador:
            raise ValueError(
                f"No se puede editar la Memoria en estado {ccaa.estado}. "
                f"Solo se permite en BORRADOR."
            )
        claves_validas = {k for k, _ in APARTADOS_MEMORIA}
        if apartado not in claves_validas:
            raise ValueError(
                f"Apartado '{apartado}' no válido. Use apartado_1 .. apartado_12."
            )
        memoria = dict(ccaa.memoria or {})
        memoria[apartado] = texto
        ccaa.memoria = memoria
        self.session.add(ccaa)
        await self.session.commit()
        await self.session.refresh(ccaa)
        return ccaa

    # ── A3 — Aprobar por junta ──────────────────────────────────────────────

    async def aprobar(
        self,
        ccaa_id: UUID,
        aprobado_por_id: UUID,
        acta_referencia: str,
        fecha_aprobacion: Optional[date] = None,
    ) -> CuentasAnuales:
        """Pasa BORRADOR → APROBADAS. Requiere referencia al acta de junta."""
        ccaa = await self.obtener(ccaa_id)
        if not ccaa:
            raise ValueError(f"CCAA {ccaa_id} no encontradas")
        if not ccaa.es_borrador:
            raise ValueError(
                f"Solo se pueden aprobar CCAA en estado BORRADOR (estado actual: {ccaa.estado})."
            )
        if not acta_referencia or not acta_referencia.strip():
            raise ValueError("Se requiere la referencia al acta de la junta que aprueba.")
        ccaa.estado = "APROBADAS"
        ccaa.aprobado_por_id = aprobado_por_id
        ccaa.fecha_aprobacion = fecha_aprobacion or date.today()
        ccaa.acta_referencia = acta_referencia.strip()
        self.session.add(ccaa)
        await self.session.commit()
        await self.session.refresh(ccaa)
        return ccaa

    # ── A4 — Marcar depositadas ─────────────────────────────────────────────

    async def marcar_depositadas(
        self,
        ccaa_id: UUID,
        fecha_deposito: Optional[date] = None,
        archivo_acuse_recibo: Optional[str] = None,
    ) -> CuentasAnuales:
        """Pasa APROBADAS → DEPOSITADAS con fecha y acuse de recibo del registro."""
        ccaa = await self.obtener(ccaa_id)
        if not ccaa:
            raise ValueError(f"CCAA {ccaa_id} no encontradas")
        if not ccaa.es_aprobada:
            raise ValueError(
                f"Solo se pueden depositar CCAA en estado APROBADAS (estado actual: {ccaa.estado})."
            )
        ccaa.estado = "DEPOSITADAS"
        ccaa.fecha_deposito = fecha_deposito or date.today()
        if archivo_acuse_recibo:
            ccaa.archivo_acuse_recibo = archivo_acuse_recibo
        self.session.add(ccaa)
        await self.session.commit()
        await self.session.refresh(ccaa)
        return ccaa

    # ── A6 — Reabrir (excepcional) ──────────────────────────────────────────

    async def reabrir(self, ccaa_id: UUID, motivo: str) -> CuentasAnuales:
        """Devuelve las CCAA a BORRADOR. Solo usar en casos excepcionales (errores
        materiales detectados antes o después del depósito).
        """
        ccaa = await self.obtener(ccaa_id)
        if not ccaa:
            raise ValueError(f"CCAA {ccaa_id} no encontradas")
        if ccaa.es_borrador:
            raise ValueError("Las CCAA ya están en BORRADOR.")
        if not motivo or not motivo.strip():
            raise ValueError("La reapertura requiere un motivo justificado.")
        obs_prev = ccaa.observaciones or ""
        sufijo = f"[{date.today().isoformat()}] Reapertura desde {ccaa.estado}: {motivo.strip()}"
        ccaa.observaciones = f"{obs_prev}\n{sufijo}".strip()
        ccaa.estado = "BORRADOR"
        # Limpiar firmas posteriores
        ccaa.fecha_deposito = None
        ccaa.archivo_acuse_recibo = None
        self.session.add(ccaa)
        await self.session.commit()
        await self.session.refresh(ccaa)
        return ccaa


def _decimals_a_float(d):
    """Convierte recursivamente Decimal a float para serializar a JSON."""
    if isinstance(d, dict):
        return {k: _decimals_a_float(v) for k, v in d.items()}
    if isinstance(d, list):
        return [_decimals_a_float(x) for x in d]
    if isinstance(d, Decimal):
        return float(d)
    return d


# ────────────────────────────────────────────────────────────────────────────
# Exportación PDF (D10.4) — usa reportlab
# ────────────────────────────────────────────────────────────────────────────

def generar_pdf_ccaa(ccaa: CuentasAnuales, organizacion_nombre: str = "Organización") -> bytes:
    """Genera el PDF de las Cuentas Anuales con reportlab. A4, varias páginas."""
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    )
    from reportlab.lib import colors

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title=f"Cuentas Anuales {ccaa.ejercicio}",
        author=organizacion_nombre,
    )

    styles = getSampleStyleSheet()
    style_h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=18,
                              textColor=colors.HexColor("#1e3a8a"), spaceAfter=12)
    style_h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=13,
                              textColor=colors.HexColor("#1e3a8a"), spaceBefore=14, spaceAfter=6)
    style_h3 = ParagraphStyle("h3", parent=styles["Heading3"], fontSize=11,
                              textColor=colors.HexColor("#475569"), spaceBefore=10, spaceAfter=4)
    style_body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=10, leading=13)
    style_small = ParagraphStyle("small", parent=styles["BodyText"], fontSize=9,
                                 textColor=colors.HexColor("#64748b"))

    elements = []

    # Portada
    elements.append(Paragraph(f"<b>Cuentas Anuales — Ejercicio {ccaa.ejercicio}</b>", style_h1))
    elements.append(Paragraph(organizacion_nombre, style_body))
    elements.append(Spacer(1, 12))
    info_rows = [
        ["Estado", ccaa.estado],
        ["Excedente del ejercicio", f"{float(ccaa.excedente or 0):.2f} €"],
    ]
    if ccaa.fecha_aprobacion:
        info_rows.append(["Fecha de aprobación", ccaa.fecha_aprobacion.isoformat()])
    if ccaa.acta_referencia:
        info_rows.append(["Acta de junta", ccaa.acta_referencia])
    if ccaa.fecha_deposito:
        info_rows.append(["Fecha de depósito", ccaa.fecha_deposito.isoformat()])
    tbl = Table(info_rows, colWidths=[5 * cm, 11 * cm])
    tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(tbl)

    # Balance
    elements.append(PageBreak())
    elements.append(Paragraph("1. Balance PCESFL", style_h2))
    _add_dict_as_table(elements, ccaa.balance_pcesfl or {}, style_h3, style_body)

    # Cuenta de Resultados
    elements.append(PageBreak())
    elements.append(Paragraph("2. Cuenta de Resultados (Excedente)", style_h2))
    _add_dict_as_table(elements, ccaa.cuenta_resultados or {}, style_h3, style_body)

    # Memoria
    elements.append(PageBreak())
    elements.append(Paragraph("3. Memoria económica (12 apartados PCESFL)", style_h2))
    from ..models.cuentas_anuales import APARTADOS_MEMORIA
    memoria = ccaa.memoria or {}
    for i, (clave, titulo) in enumerate(APARTADOS_MEMORIA, start=1):
        elements.append(Paragraph(f"<b>{i}. {titulo}</b>", style_h3))
        texto = (memoria.get(clave) or "").strip()
        if not texto:
            elements.append(Paragraph("<i>(Sin contenido)</i>", style_small))
        else:
            for parrafo in texto.split("\n"):
                if parrafo.strip():
                    elements.append(Paragraph(_escape_xml(parrafo), style_body))
                else:
                    elements.append(Spacer(1, 4))
        elements.append(Spacer(1, 8))

    doc.build(elements)
    return buf.getvalue()


def _add_dict_as_table(elements, datos: dict, style_h3, style_body):
    """Auxiliar: vuelca un dict (con valores numéricos o subdicts) como tabla."""
    from reportlab.platypus import Paragraph, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    rows = []
    _flatten_dict(datos, "", rows)
    if not rows:
        elements.append(Paragraph("<i>Sin datos</i>", style_body))
        return
    tbl = Table([["Concepto", "Importe"]] + rows, colWidths=[12 * cm, 4 * cm])
    tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
        ("FONTNAME", (1, 1), (1, -1), "Courier"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(tbl)


def _flatten_dict(d, prefix, rows):
    """Aplana un dict anidado en filas [concepto, valor]."""
    if not isinstance(d, dict):
        rows.append([prefix or "(valor)", _fmt_num(d)])
        return
    for k, v in d.items():
        key = _humanizar(k)
        full = f"{prefix} · {key}" if prefix else key
        if isinstance(v, dict):
            _flatten_dict(v, full, rows)
        else:
            rows.append([full, _fmt_num(v)])


def _humanizar(clave):
    return clave.replace("_", " ").capitalize()


def _fmt_num(v):
    try:
        return f"{float(v):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return str(v)


def _escape_xml(s):
    """Escapa caracteres reservados para los párrafos de reportlab."""
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;"))
