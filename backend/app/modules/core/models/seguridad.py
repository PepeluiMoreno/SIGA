"""Shim: re-exporta desde el módulo canónico para compatibilidad de importaciones."""

from app.modules.acceso.models.seguridad import (
    Sesion,
    HistorialSeguridad,
    IPBloqueada,
    IntentoAcceso,
)

__all__ = ['Sesion', 'HistorialSeguridad', 'IPBloqueada', 'IntentoAcceso']
