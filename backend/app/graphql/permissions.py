"""Integración Strawberry BasePermission con el sistema de PermissionMatrix.

Uso en resolvers:
    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_CREAR")])
    @strawberry.mutation(permission_classes=[RequireAuthenticated])
    async def my_mutation(...) -> ...
"""

from __future__ import annotations

from typing import Any

import strawberry
from strawberry.types import Info

from .context import Context


class RequireAuthenticated(strawberry.BasePermission):
    message = "No autenticado"

    async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
        ctx: Context = info.context
        return ctx.is_authenticated


def RequireTransaction(transaction_id: str) -> type:
    """Devuelve una clase de permiso que verifica una transacción concreta.

    Strawberry necesita clases en permission_classes (no instancias).
    Esta función actúa como factory para crear una clase anónima por cada código.
    """

    class _Perm(strawberry.BasePermission):
        message = f"Permiso denegado: {transaction_id}"

        async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
            ctx: Context = info.context
            return await ctx.check_permission(transaction_id)

    _Perm.__name__ = f"Require_{transaction_id}"
    _Perm.__qualname__ = f"Require_{transaction_id}"
    return _Perm


def RequireAnyTransaction(*transaction_ids: str) -> type:
    """Devuelve una clase de permiso que pasa si el usuario tiene al menos uno de los permisos."""

    class _Perm(strawberry.BasePermission):
        message = "Permiso denegado"

        async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
            ctx: Context = info.context
            if not ctx.is_authenticated:
                return False
            for tid in transaction_ids:
                if await ctx.check_permission(tid):
                    return True
            return False

    name = f"RequireAny_{'_or_'.join(transaction_ids[:3])}"
    _Perm.__name__ = name
    _Perm.__qualname__ = name
    return _Perm
