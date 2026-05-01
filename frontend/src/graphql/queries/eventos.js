// Queries GraphQL para el módulo de eventos
// IMPORTANTE: Strawberry usa camelCase automáticamente

export const GET_TIPOS_EVENTO = `
  query TiposEvento {
    tiposEvento {
      id
      nombre
      descripcion
      requiereInscripcion
      requiereAforo
      activo
    }
  }
`

export const GET_ESTADOS_EVENTO = `
  query EstadosEvento {
    estadosEvento {
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

export const GET_EVENTOS = `
  query Eventos {
    eventos {
      id
      nombre
      descripcionCorta
      fechaInicio
      fechaFin
      horaInicio
      horaFin
      esTodoDia
      lugar
      ciudad
      esOnline
      urlOnline
      aforoMaximo
      requiereInscripcion
      fechaLimiteInscripcion
      tipoEvento {
        id
        nombre
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
      grupoOrganizador {
        id
        nombre
      }
      campania {
        id
        nombre
      }
      agrupacion {
        id
        nombre
      }
      participantes {
        id
      }
      materiales {
        id
        tipo
        nombre
        url
      }
      fechaCreacion
    }
  }
`

export const GET_EVENTO_BY_ID = `
  query Evento($id: UUID!) {
    eventos(filter: { id: { eq: $id } }) {
      id
      nombre
      descripcionCorta
      descripcionLarga
      fechaInicio
      fechaFin
      horaInicio
      horaFin
      esTodoDia
      lugar
      direccion
      ciudad
      esOnline
      urlOnline
      aforoMaximo
      requiereInscripcion
      fechaLimiteInscripcion
      observaciones
      tipoEvento {
        id
        nombre
        requiereInscripcion
        requiereAforo
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
      grupoOrganizador {
        id
        nombre
      }
      campania {
        id
        nombre
      }
      agrupacion {
        id
        nombre
      }
      participantes {
        id
        rol
        confirmado
        asistio
        fechaInscripcion
        miembro {
          id
          nombre
          apellido1
          email
        }
      }
      materiales {
        id
        tipo
        nombre
        descripcion
        url
        fechaSubida
      }
    }
  }
`

export const CREAR_EVENTO = `
  mutation CrearEvento($data: EventoCreateInput!) {
    crearEvento(data: $data) {
      id
      nombre
    }
  }
`

export const ACTUALIZAR_EVENTO = `
  mutation ActualizarEvento($data: EventoUpdateInput!) {
    actualizarEvento(data: $data) {
      id
      nombre
    }
  }
`

export const INSCRIBIR_PARTICIPANTE = `
  mutation InscribirParticipante($data: ParticipanteEventoCreateInput!) {
    crearParticipanteEvento(data: $data) {
      id
      rol
      confirmado
    }
  }
`
