"""Modelos del módulo de configuración."""

from .configuracion import Configuracion, ReglaValidacionConfig, HistorialConfiguracion
from .estados import (
    EstadoBase,
    EstadoCuota,
    EstadoCampania,
    EstadoTarea,
    EstadoActividad,
    EstadoParticipante,
    EstadoOrdenCobro,
    EstadoRemesa,
    EstadoDonacion,
    EstadoNotificacion,
    HistorialEstado,
)
from .organizacion import TipoOrganizacion, Organizacion

__all__ = [
    # Configuración del sistema
    'Configuracion',
    'ReglaValidacionConfig',
    'HistorialConfiguracion',
    # Estados por dominio
    'EstadoBase',
    'EstadoCuota',
    'EstadoCampania',
    'EstadoTarea',
    'EstadoActividad',
    'EstadoParticipante',
    'EstadoOrdenCobro',
    'EstadoRemesa',
    'EstadoDonacion',
    'EstadoNotificacion',
    'HistorialEstado',
    # Organizaciones (re-export from configuracion for compat)
    'TipoOrganizacion',
    'Organizacion',
]
