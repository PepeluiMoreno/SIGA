"""Modelos del dominio de actividades."""

from .catalogos import (
    TipoActividad,
    EstadoPropuesta,
    TipoRecurso,
    TipoKPI,
)
from ...core.models.estados import EstadoActividad
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

__all__ = [
    # Catálogos
    "TipoActividad",
    "EstadoActividad",
    "EstadoPropuesta",
    "TipoRecurso",
    "TipoKPI",
    # Propuestas
    "PropuestaActividad",
    "TareaPropuesta",
    "RecursoPropuesta",
    "GrupoPropuesta",
    # Actividades
    "Actividad",
    "TareaActividad",
    "RecursoActividad",
    "GrupoActividad",
    "ParticipanteActividad",
    # KPIs
    "KPI",
    "KPIActividad",
    "MedicionKPI",
]
