// Queries GraphQL para el módulo de Acciones

export const GET_TIPOS_ACCION = `
  query TiposAccion {
    tiposAccion {
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
  query Acciones {
    acciones(filter: { eliminado: { eq: false } }) {
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
      tipoAccion {
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
      iniciativa {
        id
        nombre
      }
      fechaCreacion
    }
  }
`

export const GET_ACCION_BY_ID = `
  query Accion($id: UUID!) {
    acciones(filter: { id: { eq: $id } }) {
      id
      nombre
      descripcion
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
      tipoAccion {
        id
        nombre
        tieneLugar
        tieneParticipantes
      }
      estado {
        id
        nombre
        color
        esFinal
      }
      responsable {
        id
        nombre
        apellido1
        email
      }
      iniciativa {
        id
        nombre
      }
      tareas {
        id
        titulo
        descripcion
        prioridad
        fechaLimite
        horasEstimadas
        horasReales
        estado { id nombre }
        responsable { id nombre apellido1 }
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
  mutation CrearAccion($data: AccionCreateData!) {
    crearAccion(data: $data) {
      id
      nombre
    }
  }
`

export const ACTUALIZAR_ACCION = `
  mutation ActualizarAccion($data: AccionUpdateData!) {
    actualizarAccion(data: $data) {
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
    }
  }
`

export const ELIMINAR_TAREA = `
  mutation EliminarTarea($id: UUID!) {
    eliminarTareas(filter: { id: { eq: $id } }) { id }
  }
`

export const SOFT_DELETE_ACCION = `
  mutation SoftDeleteAccion($id: UUID!) {
    actualizarAccion(data: { id: $id, eliminado: true }) { id }
  }
`

export const ELIMINAR_ACCION = `
  mutation EliminarAccion($id: UUID!) {
    eliminarAcciones(filter: { id: { eq: $id } }) { id }
  }
`

export const CREAR_TAREA = `
  mutation CrearTarea($data: TareaCreateData!) {
    crearTarea(data: $data) {
      id titulo
    }
  }
`
