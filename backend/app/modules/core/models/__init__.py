"""
Shim de compatibilidad: re-exporta modelos desde sus nuevos módulos.

Los modelos de core fueron redistribuidos:
- Configuracion, estados → modules/configuracion/
- Seguridad (Sesion, etc.) → modules/acceso/
- Geográfico → modules/core/geografico/
- Comunicación → modules/core/comunicacion/
"""

from ..geografico import Pais, Provincia, Municipio, Direccion, AgrupacionTerritorial
from ..comunicacion import TipoNotificacion, Notificacion, PreferenciaNotificacion
from ...configuracion.models import (
    Configuracion,
    ReglaValidacionConfig,
    HistorialConfiguracion,
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
from ...acceso.models import Sesion, HistorialSeguridad, IPBloqueada, IntentoAcceso

__all__ = [
    'Pais', 'Provincia', 'Municipio', 'Direccion', 'AgrupacionTerritorial',
    'TipoNotificacion', 'Notificacion', 'PreferenciaNotificacion',
    'Configuracion', 'ReglaValidacionConfig', 'HistorialConfiguracion',
    'EstadoBase', 'EstadoCuota', 'EstadoCampania', 'EstadoTarea',
    'EstadoActividad', 'EstadoParticipante', 'EstadoOrdenCobro',
    'EstadoRemesa', 'EstadoDonacion', 'EstadoNotificacion', 'HistorialEstado',
    'Sesion', 'HistorialSeguridad', 'IPBloqueada', 'IntentoAcceso',
]
