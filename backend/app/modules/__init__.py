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
    UnidadOrganizativa,
)
from .core.comunicacion import (
    TipoNotificacion,
    Notificacion,
    PreferenciaNotificacion,
    PlantillaEmail,
)

# Configuración: parámetros, estados, catálogos
from .configuracion.models import (
    Configuracion,
    ReglaValidacionConfig,
    HistorialConfiguracion,
    EstadoBase,
    EstadoCuota,
    EstadoCampania,
    EstadoAccion,
    EstadoTarea,
    EstadoParticipante,
    EstadoOrdenCobro,
    EstadoRemesa,
    EstadoDonacion,
    EstadoNotificacion,
    EstadoReunion,
    EstadoActa,
    EstadoEjecucionAcuerdo,
    HistorialEstado,
)

# Membresía: contactos (CRM), miembros, voluntariado, traslados
from .membresia.models import (
    # Núcleo CRM (Party-Role): contactos, vinculaciones, participaciones
    Contacto,
    TipoEntidadJuridica,
    TipoVinculacion,
    Vinculacion,
    Socio,
    Voluntario,
    Participacion,
    Membresia,
    TipoMiembro,
    EstadoMiembro,
    MotivoBaja,
    Miembro,
    NivelEstudios,
    NivelHabilidad,
    JuntaDirectiva,
    HistorialNombramiento,
    CoordinacionTerritorial,
    CategoriaHabilidad,
    Habilidad,
    MiembroHabilidad,
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

# Actividades: campañas, actividades, grupos de trabajo
from .actividades.models import (
    TipoActividad,
    TipoAccion as TipoAccionActividades,
    Actividad,
    Accion,
    AsistenciaActividad,
    Tarea,
    TipoCampania,
    Campania,
    FirmaCampania,
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
    FormaPago,
    TipoPago,
    Pago,
    EventoPago,
    Suscripcion,
    Reclamacion,
    AccionReclamacion,
)

# Secretaría: reuniones, actas, libro de socios, convenios
from .secretaria.models import (
    TipoReunion,
    Reunion,
    AsistenteReunionSecretaria,
    PuntoOrdenDia,
    Acuerdo,
    VotacionAcuerdo,
    Acta,
    CertificadoAcuerdo,
    LibroSociosSnapshot,
    TipoConvenio,
    Convenio,
    DelegacionFirma,
    PlataformaTelematica,
)

# Protección de datos (RGPD / LOPDGDD)
from .proteccion_datos.models import (
    EncargadoTratamiento,
    ActividadTratamiento,
    ActividadTratamientoEncargado,
    ClausulaInformativa,
    Consentimiento,
    SolicitudDerechoRGPD,
    BrechaSeguridad,
    AuditoriaAccesoDatos,
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
    'Pais', 'Provincia', 'Municipio', 'Direccion', 'UnidadOrganizativa',
    # Core - Comunicación
    'TipoNotificacion', 'Notificacion', 'PreferenciaNotificacion', 'PlantillaEmail',
    # Configuración
    'Configuracion', 'ReglaValidacionConfig', 'HistorialConfiguracion',
    'EstadoBase', 'EstadoCuota', 'EstadoCampania', 'EstadoAccion', 'EstadoTarea',
    'EstadoParticipante', 'EstadoOrdenCobro',
    'EstadoRemesa', 'EstadoDonacion', 'EstadoNotificacion',
    'EstadoReunion', 'EstadoActa', 'EstadoEjecucionAcuerdo',
    'HistorialEstado',
    # Membresía — núcleo CRM (Party-Role)
    'Contacto', 'TipoEntidadJuridica', 'TipoVinculacion', 'Vinculacion',
    'Socio', 'Voluntario', 'Participacion', 'Membresia',
    # Membresía
    'TipoMiembro', 'EstadoMiembro', 'MotivoBaja', 'Miembro',
    'NivelEstudios', 'NivelHabilidad',
    'JuntaDirectiva', 'HistorialNombramiento', 'CoordinacionTerritorial',
    'CategoriaHabilidad', 'Habilidad', 'MiembroHabilidad', 'FranjaDisponibilidad',
    'HistorialAgrupacion', 'SolicitudTraslado', 'EstadoTraslado',
    'CategoriaCompetencia', 'Competencia', 'NivelCompetencia', 'MiembroCompetencia',
    'TipoDocumentoVoluntario', 'DocumentoMiembro', 'TipoFormacion', 'FormacionMiembro',
    # Actividades
    'TipoActividad', 'TipoAccionActividades', 'Actividad', 'Accion', 'AsistenciaActividad', 'Tarea',
    'TipoCampania', 'Campania', 'FirmaCampania',
    'TipoGrupo', 'RolGrupo', 'GrupoTrabajo', 'MiembroGrupo',
    'GrupoIniciativa', 'ReunionGrupo', 'AsistenteReunion',
    'RequisitoRecurso', 'AportacionHoras',
    # Secretaría
    'TipoReunion', 'Reunion', 'AsistenteReunionSecretaria',
    'PuntoOrdenDia', 'Acuerdo', 'VotacionAcuerdo',
    'Acta', 'CertificadoAcuerdo',
    'LibroSociosSnapshot',
    'TipoConvenio', 'Convenio', 'DelegacionFirma',
    'PlataformaTelematica',
    # Protección de datos (RGPD)
    'EncargadoTratamiento', 'ActividadTratamiento', 'ActividadTratamientoEncargado',
    'ClausulaInformativa', 'Consentimiento', 'SolicitudDerechoRGPD',
    'BrechaSeguridad', 'AuditoriaAccesoDatos',
]