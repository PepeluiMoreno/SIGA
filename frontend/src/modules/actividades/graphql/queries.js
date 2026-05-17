// Queries GraphQL para el módulo de Actividades

export const GET_TIPOS_ACCION = `
  query TiposActividad {
    tiposActividad {
      id
      nombre
      descripcion
      tieneLugar
      tieneParticipantes
      activo
    }
  }
`

export const GET_ESTADOS_ACCION = `
  query EstadosAccion {
    estadosAccion {
      id
      nombre
      descripcion
      orden
      color
      esFinal
      activo
    }
  }
`

export const GET_ACCIONES = `
  query Actividades {
    actividades(filter: { eliminado: { eq: false } }) {
      id
      nombre
      descripcion
      fechaInicio
      fechaFin
      horaInicio
      horaFin
      lugar
      esOnline
      urlOnline
      aforo
      tipoActividad {
        id
        nombre
        tieneLugar
        tieneParticipantes
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
      }
      campania {
        id
        nombre
      }
      fechaCreacion
    }
  }
`

export const GET_ACCION_BY_ID = `
  query Actividad($id: UUID!) {
    actividades(filter: { id: { eq: $id } }) {
      id
      nombre
      descripcion
      fechaInicio
      fechaFin
      horaInicio
      horaFin
      lugar
      direccion
      localidad
      provincia
      duracionHoras
      duracionDias
      aforo
      esOnline
      urlOnline
      presupuestoEstimado
      presupuestoEjecutado
      valoracion
      objetivosCumplidos
      asistenciaReal
      notasAprobacion
      aprobadoPorId
      fechaAprobacion
      tipoActividad {
        id
        nombre
        tieneLugar
        tieneParticipantes
      }
      estado {
        id
        nombre
      }
      responsable {
        id
        nombre
        apellido1
        email
      }
      campania {
        id
        nombre
      }
      tareas {
        id
        titulo
        descripcion
        prioridad
        orden
        fechaLimite
        horasEstimadas
        horasReales
        estado { id nombre }
        responsable { id nombre apellido1 }
        habilidad { id nombre }
        nivelHabilidad { id nombre orden }
      }
      participaciones {
        id
        rol
        confirmado
        asistio
        horasAportadas
        miembro {
          id
          nombre
          apellido1
          email
          fotoUrl
        }
        nombreExterno
        emailExterno
      }
    }
  }
`

export const CREAR_ACCION = `
  mutation CrearActividad($data: ActividadCreateData!) {
    crearActividad(data: $data) {
      id
      nombre
    }
  }
`

export const ACTUALIZAR_ACCION = `
  mutation ActualizarActividad($data: ActividadUpdateData!) {
    actualizarActividad(data: $data) {
      id
      nombre
    }
  }
`

export const REGISTRAR_PARTICIPACION = `
  mutation RegistrarParticipacion($data: ParticipacionCreateData!) {
    crearParticipacion(data: $data) {
      id
      rol
      confirmado
    }
  }
`

export const ACTUALIZAR_PARTICIPACION = `
  mutation ActualizarParticipacion($data: ParticipacionUpdateInput!) {
    actualizarParticipacion(data: $data) {
      id rol confirmado asistio horasAportadas
    }
  }
`

export const ELIMINAR_PARTICIPACION = `
  mutation EliminarParticipacion($id: UUID!) {
    eliminarParticipaciones(filter: { id: { eq: $id } }) { id }
  }
`

export const ACTUALIZAR_TAREA = `
  mutation ActualizarTarea($data: TareaUpdateData!) {
    actualizarTarea(data: $data) {
      id titulo descripcion prioridad fechaLimite horasEstimadas horasReales
      estado { id nombre }
      responsable { id nombre apellido1 }
      habilidad { id nombre }
      nivelHabilidad { id nombre }
    }
  }
`

export const ELIMINAR_TAREA = `
  mutation EliminarTarea($id: UUID!) {
    eliminarTareas(filter: { id: { eq: $id } }) { id }
  }
`

export const SOFT_DELETE_ACCION = `
  mutation SoftDeleteActividad($id: UUID!) {
    actualizarActividad(data: { id: $id, eliminado: true }) { id }
  }
`

export const ELIMINAR_ACCION = `
  mutation EliminarActividad($id: UUID!) {
    eliminarActividades(filter: { id: { eq: $id } }) { id }
  }
`

export const CREAR_TAREA = `
  mutation CrearTarea($data: TareaCreateData!) {
    crearTarea(data: $data) {
      id titulo
    }
  }
`

export const TRANSICIONAR_ACTIVIDAD = `
  mutation TransicionarActividad($id: UUID!, $estadoId: UUID!, $notas: String) {
    transicionarActividad(id: $id, estadoId: $estadoId, notas: $notas) {
      id estado { id nombre } aprobadoPorId fechaAprobacion notasAprobacion
    }
  }
`

export const APROBAR_ACTIVIDAD = `
  mutation AprobarActividad($id: UUID!, $estadoId: UUID!, $notas: String) {
    aprobarActividad(id: $id, estadoId: $estadoId, notas: $notas) {
      id estado { id nombre } aprobadoPorId fechaAprobacion notasAprobacion
    }
  }
`

export const CERRAR_ACTIVIDAD = `
  mutation CerrarActividad($id: UUID!, $estadoId: UUID!, $valoracion: String, $objetivosCumplidos: Boolean, $asistenciaReal: Int, $presupuestoEjecutado: Decimal) {
    cerrarActividad(id: $id, estadoId: $estadoId, valoracion: $valoracion, objetivosCumplidos: $objetivosCumplidos, asistenciaReal: $asistenciaReal, presupuestoEjecutado: $presupuestoEjecutado) {
      id estado { id nombre } valoracion objetivosCumplidos asistenciaReal presupuestoEjecutado
    }
  }
`

export const TRANSICIONAR_CAMPANIA = `
  mutation TransicionarCampania($id: UUID!, $estadoId: UUID!, $notas: String) {
    transicionarCampania(id: $id, estadoId: $estadoId, notas: $notas) {
      id estado { id nombre }
    }
  }
`

export const APROBAR_CAMPANIA = `
  mutation AprobarCampania($id: UUID!, $estadoId: UUID!, $notas: String) {
    aprobarCampania(id: $id, estadoId: $estadoId, notas: $notas) {
      id estado { id nombre } aprobadoPorId fechaAprobacion
    }
  }
`

export const CERRAR_CAMPANIA = `
  mutation CerrarCampania($id: UUID!, $estadoId: UUID!, $valoracion: String, $objetivosCumplidos: Boolean, $presupuestoEjecutado: Decimal) {
    cerrarCampania(id: $id, estadoId: $estadoId, valoracion: $valoracion, objetivosCumplidos: $objetivosCumplidos, presupuestoEjecutado: $presupuestoEjecutado) {
      id estado { id nombre } valoracion objetivosCumplidos
    }
  }
`
