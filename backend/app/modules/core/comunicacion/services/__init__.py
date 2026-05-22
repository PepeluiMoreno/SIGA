"""Servicios del subsistema de comunicación dirigida por flujos de trabajo.

Expone el `DestinatarioResolver`: traduce especificaciones de audiencia (rol,
cargo, permiso, usuario directo, ámbito territorial) a una lista concreta de
destinatarios.

El `NotificacionService` (creación in-app en lote + envío de email por
prioridad) vive en `app.infrastructure.services.notificacion_service`, junto al
resto de servicios de infraestructura, y consume este resolver.
"""

from .destinatario_resolver import (
    DestinatarioResolver,
    Destinatario,
    EspecificacionAudiencia,
    TipoAudiencia,
)

__all__ = [
    "DestinatarioResolver",
    "Destinatario",
    "EspecificacionAudiencia",
    "TipoAudiencia",
]
