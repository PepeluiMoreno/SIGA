from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import FrozenSet, Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext

from .auth import decode_token
from .database import async_session


@dataclass
class Context(BaseContext):
    request: Request
    session: AsyncSession

    @cached_property
    def user_id(self) -> Optional[str]:
        auth = self.request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return None
        payload = decode_token(auth[7:])
        return payload.get("sub") if payload else None

    @cached_property
    def territory_id(self) -> Optional[str]:
        """Agrupación territorial activa del usuario (del JWT)."""
        auth = self.request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return None
        payload = decode_token(auth[7:])
        return payload.get("territory_id") if payload else None

    @cached_property
    def _jwt_role_ids(self) -> FrozenSet[str]:
        """IDs de roles incluidos en el JWT (sin consulta DB)."""
        auth = self.request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return frozenset()
        payload = decode_token(auth[7:])
        if not payload:
            return frozenset()
        return frozenset(payload.get("roles", []))

    def check_permission(self, transaction_id: str) -> bool:
        """Comprueba si el usuario tiene permiso usando la PermissionMatrix en memoria.

        Para resolvers Strawberry: rápido, sin consulta DB.
        Para validación completa con DB, usar AuthorizationService directamente.
        """
        from ..modules.acceso.services.matrix import matrix_cache
        if not self._jwt_role_ids or not matrix_cache.is_ready():
            return False
        return matrix_cache.can(self._jwt_role_ids, transaction_id)

    def require_permission(self, transaction_id: str) -> None:
        """Lanza PermissionDeniedError si el usuario no tiene el permiso."""
        if not self.check_permission(transaction_id):
            raise PermissionDeniedError(transaction_id)

    @property
    def is_authenticated(self) -> bool:
        return self.user_id is not None


class PermissionDeniedError(Exception):
    def __init__(self, transaction_id: str) -> None:
        super().__init__(f"Permiso denegado: {transaction_id}")
        self.transaction_id = transaction_id


async def get_context(request: Request, session: AsyncSession = None) -> Context:
    return Context(request=request, session=session or async_session())
