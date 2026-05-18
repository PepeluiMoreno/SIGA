"""Endpoint REST para descargar el XML SEPA de una remesa.

GET /api/remesas/{remesa_id}/sepa-xml
  → Descarga el Pain.008.003.02 firmado con los datos de la organización.

Los datos del acreedor (nombre, IBAN, BIC, identificador SEPA) se leen
de los parámetros de configuración de la organización.
"""
import re
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import Response
from typing import Optional

from app.core.database import async_session
from app.core.security import extract_bearer_token, load_user_from_token
from app.modules.economico.services.remesa_service import RemesaService
from app.modules.configuracion.models.configuracion import Configuracion
from sqlalchemy import select

router = APIRouter(prefix="/api/remesas", tags=["remesas"])


async def _cfg(session, clave: str, default: str = "") -> str:
    r = await session.execute(select(Configuracion).where(Configuracion.clave == clave))
    cfg = r.scalars().first()
    return cfg.valor if cfg else default


@router.get(
    "/{remesa_id}/sepa-xml",
    response_class=Response,
    responses={200: {"content": {"application/xml": {}}}},
    summary="Descarga el XML SEPA Pain.008.003.02 de la remesa",
)
async def descargar_sepa_xml(
    remesa_id: UUID,
    authorization: Optional[str] = Header(None),
):
    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")

    async with async_session() as session:
        user = await load_user_from_token(session, token)
        if not user:
            raise HTTPException(status_code=401, detail="Token inválido")

        # Datos del acreedor desde configuración
        nombre       = await _cfg(session, "org.nombre", "Organización")
        iban         = await _cfg(session, "org.sepa_iban", "ES0000000000000000000000")
        bic          = await _cfg(session, "org.sepa_bic", "XXXXXXXXXXXXX")
        creditor_id  = await _cfg(session, "org.sepa_creditor_id", "ES00ZZZ00000000")

        service = RemesaService(session)
        try:
            xml_bytes = await service.generar_xml_sepa(
                remesa_id=remesa_id,
                creditor_name=nombre,
                creditor_iban=iban,
                creditor_bic=bic,
                creditor_id=creditor_id,
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

        filename = f"remesa_{str(remesa_id)[:8]}.xml"
        return Response(
            content=xml_bytes,
            media_type="application/xml",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
