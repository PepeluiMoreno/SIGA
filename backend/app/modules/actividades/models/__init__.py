"""Modelos del módulo de actividades."""

from app.modules.configuracion.models.estados import (
    EstadoAccion,
    EstadoTarea,
)
from .accion import (
    TipoAccion,
    Accion,
    Participacion,
)
from .tarea import Tarea
from .campana import (
    TipoCampania,
    Campania,
    RolParticipante,
    ParticipanteCampania,
    Firmante,
    FirmaCampania,
)
from .grupo import (
    TipoGrupo,
    RolGrupo,
    GrupoTrabajo,
    MiembroGrupo,
    GrupoIniciativa,
    ReunionGrupo,
    AsistenteReunion,
)

__all__ = [
    # Estados (re-exportados desde configuracion)
    'EstadoAccion',
    'EstadoTarea',
    # Acciones
    'TipoAccion',
    'Accion',
    'Participacion',
    'Tarea',
    # Campañas (iniciativas estratégicas)
    'TipoCampania',
    'Campania',
    'RolParticipante',
    'ParticipanteCampania',
    'Firmante',
    'FirmaCampania',
    # Grupos de trabajo
    'TipoGrupo',
    'RolGrupo',
    'GrupoTrabajo',
    'MiembroGrupo',
    'GrupoIniciativa',
    'ReunionGrupo',
    'AsistenteReunion',
]
