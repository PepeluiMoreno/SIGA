"""
Mutaciones GraphQL para SIGA con generación automática de Strawchemy.

Strawchemy genera automáticamente:
- Create mutations (single y batch)
- Update mutations (by id y by filter)
- Delete mutations (by filter)
- Soporte para relaciones anidadas
"""

import strawberry

from . import strawchemy
from .auth import AuthMutation
from .types_auto import *
from .inputs_auto import *


@strawberry.type
class Mutation(AuthMutation):
    """Mutations GraphQL del sistema SIGA con generación automática."""

    # === ACCESO: roles, transacciones, funcionalidades ===
    crear_rol: RolType = strawchemy.create(RolCreateInput)
    actualizar_rol: RolType = strawchemy.update_by_ids(RolUpdateInput)
    eliminar_roles: list[RolType] = strawchemy.delete(RolFilter)

    crear_transaccion: TransaccionType = strawchemy.create(TransaccionCreateInput)
    actualizar_transaccion: TransaccionType = strawchemy.update_by_ids(TransaccionUpdateInput)
    eliminar_transacciones: list[TransaccionType] = strawchemy.delete(TransaccionFilter)

    crear_rol_transaccion: RolTransaccionType = strawchemy.create(RolTransaccionCreateInput)
    eliminar_roles_transacciones: list[RolTransaccionType] = strawchemy.delete(RolTransaccionFilter)

    crear_funcionalidad: FuncionalidadType = strawchemy.create(FuncionalidadCreateInput)
    actualizar_funcionalidad: FuncionalidadType = strawchemy.update_by_ids(FuncionalidadUpdateInput)
    eliminar_funcionalidades: list[FuncionalidadType] = strawchemy.delete(FuncionalidadFilter)

    crear_rol_funcionalidad: RolFuncionalidadType = strawchemy.create(RolFuncionalidadCreateInput)
    eliminar_roles_funcionalidades: list[RolFuncionalidadType] = strawchemy.delete(RolFuncionalidadFilter)

    crear_usuario_rol: UsuarioRolType = strawchemy.create(UsuarioRolCreateInput)
    eliminar_usuarios_roles: list[UsuarioRolType] = strawchemy.delete(UsuarioRolFilter)

    # === CORE - Estados ===
    crear_estado_cuota: EstadoCuotaType = strawchemy.create(EstadoCuotaCreateInput)
    actualizar_estado_cuota: EstadoCuotaType = strawchemy.update_by_ids(EstadoCuotaUpdateInput)
    eliminar_estados_cuota: list[EstadoCuotaType] = strawchemy.delete(EstadoCuotaFilter)

    crear_estado_campania: EstadoCampaniaType = strawchemy.create(EstadoCampaniaCreateInput)
    actualizar_estado_campania: EstadoCampaniaType = strawchemy.update_by_ids(EstadoCampaniaUpdateInput)
    eliminar_estados_campania: list[EstadoCampaniaType] = strawchemy.delete(EstadoCampaniaFilter)

    crear_estado_tarea: EstadoTareaType = strawchemy.create(EstadoTareaCreateInput)
    actualizar_estado_tarea: EstadoTareaType = strawchemy.update_by_ids(EstadoTareaUpdateInput)
    eliminar_estados_tarea: list[EstadoTareaType] = strawchemy.delete(EstadoTareaFilter)

    crear_estado_participante: EstadoParticipanteType = strawchemy.create(EstadoParticipanteCreateInput)
    actualizar_estado_participante: EstadoParticipanteType = strawchemy.update_by_ids(EstadoParticipanteUpdateInput)
    eliminar_estados_participante: list[EstadoParticipanteType] = strawchemy.delete(EstadoParticipanteFilter)

    crear_estado_orden_cobro: EstadoOrdenCobroType = strawchemy.create(EstadoOrdenCobroCreateInput)
    actualizar_estado_orden_cobro: EstadoOrdenCobroType = strawchemy.update_by_ids(EstadoOrdenCobroUpdateInput)
    eliminar_estados_orden_cobro: list[EstadoOrdenCobroType] = strawchemy.delete(EstadoOrdenCobroFilter)

    crear_estado_remesa: EstadoRemesaType = strawchemy.create(EstadoRemesaCreateInput)
    actualizar_estado_remesa: EstadoRemesaType = strawchemy.update_by_ids(EstadoRemesaUpdateInput)
    eliminar_estados_remesa: list[EstadoRemesaType] = strawchemy.delete(EstadoRemesaFilter)

    crear_estado_donacion: EstadoDonacionType = strawchemy.create(EstadoDonacionCreateInput)
    actualizar_estado_donacion: EstadoDonacionType = strawchemy.update_by_ids(EstadoDonacionUpdateInput)
    eliminar_estados_donacion: list[EstadoDonacionType] = strawchemy.delete(EstadoDonacionFilter)

    crear_estado_notificacion: EstadoNotificacionType = strawchemy.create(EstadoNotificacionCreateInput)
    actualizar_estado_notificacion: EstadoNotificacionType = strawchemy.update_by_ids(EstadoNotificacionUpdateInput)
    eliminar_estados_notificacion: list[EstadoNotificacionType] = strawchemy.delete(EstadoNotificacionFilter)

    # === GEOGRÁFICO ===
    crear_pais: PaisType = strawchemy.create(PaisCreateInput)
    actualizar_pais: PaisType = strawchemy.update_by_ids(PaisUpdateInput)
    eliminar_paises: list[PaisType] = strawchemy.delete(PaisFilter)

    crear_provincia: ProvinciaType = strawchemy.create(ProvinciaCreateInput)
    actualizar_provincia: ProvinciaType = strawchemy.update_by_ids(ProvinciaUpdateInput)
    eliminar_provincias: list[ProvinciaType] = strawchemy.delete(ProvinciaFilter)

    crear_municipio: MunicipioType = strawchemy.create(MunicipioCreateInput)
    actualizar_municipio: MunicipioType = strawchemy.update_by_ids(MunicipioUpdateInput)
    eliminar_municipios: list[MunicipioType] = strawchemy.delete(MunicipioFilter)

    crear_agrupacion_territorial: AgrupacionTerritorialType = strawchemy.create(AgrupacionTerritorialCreateInput)
    actualizar_agrupacion_territorial: AgrupacionTerritorialType = strawchemy.update_by_ids(AgrupacionTerritorialUpdateInput)
    eliminar_agrupaciones_territoriales: list[AgrupacionTerritorialType] = strawchemy.delete(AgrupacionTerritorialFilter)

    # === MIEMBROS ===
    crear_tipo_miembro: TipoMiembroType = strawchemy.create(TipoMiembroCreateInput)
    actualizar_tipo_miembro: TipoMiembroType = strawchemy.update_by_ids(TipoMiembroUpdateInput)
    eliminar_tipos_miembro: list[TipoMiembroType] = strawchemy.delete(TipoMiembroFilter)

    crear_estado_miembro: EstadoMiembroType = strawchemy.create(EstadoMiembroCreateInput)
    actualizar_estado_miembro: EstadoMiembroType = strawchemy.update_by_ids(EstadoMiembroUpdateInput)
    eliminar_estados_miembro: list[EstadoMiembroType] = strawchemy.delete(EstadoMiembroFilter)

    crear_motivo_baja: MotivoBajaType = strawchemy.create(MotivoBajaCreateInput)
    actualizar_motivo_baja: MotivoBajaType = strawchemy.update_by_ids(MotivoBajaUpdateInput)
    eliminar_motivos_baja: list[MotivoBajaType] = strawchemy.delete(MotivoBajaFilter)

    crear_miembro: MiembroType = strawchemy.create(MiembroCreateInput)
    crear_miembros: list[MiembroType] = strawchemy.create(MiembroCreateInput)  # Batch create
    actualizar_miembro: MiembroType = strawchemy.update_by_ids(MiembroUpdateInput)
    eliminar_miembros: list[MiembroType] = strawchemy.delete(MiembroFilter)

    # === MILITANCIA ===
    crear_skill: SkillType = strawchemy.create(SkillCreateInput)
    actualizar_skill: SkillType = strawchemy.update_by_ids(SkillUpdateInput)
    eliminar_skills: list[SkillType] = strawchemy.delete(SkillFilter)

    crear_miembro_skill: MiembroSkillType = strawchemy.create(MiembroSkillCreateInput)
    actualizar_miembro_skill: MiembroSkillType = strawchemy.update_by_ids(MiembroSkillUpdateInput)
    eliminar_miembros_skill: list[MiembroSkillType] = strawchemy.delete(MiembroSkillFilter)

    crear_franja_disponibilidad: FranjaDisponibilidadType = strawchemy.create(FranjaDisponibilidadCreateInput)
    actualizar_franja_disponibilidad: FranjaDisponibilidadType = strawchemy.update_by_ids(FranjaDisponibilidadUpdateInput)
    eliminar_franjas_disponibilidad: list[FranjaDisponibilidadType] = strawchemy.delete(FranjaDisponibilidadFilter)

    crear_solicitud_traslado: SolicitudTrasladoType = strawchemy.create(SolicitudTrasladoCreateInput)
    actualizar_solicitud_traslado: SolicitudTrasladoType = strawchemy.update_by_ids(SolicitudTrasladoUpdateInput)
    eliminar_solicitudes_traslado: list[SolicitudTrasladoType] = strawchemy.delete(SolicitudTrasladoFilter)

    # === CAMPAÑAS ===
    crear_tipo_campania: TipoCampaniaType = strawchemy.create(TipoCampaniaCreateInput)
    actualizar_tipo_campania: TipoCampaniaType = strawchemy.update_by_ids(TipoCampaniaUpdateInput)
    eliminar_tipos_campania: list[TipoCampaniaType] = strawchemy.delete(TipoCampaniaFilter)

    crear_campania: CampaniaType = strawchemy.create(CampaniaCreateInput)
    actualizar_campania: CampaniaType = strawchemy.update_by_ids(CampaniaUpdateInput)
    eliminar_campanias: list[CampaniaType] = strawchemy.delete(CampaniaFilter)

    crear_rol_participante: RolParticipanteType = strawchemy.create(RolParticipanteCreateInput)
    actualizar_rol_participante: RolParticipanteType = strawchemy.update_by_ids(RolParticipanteUpdateInput)
    eliminar_roles_participante: list[RolParticipanteType] = strawchemy.delete(RolParticipanteFilter)

    crear_participante_campania: ParticipanteCampaniaType = strawchemy.create(ParticipanteCampaniaCreateInput)
    actualizar_participante_campania: ParticipanteCampaniaType = strawchemy.update_by_ids(ParticipanteCampaniaUpdateInput)
    eliminar_participantes_campania: list[ParticipanteCampaniaType] = strawchemy.delete(ParticipanteCampaniaFilter)

    # === ACTIVIDADES ===
    crear_tipo_actividad: TipoActividadType = strawchemy.create(TipoActividadCreateInput)
    actualizar_tipo_actividad: TipoActividadType = strawchemy.update_by_ids(TipoActividadUpdateInput)
    eliminar_tipos_actividad: list[TipoActividadType] = strawchemy.delete(TipoActividadFilter)

    crear_estado_actividad: EstadoActividadType = strawchemy.create(EstadoActividadCreateInput)
    actualizar_estado_actividad: EstadoActividadType = strawchemy.update_by_ids(EstadoActividadUpdateInput)
    eliminar_estados_actividad: list[EstadoActividadType] = strawchemy.delete(EstadoActividadFilter)

    crear_estado_propuesta: EstadoPropuestaType = strawchemy.create(EstadoPropuestaCreateInput)
    actualizar_estado_propuesta: EstadoPropuestaType = strawchemy.update_by_ids(EstadoPropuestaUpdateInput)
    eliminar_estados_propuesta: list[EstadoPropuestaType] = strawchemy.delete(EstadoPropuestaFilter)

    crear_tipo_recurso: TipoRecursoType = strawchemy.create(TipoRecursoCreateInput)
    actualizar_tipo_recurso: TipoRecursoType = strawchemy.update_by_ids(TipoRecursoUpdateInput)
    eliminar_tipos_recurso: list[TipoRecursoType] = strawchemy.delete(TipoRecursoFilter)

    crear_tipo_kpi: TipoKPIType = strawchemy.create(TipoKPICreateInput)
    actualizar_tipo_kpi: TipoKPIType = strawchemy.update_by_ids(TipoKPIUpdateInput)
    eliminar_tipos_kpi: list[TipoKPIType] = strawchemy.delete(TipoKPIFilter)

    crear_propuesta_actividad: PropuestaActividadType = strawchemy.create(PropuestaActividadCreateInput)
    actualizar_propuesta_actividad: PropuestaActividadType = strawchemy.update_by_ids(PropuestaActividadUpdateInput)
    eliminar_propuestas_actividad: list[PropuestaActividadType] = strawchemy.delete(PropuestaActividadFilter)

    crear_actividad: ActividadType = strawchemy.create(ActividadCreateInput)
    actualizar_actividad: ActividadType = strawchemy.update_by_ids(ActividadUpdateInput)
    eliminar_actividades: list[ActividadType] = strawchemy.delete(ActividadFilter)

    crear_tarea_actividad: TareaActividadType = strawchemy.create(TareaActividadCreateInput)
    actualizar_tarea_actividad: TareaActividadType = strawchemy.update_by_ids(TareaActividadUpdateInput)
    eliminar_tareas_actividad: list[TareaActividadType] = strawchemy.delete(TareaActividadFilter)

    # === GRUPOS ===
    crear_tipo_grupo: TipoGrupoType = strawchemy.create(TipoGrupoCreateInput)
    actualizar_tipo_grupo: TipoGrupoType = strawchemy.update_by_ids(TipoGrupoUpdateInput)
    eliminar_tipos_grupo: list[TipoGrupoType] = strawchemy.delete(TipoGrupoFilter)

    crear_rol_grupo: RolGrupoType = strawchemy.create(RolGrupoCreateInput)
    actualizar_rol_grupo: RolGrupoType = strawchemy.update_by_ids(RolGrupoUpdateInput)
    eliminar_roles_grupo: list[RolGrupoType] = strawchemy.delete(RolGrupoFilter)

    crear_grupo_trabajo: GrupoTrabajoType = strawchemy.create(GrupoTrabajoCreateInput)
    actualizar_grupo_trabajo: GrupoTrabajoType = strawchemy.update_by_ids(GrupoTrabajoUpdateInput)
    eliminar_grupos_trabajo: list[GrupoTrabajoType] = strawchemy.delete(GrupoTrabajoFilter)

    crear_miembro_grupo: MiembroGrupoType = strawchemy.create(MiembroGrupoCreateInput)
    actualizar_miembro_grupo: MiembroGrupoType = strawchemy.update_by_ids(MiembroGrupoUpdateInput)
    eliminar_miembros_grupo: list[MiembroGrupoType] = strawchemy.delete(MiembroGrupoFilter)

    crear_tarea_grupo: TareaGrupoType = strawchemy.create(TareaGrupoCreateInput)
    actualizar_tarea_grupo: TareaGrupoType = strawchemy.update_by_ids(TareaGrupoUpdateInput)
    eliminar_tareas_grupo: list[TareaGrupoType] = strawchemy.delete(TareaGrupoFilter)

    # === FINANCIERO ===
    crear_importe_cuota_anio: ImporteCuotaAnioType = strawchemy.create(ImporteCuotaAnioCreateInput)
    actualizar_importe_cuota_anio: ImporteCuotaAnioType = strawchemy.update_by_ids(ImporteCuotaAnioUpdateInput)
    eliminar_importes_cuota_anio: list[ImporteCuotaAnioType] = strawchemy.delete(ImporteCuotaAnioFilter)

    crear_cuota_anual: CuotaAnualType = strawchemy.create(CuotaAnualCreateInput)
    crear_cuotas_anuales: list[CuotaAnualType] = strawchemy.create(CuotaAnualCreateInput)  # Batch
    actualizar_cuota_anual: CuotaAnualType = strawchemy.update_by_ids(CuotaAnualUpdateInput)
    eliminar_cuotas_anuales: list[CuotaAnualType] = strawchemy.delete(CuotaAnualFilter)

    crear_donacion_concepto: DonacionConceptoType = strawchemy.create(DonacionConceptoCreateInput)
    actualizar_donacion_concepto: DonacionConceptoType = strawchemy.update_by_ids(DonacionConceptoUpdateInput)
    eliminar_donacion_conceptos: list[DonacionConceptoType] = strawchemy.delete(DonacionConceptoFilter)

    crear_donacion: DonacionType = strawchemy.create(DonacionCreateInput)
    actualizar_donacion: DonacionType = strawchemy.update_by_ids(DonacionUpdateInput)
    eliminar_donaciones: list[DonacionType] = strawchemy.delete(DonacionFilter)

    crear_remesa: RemesaType = strawchemy.create(RemesaCreateInput)
    actualizar_remesa: RemesaType = strawchemy.update_by_ids(RemesaUpdateInput)
    eliminar_remesas: list[RemesaType] = strawchemy.delete(RemesaFilter)

    crear_orden_cobro: OrdenCobroType = strawchemy.create(OrdenCobroCreateInput)
    crear_ordenes_cobro: list[OrdenCobroType] = strawchemy.create(OrdenCobroCreateInput)  # Batch
    actualizar_orden_cobro: OrdenCobroType = strawchemy.update_by_ids(OrdenCobroUpdateInput)
    eliminar_ordenes_cobro: list[OrdenCobroType] = strawchemy.delete(OrdenCobroFilter)

    # === VOLUNTARIADO ===
    crear_categoria_competencia: CategoriaCompetenciaType = strawchemy.create(CategoriaCompetenciaCreateInput)
    actualizar_categoria_competencia: CategoriaCompetenciaType = strawchemy.update_by_ids(CategoriaCompetenciaUpdateInput)
    eliminar_categorias_competencia: list[CategoriaCompetenciaType] = strawchemy.delete(CategoriaCompetenciaFilter)

    crear_competencia: CompetenciaType = strawchemy.create(CompetenciaCreateInput)
    actualizar_competencia: CompetenciaType = strawchemy.update_by_ids(CompetenciaUpdateInput)
    eliminar_competencias: list[CompetenciaType] = strawchemy.delete(CompetenciaFilter)

    crear_nivel_competencia: NivelCompetenciaType = strawchemy.create(NivelCompetenciaCreateInput)
    actualizar_nivel_competencia: NivelCompetenciaType = strawchemy.update_by_ids(NivelCompetenciaUpdateInput)
    eliminar_niveles_competencia: list[NivelCompetenciaType] = strawchemy.delete(NivelCompetenciaFilter)

    crear_miembro_competencia: MiembroCompetenciaType = strawchemy.create(MiembroCompetenciaCreateInput)
    actualizar_miembro_competencia: MiembroCompetenciaType = strawchemy.update_by_ids(MiembroCompetenciaUpdateInput)
    eliminar_miembros_competencia: list[MiembroCompetenciaType] = strawchemy.delete(MiembroCompetenciaFilter)

    crear_tipo_documento_voluntario: TipoDocumentoVoluntarioType = strawchemy.create(TipoDocumentoVoluntarioCreateInput)
    actualizar_tipo_documento_voluntario: TipoDocumentoVoluntarioType = strawchemy.update_by_ids(TipoDocumentoVoluntarioUpdateInput)
    eliminar_tipos_documento_voluntario: list[TipoDocumentoVoluntarioType] = strawchemy.delete(TipoDocumentoVoluntarioFilter)

    crear_documento_miembro: DocumentoMiembroType = strawchemy.create(DocumentoMiembroCreateInput)
    actualizar_documento_miembro: DocumentoMiembroType = strawchemy.update_by_ids(DocumentoMiembroUpdateInput)
    eliminar_documentos_miembro: list[DocumentoMiembroType] = strawchemy.delete(DocumentoMiembroFilter)

    crear_tipo_formacion: TipoFormacionType = strawchemy.create(TipoFormacionCreateInput)
    actualizar_tipo_formacion: TipoFormacionType = strawchemy.update_by_ids(TipoFormacionUpdateInput)
    eliminar_tipos_formacion: list[TipoFormacionType] = strawchemy.delete(TipoFormacionFilter)

    crear_formacion_miembro: FormacionMiembroType = strawchemy.create(FormacionMiembroCreateInput)
    actualizar_formacion_miembro: FormacionMiembroType = strawchemy.update_by_ids(FormacionMiembroUpdateInput)
    eliminar_formaciones_miembro: list[FormacionMiembroType] = strawchemy.delete(FormacionMiembroFilter)

    # === NOTIFICACIONES ===
    crear_tipo_notificacion: TipoNotificacionType = strawchemy.create(TipoNotificacionCreateInput)
    actualizar_tipo_notificacion: TipoNotificacionType = strawchemy.update_by_ids(TipoNotificacionUpdateInput)
    eliminar_tipos_notificacion: list[TipoNotificacionType] = strawchemy.delete(TipoNotificacionFilter)

    crear_notificacion: NotificacionType = strawchemy.create(NotificacionCreateInput)
    crear_notificaciones: list[NotificacionType] = strawchemy.create(NotificacionCreateInput)  # Batch
    actualizar_notificacion: NotificacionType = strawchemy.update_by_ids(NotificacionUpdateInput)
    eliminar_notificaciones: list[NotificacionType] = strawchemy.delete(NotificacionFilter)

    crear_preferencia_notificacion: PreferenciaNotificacionType = strawchemy.create(PreferenciaNotificacionCreateInput)
    actualizar_preferencia_notificacion: PreferenciaNotificacionType = strawchemy.update_by_ids(PreferenciaNotificacionUpdateInput)
    eliminar_preferencias_notificacion: list[PreferenciaNotificacionType] = strawchemy.delete(PreferenciaNotificacionFilter)

    # === COLABORACIONES ===
    crear_tipo_asociacion: TipoAsociacionType = strawchemy.create(TipoAsociacionCreateInput)
    actualizar_tipo_asociacion: TipoAsociacionType = strawchemy.update_by_ids(TipoAsociacionUpdateInput)
    eliminar_tipos_asociacion: list[TipoAsociacionType] = strawchemy.delete(TipoAsociacionFilter)

    crear_asociacion: AsociacionType = strawchemy.create(AsociacionCreateInput)
    actualizar_asociacion: AsociacionType = strawchemy.update_by_ids(AsociacionUpdateInput)
    eliminar_asociaciones: list[AsociacionType] = strawchemy.delete(AsociacionFilter)

    crear_estado_convenio: EstadoConvenioType = strawchemy.create(EstadoConvenioCreateInput)
    actualizar_estado_convenio: EstadoConvenioType = strawchemy.update_by_ids(EstadoConvenioUpdateInput)
    eliminar_estados_convenio: list[EstadoConvenioType] = strawchemy.delete(EstadoConvenioFilter)

    crear_convenio: ConvenioType = strawchemy.create(ConvenioCreateInput)
    actualizar_convenio: ConvenioType = strawchemy.update_by_ids(ConvenioUpdateInput)
    eliminar_convenios: list[ConvenioType] = strawchemy.delete(ConvenioFilter)
