"""Modelos del módulo de actividades."""

from app.modules.configuracion.models.estados import (
    EstadoAccion,
    EstadoTarea,
)
from .actividad import (
    TipoActividad,
    TipoAccion,  # alias de compatibilidad
    Actividad,
    Accion,      # alias de compatibilidad
    Participacion,
    PartidaPresupuestoActividad,
    RegistroTrabajoActividad,
    DocumentoActividad,
    DocumentoPartida,
)
from .tarea import Tarea
from .campana import (
    TipoCampania,
    TipoMeta,
    TipoCanalDifusion,
    Campania,
    MetaCampania,
    CanalDifusionCampania,
    PartidaPresupuestoCampania,
    PlantillaCampania,
    PlantillaMeta,
    PlantillaPartida,
    PlantillaActividad,
    PlantillaTarea,
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
    RequisitoRecurso,
    AportacionHoras,
)

__all__ = [
    # Estados (re-exportados desde configuracion)
    'EstadoAccion',
    'EstadoTarea',
    # Actividades
    'TipoActividad',
    'TipoAccion',
    'Actividad',
    'Accion',
    'Participacion',
    'PartidaPresupuestoActividad',
    'RegistroTrabajoActividad',
    'DocumentoActividad',
    'DocumentoPartida',
    'Tarea',
    # Campañas
    'TipoCampania',
    'TipoMeta',
    'TipoCanalDifusion',
    'Campania',
    'MetaCampania',
    'CanalDifusionCampania',
    'PartidaPresupuestoCampania',
    'PlantillaCampania',
    'PlantillaMeta',
    'PlantillaPartida',
    'PlantillaActividad',
    'PlantillaTarea',
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
    'RequisitoRecurso',
    'AportacionHoras',
]
