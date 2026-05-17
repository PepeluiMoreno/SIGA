import strawberry
from datetime import date
from decimal import Decimal
from enum import Enum

from .tipos_base import UnidadOrganizativa
from .miembro import Miembro


@strawberry.enum
class EstadoCuota(Enum):
    PENDIENTE = "PENDIENTE"
    COBRADA = "COBRADA"
    COBRADA_PARCIAL = "COBRADA_PARCIAL"
    EXENTO = "EXENTO"
    DEVUELTA = "DEVUELTA"


@strawberry.enum
class ModoIngreso(Enum):
    SEPA = "SEPA"
    TRANSFERENCIA = "TRANSFERENCIA"
    PAYPAL = "PAYPAL"
    EFECTIVO = "EFECTIVO"


@strawberry.type
class ImporteCuotaAnio:
    id: int
    anio: int
    importe: Decimal


@strawberry.type
class CuotaAnio:
    id: int
    anio: int
    importe: Decimal
    importe_pagado: Decimal
    estado: EstadoCuota
    modo_ingreso: ModoIngreso | None
    fecha_pago: date | None
    observaciones: str | None
    miembro: Miembro
    agrupacion: UnidadOrganizativa


@strawberry.type
class DonacionConcepto:
    id: int
    codigo: str
    nombre: str
    activo: bool


@strawberry.type
class Donacion:
    id: int
    importe: Decimal
    gastos: Decimal
    fecha: date
    modo_ingreso: ModoIngreso | None
    observaciones: str | None
    miembro: Miembro
    concepto: DonacionConcepto | None


@strawberry.type
class OrdenCobro:
    id: int
    importe: Decimal
    estado: str
    cuota: CuotaAnio


@strawberry.type
class Remesa:
    id: int
    fecha: date
    importe_total: Decimal
    gastos: Decimal
    archivo_sepa: str | None
    observaciones: str | None
    ordenes: list[OrdenCobro]


# Inputs

@strawberry.input
class CuotaAnioInput:
    miembro_id: int
    anio: int
    agrupacion_id: int
    importe: Decimal


@strawberry.input
class PagoCuotaInput:
    cuota_id: int
    importe_pagado: Decimal
    modo_ingreso: ModoIngreso
    observaciones: str | None = None


@strawberry.input
class DonacionInput:
    miembro_id: int
    importe: Decimal
    concepto_id: int | None = None
    gastos: Decimal = Decimal("0")
    modo_ingreso: ModoIngreso | None = None
    observaciones: str | None = None


@strawberry.input
class RemesaInput:
    cuota_ids: list[int]
    observaciones: str | None = None
