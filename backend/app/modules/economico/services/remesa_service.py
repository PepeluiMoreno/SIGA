"""Servicio de generación y gestión de remesas SEPA.

Flujo principal:
  1. generar_remesa()     → crea Remesa en estado Borrador + OrdenCobro por cada cuota pendiente
  2. generar_xml_sepa()   → produce el Pain.008.003.02 listo para enviar al banco
  3. marcar_enviada()     → cambia estado a Enviada (archivo guardado)
  4. liquidar_remesa()    → TesoreriaService.liquidar_remesa() (ApunteCaja + asiento)
"""
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4
from xml.etree.ElementTree import Element, SubElement, tostring
import re
import uuid as uuid_module

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.remesas import Remesa, OrdenCobro
from ..models.cuotas import CuotaAnual
from app.modules.configuracion.models.estados import EstadoCuota, EstadoRemesa, EstadoOrdenCobro
from app.modules.membresia.models.miembro import Miembro


class RemesaService:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Generar remesa ────────────────────────────────────────────────────────

    async def generar_remesa(
        self,
        ejercicio: int,
        fecha_cobro: date,
        agrupacion_id: Optional[UUID] = None,
        observaciones: Optional[str] = None,
    ) -> Remesa:
        """Crea una remesa en estado Borrador con las cuotas pendientes del ejercicio.

        Si agrupacion_id es None, incluye cuotas de toda la organización.
        Si agrupacion_id está presente, solo las cuotas de esa agrupación (tesorería delegada).
        """
        # Estado Pendiente de cuotas
        est_pend = await self._estado_cuota("Pendiente")
        est_rem_borrador = await self._estado_remesa("Borrador")
        est_oc_pendiente = await self._estado_orden_cobro("Pendiente")

        if not est_rem_borrador or not est_oc_pendiente:
            raise ValueError("Estados de remesa/orden no encontrados en BD")

        # Cuotas pendientes del ejercicio
        q = select(CuotaAnual).where(
            CuotaAnual.ejercicio == ejercicio,
        )
        if est_pend:
            q = q.where(CuotaAnual.estado_id == est_pend.id)
        if agrupacion_id:
            q = q.where(CuotaAnual.agrupacion_id == agrupacion_id)

        # Solo cuotas con modo SEPA o sin modo especificado (incluir todas las pendientes)
        result = await self.session.execute(q)
        cuotas = list(result.scalars().all())

        if not cuotas:
            raise ValueError(
                f"No hay cuotas pendientes para el ejercicio {ejercicio}"
                + (f" en la agrupación indicada" if agrupacion_id else "")
            )

        # Calcular importe total (importe - importe_pagado)
        importe_total = sum(c.importe - c.importe_pagado for c in cuotas)

        # Referencia única
        ts = date.today().strftime("%Y-%m-%dT%H-%M-%S")
        referencia = f"SEPA_ISO20022CORE_{ts}.xml"

        remesa = Remesa(
            referencia=referencia,
            mensaje_id=referencia.replace(".xml", ""),
            fecha_creacion=date.today(),
            fecha_cobro=fecha_cobro,
            importe_total=importe_total,
            gastos=Decimal("0.00"),
            num_ordenes=len(cuotas),
            estado_id=est_rem_borrador.id,
            agrupacion_id=agrupacion_id,
            observaciones=observaciones,
        )
        self.session.add(remesa)
        await self.session.flush()  # necesitamos remesa.id para las órdenes

        for cuota in cuotas:
            importe_orden = cuota.importe - cuota.importe_pagado
            mandato = f"MAND-{str(cuota.miembro_id)[:8].upper()}"

            # Intentar obtener IBAN del miembro
            miembro = cuota.miembro
            iban = None
            if miembro and hasattr(miembro, 'iban'):
                iban = miembro.iban

            orden = OrdenCobro(
                remesa_id=remesa.id,
                cuota_id=cuota.id,
                importe=importe_orden,
                referencia_mandato=mandato,
                iban=iban,
                estado_id=est_oc_pendiente.id,
            )
            self.session.add(orden)

        await self.session.commit()
        await self.session.refresh(remesa)
        return remesa

    # ── Generar XML SEPA Pain.008.003.02 ─────────────────────────────────────

    async def generar_xml_sepa(
        self,
        remesa_id: UUID,
        creditor_name: str,
        creditor_iban: str,
        creditor_bic: str,
        creditor_id: str,  # identificador acreedor SEPA (AT-02)
    ) -> bytes:
        """Genera el XML SEPA Direct Debit (Pain.008.003.02)."""
        result = await self.session.execute(
            select(Remesa).where(Remesa.id == remesa_id)
        )
        remesa = result.scalars().first()
        if not remesa:
            raise ValueError(f"Remesa {remesa_id} no encontrada")

        root = Element("Document", attrib={
            "xmlns": "urn:iso:std:iso:20022:tech:xsd:pain.008.003.02",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        })
        cstmr = SubElement(root, "CstmrDrctDbtInitn")

        # Group Header
        grp_hdr = SubElement(cstmr, "GrpHdr")
        SubElement(grp_hdr, "MsgId").text = remesa.mensaje_id or str(remesa.id)[:35]
        SubElement(grp_hdr, "CreDtTm").text = f"{date.today().isoformat()}T00:00:00"
        SubElement(grp_hdr, "NbOfTxs").text = str(remesa.num_ordenes)
        SubElement(grp_hdr, "CtrlSum").text = str(remesa.importe_total)
        init_pty = SubElement(grp_hdr, "InitgPty")
        SubElement(init_pty, "Nm").text = creditor_name[:70]

        # Payment Information block
        pmt_inf = SubElement(cstmr, "PmtInf")
        SubElement(pmt_inf, "PmtInfId").text = (remesa.mensaje_id or str(remesa.id))[:35]
        SubElement(pmt_inf, "PmtMtd").text = "DD"
        SubElement(pmt_inf, "NbOfTxs").text = str(remesa.num_ordenes)
        SubElement(pmt_inf, "CtrlSum").text = str(remesa.importe_total)

        pmt_tp_inf = SubElement(pmt_inf, "PmtTpInf")
        svc_lvl = SubElement(pmt_tp_inf, "SvcLvl")
        SubElement(svc_lvl, "Cd").text = "SEPA"
        lcl_instrm = SubElement(pmt_tp_inf, "LclInstrm")
        SubElement(lcl_instrm, "Cd").text = "CORE"
        SubElement(pmt_tp_inf, "SeqTp").text = "RCUR"

        SubElement(pmt_inf, "ReqdColltnDt").text = remesa.fecha_cobro.isoformat()

        # Creditor
        cdtr = SubElement(pmt_inf, "Cdtr")
        SubElement(cdtr, "Nm").text = creditor_name[:70]
        cdtr_acct = SubElement(pmt_inf, "CdtrAcct")
        cdtr_id_elem = SubElement(cdtr_acct, "Id")
        SubElement(cdtr_id_elem, "IBAN").text = re.sub(r"\s", "", creditor_iban)
        cdtr_agt = SubElement(pmt_inf, "CdtrAgt")
        fin_instn_id = SubElement(cdtr_agt, "FinInstnId")
        SubElement(fin_instn_id, "BIC").text = creditor_bic

        cdtr_schme = SubElement(pmt_inf, "CdtrSchmeId")
        cdtr_schme_id = SubElement(cdtr_schme, "Id")
        prvt_id = SubElement(cdtr_schme_id, "PrvtId")
        othr = SubElement(prvt_id, "Othr")
        SubElement(othr, "Id").text = creditor_id
        schme_nm = SubElement(othr, "SchmeNm")
        SubElement(schme_nm, "Prtry").text = "SEPA"

        # Transactions
        for orden in remesa.ordenes:
            drct_dbt_tx_inf = SubElement(pmt_inf, "DrctDbtTxInf")

            pmt_id = SubElement(drct_dbt_tx_inf, "PmtId")
            SubElement(pmt_id, "EndToEndId").text = str(orden.id)[:35]

            instd_amt = SubElement(drct_dbt_tx_inf, "InstdAmt", attrib={"Ccy": "EUR"})
            instd_amt.text = f"{orden.importe:.2f}"

            drct_dbt_tx = SubElement(drct_dbt_tx_inf, "DrctDbtTx")
            mndtn_rltd_inf = SubElement(drct_dbt_tx, "MndtRltdInf")
            SubElement(mndtn_rltd_inf, "MndtId").text = (orden.referencia_mandato or str(orden.id)[:35])
            SubElement(mndtn_rltd_inf, "DtOfSgntr").text = "2010-01-01"

            if orden.iban:
                dbtr_agt = SubElement(drct_dbt_tx_inf, "DbtrAgt")
                fi = SubElement(dbtr_agt, "FinInstnId")
                SubElement(fi, "Othr").text = "NOTPROVIDED"

                dbtr = SubElement(drct_dbt_tx_inf, "Dbtr")
                cuota = orden.cuota
                if cuota and cuota.miembro:
                    m = cuota.miembro
                    nombre = f"{m.nombre or ''} {m.apellido1 or ''}".strip()[:70]
                    SubElement(dbtr, "Nm").text = nombre or "DESCONOCIDO"
                else:
                    SubElement(dbtr, "Nm").text = "DESCONOCIDO"

                dbtr_acct = SubElement(drct_dbt_tx_inf, "DbtrAcct")
                dbtr_acct_id = SubElement(dbtr_acct, "Id")
                SubElement(dbtr_acct_id, "IBAN").text = re.sub(r"\s", "", orden.iban)

            purp = SubElement(drct_dbt_tx_inf, "Purp")
            SubElement(purp, "Cd").text = "OTHR"

            ustrd_rmt = SubElement(drct_dbt_tx_inf, "RmtInf")
            cuota = orden.cuota
            ejercicio = cuota.ejercicio if cuota else "?"
            SubElement(ustrd_rmt, "Ustrd").text = f"Cuota {ejercicio}"

        xml_bytes = b'<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(root, encoding="unicode").encode("utf-8")
        return xml_bytes

    async def marcar_enviada(self, remesa_id: UUID, archivo: Optional[str] = None) -> Remesa:
        estado_enviada = await self._estado_remesa("Enviada")
        result = await self.session.execute(select(Remesa).where(Remesa.id == remesa_id))
        remesa = result.scalars().first()
        if not remesa:
            raise ValueError("Remesa no encontrada")
        if estado_enviada:
            remesa.estado_id = estado_enviada.id
        remesa.fecha_envio = date.today()
        if archivo:
            remesa.archivo_sepa = archivo
        self.session.add(remesa)
        await self.session.commit()
        await self.session.refresh(remesa)
        return remesa

    async def listar_cuotas_pendientes(
        self,
        ejercicio: int,
        agrupacion_id: Optional[UUID] = None,
    ) -> list[CuotaAnual]:
        """Devuelve cuotas pendientes para previsualizar antes de crear la remesa."""
        est_pend = await self._estado_cuota("Pendiente")
        q = select(CuotaAnual).where(CuotaAnual.ejercicio == ejercicio)
        if est_pend:
            q = q.where(CuotaAnual.estado_id == est_pend.id)
        if agrupacion_id:
            q = q.where(CuotaAnual.agrupacion_id == agrupacion_id)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _estado_cuota(self, nombre: str):
        r = await self.session.execute(select(EstadoCuota).where(EstadoCuota.nombre == nombre))
        return r.scalars().first()

    async def _estado_remesa(self, nombre: str):
        r = await self.session.execute(select(EstadoRemesa).where(EstadoRemesa.nombre == nombre))
        return r.scalars().first()

    async def _estado_orden_cobro(self, nombre: str):
        r = await self.session.execute(select(EstadoOrdenCobro).where(EstadoOrdenCobro.nombre == nombre))
        return r.scalars().first()
