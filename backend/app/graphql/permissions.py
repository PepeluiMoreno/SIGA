"""Permisos GraphQL: RBAC basado en transacciones."""

from typing import Type

from sqlalchemy import select
from strawberry.permission import BasePermission

from ..modules.administracion.models.rol import Rol
from ..modules.administracion.models.rol_transaccion import RolTransaccion
from ..modules.administracion.models.transaccion import Transaccion
from ..modules.usuarios.models.usuario import UsuarioRol


async def user_has_transaction(session, user, codigo: str) -> bool:
    """Devuelve True si el usuario tiene un rol activo que incluya la transacción."""
    if user is None:
        return False
    stmt = (
        select(UsuarioRol.id)
        .join(Rol, Rol.id == UsuarioRol.rol_id)
        .join(RolTransaccion, RolTransaccion.rol_id == Rol.id)
        .join(Transaccion, Transaccion.id == RolTransaccion.transaccion_id)
        .where(
            UsuarioRol.usuario_id == user.id,
            UsuarioRol.eliminado == False,  # noqa: E712
            Rol.activo == True,  # noqa: E712
            Rol.eliminado == False,  # noqa: E712
            RolTransaccion.eliminado == False,  # noqa: E712
            Transaccion.codigo == codigo,
            Transaccion.activa == True,  # noqa: E712
        )
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.first() is not None


def requires_transaction(codigo: str) -> Type[BasePermission]:
    """Factory: devuelve un BasePermission que exige la transacción `codigo`.

    Uso:
        @strawberry.field(permission_classes=[requires_transaction("USR_LIST")])
        async def list_users(self, info): ...
    """
    class _RequiresTransaction(BasePermission):
        message = f"Permiso requerido: {codigo}"

        async def has_permission(self, source, info, **kwargs) -> bool:
            ctx = info.context
            return await user_has_transaction(ctx.session, ctx.user, codigo)

    _RequiresTransaction.__name__ = f"RequiresTransaction_{codigo}"
    return _RequiresTransaction
