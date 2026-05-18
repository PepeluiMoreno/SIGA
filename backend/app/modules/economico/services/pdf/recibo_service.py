"""Generación de recibos PDF para cuotas y apuntes de caja.

Usa WeasyPrint (HTML→PDF). Requiere: pip install weasyprint
Alternativa ligera: reportlab (incluida en la comparación de dependencias).

La función devuelve bytes del PDF listo para enviar como respuesta HTTP.
"""
import io
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.economico.models.cuotas import CuotaAnual
from app.modules.economico.models.tesoreria import ApunteCaja


# ─── Templates HTML ───────────────────────────────────────────────────────────

_CSS_BASE = """
@page { size: A4; margin: 2cm 2.5cm; }
body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 12pt; color: #333; }
.header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #6d28d9; padding-bottom: 1em; margin-bottom: 1.5em; }
.logo-area h1 { font-size: 20pt; color: #6d28d9; margin: 0; }
.logo-area p { color: #666; font-size: 9pt; margin: 0.2em 0; }
.recibo-num { text-align: right; }
.recibo-num .label { font-size: 9pt; color: #666; text-transform: uppercase; letter-spacing: 1px; }
.recibo-num .num { font-size: 18pt; font-weight: bold; color: #6d28d9; }
.seccion { margin: 1.2em 0; }
.seccion h2 { font-size: 10pt; text-transform: uppercase; letter-spacing: 1px; color: #666; border-bottom: 1px solid #eee; padding-bottom: 0.3em; margin-bottom: 0.6em; }
table { width: 100%; border-collapse: collapse; }
table th { background: #f5f3ff; color: #4c1d95; text-align: left; padding: 8px 10px; font-size: 10pt; }
table td { padding: 8px 10px; border-bottom: 1px solid #f0f0f0; font-size: 11pt; }
.importe-row { background: #f5f3ff; font-weight: bold; font-size: 14pt; }
.importe-row td { color: #4c1d95; padding: 12px 10px; }
.sello { margin-top: 3em; padding: 1em; border: 2px solid #6d28d9; border-radius: 8px; text-align: center; }
.sello p { color: #6d28d9; font-weight: bold; margin: 0; font-size: 11pt; }
.footer { margin-top: 4em; border-top: 1px solid #ddd; padding-top: 1em; font-size: 8pt; color: #999; text-align: center; }
"""


def _html_recibo_cuota(
    numero_recibo: str,
    nombre_organizacion: str,
    cif_organizacion: str,
    direccion_organizacion: str,
    nombre_socio: str,
    nif_socio: Optional[str],
    ejercicio: int,
    importe: Decimal,
    fecha_pago: date,
    concepto: str,
    referencia: Optional[str],
) -> str:
    nif_str = f"NIF: {nif_socio}" if nif_socio else ""
    ref_str = f"<tr><td>Referencia</td><td>{referencia}</td></tr>" if referencia else ""
    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><style>{_CSS_BASE}</style></head>
<body>
  <div class="header">
    <div class="logo-area">
      <h1>{nombre_organizacion}</h1>
      <p>{cif_organizacion}</p>
      <p>{direccion_organizacion}</p>
    </div>
    <div class="recibo-num">
      <div class="label">Recibo nº</div>
      <div class="num">{numero_recibo}</div>
    </div>
  </div>

  <div class="seccion">
    <h2>Datos del socio</h2>
    <table>
      <tr><td><strong>{nombre_socio}</strong></td><td>{nif_str}</td></tr>
    </table>
  </div>

  <div class="seccion">
    <h2>Concepto</h2>
    <table>
      <tr><th>Descripción</th><th>Ejercicio</th><th>Fecha de pago</th></tr>
      <tr>
        <td>{concepto}</td>
        <td>{ejercicio}</td>
        <td>{fecha_pago.strftime('%d/%m/%Y')}</td>
      </tr>
      {ref_str}
      <tr class="importe-row">
        <td colspan="2">TOTAL PAGADO</td>
        <td>{importe:,.2f} €</td>
      </tr>
    </table>
  </div>

  <div class="sello">
    <p>✓ Pago recibido — {fecha_pago.strftime('%d de %B de %Y')}</p>
  </div>

  <div class="footer">
    <p>Este documento es un recibo de pago emitido por {nombre_organizacion}. Consérvelo como justificante.</p>
  </div>
</body>
</html>"""


def _html_recibo_apunte(
    numero_recibo: str,
    nombre_organizacion: str,
    cif_organizacion: str,
    concepto: str,
    tipo: str,
    importe: Decimal,
    fecha: date,
    referencia: Optional[str],
) -> str:
    tipo_label = "INGRESO" if tipo == "INGRESO" else "GASTO"
    color_tipo = "#059669" if tipo == "INGRESO" else "#dc2626"
    ref_str = f"<tr><td>Referencia</td><td>{referencia}</td></tr>" if referencia else ""
    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><style>{_CSS_BASE}</style></head>
<body>
  <div class="header">
    <div class="logo-area">
      <h1>{nombre_organizacion}</h1>
      <p>{cif_organizacion}</p>
    </div>
    <div class="recibo-num">
      <div class="label">Justificante nº</div>
      <div class="num">{numero_recibo}</div>
    </div>
  </div>

  <div class="seccion">
    <h2>Movimiento de tesorería</h2>
    <table>
      <tr><th>Concepto</th><th>Tipo</th><th>Fecha</th></tr>
      <tr>
        <td>{concepto}</td>
        <td style="color:{color_tipo};font-weight:bold;">{tipo_label}</td>
        <td>{fecha.strftime('%d/%m/%Y')}</td>
      </tr>
      {ref_str}
      <tr class="importe-row">
        <td colspan="2">IMPORTE</td>
        <td>{importe:,.2f} €</td>
      </tr>
    </table>
  </div>

  <div class="footer">
    <p>Justificante de movimiento emitido por {nombre_organizacion}.</p>
  </div>
</body>
</html>"""


# ─── Servicio ─────────────────────────────────────────────────────────────────

class ReciboService:
    """Genera PDFs de recibos para cuotas y movimientos de caja."""

    # Estos datos se leerían de la configuración de la organización.
    # Por ahora están hardcodeados; en producción vendrían de
    # app/domains/core/models/configuracion.py.
    ORG_NOMBRE = "Intramuros Jerez"
    ORG_CIF = "G00000000"
    ORG_DIRECCION = "Jerez de la Frontera, Cádiz"

    def __init__(self, session: AsyncSession):
        self.session = session

    def _generar_pdf(self, html: str) -> bytes:
        """Convierte HTML a bytes PDF usando WeasyPrint."""
        try:
            from weasyprint import HTML
            buffer = io.BytesIO()
            HTML(string=html).write_pdf(buffer)
            return buffer.getvalue()
        except ImportError:
            raise RuntimeError(
                "WeasyPrint no está instalado. Ejecuta: pip install weasyprint"
            )

    async def recibo_cuota(self, cuota_id: UUID) -> bytes:
        """Genera el PDF de recibo para una CuotaAnual pagada."""
        result = await self.session.execute(
            select(CuotaAnual).where(CuotaAnual.id == cuota_id)
        )
        cuota = result.scalars().first()
        if not cuota:
            raise ValueError(f"CuotaAnual {cuota_id} no encontrada")

        miembro = cuota.miembro
        nombre_socio = (
            f"{miembro.nombre} {miembro.apellidos}"
            if miembro
            else "Socio desconocido"
        )
        nif_socio = getattr(miembro, 'numero_documento', None) if miembro else None

        numero_recibo = f"REC-{cuota.ejercicio}-{str(cuota_id)[:8].upper()}"
        fecha_pago = cuota.fecha_pago or date.today()

        html = _html_recibo_cuota(
            numero_recibo=numero_recibo,
            nombre_organizacion=self.ORG_NOMBRE,
            cif_organizacion=self.ORG_CIF,
            direccion_organizacion=self.ORG_DIRECCION,
            nombre_socio=nombre_socio,
            nif_socio=nif_socio,
            ejercicio=cuota.ejercicio,
            importe=cuota.importe_pagado or cuota.importe,
            fecha_pago=fecha_pago,
            concepto=f"Cuota de socio — Ejercicio {cuota.ejercicio}",
            referencia=cuota.referencia_pago,
        )
        return self._generar_pdf(html)

    async def recibo_apunte(self, apunte_id: UUID) -> bytes:
        """Genera el PDF de justificante para un ApunteCaja."""
        result = await self.session.execute(
            select(ApunteCaja).where(ApunteCaja.id == apunte_id)
        )
        apunte = result.scalars().first()
        if not apunte:
            raise ValueError(f"ApunteCaja {apunte_id} no encontrado")

        numero_recibo = f"MOV-{apunte.fecha.year}-{str(apunte_id)[:8].upper()}"

        html = _html_recibo_apunte(
            numero_recibo=numero_recibo,
            nombre_organizacion=self.ORG_NOMBRE,
            cif_organizacion=self.ORG_CIF,
            concepto=apunte.concepto,
            tipo=apunte.tipo.value,
            importe=apunte.importe,
            fecha=apunte.fecha,
            referencia=apunte.referencia_externa,
        )
        return self._generar_pdf(html)
