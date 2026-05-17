import strawberry
from enum import Enum


@strawberry.enum
class TipoTransaccion(Enum):
    QUERY = "QUERY"
    MUTATION = "MUTATION"


@strawberry.type
class Pais:
    codpais: str
    nombre: str


@strawberry.type
class Provincia:
    codprov: str
    nombre: str


@strawberry.type
class TipoMiembro:
    id: int
    codigo: str
    nombre: str
    requiere_cuota: bool
    activo: bool


@strawberry.type
class Rol:
    id: int
    codigo: str
    nombre: str
    descripcion: str | None
    activo: bool


@strawberry.type
class Transaccion:
    id: int
    codigo: str
    nombre: str
    tipo: TipoTransaccion
    modulo: str | None
    activo: bool


@strawberry.type
class UnidadOrganizativa:
    id: int
    codigo: str
    nombre: str
    email_coordinador: str | None
    email_secretario: str | None
    email_tesorero: str | None
    activo: bool
