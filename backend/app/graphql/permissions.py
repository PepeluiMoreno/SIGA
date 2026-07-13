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


def RequireTransaction(transaction_id: str, objetivo: "Objetivo | None" = None) -> type:
    """Clase de permiso que verifica una transacción **sobre un objetivo concreto**.

    Sin `objetivo`, la comprobación es la de siempre: «¿tienes este permiso?».
    Con `objetivo`, el motor además responde «¿lo tienes **sobre esto**?»:

        RequireTransaction("MEMBRESIA_MIEMBRO_BAJA", objetivo=Objetivo.contacto("contacto_id"))

    El guard toma el argumento indicado de la llamada (aquí, `contacto_id`), resuelve la
    agrupación de esa entidad y comprueba que caiga en el ámbito territorial del usuario.
    Ver `MOTOR_TERRITORIAL.md`.

    El ámbito de la transacción (GLOBAL/TERRITORIAL/PROPIO) se declara en el `catalog.py`
    del módulo y decide si el territorio se comprueba o no.

    Strawberry necesita clases en permission_classes (no instancias): esta función es la
    factory que crea una clase por cada código.
    """

    class _Perm(strawberry.BasePermission):
        message = f"Permiso denegado: {transaction_id}"

        async def has_permission(self, source: Any, info: Info, **kwargs: Any) -> bool:
            ctx: Context = info.context
            # 1) ¿Tiene el permiso, en abstracto?
            if not await ctx.check_permission(transaction_id):
                return False
            # 2) ¿Lo tiene SOBRE ESTO? (solo si la transacción es territorial)
            if objetivo is None:
                return True
            ok, motivo = await ctx.check_ambito(transaction_id, objetivo, kwargs)
            if not ok:
                self.message = motivo
            return ok

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


def campo(*args, permission_classes=None, **kwargs):
    """`strawchemy.field` con *default-deny*: todo listado exige al menos estar
    autenticado salvo que declare sus propios `permission_classes`.

    Motivación: los campos de strawchemy son públicos por defecto. Sin esta
    envoltura, cualquier anónimo podía listar `usuarios`, `logsAuditoria`, toda la
    estructura RBAC, etc. Aquí invertimos el defecto a *cerrado*: un campo nuevo
    queda autenticado aunque quien lo añada olvide anotarlo. Los campos con RBAC
    fino (p. ej. `RequireTransaction("ECO_CUOTA_LISTAR")`) pasan su lista tal cual.

    Nota: se importa `strawchemy` de forma perezosa para evitar un ciclo de imports
    (schema_simple → permissions → strawchemy singleton).
    """
    from . import strawchemy

    if not permission_classes:
        permission_classes = [RequireAuthenticated]
    return strawchemy.field(*args, permission_classes=permission_classes, **kwargs)
