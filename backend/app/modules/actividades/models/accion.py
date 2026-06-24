# Compatibilidad: las clases de este archivo han sido movidas a actividad.py.
# `Participacion` (actividades) se renombró a `AsistenciaActividad`.
from .actividad import (  # noqa: F401
    TipoActividad as TipoAccion,
    Actividad as Accion,
    AsistenciaActividad,
)
