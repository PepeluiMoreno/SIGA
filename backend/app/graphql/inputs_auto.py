"""
Tipos de Input GraphQL generados automáticamente desde modelos SQLAlchemy.

Strawchemy genera automáticamente:
- Input types para Create (mode="create_input")
- Input types para Update by PK (mode="update_by_pk_input")
- Filter types para queries y deletes

Este módulo usa introspección de SQLAlchemy para:
1. Detectar automáticamente los campos de auditoría del mixin AuditoriaMixin
2. Detectar automáticamente todas las relaciones del modelo (relationship())
3. Excluirlos de los inputs para evitar conflictos de tipos anidados
"""

from typing import Type, List
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy import inspect

from . import strawchemy
from ..infrastructure.base_model import AuditoriaMixin


def get_audit_fields() -> List[str]:
    """Obtiene los nombres de los campos de auditoría del mixin."""
    audit_fields = []

    # Campos definidos directamente en AuditoriaMixin
    for attr_name in dir(AuditoriaMixin):
        if not attr_name.startswith('_'):
            attr = getattr(AuditoriaMixin, attr_name, None)
            # Es un campo mapeado (Mapped) o un declared_attr
            if hasattr(attr, 'property') or hasattr(attr, '__func__'):
                audit_fields.append(attr_name)

    # Lista explícita para asegurar que están todos
    return [
        "fecha_creacion",
        "fecha_modificacion",
        "fecha_eliminacion",
        "eliminado",
        "creado_por_id",
        "modificado_por_id",
    ]


def get_relationship_names(model_class: Type) -> List[str]:
    """Obtiene los nombres de todas las relaciones de un modelo SQLAlchemy."""
    try:
        mapper = inspect(model_class)
        return [
            rel.key
            for rel in mapper.relationships
        ]
    except Exception:
        return []


def get_exclude_fields(model_class: Type) -> List[str]:
    """
    Genera la lista de campos a excluir para un modelo:
    - Campos de auditoría (del mixin)
    - Todas las relaciones (evita inputs anidados complejos)
    """
    audit_fields = get_audit_fields()
    relationship_names = get_relationship_names(model_class)
    return list(set(audit_fields + relationship_names))


# ============================================================================
# MACRO: Genera Input y Filter para un modelo
# ============================================================================

def create_input_classes(model_class: Type, class_name_prefix: str):
    """
    Crea las clases de input para un modelo.
    Retorna una tupla: (CreateInput, UpdateInput, Filter)
    """
    exclude = get_exclude_fields(model_class)

    # Las clases se crean dinámicamente con los decoradores de strawchemy
    # Pero como strawchemy necesita clases declaradas, usamos este patrón
    # de definición explícita con la función de exclusión automática
    return exclude


# ============================================================================
# CORE - Estados
# ============================================================================

from ..modules.core.models import (
    EstadoCuota,
    EstadoCampania,
    EstadoTarea,
    EstadoParticipante,
    EstadoOrdenCobro,
    EstadoRemesa,
    EstadoDonacion,
    EstadoNotificacion,
)


@strawchemy.input(EstadoCuota, mode="create_input", include="all", exclude=get_exclude_fields(EstadoCuota))
class EstadoCuotaCreateInput:
    pass


@strawchemy.input(EstadoCuota, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(EstadoCuota))
class EstadoCuotaUpdateInput:
    pass


@strawchemy.filter(EstadoCuota, include="all")
class EstadoCuotaFilter:
    pass


@strawchemy.input(EstadoCampania, mode="create_input", include="all", exclude=get_exclude_fields(EstadoCampania))
class EstadoCampaniaCreateInput:
    pass


@strawchemy.input(EstadoCampania, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(EstadoCampania))
class EstadoCampaniaUpdateInput:
    pass


@strawchemy.filter(EstadoCampania, include="all")
class EstadoCampaniaFilter:
    pass


@strawchemy.input(EstadoTarea, mode="create_input", include="all", exclude=get_exclude_fields(EstadoTarea))
class EstadoTareaCreateInput:
    pass


@strawchemy.input(EstadoTarea, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(EstadoTarea))
class EstadoTareaUpdateInput:
    pass


@strawchemy.filter(EstadoTarea)
class EstadoTareaFilter:
    pass


@strawchemy.input(EstadoParticipante, mode="create_input", include="all", exclude=get_exclude_fields(EstadoParticipante))
class EstadoParticipanteCreateInput:
    pass


@strawchemy.input(EstadoParticipante, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(EstadoParticipante))
class EstadoParticipanteUpdateInput:
    pass


@strawchemy.filter(EstadoParticipante)
class EstadoParticipanteFilter:
    pass


@strawchemy.input(EstadoOrdenCobro, mode="create_input", include="all", exclude=get_exclude_fields(EstadoOrdenCobro))
class EstadoOrdenCobroCreateInput:
    pass


@strawchemy.input(EstadoOrdenCobro, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(EstadoOrdenCobro))
class EstadoOrdenCobroUpdateInput:
    pass


@strawchemy.filter(EstadoOrdenCobro)
class EstadoOrdenCobroFilter:
    pass


@strawchemy.input(EstadoRemesa, mode="create_input", include="all", exclude=get_exclude_fields(EstadoRemesa))
class EstadoRemesaCreateInput:
    pass


@strawchemy.input(EstadoRemesa, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(EstadoRemesa))
class EstadoRemesaUpdateInput:
    pass


@strawchemy.filter(EstadoRemesa)
class EstadoRemesaFilter:
    pass


@strawchemy.input(EstadoDonacion, mode="create_input", include="all", exclude=get_exclude_fields(EstadoDonacion))
class EstadoDonacionCreateInput:
    pass


@strawchemy.input(EstadoDonacion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(EstadoDonacion))
class EstadoDonacionUpdateInput:
    pass


@strawchemy.filter(EstadoDonacion)
class EstadoDonacionFilter:
    pass


@strawchemy.input(EstadoNotificacion, mode="create_input", include="all", exclude=get_exclude_fields(EstadoNotificacion))
class EstadoNotificacionCreateInput:
    pass


@strawchemy.input(EstadoNotificacion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(EstadoNotificacion))
class EstadoNotificacionUpdateInput:
    pass


@strawchemy.filter(EstadoNotificacion)
class EstadoNotificacionFilter:
    pass


# ============================================================================
# GEOGRÁFICO
# ============================================================================

from ..modules.geografico.models import Pais, Provincia, Municipio, AgrupacionTerritorial


@strawchemy.input(Pais, mode="create_input", include="all", exclude=get_exclude_fields(Pais))
class PaisCreateInput:
    pass


@strawchemy.input(Pais, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Pais))
class PaisUpdateInput:
    pass


@strawchemy.filter(Pais)
class PaisFilter:
    pass


@strawchemy.input(Provincia, mode="create_input", include="all", exclude=get_exclude_fields(Provincia))
class ProvinciaCreateInput:
    pass


@strawchemy.input(Provincia, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Provincia))
class ProvinciaUpdateInput:
    pass


@strawchemy.filter(Provincia)
class ProvinciaFilter:
    pass


@strawchemy.input(Municipio, mode="create_input", include="all", exclude=get_exclude_fields(Municipio))
class MunicipioCreateInput:
    pass


@strawchemy.input(Municipio, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Municipio))
class MunicipioUpdateInput:
    pass


@strawchemy.filter(Municipio)
class MunicipioFilter:
    pass


@strawchemy.input(AgrupacionTerritorial, mode="create_input", include="all", exclude=get_exclude_fields(AgrupacionTerritorial))
class AgrupacionTerritorialCreateInput:
    pass


@strawchemy.input(AgrupacionTerritorial, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(AgrupacionTerritorial))
class AgrupacionTerritorialUpdateInput:
    pass


@strawchemy.filter(AgrupacionTerritorial)
class AgrupacionTerritorialFilter:
    pass


# ============================================================================
# MIEMBROS
# ============================================================================

from ..modules.miembros.models import (
    TipoMiembro, EstadoMiembro, MotivoBaja, Miembro,
    Skill, MiembroSkill, FranjaDisponibilidad, HistorialAgrupacion, SolicitudTraslado,
)


@strawchemy.input(TipoMiembro, mode="create_input", include="all", exclude=get_exclude_fields(TipoMiembro))
class TipoMiembroCreateInput:
    pass


@strawchemy.input(TipoMiembro, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TipoMiembro))
class TipoMiembroUpdateInput:
    pass


@strawchemy.filter(TipoMiembro, include="all")
class TipoMiembroFilter:
    pass


@strawchemy.input(EstadoMiembro, mode="create_input", include="all", exclude=get_exclude_fields(EstadoMiembro))
class EstadoMiembroCreateInput:
    pass


@strawchemy.input(EstadoMiembro, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(EstadoMiembro))
class EstadoMiembroUpdateInput:
    pass


@strawchemy.filter(EstadoMiembro, include="all")
class EstadoMiembroFilter:
    pass


@strawchemy.input(MotivoBaja, mode="create_input", include="all", exclude=get_exclude_fields(MotivoBaja))
class MotivoBajaCreateInput:
    pass


@strawchemy.input(MotivoBaja, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(MotivoBaja))
class MotivoBajaUpdateInput:
    pass


@strawchemy.filter(MotivoBaja, include="all")
class MotivoBajaFilter:
    pass


@strawchemy.input(Miembro, mode="create_input", include="all", exclude=get_exclude_fields(Miembro))
class MiembroCreateInput:
    pass


@strawchemy.input(Miembro, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Miembro))
class MiembroUpdateInput:
    pass


@strawchemy.filter(Miembro, include="all")
class MiembroFilter:
    pass


# ============================================================================
# MILITANCIA — Skills, Disponibilidad, Historial, Traslados
# ============================================================================

@strawchemy.input(Skill, mode="create_input", include="all", exclude=get_exclude_fields(Skill))
class SkillCreateInput:
    pass


@strawchemy.input(Skill, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Skill))
class SkillUpdateInput:
    pass


@strawchemy.filter(Skill, include="all")
class SkillFilter:
    pass


@strawchemy.input(MiembroSkill, mode="create_input", include="all", exclude=get_exclude_fields(MiembroSkill))
class MiembroSkillCreateInput:
    pass


@strawchemy.input(MiembroSkill, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(MiembroSkill))
class MiembroSkillUpdateInput:
    pass


@strawchemy.filter(MiembroSkill, include="all")
class MiembroSkillFilter:
    pass


@strawchemy.input(FranjaDisponibilidad, mode="create_input", include="all", exclude=get_exclude_fields(FranjaDisponibilidad))
class FranjaDisponibilidadCreateInput:
    pass


@strawchemy.input(FranjaDisponibilidad, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(FranjaDisponibilidad))
class FranjaDisponibilidadUpdateInput:
    pass


@strawchemy.filter(FranjaDisponibilidad, include="all")
class FranjaDisponibilidadFilter:
    pass


@strawchemy.input(HistorialAgrupacion, mode="create_input", include="all", exclude=get_exclude_fields(HistorialAgrupacion))
class HistorialAgrupacionCreateInput:
    pass


@strawchemy.input(HistorialAgrupacion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(HistorialAgrupacion))
class HistorialAgrupacionUpdateInput:
    pass


@strawchemy.filter(HistorialAgrupacion, include="all")
class HistorialAgrupacionFilter:
    pass


@strawchemy.input(SolicitudTraslado, mode="create_input", include="all", exclude=get_exclude_fields(SolicitudTraslado))
class SolicitudTrasladoCreateInput:
    pass


@strawchemy.input(SolicitudTraslado, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(SolicitudTraslado))
class SolicitudTrasladoUpdateInput:
    pass


@strawchemy.filter(SolicitudTraslado, include="all")
class SolicitudTrasladoFilter:
    pass


# ============================================================================
# CAMPAÑAS
# ============================================================================

from ..modules.campanas.models import TipoCampania, Campania, RolParticipante, ParticipanteCampania


@strawchemy.input(TipoCampania, mode="create_input", include="all", exclude=get_exclude_fields(TipoCampania))
class TipoCampaniaCreateInput:
    pass


@strawchemy.input(TipoCampania, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TipoCampania))
class TipoCampaniaUpdateInput:
    pass


@strawchemy.filter(TipoCampania, include="all")
class TipoCampaniaFilter:
    pass


@strawchemy.input(Campania, mode="create_input", include="all", exclude=get_exclude_fields(Campania))
class CampaniaCreateInput:
    pass


@strawchemy.input(Campania, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Campania))
class CampaniaUpdateInput:
    pass


@strawchemy.filter(Campania, include="all")
class CampaniaFilter:
    pass


@strawchemy.input(RolParticipante, mode="create_input", include="all", exclude=get_exclude_fields(RolParticipante))
class RolParticipanteCreateInput:
    pass


@strawchemy.input(RolParticipante, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(RolParticipante))
class RolParticipanteUpdateInput:
    pass


@strawchemy.filter(RolParticipante)
class RolParticipanteFilter:
    pass


@strawchemy.input(ParticipanteCampania, mode="create_input", include="all", exclude=get_exclude_fields(ParticipanteCampania))
class ParticipanteCampaniaCreateInput:
    pass


@strawchemy.input(ParticipanteCampania, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(ParticipanteCampania))
class ParticipanteCampaniaUpdateInput:
    pass


@strawchemy.filter(ParticipanteCampania)
class ParticipanteCampaniaFilter:
    pass


# ============================================================================
# ACTIVIDADES
# ============================================================================

from ..modules.actividades.models import (
    TipoActividad, EstadoActividad, EstadoPropuesta, TipoRecurso, TipoKPI,
    PropuestaActividad, Actividad, TareaActividad
)


@strawchemy.input(TipoActividad, mode="create_input", include="all", exclude=get_exclude_fields(TipoActividad))
class TipoActividadCreateInput:
    pass


@strawchemy.input(TipoActividad, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TipoActividad))
class TipoActividadUpdateInput:
    pass


@strawchemy.filter(TipoActividad, include="all")
class TipoActividadFilter:
    pass


@strawchemy.input(EstadoActividad, mode="create_input", include="all", exclude=get_exclude_fields(EstadoActividad))
class EstadoActividadCreateInput:
    pass


@strawchemy.input(EstadoActividad, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(EstadoActividad))
class EstadoActividadUpdateInput:
    pass


@strawchemy.filter(EstadoActividad, include="all")
class EstadoActividadFilter:
    pass


@strawchemy.input(EstadoPropuesta, mode="create_input", include="all", exclude=get_exclude_fields(EstadoPropuesta))
class EstadoPropuestaCreateInput:
    pass


@strawchemy.input(EstadoPropuesta, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(EstadoPropuesta))
class EstadoPropuestaUpdateInput:
    pass


@strawchemy.filter(EstadoPropuesta)
class EstadoPropuestaFilter:
    pass


@strawchemy.input(TipoRecurso, mode="create_input", include="all", exclude=get_exclude_fields(TipoRecurso))
class TipoRecursoCreateInput:
    pass


@strawchemy.input(TipoRecurso, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TipoRecurso))
class TipoRecursoUpdateInput:
    pass


@strawchemy.filter(TipoRecurso)
class TipoRecursoFilter:
    pass


@strawchemy.input(TipoKPI, mode="create_input", include="all", exclude=get_exclude_fields(TipoKPI))
class TipoKPICreateInput:
    pass


@strawchemy.input(TipoKPI, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TipoKPI))
class TipoKPIUpdateInput:
    pass


@strawchemy.filter(TipoKPI)
class TipoKPIFilter:
    pass


@strawchemy.input(PropuestaActividad, mode="create_input", include="all", exclude=get_exclude_fields(PropuestaActividad))
class PropuestaActividadCreateInput:
    pass


@strawchemy.input(PropuestaActividad, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(PropuestaActividad))
class PropuestaActividadUpdateInput:
    pass


@strawchemy.filter(PropuestaActividad)
class PropuestaActividadFilter:
    pass


@strawchemy.input(Actividad, mode="create_input", include="all", exclude=get_exclude_fields(Actividad))
class ActividadCreateInput:
    pass


@strawchemy.input(Actividad, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Actividad))
class ActividadUpdateInput:
    pass


@strawchemy.filter(Actividad)
class ActividadFilter:
    pass


@strawchemy.input(TareaActividad, mode="create_input", include="all", exclude=get_exclude_fields(TareaActividad))
class TareaActividadCreateInput:
    pass


@strawchemy.input(TareaActividad, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TareaActividad))
class TareaActividadUpdateInput:
    pass


@strawchemy.filter(TareaActividad)
class TareaActividadFilter:
    pass


# ============================================================================
# GRUPOS
# ============================================================================

from ..modules.grupos.models import TipoGrupo, RolGrupo, GrupoTrabajo, MiembroGrupo, TareaGrupo


@strawchemy.input(TipoGrupo, mode="create_input", include="all", exclude=get_exclude_fields(TipoGrupo))
class TipoGrupoCreateInput:
    pass


@strawchemy.input(TipoGrupo, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TipoGrupo))
class TipoGrupoUpdateInput:
    pass


@strawchemy.filter(TipoGrupo)
class TipoGrupoFilter:
    pass


@strawchemy.input(RolGrupo, mode="create_input", include="all", exclude=get_exclude_fields(RolGrupo))
class RolGrupoCreateInput:
    pass


@strawchemy.input(RolGrupo, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(RolGrupo))
class RolGrupoUpdateInput:
    pass


@strawchemy.filter(RolGrupo)
class RolGrupoFilter:
    pass


@strawchemy.input(GrupoTrabajo, mode="create_input", include="all", exclude=get_exclude_fields(GrupoTrabajo))
class GrupoTrabajoCreateInput:
    pass


@strawchemy.input(GrupoTrabajo, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(GrupoTrabajo))
class GrupoTrabajoUpdateInput:
    pass


@strawchemy.filter(GrupoTrabajo)
class GrupoTrabajoFilter:
    pass


@strawchemy.input(MiembroGrupo, mode="create_input", include="all", exclude=get_exclude_fields(MiembroGrupo))
class MiembroGrupoCreateInput:
    pass


@strawchemy.input(MiembroGrupo, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(MiembroGrupo))
class MiembroGrupoUpdateInput:
    pass


@strawchemy.filter(MiembroGrupo)
class MiembroGrupoFilter:
    pass


@strawchemy.input(TareaGrupo, mode="create_input", include="all", exclude=get_exclude_fields(TareaGrupo))
class TareaGrupoCreateInput:
    pass


@strawchemy.input(TareaGrupo, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TareaGrupo))
class TareaGrupoUpdateInput:
    pass


@strawchemy.filter(TareaGrupo)
class TareaGrupoFilter:
    pass


# ============================================================================
# FINANCIERO
# ============================================================================

from ..modules.economico.models import (
    ImporteCuotaAnio, CuotaAnual, DonacionConcepto, Donacion, Remesa, OrdenCobro
)


@strawchemy.input(ImporteCuotaAnio, mode="create_input", include="all", exclude=get_exclude_fields(ImporteCuotaAnio))
class ImporteCuotaAnioCreateInput:
    pass


@strawchemy.input(ImporteCuotaAnio, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(ImporteCuotaAnio))
class ImporteCuotaAnioUpdateInput:
    pass


@strawchemy.filter(ImporteCuotaAnio)
class ImporteCuotaAnioFilter:
    pass


@strawchemy.input(CuotaAnual, mode="create_input", include="all", exclude=get_exclude_fields(CuotaAnual))
class CuotaAnualCreateInput:
    pass


@strawchemy.input(CuotaAnual, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(CuotaAnual))
class CuotaAnualUpdateInput:
    pass


@strawchemy.filter(CuotaAnual)
class CuotaAnualFilter:
    pass


@strawchemy.input(DonacionConcepto, mode="create_input", include="all", exclude=get_exclude_fields(DonacionConcepto))
class DonacionConceptoCreateInput:
    pass


@strawchemy.input(DonacionConcepto, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(DonacionConcepto))
class DonacionConceptoUpdateInput:
    pass


@strawchemy.filter(DonacionConcepto)
class DonacionConceptoFilter:
    pass


@strawchemy.input(Donacion, mode="create_input", include="all", exclude=get_exclude_fields(Donacion))
class DonacionCreateInput:
    pass


@strawchemy.input(Donacion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Donacion))
class DonacionUpdateInput:
    pass


@strawchemy.filter(Donacion)
class DonacionFilter:
    pass


@strawchemy.input(Remesa, mode="create_input", include="all", exclude=get_exclude_fields(Remesa))
class RemesaCreateInput:
    pass


@strawchemy.input(Remesa, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Remesa))
class RemesaUpdateInput:
    pass


@strawchemy.filter(Remesa)
class RemesaFilter:
    pass


@strawchemy.input(OrdenCobro, mode="create_input", include="all", exclude=get_exclude_fields(OrdenCobro))
class OrdenCobroCreateInput:
    pass


@strawchemy.input(OrdenCobro, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(OrdenCobro))
class OrdenCobroUpdateInput:
    pass


@strawchemy.filter(OrdenCobro)
class OrdenCobroFilter:
    pass


# ============================================================================
# VOLUNTARIADO
# ============================================================================

from ..modules.voluntariado.models import (
    CategoriaCompetencia, Competencia, NivelCompetencia, MiembroCompetencia,
    TipoDocumentoVoluntario, DocumentoMiembro, TipoFormacion, FormacionMiembro
)


@strawchemy.input(CategoriaCompetencia, mode="create_input", include="all", exclude=get_exclude_fields(CategoriaCompetencia))
class CategoriaCompetenciaCreateInput:
    pass


@strawchemy.input(CategoriaCompetencia, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(CategoriaCompetencia))
class CategoriaCompetenciaUpdateInput:
    pass


@strawchemy.filter(CategoriaCompetencia)
class CategoriaCompetenciaFilter:
    pass


@strawchemy.input(Competencia, mode="create_input", include="all", exclude=get_exclude_fields(Competencia))
class CompetenciaCreateInput:
    pass


@strawchemy.input(Competencia, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Competencia))
class CompetenciaUpdateInput:
    pass


@strawchemy.filter(Competencia)
class CompetenciaFilter:
    pass


@strawchemy.input(NivelCompetencia, mode="create_input", include="all", exclude=get_exclude_fields(NivelCompetencia))
class NivelCompetenciaCreateInput:
    pass


@strawchemy.input(NivelCompetencia, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(NivelCompetencia))
class NivelCompetenciaUpdateInput:
    pass


@strawchemy.filter(NivelCompetencia)
class NivelCompetenciaFilter:
    pass


@strawchemy.input(MiembroCompetencia, mode="create_input", include="all", exclude=get_exclude_fields(MiembroCompetencia))
class MiembroCompetenciaCreateInput:
    pass


@strawchemy.input(MiembroCompetencia, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(MiembroCompetencia))
class MiembroCompetenciaUpdateInput:
    pass


@strawchemy.filter(MiembroCompetencia)
class MiembroCompetenciaFilter:
    pass


@strawchemy.input(TipoDocumentoVoluntario, mode="create_input", include="all", exclude=get_exclude_fields(TipoDocumentoVoluntario))
class TipoDocumentoVoluntarioCreateInput:
    pass


@strawchemy.input(TipoDocumentoVoluntario, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TipoDocumentoVoluntario))
class TipoDocumentoVoluntarioUpdateInput:
    pass


@strawchemy.filter(TipoDocumentoVoluntario)
class TipoDocumentoVoluntarioFilter:
    pass


@strawchemy.input(DocumentoMiembro, mode="create_input", include="all", exclude=get_exclude_fields(DocumentoMiembro))
class DocumentoMiembroCreateInput:
    pass


@strawchemy.input(DocumentoMiembro, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(DocumentoMiembro))
class DocumentoMiembroUpdateInput:
    pass


@strawchemy.filter(DocumentoMiembro)
class DocumentoMiembroFilter:
    pass


@strawchemy.input(TipoFormacion, mode="create_input", include="all", exclude=get_exclude_fields(TipoFormacion))
class TipoFormacionCreateInput:
    pass


@strawchemy.input(TipoFormacion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TipoFormacion))
class TipoFormacionUpdateInput:
    pass


@strawchemy.filter(TipoFormacion)
class TipoFormacionFilter:
    pass


@strawchemy.input(FormacionMiembro, mode="create_input", include="all", exclude=get_exclude_fields(FormacionMiembro))
class FormacionMiembroCreateInput:
    pass


@strawchemy.input(FormacionMiembro, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(FormacionMiembro))
class FormacionMiembroUpdateInput:
    pass


@strawchemy.filter(FormacionMiembro)
class FormacionMiembroFilter:
    pass


# ============================================================================
# NOTIFICACIONES
# ============================================================================

from ..modules.notificaciones.models import TipoNotificacion, Notificacion, PreferenciaNotificacion


@strawchemy.input(TipoNotificacion, mode="create_input", include="all", exclude=get_exclude_fields(TipoNotificacion))
class TipoNotificacionCreateInput:
    pass


@strawchemy.input(TipoNotificacion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TipoNotificacion))
class TipoNotificacionUpdateInput:
    pass


@strawchemy.filter(TipoNotificacion)
class TipoNotificacionFilter:
    pass


# Excluir datos_adicionales (campo JSON/dict no soportado por Strawberry)
_notificacion_exclude = get_exclude_fields(Notificacion) + ["datos_adicionales"]


@strawchemy.input(Notificacion, mode="create_input", include="all", exclude=_notificacion_exclude)
class NotificacionCreateInput:
    pass


@strawchemy.input(Notificacion, mode="update_by_pk_input", include="all", exclude=_notificacion_exclude)
class NotificacionUpdateInput:
    pass


@strawchemy.filter(Notificacion)
class NotificacionFilter:
    pass


@strawchemy.input(PreferenciaNotificacion, mode="create_input", include="all", exclude=get_exclude_fields(PreferenciaNotificacion))
class PreferenciaNotificacionCreateInput:
    pass


@strawchemy.input(PreferenciaNotificacion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(PreferenciaNotificacion))
class PreferenciaNotificacionUpdateInput:
    pass


@strawchemy.filter(PreferenciaNotificacion)
class PreferenciaNotificacionFilter:
    pass


# ============================================================================
# COLABORACIONES
# ============================================================================

from ..modules.colaboraciones.models import TipoAsociacion, Asociacion, EstadoConvenio, Convenio


@strawchemy.input(TipoAsociacion, mode="create_input", include="all", exclude=get_exclude_fields(TipoAsociacion))
class TipoAsociacionCreateInput:
    pass


@strawchemy.input(TipoAsociacion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TipoAsociacion))
class TipoAsociacionUpdateInput:
    pass


@strawchemy.filter(TipoAsociacion)
class TipoAsociacionFilter:
    pass


@strawchemy.input(Asociacion, mode="create_input", include="all", exclude=get_exclude_fields(Asociacion))
class AsociacionCreateInput:
    pass


@strawchemy.input(Asociacion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Asociacion))
class AsociacionUpdateInput:
    pass


@strawchemy.filter(Asociacion)
class AsociacionFilter:
    pass


@strawchemy.input(EstadoConvenio, mode="create_input", include="all", exclude=get_exclude_fields(EstadoConvenio))
class EstadoConvenioCreateInput:
    pass


@strawchemy.input(EstadoConvenio, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(EstadoConvenio))
class EstadoConvenioUpdateInput:
    pass


@strawchemy.filter(EstadoConvenio)
class EstadoConvenioFilter:
    pass


@strawchemy.input(Convenio, mode="create_input", include="all", exclude=get_exclude_fields(Convenio))
class ConvenioCreateInput:
    pass


@strawchemy.input(Convenio, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Convenio))
class ConvenioUpdateInput:
    pass


@strawchemy.filter(Convenio)
class ConvenioFilter:
    pass
