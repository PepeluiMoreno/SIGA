"""Contexto GraphQL con sesión de base de datos y usuario autenticado."""

from dataclasses import dataclass
from typing import AsyncGenerator, Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext

from ..core.database import async_session
from ..core.security import extract_bearer_token, load_user_from_token
from ..modules.usuarios.models.usuario import Usuario


@dataclass
class Context(BaseContext):
    """Contexto GraphQL: sesión de BD + usuario autenticado (si lo hay)."""
    session: AsyncSession
    user: Optional[Usuario] = None


async def get_context(request: Request) -> AsyncGenerator[Context, None]:
    """Construye el contexto: abre sesión de BD y resuelve el usuario actual.

    Mantiene la sesión abierta durante toda la petición; commit al finalizar
    si no hubo excepción (necesario para mutaciones de Strawchemy).
    """
    async with async_session() as session:
        token = extract_bearer_token(request.headers.get("authorization"))
        user = await load_user_from_token(session, token) if token else None

        try:
            yield Context(session=session, user=user)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
