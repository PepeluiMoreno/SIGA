"""Handlers de eventos de dominio que disparan avisos de comunicación.

Suscriben al `event_bus` los flujos de trabajo de secretaría y membresía y los
traducen a `NotificacionService.emitir(...)` con la audiencia adecuada (resuelta
por permiso/cargo/miembro). Mantienen los módulos de negocio desacoplados del de
comunicación: el emisor solo publica un evento; aquí se decide a quién y cómo.

Cada handler abre su propia sesión (los eventos se procesan fuera de la
transacción de negocio) y nunca propaga excepciones: un fallo de aviso no debe
afectar a la operación que lo originó (el event_bus ya captura, pero reforzamos).

Registro: llamar `wire_comunicacion_handlers(async_session)` una vez en el
lifespan de FastAPI, junto a `wire_matrix_invalidation`.
"""

from __future__ import annotations

import logging
from typing import Callable, Optional
from uuid import UUID

from app.core.events import (
    event_bus,
    ReunionConvocada,
    ActaEnBorrador,
    ActaAprobada,
    NombramientoPendienteAprobacion,
    TrasladoSolicitado,
    TrasladoResuelto,
    RemesaDevolucion,
)

logger = logging.getLogger(__name__)


def _uuid(val: Optional[str]) -> Optional[UUID]:
    if not val:
        return None
    try:
        return UUID(str(val))
    except (ValueError, TypeError):
        return None


def wire_comunicacion_handlers(session_factory: Callable) -> None:
    """Suscribe los handlers de comunicación al event bus."""

    # Imports diferidos para no acoplar el arranque ni crear ciclos.
    from app.infrastructure.services.notificacion_service import NotificacionService
    from app.modules.core.comunicacion.services import EspecificacionAudiencia

    async def _emitir(*, tipo_codigo, audiencia, titulo, mensaje,
                      entidad_tipo=None, entidad_id=None, url_accion=None):
        try:
            async with session_factory() as session:
                await NotificacionService(session).emitir(
                    tipo_codigo=tipo_codigo,
                    audiencia=audiencia,
                    titulo=titulo,
                    mensaje=mensaje,
                    entidad_tipo=entidad_tipo,
                    entidad_id=entidad_id,
                    url_accion=url_accion,
                )
        except Exception:
            logger.exception("Fallo emitiendo aviso de tipo %s", tipo_codigo)

    # ── Secretaría ────────────────────────────────────────────────────────

    async def _on_reunion_convocada(ev: ReunionConvocada) -> None:
        await _emitir(
            tipo_codigo="SECRETARIA_CONVOCATORIA",
            audiencia=EspecificacionAudiencia.por_permiso(
                "REUNION_REGISTRAR_ASIST", _uuid(ev.agrupacion_id)),
            titulo="Convocatoria de reunión",
            mensaje=f"Se ha convocado la reunión «{ev.titulo}»"
                    + (f" para el {ev.fecha}." if ev.fecha else "."),
            entidad_tipo="reunion", entidad_id=ev.reunion_id,
        )

    async def _on_acta_borrador(ev: ActaEnBorrador) -> None:
        await _emitir(
            tipo_codigo="SECRETARIA_ACTA_BORRADOR",
            audiencia=EspecificacionAudiencia.por_permiso(
                "ACTA_APROBAR", _uuid(ev.agrupacion_id)),
            titulo="Acta en borrador pendiente de revisión",
            mensaje=f"El acta de «{ev.reunion_titulo}» está en borrador y "
                    f"pendiente de revisión.",
            entidad_tipo="acta", entidad_id=ev.acta_id,
        )

    async def _on_acta_aprobada(ev: ActaAprobada) -> None:
        await _emitir(
            tipo_codigo="SECRETARIA_ACTA_APROBADA",
            audiencia=EspecificacionAudiencia.por_permiso(
                "ACTA_FIRMAR", _uuid(ev.agrupacion_id)),
            titulo="Acta aprobada, lista para firma",
            mensaje=f"El acta de «{ev.reunion_titulo}» ha sido aprobada y está "
                    f"lista para su firma.",
            entidad_tipo="acta", entidad_id=ev.acta_id,
        )

    # ── Membresía ─────────────────────────────────────────────────────────

    async def _on_nombramiento_pendiente(ev: NombramientoPendienteAprobacion) -> None:
        await _emitir(
            tipo_codigo="NOMBRAMIENTO_PENDIENTE_APROBACION",
            audiencia=EspecificacionAudiencia.por_permiso(
                "MEMBRESIA_CARGO_ASIGNAR", _uuid(ev.agrupacion_id)),
            titulo="Nombramiento pendiente de aprobación",
            mensaje=f"El nombramiento de {ev.miembro_nombre} como "
                    f"«{ev.cargo_nombre}» está pendiente de tu aprobación.",
            entidad_tipo="nombramiento", entidad_id=ev.nombramiento_id,
        )

    async def _on_traslado_solicitado(ev: TrasladoSolicitado) -> None:
        await _emitir(
            tipo_codigo="TRASLADO_SOLICITADO",
            audiencia=EspecificacionAudiencia.por_permiso(
                "MEMBRESIA_TRASLADO_APROBAR", _uuid(ev.agrupacion_destino_id)),
            titulo="Solicitud de traslado",
            mensaje=f"{ev.miembro_nombre} ha solicitado el traslado de agrupación.",
            entidad_tipo="solicitud_traslado", entidad_id=ev.solicitud_id,
        )

    async def _on_traslado_resuelto(ev: TrasladoResuelto) -> None:
        miembro_id = _uuid(ev.miembro_id)
        if miembro_id is None:
            return
        resultado = "aprobada" if ev.aprobado else "rechazada"
        await _emitir(
            tipo_codigo="TRASLADO_RESUELTO",
            audiencia=EspecificacionAudiencia.por_miembro(miembro_id),
            titulo="Resolución de tu solicitud de traslado",
            mensaje=f"Tu solicitud de traslado ha sido {resultado}.",
            entidad_tipo="solicitud_traslado", entidad_id=ev.solicitud_id,
        )

    # ── Económico ─────────────────────────────────────────────────────────

    async def _on_remesa_devolucion(ev: RemesaDevolucion) -> None:
        n = ev.num_devoluciones
        plural = "adeudos" if n != 1 else "adeudo"
        await _emitir(
            tipo_codigo="REMESA_DEVOLUCION",
            audiencia=EspecificacionAudiencia.por_permiso(
                "ECO_REMESA_ENVIAR", _uuid(ev.agrupacion_id)),
            titulo="Devolución de remesa",
            mensaje=f"El banco ha devuelto {n} {plural} de la remesa. "
                    f"Revisa las órdenes fallidas para gestionar el cobro.",
            entidad_tipo="remesa", entidad_id=ev.remesa_id,
        )

    # ── Suscripciones ─────────────────────────────────────────────────────

    event_bus.subscribe(ReunionConvocada, _on_reunion_convocada)
    event_bus.subscribe(ActaEnBorrador, _on_acta_borrador)
    event_bus.subscribe(ActaAprobada, _on_acta_aprobada)
    event_bus.subscribe(NombramientoPendienteAprobacion, _on_nombramiento_pendiente)
    event_bus.subscribe(TrasladoSolicitado, _on_traslado_solicitado)
    event_bus.subscribe(TrasladoResuelto, _on_traslado_resuelto)
    event_bus.subscribe(RemesaDevolucion, _on_remesa_devolucion)

    logger.info("Comunicación: 7 handlers de eventos suscritos al event bus.")
