"""Shim: re-exporta desde el módulo canónico para compatibilidad de importaciones."""

from app.modules.configuracion.models.configuracion import (
    Configuracion,
    ReglaValidacionConfig,
    HistorialConfiguracion,
)

__all__ = ['Configuracion', 'ReglaValidacionConfig', 'HistorialConfiguracion']
