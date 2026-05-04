// Queries GraphQL para el módulo de voluntariado
// IMPORTANTE: Strawberry usa camelCase automáticamente
// NO usar campos 'codigo' - solo se identifican por UUID

// Query para obtener miembros voluntarios
export const GET_VOLUNTARIOS = `
  query Voluntarios {
    miembros(filter: {esVoluntario: {eq: true}}) {
      id
      nombre
      apellido1
      apellido2
      email
      telefono
      disponibilidad
      horasDisponiblesSemana
      profesion
      nivelEstudios
      intereses
      activo
      fechaAlta
    }
  }
`

// Query para obtener un voluntario por ID
export const GET_VOLUNTARIO_BY_ID = `
  query Voluntario($id: UUID!) {
    miembros(filter: {id: {eq: $id}}) {
      id
      nombre
      apellido1
      apellido2
      email
      telefono
      disponibilidad
      horasDisponiblesSemana
      profesion
      nivelEstudios
      intereses
      experienciaVoluntariado
      observacionesVoluntariado
      puedeConducir
      vehiculoPropio
      disponibilidadViajar
      activo
      fechaAlta
    }
  }
`

// Query para categorías de competencia
export const GET_CATEGORIAS_COMPETENCIA = `
  query CategoriasCompetencia {
    categoriasCompetencia {
      id
      nombre
      descripcion
      activo
    }
  }
`

// Query para competencias
export const GET_COMPETENCIAS = `
  query Competencias {
    competencias {
      id
      nombre
      descripcion
      categoria {
        id
        nombre
      }
      activo
    }
  }
`

// Query para niveles de competencia
export const GET_NIVELES_COMPETENCIA = `
  query NivelesCompetencia {
    nivelesCompetencia {
      id
      nombre
      descripcion
      valor
      activo
    }
  }
`

// Query para tipos de documento voluntario
export const GET_TIPOS_DOCUMENTO_VOLUNTARIO = `
  query TiposDocumentoVoluntario {
    tiposDocumentoVoluntario {
      id
      nombre
      descripcion
      requiereValidacion
      activo
    }
  }
`

// Query para tipos de formación
export const GET_TIPOS_FORMACION = `
  query TiposFormacion {
    tiposFormacion {
      id
      nombre
      descripcion
      activo
    }
  }
`
