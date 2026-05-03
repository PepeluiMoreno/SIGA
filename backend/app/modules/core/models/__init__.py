"""Modelos del dominio core (funcionalidad base)."""

from .configuracion import Configuracion, ReglaValidacionConfig, HistorialConfiguracion
from .estados import (
    EstadoBase,
    EstadoCuota,
    EstadoCampania,
    EstadoTarea,
    EstadoParticipante,
    EstadoOrdenCobro,
    EstadoRemesa,
    EstadoDonacion,
    EstadoNotificacion,
    HistorialEstado,
)
from .seguridad import Sesion, HistorialSeguridad, IPBloqueada, IntentoAcceso

__all__ = [
    # Configuración
    'Configuracion',
    'ReglaValidacionConfig',
    'HistorialConfiguracion',
    # Estados
    'EstadoBase',
    'EstadoCuota',
    'EstadoCampania',
    'EstadoTarea',
    'EstadoParticipante',
    'EstadoOrdenCobro',
    'EstadoRemesa',
    'EstadoDonacion',
    'EstadoNotificacion',
    'HistorialEstado',
    # Seguridad
    'Sesion',
    'HistorialSeguridad',
    'IPBloqueada',
    'IntentoAcceso',
]
