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
# TipoVinculacion es ahora el catálogo CRM canónico (módulo membresía).
from ..modules.membresia.models import TipoVinculacion
from ..modules.acceso.models import Usuario, UsuarioRol

@strawchemy.type(TipoVinculacion, include="all", override=True)
class TipoVinculacionType:
    pass

@strawchemy.type(Usuario, exclude=["password_hash"], override=True)
class UsuarioType:
    pass

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
from ..modules.core.geografico import AmbitoGeografico, Pais, Provincia, Municipio, Direccion, UnidadOrganizativa, NivelOrganizativo, EntidadGeografica

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

@strawchemy.type(EntidadGeografica, include="all", exclude=["padre", "hijos"], override=True)
class EntidadGeograficaType:
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
    MotivoReduccionCuota,
    SolicitudReduccionCuota,
    SolicitudReduccionCuotaDocumento,
    DonacionConcepto,
    Donacion,
    Remesa,
    OrdenCobro,
    Recibo,
    JustificanteGasto,
    JustificanteGastoLinea,
    JustificanteGastoDocumento,
    CategoriaFiscal,
    ReglaCategorizacion,
    EstadoPlanificacion,
    CategoriaPartida,
    PartidaPresupuestaria,
    CompromisoPresupuestario,
    PlanificacionAnual,
    ModificacionPresupuestaria,
    FormaPago,
    CuentaBancaria,
    ApunteCaja,
    ExtractoBancario,
    MovimientoTesoreria,
    ConciliacionBancaria,
    CuentaContable,
    AsientoContable,
    ApunteContable,
)

@strawchemy.type(ImporteCuotaAnio, include="all", override=True)
class ImporteCuotaAnioType:
    pass

@strawchemy.type(CuotaAnual, include="all", override=True)
class CuotaAnualType:
    @strawberry.field
    def miembro(self) -> Optional['ContactoType']:
        """Compat: la cuota cuelga de la vinculación de socio; expone su contacto."""
        vs = getattr(self, 'vinculacion_socio', None)
        return vs.contacto if vs else None

@strawchemy.type(MotivoReduccionCuota, include="all", override=True)
class MotivoReduccionCuotaType:
    # Marker para que strawchemy procese el body con campos custom
    descripcion: Optional[str] = None

    @strawberry.field
    def excluye_cuota(self) -> bool:
        """D1.4: % ≥ 100 ⇒ no se genera CuotaAnual para miembros con este motivo."""
        from decimal import Decimal
        return self.porcentaje_reduccion is not None and self.porcentaje_reduccion >= Decimal("100.00")

@strawchemy.type(SolicitudReduccionCuota, include="all", override=True)
class SolicitudReduccionCuotaType:
    # resolutor sale de resuelto_por_id (nullable mientras está PRESENTADA)
    resolutor: Optional['ContactoType'] = None

@strawchemy.type(SolicitudReduccionCuotaDocumento, include="all", override=True)
class SolicitudReduccionCuotaDocumentoType:
    pass

@strawchemy.type(DonacionConcepto, include="all", override=True)
class DonacionConceptoType:
    pass

@strawchemy.type(Donacion, include="all", override=True)
class DonacionType:
    # Marker para que strawchemy procese el body con campos custom escalares.
    observaciones: Optional[str] = None

    # Compat: los datos del donante salen del Contacto (ya no hay donante_* en Donacion).
    @strawberry.field
    def donante_nombre(self) -> Optional[str]:
        return self.contacto.nombre_completo if self.contacto else None

    @strawberry.field
    def donante_dni(self) -> Optional[str]:
        return self.contacto.numero_documento if self.contacto else None

    @strawberry.field
    def donante_email(self) -> Optional[str]:
        return self.contacto.email if self.contacto else None

    @strawberry.field
    def donante_telefono(self) -> Optional[str]:
        return self.contacto.telefono if self.contacto else None

@strawchemy.type(Remesa, include="all", override=True)
class RemesaType:
    agrupacion: Optional['UnidadOrganizativaType'] = None

@strawchemy.type(OrdenCobro, include="all", override=True)
class OrdenCobroType:
    pass

@strawchemy.type(Recibo, include="all", override=True)
class ReciboType:
    @strawberry.field
    def miembro(self) -> Optional['ContactoType']:
        """Compat: el recibo cuelga de la vinculación de socio; expone su contacto."""
        vs = getattr(self, 'vinculacion_socio', None)
        return vs.contacto if vs else None

@strawchemy.type(JustificanteGasto, include="all", override=True)
class JustificanteGastoType:
    # Relaciones que pueden estar vacías mientras el justificante avanza por estados
    aceptador: Optional['ContactoType'] = None
    aprobador: Optional['ContactoType'] = None
    partida_actividad: Optional['PartidaPresupuestoActividadType'] = None
    agrupacion: Optional['UnidadOrganizativaType'] = None
    cuenta_bancaria: Optional['CuentaBancariaType'] = None
    apunte_caja: Optional['ApunteCajaType'] = None
    cuenta_contable: Optional['CuentaContableType'] = None
    presentado_por_tesorero: Optional['ContactoType'] = None

@strawchemy.type(JustificanteGastoLinea, include="all", override=True)
class JustificanteGastoLineaType:
    pass

@strawchemy.type(JustificanteGastoDocumento, include="all", override=True)
class JustificanteGastoDocumentoType:
    pass

@strawchemy.type(CategoriaFiscal, include="all", override=True)
class CategoriaFiscalType:
    pass

@strawchemy.type(ReglaCategorizacion, include="all", override=True)
class ReglaCategorizacionType:
    pass

@strawchemy.type(FormaPago, include="all", override=True)
class FormaPagoType:
    pass

@strawchemy.type(ModificacionPresupuestaria, include="all", override=True)
class ModificacionPresupuestariaType:
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
    agrupacion: Optional['UnidadOrganizativaType'] = None

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

# === FINANCIERO — REGLAS CONTABLES ===
from ..modules.economico.models.contabilidad import ReglaContable

@strawchemy.type(ReglaContable, include="all", override=True)
class ReglaContableType:
    pass


# === COLABORACIONES ===
# El módulo `organizaciones` quedó obsoleto: TipoOrganizacion/Organizacion/
# EstadoConvenio/Convenio fueron sustituidos por Contacto PJ + TipoEntidadJuridica
# y el satélite Convenio de secretaría (resolvers propios en secretaria_resolvers).


# === MIEMBROS ===
from ..modules.membresia.models import (
    TipoMiembro, Contacto, EstadoMiembro, MotivoBaja,
    NivelEstudios, NivelHabilidad,
    CategoriaHabilidad, Habilidad, MiembroHabilidad, FranjaDisponibilidad,
    HistorialAgrupacion, SolicitudTraslado,
    JuntaDirectiva, HistorialNombramiento, CoordinacionTerritorial,
)

@strawchemy.type(TipoMiembro, include="all", override=True)
class TipoMiembroType:
    motivo_reduccion: Optional['MotivoReduccionCuotaType'] = None

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
    miembro: Optional['ContactoType'] = None
    agrupacion: Optional['UnidadOrganizativaType'] = None
    cargo: Optional['CargoType'] = None

@strawchemy.type(CoordinacionTerritorial, include="all", exclude=["fecha_asignacion"], override=True)
class CoordinacionTerritorialType:
    miembro: Optional['ContactoType'] = None
    agrupacion: Optional['UnidadOrganizativaType'] = None

# El antiguo MiembroType se sustituye por ContactoType (la identidad viva es el
# Contacto). Se exponen las columnas escalares y `vinculaciones` (facetas del
# contacto, ahora que VinculacionType existe) para que el directorio saque los
# badges de faceta en una sola query. Las participaciones/firmas se siguen
# consultando vía resolvers dedicados (y se excluyen aquí para no colisionar con
# ParticipacionType = AsistenciaActividad).
@strawchemy.type(
    Contacto, include="all", override=True,
    exclude=[
        "participaciones", "firmas_campania",
        "contactos_donde_represento", "representante_legal",
    ],
)
class ContactoType:
    """Identidad viva (persona física o jurídica)."""
    pass


# === VINCULACIONES (facetas CRM de un Contacto) ===
# Una Vinculacion es la faceta tipada de un Contacto (SOCIO, VOLUNTARIO, …) con
# su satélite de datos. Se exponen ahora como tipos GraphQL para poder navegar
# las facetas de un contacto (resolver `vinculacionesDeContacto`).
from ..modules.membresia.models import Vinculacion, Socio, Voluntario

@strawchemy.type(Socio, include="all", exclude=["vinculacion"], override=True)
class SocioType:
    """Satélite económico/administrativo de una vinculación de tipo SOCIO."""
    motivo_reduccion: Optional['MotivoReduccionCuotaType'] = None

@strawchemy.type(Voluntario, include="all", exclude=["vinculacion"], override=True)
class VoluntarioType:
    """Satélite de una vinculación de tipo VOLUNTARIO."""
    pass

@strawchemy.type(Vinculacion, include="all", override=True)
class VinculacionType:
    """Faceta tipada de un Contacto (socio, voluntario, …) con su satélite."""
    contacto: Optional['ContactoType'] = None
    tipo_vinculacion: Optional['TipoVinculacionType'] = None
    socio: Optional['SocioType'] = None
    voluntario: Optional['VoluntarioType'] = None


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
    FirmaCampania,
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
    responsable: Optional['ContactoType'] = None

# RolParticipante/ParticipanteCampania/Firmante se disolvieron en el modelo
# Contacto + Participacion + Vinculacion; sus tipos GraphQL quedan retirados.

@strawchemy.type(FirmaCampania, include="all", override=True)
class FirmaCampaniaType:
    pass


# === ACTIVIDADES ===
from ..modules.actividades.models import (
    TipoActividad, TipoAccion, Actividad, Accion, Tarea, AsistenciaActividad,
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
    responsable: Optional['ContactoType'] = None

# Alias de compatibilidad
AccionType = ActividadType

@strawchemy.type(Tarea, include="all", override=True)
class TareaType:
    estado: Optional['EstadoTareaType'] = None
    responsable: Optional['ContactoType'] = None
    habilidad: Optional['HabilidadType'] = None
    nivel_habilidad: Optional['NivelHabilidadType'] = None

# `Participacion` (actividades) se renombró a `AsistenciaActividad`. Se conserva
# el nombre GraphQL `ParticipacionType` por compatibilidad con el frontend.
@strawchemy.type(AsistenciaActividad, include="all", override=True)
class ParticipacionType:
    miembro: Optional['ContactoType'] = None

@strawchemy.type(PartidaPresupuestoActividad, include="all", override=True)
class PartidaPresupuestoActividadType:
    pass

@strawchemy.type(RegistroTrabajoActividad, include="all", override=True)
class RegistroTrabajoActividadType:
    miembro: Optional['ContactoType'] = None

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


# === PROTECCIÓN DE DATOS (RGPD) ===
from ..modules.proteccion_datos.models import (
    EncargadoTratamiento, ActividadTratamiento, ActividadTratamientoEncargado,
    ClausulaInformativa, Consentimiento, SolicitudDerechoRGPD,
    BrechaSeguridad, AuditoriaAccesoDatos,
)

@strawchemy.type(EncargadoTratamiento, include="all", override=True)
class EncargadoTratamientoType:
    pass

@strawchemy.type(ActividadTratamiento, include="all", override=True)
class ActividadTratamientoType:
    pass

@strawchemy.type(ActividadTratamientoEncargado, include="all", override=True)
class ActividadTratamientoEncargadoType:
    pass

@strawchemy.type(ClausulaInformativa, include="all", override=True)
class ClausulaInformativaType:
    pass

@strawchemy.type(Consentimiento, include="all", override=True)
class ConsentimientoType:
    pass

@strawchemy.type(SolicitudDerechoRGPD, include="all", override=True)
class SolicitudDerechoRGPDType:
    pass

@strawchemy.type(BrechaSeguridad, include="all", override=True)
class BrechaSeguridadType:
    pass

@strawchemy.type(AuditoriaAccesoDatos, include="all", override=True)
class AuditoriaAccesoDatosType:
    pass


# === SECRETARÍA — PLATAFORMAS TELEMÁTICAS ===
from ..modules.secretaria.models import PlataformaTelematica

@strawchemy.type(PlataformaTelematica, include="all", override=True)
class PlataformaTelematicaType:
    pass


