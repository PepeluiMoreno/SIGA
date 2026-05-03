"""Helper para registrar entradas en el log de auditoría."""

import uuid
from typing import Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..modules.administracion.models.auditoria import LogAuditoria, TipoAccion
from ..modules.usuarios.models.usuario import Usuario


async def log_action(
    session: AsyncSession,
    *,
    accion: TipoAccion,
    usuario: Optional[Usuario] = None,
    transaccion_codigo: Optional[str] = None,
    descripcion: Optional[str] = None,
    entidad: Optional[str] = None,
    entidad_id: Optional[uuid.UUID] = None,
    exitoso: bool = True,
    mensaje_error: Optional[str] = None,
    request: Optional[Request] = None,
) -> LogAuditoria:
    """Inserta una entrada en logs_auditoria. Hace flush, no commit."""
    log = LogAuditoria(
        usuario_id=usuario.id if usuario else None,
        username_snapshot=usuario.email if usuario else None,
        transaccion_codigo=transaccion_codigo,
        accion=accion,
        descripcion=descripcion,
        entidad=entidad,
        entidad_id=entidad_id,
        exitoso=exitoso,
        mensaje_error=mensaje_error,
        ip_address=(request.client.host if request and request.client else None),
        user_agent=(request.headers.get("user-agent") if request else None),
    )
    session.add(log)
    await session.flush()
    return log
