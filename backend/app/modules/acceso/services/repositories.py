"""Implementaciones async SQLAlchemy de los puertos del AuthorizationService."""

from __future__ import annotations

from typing import Optional, Set

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.usuario import UsuarioRol
from ..models.rol_transaccion import RolTransaccion
from ..models.funcionalidad import RolFuncionalidad, FuncionalidadTransaccion


class SQLRoleRepository:
    """Resuelve roles efectivos de un usuario (directos + por cargo)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_direct_roles(self, user_id: str) -> Set[str]:
        result = await self.session.execute(
            select(UsuarioRol.rol_id)
            .where(
                UsuarioRol.usuario_id == user_id,
                UsuarioRol.activo == True,
                UsuarioRol.eliminado == False,
            )
        )
        return {str(row[0]) for row in result.all()}

    async def get_roles_by_positions(
        self, user_id: str, territory_id: Optional[str]
    ) -> Set[str]:
        """Roles derivados del cargo activo del usuario en una agrupación."""
        from ...membresia.models.miembro import Miembro
        from ...core.geografico.models import AgrupacionTerritorial

        q = (
            select(UsuarioRol.rol_id)
            .where(
                UsuarioRol.usuario_id == user_id,
                UsuarioRol.activo == True,
                UsuarioRol.eliminado == False,
            )
        )
        if territory_id:
            q = q.where(
                (UsuarioRol.agrupacion_id == territory_id)
                | (UsuarioRol.agrupacion_id == None)
            )

        result = await self.session.execute(q)
        return {str(row[0]) for row in result.all()}

    async def get_all_role_ids(self) -> Set[str]:
        from ..models.rol import Rol
        result = await self.session.execute(
            select(Rol.id).where(Rol.activo == True, Rol.eliminado == False)
        )
        return {str(row[0]) for row in result.all()}


class SQLPermissionRepository:
    """Resuelve transacciones asignadas directamente a un rol."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_transactions_by_role(self, role_id: str) -> Set[str]:
        result = await self.session.execute(
            select(RolTransaccion.transaccion_id)
            .where(
                RolTransaccion.rol_id == role_id,
                RolTransaccion.eliminado == False,
            )
        )
        return {str(row[0]) for row in result.all()}


class SQLFunctionalityRepository:
    """Resuelve funcionalidades y transacciones por la cadena funcionalidad."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_functionalities_by_role(self, role_id: str) -> Set[str]:
        result = await self.session.execute(
            select(RolFuncionalidad.funcionalidad_id)
            .where(
                RolFuncionalidad.rol_id == role_id,
                RolFuncionalidad.eliminado == False,
            )
        )
        return {str(row[0]) for row in result.all()}

    async def get_transactions_by_functionality(self, functionality_id: str) -> Set[str]:
        result = await self.session.execute(
            select(FuncionalidadTransaccion.transaccion_id)
            .where(
                FuncionalidadTransaccion.funcionalidad_id == functionality_id,
                FuncionalidadTransaccion.eliminado == False,
            )
        )
        return {str(row[0]) for row in result.all()}

    async def get_all_functionality_ids(self) -> Set[str]:
        from ..models.funcionalidad import Funcionalidad
        result = await self.session.execute(
            select(Funcionalidad.id).where(
                Funcionalidad.activa == True,
                Funcionalidad.eliminado == False,
            )
        )
        return {str(row[0]) for row in result.all()}
