# Compatibilidad: lógica movida a actividad_resolvers.py
from .actividad_resolvers import (  # noqa: F401
    ActividadCreateData, ActividadUpdateData,
    TareaCreateData, TareaUpdateData,
    ParticipacionCreateData,
    ActividadResolverMutation as AccionResolverMutation,
)
