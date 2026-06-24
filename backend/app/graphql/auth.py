"""Resolvers de autenticación, gestión de usuarios y juntas directivas."""

import secrets
import uuid
from datetime import datetime, date
from typing import Optional

import strawberry
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..core.audit import log_action
from ..core.security import create_access_token, hash_password, verify_password
from ..modules.acceso.models.auditoria import TipoAccion
from ..modules.acceso.models.usuario import Usuario, UsuarioRol
from ..modules.acceso.models.rol import Rol
from ..modules.acceso.models.rol_transaccion import RolTransaccion
from ..modules.acceso.models.transaccion import Transaccion
from ..modules.acceso.services.acceso_service import AccesoService
from ..modules.acceso.services.password_reset_service import PasswordResetService
from app.graphql.permissions import RequireTransaction, RequireAuthenticated


@strawberry.type
class UserPayload:
    """Datos públicos del usuario autenticado."""
    id: uuid.UUID
    email: str
    activo: bool
    miembro_id: Optional[uuid.UUID] = None


@strawberry.type
class LoginPayload:
    """Resultado de un login exitoso."""
    token: str
    user: UserPayload


@strawberry.type
class MiPerfilPayload:
    """Perfil completo del usuario autenticado incluyendo datos de membresía."""
    id: uuid.UUID
    email: str
    activo: bool
    ultimo_acceso: Optional[datetime]
    entidad_vinculacion: Optional[str]
    miembro_id: Optional[uuid.UUID]
    tipo_vinculacion_id: Optional[uuid.UUID]
    tipo_vinculacion_nombre: Optional[str]


def _to_payload(u: Usuario) -> UserPayload:
    return UserPayload(id=u.id, email=u.email, activo=u.activo, miembro_id=u.contacto_id)


def _to_mi_perfil(u: Usuario) -> MiPerfilPayload:
    return MiPerfilPayload(
        id=u.id,
        email=u.email,
        activo=u.activo,
        ultimo_acceso=u.ultimo_acceso,
        entidad_vinculacion=u.entidad_vinculacion,
        miembro_id=u.contacto_id,
        tipo_vinculacion_id=u.tipo_vinculacion_id,
        # tipo_vinculacion_id está deprecado en Usuario y no tiene relación ORM
        # (la vinculación vive en Contacto.vinculaciones). No se resuelve el nombre aquí.
        tipo_vinculacion_nombre=None,
    )


@strawberry.type
class AuthQuery:
    @strawberry.field
    async def me(self, info: strawberry.Info) -> Optional[UserPayload]:
        """Devuelve el usuario actual o null si no hay sesión válida."""
        user: Optional[Usuario] = info.context.user
        if user is None:
            return None
        return _to_payload(user)

    @strawberry.field
    async def mi_perfil(self, info: strawberry.Info) -> Optional[MiPerfilPayload]:
        """Devuelve el perfil completo del usuario autenticado."""
        user: Optional[Usuario] = info.context.user
        if user is None:
            return None
        return _to_mi_perfil(user)

    @strawberry.field
    async def mis_transacciones(self, info: strawberry.Info) -> list[str]:
        """Devuelve los códigos de transacción permitidos para el usuario autenticado."""
        user: Optional[Usuario] = info.context.user
        if user is None:
            return []
        session = info.context.session
        result = await session.execute(
            select(Transaccion.codigo)
            .join(RolTransaccion, RolTransaccion.transaccion_id == Transaccion.id)
            .join(Rol, Rol.id == RolTransaccion.rol_id)
            .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
            .where(
                UsuarioRol.usuario_id == user.id,
                UsuarioRol.activo == True,  # noqa: E712
                UsuarioRol.eliminado == False,
                Transaccion.activa == True,
            )
            .distinct()
        )
        return list(result.scalars())


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

    @strawberry.mutation(permission_classes=[RequireTransaction("ACCESO_USUARIO_CREAR")])
    async def crear_usuario(
        self,
        info: strawberry.Info,
        email: str,
        password: Optional[str] = None,
        activo: bool = True,
        miembro_id: Optional[uuid.UUID] = None,
        tipo_vinculacion_id: Optional[uuid.UUID] = None,
        entidad_vinculacion: Optional[str] = None,
        enviar_email_bienvenida: bool = False,
    ) -> UserPayload:
        """Crea un nuevo usuario del sistema. Requiere permisos de administrador.

        Si enviar_email_bienvenida=True, la contraseña proporcionada es ignorada
        y se genera una temporal; el usuario recibirá un email para establecer la suya.
        Requiere que el servidor SMTP esté configurado en Parámetros Generales.
        """
        session = info.context.session

        pwd = password
        if enviar_email_bienvenida:
            pwd = secrets.token_urlsafe(32)
        elif not pwd:
            raise ValueError("Debe proporcionar una contraseña o activar el envío de email de bienvenida")

        svc = AccesoService(session)
        usuario = await svc.crear_usuario(
            email=email,
            password=pwd,
            activo=activo,
            contacto_id=miembro_id,
            tipo_vinculacion_id=tipo_vinculacion_id,
            entidad_vinculacion=entidad_vinculacion,
        )

        if enviar_email_bienvenida:
            reset_svc = PasswordResetService(session)
            await reset_svc.solicitar_reset(email.strip().lower())

        await session.commit()
        return _to_payload(usuario)

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_JUNTA_CONFIGURAR")])
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

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_CARGO_ASIGNAR")])
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

    @strawberry.mutation(permission_classes=[RequireAuthenticated])
    async def cambiar_mi_password(
        self,
        info: strawberry.Info,
        password_actual: str,
        nueva_password: str,
    ) -> bool:
        """Permite al usuario autenticado cambiar su propia contraseña."""
        usuario: Optional[Usuario] = info.context.user
        if not usuario:
            raise ValueError("No autenticado")
        if not verify_password(password_actual, usuario.password_hash):
            raise ValueError("La contraseña actual no es correcta")
        if len(nueva_password) < 8:
            raise ValueError("La nueva contraseña debe tener al menos 8 caracteres")
        session = info.context.session
        result = await session.execute(select(Usuario).where(Usuario.id == usuario.id))
        db_usuario = result.scalar_one()
        db_usuario.password_hash = hash_password(nueva_password)
        await session.commit()
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("MEMBRESIA_CARGO_REVOCAR")])
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
