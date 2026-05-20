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
from .configuracion_resolvers import ConfiguracionOrganizacionMutation
from .acceso_resolvers import AccesoMutation
from .economico_resolvers import EconomicoMutation
from .membresia_resolvers import MembresiaResolverMutation
from .secretaria_resolvers import SecretariaResolverMutation
from .geografico_resolvers import GeograficoMutation
from .campania_resolvers import CampaniaResolverMutation, CampaniaClonarMutation
from .actividad_resolvers import ActividadResolverMutation
from .papelera_resolvers import PapeleraResolverMutation
from .economico_mutations import EconomicoFlujosMutation
from .types_auto import *
from .inputs_auto import *
from .categoria_fiscal_resolvers import CategoriaFiscalMutation
from .categorizacion_resolvers import CategorizacionMutation


@strawberry.type
class Mutation(AuthMutation, EconomicoFlujosMutation, ConfiguracionOrganizacionMutation, AccesoMutation, EconomicoMutation, MembresiaResolverMutation, GeograficoMutation, CampaniaResolverMutation, CampaniaClonarMutation, ActividadResolverMutation, PapeleraResolverMutation, SecretariaResolverMutation, CategoriaFiscalMutation, CategorizacionMutation):
    """Mutations GraphQL del sistema SIGA con generación automática."""

    # === ACCESO: roles y transacciones (CRUD) ===
    # crear_rol / actualizar_rol / eliminar_roles → AccesoMutation (custom, protege roles sistema)

    crear_transaccion: TransaccionType = strawchemy.create(TransaccionCreateInput)
    actualizar_transaccion: TransaccionType = strawchemy.update_by_ids(TransaccionUpdateInput)
    eliminar_transacciones: list[TransaccionType] = strawchemy.delete(TransaccionFilter)

    # asignar_transaccion_rol / revocar_transaccion_rol → AccesoMutation (custom)

    crear_funcionalidad: FuncionalidadType = strawchemy.create(FuncionalidadCreateInput)
    actualizar_funcionalidad: FuncionalidadType = strawchemy.update_by_ids(FuncionalidadUpdateInput)
    eliminar_funcionalidades: list[FuncionalidadType] = strawchemy.delete(FuncionalidadFilter)

    # asignar_rol_usuario / revocar_rol_usuario → AccesoMutation (custom)
    eliminar_usuarios_roles: list[UsuarioRolType] = strawchemy.delete(UsuarioRolFilter)

    crear_tipo_vinculacion: TipoVinculacionType = strawchemy.create(TipoVinculacionCreateInput)
    actualizar_tipo_vinculacion: TipoVinculacionType = strawchemy.update_by_ids(TipoVinculacionUpdateInput)
    eliminar_tipos_vinculacion: list[TipoVinculacionType] = strawchemy.delete(TipoVinculacionFilter)

    # === CARGOS ORGÁNICOS ===
    crear_cargo: CargoType = strawchemy.create(CargoCreateInput)
    actualizar_cargo: CargoType = strawchemy.update_by_ids(CargoUpdateInput)
    eliminar_cargos: list[CargoType] = strawchemy.delete(CargoFilter)
    crear_cargo_rol: CargoRolType = strawchemy.create(CargoRolCreateInput)
    eliminar_cargos_roles: list[CargoRolType] = strawchemy.delete(CargoRolFilter)

    # === NOMBRAMIENTOS ===
    crear_historial_nombramiento: HistorialNombramientoType = strawchemy.create(HistorialNombramientoCreateInput)
    actualizar_historial_nombramiento: HistorialNombramientoType = strawchemy.update_by_ids(HistorialNombramientoUpdateInput)
    eliminar_historial_nombramientos: list[HistorialNombramientoType] = strawchemy.delete(HistorialNombramientoFilter)

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

    # === TEMAS UI ===
    crear_tema_ui: TemaUIType = strawchemy.create(TemaUICreateInput)
    actualizar_tema_ui: TemaUIType = strawchemy.update_by_ids(TemaUIUpdateInput)
    eliminar_temas_ui: list[TemaUIType] = strawchemy.delete(TemaUIFilter)

    # === GEOGRÁFICO ===
    crear_ambito_geografico: AmbitoGeograficoType = strawchemy.create(AmbitoGeograficoCreateInput)
    actualizar_ambito_geografico: AmbitoGeograficoType = strawchemy.update_by_ids(AmbitoGeograficoUpdateInput)
    eliminar_ambitos_geograficos: list[AmbitoGeograficoType] = strawchemy.delete(AmbitoGeograficoFilter)

    # crear_nivel_organizativo / actualizar_nivel_organizativo → GeograficoMutation (custom, FK UUID explícitos)
    eliminar_niveles_organizativos: list[NivelOrganizativoType] = strawchemy.delete(NivelOrganizativoFilter)

    eliminar_unidades_organizativas: list[UnidadOrganizativaType] = strawchemy.delete(UnidadOrganizativaFilter)

    crear_pais: PaisType = strawchemy.create(PaisCreateInput)
    actualizar_pais: PaisType = strawchemy.update_by_ids(PaisUpdateInput)
    eliminar_paises: list[PaisType] = strawchemy.delete(PaisFilter)

    crear_provincia: ProvinciaType = strawchemy.create(ProvinciaCreateInput)
    actualizar_provincia: ProvinciaType = strawchemy.update_by_ids(ProvinciaUpdateInput)
    eliminar_provincias: list[ProvinciaType] = strawchemy.delete(ProvinciaFilter)

    crear_municipio: MunicipioType = strawchemy.create(MunicipioCreateInput)
    actualizar_municipio: MunicipioType = strawchemy.update_by_ids(MunicipioUpdateInput)
    eliminar_municipios: list[MunicipioType] = strawchemy.delete(MunicipioFilter)

    # crear_unidad_organizativa / actualizar_unidad_organizativa / archivar_unidad_organizativa
    # → GeograficoMutation (resolver custom con FK UUID explícitos)

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

    # crear_miembro / actualizar_miembro → MembresiaResolverMutation (custom, incluye FK UUIDs)
    eliminar_miembros: list[MiembroType] = strawchemy.delete(MiembroFilter)

    # === MILITANCIA ===
    crear_nivel_estudios: NivelEstudiosType = strawchemy.create(NivelEstudiosCreateInput)
    actualizar_niveles_estudios: list[NivelEstudiosType] = strawchemy.update(NivelEstudiosUpdateInput, NivelEstudiosFilter)
    eliminar_niveles_estudios: list[NivelEstudiosType] = strawchemy.delete(NivelEstudiosFilter)

    crear_nivel_habilidad: NivelHabilidadType = strawchemy.create(NivelHabilidadCreateInput)
    actualizar_niveles_habilidad: list[NivelHabilidadType] = strawchemy.update(NivelHabilidadUpdateInput, NivelHabilidadFilter)
    eliminar_niveles_habilidad: list[NivelHabilidadType] = strawchemy.delete(NivelHabilidadFilter)

    crear_categoria_habilidad: CategoriaHabilidadType = strawchemy.create(CategoriaHabilidadCreateInput)
    actualizar_categoria_habilidad: CategoriaHabilidadType = strawchemy.update_by_ids(CategoriaHabilidadUpdateInput)
    eliminar_categorias_habilidad: list[CategoriaHabilidadType] = strawchemy.delete(CategoriaHabilidadFilter)

    crear_habilidad: HabilidadType = strawchemy.create(HabilidadCreateInput)
    actualizar_habilidad: HabilidadType = strawchemy.update_by_ids(HabilidadUpdateInput)
    eliminar_habilidades: list[HabilidadType] = strawchemy.delete(HabilidadFilter)

    crear_miembro_habilidad: MiembroHabilidadType = strawchemy.create(MiembroHabilidadCreateInput)
    actualizar_miembro_habilidad: MiembroHabilidadType = strawchemy.update_by_ids(MiembroHabilidadUpdateInput)
    eliminar_miembros_habilidad: list[MiembroHabilidadType] = strawchemy.delete(MiembroHabilidadFilter)

    crear_franja_disponibilidad: FranjaDisponibilidadType = strawchemy.create(FranjaDisponibilidadCreateInput)
    actualizar_franja_disponibilidad: FranjaDisponibilidadType = strawchemy.update_by_ids(FranjaDisponibilidadUpdateInput)
    eliminar_franjas_disponibilidad: list[FranjaDisponibilidadType] = strawchemy.delete(FranjaDisponibilidadFilter)

    crear_solicitud_traslado: SolicitudTrasladoType = strawchemy.create(SolicitudTrasladoCreateInput)
    actualizar_solicitud_traslado: SolicitudTrasladoType = strawchemy.update_by_ids(SolicitudTrasladoUpdateInput)
    eliminar_solicitudes_traslado: list[SolicitudTrasladoType] = strawchemy.delete(SolicitudTrasladoFilter)

    # === CAMPAÑAS: catálogos ===
    crear_tipo_meta: TipoMetaType = strawchemy.create(TipoMetaCreateInput)
    actualizar_tipo_meta: TipoMetaType = strawchemy.update_by_ids(TipoMetaUpdateInput)
    eliminar_tipos_meta: list[TipoMetaType] = strawchemy.delete(TipoMetaFilter)

    crear_tipo_canal_difusion: TipoCanalDifusionType = strawchemy.create(TipoCanalDifusionCreateInput)
    actualizar_tipo_canal_difusion: TipoCanalDifusionType = strawchemy.update_by_ids(TipoCanalDifusionUpdateInput)
    eliminar_tipos_canal_difusion: list[TipoCanalDifusionType] = strawchemy.delete(TipoCanalDifusionFilter)

    crear_tipo_campania: TipoCampaniaType = strawchemy.create(TipoCampaniaCreateInput)
    actualizar_tipo_campania: TipoCampaniaType = strawchemy.update_by_ids(TipoCampaniaUpdateInput)
    eliminar_tipos_campania: list[TipoCampaniaType] = strawchemy.delete(TipoCampaniaFilter)

    # === CAMPAÑAS: instancias ===
    # crear_campania / actualizar_campania → CampaniaResolverMutation (custom)
    eliminar_campanias: list[CampaniaType] = strawchemy.delete(CampaniaFilter)

    crear_meta_campania: MetaCampaniaType = strawchemy.create(MetaCampaniaCreateInput)
    actualizar_meta_campania: MetaCampaniaType = strawchemy.update_by_ids(MetaCampaniaUpdateInput)

    crear_canal_difusion_campania: CanalDifusionCampaniaType = strawchemy.create(CanalDifusionCampaniaCreateInput)

    crear_partida_presupuesto_campania: PartidaPresupuestoCampaniaType = strawchemy.create(PartidaPresupuestoCampaniaCreateInput)
    actualizar_partida_presupuesto_campania: PartidaPresupuestoCampaniaType = strawchemy.update_by_ids(PartidaPresupuestoCampaniaUpdateInput)

    # === CAMPAÑAS: plantillas ===
    crear_plantilla_campania: PlantillaCampaniaType = strawchemy.create(PlantillaCampaniaCreateInput)
    actualizar_plantilla_campania: PlantillaCampaniaType = strawchemy.update_by_ids(PlantillaCampaniaUpdateInput)
    eliminar_plantillas_campania: list[PlantillaCampaniaType] = strawchemy.delete(PlantillaCampaniaFilter)

    crear_plantilla_meta: PlantillaMetaType = strawchemy.create(PlantillaMetaCreateInput)
    actualizar_plantilla_meta: PlantillaMetaType = strawchemy.update_by_ids(PlantillaMetaUpdateInput)
    eliminar_plantilla_metas: list[PlantillaMetaType] = strawchemy.delete(PlantillaMetaFilter)

    crear_plantilla_partida: PlantillaPartidaType = strawchemy.create(PlantillaPartidaCreateInput)
    actualizar_plantilla_partida: PlantillaPartidaType = strawchemy.update_by_ids(PlantillaPartidaUpdateInput)
    eliminar_plantilla_partidas: list[PlantillaPartidaType] = strawchemy.delete(PlantillaPartidaFilter)

    crear_plantilla_actividad: PlantillaActividadType = strawchemy.create(PlantillaActividadCreateInput)
    actualizar_plantilla_actividad: PlantillaActividadType = strawchemy.update_by_ids(PlantillaActividadUpdateInput)

    crear_plantilla_tarea: PlantillaTareaType = strawchemy.create(PlantillaTareaCreateInput)
    actualizar_plantilla_tarea: PlantillaTareaType = strawchemy.update_by_ids(PlantillaTareaUpdateInput)

    crear_rol_participante: RolParticipanteType = strawchemy.create(RolParticipanteCreateInput)
    actualizar_rol_participante: RolParticipanteType = strawchemy.update_by_ids(RolParticipanteUpdateInput)
    eliminar_roles_participante: list[RolParticipanteType] = strawchemy.delete(RolParticipanteFilter)

    crear_participante_campania: ParticipanteCampaniaType = strawchemy.create(ParticipanteCampaniaCreateInput)
    actualizar_participante_campania: ParticipanteCampaniaType = strawchemy.update_by_ids(ParticipanteCampaniaUpdateInput)
    eliminar_participantes_campania: list[ParticipanteCampaniaType] = strawchemy.delete(ParticipanteCampaniaFilter)

    # === ACTIVIDADES ===
    crear_estado_accion: EstadoAccionType = strawchemy.create(EstadoAccionCreateInput)
    actualizar_estado_accion: EstadoAccionType = strawchemy.update_by_ids(EstadoAccionUpdateInput)
    eliminar_estados_accion: list[EstadoAccionType] = strawchemy.delete(EstadoAccionFilter)
    # Alias semántico
    crear_estado_actividad: EstadoAccionType = strawchemy.create(EstadoAccionCreateInput)
    actualizar_estado_actividad: EstadoAccionType = strawchemy.update_by_ids(EstadoAccionUpdateInput)
    eliminar_estados_actividad: list[EstadoAccionType] = strawchemy.delete(EstadoAccionFilter)

    crear_tipo_actividad: TipoActividadType = strawchemy.create(TipoActividadCreateInput)
    actualizar_tipo_actividad: TipoActividadType = strawchemy.update_by_ids(TipoActividadUpdateInput)
    eliminar_tipos_actividad: list[TipoActividadType] = strawchemy.delete(TipoActividadFilter)

    # crear_actividad / actualizar_actividad → ActividadResolverMutation (custom, FK IDs)
    eliminar_actividades: list[ActividadType] = strawchemy.delete(ActividadFilter)

    # crear_tarea / actualizar_tarea → ActividadResolverMutation (custom, FK IDs)
    eliminar_tareas: list[TareaType] = strawchemy.delete(TareaFilter)

    # crear_participacion → ActividadResolverMutation (custom, FK IDs)
    actualizar_participacion: ParticipacionType = strawchemy.update_by_ids(ParticipacionUpdateInput)
    eliminar_participaciones: list[ParticipacionType] = strawchemy.delete(ParticipacionFilter)

    crear_partida_presupuesto_actividad: PartidaPresupuestoActividadType = strawchemy.create(PartidaPresupuestoActividadCreateInput)
    actualizar_partida_presupuesto_actividad: PartidaPresupuestoActividadType = strawchemy.update_by_ids(PartidaPresupuestoActividadUpdateInput)
    eliminar_partidas_presupuesto_actividad: list[PartidaPresupuestoActividadType] = strawchemy.delete(PartidaPresupuestoActividadFilter)

    crear_registro_trabajo_actividad: RegistroTrabajoActividadType = strawchemy.create(RegistroTrabajoActividadCreateInput)
    actualizar_registro_trabajo_actividad: RegistroTrabajoActividadType = strawchemy.update_by_ids(RegistroTrabajoActividadUpdateInput)
    eliminar_registros_trabajo_actividad: list[RegistroTrabajoActividadType] = strawchemy.delete(RegistroTrabajoActividadFilter)

    # documentos: alta via REST /api/uploads/; baja via GraphQL
    eliminar_documentos_actividad: list[DocumentoActividadType] = strawchemy.delete(DocumentoActividadFilter)
    eliminar_documentos_partida: list[DocumentoPartidaType] = strawchemy.delete(DocumentoPartidaFilter)

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

    crear_grupo_iniciativa: GrupoIniciativaType = strawchemy.create(GrupoIniciativaCreateInput)
    actualizar_grupo_iniciativa: GrupoIniciativaType = strawchemy.update_by_ids(GrupoIniciativaUpdateInput)
    eliminar_grupos_iniciativa: list[GrupoIniciativaType] = strawchemy.delete(GrupoIniciativaFilter)

    crear_requisito_recurso: RequisitoRecursoType = strawchemy.create(RequisitoRecursoCreateInput)
    actualizar_requisito_recurso: RequisitoRecursoType = strawchemy.update_by_ids(RequisitoRecursoUpdateInput)
    eliminar_requisitos_recurso: list[RequisitoRecursoType] = strawchemy.delete(RequisitoRecursoFilter)

    crear_aportacion_horas: AportacionHorasType = strawchemy.create(AportacionHorasCreateInput)
    actualizar_aportacion_horas: AportacionHorasType = strawchemy.update_by_ids(AportacionHorasUpdateInput)
    eliminar_aportaciones_horas: list[AportacionHorasType] = strawchemy.delete(AportacionHorasFilter)

    # === FINANCIERO ===
    crear_importe_cuota_anio: ImporteCuotaAnioType = strawchemy.create(ImporteCuotaAnioCreateInput)
    actualizar_importe_cuota_anio: ImporteCuotaAnioType = strawchemy.update_by_ids(ImporteCuotaAnioUpdateInput)
    eliminar_importes_cuota_anio: list[ImporteCuotaAnioType] = strawchemy.delete(ImporteCuotaAnioFilter)

    crear_cuota_anual: CuotaAnualType = strawchemy.create(CuotaAnualCreateInput)
    crear_cuotas_anuales: list[CuotaAnualType] = strawchemy.create(CuotaAnualCreateInput)  # Batch
    actualizar_cuota_anual: CuotaAnualType = strawchemy.update_by_ids(CuotaAnualUpdateInput)
    eliminar_cuotas_anuales: list[CuotaAnualType] = strawchemy.delete(CuotaAnualFilter)

    # Flujo 1 — catálogo de motivos de reducción
    # Create/update se hacen vía resolvers manuales en economico_mutations.py
    # (con guard CUOT_MOTIVO_REDUC_MGMT + validación D1.5 de inmutabilidad del %).
    eliminar_motivos_reduccion_cuota: list[MotivoReduccionCuotaType] = strawchemy.delete(MotivoReduccionCuotaFilter)

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

    crear_recibo: ReciboType = strawchemy.create(ReciboCreateInput)
    actualizar_recibo: ReciboType = strawchemy.update_by_ids(ReciboUpdateInput)
    eliminar_recibos: list[ReciboType] = strawchemy.delete(ReciboFilter)

    crear_justificante_gasto: JustificanteGastoType = strawchemy.create(JustificanteGastoCreateInput)
    actualizar_justificante_gasto: JustificanteGastoType = strawchemy.update_by_ids(JustificanteGastoUpdateInput)
    eliminar_justificantes_gasto: list[JustificanteGastoType] = strawchemy.delete(JustificanteGastoFilter)

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

    # === PLANTILLAS EMAIL ===
    crear_plantilla_email: PlantillaEmailType = strawchemy.create(PlantillaEmailCreateInput)
    actualizar_plantilla_email: PlantillaEmailType = strawchemy.update_by_ids(PlantillaEmailUpdateInput)
    eliminar_plantillas_email: list[PlantillaEmailType] = strawchemy.delete(PlantillaEmailFilter)

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
    crear_tipo_asociacion: TipoOrganizacionType = strawchemy.create(TipoOrganizacionCreateInput)
    actualizar_tipo_asociacion: TipoOrganizacionType = strawchemy.update_by_ids(TipoOrganizacionUpdateInput)
    eliminar_tipos_asociacion: list[TipoOrganizacionType] = strawchemy.delete(TipoOrganizacionFilter)

    crear_organizacion: OrganizacionType = strawchemy.create(OrganizacionCreateInput)
    actualizar_organizacion: OrganizacionType = strawchemy.update_by_ids(OrganizacionUpdateInput)
    eliminar_organizaciones: list[OrganizacionType] = strawchemy.delete(OrganizacionFilter)

    crear_estado_convenio: EstadoConvenioType = strawchemy.create(EstadoConvenioCreateInput)
    actualizar_estado_convenio: EstadoConvenioType = strawchemy.update_by_ids(EstadoConvenioUpdateInput)
    eliminar_estados_convenio: list[EstadoConvenioType] = strawchemy.delete(EstadoConvenioFilter)

    crear_convenio: ConvenioType = strawchemy.create(ConvenioCreateInput)
    actualizar_convenio: ConvenioType = strawchemy.update_by_ids(ConvenioUpdateInput)
    eliminar_convenios: list[ConvenioType] = strawchemy.delete(ConvenioFilter)

    # === FINANCIERO — TESORERÍA ===
    crear_cuenta_bancaria: CuentaBancariaType = strawchemy.create(CuentaBancariaCreateInput)
    actualizar_cuenta_bancaria: CuentaBancariaType = strawchemy.update_by_ids(CuentaBancariaUpdateInput)
    eliminar_cuentas_bancarias: list[CuentaBancariaType] = strawchemy.delete(CuentaBancariaFilter)

    crear_apunte_caja: ApunteCajaType = strawchemy.create(ApunteCajaCreateInput)
    actualizar_apunte_caja: ApunteCajaType = strawchemy.update_by_ids(ApunteCajaUpdateInput)
    eliminar_apuntes_caja: list[ApunteCajaType] = strawchemy.delete(ApunteCajaFilter)

    crear_extracto_bancario: ExtractoBancarioType = strawchemy.create(ExtractoBancarioCreateInput)

    crear_conciliacion_bancaria: ConciliacionBancariaType = strawchemy.create(ConciliacionBancariaCreateInput)

    # === FINANCIERO — CONTABILIDAD ===
    # CuentaContable: CRUD restringido a TESORERO matriz vía resolvers manuales en
    # EconomicoMutation (crear_cuenta_contable / actualizar_cuenta_contable /
    # desactivar_cuenta_contable) con permiso `ECO_ESTRUCTURA_CONTABLE_GESTIONAR`
    # (compartido con la gestión de categorías fiscales en modo simplificado).
    # Las versiones strawchemy quedaron deshabilitadas por seguridad (no admiten permission_classes).

    crear_asiento_contable: AsientoContableType = strawchemy.create(AsientoContableCreateInput)
    actualizar_asiento_contable: AsientoContableType = strawchemy.update_by_ids(AsientoContableUpdateInput)
    eliminar_asientos_contables: list[AsientoContableType] = strawchemy.delete(AsientoContableFilter)

    crear_apunte_contable: ApunteContableType = strawchemy.create(ApunteContableCreateInput)
    actualizar_apunte_contable: ApunteContableType = strawchemy.update_by_ids(ApunteContableUpdateInput)
    eliminar_apuntes_contables: list[ApunteContableType] = strawchemy.delete(ApunteContableFilter)

    # === FINANCIERO — REGLAS CONTABLES ===
    crear_regla_contable: ReglaContableType = strawchemy.create(ReglaContableCreateInput)
    actualizar_regla_contable: ReglaContableType = strawchemy.update_by_ids(ReglaContableUpdateInput)
    eliminar_reglas_contables: list[ReglaContableType] = strawchemy.delete(ReglaContableFilter)

    # === FORMAS DE PAGO ===
    crear_forma_pago: FormaPagoType = strawchemy.create(FormaPagoCreateInput)
    actualizar_forma_pago: FormaPagoType = strawchemy.update_by_ids(FormaPagoUpdateInput)
    eliminar_formas_pago: list[FormaPagoType] = strawchemy.delete(FormaPagoFilter)

    # === COMPROMISOS PRESUPUESTARIOS ===
    crear_compromiso_presupuestario: CompromisoPresupuestarioType = strawchemy.create(CompromisoPresupuestarioCreateInput)
    actualizar_compromiso_presupuestario: CompromisoPresupuestarioType = strawchemy.update_by_ids(CompromisoPresupuestarioUpdateInput)
    eliminar_compromisos_presupuestarios: list[CompromisoPresupuestarioType] = strawchemy.delete(CompromisoPresupuestarioFilter)
