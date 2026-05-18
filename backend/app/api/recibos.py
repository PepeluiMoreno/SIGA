"""Endpoints REST para descarga de recibos PDF.

GET /api/recibos/cuota/{cuota_id}   → PDF recibo cuota anual
GET /api/recibos/apunte/{apunte_id} → PDF justificante de movimiento
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from app.core.database import get_db as get_async_session
from app.modules.economico.services.pdf.recibo_service import ReciboService

router = APIRouter(prefix="/api/recibos", tags=["recibos"])


@router.get(
    "/cuota/{cuota_id}",
    response_class=Response,
    responses={200: {"content": {"application/pdf": {}}}},
    summary="Recibo PDF de cuota anual",
)
async def descargar_recibo_cuota(
    cuota_id: UUID,
    session=Depends(get_async_session),
):
    """Genera y devuelve el recibo PDF de una cuota anual pagada."""
    service = ReciboService(session)
    try:
        pdf_bytes = await service.recibo_cuota(cuota_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=recibo-cuota-{cuota_id}.pdf"},
    )


@router.get(
    "/apunte/{apunte_id}",
    response_class=Response,
    responses={200: {"content": {"application/pdf": {}}}},
    summary="Justificante PDF de movimiento de caja",
)
async def descargar_recibo_apunte(
    apunte_id: UUID,
    session=Depends(get_async_session),
):
    """Genera y devuelve el justificante PDF de un apunte de caja."""
    service = ReciboService(session)
    try:
        pdf_bytes = await service.recibo_apunte(apunte_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=movimiento-{apunte_id}.pdf"},
    )
