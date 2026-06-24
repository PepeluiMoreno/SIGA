"""Servicio del Flujo 6 — Donaciones.

Implementa el alta, cobro, anulación y emisión de certificado fiscal de
donaciones (Ley 49/2002). Genera automáticamente ApunteCaja + asiento contable
al pasar a COBRADA (D6.2).
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.donaciones import Donacion
from app.modules.configuracion.models.estados import EstadoDonacion


class DonacionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Helpers ─────────────────────────────────────────────────────────────

    async def _estado(self, nombre: str) -> Optional[EstadoDonacion]:
        r = await self.session.execute(
            select(EstadoDonacion).where(EstadoDonacion.nombre == nombre)
        )
        return r.scalars().first()

    async def obtener(self, donacion_id: UUID) -> Optional[Donacion]:
        r = await self.session.execute(
            select(Donacion).where(Donacion.id == donacion_id)
        )
        return r.scalars().first()

    # ── A1 — Registrar ──────────────────────────────────────────────────────

    async def _resolver_contacto_donante(
        self, *, contacto_id: Optional[UUID], donante_nombre: Optional[str],
        donante_dni: Optional[str], donante_email: Optional[str],
        donante_telefono: Optional[str], anonima: bool,
    ) -> Optional[UUID]:
        """Resuelve el donante a un Contacto. Anónima -> None. Con contacto_id ->
        ese. Si no, busca por NIF (numero_documento) y, si no existe y hay datos,
        crea un Contacto PERSONA_FISICA al vuelo."""
        if anonima:
            return None
        if contacto_id:
            return contacto_id
        from app.modules.membresia.models.contacto import Contacto
        nif = (donante_dni or "").strip().upper() or None
        if nif:
            existente = await self.session.scalar(
                select(Contacto).where(
                    func.upper(Contacto.numero_documento) == nif,
                    Contacto.eliminado.is_(False),
                )
            )
            if existente:
                return existente.id
        if not (donante_nombre or nif or donante_email):
            return None  # donación sin datos de donante -> sin contacto
        contacto = Contacto(
            tipo="PERSONA_FISICA",
            nombre=donante_nombre or "Donante",
            numero_documento=nif,
            email=donante_email,
            telefono=donante_telefono,
        )
        self.session.add(contacto)
        await self.session.flush()
        return contacto.id

    async def registrar(
        self,
        importe: Decimal,
        fecha_donacion: date,
        tipo: str = "DINERARIA",
        caracter: str = "PUNTUAL",
        contacto_id: Optional[UUID] = None,
        donante_nombre: Optional[str] = None,
        donante_dni: Optional[str] = None,
        donante_email: Optional[str] = None,
        donante_telefono: Optional[str] = None,
        concepto_id: Optional[UUID] = None,
        campania_id: Optional[UUID] = None,
        modo_ingreso: Optional[str] = None,
        referencia_pago: Optional[str] = None,
        descripcion_especie: Optional[str] = None,
        valoracion: Optional[Decimal] = None,
        documento_valoracion: Optional[str] = None,
        anonima: bool = False,
        observaciones: Optional[str] = None,
        agrupacion_id: Optional[UUID] = None,
        cobrar_inmediato: bool = False,
        cuenta_bancaria_id: Optional[UUID] = None,
    ) -> Donacion:
        """Crea una donación en estado REGISTRADA. Si `cobrar_inmediato=True`
        y se indica cuenta bancaria (o es ESPECIE), también ejecuta A2."""
        if importe <= Decimal("0") and not (tipo == "ESPECIE" and valoracion and valoracion > 0):
            raise ValueError("El importe (o la valoración en especie) debe ser positivo.")

        if tipo == "ESPECIE":
            if not descripcion_especie or not valoracion:
                raise ValueError(
                    "Una donación en especie requiere descripción y valoración."
                )

        est_registrada = await self._estado("REGISTRADA")
        if not est_registrada:
            raise ValueError("Estado 'REGISTRADA' no encontrado en estados_donacion.")

        # El donante es un Contacto. Si no se pasa contacto_id y la donación no es
        # anónima, se busca-o-crea por NIF (decisión: el externo se registra como
        # contacto salvo que se marque anónima).
        contacto_id = await self._resolver_contacto_donante(
            contacto_id=contacto_id, donante_nombre=donante_nombre, donante_dni=donante_dni,
            donante_email=donante_email, donante_telefono=donante_telefono, anonima=anonima,
        )

        donacion = Donacion(
            contacto_id=contacto_id,
            concepto_id=concepto_id,
            campania_id=campania_id,
            tipo=tipo,
            caracter=caracter,
            descripcion_especie=descripcion_especie,
            valoracion=valoracion,
            documento_valoracion=documento_valoracion,
            importe=importe,
            fecha=fecha_donacion,
            modo_ingreso=modo_ingreso,
            referencia_pago=referencia_pago,
            estado_id=est_registrada.id,
            anonima=anonima,
            observaciones=observaciones,
            agrupacion_id=agrupacion_id,
        )
        self.session.add(donacion)
        await self.session.commit()
        await self.session.refresh(donacion)

        if cobrar_inmediato:
            return await self.marcar_cobrada(
                donacion.id,
                cuenta_bancaria_id=cuenta_bancaria_id,
                fecha_cobro=fecha_donacion,
            )

        return donacion

    # ── A2 — Marcar cobrada (D6.2) ──────────────────────────────────────────

    async def marcar_cobrada(
        self,
        donacion_id: UUID,
        cuenta_bancaria_id: Optional[UUID] = None,
        fecha_cobro: Optional[date] = None,
    ) -> Donacion:
        """Pasa REGISTRADA → COBRADA y genera ApunteCaja + asiento (D6.2)."""
        from ..models.tesoreria import ApunteCaja, TipoApunte, OrigenApunte

        donacion = await self.obtener(donacion_id)
        if not donacion:
            raise ValueError(f"Donación {donacion_id} no encontrada")

        if donacion.estado and donacion.estado.nombre == "COBRADA":
            return donacion  # idempotente

        if donacion.estado and donacion.estado.nombre == "ANULADA":
            raise ValueError("No se puede cobrar una donación anulada.")

        # Dineraria requiere cuenta bancaria
        if donacion.tipo == "DINERARIA" and not cuenta_bancaria_id:
            raise ValueError(
                "Para marcar como cobrada una donación dineraria hay que indicar la cuenta bancaria."
            )

        est_cobrada = await self._estado("COBRADA")
        if not est_cobrada:
            raise ValueError("Estado 'COBRADA' no encontrado.")

        f_cobro = fecha_cobro or donacion.fecha or date.today()

        # Dineraria: crear ApunteCaja
        if donacion.tipo == "DINERARIA":
            concepto = f"Donación de {(donacion.contacto.nombre_completo if donacion.contacto else None) or 'donante'}"
            apunte = ApunteCaja(
                cuenta_bancaria_id=cuenta_bancaria_id,
                fecha=f_cobro,
                importe=donacion.importe,
                tipo=TipoApunte.INGRESO,
                origen=OrigenApunte.DONACION,
                concepto=concepto,
                entidad_origen_tipo="donacion",
                entidad_origen_id=donacion.id,
                referencia_externa=donacion.referencia_pago,
            )
            self.session.add(apunte)
            await self.session.flush()
            donacion.apunte_caja_id = apunte.id
            donacion.cuenta_bancaria_id = cuenta_bancaria_id

            # Generar asiento contable vía RegistroContable
            from .registro_contable import RegistroContable
            registro = RegistroContable(self.session)
            asiento = await registro.generar_asiento_para_apunte(apunte)
            if asiento:
                donacion.asiento_id = asiento.id

        # Especie: solo asiento contable (sin ApunteCaja)
        else:
            from .contabilidad_service import ContabilidadService
            from ..models.contabilidad.asiento import TipoAsientoContable
            contab = ContabilidadService(self.session)

            cuenta_haber = await contab.obtener_cuenta_por_codigo("730")
            # Para especie, el DEBE depende del bien — usamos 219 (Otro inmovilizado material) como genérica
            cuenta_debe = await contab.obtener_cuenta_por_codigo("219")
            if cuenta_haber and cuenta_debe:
                glosa = f"Donación en especie — {donacion.descripcion_especie or ''}"[:200]
                asiento = await contab.crear_asiento(
                    ejercicio=f_cobro.year,
                    fecha=f_cobro,
                    glosa=glosa,
                    tipo_asiento=TipoAsientoContable.GESTION,
                )
                await contab.añadir_apunte(
                    asiento_id=asiento.id,
                    cuenta_id=cuenta_debe.id,
                    debe=donacion.valoracion or donacion.importe,
                    concepto=glosa,
                )
                await contab.añadir_apunte(
                    asiento_id=asiento.id,
                    cuenta_id=cuenta_haber.id,
                    haber=donacion.valoracion or donacion.importe,
                    concepto=glosa,
                )
                asiento_confirmado = await contab.confirmar_asiento(asiento.id)
                donacion.asiento_id = asiento_confirmado.id

        donacion.fecha = f_cobro
        donacion.estado_id = est_cobrada.id
        self.session.add(donacion)
        await self.session.commit()
        await self.session.refresh(donacion)
        return donacion

    # ── A4 — Anular ─────────────────────────────────────────────────────────

    async def anular(self, donacion_id: UUID, motivo: Optional[str] = None) -> Donacion:
        """Pasa a ANULADA. Si tenía asiento contable, lo deja en estado ANULADO."""
        from .contabilidad_service import ContabilidadService

        donacion = await self.obtener(donacion_id)
        if not donacion:
            raise ValueError(f"Donación {donacion_id} no encontrada")

        if donacion.estado and donacion.estado.nombre == "ANULADA":
            return donacion

        est_anulada = await self._estado("ANULADA")
        if not est_anulada:
            raise ValueError("Estado 'ANULADA' no encontrado.")

        if donacion.asiento_id:
            contab = ContabilidadService(self.session)
            try:
                await contab.anular_asiento(donacion.asiento_id)
            except Exception:
                pass  # si ya estaba anulado, seguimos

        donacion.estado_id = est_anulada.id
        if motivo:
            obs_prev = donacion.observaciones or ""
            sufijo = f"[{date.today().isoformat()}] ANULADA: {motivo.strip()}"
            donacion.observaciones = f"{obs_prev}\n{sufijo}".strip()
        self.session.add(donacion)
        await self.session.commit()
        await self.session.refresh(donacion)
        return donacion

    # ── A3 — Certificado anual agrupado (D6.3, D6.6) ────────────────────────

    async def listar_certificables_por_ejercicio(self, ejercicio: int) -> list[dict]:
        """Devuelve, por (donante, tipo), el agregado certificable del ejercicio.
        Excluye las anónimas y las que ya tienen `certificado_emitido = true`."""
        est_cobrada = await self._estado("COBRADA")
        if not est_cobrada:
            return []
        q = select(Donacion).where(
            and_(
                Donacion.estado_id == est_cobrada.id,
                Donacion.eliminado.is_(False),
                Donacion.anonima.is_(False),
                Donacion.fecha >= date(ejercicio, 1, 1),
                Donacion.fecha <= date(ejercicio, 12, 31),
            )
        )
        r = await self.session.execute(q)
        donaciones = list(r.scalars().all())

        # Agrupar por (donante_clave, tipo)
        agrupado: dict[tuple, dict] = {}
        for d in donaciones:
            # El donante es un Contacto; NIF y nombre salen de él.
            c = d.contacto
            if not c:
                continue  # sin contacto no es certificable
            nif = (getattr(c, "numero_documento", None) or "").strip().upper() or None
            nombre = c.nombre_completo or ""
            if not nif:
                continue  # no certificable sin NIF
            clave = (nif, d.tipo)
            entry = agrupado.get(clave)
            if not entry:
                entry = {
                    "nif": nif, "nombre": nombre, "tipo": d.tipo,
                    "total": Decimal("0"), "n": 0,
                    "donacion_ids": [],
                    "todas_certificadas": True,
                }
                agrupado[clave] = entry
            valor = d.valoracion if d.tipo == "ESPECIE" else d.importe
            entry["total"] += valor or Decimal("0")
            entry["n"] += 1
            entry["donacion_ids"].append(str(d.id))
            if not d.certificado_emitido:
                entry["todas_certificadas"] = False
        return list(agrupado.values())

    async def emitir_certificado_anual(
        self,
        ejercicio: int,
        nif_donante: str,
        tipo: str,
        organizacion_nombre: str,
        organizacion_nif: str,
    ) -> tuple[str, bytes]:
        """A3 — Emite el certificado anual de un donante para el ejercicio y
        tipo dados (clave A=DINERARIA, B=ESPECIE). Marca las donaciones como
        certificadas y asigna `numero_certificado`. Devuelve (numero, pdf_bytes).
        """
        est_cobrada = await self._estado("COBRADA")
        if not est_cobrada:
            raise ValueError("Estado 'COBRADA' no encontrado.")

        # Donaciones del donante en el ejercicio del tipo indicado
        q = select(Donacion).where(
            and_(
                Donacion.estado_id == est_cobrada.id,
                Donacion.eliminado.is_(False),
                Donacion.anonima.is_(False),
                Donacion.fecha >= date(ejercicio, 1, 1),
                Donacion.fecha <= date(ejercicio, 12, 31),
                Donacion.tipo == tipo,
            )
        )
        r = await self.session.execute(q)
        donaciones = list(r.scalars().all())

        nif_norm = (nif_donante or "").strip().upper()
        donaciones_donante = []
        nombre = ""
        for d in donaciones:
            c = d.contacto
            if not c:
                continue
            nif = (getattr(c, "numero_documento", None) or "").strip().upper() or None
            if nif == nif_norm:
                donaciones_donante.append(d)
                nombre = nombre or (c.nombre_completo or "")

        if not donaciones_donante:
            raise ValueError(
                f"No hay donaciones {tipo} COBRADAS del donante {nif_donante} en {ejercicio}."
            )

        # Generar número correlativo CERT-YYYY-NNNNN
        cnt_r = await self.session.execute(
            select(func.count(Donacion.id)).where(
                Donacion.numero_certificado.like(f"CERT-{ejercicio}-%")
            )
        )
        siguiente = (cnt_r.scalar() or 0) + 1
        numero = f"CERT-{ejercicio}-{siguiente:05d}"

        total = sum(
            (d.valoracion if d.tipo == "ESPECIE" else d.importe) or Decimal("0")
            for d in donaciones_donante
        )

        # Generar PDF
        pdf_bytes = _generar_pdf_certificado(
            numero_certificado=numero,
            ejercicio=ejercicio,
            organizacion_nombre=organizacion_nombre,
            organizacion_nif=organizacion_nif,
            donante_nif=nif_norm,
            donante_nombre=nombre,
            tipo=tipo,
            total=total,
            donaciones=donaciones_donante,
        )

        # Marcar todas las donaciones como certificadas, una de ellas guarda el número
        hoy = date.today()
        for i, d in enumerate(donaciones_donante):
            d.certificado_emitido = True
            d.fecha_certificado = hoy
            if i == 0:
                d.numero_certificado = numero
            self.session.add(d)
        await self.session.commit()

        return numero, pdf_bytes


# ────────────────────────────────────────────────────────────────────────────
# PDF certificado (Ley 49/2002 art. 24) — D6.3
# ────────────────────────────────────────────────────────────────────────────

def _generar_pdf_certificado(
    numero_certificado: str,
    ejercicio: int,
    organizacion_nombre: str,
    organizacion_nif: str,
    donante_nif: str,
    donante_nombre: str,
    tipo: str,
    total,
    donaciones: list[Donacion],
) -> bytes:
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    )
    from reportlab.lib import colors

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2.5 * cm, rightMargin=2.5 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title=f"Certificado de donación {numero_certificado}",
        author=organizacion_nombre,
    )

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=18,
                        alignment=1, textColor=colors.HexColor("#1e3a8a"))
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12,
                        textColor=colors.HexColor("#1e3a8a"), spaceBefore=12)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=11, leading=14)
    small = ParagraphStyle("small", parent=styles["BodyText"], fontSize=9,
                            textColor=colors.HexColor("#475569"))

    elements = []
    elements.append(Paragraph(f"<b>Certificado de donación</b>", h1))
    elements.append(Paragraph(f"Nº {numero_certificado} · Ejercicio {ejercicio}", small))
    elements.append(Spacer(1, 16))

    clave = "A — Donativo dinerario" if tipo == "DINERARIA" else "B — Donativo en especie"
    elements.append(Paragraph(
        f"<b>{organizacion_nombre}</b>, con NIF <b>{organizacion_nif}</b>, "
        f"certifica que ha recibido de <b>{donante_nombre}</b> (NIF <b>{donante_nif}</b>) "
        f"durante el ejercicio fiscal {ejercicio}, donativos por importe total de "
        f"<b>{_fmt_eur(total)}</b> ({clave}).",
        body,
    ))

    elements.append(Paragraph("Detalle de las donaciones del ejercicio", h2))
    data = [["Fecha", "Forma de pago", "Importe"]]
    for d in donaciones:
        data.append([
            d.fecha.isoformat() if d.fecha else "—",
            d.modo_ingreso or "—",
            _fmt_eur(d.valoracion if d.tipo == "ESPECIE" else d.importe),
        ])
    tbl = Table(data, colWidths=[3 * cm, 8 * cm, 4 * cm])
    tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
        ("ALIGN", (-1, 1), (-1, -1), "RIGHT"),
        ("FONTNAME", (-1, 1), (-1, -1), "Courier"),
    ]))
    elements.append(tbl)

    elements.append(Spacer(1, 16))
    elements.append(Paragraph(
        "<i>La entidad está acogida al régimen especial de la Ley 49/2002, de 23 de "
        "diciembre, de régimen fiscal de las entidades sin fines lucrativos y de los "
        "incentivos fiscales al mecenazgo.</i>",
        body,
    ))
    elements.append(Paragraph(
        "<i>La donación es irrevocable, pura y simple, según la legislación vigente.</i>",
        body,
    ))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        f"Emitido el {date.today().strftime('%d/%m/%Y')}",
        small,
    ))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(
        "______________________________<br/>"
        f"Firma y sello de {organizacion_nombre}",
        small,
    ))

    doc.build(elements)
    return buf.getvalue()


def _fmt_eur(v) -> str:
    try:
        return f"{float(v):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return str(v)
