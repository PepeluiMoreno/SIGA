"""Modelos del dominio de administración."""

from .transaccion import Transaccion
from .rol import Rol, TipoRol
from .rol_transaccion import RolTransaccion
from .auditoria import LogAuditoria, TipoAccion

__all__ = [
    'Transaccion',
    'Rol',
    'TipoRol',
    'RolTransaccion',
    'LogAuditoria',
    'TipoAccion',
]
