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

# === ADMINISTRACION ===
from ..modules.acceso.models import (
    Transaccion,
    Rol,
    RolTransaccion,
    LogAuditoria,
)

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


# === USUARIOS ===
from ..modules.acceso.models import Usuario, UsuarioRol

@strawchemy.type(Usuario, exclude=["password_hash"], override=True)
class UsuarioType:
    pass

@strawchemy.type(UsuarioRol, include="all", override=True)
class UsuarioRolType:
    pass


# === CORE ===
from ..modules.core.models import (
    Configuracion,
    ReglaValidacionConfig,
    HistorialConfiguracion,
    EstadoCuota,
    EstadoCampania,
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
from ..modules.geografico.models import Pais, Provincia, Municipio, Direccion, AgrupacionTerritorial

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

@strawchemy.type(AgrupacionTerritorial, include="all", override=True)
class AgrupacionTerritorialType:
    pass


# === NOTIFICACIONES ===
from ..modules.notificaciones.models import TipoNotificacion, Notificacion, PreferenciaNotificacion

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
    PlanificacionAnual,
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

@strawchemy.type(EstadoPlanificacion, include="all", override=True)
class EstadoPlanificacionType:
    pass

@strawchemy.type(CategoriaPartida, include="all", override=True)
class CategoriaPartidaType:
    pass

@strawchemy.type(PartidaPresupuestaria, include="all", override=True)
class PartidaPresupuestariaType:
    pass

@strawchemy.type(PlanificacionAnual, include="all", override=True)
class PlanificacionAnualType:
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
from ..modules.miembros.models import (
    TipoMiembro, Miembro, EstadoMiembro, MotivoBaja, TipoCargo, MiembroSegmentacion,
    Skill, MiembroSkill, FranjaDisponibilidad, HistorialAgrupacion, SolicitudTraslado,
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

@strawchemy.type(TipoCargo, include="all", override=True)
class TipoCargoType:
    pass

@strawchemy.type(Miembro, include="all", override=True)
class MiembroType:
    # Hacer nullable las relaciones opcionales que Strawchemy infiere como no-nullable
    agrupacion: Optional['AgrupacionTerritorialType'] = None
    provincia: Optional['ProvinciaType'] = None
    pais_documento: Optional['PaisType'] = None
    pais_domicilio: Optional['PaisType'] = None
    motivo_baja_rel: Optional['MotivoBajaType'] = None
    cargo: Optional['TipoCargoType'] = None

@strawchemy.type(MiembroSegmentacion, include="all", override=True)
class MiembroSegmentacionType:
    """Vista materializada para segmentación de miembros en campañas."""
    pass


# === MILITANCIA ===

@strawchemy.type(Skill, include="all", override=True)
class SkillType:
    pass

@strawchemy.type(MiembroSkill, include="all", override=True)
class MiembroSkillType:
    skill: Optional['SkillType'] = None

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
from ..modules.campanas.models import (
    TipoCampania, Campania, RolParticipante, ParticipanteCampania, Firmante, FirmaCampania
)

@strawchemy.type(TipoCampania, include="all", override=True)
class TipoCampaniaType:
    pass

@strawchemy.type(Campania, include="all", override=True)
class CampaniaType:
    # Hacer nullable las relaciones opcionales que Strawchemy infiere como no-nullable
    agrupacion: Optional['AgrupacionTerritorialType'] = None
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
    TipoActividad, EstadoActividad, EstadoPropuesta, TipoRecurso, TipoKPI,
    PropuestaActividad, TareaPropuesta, RecursoPropuesta, GrupoPropuesta,
    Actividad, TareaActividad, RecursoActividad, GrupoActividad, ParticipanteActividad,
    KPI, KPIActividad, MedicionKPI
)

@strawchemy.type(TipoActividad, include="all", override=True)
class TipoActividadType:
    pass

@strawchemy.type(EstadoActividad, include="all", override=True)
class EstadoActividadType:
    pass

@strawchemy.type(EstadoPropuesta, include="all", override=True)
class EstadoPropuestaType:
    pass

@strawchemy.type(TipoRecurso, include="all", override=True)
class TipoRecursoType:
    pass

@strawchemy.type(TipoKPI, include="all", override=True)
class TipoKPIType:
    pass

@strawchemy.type(PropuestaActividad, include="all", override=True)
class PropuestaActividadType:
    pass

@strawchemy.type(TareaPropuesta, include="all", override=True)
class TareaPropuestaType:
    pass

@strawchemy.type(RecursoPropuesta, include="all", override=True)
class RecursoPropuestaType:
    pass

@strawchemy.type(GrupoPropuesta, include="all", override=True)
class GrupoPropuestaType:
    pass

@strawchemy.type(Actividad, include="all", override=True)
class ActividadType:
    pass

@strawchemy.type(TareaActividad, include="all", override=True)
class TareaActividadType:
    pass

@strawchemy.type(RecursoActividad, include="all", override=True)
class RecursoActividadType:
    pass

@strawchemy.type(GrupoActividad, include="all", override=True)
class GrupoActividadType:
    pass

@strawchemy.type(ParticipanteActividad, include="all", override=True)
class ParticipanteActividadType:
    pass

@strawchemy.type(KPI, include="all", override=True)
class KPIType:
    pass

@strawchemy.type(KPIActividad, include="all", override=True)
class KPIActividadType:
    pass

@strawchemy.type(MedicionKPI, include="all", override=True)
class MedicionKPIType:
    pass


# === GRUPOS ===
from ..modules.grupos.models import (
    TipoGrupo, RolGrupo, GrupoTrabajo, MiembroGrupo, TareaGrupo, ReunionGrupo, AsistenteReunion
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

@strawchemy.type(TareaGrupo, include="all", override=True)
class TareaGrupoType:
    pass

@strawchemy.type(ReunionGrupo, include="all", override=True)
class ReunionGrupoType:
    pass

@strawchemy.type(AsistenteReunion, include="all", override=True)
class AsistenteReunionType:
    pass


# === VOLUNTARIADO ===
from ..modules.voluntariado.models import (
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


# === EVENTOS ===
from ..modules.eventos.models import (
    TipoEvento, EstadoEvento, Evento, ParticipanteEvento, MaterialEvento
)

@strawchemy.type(TipoEvento, include="all", override=True)
class TipoEventoType:
    pass

@strawchemy.type(EstadoEvento, include="all", override=True)
class EstadoEventoType:
    pass

@strawchemy.type(Evento, include="all", override=True)
class EventoType:
    pass

@strawchemy.type(ParticipanteEvento, include="all", override=True)
class ParticipanteEventoType:
    pass

@strawchemy.type(MaterialEvento, include="all", override=True)
class MaterialEventoType:
    pass
