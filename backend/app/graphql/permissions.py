"""Integración Strawberry BasePermission con el sistema de PermissionMatrix.

Uso en resolvers:
    @strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_CREAR")])
    async def crear_campana(...) -> ...
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


class RequireTransaction(strawberry.BasePermission):
    """Verifica que el usuario posee el permiso de una transacción concreta.

    Usa la PermissionMatrix en memoria — sin consulta DB extra por request.
    """

    message = "Permiso denegado"

    def __init__(self, transaction_id: str) -> None:
        self.transaction_id = transaction_id
        self.message = f"Permiso denegado: {transaction_id}"

    async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
        ctx: Context = info.context
        return await ctx.check_permission(self.transaction_id)


class RequireAnyTransaction(strawberry.BasePermission):
    """Pasa si el usuario tiene al menos uno de los permisos indicados."""

    message = "Permiso denegado"

    def __init__(self, *transaction_ids: str) -> None:
        self.transaction_ids = transaction_ids

    async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
        ctx: Context = info.context
        if not ctx.is_authenticated:
            return False
        for tid in self.transaction_ids:
            if await ctx.check_permission(tid):
                return True
        return False
