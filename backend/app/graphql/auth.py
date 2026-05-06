"""Resolvers de autenticación, gestión de usuarios y juntas directivas."""

import uuid
from datetime import datetime, date
from typing import Optional

import strawberry
from sqlalchemy import select

from ..core.audit import log_action
from ..core.security import create_access_token, verify_password
from ..modules.acceso.models.auditoria import TipoAccion
from ..modules.acceso.models.usuario import Usuario
from ..modules.acceso.services.acceso_service import AccesoService
from ..modules.acceso.services.password_reset_service import PasswordResetService


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

    @strawberry.mutation
    async def crear_usuario(
        self,
        info: strawberry.Info,
        email: str,
        password: str,
        activo: bool = True,
    ) -> UserPayload:
        """Crea un nuevo usuario del sistema. Requiere permisos de administrador."""
        session = info.context.session
        svc = AccesoService(session)
        usuario = await svc.crear_usuario(email=email, password=password, activo=activo)
        await session.commit()
        return _to_payload(usuario)

    @strawberry.mutation
    async def constituir_junta(
        self,
        info: strawberry.Info,
        agrupacion_id: uuid.UUID,
        nombre: str,
        fecha_constitucion: date,
        observaciones: Optional[str] = None,
    ) -> uuid.UUID:
        """Constituye una nueva junta directiva para una agrupación.

        Devuelve el ID de la nueva JuntaDirectiva.
        Desactiva la junta activa anterior si existiera.
        """
        session = info.context.session
        svc = AccesoService(session)
        junta = await svc.constituir_junta(
            agrupacion_id=agrupacion_id,
            nombre=nombre,
            fecha_constitucion=fecha_constitucion,
            observaciones=observaciones,
        )
        await session.commit()
        return junta.id

    @strawberry.mutation
    async def asignar_nombramiento(
        self,
        info: strawberry.Info,
        usuario_id: uuid.UUID,
        rol_id: uuid.UUID,
        fecha_inicio: date,
        agrupacion_id: Optional[uuid.UUID] = None,
        motivo: Optional[str] = None,
        tipo_origen: Optional[str] = None,
    ) -> uuid.UUID:
        """Asigna un cargo (rol organizacional) a un usuario.

        Crea UsuarioRol activo + registro en HistorialNombramiento.
        Devuelve el ID del UsuarioRol creado.
        """
        session = info.context.session
        svc = AccesoService(session)
        nombramiento = await svc.asignar_nombramiento(
            usuario_id=usuario_id,
            rol_id=rol_id,
            fecha_inicio=fecha_inicio,
            agrupacion_id=agrupacion_id,
            motivo=motivo,
            tipo_origen=tipo_origen,
        )
        await session.commit()
        return nombramiento.id

    # ── Reset de contraseña ──────────────────────────────────────────────────

    @strawberry.mutation
    async def solicitar_reset_password(
        self,
        info: strawberry.Info,
        email: str,
        honeypot: str = "",
    ) -> bool:
        """Envía un email con enlace de restablecimiento de contraseña.

        Siempre devuelve True para no revelar si el email existe.
        El campo honeypot debe llegar vacío; si tiene valor, es un bot.
        """
        if honeypot:
            return True  # bot detectado — respuesta silenciosa

        svc = PasswordResetService(info.context.session)
        try:
            await svc.solicitar_reset(email.strip().lower())
            await info.context.session.commit()
        except ValueError as exc:
            raise ValueError(str(exc))
        except RuntimeError as exc:
            raise ValueError(str(exc))
        return True

    @strawberry.mutation
    async def reset_password(
        self,
        info: strawberry.Info,
        token: str,
        nueva_password: str,
    ) -> bool:
        """Aplica la nueva contraseña si el token es válido y no ha expirado."""
        svc = PasswordResetService(info.context.session)
        await svc.confirmar_reset(token, nueva_password)
        await info.context.session.commit()
        return True

    @strawberry.mutation
    async def revocar_nombramiento(
        self,
        info: strawberry.Info,
        usuario_id: uuid.UUID,
        rol_id: uuid.UUID,
        fecha_fin: date,
        motivo: Optional[str] = None,
        agrupacion_id: Optional[uuid.UUID] = None,
    ) -> uuid.UUID:
        """Revoca un nombramiento (cargo) activo.

        Desactiva UsuarioRol + cierra HistorialNombramiento.
        Devuelve el ID del UsuarioRol desactivado.
        """
        session = info.context.session
        svc = AccesoService(session)
        nombramiento = await svc.revocar_nombramiento(
            usuario_id=usuario_id,
            rol_id=rol_id,
            fecha_fin=fecha_fin,
            motivo=motivo,
            agrupacion_id=agrupacion_id,
        )
        await session.commit()
        return nombramiento.id
