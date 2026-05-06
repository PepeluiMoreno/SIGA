"""Shim: re-exporta desde el módulo canónico para compatibilidad de importaciones."""

from app.modules.configuracion.models.estados import (
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

__all__ = [
    'EstadoBase', 'EstadoCuota', 'EstadoCampania', 'EstadoTarea',
    'EstadoActividad', 'EstadoParticipante', 'EstadoOrdenCobro',
    'EstadoRemesa', 'EstadoDonacion', 'EstadoNotificacion', 'HistorialEstado',
]
