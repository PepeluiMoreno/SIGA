// Queries GraphQL para el módulo de campañas
// IMPORTANTE: Strawberry usa camelCase automáticamente
// NO usar campos 'codigo' - solo se identifican por UUID

export const GET_CAMPANIAS = `
  query Campanias {
    campanias(filter: { eliminado: { eq: false } }) {
      id
      nombre
      lema
      descripcionCorta
      descripcionLarga
      urlExterna
      tipoCampania {
        id
        nombre
      }
      estado {
        id
        nombre
      }
      responsable {
        id
        nombre
        apellido1
        apellido2
      }
      fechaInicioPlan
      fechaFinPlan
      fechaInicioReal
      fechaFinReal
      objetivoPrincipal
    }
  }
`

export const GET_CAMPANIA = `
  query Campania($id: UUID!) {
    campanias(filter: {id: {eq: $id}}) {
      id
      nombre
      lema
      descripcionCorta
      descripcionLarga
      urlExterna
      fotoUrl
      tipoCampania {
        id
        nombre
        plantilla {
          id
          nombre
        }
      }
      estado {
        id
        nombre
        color
      }
      responsable {
        id
        nombre
        apellido1
        apellido2
        agrupacion {
          id
          nombre
        }
      }
      agrupacion {
        id
        nombre
        tipoUnidad { id nombre nivel }
      }
      fechaInicioPlan
      fechaFinPlan
      fechaInicioReal
      fechaFinReal
      objetivoPrincipal
      presupuestoEstimado
      presupuestoEjecutado
      objetivosCumplidos
      valoracion
      notificacionEnviada
      esRecurrente
      periodicidad
      metas {
        id
        tipoMeta {
          id
          nombre
          unidadMedida
        }
        valorPlanificado
        valorReal
        notas
        orden
      }
      canales {
        id
        canal {
          id
          nombre
        }
        notas
      }
      partidasPresupuesto {
        id
        concepto
        importeEstimado
        importeReal
        tipoPartida
        orden
      }
      actividades {
        id
        nombre
        descripcion
        tipoActividad { id nombre }
        estado { id nombre color }
        responsable { id nombre apellido1 apellido2 }
        fechaInicio
        fechaFin
        horaInicio
        horaFin
        lugar
        direccion
        aforo
        esOnline
        urlOnline
        presupuestoEstimado
        presupuestoEjecutado
        esRecurrente
        participaciones {
          id
          miembro { id nombre apellido1 apellido2 fotoUrl }
          nombreExterno
          emailExterno
          rol
          confirmado
          asistio
          horasAportadas
        }
        partidas {
          id
          concepto
          importeEstimado
          importeReal
          tipoPartida
          orden
        }
        registrosTrabajo {
          id
          miembro { id nombre apellido1 apellido2 }
          fecha
          horas
          descripcion
          tipo
          creadoEn
        }
        documentos {
          id
          nombre
          nombreArchivo
          ruta
          tipoMime
          tamanyo
          tipoDoc
          creadoEn
        }
        tareas {
          id
          titulo
          descripcion
          estado { id nombre color }
          prioridad
          horasEstimadas
          horasReales
          responsable { id nombre apellido1 }
          fechaLimite
          orden
        }
      }
    }
  }
`

export const GET_TIPOS_CAMPANIA = `
  query TiposCampania {
    tiposCampania {
      id
      nombre
      activo
    }
  }
`
export const CREATE_TIPO_CAMPANIA = `
  mutation CrearTipoCampania($data: TipoCampaniaCreateInput!) {
    crearTipoCampania(data: $data) { id nombre }
  }
`
export const UPDATE_TIPO_CAMPANIA = `
  mutation ActualizarTipoCampania($data: TipoCampaniaUpdateInput!) {
    actualizarTipoCampania(data: $data) { id nombre }
  }
`
export const DELETE_TIPO_CAMPANIA = `
  mutation EliminarTiposCampania($filter: TipoCampaniaFilter!) {
    eliminarTiposCampania(filter: $filter) { id }
  }
`

export const GET_ESTADOS_CAMPANIA = `
  query EstadosCampania {
    estadosCampania {
      id
      nombre
      orden
      color
      activo
    }
  }
`
export const CREATE_ESTADO_CAMPANIA = `
  mutation CrearEstadoCampania($data: EstadoCampaniaCreateInput!) {
    crearEstadoCampania(data: $data) { id nombre }
  }
`
export const UPDATE_ESTADO_CAMPANIA = `
  mutation ActualizarEstadoCampania($data: EstadoCampaniaUpdateInput!) {
    actualizarEstadoCampania(data: $data) { id nombre }
  }
`

export const GET_TIPOS_META = `
  query TiposMeta {
    tiposMetaCampania(filter: { activo: { eq: true } }) {
      id
      nombre
      descripcion
      unidadMedida
    }
  }
`
export const GET_ALL_TIPOS_META = `
  query TiposMetaTodos {
    tiposMetaCampania {
      id
      nombre
      descripcion
      unidadMedida
      activo
    }
  }
`
export const CREATE_TIPO_META = `
  mutation CrearTipoMeta($data: TipoMetaCreateInput!) {
    crearTipoMeta(data: $data) { id nombre }
  }
`
export const UPDATE_TIPO_META = `
  mutation ActualizarTipoMeta($data: TipoMetaUpdateInput!) {
    actualizarTipoMeta(data: $data) { id nombre }
  }
`
export const DELETE_TIPO_META = `
  mutation EliminarTiposMeta($filter: TipoMetaFilter!) {
    eliminarTiposMeta(filter: $filter) { id }
  }
`

export const GET_TIPOS_CANAL = `
  query TiposCanal {
    tiposCanalDifusion(filter: { activo: { eq: true } }) {
      id
      nombre
      descripcion
    }
  }
`
export const GET_ALL_TIPOS_CANAL = `
  query TiposCanalTodos {
    tiposCanalDifusion {
      id
      nombre
      descripcion
      activo
    }
  }
`
export const CREATE_TIPO_CANAL = `
  mutation CrearTipoCanalDifusion($data: TipoCanalDifusionCreateInput!) {
    crearTipoCanalDifusion(data: $data) { id nombre }
  }
`
export const UPDATE_TIPO_CANAL = `
  mutation ActualizarTipoCanalDifusion($data: TipoCanalDifusionUpdateInput!) {
    actualizarTipoCanalDifusion(data: $data) { id nombre }
  }
`
export const DELETE_TIPO_CANAL = `
  mutation EliminarTiposCanalDifusion($filter: TipoCanalDifusionFilter!) {
    eliminarTiposCanalDifusion(filter: $filter) { id }
  }
`

export const GET_PLANTILLA_POR_TIPO = `
  query PlantillaPorTipo($tipoCampaniaId: UUID!) {
    plantillasCampania(filter: { tipoCampaniaId: { eq: $tipoCampaniaId }, activo: { eq: true } }) {
      id
      nombre
      descripcion
      metas {
        id
        tipoMeta { id nombre unidadMedida }
        valorSugerido
        notas
        orden
      }
      partidas {
        id
        concepto
        importeEstimado
        tipoPartida
        orden
      }
      actividades {
        id
        nombre
        descripcion
        duracionDias
        orden
        tareas {
          id
          titulo
          horasEstimadas
          habilidad { id nombre }
          nivelHabilidad { id nombre orden }
        }
      }
    }
  }
`

export const GET_HABILIDADES = `
  query Habilidades {
    habilidades(filter: { activo: { eq: true } }) {
      id
      nombre
      categoria { id nombre }
    }
  }
`
export const GET_NIVELES_HABILIDAD = `
  query NivelesHabilidad {
    nivelesHabilidad(filter: { activo: { eq: true } }) {
      id
      nombre
      orden
    }
  }
`

export const GET_ALL_PLANTILLAS = `
  query TodasPlantillasCampania {
    plantillasCampania {
      id
      nombre
      descripcion
      activo
      tipoCampania { id nombre }
      metas { id }
      actividades { id }
    }
  }
`

export const GET_PLANTILLA = `
  query PlantillaCampania($id: UUID!) {
    plantillasCampania(filter: { id: { eq: $id } }) {
      id
      nombre
      descripcion
      activo
      tipoCampania { id nombre }
      metas {
        id
        tipoMeta { id nombre unidadMedida }
        valorSugerido
        notas
        orden
      }
      partidas {
        id
        concepto
        importeEstimado
        tipoPartida
        orden
      }
      actividades {
        id
        nombre
        descripcion
        duracionDias
        orden
        tipoActividad { id nombre }
        tareas {
          id
          titulo
          descripcion
          horasEstimadas
          orden
          habilidad { id nombre }
          nivelHabilidad { id nombre }
        }
      }
    }
  }
`

export const CREAR_PLANTILLA = `
  mutation CrearPlantilla($data: PlantillaCreateInput!) {
    crearPlantilla(data: $data) { id nombre }
  }
`
export const ACTUALIZAR_PLANTILLA = `
  mutation ActualizarPlantilla($data: PlantillaUpdateInput!) {
    actualizarPlantilla(data: $data) { id nombre }
  }
`
export const GUARDAR_METAS_PLANTILLA = `
  mutation GuardarMetasPlantilla($plantillaId: UUID!, $metas: [PlantillaMetaItemInput!]!) {
    guardarMetasPlantilla(plantillaId: $plantillaId, metas: $metas) {
      id
      metas { id tipoMeta { id nombre unidadMedida } valorSugerido notas orden }
    }
  }
`
export const GUARDAR_PARTIDAS_PLANTILLA = `
  mutation GuardarPartidasPlantilla($plantillaId: UUID!, $partidas: [PlantillaPartidaItemInput!]!) {
    guardarPartidasPlantilla(plantillaId: $plantillaId, partidas: $partidas) {
      id
      partidas { id concepto tipoPartida importeEstimado orden }
    }
  }
`
export const CREAR_PLANTILLA_ACTIVIDAD = `
  mutation CrearPlantillaActividad($data: PlantillaActividadItemInput!) {
    crearPlantillaActividad(data: $data) { id nombre orden }
  }
`
export const ACTUALIZAR_PLANTILLA_ACTIVIDAD = `
  mutation ActualizarPlantillaActividad($data: PlantillaActividadUpdateItemInput!) {
    actualizarPlantillaActividad(data: $data) { id nombre orden }
  }
`
export const CREAR_PLANTILLA_TAREA = `
  mutation CrearPlantillaTarea($data: PlantillaTareaItemInput!) {
    crearPlantillaTarea(data: $data) { id titulo orden }
  }
`
export const ACTUALIZAR_PLANTILLA_TAREA = `
  mutation ActualizarPlantillaTarea($data: PlantillaTareaUpdateItemInput!) {
    actualizarPlantillaTarea(data: $data) { id titulo orden }
  }
`

export const CREAR_CAMPANIA = `
  mutation CrearCampania($data: CampaniaCreateInput!) {
    crearCampania(data: $data) {
      id
      nombre
    }
  }
`

export const ACTUALIZAR_CAMPANIA = `
  mutation ActualizarCampania($data: CampaniaUpdateInput!) {
    actualizarCampania(data: $data) {
      id
      nombre
    }
  }
`

export const CREAR_META_CAMPANIA = `
  mutation CrearMetaCampania($data: MetaCampaniaCreateInput!) {
    crearMetaCampania(data: $data) { id }
  }
`

export const ACTUALIZAR_META_CAMPANIA = `
  mutation ActualizarMetaCampania($data: MetaCampaniaUpdateInput!) {
    actualizarMetaCampania(data: $data) { id }
  }
`

export const CREAR_CANAL_DIFUSION_CAMPANIA = `
  mutation CrearCanalDifusionCampania($data: CanalDifusionCampaniaCreateInput!) {
    crearCanalDifusionCampania(data: $data) { id }
  }
`

export const CREAR_PARTIDA_PRESUPUESTO = `
  mutation CrearPartidaPresupuesto($data: PartidaPresupuestoCampaniaCreateInput!) {
    crearPartidaPresupuestoCampania(data: $data) { id }
  }
`

export const ACTUALIZAR_PARTIDA_PRESUPUESTO = `
  mutation ActualizarPartidaPresupuesto($data: PartidaPresupuestoCampaniaUpdateInput!) {
    actualizarPartidaPresupuestoCampania(data: $data) { id }
  }
`

export const GUARDAR_METAS_CAMPANIA = `
  mutation GuardarMetasCampania($campaniaId: UUID!, $metas: [MetaInput!]!) {
    guardarMetasCampania(campaniaId: $campaniaId, metas: $metas) { id }
  }
`

export const GUARDAR_CANALES_CAMPANIA = `
  mutation GuardarCanalesCampania($campaniaId: UUID!, $canalIds: [UUID!]!) {
    guardarCanalesCampania(campaniaId: $campaniaId, canalIds: $canalIds) { id }
  }
`

export const GUARDAR_PARTIDAS_CAMPANIA = `
  mutation GuardarPartidasCampania($campaniaId: UUID!, $partidas: [PartidaInput!]!) {
    guardarPartidasCampania(campaniaId: $campaniaId, partidas: $partidas) { id }
  }
`

export const APLICAR_PLANTILLA = `
  mutation AplicarPlantilla($campaniaId: UUID!, $plantillaId: UUID!) {
    aplicarPlantilla(campaniaId: $campaniaId, plantillaId: $plantillaId) {
      id
      metas { id tipoMeta { id nombre unidadMedida } valorPlanificado }
      partidasPresupuesto { id concepto importeEstimado tipoPartida }
      actividades {
        id nombre fechaInicio horaInicio fechaFin horaFin
        tareas { id titulo orden }
      }
    }
  }
`

export const GET_MEMORIA_ANUAL = `
  query MemoriaAnual {
    campanias(filter: { eliminado: { eq: false } }) {
      id
      nombre
      lema
      tipoCampania { id nombre }
      estado { id nombre }
      responsable { id nombre apellido1 }
      fechaInicioPlan
      fechaFinPlan
      fechaInicioReal
      fechaFinReal
      objetivoPrincipal
      presupuestoEstimado
      presupuestoEjecutado
      objetivosCumplidos
      valoracion
      metas { id tipoMeta { id nombre unidadMedida } valorPlanificado valorReal }
      actividades {
        id
        nombre
        tipoActividad { id nombre }
        estado { id nombre }
        fechaInicio
        fechaFin
        presupuestoEstimado
        presupuestoEjecutado
        objetivosCumplidos
        valoracion
        asistenciaReal
        participaciones { id }
      }
      participantes { id }
    }
    actividades(filter: { eliminado: { eq: false } }) {
      id
      nombre
      tipoActividad { id nombre }
      estado { id nombre }
      campania { id }
      responsable { id nombre apellido1 }
      fechaInicio
      fechaFin
      presupuestoEstimado
      presupuestoEjecutado
      objetivosCumplidos
      valoracion
      asistenciaReal
      participaciones { id }
    }
  }
`

// Plantillas de email del módulo campañas
export const GET_PLANTILLAS_CAMPANIA = `
  query PlantillasCampania {
    plantillasEmail(filter: { modulo: { eq: "campanias" }, activo: { eq: true }, eliminado: { eq: false } }) {
      id codigo nombre descripcion
    }
  }
`

export const PREVISUALIZAR_NOTIFICACION_CAMPANIA = `
  mutation PrevisualizarNotificacionCampania($campaniaId: UUID!, $plantillaCodigo: String) {
    previsualizarNotificacionCampania(campaniaId: $campaniaId, plantillaCodigo: $plantillaCodigo) {
      asunto cuerpoHtml totalDestinatarios
    }
  }
`

export const ENVIAR_NOTIFICACION_CAMPANIA = `
  mutation EnviarNotificacionCampania($campaniaId: UUID!, $asunto: String!, $cuerpoHtml: String!) {
    enviarNotificacionCampania(campaniaId: $campaniaId, asunto: $asunto, cuerpoHtml: $cuerpoHtml) {
      enviados fallidos sinEmail total simulado mensaje
    }
  }
`

export const GUARDAR_PARTIDAS_ACTIVIDAD = `
  mutation GuardarPartidasActividad($actividadId: UUID!, $partidas: [PartidaPresupuestoActividadCreateInput!]!) {
    eliminarPartidasPresupuestoActividad(filter: { actividadId: { eq: $actividadId } }) { id }
    crearPartidaPresupuestoActividad(data: $partidas) { id concepto importeEstimado importeReal tipoPartida orden }
  }
`

export const CREAR_REGISTRO_TRABAJO = `
  mutation CrearRegistroTrabajo($data: RegistroTrabajoActividadCreateInput!) {
    crearRegistroTrabajoActividad(data: $data) {
      id miembro { id nombre apellido1 apellido2 } fecha horas descripcion tipo creadoEn
    }
  }
`

export const ACTUALIZAR_REGISTRO_TRABAJO = `
  mutation ActualizarRegistroTrabajo($data: RegistroTrabajoActividadUpdateInput!) {
    actualizarRegistroTrabajoActividad(data: $data) { id fecha horas descripcion tipo }
  }
`

export const ELIMINAR_REGISTROS_TRABAJO = `
  mutation EliminarRegistrosTrabajo($filter: RegistroTrabajoActividadFilter!) {
    eliminarRegistrosTrabajoActividad(filter: $filter) { id }
  }
`

export const ELIMINAR_DOCUMENTO_ACTIVIDAD = `
  mutation EliminarDocumentoActividad($filter: DocumentoActividadFilter!) {
    eliminarDocumentosActividad(filter: $filter) { id }
  }
`

export const ELIMINAR_DOCUMENTO_PARTIDA = `
  mutation EliminarDocumentoPartida($filter: DocumentoPartidaFilter!) {
    eliminarDocumentosPartida(filter: $filter) { id }
  }
`

export const CLONAR_CAMPANIA = `
  mutation ClonarCampania($data: ClonarCampaniaInput!) {
    clonarCampania(data: $data) {
      id nombre estado { id nombre color }
    }
  }
`

export const PROPAGAR_A_SUBCAMPANIAS = `
  mutation PropagarASubcampanias($data: PropagarACampaniasInput!) {
    propagarASubcampanias(data: $data) {
      id nombre
    }
  }
`

export const CERRAR_CAMPANIA = `
  mutation CerrarCampania(
    $id: UUID!
    $estadoId: UUID!
    $presupuestoEjecutado: Decimal!
    $resultadosMetas: [ResultadoMetaInput!]!
    $resultadosPartidas: [ResultadoPartidaInput!]!
    $valoracion: String
  ) {
    cerrarCampania(
      id: $id
      estadoId: $estadoId
      presupuestoEjecutado: $presupuestoEjecutado
      resultadosMetas: $resultadosMetas
      resultadosPartidas: $resultadosPartidas
      valoracion: $valoracion
    ) {
      id
      estado { id nombre }
      presupuestoEjecutado
      valoracion
      metas { id valorReal }
      partidasPresupuesto { id importeReal }
    }
  }
`

// Nº de firmas verificadas (doble opt-in) de una campaña de recogida de firmas.
// Alimenta el panel "Recogida de firmas" del detalle de campaña.
export const FIRMAS_VERIFICADAS_CAMPANIA = `
  query FirmasVerificadasCampania($campaniaId: UUID!) {
    firmasVerificadasCampania(campaniaId: $campaniaId)
  }
`
