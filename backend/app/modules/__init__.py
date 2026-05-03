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

<<<<<<< HEAD
# Financiero domain
from .economico.models import (
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
=======
# Configuración: parámetros, estados, catálogos, organizaciones
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
>>>>>>> daab14f (redistribucion modules backend y completar modulo accesos, primera fase)
    TipoAsociacion,
    Asociacion,
    EstadoConvenio,
    Convenio,
    TipoOrganizacion,
    Organizacion,
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
    'TipoAsociacion', 'Asociacion', 'EstadoConvenio', 'Convenio',
    'TipoOrganizacion', 'Organizacion',
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
