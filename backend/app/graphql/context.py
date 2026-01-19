"""Contexto GraphQL con sesión de base de datos."""

from typing import AsyncIterator
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext

from ..core.database import async_session


@dataclass
class Context(BaseContext):
    """Contexto GraphQL con sesión de base de datos."""
    session: AsyncSession


async def get_context() -> AsyncIterator[Context]:
    """
    Obtiene el contexto GraphQL con una sesión de base de datos.

    La sesión se cierra automáticamente al finalizar la request.
    """
    async with async_session() as session:
        yield Context(session=session)
