"""Modelos del módulo de acceso y control de permisos."""

from .transaccion import Transaccion
from .rol import Rol, TipoRol
from .rol_transaccion import RolTransaccion
from .funcionalidad import (
    Funcionalidad,
    RolFuncionalidad,
    FuncionalidadTransaccion,
    FlujoAprobacion,
    AmbitoTransaccion,
)
from .auditoria import LogAuditoria, TipoAccion
from .usuario import Usuario, UsuarioRol
from .seguridad import Sesion, HistorialSeguridad, IPBloqueada, IntentoAcceso

__all__ = [
    'Transaccion',
    'Rol',
    'TipoRol',
    'RolTransaccion',
    'Funcionalidad',
    'RolFuncionalidad',
    'FuncionalidadTransaccion',
    'FlujoAprobacion',
    'AmbitoTransaccion',
    'LogAuditoria',
    'TipoAccion',
    'Usuario',
    'UsuarioRol',
    'Sesion',
    'HistorialSeguridad',
    'IPBloqueada',
    'IntentoAcceso',
]
