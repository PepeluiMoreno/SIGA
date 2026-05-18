"""
Tipos GraphQL generados automáticamente desde todos los modelos SQLAlchemy.

Strawchemy genera automáticamente:
- Tipos GraphQL para cada modelo
- Resolvers optimizados
- Filtrado y paginación
- CRUD completo
"""

from typing import Optional
import strawberry
from . import strawchemy

# === ACCESO: roles, transacciones, funcionalidades, cargos ===
from ..modules.acceso.models import (
    Transaccion,
    Rol,
    RolTransaccion,
    LogAuditoria,
    Funcionalidad,
    RolFuncionalidad,
    FuncionalidadTransaccion,
    FlujoAprobacion,
)
from ..modules.acceso.models.cargo import Cargo, CargoRol

@strawchemy.type(Transaccion, include="all", override=True)
class TransaccionType:
    pass

@strawchemy.type(Rol, include="all", override=True)
class RolType:
    pass

@strawchemy.type(RolTransaccion, include="all", override=True)
class RolTransaccionType:
    pass

@strawchemy.type(LogAuditoria, include="all", override=True)
class LogAuditoriaType:
    pass

@strawchemy.type(Funcionalidad, include="all", override=True)
class FuncionalidadType:
    pass

@strawchemy.type(RolFuncionalidad, include="all", override=True)
class RolFuncionalidadType:
    pass

@strawchemy.type(FuncionalidadTransaccion, include="all", override=True)
class FuncionalidadTransaccionType:
    pass

@strawchemy.type(FlujoAprobacion, include="all", override=True)
class FlujoAprobacionType:
    pass


# === VINCULACIÓN Y USUARIOS ===
from ..modules.acceso.models import TipoVinculacion, Usuario, UsuarioRol

@strawchemy.type(TipoVinculacion, include="all", override=True)
class TipoVinculacionType:
    pass

@strawchemy.type(Usuario, exclude=["password_hash"], override=True)
class UsuarioType:
    tipo_vinculacion: Optional['TipoVinculacionType'] = None

@strawchemy.type(UsuarioRol, include="all", override=True)
class UsuarioRolType:
    pass


@strawchemy.type(CargoRol, include="all", override=True)
class CargoRolType:
    rol: Optional['RolType'] = None

@strawchemy.type(Cargo, include="all", override=True)
class CargoType:
    roles_sistema: list['CargoRolType'] = strawberry.field(default_factory=list)
    cargo_aprobador: Optional['CargoType'] = None


from ..modules.configuracion.models.tema_ui import TemaUI

@strawchemy.type(TemaUI, include="all", override=True)
class TemaUIType:
    pass


# === CORE ===
from ..modules.core.models import (
    Configuracion,
    ReglaValidacionConfig,
    HistorialConfiguracion,
    EstadoCuota,
    EstadoCampania,
    EstadoAccion,
    EstadoTarea,
    EstadoParticipante,
    EstadoOrdenCobro,
    EstadoRemesa,
    EstadoDonacion,
    EstadoNotificacion,
    HistorialEstado,
    Sesion,
    HistorialSeguridad,
    IPBloqueada,
    IntentoAcceso,
)

@strawchemy.type(Configuracion, include="all", override=True)
class ConfiguracionType:
    pass

@strawchemy.type(EstadoCuota, include="all", override=True)
class EstadoCuotaType:
    pass

@strawchemy.type(EstadoCampania, include="all", override=True)
class EstadoCampaniaType:
    pass

@strawchemy.type(EstadoAccion, include="all", override=True)
class EstadoAccionType:
    pass

@strawchemy.type(EstadoTarea, include="all", override=True)
class EstadoTareaType:
    pass

@strawchemy.type(EstadoParticipante, include="all", override=True)
class EstadoParticipanteType:
    pass

@strawchemy.type(EstadoOrdenCobro, include="all", override=True)
class EstadoOrdenCobroType:
    pass

@strawchemy.type(EstadoRemesa, include="all", override=True)
class EstadoRemesaType:
    pass

@strawchemy.type(EstadoDonacion, include="all", override=True)
class EstadoDonacionType:
    pass

@strawchemy.type(EstadoNotificacion, include="all", override=True)
class EstadoNotificacionType:
    pass

@strawchemy.type(Sesion, include="all", override=True)
class SesionType:
    pass

@strawchemy.type(ReglaValidacionConfig, include="all", override=True)
class ReglaValidacionConfigType:
    pass

@strawchemy.type(HistorialConfiguracion, include="all", override=True)
class HistorialConfiguracionType:
    pass

@strawchemy.type(HistorialEstado, include="all", override=True)
class HistorialEstadoType:
    pass

@strawchemy.type(HistorialSeguridad, include="all", override=True)
class HistorialSeguridadType:
    pass

@strawchemy.type(IPBloqueada, include="all", override=True)
class IPBloqueadaType:
    pass

@strawchemy.type(IntentoAcceso, include="all", override=True)
class IntentoAccesoType:
    pass


# === GEOGRÁFICO ===
from ..modules.core.geografico import AmbitoGeografico, Pais, Provincia, Municipio, Direccion, UnidadOrganizativa, NivelOrganizativo

@strawchemy.type(AmbitoGeografico, include="all", exclude=["niveles_organizativos"], override=True)
class AmbitoGeograficoType:
    pass

@strawchemy.type(NivelOrganizativo, include="all", override=True)
class NivelOrganizativoType:
    ambito_geografico: Optional['AmbitoGeograficoType'] = None

@strawchemy.type(Pais, include="all", override=True)
class PaisType:
    pass

@strawchemy.type(Provincia, include="all", override=True)
class ProvinciaType:
    pass

@strawchemy.type(Municipio, include="all", override=True)
class MunicipioType:
    pass

@strawchemy.type(Direccion, include="all", override=True)
class DireccionType:
    pass

@strawchemy.type(UnidadOrganizativa, include="all", exclude=["agrupacion_padre", "agrupaciones_hijas"], override=True)
class UnidadOrganizativaType:
    pass


# === NOTIFICACIONES Y PLANTILLAS EMAIL ===
from ..modules.core.comunicacion import TipoNotificacion, Notificacion, PreferenciaNotificacion, PlantillaEmail

@strawchemy.type(TipoNotificacion, include="all", override=True)
class TipoNotificacionType:
    pass

@strawchemy.type(Notificacion, exclude=["datos_adicionales"], override=True)
class NotificacionType:
    # Excluimos datos_adicionales porque es un campo JSON que requiere tratamiento especial
    pass

@strawchemy.type(PreferenciaNotificacion, include="all", override=True)
class PreferenciaNotificacionType:
    pass

@strawchemy.type(PlantillaEmail, exclude=["variables_disponibles"], override=True)
class PlantillaEmailType:
    pass


# === FINANCIERO ===
from ..modules.economico.models import (
    ImporteCuotaAnio,
    CuotaAnual,
    DonacionConcepto,
    Donacion,
    Remesa,
    OrdenCobro,
    EstadoPlanificacion,
    CategoriaPartida,
    PartidaPresupuestaria,
    CompromisoPresupuestario,
    PlanificacionAnual,
    FormaPago,
    CuentaBancaria,
    ApunteCaja,
    ExtractoBancario,
    MovimientoTesoreria,
    ConciliacionBancaria,
    CuentaContable,
    AsientoContable,
    ApunteContable,
    BalanceContable,
)

@strawchemy.type(ImporteCuotaAnio, include="all", override=True)
class ImporteCuotaAnioType:
    pass

@strawchemy.type(CuotaAnual, include="all", override=True)
class CuotaAnualType:
    pass

@strawchemy.type(DonacionConcepto, include="all", override=True)
class DonacionConceptoType:
    pass

@strawchemy.type(Donacion, include="all", override=True)
class DonacionType:
    pass

@strawchemy.type(Remesa, include="all", override=True)
class RemesaType:
    pass

@strawchemy.type(OrdenCobro, include="all", override=True)
class OrdenCobroType:
    pass

@strawchemy.type(FormaPago, include="all", override=True)
class FormaPagoType:
    pass

@strawchemy.type(EstadoPlanificacion, include="all", override=True)
class EstadoPlanificacionType:
    pass

@strawchemy.type(CategoriaPartida, include="all", override=True)
class CategoriaPartidaType:
    pass

@strawchemy.type(PartidaPresupuestaria, include="all", override=True)
class PartidaPresupuestariaType:
    pass

@strawchemy.type(CompromisoPresupuestario, include="all", override=True)
class CompromisoPresupuestarioType:
    pass

@strawchemy.type(PlanificacionAnual, include="all", override=True)
class PlanificacionAnualType:
    pass

@strawchemy.type(CuentaBancaria, include="all", override=True)
class CuentaBancariaType:
    pass

@strawchemy.type(ApunteCaja, include="all", override=True)
class ApunteCajaType:
    pass

@strawchemy.type(ExtractoBancario, include="all", override=True)
class ExtractoBancarioType:
    pass

@strawchemy.type(MovimientoTesoreria, include="all", override=True)
class MovimientoTesoreriaType:
    pass

@strawchemy.type(ConciliacionBancaria, include="all", override=True)
class ConciliacionBancariaType:
    pass

@strawchemy.type(CuentaContable, include="all", override=True)
class CuentaContableType:
    pass

@strawchemy.type(AsientoContable, include="all", override=True)
class AsientoContableType:
    pass

@strawchemy.type(ApunteContable, include="all", override=True)
class ApunteContableType:
    pass

@strawchemy.type(BalanceContable, include="all", override=True)
class BalanceContableType:
    pass


# === FINANCIERO — REGLAS CONTABLES ===
from ..modules.economico.models.contabilidad import ReglaContable

@strawchemy.type(ReglaContable, include="all", override=True)
class ReglaContableType:
    pass


# === COLABORACIONES ===
from ..modules.organizaciones.models import Organizacion, TipoOrganizacion, Convenio, EstadoConvenio

@strawchemy.type(TipoOrganizacion, include="all", override=True)
class TipoOrganizacionType:
    pass

@strawchemy.type(Organizacion, include="all", override=True)
class OrganizacionType:
    pass

@strawchemy.type(EstadoConvenio, include="all", override=True)
class EstadoConvenioType:
    pass

@strawchemy.type(Convenio, include="all", override=True)
class ConvenioType:
    pass


# === MIEMBROS ===
from ..modules.membresia.models import (
    TipoMiembro, Miembro, EstadoMiembro, MotivoBaja, MiembroSegmentacion,
    NivelEstudios, NivelHabilidad,
    CategoriaHabilidad, Habilidad, MiembroHabilidad, FranjaDisponibilidad,
    HistorialAgrupacion, SolicitudTraslado,
    JuntaDirectiva, HistorialNombramiento, CoordinacionTerritorial,
)

@strawchemy.type(TipoMiembro, include="all", override=True)
class TipoMiembroType:
    pass

@strawchemy.type(EstadoMiembro, include="all", override=True)
class EstadoMiembroType:
    pass

@strawchemy.type(MotivoBaja, include="all", override=True)
class MotivoBajaType:
    pass

@strawchemy.type(JuntaDirectiva, include="all", override=True)
class JuntaDirectivaType:
    pass

@strawchemy.type(HistorialNombramiento, include="all", override=True)
class HistorialNombramientoType:
    rol: Optional['RolType'] = None
    miembro: Optional['MiembroType'] = None
    agrupacion: Optional['UnidadOrganizativaType'] = None
    cargo: Optional['CargoType'] = None

@strawchemy.type(CoordinacionTerritorial, include="all", exclude=["fecha_asignacion"], override=True)
class CoordinacionTerritorialType:
    miembro: Optional['MiembroType'] = None
    agrupacion: Optional['UnidadOrganizativaType'] = None

@strawchemy.type(Miembro, include="all", override=True)
class MiembroType:
    # Hacer nullable las relaciones opcionales que Strawchemy infiere como no-nullable
    agrupacion: Optional['UnidadOrganizativaType'] = None
    provincia: Optional['ProvinciaType'] = None
    pais_documento: Optional['PaisType'] = None
    pais_domicilio: Optional['PaisType'] = None
    pais_nacimiento: Optional['PaisType'] = None
    motivo_baja_rel: Optional['MotivoBajaType'] = None
    usuario: Optional['UsuarioType'] = None
    nivel_estudios_rel: Optional['NivelEstudiosType'] = None

    @strawberry.field
    def tiene_acceso(self) -> bool:
        return self.usuario is not None

@strawchemy.type(MiembroSegmentacion, include="all", override=True)
class MiembroSegmentacionType:
    """Vista materializada para segmentación de miembros en campañas."""
    pass


# === MILITANCIA ===

@strawchemy.type(NivelEstudios, include="all", override=True)
class NivelEstudiosType:
    pass

@strawchemy.type(NivelHabilidad, include="all", override=True)
class NivelHabilidadType:
    pass

@strawchemy.type(CategoriaHabilidad, include="all", override=True)
class CategoriaHabilidadType:
    pass

@strawchemy.type(Habilidad, include="all", override=True)
class HabilidadType:
    categoria: Optional['CategoriaHabilidadType'] = None

@strawchemy.type(MiembroHabilidad, include="all", override=True)
class MiembroHabilidadType:
    habilidad: Optional['HabilidadType'] = None
    nivel_habilidad: Optional['NivelHabilidadType'] = None

@strawchemy.type(FranjaDisponibilidad, include="all", override=True)
class FranjaDisponibilidadType:
    pass

@strawchemy.type(HistorialAgrupacion, include="all", override=True)
class HistorialAgrupacionType:
    pass

@strawchemy.type(SolicitudTraslado, include="all", override=True)
class SolicitudTrasladoType:
    pass


# === CAMPAÑAS ===
from ..modules.actividades.models import (
    TipoCampania, TipoMeta, TipoCanalDifusion,
    Campania, MetaCampania, CanalDifusionCampania, PartidaPresupuestoCampania,
    PlantillaCampania, PlantillaMeta, PlantillaPartida, PlantillaActividad, PlantillaTarea,
    RolParticipante, ParticipanteCampania, Firmante, FirmaCampania,
)

@strawchemy.type(TipoMeta, include="all", override=True)
class TipoMetaType:
    pass

@strawchemy.type(TipoCanalDifusion, include="all", override=True)
class TipoCanalDifusionType:
    pass

@strawchemy.type(TipoCampania, include="all", override=True)
class TipoCampaniaType:
    pass

@strawchemy.type(MetaCampania, include="all", override=True)
class MetaCampaniaType:
    tipo_meta: Optional['TipoMetaType'] = None

@strawchemy.type(CanalDifusionCampania, include="all", override=True)
class CanalDifusionCampaniaType:
    canal: Optional['TipoCanalDifusionType'] = None

@strawchemy.type(PartidaPresupuestoCampania, include="all", override=True)
class PartidaPresupuestoCampaniaType:
    pass

@strawchemy.type(PlantillaMeta, include="all", override=True)
class PlantillaMetaType:
    tipo_meta: Optional['TipoMetaType'] = None

@strawchemy.type(PlantillaPartida, include="all", override=True)
class PlantillaPartidaType:
    pass

@strawchemy.type(PlantillaTarea, include="all", override=True)
class PlantillaTareaType:
    habilidad: Optional['HabilidadType'] = None
    nivel_habilidad: Optional['NivelHabilidadType'] = None

@strawchemy.type(PlantillaActividad, include="all", override=True)
class PlantillaActividadType:
    tipo_actividad: Optional['TipoActividadType'] = None

@strawchemy.type(PlantillaCampania, include="all", override=True)
class PlantillaCampaniaType:
    tipo_campania: Optional['TipoCampaniaType'] = None

@strawchemy.type(Campania, include="all", override=True)
class CampaniaType:
    agrupacion: Optional['UnidadOrganizativaType'] = None
    responsable: Optional['MiembroType'] = None

@strawchemy.type(RolParticipante, include="all", override=True)
class RolParticipanteType:
    pass

@strawchemy.type(ParticipanteCampania, include="all", override=True)
class ParticipanteCampaniaType:
    pass

@strawchemy.type(Firmante, include="all", override=True)
class FirmanteType:
    pass

@strawchemy.type(FirmaCampania, include="all", override=True)
class FirmaCampaniaType:
    pass


# === ACTIVIDADES ===
from ..modules.actividades.models import (
    TipoActividad, TipoAccion, Actividad, Accion, Tarea, Participacion,
    PartidaPresupuestoActividad, RegistroTrabajoActividad, DocumentoActividad, DocumentoPartida,
)


@strawchemy.type(TipoActividad, include="all", override=True)
class TipoActividadType:
    pass

# Alias de compatibilidad
TipoAccionType = TipoActividadType

@strawchemy.type(Actividad, include="all", override=True)
class ActividadType:
    tipo_actividad: Optional['TipoActividadType'] = None
    estado: Optional['EstadoAccionType'] = None
    campania: Optional['CampaniaType'] = None
    responsable: Optional['MiembroType'] = None

# Alias de compatibilidad
AccionType = ActividadType

@strawchemy.type(Tarea, include="all", override=True)
class TareaType:
    estado: Optional['EstadoTareaType'] = None
    responsable: Optional['MiembroType'] = None
    habilidad: Optional['HabilidadType'] = None
    nivel_habilidad: Optional['NivelHabilidadType'] = None

@strawchemy.type(Participacion, include="all", override=True)
class ParticipacionType:
    miembro: Optional['MiembroType'] = None

@strawchemy.type(PartidaPresupuestoActividad, include="all", override=True)
class PartidaPresupuestoActividadType:
    pass

@strawchemy.type(RegistroTrabajoActividad, include="all", override=True)
class RegistroTrabajoActividadType:
    miembro: Optional['MiembroType'] = None

@strawchemy.type(DocumentoActividad, include="all", override=True)
class DocumentoActividadType:
    subido_por: Optional['UsuarioType'] = None

@strawchemy.type(DocumentoPartida, include="all", override=True)
class DocumentoPartidaType:
    subido_por: Optional['UsuarioType'] = None


# === GRUPOS ===
from ..modules.actividades.models import (
    TipoGrupo, RolGrupo, GrupoTrabajo, MiembroGrupo, GrupoIniciativa, ReunionGrupo, AsistenteReunion,
    RequisitoRecurso, AportacionHoras,
)

@strawchemy.type(TipoGrupo, include="all", override=True)
class TipoGrupoType:
    pass

@strawchemy.type(RolGrupo, include="all", override=True)
class RolGrupoType:
    pass

@strawchemy.type(GrupoTrabajo, include="all", override=True)
class GrupoTrabajoType:
    pass

@strawchemy.type(MiembroGrupo, include="all", override=True)
class MiembroGrupoType:
    pass

@strawchemy.type(GrupoIniciativa, include="all", override=True)
class GrupoIniciativaType:
    pass

@strawchemy.type(ReunionGrupo, include="all", override=True)
class ReunionGrupoType:
    pass

@strawchemy.type(AsistenteReunion, include="all", override=True)
class AsistenteReunionType:
    pass

@strawchemy.type(RequisitoRecurso, include="all", override=True)
class RequisitoRecursoType:
    pass

@strawchemy.type(AportacionHoras, include="all", override=True)
class AportacionHorasType:
    pass


# === VOLUNTARIADO ===
from ..modules.membresia.models import (
    CategoriaCompetencia, Competencia, NivelCompetencia, MiembroCompetencia,
    TipoDocumentoVoluntario, DocumentoMiembro, TipoFormacion, FormacionMiembro
)

@strawchemy.type(CategoriaCompetencia, include="all", override=True)
class CategoriaCompetenciaType:
    pass

@strawchemy.type(Competencia, include="all", override=True)
class CompetenciaType:
    pass

@strawchemy.type(NivelCompetencia, include="all", override=True)
class NivelCompetenciaType:
    pass

@strawchemy.type(MiembroCompetencia, include="all", override=True)
class MiembroCompetenciaType:
    pass

@strawchemy.type(TipoDocumentoVoluntario, include="all", override=True)
class TipoDocumentoVoluntarioType:
    pass

@strawchemy.type(DocumentoMiembro, include="all", override=True)
class DocumentoMiembroType:
    pass

@strawchemy.type(TipoFormacion, include="all", override=True)
class TipoFormacionType:
    pass

@strawchemy.type(FormacionMiembro, include="all", override=True)
class FormacionMiembroType:
    pass


