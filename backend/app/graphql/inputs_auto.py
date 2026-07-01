"""Tipos de Input y Filter GraphQL generados con strawchemy para cada modelo."""

import uuid
from typing import Type, List, Optional
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy import inspect

import strawberry
from . import strawchemy


def get_audit_fields() -> List[str]:
    """Devuelve los campos de auditoría que deben excluirse de los inputs."""
    return [
        "fecha_creacion",
        "fecha_modificacion",
        "fecha_eliminacion",
        "eliminado",
        "creado_por_id",
        "modificado_por_id",
        "es_inmutable",
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
# ACCESO - Roles, transacciones, funcionalidades
# ============================================================================

from ..modules.acceso.models import (
    Rol,
    Transaccion,
    RolTransaccion,
    Funcionalidad,
    RolFuncionalidad,
    FuncionalidadTransaccion,
    UsuarioRol,
)
# TipoVinculacion es ahora el catálogo CRM canónico (módulo membresía).
from ..modules.membresia.models import TipoVinculacion
from ..modules.acceso.models.cargo import Cargo, CargoRol


@strawchemy.input(Cargo, mode="create_input", include="all", exclude=get_exclude_fields(Cargo))
class CargoCreateInput:
    pass


@strawchemy.input(Cargo, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Cargo))
class CargoUpdateInput:
    pass


@strawchemy.filter(Cargo, include="all")
class CargoFilter:
    pass


@strawchemy.input(CargoRol, mode="create_input", include="all", exclude=get_exclude_fields(CargoRol))
class CargoRolCreateInput:
    pass


@strawchemy.filter(CargoRol, include="all")
class CargoRolFilter:
    pass


@strawchemy.input(Rol, mode="create_input", include="all", exclude=get_exclude_fields(Rol))
class RolCreateInput:
    pass


@strawchemy.input(Rol, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Rol))
class RolUpdateInput:
    pass


@strawchemy.filter(Rol, include="all")
class RolFilter:
    pass


@strawchemy.input(Transaccion, mode="create_input", include="all", exclude=get_exclude_fields(Transaccion))
class TransaccionCreateInput:
    pass


@strawchemy.input(Transaccion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Transaccion))
class TransaccionUpdateInput:
    pass


@strawchemy.filter(Transaccion, include="all")
class TransaccionFilter:
    pass


@strawchemy.input(RolTransaccion, mode="create_input", include="all", exclude=get_exclude_fields(RolTransaccion))
class RolTransaccionCreateInput:
    rol_id: uuid.UUID
    transaccion_id: uuid.UUID


@strawchemy.filter(RolTransaccion, include="all")
class RolTransaccionFilter:
    pass


@strawchemy.input(Funcionalidad, mode="create_input", include="all", exclude=get_exclude_fields(Funcionalidad))
class FuncionalidadCreateInput:
    pass


@strawchemy.input(Funcionalidad, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Funcionalidad))
class FuncionalidadUpdateInput:
    pass


@strawchemy.filter(Funcionalidad, include="all")
class FuncionalidadFilter:
    pass


@strawchemy.input(RolFuncionalidad, mode="create_input", include="all", exclude=get_exclude_fields(RolFuncionalidad))
class RolFuncionalidadCreateInput:
    rol_id: uuid.UUID
    funcionalidad_id: uuid.UUID


@strawchemy.filter(RolFuncionalidad, include="all")
class RolFuncionalidadFilter:
    pass


@strawchemy.input(FuncionalidadTransaccion, mode="create_input", include="all", exclude=get_exclude_fields(FuncionalidadTransaccion))
class FuncionalidadTransaccionCreateInput:
    pass


@strawchemy.filter(FuncionalidadTransaccion, include="all")
class FuncionalidadTransaccionFilter:
    pass


@strawchemy.input(UsuarioRol, mode="create_input", include="all", exclude=get_exclude_fields(UsuarioRol))
class UsuarioRolCreateInput:
    pass


@strawchemy.filter(UsuarioRol, include="all")
class UsuarioRolFilter:
    pass


@strawchemy.input(TipoVinculacion, mode="create_input", include="all", exclude=get_exclude_fields(TipoVinculacion))
class TipoVinculacionCreateInput:
    pass


@strawchemy.input(TipoVinculacion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TipoVinculacion))
class TipoVinculacionUpdateInput:
    pass


@strawchemy.filter(TipoVinculacion, include="all")
class TipoVinculacionFilter:
    pass


# ============================================================================
# MEMBRESIA - Junta directiva y nombramientos
# ============================================================================

from ..modules.membresia.models import JuntaDirectiva, HistorialNombramiento, CoordinacionTerritorial


@strawchemy.input(JuntaDirectiva, mode="create_input", include="all", exclude=get_exclude_fields(JuntaDirectiva))
class JuntaDirectivaCreateInput:
    pass


@strawchemy.input(JuntaDirectiva, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(JuntaDirectiva))
class JuntaDirectivaUpdateInput:
    pass


@strawchemy.filter(JuntaDirectiva, include="all")
class JuntaDirectivaFilter:
    pass


@strawchemy.input(HistorialNombramiento, mode="create_input", include="all", exclude=get_exclude_fields(HistorialNombramiento))
class HistorialNombramientoCreateInput:
    pass


@strawchemy.input(HistorialNombramiento, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(HistorialNombramiento))
class HistorialNombramientoUpdateInput:
    pass


@strawchemy.filter(HistorialNombramiento, include="all")
class HistorialNombramientoFilter:
    pass


@strawchemy.input(CoordinacionTerritorial, mode="create_input", include="all", exclude=get_exclude_fields(CoordinacionTerritorial))
class CoordinacionTerritorialCreateInput:
    pass


@strawchemy.input(CoordinacionTerritorial, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(CoordinacionTerritorial))
class CoordinacionTerritorialUpdateInput:
    pass


@strawchemy.filter(CoordinacionTerritorial, include="all")
class CoordinacionTerritorialFilter:
    pass


# ============================================================================
# CORE - Estados
# ============================================================================

from ..modules.core.models import (
    EstadoCuota,
    EstadoCampania,
    EstadoAccion,
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


@strawchemy.input(EstadoAccion, mode="create_input", include="all", exclude=get_exclude_fields(EstadoAccion))
class EstadoAccionCreateInput:
    pass


@strawchemy.input(EstadoAccion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(EstadoAccion))
class EstadoAccionUpdateInput:
    pass


@strawchemy.filter(EstadoAccion, include="all")
class EstadoAccionFilter:
    pass

# Estados de actividad reutilizan el catálogo de estados de acción
# (Actividad.estado_id → estados_accion). No se exponen tipos GraphQL
# separados: el frontend usa los nombres EstadoAccion* en las mutaciones
# crear/actualizar/eliminar estado_actividad. Aliasar en Python no registra
# un tipo GraphQL nuevo, así que aquí no hay nada que aliasar.


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

from ..modules.core.geografico import AmbitoGeografico, Pais, Provincia, Municipio, UnidadOrganizativa, NivelOrganizativo, EntidadGeografica


@strawchemy.input(AmbitoGeografico, mode="create_input", include="all",
                  exclude=get_exclude_fields(AmbitoGeografico))
class AmbitoGeograficoCreateInput:
    pass


@strawchemy.input(AmbitoGeografico, mode="update_by_pk_input", include="all",
                  exclude=get_exclude_fields(AmbitoGeografico))
class AmbitoGeograficoUpdateInput:
    pass


@strawchemy.filter(AmbitoGeografico)
class AmbitoGeograficoFilter:
    pass


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


@strawchemy.filter(UnidadOrganizativa)
class UnidadOrganizativaFilter:
    pass


@strawchemy.filter(EntidadGeografica, exclude=["padre", "hijos"])
class EntidadGeograficaFilter:
    pass


@strawchemy.filter(NivelOrganizativo)
class NivelOrganizativoFilter:
    pass


# ============================================================================
# TEMAS UI
# ============================================================================

from ..modules.configuracion.models.tema_ui import TemaUI

@strawchemy.input(TemaUI, mode="create_input", include="all", exclude=get_exclude_fields(TemaUI))
class TemaUICreateInput:
    pass

@strawchemy.input(TemaUI, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TemaUI))
class TemaUIUpdateInput:
    pass

@strawchemy.filter(TemaUI, include="all")
class TemaUIFilter:
    pass


# ============================================================================
# MIEMBROS
# ============================================================================

from ..modules.membresia.models import (
    TipoMiembro, EstadoMiembro, MotivoBaja, Contacto,
    NivelEstudios, NivelHabilidad,
    CategoriaHabilidad, Habilidad, MiembroHabilidad, FranjaDisponibilidad,
    HistorialAgrupacion, SolicitudTraslado,
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


@strawchemy.filter(Contacto, include="all")
class ContactoFilter:
    pass


# ============================================================================
# MILITANCIA — Habilidades, Disponibilidad, Historial, Traslados
# ============================================================================

@strawchemy.input(NivelEstudios, mode="create_input", include="all", exclude=get_exclude_fields(NivelEstudios))
class NivelEstudiosCreateInput:
    pass

@strawchemy.input(NivelEstudios, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(NivelEstudios))
class NivelEstudiosUpdateInput:
    pass

@strawchemy.filter(NivelEstudios, include="all")
class NivelEstudiosFilter:
    pass

@strawchemy.input(NivelHabilidad, mode="create_input", include="all", exclude=get_exclude_fields(NivelHabilidad))
class NivelHabilidadCreateInput:
    pass

@strawchemy.input(NivelHabilidad, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(NivelHabilidad))
class NivelHabilidadUpdateInput:
    pass

@strawchemy.filter(NivelHabilidad, include="all")
class NivelHabilidadFilter:
    pass

@strawchemy.input(CategoriaHabilidad, mode="create_input", include="all", exclude=get_exclude_fields(CategoriaHabilidad))
class CategoriaHabilidadCreateInput:
    pass


@strawchemy.input(CategoriaHabilidad, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(CategoriaHabilidad))
class CategoriaHabilidadUpdateInput:
    pass


@strawchemy.filter(CategoriaHabilidad, include="all")
class CategoriaHabilidadFilter:
    pass


@strawchemy.input(Habilidad, mode="create_input", include="all", exclude=get_exclude_fields(Habilidad))
class HabilidadCreateInput:
    categoria_id: Optional[uuid.UUID] = strawberry.UNSET


@strawchemy.input(Habilidad, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Habilidad))
class HabilidadUpdateInput:
    categoria_id: Optional[uuid.UUID] = strawberry.UNSET


@strawchemy.filter(Habilidad, include="all")
class HabilidadFilter:
    pass


@strawchemy.input(MiembroHabilidad, mode="create_input", include="all", exclude=get_exclude_fields(MiembroHabilidad))
class MiembroHabilidadCreateInput:
    pass


@strawchemy.input(MiembroHabilidad, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(MiembroHabilidad))
class MiembroHabilidadUpdateInput:
    pass


@strawchemy.filter(MiembroHabilidad, include="all")
class MiembroHabilidadFilter:
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

from ..modules.actividades.models import (
    TipoCampania, TipoMeta, TipoCanalDifusion,
    Campania, MetaCampania, CanalDifusionCampania, PartidaPresupuestoCampania,
    PlantillaCampania, PlantillaMeta, PlantillaPartida, PlantillaActividad, PlantillaTarea,
)


@strawchemy.input(TipoMeta, mode="create_input", include="all", exclude=get_exclude_fields(TipoMeta))
class TipoMetaCreateInput:
    pass


@strawchemy.input(TipoMeta, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TipoMeta))
class TipoMetaUpdateInput:
    pass


@strawchemy.filter(TipoMeta, include="all")
class TipoMetaFilter:
    pass


@strawchemy.input(TipoCanalDifusion, mode="create_input", include="all", exclude=get_exclude_fields(TipoCanalDifusion))
class TipoCanalDifusionCreateInput:
    pass


@strawchemy.input(TipoCanalDifusion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TipoCanalDifusion))
class TipoCanalDifusionUpdateInput:
    pass


@strawchemy.filter(TipoCanalDifusion, include="all")
class TipoCanalDifusionFilter:
    pass


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


@strawchemy.input(MetaCampania, mode="create_input", include="all", exclude=get_exclude_fields(MetaCampania))
class MetaCampaniaCreateInput:
    pass


@strawchemy.input(MetaCampania, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(MetaCampania))
class MetaCampaniaUpdateInput:
    pass


@strawchemy.input(CanalDifusionCampania, mode="create_input", include="all", exclude=get_exclude_fields(CanalDifusionCampania))
class CanalDifusionCampaniaCreateInput:
    pass


@strawchemy.input(PartidaPresupuestoCampania, mode="create_input", include="all", exclude=get_exclude_fields(PartidaPresupuestoCampania))
class PartidaPresupuestoCampaniaCreateInput:
    pass


@strawchemy.input(PartidaPresupuestoCampania, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(PartidaPresupuestoCampania))
class PartidaPresupuestoCampaniaUpdateInput:
    pass


@strawchemy.input(PlantillaCampania, mode="create_input", include="all", exclude=get_exclude_fields(PlantillaCampania))
class PlantillaCampaniaCreateInput:
    pass


@strawchemy.input(PlantillaCampania, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(PlantillaCampania))
class PlantillaCampaniaUpdateInput:
    pass


@strawchemy.filter(PlantillaCampania, include="all")
class PlantillaCampaniaFilter:
    pass


@strawchemy.filter(PlantillaMeta, include="all")
class PlantillaMetaFilter:
    pass


@strawchemy.input(PlantillaMeta, mode="create_input", include="all", exclude=get_exclude_fields(PlantillaMeta))
class PlantillaMetaCreateInput:
    pass


@strawchemy.input(PlantillaMeta, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(PlantillaMeta))
class PlantillaMetaUpdateInput:
    pass


@strawchemy.filter(PlantillaPartida, include="all")
class PlantillaPartidaFilter:
    pass


@strawchemy.input(PlantillaPartida, mode="create_input", include="all", exclude=get_exclude_fields(PlantillaPartida))
class PlantillaPartidaCreateInput:
    pass


@strawchemy.input(PlantillaPartida, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(PlantillaPartida))
class PlantillaPartidaUpdateInput:
    pass


@strawchemy.input(PlantillaActividad, mode="create_input", include="all", exclude=get_exclude_fields(PlantillaActividad))
class PlantillaActividadCreateInput:
    pass


@strawchemy.input(PlantillaActividad, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(PlantillaActividad))
class PlantillaActividadUpdateInput:
    pass


@strawchemy.input(PlantillaTarea, mode="create_input", include="all", exclude=get_exclude_fields(PlantillaTarea))
class PlantillaTareaCreateInput:
    pass


@strawchemy.input(PlantillaTarea, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(PlantillaTarea))
class PlantillaTareaUpdateInput:
    pass


# RolParticipante/ParticipanteCampania se disolvieron en Contacto + Participacion
# + Vinculacion; sus inputs/filtros GraphQL quedan retirados.


# ============================================================================
# ACCIONES (unifica Evento + Actividad)
# ============================================================================

from ..modules.actividades.models import (
    TipoActividad, TipoAccion, Actividad, Accion, Tarea, AsistenciaActividad,
    PartidaPresupuestoActividad, RegistroTrabajoActividad, DocumentoActividad, DocumentoPartida,
    PublicacionWeb,
)


@strawchemy.input(PublicacionWeb, mode="create_input", include="all", exclude=get_exclude_fields(PublicacionWeb))
class PublicacionWebCreateInput:
    pass


@strawchemy.input(PublicacionWeb, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(PublicacionWeb))
class PublicacionWebUpdateInput:
    pass


@strawchemy.filter(PublicacionWeb, include="all")
class PublicacionWebFilter:
    pass


@strawchemy.input(TipoActividad, mode="create_input", include="all", exclude=get_exclude_fields(TipoActividad))
class TipoActividadCreateInput:
    pass


@strawchemy.input(TipoActividad, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TipoActividad))
class TipoActividadUpdateInput:
    pass


@strawchemy.filter(TipoActividad, include="all")
class TipoActividadFilter:
    pass

# Alias de compatibilidad
TipoAccionCreateInput = TipoActividadCreateInput
TipoAccionUpdateInput = TipoActividadUpdateInput
TipoAccionFilter = TipoActividadFilter


@strawchemy.input(Actividad, mode="create_input", include="all", exclude=get_exclude_fields(Actividad))
class ActividadCreateInput:
    pass


@strawchemy.input(Actividad, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Actividad))
class ActividadUpdateInput:
    pass


@strawchemy.filter(Actividad, include="all")
class ActividadFilter:
    pass

# Alias de compatibilidad
AccionCreateInput = ActividadCreateInput
AccionUpdateInput = ActividadUpdateInput
AccionFilter = ActividadFilter


@strawchemy.input(Tarea, mode="create_input", include="all", exclude=get_exclude_fields(Tarea))
class TareaCreateInput:
    pass


@strawchemy.input(Tarea, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Tarea))
class TareaUpdateInput:
    pass


@strawchemy.filter(Tarea, include="all")
class TareaFilter:
    pass


# `Participacion` (actividades) -> `AsistenciaActividad`. Se conservan los nombres
# GraphQL `Participacion*Input/Filter` por compatibilidad con el frontend.
@strawchemy.input(AsistenciaActividad, mode="create_input", include="all", exclude=get_exclude_fields(AsistenciaActividad))
class ParticipacionCreateInput:
    pass


@strawchemy.input(AsistenciaActividad, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(AsistenciaActividad))
class ParticipacionUpdateInput:
    pass


@strawchemy.filter(AsistenciaActividad, include="all")
class ParticipacionFilter:
    pass


@strawchemy.input(PartidaPresupuestoActividad, mode="create_input", include="all", exclude=get_exclude_fields(PartidaPresupuestoActividad))
class PartidaPresupuestoActividadCreateInput:
    pass


@strawchemy.input(PartidaPresupuestoActividad, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(PartidaPresupuestoActividad))
class PartidaPresupuestoActividadUpdateInput:
    pass


@strawchemy.filter(PartidaPresupuestoActividad, include="all")
class PartidaPresupuestoActividadFilter:
    pass


@strawchemy.input(RegistroTrabajoActividad, mode="create_input", include="all", exclude=get_exclude_fields(RegistroTrabajoActividad))
class RegistroTrabajoActividadCreateInput:
    pass


@strawchemy.input(RegistroTrabajoActividad, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(RegistroTrabajoActividad))
class RegistroTrabajoActividadUpdateInput:
    pass


@strawchemy.filter(RegistroTrabajoActividad, include="all")
class RegistroTrabajoActividadFilter:
    pass


@strawchemy.filter(DocumentoActividad, include="all")
class DocumentoActividadFilter:
    pass


@strawchemy.filter(DocumentoPartida, include="all")
class DocumentoPartidaFilter:
    pass


# ============================================================================
# GRUPOS
# ============================================================================

from ..modules.actividades.models import TipoGrupo, RolGrupo, GrupoTrabajo, MiembroGrupo, GrupoIniciativa, RequisitoRecurso, AportacionHoras


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
    # FK IDs eliminados por strawchemy al detectar relationships — los reponemos explícitamente
    tipo_grupo_id: uuid.UUID = strawberry.UNSET
    coordinador_id: Optional[uuid.UUID] = strawberry.UNSET
    agrupacion_id: Optional[uuid.UUID] = strawberry.UNSET


@strawchemy.input(GrupoTrabajo, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(GrupoTrabajo))
class GrupoTrabajoUpdateInput:
    tipo_grupo_id: Optional[uuid.UUID] = strawberry.UNSET
    coordinador_id: Optional[uuid.UUID] = strawberry.UNSET
    agrupacion_id: Optional[uuid.UUID] = strawberry.UNSET


@strawchemy.filter(GrupoTrabajo)
class GrupoTrabajoFilter:
    pass


@strawchemy.input(MiembroGrupo, mode="create_input", include="all", exclude=get_exclude_fields(MiembroGrupo))
class MiembroGrupoCreateInput:
    grupo_id: uuid.UUID = strawberry.UNSET
    miembro_id: uuid.UUID = strawberry.UNSET
    rol_grupo_id: uuid.UUID = strawberry.UNSET


@strawchemy.input(MiembroGrupo, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(MiembroGrupo))
class MiembroGrupoUpdateInput:
    grupo_id: Optional[uuid.UUID] = strawberry.UNSET
    miembro_id: Optional[uuid.UUID] = strawberry.UNSET
    rol_grupo_id: Optional[uuid.UUID] = strawberry.UNSET


@strawchemy.filter(MiembroGrupo)
class MiembroGrupoFilter:
    pass


@strawchemy.input(GrupoIniciativa, mode="create_input", include="all", exclude=get_exclude_fields(GrupoIniciativa))
class GrupoIniciativaCreateInput:
    pass


@strawchemy.input(GrupoIniciativa, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(GrupoIniciativa))
class GrupoIniciativaUpdateInput:
    pass


@strawchemy.filter(GrupoIniciativa, include="all")
class GrupoIniciativaFilter:
    pass


@strawchemy.input(RequisitoRecurso, mode="create_input", include="all", exclude=get_exclude_fields(RequisitoRecurso))
class RequisitoRecursoCreateInput:
    pass


@strawchemy.input(RequisitoRecurso, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(RequisitoRecurso))
class RequisitoRecursoUpdateInput:
    pass


@strawchemy.filter(RequisitoRecurso, include="all")
class RequisitoRecursoFilter:
    pass


@strawchemy.input(AportacionHoras, mode="create_input", include="all", exclude=get_exclude_fields(AportacionHoras))
class AportacionHorasCreateInput:
    pass


@strawchemy.input(AportacionHoras, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(AportacionHoras))
class AportacionHorasUpdateInput:
    pass


@strawchemy.filter(AportacionHoras, include="all")
class AportacionHorasFilter:
    pass


# ============================================================================
# FINANCIERO
# ============================================================================

from ..modules.economico.models import (
    ImporteCuotaAnio, CuotaAnual, MotivoReduccionCuota, DonacionConcepto, Donacion, Remesa, OrdenCobro, Recibo,
    JustificanteGasto, SolicitudReduccionCuota, FormaPago,
    CuentaBancaria, MovimientoTesoreria, ConciliacionBancaria,
    CuentaContable, AsientoContable, ApunteContable,
    CompromisoPresupuestario,
)


@strawchemy.input(ImporteCuotaAnio, mode="create_input", include="all", exclude=get_exclude_fields(ImporteCuotaAnio))
class ImporteCuotaAnioCreateInput:
    pass


@strawchemy.input(ImporteCuotaAnio, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(ImporteCuotaAnio))
class ImporteCuotaAnioUpdateInput:
    pass


@strawchemy.input(MotivoReduccionCuota, mode="create_input", include="all", exclude=get_exclude_fields(MotivoReduccionCuota))
class MotivoReduccionCuotaCreateInput:
    pass

@strawchemy.input(MotivoReduccionCuota, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(MotivoReduccionCuota))
class MotivoReduccionCuotaUpdateInput:
    pass

@strawchemy.filter(MotivoReduccionCuota, include="all")
class MotivoReduccionCuotaFilter:
    pass

@strawchemy.filter(ImporteCuotaAnio, include="all")
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


@strawchemy.input(Recibo, mode="create_input", include="all", exclude=get_exclude_fields(Recibo))
class ReciboCreateInput:
    pass


@strawchemy.input(Recibo, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Recibo))
class ReciboUpdateInput:
    pass


@strawchemy.filter(Recibo)
class ReciboFilter:
    pass


@strawchemy.input(JustificanteGasto, mode="create_input", include="all", exclude=get_exclude_fields(JustificanteGasto))
class JustificanteGastoCreateInput:
    pass


@strawchemy.input(JustificanteGasto, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(JustificanteGasto))
class JustificanteGastoUpdateInput:
    pass


@strawchemy.filter(JustificanteGasto, include="all")
class JustificanteGastoFilter:
    pass


@strawchemy.filter(SolicitudReduccionCuota, include="all")
class SolicitudReduccionCuotaFilter:
    pass


@strawchemy.input(FormaPago, mode="create_input", include="all", exclude=get_exclude_fields(FormaPago))
class FormaPagoCreateInput:
    pass


@strawchemy.input(FormaPago, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(FormaPago))
class FormaPagoUpdateInput:
    pass


@strawchemy.filter(FormaPago)
class FormaPagoFilter:
    pass


@strawchemy.filter(CuentaBancaria, include="all")
class CuentaBancariaFilter:
    pass


@strawchemy.filter(MovimientoTesoreria, include="all")
class MovimientoTesoreriaFilter:
    pass


@strawchemy.filter(ConciliacionBancaria, include="all")
class ConciliacionBancariaFilter:
    pass


@strawchemy.filter(CuentaContable)
class CuentaContableFilter:
    pass


@strawchemy.filter(AsientoContable)
class AsientoContableFilter:
    pass


@strawchemy.filter(ApunteContable)
class ApunteContableFilter:
    pass


@strawchemy.input(CompromisoPresupuestario, mode="create_input", include="all", exclude=get_exclude_fields(CompromisoPresupuestario))
class CompromisoPresupuestarioCreateInput:
    pass


@strawchemy.input(CompromisoPresupuestario, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(CompromisoPresupuestario))
class CompromisoPresupuestarioUpdateInput:
    pass


@strawchemy.filter(CompromisoPresupuestario, include="all")
class CompromisoPresupuestarioFilter:
    pass


# ============================================================================
# VOLUNTARIADO
# ============================================================================

from ..modules.membresia.models import (
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

from ..modules.core.comunicacion import TipoNotificacion, Notificacion, PreferenciaNotificacion, PlantillaEmail


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


_plantilla_exclude = get_exclude_fields(PlantillaEmail) + ["variables_disponibles"]


@strawchemy.input(PlantillaEmail, mode="create_input", include="all", exclude=_plantilla_exclude)
class PlantillaEmailCreateInput:
    pass


@strawchemy.input(PlantillaEmail, mode="update_by_pk_input", include="all", exclude=_plantilla_exclude)
class PlantillaEmailUpdateInput:
    pass


@strawchemy.filter(PlantillaEmail)
class PlantillaEmailFilter:
    pass


# ============================================================================
# COLABORACIONES
# ============================================================================
# El módulo `organizaciones` quedó obsoleto. Sus inputs/filtros GraphQL
# (TipoOrganizacion/Organizacion/EstadoConvenio/Convenio) quedan retirados;
# los convenios de secretaría tienen sus propios resolvers.


# === FINANCIERO — TESORERÍA ===
from ..modules.economico.models import (
    CuentaBancaria,
    ApunteCaja,
    ExtractoBancario,
    ConciliacionBancaria,
    CuentaContable,
    AsientoContable,
    ApunteContable,
)

@strawchemy.input(CuentaBancaria, mode="create_input", include="all", exclude=get_exclude_fields(CuentaBancaria))
class CuentaBancariaCreateInput:
    pass


@strawchemy.input(CuentaBancaria, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(CuentaBancaria))
class CuentaBancariaUpdateInput:
    pass


@strawchemy.input(ApunteCaja, mode="create_input", include="all", exclude=get_exclude_fields(ApunteCaja))
class ApunteCajaCreateInput:
    pass


@strawchemy.input(ApunteCaja, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(ApunteCaja))
class ApunteCajaUpdateInput:
    pass


@strawchemy.filter(ApunteCaja)
class ApunteCajaFilter:
    pass


@strawchemy.input(ExtractoBancario, mode="create_input", include="all", exclude=get_exclude_fields(ExtractoBancario))
class ExtractoBancarioCreateInput:
    pass


@strawchemy.filter(ExtractoBancario, include="all")
class ExtractoBancarioFilter:
    pass


@strawchemy.input(ConciliacionBancaria, mode="create_input", include="all", exclude=get_exclude_fields(ConciliacionBancaria))
class ConciliacionBancariaCreateInput:
    pass


# === FINANCIERO — CONTABILIDAD ===

@strawchemy.input(CuentaContable, mode="create_input", include="all", exclude=get_exclude_fields(CuentaContable))
class CuentaContableCreateInput:
    pass


@strawchemy.input(CuentaContable, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(CuentaContable))
class CuentaContableUpdateInput:
    pass


@strawchemy.input(AsientoContable, mode="create_input", include="all", exclude=get_exclude_fields(AsientoContable))
class AsientoContableCreateInput:
    pass


@strawchemy.input(AsientoContable, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(AsientoContable))
class AsientoContableUpdateInput:
    pass


@strawchemy.input(ApunteContable, mode="create_input", include="all", exclude=get_exclude_fields(ApunteContable))
class ApunteContableCreateInput:
    pass


@strawchemy.input(ApunteContable, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(ApunteContable))
class ApunteContableUpdateInput:
    pass


# === FINANCIERO — REGLAS CONTABLES ===
from ..modules.economico.models.contabilidad import ReglaContable as ReglaContableModel

@strawchemy.input(ReglaContableModel, mode="create_input", include="all", exclude=get_exclude_fields(ReglaContableModel))
class ReglaContableCreateInput:
    pass

@strawchemy.input(ReglaContableModel, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(ReglaContableModel))
class ReglaContableUpdateInput:
    pass

@strawchemy.filter(ReglaContableModel)
class ReglaContableFilter:
    pass


# === PROTECCIÓN DE DATOS (RGPD) ===
from ..modules.proteccion_datos.models import (
    EncargadoTratamiento, ActividadTratamiento, ActividadTratamientoEncargado,
    ClausulaInformativa, Consentimiento, SolicitudDerechoRGPD,
    BrechaSeguridad, AuditoriaAccesoDatos,
)


@strawchemy.input(EncargadoTratamiento, mode="create_input", include="all", exclude=get_exclude_fields(EncargadoTratamiento))
class EncargadoTratamientoCreateInput:
    pass

@strawchemy.input(EncargadoTratamiento, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(EncargadoTratamiento))
class EncargadoTratamientoUpdateInput:
    pass

@strawchemy.filter(EncargadoTratamiento, include="all")
class EncargadoTratamientoFilter:
    pass


@strawchemy.input(ActividadTratamiento, mode="create_input", include="all", exclude=get_exclude_fields(ActividadTratamiento))
class ActividadTratamientoCreateInput:
    pass

@strawchemy.input(ActividadTratamiento, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(ActividadTratamiento))
class ActividadTratamientoUpdateInput:
    pass

@strawchemy.filter(ActividadTratamiento, include="all")
class ActividadTratamientoFilter:
    pass


@strawchemy.input(ActividadTratamientoEncargado, mode="create_input", include="all", exclude=get_exclude_fields(ActividadTratamientoEncargado))
class ActividadTratamientoEncargadoCreateInput:
    pass

@strawchemy.filter(ActividadTratamientoEncargado, include="all")
class ActividadTratamientoEncargadoFilter:
    pass


@strawchemy.input(ClausulaInformativa, mode="create_input", include="all", exclude=get_exclude_fields(ClausulaInformativa))
class ClausulaInformativaCreateInput:
    pass

@strawchemy.input(ClausulaInformativa, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(ClausulaInformativa))
class ClausulaInformativaUpdateInput:
    pass

@strawchemy.filter(ClausulaInformativa, include="all")
class ClausulaInformativaFilter:
    pass


@strawchemy.input(Consentimiento, mode="create_input", include="all", exclude=get_exclude_fields(Consentimiento))
class ConsentimientoCreateInput:
    pass

@strawchemy.input(Consentimiento, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Consentimiento))
class ConsentimientoUpdateInput:
    pass

@strawchemy.filter(Consentimiento, include="all")
class ConsentimientoFilter:
    pass


@strawchemy.input(SolicitudDerechoRGPD, mode="create_input", include="all", exclude=get_exclude_fields(SolicitudDerechoRGPD))
class SolicitudDerechoRGPDCreateInput:
    pass

@strawchemy.input(SolicitudDerechoRGPD, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(SolicitudDerechoRGPD))
class SolicitudDerechoRGPDUpdateInput:
    pass

@strawchemy.filter(SolicitudDerechoRGPD, include="all")
class SolicitudDerechoRGPDFilter:
    pass


@strawchemy.input(BrechaSeguridad, mode="create_input", include="all", exclude=get_exclude_fields(BrechaSeguridad))
class BrechaSeguridadCreateInput:
    pass

@strawchemy.input(BrechaSeguridad, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(BrechaSeguridad))
class BrechaSeguridadUpdateInput:
    pass

@strawchemy.filter(BrechaSeguridad, include="all")
class BrechaSeguridadFilter:
    pass


@strawchemy.filter(AuditoriaAccesoDatos, include="all")
class AuditoriaAccesoDatosFilter:
    pass


# === SECRETARÍA — PLATAFORMAS TELEMÁTICAS ===
from ..modules.secretaria.models import PlataformaTelematica

@strawchemy.input(PlataformaTelematica, mode="create_input", include="all", exclude=get_exclude_fields(PlataformaTelematica))
class PlataformaTelematicaCreateInput:
    pass

@strawchemy.input(PlataformaTelematica, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(PlataformaTelematica))
class PlataformaTelematicaUpdateInput:
    pass

@strawchemy.filter(PlataformaTelematica, include="all")
class PlataformaTelematicaFilter:
    pass


# === RELACIONES (contacto ↔ contacto) ===
from ..modules.membresia.models import TipoRelacion, Relacion


@strawchemy.input(TipoRelacion, mode="create_input", include="all", exclude=get_exclude_fields(TipoRelacion))
class TipoRelacionCreateInput:
    pass


@strawchemy.input(TipoRelacion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TipoRelacion))
class TipoRelacionUpdateInput:
    pass


@strawchemy.filter(TipoRelacion, include="all")
class TipoRelacionFilter:
    pass


@strawchemy.input(Relacion, mode="create_input", include="all", exclude=get_exclude_fields(Relacion))
class RelacionCreateInput:
    pass


@strawchemy.input(Relacion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Relacion))
class RelacionUpdateInput:
    pass


@strawchemy.filter(Relacion, include="all")
class RelacionFilter:
    pass


# === ETIQUETAS (tags de contacto) ===
from ..modules.membresia.models import Etiqueta, ContactoEtiqueta


@strawchemy.input(Etiqueta, mode="create_input", include="all", exclude=get_exclude_fields(Etiqueta))
class EtiquetaCreateInput:
    pass


@strawchemy.input(Etiqueta, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Etiqueta))
class EtiquetaUpdateInput:
    pass


@strawchemy.filter(Etiqueta, include="all")
class EtiquetaFilter:
    pass


@strawchemy.input(ContactoEtiqueta, mode="create_input", include="all", exclude=get_exclude_fields(ContactoEtiqueta))
class ContactoEtiquetaCreateInput:
    pass


@strawchemy.filter(ContactoEtiqueta, include="all")
class ContactoEtiquetaFilter:
    pass
