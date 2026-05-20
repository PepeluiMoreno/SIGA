"""Servicios del módulo de Secretaría."""

from .reunion_service import ReunionService
from .acta_service import ActaService
from .libro_socios_service import LibroSociosService
from .convenio_service import ConvenioService

__all__ = [
    'ReunionService',
    'ActaService',
    'LibroSociosService',
    'ConvenioService',
]
