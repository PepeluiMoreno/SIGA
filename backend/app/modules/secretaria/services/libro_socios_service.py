"""Servicio del Libro de Socios (Ley Orgánica 1/2002).

Genera snapshots con sus conteos y un **PDF descargable** (reportlab) con el listado
de socios a la fecha de corte, ordenado por agrupación → apellidos. El PDF se guarda
en un directorio NO público (`storage/libro_socios/`) porque contiene datos personales;
se descarga vía un endpoint autenticado (ver main.py).
"""

from datetime import date, datetime
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.libro_socios import LibroSociosSnapshot

# Directorio privado (NO montado como estático) para los PDF del Libro de Socios.
_PDF_DIR = Path("storage/libro_socios")


class LibroSociosService:
    """Genera y custodia snapshots del Libro de Socios."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def generar_snapshot(
        self,
        fecha_corte: Optional[date] = None,
        motivo: Optional[str] = None,
        observaciones: Optional[str] = None,
        creado_por_id: Optional[UUID] = None,
    ) -> LibroSociosSnapshot:
        """Genera un snapshot del libro de socios y su PDF descargable."""
        if fecha_corte is None:
            fecha_corte = date.today()

        # El "socio" es una VINCULACIÓN de tipo SOCIO; activa = estado 'activa'.
        from ...membresia.models.vinculacion import Vinculacion
        from ...membresia.models.tipo_vinculacion import TipoVinculacion

        base = (
            select(func.count(Vinculacion.id))
            .join(TipoVinculacion, Vinculacion.tipo_vinculacion_id == TipoVinculacion.id)
            .where(TipoVinculacion.codigo == "SOCIO", Vinculacion.eliminado == False)
        )
        total_historico = (await self.session.execute(base)).scalar() or 0
        total_activos = (
            await self.session.execute(base.where(Vinculacion.estado == "activa"))
        ).scalar() or 0
        total_baja = total_historico - total_activos

        snapshot = LibroSociosSnapshot(
            fecha_corte=fecha_corte,
            fecha_generacion=datetime.utcnow(),
            total_socios_activos=total_activos,
            total_socios_baja=max(total_baja, 0),
            total_socios_historico=total_historico,
            motivo=motivo,
            observaciones=observaciones,
            creado_por_id=creado_por_id,
        )
        self.session.add(snapshot)
        await self.session.commit()
        await self.session.refresh(snapshot)

        # PDF en una operación aparte: si falla, el snapshot (con sus conteos) ya
        # está guardado sin PDF y se hace rollback de la generación.
        try:
            socios = await self._socios_para_libro()
            org_nombre = await self._org_nombre()
            ruta = await self._generar_pdf(snapshot, socios, org_nombre)
            snapshot.ruta_pdf = ruta
            await self.session.commit()
            await self.session.refresh(snapshot)
        except Exception:
            await self.session.rollback()
        return snapshot

    # ── Datos ────────────────────────────────────────────────────────────────

    async def _org_nombre(self) -> str:
        from ...configuracion.models.configuracion import Configuracion
        row = (await self.session.execute(
            select(Configuracion).where(
                Configuracion.grupo == "organizacion",
                Configuracion.clave == "org.nombre",
            )
        )).scalar_one_or_none()
        return (row.get_valor() if row else "") or "La asociación"

    async def _socios_para_libro(self) -> List[dict]:
        """Lista de socios (histórico) ordenada por agrupación → apellidos.

        Selecciona COLUMNAS (no entidades) a propósito: evita el selectin-load de
        relaciones (p.ej. TipoVinculacion) y, por tanto, es robusto frente a desfases
        modelo↔BD de otros campos no usados aquí.
        """
        from ...membresia.models.vinculacion import Vinculacion, Socio
        from ...membresia.models.tipo_vinculacion import TipoVinculacion
        from ...membresia.models.contacto import Contacto
        from ...core.geografico.direccion import UnidadOrganizativa

        unidades = {
            uid: nombre for (uid, nombre) in (await self.session.execute(
                select(UnidadOrganizativa.id, UnidadOrganizativa.nombre)
            )).all()
        }

        rows = (await self.session.execute(
            select(
                Contacto.agrupacion_id, Contacto.razon_social,
                Contacto.apellido1, Contacto.apellido2, Contacto.nombre,
                Contacto.numero_documento, Contacto.cif,
                Vinculacion.fecha_inicio, Vinculacion.fecha_fin, Vinculacion.estado,
                Socio.numero_socio,
            )
            .join(Contacto, Vinculacion.contacto_id == Contacto.id)
            .join(TipoVinculacion, Vinculacion.tipo_vinculacion_id == TipoVinculacion.id)
            .outerjoin(Socio, Socio.vinculacion_id == Vinculacion.id)
            .where(TipoVinculacion.codigo == "SOCIO", Vinculacion.eliminado == False)
        )).all()

        socios = []
        for r in rows:
            nombre = (r.razon_social or
                      " ".join(filter(None, [r.apellido1, r.apellido2, r.nombre])) or
                      r.nombre or "—")
            socios.append({
                "agrupacion": unidades.get(r.agrupacion_id, "(sin agrupación)"),
                "orden": (r.apellido1 or "", r.apellido2 or "", r.nombre or ""),
                "num": r.numero_socio or "",
                "nombre": nombre,
                "nif": (r.numero_documento or r.cif or "") or "—",
                "alta": r.fecha_inicio.strftime("%d/%m/%Y") if r.fecha_inicio else "—",
                "baja": r.fecha_fin.strftime("%d/%m/%Y") if r.fecha_fin else "—",
                "estado": "Activo" if r.estado == "activa" else "Baja",
            })
        socios.sort(key=lambda s: (s["agrupacion"].lower(), s["orden"]))
        return socios

    # ── PDF ──────────────────────────────────────────────────────────────────

    async def _generar_pdf(self, snapshot: LibroSociosSnapshot, socios: List[dict], org_nombre: str) -> str:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

        _PDF_DIR.mkdir(parents=True, exist_ok=True)
        ruta = _PDF_DIR / f"libro_socios_{snapshot.id}.pdf"

        styles = getSampleStyleSheet()
        h1 = ParagraphStyle("h1", parent=styles["Title"], fontSize=16)
        sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#475569"))
        agr = ParagraphStyle("agr", parent=styles["Heading3"], fontSize=11, spaceBefore=10, spaceAfter=2,
                              textColor=colors.HexColor("#1e293b"))

        doc = SimpleDocTemplate(
            str(ruta), pagesize=A4,
            leftMargin=15 * mm, rightMargin=15 * mm, topMargin=15 * mm, bottomMargin=15 * mm,
            title=f"Libro de Socios — {org_nombre}",
        )
        elems = [
            Paragraph(org_nombre, h1),
            Paragraph(
                f"Libro de Socios · Fecha de corte: {snapshot.fecha_corte.strftime('%d/%m/%Y')} · "
                f"Generado: {snapshot.fecha_generacion.strftime('%d/%m/%Y %H:%M')}", sub),
            Paragraph(
                f"Activos: {snapshot.total_socios_activos} · Bajas: {snapshot.total_socios_baja} · "
                f"Histórico: {snapshot.total_socios_historico}", sub),
            Spacer(1, 6 * mm),
        ]

        cabecera = ["Nº", "Nombre", "NIF", "Alta", "Baja", "Estado"]
        anchos = [16 * mm, 70 * mm, 28 * mm, 22 * mm, 22 * mm, 20 * mm]

        # Una tabla por agrupación
        por_agrupacion: dict = {}
        for s in socios:
            por_agrupacion.setdefault(s["agrupacion"], []).append(s)

        def _tabla(filas):
            data = [cabecera] + [[f["num"], f["nombre"], f["nif"], f["alta"], f["baja"], f["estado"]] for f in filas]
            t = Table(data, colWidths=anchos, repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            return t

        if not socios:
            elems.append(Paragraph("No hay socios registrados.", styles["Normal"]))
        else:
            for nombre_agr, filas in por_agrupacion.items():
                elems.append(Paragraph(f"{nombre_agr} ({len(filas)})", agr))
                elems.append(_tabla(filas))

        # Generación síncrona (reportlab no es async); ruta corta, sin bloqueo apreciable.
        doc.build(elems)
        return str(ruta)

    async def listar_snapshots(self) -> List[LibroSociosSnapshot]:
        result = await self.session.execute(
            select(LibroSociosSnapshot)
            .where(LibroSociosSnapshot.eliminado == False)
            .order_by(LibroSociosSnapshot.fecha_corte.desc())
        )
        return list(result.scalars().all())

    async def obtener_ultimo_snapshot(self) -> Optional[LibroSociosSnapshot]:
        result = await self.session.execute(
            select(LibroSociosSnapshot)
            .where(LibroSociosSnapshot.eliminado == False)
            .order_by(LibroSociosSnapshot.fecha_corte.desc())
            .limit(1)
        )
        return result.scalars().first()
