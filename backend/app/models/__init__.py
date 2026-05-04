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
)

# Core - Geográfico
from ..modules.core.geografico import Pais, Provincia, Municipio, Direccion, AgrupacionTerritorial

# Core - Comunicación
from ..modules.core.comunicacion import TipoNotificacion, Notificacion, PreferenciaNotificacion

# Configuración
from ..modules.configuracion.models import (
    Configuracion, ReglaValidacionConfig, HistorialConfiguracion,
    EstadoBase, EstadoCuota, EstadoCampania, EstadoTarea,
    EstadoActividad, EstadoParticipante, EstadoOrdenCobro,
    EstadoRemesa, EstadoDonacion, EstadoNotificacion, HistorialEstado,
    TipoOrganizacion, Organizacion,
)

# Organizaciones
from ..modules.organizaciones.models import EstadoConvenio, Convenio

# Membresía
from ..modules.membresia.models import (
    TipoMiembro, EstadoMiembro, MotivoBaja, Miembro,
    TipoCargo, Skill, MiembroSkill, FranjaDisponibilidad,
    HistorialAgrupacion, SolicitudTraslado, EstadoTraslado,
    CategoriaCompetencia, Competencia, NivelCompetencia, MiembroCompetencia,
    TipoDocumentoVoluntario, DocumentoMiembro, TipoFormacion, FormacionMiembro,
)

# Actividades
from ..modules.actividades.models import (
    TipoActividad, EstadoPropuesta, TipoRecurso, TipoKPI,
    PropuestaActividad, TareaPropuesta, RecursoPropuesta, GrupoPropuesta,
    Actividad, TareaActividad, RecursoActividad, GrupoActividad,
    ParticipanteActividad, KPI, KPIActividad, MedicionKPI,
    TipoCampania, Campania, RolParticipante, ParticipanteCampania,
    Firmante, FirmaCampania,
    TipoGrupo, RolGrupo, GrupoTrabajo, MiembroGrupo,
    TareaGrupo, ReunionGrupo, AsistenteReunion,
    TipoEvento, EstadoEvento, Evento,
    ParticipanteEvento, MaterialEvento, GrupoEvento, TareaEvento, GastoEvento,
)

# Económico
from ..modules.economico.models import (
    TipoMovimientoTesoreria, CuentaBancaria, MovimientoTesoreria, ConciliacionBancaria,
    TipoCuentaContable, TipoAsientoContable, EstadoAsientoContable,
    CuentaContable, AsientoContable, ApunteContable, BalanceContable,
    ModoIngreso, ImporteCuotaAnio, CuotaAnual,
    DonacionConcepto, Donacion,
    Remesa, OrdenCobro,
    EstadoPlanificacion, CategoriaPartida, PartidaPresupuestaria, PlanificacionAnual,
    ProveedorPago, TipoPago, Pago, EventoPago, Suscripcion,
    Reclamacion, AccionReclamacion,
)
