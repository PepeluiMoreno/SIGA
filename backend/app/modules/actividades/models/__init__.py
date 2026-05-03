"""Modelos del módulo de actividades."""

from .catalogos import (
    TipoActividad,
    EstadoPropuesta,
    TipoRecurso,
    TipoKPI,
)
from .actividad import (
    PropuestaActividad,
    TareaPropuesta,
    RecursoPropuesta,
    GrupoPropuesta,
    Actividad,
    TareaActividad,
    RecursoActividad,
    GrupoActividad,
    ParticipanteActividad,
    KPI,
    KPIActividad,
    MedicionKPI,
)
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
    TareaGrupo,
    ReunionGrupo,
    AsistenteReunion,
)
from .evento import (
    TipoEvento,
    EstadoEvento,
    Evento,
    ParticipanteEvento,
    MaterialEvento,
    GrupoEvento,
    TareaEvento,
    GastoEvento,
)

__all__ = [
    # Catálogos
    'TipoActividad',
    'EstadoPropuesta',
    'TipoRecurso',
    'TipoKPI',
    # Actividades y propuestas
    'PropuestaActividad',
    'TareaPropuesta',
    'RecursoPropuesta',
    'GrupoPropuesta',
    'Actividad',
    'TareaActividad',
    'RecursoActividad',
    'GrupoActividad',
    'ParticipanteActividad',
    'KPI',
    'KPIActividad',
    'MedicionKPI',
    # Campañas
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
    'TareaGrupo',
    'ReunionGrupo',
    'AsistenteReunion',
    # Eventos
    'TipoEvento',
    'EstadoEvento',
    'Evento',
    'ParticipanteEvento',
    'MaterialEvento',
    'GrupoEvento',
    'TareaEvento',
    'GastoEvento',
]
