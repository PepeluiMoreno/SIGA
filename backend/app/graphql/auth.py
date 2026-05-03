"""Resolvers de autenticación: login y me."""

import uuid
from datetime import datetime
from typing import Optional

import strawberry
from sqlalchemy import select

from ..core.audit import log_action
from ..core.security import create_access_token, verify_password
from ..modules.administracion.models.auditoria import TipoAccion
from ..modules.usuarios.models.usuario import Usuario


@strawberry.type
class UserPayload:
    """Datos públicos del usuario autenticado."""
    id: uuid.UUID
    email: str
    activo: bool


@strawberry.type
class LoginPayload:
    """Resultado de un login exitoso."""
    token: str
    user: UserPayload


def _to_payload(u: Usuario) -> UserPayload:
    return UserPayload(id=u.id, email=u.email, activo=u.activo)


@strawberry.type
class AuthQuery:
    @strawberry.field
    async def me(self, info: strawberry.Info) -> Optional[UserPayload]:
        """Devuelve el usuario actual o null si no hay sesión válida."""
        user: Optional[Usuario] = info.context.user
        if user is None:
            return None
        return _to_payload(user)


@strawberry.type
class AuthMutation:
    @strawberry.mutation
    async def login(
        self,
        info: strawberry.Info,
        email: str,
        password: str,
    ) -> LoginPayload:
        """Autentica al usuario y devuelve un JWT."""
        session = info.context.session
        request = info.context.request

        stmt = select(Usuario).where(
            Usuario.email == email,
            Usuario.activo == True,  # noqa: E712
        )
        result = await session.execute(stmt)
        usuario = result.scalar_one_or_none()

        if usuario is None or not verify_password(password, usuario.password_hash):
            await log_action(
                session,
                accion=TipoAccion.LOGIN,
                usuario=usuario,
                exitoso=False,
                mensaje_error="Credenciales inválidas",
                descripcion=f"Intento de login para {email}",
                request=request,
            )
            raise ValueError("Credenciales inválidas")

        usuario.ultimo_acceso = datetime.utcnow()
        await log_action(
            session,
            accion=TipoAccion.LOGIN,
            usuario=usuario,
            exitoso=True,
            descripcion=f"Login exitoso de {usuario.email}",
            request=request,
        )

        token = create_access_token(usuario.id)
        return LoginPayload(token=token, user=_to_payload(usuario))
