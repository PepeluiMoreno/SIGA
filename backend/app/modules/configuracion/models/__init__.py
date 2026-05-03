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
from .colaboraciones import TipoAsociacion, Asociacion, EstadoConvenio, Convenio
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
    # Colaboraciones externas
    'TipoAsociacion',
    'Asociacion',
    'EstadoConvenio',
    'Convenio',
    # Organizaciones
    'TipoOrganizacion',
    'Organizacion',
]
