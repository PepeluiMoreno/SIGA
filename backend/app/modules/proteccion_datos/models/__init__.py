"""Modelos del módulo Protección de Datos (RGPD)."""

from .encargado import EncargadoTratamiento
from .rat import ActividadTratamiento, ActividadTratamientoEncargado
from .clausula import ClausulaInformativa
from .consentimiento import Consentimiento
from .solicitud_derecho import SolicitudDerechoRGPD
from .brecha import BrechaSeguridad
from .auditoria_acceso import AuditoriaAccesoDatos

__all__ = [
    'EncargadoTratamiento',
    'ActividadTratamiento',
    'ActividadTratamientoEncargado',
    'ClausulaInformativa',
    'Consentimiento',
    'SolicitudDerechoRGPD',
    'BrechaSeguridad',
    'AuditoriaAccesoDatos',
]
