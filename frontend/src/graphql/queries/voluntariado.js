// Queries GraphQL para el módulo de voluntariado
// IMPORTANTE: Strawberry usa camelCase automáticamente
// NO usar campos 'codigo' - solo se identifican por UUID

// Query para obtener voluntarios — con scoping de ámbito territorial en backend
// (resolver voluntariosEnAmbito: solo los voluntarios del ámbito del usuario).
export const GET_VOLUNTARIOS = `
  query Voluntarios {
    voluntariosEnAmbito {
      id
      nombre
      apellido1
      apellido2
      email
      telefono
      disponibilidad
      horasDisponiblesSemana
      profesion
      nivelEstudiosId
      intereses
      puedeConducir
      vehiculoPropio
      disponibilidadViajar
      activo
      fechaAlta
    }
  }
`

// Query para obtener un voluntario por ID
export const GET_VOLUNTARIO_BY_ID = `
  query Voluntario($id: UUID!) {
    miembros: socios(contactoId: $id) {
      id
      nombre
      apellido1
      apellido2
      email
      telefono
      disponibilidad
      horasDisponiblesSemana
      profesion
      nivelEstudiosId
      nivelEstudiosRel { id nombre }
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

// ── Gestión por delegación (con scoping de ámbito en backend) ───────────────

// Catálogo de habilidades y niveles (para el editor)
export const GET_CATALOGO_HABILIDADES = `
  query CatalogoHabilidades {
    habilidades(filter: { activo: { eq: true } }) { id nombre }
    nivelesHabilidad(filter: { activo: { eq: true } }) { id nombre orden }
  }
`

// Habilidades actuales de un socio
export const GET_HABILIDADES_MIEMBRO = `
  query HabilidadesMiembro($id: UUID!) {
    miembrosHabilidades(filter: { miembroId: { eq: $id } }) {
      id
      habilidadId
      nivelId
    }
  }
`

// Editar el perfil de voluntario (disponibilidad/profesión/intereses…) por delegación
export const GESTIONAR_PERFIL_VOLUNTARIO = `
  mutation GestionarPerfilVoluntario($data: PerfilVoluntarioInput!) {
    gestionarPerfilVoluntario(data: $data) { id }
  }
`

// Asignar / quitar habilidad de un socio por delegación
export const ASIGNAR_HABILIDAD_VOLUNTARIO = `
  mutation AsignarHabilidadVoluntario($miembroId: UUID!, $habilidadId: UUID!, $nivelId: UUID) {
    asignarHabilidadVoluntario(miembroId: $miembroId, habilidadId: $habilidadId, nivelId: $nivelId)
  }
`

export const QUITAR_HABILIDAD_VOLUNTARIO = `
  mutation QuitarHabilidadVoluntario($miembroId: UUID!, $habilidadId: UUID!) {
    quitarHabilidadVoluntario(miembroId: $miembroId, habilidadId: $habilidadId)
  }
`
