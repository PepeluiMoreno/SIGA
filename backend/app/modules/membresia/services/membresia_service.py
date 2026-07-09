"""Capa de servicio del módulo de membresía.

Estado actual (2026-07): la lógica de membresía vive repartida así:

- **Auto-alta pública de socio** (doble opt-in, SOCIO_ASPIRANTE):
  ``solicitud_socio_publica_service.SolicitudSocioPublicaService``.
- **Gestión por gestores** (crear/actualizar/aprobar/exportar…): resolvers de
  ``app/graphql/membresia_resolvers.py``.
- **Vinculaciones y ciclo de vida** (suspender/baja/reactivar, simpatizante→socio,
  traslados): resolvers de ``app/graphql/vinculaciones_resolvers.py``.

La extracción de esa lógica de resolvers a servicios está en curso en la rama
``refactor/coherencia-modulos``; este módulo queda como punto de anclaje para
esa migración.
"""
from .solicitud_socio_publica_service import SolicitudSocioPublicaService

__all__ = ["SolicitudSocioPublicaService"]
