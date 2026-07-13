"""Resolutores de territorio: de una entidad a su agrupación.

El motor de permisos necesita saber **sobre qué** se actúa para poder decidir si el
objetivo cae dentro del ámbito territorial del usuario. Cada entidad llega a su
agrupación por un camino distinto (unas la tienen directa, otras a través de un
salto), y aquí se declara ese camino una sola vez.

Uso en un resolver:

    @strawberry.mutation(permission_classes=[
        RequireTransaction("MEMBRESIA_MIEMBRO_BAJA", objetivo=Objetivo.contacto("contacto_id"))
    ])
    async def dar_de_baja_socio(self, info, contacto_id: uuid.UUID, ...):

El guard toma el argumento `contacto_id` de la llamada, resuelve su agrupación y la
compara con el ámbito del usuario. Ver `graphql/permissions.py`.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Awaitable, Callable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


# Una entidad puede no tener agrupación (p. ej. una actividad de la organización
# central). Se distingue de «no encontrada», que es un error.
SIN_AGRUPACION = None


@dataclass(frozen=True)
class Objetivo:
    """Cómo llegar del argumento de un resolver a la entidad sobre la que se actúa.

    `arg` es el nombre del argumento de la mutación que trae el id de la entidad.

    Hay **dos ejes de comprobación**, y cada uno pregunta por algo distinto:

      - TERRITORIAL → «¿en qué agrupación está esto?».  Lo responde `resolver`.
      - PROPIO      → «¿de qué persona es esto?».       Lo responde `resolver_propio`.

    Una misma entidad contesta a las dos: un traslado está en la agrupación de origen
    *y* pertenece al miembro que se traslada. Por eso el objetivo declara ambos saltos y
    el motor usa el que corresponda al ámbito de la transacción. Si una entidad no tiene
    sentido en un eje, ese resolver devuelve `None` y el motor deniega (falla cerrado).
    """

    arg: str
    resolver: Callable[[AsyncSession, uuid.UUID], Awaitable[Optional[uuid.UUID]]]
    # El id del objetivo puede venir anidado en un input (data.id). Ruta opcional.
    ruta: Optional[str] = None
    # Salto entidad → contacto, para el eje PROPIO (autoservicio).
    resolver_propio: Optional[
        Callable[[AsyncSession, uuid.UUID], Awaitable[Optional[uuid.UUID]]]
    ] = None

    # ── Fábricas por entidad (el catálogo de «hops») ─────────────────────────

    @staticmethod
    def contacto(arg: str = "contacto_id", ruta: Optional[str] = None) -> "Objetivo":
        """Socio/contacto: su agrupación es directa; y en el eje PROPIO, el contacto
        sobre el que se actúa es el propio argumento."""
        return Objetivo(
            arg=arg, ruta=ruta,
            resolver=_agrupacion_de_contacto,
            resolver_propio=_identidad,
        )

    @staticmethod
    def unidad(arg: str = "unidad_id", ruta: Optional[str] = None) -> "Objetivo":
        """Unidad organizativa: ella misma ES la agrupación."""
        return Objetivo(arg=arg, ruta=ruta, resolver=_identidad)

    @staticmethod
    def cuenta_bancaria(arg: str = "cuenta_id", ruta: Optional[str] = None) -> "Objetivo":
        return Objetivo(arg=arg, ruta=ruta, resolver=_agrupacion_de_cuenta)

    @staticmethod
    def movimiento_tesoreria(arg: str = "movimiento_id", ruta: Optional[str] = None) -> "Objetivo":
        """Movimiento de tesorería: su territorio es el de la cuenta que mueve."""
        return Objetivo(arg=arg, ruta=ruta, resolver=_agrupacion_de_movimiento)

    @staticmethod
    def actividad(arg: str = "actividad_id", ruta: Optional[str] = None) -> "Objetivo":
        return Objetivo(arg=arg, ruta=ruta, resolver=_agrupacion_de_actividad)

    @staticmethod
    def reunion(arg: str = "reunion_id", ruta: Optional[str] = None) -> "Objetivo":
        return Objetivo(arg=arg, ruta=ruta, resolver=_agrupacion_de_reunion)

    @staticmethod
    def usuario(arg: str = "usuario_id", ruta: Optional[str] = None) -> "Objetivo":
        """Cuenta de usuario: su territorio es el de la persona a la que pertenece."""
        return Objetivo(arg=arg, ruta=ruta, resolver=_agrupacion_de_usuario)

    @staticmethod
    def vinculacion(arg: str = "vinculacion_id", ruta: Optional[str] = None) -> "Objetivo":
        """Vinculación: el territorio es el del contacto vinculado."""
        return Objetivo(arg=arg, ruta=ruta, resolver=_agrupacion_de_vinculacion)

    @staticmethod
    def solicitud_traslado(arg: str = "solicitud_id", ruta: Optional[str] = None) -> "Objetivo":
        """Solicitud de traslado. En el eje territorial se ancla en la agrupación de
        ORIGEN; en el eje propio, en el miembro que se traslada (para que él pueda
        cancelar la suya).

        Un traslado toca dos territorios, y cada extremo lo aprueba quien manda en él
        (`aprobar_traslado_origen` / `aprobar_traslado_destino`). Anclarlo en el origen
        sería erróneo para el paso de destino, así que esas dos mutaciones NO usan este
        objetivo: conservan su comprobación específica de dos lados. Aquí sirve para el
        resto de operaciones (rechazar, cancelar), donde el origen es el ámbito correcto.
        """
        return Objetivo(
            arg=arg, ruta=ruta,
            resolver=_agrupacion_origen_de_traslado,
            resolver_propio=_miembro_de_traslado,
        )


# ── Los saltos concretos ─────────────────────────────────────────────────────

async def _identidad(session: AsyncSession, entidad_id: uuid.UUID) -> Optional[uuid.UUID]:
    return entidad_id


async def _agrupacion_de_contacto(session: AsyncSession, contacto_id: uuid.UUID):
    from app.modules.membresia.models.contacto import Contacto
    return (await session.execute(
        select(Contacto.agrupacion_id).where(Contacto.id == contacto_id)
    )).scalar_one_or_none()


async def _agrupacion_de_cuenta(session: AsyncSession, cuenta_id: uuid.UUID):
    from app.modules.economico.models.tesoreria import CuentaBancaria
    return (await session.execute(
        select(CuentaBancaria.agrupacion_id).where(CuentaBancaria.id == cuenta_id)
    )).scalar_one_or_none()


async def _agrupacion_de_movimiento(session: AsyncSession, movimiento_id: uuid.UUID):
    from app.modules.economico.models.tesoreria import CuentaBancaria, MovimientoTesoreria
    return (await session.execute(
        select(CuentaBancaria.agrupacion_id)
        .join(MovimientoTesoreria, MovimientoTesoreria.cuenta_id == CuentaBancaria.id)
        .where(MovimientoTesoreria.id == movimiento_id)
    )).scalar_one_or_none()


async def _agrupacion_de_actividad(session: AsyncSession, actividad_id: uuid.UUID):
    from app.modules.actividades.models.actividad import Actividad
    return (await session.execute(
        select(Actividad.agrupacion_id).where(Actividad.id == actividad_id)
    )).scalar_one_or_none()


async def _agrupacion_de_reunion(session: AsyncSession, reunion_id: uuid.UUID):
    from app.modules.secretaria.models.reunion import Reunion
    return (await session.execute(
        select(Reunion.agrupacion_id).where(Reunion.id == reunion_id)
    )).scalar_one_or_none()


async def _agrupacion_de_vinculacion(session: AsyncSession, vinculacion_id: uuid.UUID):
    """La vinculación lleva su propia agrupación, pero es nullable (vínculos no
    territoriales). Si falta, el territorio es el del contacto vinculado — no se
    deniega por un campo opcional vacío."""
    from app.modules.membresia.models.vinculacion import Vinculacion
    fila = (await session.execute(
        select(Vinculacion.agrupacion_id, Vinculacion.contacto_id)
        .where(Vinculacion.id == vinculacion_id)
    )).first()
    if fila is None:
        return None
    agrupacion_id, contacto_id = fila
    if agrupacion_id is not None:
        return agrupacion_id
    return await _agrupacion_de_contacto(session, contacto_id)


async def _agrupacion_origen_de_traslado(session: AsyncSession, solicitud_id: uuid.UUID):
    from app.modules.membresia.models.traslados.modelos import SolicitudTraslado
    return (await session.execute(
        select(SolicitudTraslado.agrupacion_origen_id)
        .where(SolicitudTraslado.id == solicitud_id)
    )).scalar_one_or_none()


async def _miembro_de_traslado(session: AsyncSession, solicitud_id: uuid.UUID):
    from app.modules.membresia.models.traslados.modelos import SolicitudTraslado
    return (await session.execute(
        select(SolicitudTraslado.miembro_id)
        .where(SolicitudTraslado.id == solicitud_id)
    )).scalar_one_or_none()


async def _agrupacion_de_usuario(session: AsyncSession, usuario_id: uuid.UUID):
    from app.modules.acceso.models.usuario import Usuario
    from app.modules.membresia.models.contacto import Contacto
    contacto_id = (await session.execute(
        select(Usuario.contacto_id).where(Usuario.id == usuario_id)
    )).scalar_one_or_none()
    if contacto_id is None:
        return None
    return await _agrupacion_de_contacto(session, contacto_id)
