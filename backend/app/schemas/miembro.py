import strawberry
from datetime import date

from .tipos_base import TipoMiembro, Pais, Provincia, UnidadOrganizativa


@strawberry.type
class Miembro:
    id: int
    nombre: str
    apellido1: str
    apellido2: str | None
    fecha_nacimiento: date | None

    tipo_documento: str | None
    numero_documento: str | None

    direccion: str | None
    codigo_postal: str | None
    localidad: str | None
    telefono: str | None

    iban: str | None
    fecha_alta: date
    fecha_baja: date | None

    tipo_miembro: TipoMiembro
    agrupacion: UnidadOrganizativa | None
    provincia: Provincia | None
    pais_domicilio: Pais | None


@strawberry.input
class MiembroInput:
    nombre: str
    apellido1: str
    apellido2: str | None = None
    fecha_nacimiento: date | None = None

    tipo_miembro_id: int

    tipo_documento: str | None = None
    numero_documento: str | None = None
    pais_documento_id: str | None = None

    direccion: str | None = None
    codigo_postal: str | None = None
    localidad: str | None = None
    provincia_id: str | None = None
    pais_domicilio_id: str | None = None

    telefono: str | None = None
    telefono2: str | None = None

    agrupacion_id: int | None = None
    iban: str | None = None


@strawberry.input
class MiembroUpdateInput:
    nombre: str | None = None
    apellido1: str | None = None
    apellido2: str | None = None
    fecha_nacimiento: date | None = None
    tipo_miembro_id: int | None = None
    tipo_documento: str | None = None
    numero_documento: str | None = None
    direccion: str | None = None
    codigo_postal: str | None = None
    localidad: str | None = None
    provincia_id: str | None = None
    pais_domicilio_id: str | None = None
    telefono: str | None = None
    agrupacion_id: int | None = None
    iban: str | None = None
