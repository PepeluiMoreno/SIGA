"""
Imports de modelos para Alembic.
Centraliza todos los modelos para que Alembic los detecte en autogenerate.
"""

from ..infrastructure.base_model import Base

# Acceso
from ..modules.acceso.models import (
    Transaccion, Rol, TipoRol, RolTransaccion,
    Funcionalidad, RolFuncionalidad, FuncionalidadTransaccion,
    FlujoAprobacion, AmbitoTransaccion,
    LogAuditoria, TipoAccion,
    Usuario, UsuarioRol,
    Sesion, HistorialSeguridad, IPBloqueada, IntentoAcceso,
    Cargo, CargoRol,
)

# Core - Geográfico
from ..modules.core.geografico import (
    NivelOrganizativo, NaturalezaUnidad, VinculoUnidad,
    Pais, Provincia, Municipio, Direccion, UnidadOrganizativa,
)

# Core - Comunicación
from ..modules.core.comunicacion import TipoNotificacion, Notificacion, PreferenciaNotificacion

# Configuración
from ..modules.configuracion.models.tema_ui import TemaUI
from ..modules.configuracion.models import (
    Configuracion, ReglaValidacionConfig, HistorialConfiguracion,
    EstadoBase, EstadoCuota, EstadoCampania, EstadoAccion, EstadoTarea,
    EstadoParticipante, EstadoOrdenCobro,
    EstadoRemesa, EstadoDonacion, EstadoNotificacion, HistorialEstado,
)

# Organizaciones: OBSOLETO (sustituido por UnidadOrganizativa + Contacto PJ)
# Las clases TipoOrganizacion, Organizacion, EstadoConvenio, Convenio fueron eliminadas.

# Membresía
from ..modules.membresia.models import (
    TipoMiembro, EstadoMiembro, MotivoBaja, Miembro,
    JuntaDirectiva, HistorialNombramiento, CoordinacionTerritorial,
    Habilidad, MiembroHabilidad, FranjaDisponibilidad,
    HistorialAgrupacion, SolicitudTraslado, EstadoTraslado,
    CategoriaCompetencia, Competencia, NivelCompetencia, MiembroCompetencia,
    TipoDocumentoVoluntario, DocumentoMiembro, TipoFormacion, FormacionMiembro,
)

# Actividades
from ..modules.actividades.models import (
    TipoActividad, TipoAccion as TipoAccionActividades,
    Actividad, Accion, Participacion, Tarea,
    TipoCampania, Campania, RolParticipante, ParticipanteCampania,
    Firmante, FirmaCampania,
    TipoGrupo, RolGrupo, GrupoTrabajo, MiembroGrupo,
    GrupoIniciativa, ReunionGrupo, AsistenteReunion,
    RequisitoRecurso, AportacionHoras,
    TipoMeta, TipoCanalDifusion, MetaCampania, CanalDifusionCampania,
    PartidaPresupuestoCampania, PlantillaCampania, PlantillaMeta,
    PlantillaPartida, PlantillaActividad, PlantillaTarea,
)

# Económico
from ..modules.economico.models import (
    TipoMovimientoTesoreria, CuentaBancaria, MovimientoTesoreria, ConciliacionBancaria,
    TipoCuentaContable, TipoAsientoContable, EstadoAsientoContable,
    CuentaContable, AsientoContable, ApunteContable,
    ModoIngreso, ImporteCuotaAnio, CuotaAnual,
    DonacionConcepto, Donacion,
    Remesa, OrdenCobro,
    EstadoPlanificacion, CategoriaPartida, PartidaPresupuestaria, CompromisoPresupuestario, PlanificacionAnual,
    ProveedorPago, FormaPago, EstadoPago, TipoEventoPago, TipoPago, Pago, EventoPago,
    EstadoSuscripcion, Suscripcion,
    EstadoReclamacion, Reclamacion, TipoAccionReclamacion, AccionReclamacion,
)
