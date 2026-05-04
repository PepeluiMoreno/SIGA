// Queries GraphQL para el módulo de campañas
// IMPORTANTE: Strawberry usa camelCase automáticamente
// NO usar campos 'codigo' - solo se identifican por UUID

// Query para obtener campañas
export const GET_CAMPANIAS = `
  query Campanias {
    campanias {
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
      metaRecaudacion
      metaParticipantes
      metaFirmas
    }
  }
`

// Query para obtener una campaña por ID
export const GET_CAMPANIA = `
  query Campania($id: UUID!) {
    campanias(filter: {id: {eq: $id}}) {
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
        agrupacion {
          id
          nombre
        }
      }
      agrupacion {
        id
        nombre
      }
      fechaInicioPlan
      fechaFinPlan
      fechaInicioReal
      fechaFinReal
      objetivoPrincipal
      metaRecaudacion
      metaParticipantes
      metaFirmas
    }
  }
`

// Query para obtener tipos de campaña
export const GET_TIPOS_CAMPANIA = `
  query TiposCampania {
    tiposCampania {
      id
      nombre
      activo
    }
  }
`

// Query para obtener estados de campaña
export const GET_ESTADOS_CAMPANIA = `
  query EstadosCampania {
    estadosCampania {
      id
      nombre
      orden
      activo
    }
  }
`

export const GET_SKILLS = `
  query Skills {
    skills {
      id
      nombre
      categoria
      activo
    }
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
