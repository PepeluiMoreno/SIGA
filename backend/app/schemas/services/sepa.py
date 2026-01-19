"""Generador de ficheros SEPA XML (pain.008.001.02 - Adeudo directo)."""

from datetime import date, datetime
from decimal import Decimal
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from ..models import Remesa, OrdenCobro, Miembro, AgrupacionTerritorial


def generar_sepa_xml(
    remesa: Remesa,
    ordenes: list[OrdenCobro],
    acreedor_nombre: str,
    acreedor_iban: str,
    acreedor_bic: str,
    acreedor_id: str,  # Identificador del acreedor SEPA
) -> str:
    """Genera XML SEPA pain.008.001.02 para adeudo directo."""

    # Namespace
    ns = "urn:iso:std:iso:20022:tech:xsd:pain.008.001.02"

    root = Element("Document", xmlns=ns)
    cstmr_drct_dbt_initn = SubElement(root, "CstmrDrctDbtInitn")

    # Group Header
    grp_hdr = SubElement(cstmr_drct_dbt_initn, "GrpHdr")
    SubElement(grp_hdr, "MsgId").text = f"REMESA-{remesa.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    SubElement(grp_hdr, "CreDtTm").text = datetime.now().isoformat()
    SubElement(grp_hdr, "NbOfTxs").text = str(len(ordenes))
    SubElement(grp_hdr, "CtrlSum").text = str(remesa.importe_total)

    initg_pty = SubElement(grp_hdr, "InitgPty")
    SubElement(initg_pty, "Nm").text = acreedor_nombre

    # Payment Information
    pmt_inf = SubElement(cstmr_drct_dbt_initn, "PmtInf")
    SubElement(pmt_inf, "PmtInfId").text = f"PMT-{remesa.id}"
    SubElement(pmt_inf, "PmtMtd").text = "DD"  # Direct Debit
    SubElement(pmt_inf, "NbOfTxs").text = str(len(ordenes))
    SubElement(pmt_inf, "CtrlSum").text = str(remesa.importe_total)

    # Payment Type Information
    pmt_tp_inf = SubElement(pmt_inf, "PmtTpInf")
    svc_lvl = SubElement(pmt_tp_inf, "SvcLvl")
    SubElement(svc_lvl, "Cd").text = "SEPA"
    lcl_instrm = SubElement(pmt_tp_inf, "LclInstrm")
    SubElement(lcl_instrm, "Cd").text = "CORE"
    SubElement(pmt_tp_inf, "SeqTp").text = "RCUR"  # Recurrente

    # Fecha de cobro (D+5 hábiles aprox)
    SubElement(pmt_inf, "ReqdColltnDt").text = _fecha_cobro().isoformat()

    # Creditor (Acreedor)
    cdtr = SubElement(pmt_inf, "Cdtr")
    SubElement(cdtr, "Nm").text = acreedor_nombre

    cdtr_acct = SubElement(pmt_inf, "CdtrAcct")
    cdtr_acct_id = SubElement(cdtr_acct, "Id")
    SubElement(cdtr_acct_id, "IBAN").text = acreedor_iban

    cdtr_agt = SubElement(pmt_inf, "CdtrAgt")
    fin_instn_id = SubElement(cdtr_agt, "FinInstnId")
    SubElement(fin_instn_id, "BIC").text = acreedor_bic

    # Creditor Scheme Identification
    cdtr_schme_id = SubElement(pmt_inf, "CdtrSchmeId")
    cdtr_schme_id_inner = SubElement(cdtr_schme_id, "Id")
    prvt_id = SubElement(cdtr_schme_id_inner, "PrvtId")
    othr = SubElement(prvt_id, "Othr")
    SubElement(othr, "Id").text = acreedor_id
    schme_nm = SubElement(othr, "SchmeNm")
    SubElement(schme_nm, "Prtry").text = "SEPA"

    # Transacciones individuales
    for orden in ordenes:
        miembro = orden.cuota.miembro
        _agregar_transaccion(pmt_inf, orden, miembro)

    # Formatear XML
    xml_str = tostring(root, encoding="unicode")
    return minidom.parseString(xml_str).toprettyxml(indent="  ")


def _fecha_cobro() -> date:
    """Calcula fecha de cobro (aprox D+5 hábiles)."""
    from datetime import timedelta
    hoy = date.today()
    dias = 5
    fecha = hoy
    while dias > 0:
        fecha += timedelta(days=1)
        if fecha.weekday() < 5:  # Lunes a viernes
            dias -= 1
    return fecha


def _agregar_transaccion(pmt_inf: Element, orden: OrdenCobro, miembro: Miembro):
    """Añade una transacción al bloque PmtInf."""
    drct_dbt_tx_inf = SubElement(pmt_inf, "DrctDbtTxInf")

    # Payment ID
    pmt_id = SubElement(drct_dbt_tx_inf, "PmtId")
    SubElement(pmt_id, "EndToEndId").text = f"CUOTA-{orden.cuota.anio}-{orden.cuota_id}"

    # Amount
    instd_amt = SubElement(drct_dbt_tx_inf, "InstdAmt", Ccy="EUR")
    instd_amt.text = str(orden.importe)

    # Mandate (simplificado)
    drct_dbt_tx = SubElement(drct_dbt_tx_inf, "DrctDbtTx")
    mndt_rltd_inf = SubElement(drct_dbt_tx, "MndtRltdInf")
    SubElement(mndt_rltd_inf, "MndtId").text = f"MNDT-{miembro.id}"
    SubElement(mndt_rltd_inf, "DtOfSgntr").text = miembro.fecha_alta.isoformat()

    # Debtor Agent (BIC del deudor - derivado del IBAN)
    dbtr_agt = SubElement(drct_dbt_tx_inf, "DbtrAgt")
    fin_instn_id = SubElement(dbtr_agt, "FinInstnId")
    SubElement(fin_instn_id, "Othr").text = "NOTPROVIDED"

    # Debtor (Deudor)
    dbtr = SubElement(drct_dbt_tx_inf, "Dbtr")
    nombre_completo = f"{miembro.apellido1} {miembro.apellido2 or ''} {miembro.nombre}".strip()
    SubElement(dbtr, "Nm").text = nombre_completo[:70]

    # Debtor Account
    dbtr_acct = SubElement(drct_dbt_tx_inf, "DbtrAcct")
    dbtr_acct_id = SubElement(dbtr_acct, "Id")
    SubElement(dbtr_acct_id, "IBAN").text = miembro.iban or ""

    # Concepto
    rmt_inf = SubElement(drct_dbt_tx_inf, "RmtInf")
    SubElement(rmt_inf, "Ustrd").text = f"Cuota {orden.cuota.anio}"
