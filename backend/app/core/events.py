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
# Event Bus
# -----------------------------------------------------------------------

AsyncHandler = Callable[[Any], Coroutine[Any, Any, None]]


class EventBus:
    """Bus in-process. Handlers son coroutines; se lanzan en background tasks."""

    def __init__(self) -> None:
        self._handlers: Dict[Type[DomainEvent], List[AsyncHandler]] = defaultdict(list)

    def subscribe(self, event_type: Type[DomainEvent], handler: AsyncHandler) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        handlers = self._handlers.get(type(event), [])
        for h in handlers:
            try:
                await h(event)
            except Exception:
                logger.exception(
                    "Error en handler %s para evento %s",
                    h.__name__,
                    type(event).__name__,
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
        event_bus.subscribe(event_type, _invalidate)
