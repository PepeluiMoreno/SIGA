"""Dominios de la aplicación siguiendo DDD (Domain-Driven Design)."""

# Usuarios domain
from .usuarios.models import (
    Usuario,
    UsuarioRol,
)

# Core domain
from .core.models import (
    # Configuración
    Configuracion,
    ReglaValidacionConfig,
    HistorialConfiguracion,
    # Estados
    EstadoBase,
    EstadoCuota,
    EstadoCampania,
    EstadoTarea,
    EstadoParticipante,
    EstadoOrdenCobro,
    EstadoRemesa,
    EstadoDonacion,
    HistorialEstado,
    # Seguridad
    Sesion,
    HistorialSeguridad,
    IPBloqueada,
    IntentoAcceso,
)

# Geographic domain
from .geografico.models import (
    Pais,
    Provincia,
    Municipio,
    Direccion,
    AgrupacionTerritorial,
)

# Notifications domain
from .notificaciones.models import (
    TipoNotificacion,
    Notificacion,
    PreferenciaNotificacion,
)

# Financiero domain
from .financiero.models import (
    ImporteCuotaAnio,
    CuotaAnual,
    DonacionConcepto,
    Donacion,
    Remesa,
    OrdenCobro,
    EstadoPlanificacion,
    CategoriaPartida,
    PartidaPresupuestaria,
    PlanificacionAnual,
)

# Colaboraciones domain
from .colaboraciones.models import (
    Asociacion,
    TipoAsociacion,
    Convenio,
    EstadoConvenio,
)

# Miembros domain
from .miembros.models import (
    TipoMiembro,
    Miembro,
)

# Campañas domain
from .campanas.models import (
    TipoCampania,
    Campania,
    RolParticipante,
    ParticipanteCampania,
)

# Actividades domain
from .actividades.models import (
    # Catálogos
    TipoActividad,
    EstadoActividad,
    EstadoPropuesta,
    TipoRecurso,
    TipoKPI,
    # Propuestas
    PropuestaActividad,
    TareaPropuesta,
    RecursoPropuesta,
    GrupoPropuesta,
    # Actividades
    Actividad,
    TareaActividad,
    RecursoActividad,
    GrupoActividad,
    ParticipanteActividad,
    # KPIs
    KPI,
    KPIActividad,
    MedicionKPI,
)

# Grupos domain
from .grupos.models import (
    TipoGrupo,
    RolGrupo,
    GrupoTrabajo,
    MiembroGrupo,
    TareaGrupo,
    ReunionGrupo,
    AsistenteReunion,
)

# Voluntariado domain
from .voluntariado.models import (
    CategoriaCompetencia,
    Competencia,
    NivelCompetencia,
    MiembroCompetencia,
    TipoDocumentoVoluntario,
    DocumentoMiembro,
    TipoFormacion,
    FormacionMiembro,
)

__all__ = [
    # Usuarios
    'Usuario',
    'UsuarioRol',
    # Core - Configuración
    'Configuracion',
    'ReglaValidacionConfig',
    'HistorialConfiguracion',
    # Core - Estados
    'EstadoBase',
    'EstadoCuota',
    'EstadoCampania',
    'EstadoTarea',
    'EstadoParticipante',
    'EstadoOrdenCobro',
    'EstadoRemesa',
    'EstadoDonacion',
    'HistorialEstado',
    # Core - Seguridad
    'Sesion',
    'HistorialSeguridad',
    'IPBloqueada',
    'IntentoAcceso',
    # Geográfico
    'Pais',
    'Provincia',
    'Municipio',
    'Direccion',
    'AgrupacionTerritorial',
    # Notificaciones
    'TipoNotificacion',
    'Notificacion',
    'PreferenciaNotificacion',
    # Financiero
    'ImporteCuotaAnio',
    'CuotaAnual',
    'DonacionConcepto',
    'Donacion',
    'Remesa',
    'OrdenCobro',
    'EstadoPlanificacion',
    'CategoriaPartida',
    'PartidaPresupuestaria',
    'PlanificacionAnual',
    # Colaboraciones
    'Asociacion',
    'TipoAsociacion',
    'Convenio',
    'EstadoConvenio',
    # Miembros
    'TipoMiembro',
    'Miembro',
    # Campañas
    'TipoCampania',
    'Campania',
    'RolParticipante',
    'ParticipanteCampania',
    # Actividades
    'TipoActividad',
    'EstadoActividad',
    'EstadoPropuesta',
    'TipoRecurso',
    'TipoKPI',
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
    # Grupos
    'TipoGrupo',
    'RolGrupo',
    'GrupoTrabajo',
    'MiembroGrupo',
    'TareaGrupo',
    'ReunionGrupo',
    'AsistenteReunion',
    # Voluntariado
    'CategoriaCompetencia',
    'Competencia',
    'NivelCompetencia',
    'MiembroCompetencia',
    'TipoDocumentoVoluntario',
    'DocumentoMiembro',
    'TipoFormacion',
    'FormacionMiembro',
]
