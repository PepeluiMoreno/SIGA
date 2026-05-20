"""Servicio del Flujo 11 — Modelo 182 (AEAT, declaración de donaciones).

Genera el agregado anual de donantes con su NIF, el fichero AEAT en formato
posicional (Orden HAC/146/2024) y el PDF resumen. Registra las presentaciones
para trazabilidad.
"""

import re
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.donaciones import Donacion
from ..models.modelo_182 import Presentacion182
from ..models.cobro import EstadoPago


# Patrón para inferir si un NIF es persona física o jurídica (D11.2)
# PF: empieza por dígito (DNI) o por K/L/M (residentes); también X/Y/Z (NIE)
# PJ: empieza por letra de organización (A/B/C/D/E/F/G/H/J/N/P/Q/R/S/U/V/W)
_NIF_PJ = set("ABCDEFGHJNPQRSUVW")
_NIF_PF_PREFIX = set("KLMXYZ")


def inferir_tipo_donante(nif: Optional[str]) -> Optional[int]:
    """D11.2: devuelve 1 (PF) o 2 (PJ). None si el NIF no encaja."""
    if not nif:
        return None
    nif_n = nif.strip().upper().replace(" ", "").replace("-", "")
    if not nif_n:
        return None
    primero = nif_n[0]
    if primero.isdigit():
        return 1  # DNI numérico → PF
    if primero in _NIF_PF_PREFIX:
        return 1  # NIE o residente → PF
    if primero in _NIF_PJ:
        return 2  # CIF → PJ
    return None  # no encaja


def _normalizar_nif(nif: str) -> str:
    return (nif or "").strip().upper().replace(" ", "").replace("-", "")


class Modelo182Service:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── A1 — Agregado por donante ───────────────────────────────────────────

    async def generar_agregado(self, ejercicio: int) -> dict:
        """Calcula el agregado anual de donaciones por (donante, clave) para el ejercicio.

        Aplica D11.1 (solo donaciones con NIF identificable y no anónimas).
        Aplica D11.2 (PF/PJ derivado del NIF; descarta NIFs no clasificables).
        Aplica D11.4 (claves A/B por tipo de donación):
          - **A** — Donativo dinerario (`Donacion.tipo = DINERARIA`).
          - **B** — Donativo en especie (`Donacion.tipo = ESPECIE`, usa `valoracion`).
        Un donante que aporta dinero Y especie genera DOS líneas en el modelo.
        """
        # Donaciones del ejercicio, no eliminadas, no anónimas
        q = select(Donacion).where(
            and_(
                Donacion.eliminado.is_(False),
                Donacion.fecha >= date(ejercicio, 1, 1),
                Donacion.fecha <= date(ejercicio, 12, 31),
                Donacion.anonima.is_(False),
            )
        )
        r = await self.session.execute(q)
        donaciones = list(r.scalars().all())

        # Construir agregado: clave (NIF, clave_aeat) → {nombre, importe, tipo, clave}
        agregado: dict[tuple[str, str], dict] = {}
        excluidos: list[dict] = []

        # Para resolver NIFs y nombres de miembros, cargamos diccionario
        # de miembros referenciados
        miembro_ids = {d.miembro_id for d in donaciones if d.miembro_id}
        miembros = {}
        if miembro_ids:
            from app.modules.membresia.models.miembro import Miembro
            mr = await self.session.execute(
                select(Miembro).where(Miembro.id.in_(miembro_ids))
            )
            miembros = {m.id: m for m in mr.scalars().all()}

        for d in donaciones:
            # Resolver NIF y nombre del donante
            nif_raw: Optional[str] = None
            nombre: Optional[str] = None
            if d.miembro_id and d.miembro_id in miembros:
                m = miembros[d.miembro_id]
                nif_raw = getattr(m, "numero_documento", None)
                nombre = f"{m.apellido1 or ''} {m.apellido2 or ''} {m.nombre or ''}".strip()
            if not nif_raw:
                nif_raw = d.donante_dni
                nombre = nombre or d.donante_nombre

            nif = _normalizar_nif(nif_raw or "")
            if not nif:
                excluidos.append({
                    "donacion_id": str(d.id),
                    "importe": float(d.importe),
                    "fecha": d.fecha.isoformat() if d.fecha else None,
                    "motivo": "Sin NIF (donante anónimo o sin datos fiscales)",
                })
                continue

            tipo = inferir_tipo_donante(nif)
            if tipo is None:
                excluidos.append({
                    "donacion_id": str(d.id),
                    "importe": float(d.importe),
                    "fecha": d.fecha.isoformat() if d.fecha else None,
                    "nif": nif,
                    "motivo": f"NIF '{nif}' con formato no reconocido",
                })
                continue

            # D11.4: clave AEAT según tipo de donación
            clave = "B" if (d.tipo or "DINERARIA") == "ESPECIE" else "A"
            # En especie usar la valoración (no el importe, que puede ser 0)
            valor = d.valoracion if clave == "B" else d.importe
            if valor is None or valor <= 0:
                excluidos.append({
                    "donacion_id": str(d.id),
                    "importe": float(d.importe),
                    "fecha": d.fecha.isoformat() if d.fecha else None,
                    "nif": nif,
                    "motivo": (
                        "Donación en especie sin valoración"
                        if clave == "B" else "Importe nulo"
                    ),
                })
                continue

            key = (nif, clave)
            entry = agregado.get(key)
            if entry is None:
                entry = {
                    "nif": nif,
                    "nombre": (nombre or "")[:80],
                    "tipo": tipo,
                    "clave": clave,
                    "importe": Decimal("0.00"),
                    "n_donaciones": 0,
                }
                agregado[key] = entry
            entry["importe"] += Decimal(str(valor))
            entry["n_donaciones"] += 1

        incluidos = sorted(agregado.values(), key=lambda x: (x["nif"], x["clave"]))
        importe_total = sum(e["importe"] for e in incluidos)

        return {
            "ejercicio": ejercicio,
            "n_incluidos": len(incluidos),
            "n_excluidos": len(excluidos),
            "importe_total": float(importe_total),
            "incluidos": [
                {**e, "importe": float(e["importe"])} for e in incluidos
            ],
            "excluidos": excluidos,
        }

    # ── A2 — Fichero AEAT (TXT 250 chars) ───────────────────────────────────

    async def generar_fichero_aeat(
        self,
        ejercicio: int,
        declarante_nif: str,
        declarante_nombre: str,
    ) -> bytes:
        """Genera el fichero del Modelo 182 en formato AEAT (texto posicional,
        ISO-8859-1, registros de 250 caracteres terminados en CRLF).

        Estructura simplificada:
        - Registro tipo 1 (cabecera) — datos del declarante y totales.
        - Registro tipo 2 (perceptores) — uno por donante.

        Nota: el formato real tiene más campos. Esta implementación cubre los
        campos esenciales para presentación; ajustar a la última orden ministerial
        antes de uso en producción.
        """
        ag = await self.generar_agregado(ejercicio)
        incluidos = ag["incluidos"]

        lineas: list[str] = []

        # Cabecera (tipo 1): 250 chars
        # Posiciones (esquemáticas): 1=tipo, 2-4=modelo "182", 5-8=ejercicio,
        # 9-17=NIF declarante, 18-57=nombre (40 chars), ...
        def _pad(s: str, n: int) -> str:
            return (s or "")[:n].ljust(n)

        def _pad_num(n, width: int) -> str:
            return str(int(round(n))).rjust(width, "0")

        cabecera = (
            "1"
            + "182"
            + str(ejercicio).rjust(4, "0")
            + _pad(declarante_nif, 9)
            + _pad(declarante_nombre.upper(), 40)
            + _pad_num(len(incluidos), 9)            # nº perceptores
            + _pad_num(int(round(ag["importe_total"] * 100)), 13)  # importe total en céntimos
            + " " * (250 - (1 + 3 + 4 + 9 + 40 + 9 + 13))
        )
        lineas.append(cabecera)

        # Perceptores (tipo 2): uno por (donante, clave). D11.4: claves A/B.
        for e in incluidos:
            importe_centimos = int(round(float(e["importe"]) * 100))
            clave = (e.get("clave") or "A")  # A = dineraria, B = especie
            linea = (
                "2"
                + "182"
                + str(ejercicio).rjust(4, "0")
                + _pad(declarante_nif, 9)
                + _pad(e["nif"], 9)
                + _pad((e["nombre"] or "").upper(), 40)
                + str(e["tipo"])                       # 1 = PF, 2 = PJ
                + _pad_num(importe_centimos, 13)
                + clave                                # A o B (1 char)
                + " " * (250 - (1 + 3 + 4 + 9 + 9 + 40 + 1 + 13 + 1))
            )
            lineas.append(linea)

        contenido = ("\r\n".join(lineas) + "\r\n").encode("iso-8859-1", errors="replace")
        return contenido

    # ── A3 — PDF resumen ────────────────────────────────────────────────────

    async def generar_pdf_resumen(
        self,
        ejercicio: int,
        organizacion_nombre: str = "Organización",
    ) -> bytes:
        """Genera el PDF resumen con totales por donante y excluidos."""
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
        )
        from reportlab.lib import colors

        ag = await self.generar_agregado(ejercicio)

        buf = BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            leftMargin=2 * cm, rightMargin=2 * cm,
            topMargin=2 * cm, bottomMargin=2 * cm,
            title=f"Modelo 182 — Resumen {ejercicio}",
            author=organizacion_nombre,
        )

        styles = getSampleStyleSheet()
        h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=16,
                            textColor=colors.HexColor("#1e3a8a"))
        h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12,
                            textColor=colors.HexColor("#1e3a8a"), spaceBefore=14)
        body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=10)

        elements = []
        elements.append(Paragraph(f"<b>Modelo 182 — Ejercicio {ejercicio}</b>", h1))
        elements.append(Paragraph(organizacion_nombre, body))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(
            f"Donantes incluibles: <b>{ag['n_incluidos']}</b><br/>"
            f"Donaciones excluidas: <b>{ag['n_excluidos']}</b><br/>"
            f"Importe total declarable: <b>{_fmt_eur(ag['importe_total'])}</b>",
            body,
        ))

        elements.append(Paragraph("Donantes incluidos", h2))
        if ag["incluidos"]:
            data = [["NIF", "Nombre", "Tipo", "Clave", "Donaciones", "Importe"]]
            for e in ag["incluidos"]:
                data.append([
                    e["nif"],
                    (e["nombre"] or "")[:32],
                    "PF" if e["tipo"] == 1 else "PJ",
                    e.get("clave") or "A",
                    str(e["n_donaciones"]),
                    _fmt_eur(e["importe"]),
                ])
            tbl = Table(data, colWidths=[2.5 * cm, 5.5 * cm, 1.2 * cm, 1.3 * cm, 2 * cm, 3 * cm])
            tbl.setStyle(TableStyle([
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
                ("ALIGN", (-1, 1), (-1, -1), "RIGHT"),
                ("ALIGN", (-2, 1), (-2, -1), "RIGHT"),
                ("FONTNAME", (-1, 1), (-1, -1), "Courier"),
            ]))
            elements.append(tbl)
        else:
            elements.append(Paragraph("<i>Ningún donante incluible.</i>", body))

        if ag["excluidos"]:
            elements.append(Paragraph("Donaciones excluidas", h2))
            data = [["Fecha", "Importe", "Motivo"]]
            for x in ag["excluidos"]:
                data.append([
                    x.get("fecha", "—"),
                    _fmt_eur(x.get("importe", 0)),
                    x.get("motivo", ""),
                ])
            tbl = Table(data, colWidths=[2.5 * cm, 3 * cm, 9.5 * cm])
            tbl.setStyle(TableStyle([
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#b91c1c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#fca5a5")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#fee2e2")),
            ]))
            elements.append(tbl)

        doc.build(elements)
        return buf.getvalue()

    # ── A4 — Registrar presentación ─────────────────────────────────────────

    async def registrar_presentacion(
        self,
        ejercicio: int,
        fecha_envio: date,
        codigo_aeat: Optional[str] = None,
        archivo_acuse: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> Presentacion182:
        """Registra la presentación del Modelo 182 a la AEAT con su acuse.
        D11.4: una sola presentación por ejercicio (constraint UNIQUE).
        """
        existente = await self.obtener_presentacion(ejercicio)
        if existente:
            raise ValueError(
                f"Ya existe una presentación del Modelo 182 para el ejercicio {ejercicio} "
                f"(fecha envío: {existente.fecha_envio})."
            )

        ag = await self.generar_agregado(ejercicio)
        pres = Presentacion182(
            ejercicio=ejercicio,
            fecha_envio=fecha_envio,
            codigo_aeat=codigo_aeat,
            n_donantes=ag["n_incluidos"],
            importe_total=Decimal(str(ag["importe_total"])),
            archivo_acuse=archivo_acuse,
            observaciones=observaciones,
        )
        self.session.add(pres)
        await self.session.commit()
        await self.session.refresh(pres)
        return pres

    async def obtener_presentacion(self, ejercicio: int) -> Optional[Presentacion182]:
        r = await self.session.execute(
            select(Presentacion182).where(Presentacion182.ejercicio == ejercicio)
        )
        return r.scalars().first()

    async def listar_presentaciones(self) -> list[Presentacion182]:
        r = await self.session.execute(
            select(Presentacion182).order_by(Presentacion182.ejercicio.desc())
        )
        return list(r.scalars().all())


def _fmt_eur(v) -> str:
    try:
        return f"{float(v):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return str(v)
