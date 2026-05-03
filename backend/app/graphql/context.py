"""Contexto GraphQL con sesión de base de datos, usuario autenticado y permisos."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from typing import AsyncGenerator, FrozenSet, Optional

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext

from ..core.database import async_session
from ..core.security import extract_bearer_token, load_user_from_token
from ..modules.acceso.models.usuario import Usuario, UsuarioRol


@dataclass
class Context(BaseContext):
    """Contexto GraphQL: sesión de BD + usuario autenticado + permisos en memoria."""
    session: AsyncSession
    user: Optional[Usuario] = None
    _role_ids_cache: Optional[FrozenSet[str]] = field(default=None, repr=False, compare=False)

    # ------------------------------------------------------------------
    # Identidad
    # ------------------------------------------------------------------

    @property
    def is_authenticated(self) -> bool:
        return self.user is not None

    @property
    def user_id(self) -> Optional[str]:
        return str(self.user.id) if self.user else None

    # ------------------------------------------------------------------
    # Roles efectivos (un solo query por request, luego cached)
    # ------------------------------------------------------------------

    async def get_role_ids(self) -> FrozenSet[str]:
        """Carga los role_ids activos del usuario desde DB (una sola vez por request)."""
        if self._role_ids_cache is not None:
            return self._role_ids_cache
        if self.user is None:
            self._role_ids_cache = frozenset()
            return self._role_ids_cache
        result = await self.session.execute(
            select(UsuarioRol.rol_id).where(
                UsuarioRol.usuario_id == self.user.id,
                UsuarioRol.activo == True,
                UsuarioRol.eliminado == False,
            )
        )
        self._role_ids_cache = frozenset(str(row[0]) for row in result.all())
        return self._role_ids_cache

    # ------------------------------------------------------------------
    # Autorización (usando PermissionMatrix en memoria — sin DB adicional)
    # ------------------------------------------------------------------

    async def check_permission(self, transaction_id: str) -> bool:
        """True si el usuario posee el permiso indicado."""
        from ..modules.acceso.services.matrix import matrix_cache
        if not self.is_authenticated or not matrix_cache.is_ready():
            return False
        role_ids = await self.get_role_ids()
        return matrix_cache.can(role_ids, transaction_id)

    async def require_permission(self, transaction_id: str) -> None:
        """Lanza PermissionError si el usuario no tiene el permiso."""
        if not await self.check_permission(transaction_id):
            raise PermissionError(f"Permiso denegado: {transaction_id}")


async def get_context(request: Request) -> AsyncGenerator[Context, None]:
    """Construye el contexto: abre sesión de BD y resuelve el usuario actual."""
    async with async_session() as session:
        token = extract_bearer_token(request.headers.get("authorization"))
        user = await load_user_from_token(session, token) if token else None

        ctx = Context(session=session, user=user)
        try:
            yield ctx
            await session.commit()
        except Exception:
            await session.rollback()
            raise
