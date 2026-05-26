"""Event bus in-process para eventos de dominio.

Diseño: síncrono en registro, async en dispatch.
Evolucionable a Redis Pub/Sub o RabbitMQ sin cambiar la interfaz.

Eventos que invalidan la PermissionMatrix:
  RoleCreated, RoleUpdated, RoleDeleted
  PermissionChanged, FunctionalityChanged
  CargoAssigned, CargoRevoked
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Coroutine, Dict, List, Optional, Type
import uuid

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------
# Base
# -----------------------------------------------------------------------

@dataclass(frozen=True)
class DomainEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)


# -----------------------------------------------------------------------
# Eventos de roles y permisos
# -----------------------------------------------------------------------

@dataclass(frozen=True)
class RoleCreated(DomainEvent):
    role_id: str = ""
    role_codigo: str = ""

@dataclass(frozen=True)
class RoleUpdated(DomainEvent):
    role_id: str = ""

@dataclass(frozen=True)
class RoleDeleted(DomainEvent):
    role_id: str = ""

@dataclass(frozen=True)
class PermissionChanged(DomainEvent):
    """Transacción añadida o eliminada de un rol."""
    role_id: str = ""
    transaction_id: str = ""

@dataclass(frozen=True)
class FunctionalityChanged(DomainEvent):
    """Funcionalidad añadida, eliminada o modificada en un rol."""
    role_id: str = ""
    functionality_id: str = ""

# -----------------------------------------------------------------------
# Eventos de cargos y juntas
# -----------------------------------------------------------------------

@dataclass(frozen=True)
class CargoAssigned(DomainEvent):
    usuario_id: str = ""
    cargo_codigo: str = ""
    agrupacion_id: Optional[str] = None

@dataclass(frozen=True)
class CargoRevoked(DomainEvent):
    usuario_id: str = ""
    cargo_codigo: str = ""
    agrupacion_id: Optional[str] = None

@dataclass(frozen=True)
class JuntaReconfigured(DomainEvent):
    agrupacion_id: str = ""


# -----------------------------------------------------------------------
# Eventos de flujos de trabajo que disparan avisos (secretaría, membresía)
# -----------------------------------------------------------------------

@dataclass(frozen=True)
class ReunionConvocada(DomainEvent):
    """Se ha convocado una reunión de un órgano de gobierno."""
    reunion_id: str = ""
    titulo: str = ""
    agrupacion_id: Optional[str] = None
    fecha: Optional[str] = None

@dataclass(frozen=True)
class ActaEnBorrador(DomainEvent):
    """Un acta ha quedado en borrador, pendiente de revisión."""
    acta_id: str = ""
    reunion_titulo: str = ""
    agrupacion_id: Optional[str] = None

@dataclass(frozen=True)
class ActaAprobada(DomainEvent):
    """Un acta ha sido aprobada y está lista para su firma."""
    acta_id: str = ""
    reunion_titulo: str = ""
    agrupacion_id: Optional[str] = None

@dataclass(frozen=True)
class NombramientoPendienteAprobacion(DomainEvent):
    """Un nombramiento de cargo está pendiente de aprobación."""
    nombramiento_id: str = ""
    cargo_nombre: str = ""
    miembro_nombre: str = ""
    agrupacion_id: Optional[str] = None

@dataclass(frozen=True)
class TrasladoSolicitado(DomainEvent):
    """Un socio ha solicitado el traslado a otra agrupación."""
    solicitud_id: str = ""
    miembro_nombre: str = ""
    agrupacion_destino_id: Optional[str] = None

@dataclass(frozen=True)
class TrasladoResuelto(DomainEvent):
    """Se ha resuelto una solicitud de traslado."""
    solicitud_id: str = ""
    miembro_id: str = ""
    aprobado: bool = False

@dataclass(frozen=True)
class RemesaDevolucion(DomainEvent):
    """El banco ha devuelto uno o varios adeudos de una remesa."""
    remesa_id: str = ""
    num_devoluciones: int = 0
    agrupacion_id: Optional[str] = None

@dataclass(frozen=True)
class GrupoTrabajoCreado(DomainEvent):
    """Se ha creado un grupo de trabajo (→ crear su canal de chat)."""
    grupo_id: str = ""
    nombre: str = ""

@dataclass(frozen=True)
class MiembroPerfilIncompleto(DomainEvent):
    """Un miembro ha sido creado/actualizado con campos clave sin rellenar
    (tipo_miembro_id, estado_id, email o telefono).

    Dispara avisos al propio miembro (si tiene cuenta) y a quien pueda
    editar miembros en su agrupación.
    """
    miembro_id: str = ""
    miembro_nombre: str = ""
    agrupacion_id: Optional[str] = None
    campos_faltantes: tuple = ()


# -----------------------------------------------------------------------
# Event Bus
# -----------------------------------------------------------------------

AsyncHandler = Callable[[Any], Coroutine[Any, Any, None]]


class EventBus:
    """Bus de eventos in-process.

    Dispatch NO bloqueante por defecto: al publicar, los handlers se lanzan como
    tareas en background (`asyncio.create_task`), de modo que quien publica no
    espera a que terminen. Esto desacopla temporalmente al emisor del consumidor
    (p. ej. aprobar un acta no espera al envío de avisos).

    Handlers SÍNCRONOS (opt-in con `subscribe(..., sync=True)`): se ejecutan en
    línea y `publish` espera a que completen antes de retornar. Reservado para
    handlers cuyo efecto debe estar garantizado al continuar — caso de la
    invalidación de la PermissionMatrix, donde servir permisos obsoletos sería un
    fallo de seguridad.

    Cada handler captura sus propias excepciones: un fallo en uno no afecta a los
    demás ni a quien publica. Limitaciones conocidas (sin durabilidad): si el
    proceso muere antes del dispatch, los eventos en vuelo se pierden. La
    evolución natural hacia entrega garantizada es un transactional outbox; ver
    docs/MODULO_COMUNICACION.md (no implementado).
    """

    def __init__(self) -> None:
        self._handlers: Dict[Type[DomainEvent], List[AsyncHandler]] = defaultdict(list)
        self._sync_handlers: Dict[Type[DomainEvent], List[AsyncHandler]] = defaultdict(list)
        # Mantener referencia fuerte a las tareas en vuelo para que el GC no las
        # cancele antes de completarse (asyncio solo guarda weakrefs).
        self._tasks: set[asyncio.Task] = set()

    def subscribe(
        self,
        event_type: Type[DomainEvent],
        handler: AsyncHandler,
        *,
        sync: bool = False,
    ) -> None:
        """Suscribe un handler. `sync=True` lo ejecuta en línea (publish espera)."""
        if sync:
            self._sync_handlers[event_type].append(handler)
        else:
            self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        event_type = type(event)

        # 1) Handlers síncronos: en línea, publish espera a que completen.
        for h in self._sync_handlers.get(event_type, []):
            try:
                await h(event)
            except Exception:
                logger.exception(
                    "Error en handler síncrono %s para evento %s",
                    getattr(h, "__name__", repr(h)), event_type.__name__,
                )

        # 2) Handlers asíncronos: en background, publish NO espera.
        for h in self._handlers.get(event_type, []):
            task = asyncio.create_task(self._run_background(h, event))
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)

    @staticmethod
    async def _run_background(handler: AsyncHandler, event: DomainEvent) -> None:
        try:
            await handler(event)
        except Exception:
            logger.exception(
                "Error en handler %s para evento %s",
                getattr(handler, "__name__", repr(handler)), type(event).__name__,
            )


# Instancia global
event_bus = EventBus()

# Eventos que requieren rebuild de la PermissionMatrix
_PERMISSION_INVALIDATING_EVENTS: tuple[Type[DomainEvent], ...] = (
    RoleCreated,
    RoleUpdated,
    RoleDeleted,
    PermissionChanged,
    FunctionalityChanged,
    CargoAssigned,
    CargoRevoked,
    JuntaReconfigured,
)


def wire_matrix_invalidation(session_factory: Callable) -> None:
    """Conecta el event bus con la invalidación de la PermissionMatrix.

    Llamar una vez en el lifespan de FastAPI, después de inicializar la matrix.
    """
    from ..modules.acceso.services.matrix import invalidate_and_rebuild

    async def _invalidate(event: DomainEvent) -> None:
        logger.info(
            "PermissionMatrix: invalidando por evento %s", type(event).__name__
        )
        async with session_factory() as session:
            await invalidate_and_rebuild(session)

    for event_type in _PERMISSION_INVALIDATING_EVENTS:
        event_bus.subscribe(event_type, _invalidate, sync=True)
