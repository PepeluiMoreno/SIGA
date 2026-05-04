"""Módulos funcionales de la aplicación SIGA."""

# Acceso: autenticación, RBAC, funcionalidades, auditoría
from .acceso.models import (
    Transaccion,
    Rol,
    TipoRol,
    RolTransaccion,
    Funcionalidad,
    RolFuncionalidad,
    FuncionalidadTransaccion,
    FlujoAprobacion,
    AmbitoTransaccion,
    LogAuditoria,
    TipoAccion,
    Usuario,
    UsuarioRol,
    Sesion,
    HistorialSeguridad,
    IPBloqueada,
    IntentoAcceso,
)

# Core: geográfico y comunicación (transversales)
from .core.geografico import (
    Pais,
    Provincia,
    Municipio,
    Direccion,
    AgrupacionTerritorial,
)
from .core.comunicacion import (
    TipoNotificacion,
    Notificacion,
    PreferenciaNotificacion,
)

# Configuración: parámetros, estados, catálogos
from .configuracion.models import (
    Configuracion,
    ReglaValidacionConfig,
    HistorialConfiguracion,
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

# Organizaciones: convenios, tipos
from .organizaciones.models import (
    TipoOrganizacion,
    Organizacion,
    EstadoConvenio,
    Convenio,
)

# Membresía: miembros, voluntariado, traslados
from .membresia.models import (
    TipoMiembro,
    EstadoMiembro,
    MotivoBaja,
    Miembro,
    TipoCargo,
    Skill,
    MiembroSkill,
    FranjaDisponibilidad,
    HistorialAgrupacion,
    SolicitudTraslado,
    EstadoTraslado,
    CategoriaCompetencia,
    Competencia,
    NivelCompetencia,
    MiembroCompetencia,
    TipoDocumentoVoluntario,
    DocumentoMiembro,
    TipoFormacion,
    FormacionMiembro,
)

# Actividades: campañas, eventos, grupos de trabajo, KPIs
from .actividades.models import (
    TipoActividad,
    EstadoPropuesta,
    TipoRecurso,
    TipoKPI,
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
    TipoCampania,
    Campania,
    RolParticipante,
    ParticipanteCampania,
    Firmante,
    FirmaCampania,
    TipoGrupo,
    RolGrupo,
    GrupoTrabajo,
    MiembroGrupo,
    TareaGrupo,
    ReunionGrupo,
    AsistenteReunion,
    TipoEvento,
    EstadoEvento,
    Evento,
    ParticipanteEvento,
    MaterialEvento,
    GrupoEvento,
    TareaEvento,
    GastoEvento,
)

# Económico: tesorería, contabilidad, cuotas, donaciones, remesas, cobro
from .economico.models import (
    TipoMovimientoTesoreria,
    CuentaBancaria,
    MovimientoTesoreria,
    ConciliacionBancaria,
    TipoCuentaContable,
    TipoAsientoContable,
    EstadoAsientoContable,
    CuentaContable,
    AsientoContable,
    ApunteContable,
    BalanceContable,
    ModoIngreso,
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
    ProveedorPago,
    TipoPago,
    Pago,
    EventoPago,
    Suscripcion,
    Reclamacion,
    AccionReclamacion,
)

__all__ = [
    # Acceso
    'Transaccion', 'Rol', 'TipoRol', 'RolTransaccion',
    'Funcionalidad', 'RolFuncionalidad', 'FuncionalidadTransaccion',
    'FlujoAprobacion', 'AmbitoTransaccion',
    'LogAuditoria', 'TipoAccion',
    'Usuario', 'UsuarioRol',
    'Sesion', 'HistorialSeguridad', 'IPBloqueada', 'IntentoAcceso',
    # Core - Geográfico
    'Pais', 'Provincia', 'Municipio', 'Direccion', 'AgrupacionTerritorial',
    # Core - Comunicación
    'TipoNotificacion', 'Notificacion', 'PreferenciaNotificacion',
    # Configuración
    'Configuracion', 'ReglaValidacionConfig', 'HistorialConfiguracion',
    'EstadoBase', 'EstadoCuota', 'EstadoCampania', 'EstadoTarea',
    'EstadoActividad', 'EstadoParticipante', 'EstadoOrdenCobro',
    'EstadoRemesa', 'EstadoDonacion', 'EstadoNotificacion', 'HistorialEstado',
    # Organizaciones
    'TipoOrganizacion', 'Organizacion', 'EstadoConvenio', 'Convenio',
    # Membresía
    'TipoMiembro', 'EstadoMiembro', 'MotivoBaja', 'Miembro',
    'TipoCargo', 'Skill', 'MiembroSkill', 'FranjaDisponibilidad',
    'HistorialAgrupacion', 'SolicitudTraslado', 'EstadoTraslado',
    'CategoriaCompetencia', 'Competencia', 'NivelCompetencia', 'MiembroCompetencia',
    'TipoDocumentoVoluntario', 'DocumentoMiembro', 'TipoFormacion', 'FormacionMiembro',
    # Actividades
    'TipoActividad', 'EstadoPropuesta', 'TipoRecurso', 'TipoKPI',
    'PropuestaActividad', 'TareaPropuesta', 'RecursoPropuesta', 'GrupoPropuesta',
    'Actividad', 'TareaActividad', 'RecursoActividad', 'GrupoActividad',
    'ParticipanteActividad', 'KPI', 'KPIActividad', 'MedicionKPI',
    'TipoCampania', 'Campania', 'RolParticipante', 'ParticipanteCampania',
    'Firmante', 'FirmaCampania',
    'TipoGrupo', 'RolGrupo', 'GrupoTrabajo', 'MiembroGrupo',
    'TareaGrupo', 'ReunionGrupo', 'AsistenteReunion',
    'TipoEvento', 'EstadoEvento', 'Evento',
    'ParticipanteEvento', 'MaterialEvento', 'GrupoEvento', 'TareaEvento', 'GastoEvento',
    # Económico
    'TipoMovimientoTesoreria', 'CuentaBancaria', 'MovimientoTesoreria', 'ConciliacionBancaria',
    'TipoCuentaContable', 'TipoAsientoContable', 'EstadoAsientoContable',
    'CuentaContable', 'AsientoContable', 'ApunteContable', 'BalanceContable',
    'ModoIngreso', 'ImporteCuotaAnio', 'CuotaAnual',
    'DonacionConcepto', 'Donacion',
    'Remesa', 'OrdenCobro',
    'EstadoPlanificacion', 'CategoriaPartida', 'PartidaPresupuestaria', 'PlanificacionAnual',
    'ProveedorPago', 'TipoPago', 'Pago', 'EventoPago', 'Suscripcion',
    'Reclamacion', 'AccionReclamacion',
]
