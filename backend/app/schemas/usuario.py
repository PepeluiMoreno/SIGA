import strawberry
from datetime import datetime

from .tipos_base import Rol, UnidadOrganizativa


@strawberry.type
class UsuarioRol:
    rol: Rol
    agrupacion: UnidadOrganizativa | None


@strawberry.type
class Usuario:
    id: int
    email: str
    activo: bool
    created_at: datetime
    last_login: datetime | None
    roles: list[UsuarioRol]


@strawberry.type
class AuthPayload:
    token: str
    usuario: Usuario


@strawberry.input
class LoginInput:
    email: str
    password: str


@strawberry.input
class UsuarioInput:
    email: str
    password: str
    rol_ids: list[int] | None = None
