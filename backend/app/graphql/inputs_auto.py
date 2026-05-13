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
    TipoVinculacion,
)


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

from ..modules.core.geografico import Pais, Provincia, Municipio, AgrupacionTerritorial, TipoUnidadOrganizativa


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


@strawchemy.filter(AgrupacionTerritorial)
class AgrupacionTerritorialFilter:
    pass


@strawchemy.input(TipoUnidadOrganizativa, mode="create_input", include="all",
                  exclude=get_exclude_fields(TipoUnidadOrganizativa))
class TipoUnidadOrganizativaCreateInput:
    padre_tipo_id: Optional[uuid.UUID] = None


@strawchemy.input(TipoUnidadOrganizativa, mode="update_by_pk_input", include="all",
                  exclude=get_exclude_fields(TipoUnidadOrganizativa))
class TipoUnidadOrganizativaUpdateInput:
    padre_tipo_id: Optional[uuid.UUID] = None


@strawchemy.filter(TipoUnidadOrganizativa)
class TipoUnidadOrganizativaFilter:
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
    TipoMiembro, EstadoMiembro, MotivoBaja, Miembro,
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


@strawchemy.filter(Miembro, include="all")
class MiembroFilter:
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
    pass


@strawchemy.input(Habilidad, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Habilidad))
class HabilidadUpdateInput:
    pass


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

from ..modules.actividades.models import TipoCampania, Campania, RolParticipante, ParticipanteCampania


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
# ACCIONES (unifica Evento + Actividad)
# ============================================================================

from ..modules.actividades.models import TipoAccion, Accion, Tarea, Participacion


@strawchemy.input(TipoAccion, mode="create_input", include="all", exclude=get_exclude_fields(TipoAccion))
class TipoAccionCreateInput:
    pass


@strawchemy.input(TipoAccion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TipoAccion))
class TipoAccionUpdateInput:
    pass


@strawchemy.filter(TipoAccion, include="all")
class TipoAccionFilter:
    pass


@strawchemy.input(Accion, mode="create_input", include="all", exclude=get_exclude_fields(Accion))
class AccionCreateInput:
    pass


@strawchemy.input(Accion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Accion))
class AccionUpdateInput:
    pass


@strawchemy.filter(Accion, include="all")
class AccionFilter:
    pass


@strawchemy.input(Tarea, mode="create_input", include="all", exclude=get_exclude_fields(Tarea))
class TareaCreateInput:
    pass


@strawchemy.input(Tarea, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Tarea))
class TareaUpdateInput:
    pass


@strawchemy.filter(Tarea, include="all")
class TareaFilter:
    pass


@strawchemy.input(Participacion, mode="create_input", include="all", exclude=get_exclude_fields(Participacion))
class ParticipacionCreateInput:
    pass


@strawchemy.input(Participacion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Participacion))
class ParticipacionUpdateInput:
    pass


@strawchemy.filter(Participacion, include="all")
class ParticipacionFilter:
    pass


# ============================================================================
# GRUPOS
# ============================================================================

from ..modules.actividades.models import TipoGrupo, RolGrupo, GrupoTrabajo, MiembroGrupo, GrupoIniciativa


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


@strawchemy.input(GrupoIniciativa, mode="create_input", include="all", exclude=get_exclude_fields(GrupoIniciativa))
class GrupoIniciativaCreateInput:
    pass


@strawchemy.input(GrupoIniciativa, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(GrupoIniciativa))
class GrupoIniciativaUpdateInput:
    pass


@strawchemy.filter(GrupoIniciativa, include="all")
class GrupoIniciativaFilter:
    pass


# ============================================================================
# FINANCIERO
# ============================================================================

from ..modules.economico.models import (
    ImporteCuotaAnio, CuotaAnual, DonacionConcepto, Donacion, Remesa, OrdenCobro, FormaPago,
    CuentaBancaria, MovimientoTesoreria, ConciliacionBancaria,
    CuentaContable, AsientoContable, ApunteContable, BalanceContable,
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


@strawchemy.input(FormaPago, mode="create_input", include="all", exclude=get_exclude_fields(FormaPago))
class FormaPagoCreateInput:
    pass


@strawchemy.input(FormaPago, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(FormaPago))
class FormaPagoUpdateInput:
    pass


@strawchemy.filter(FormaPago)
class FormaPagoFilter:
    pass


@strawchemy.filter(CuentaBancaria)
class CuentaBancariaFilter:
    pass


@strawchemy.filter(MovimientoTesoreria)
class MovimientoTesoreriaFilter:
    pass


@strawchemy.filter(ConciliacionBancaria)
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

from ..modules.core.comunicacion import TipoNotificacion, Notificacion, PreferenciaNotificacion


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

from ..modules.organizaciones.models import TipoOrganizacion, Organizacion, EstadoConvenio, Convenio


@strawchemy.input(TipoOrganizacion, mode="create_input", include="all", exclude=get_exclude_fields(TipoOrganizacion))
class TipoOrganizacionCreateInput:
    pass


@strawchemy.input(TipoOrganizacion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(TipoOrganizacion))
class TipoOrganizacionUpdateInput:
    pass


@strawchemy.filter(TipoOrganizacion)
class TipoOrganizacionFilter:
    pass


@strawchemy.input(Organizacion, mode="create_input", include="all", exclude=get_exclude_fields(Organizacion))
class OrganizacionCreateInput:
    pass


@strawchemy.input(Organizacion, mode="update_by_pk_input", include="all", exclude=get_exclude_fields(Organizacion))
class OrganizacionUpdateInput:
    pass


@strawchemy.filter(Organizacion)
class OrganizacionFilter:
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
