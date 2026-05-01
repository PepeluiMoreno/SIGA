// Queries GraphQL para el módulo de grupos de trabajo
// IMPORTANTE: Strawberry usa camelCase automáticamente
// NO usar campos 'codigo' - solo se identifican por UUID

// Query para obtener grupos de trabajo
export const GET_GRUPOS = `
  query GruposTrabajo {
    gruposTrabajo {
      id
      nombre
      descripcion
      tipo {
        id
        nombre
      }
      activo
      fechaCreacion
      coordinador {
        id
        nombre
        apellido1
      }
      miembros {
        id
      }
    }
  }
`

// Query para obtener un grupo por ID
export const GET_GRUPO_BY_ID = `
  query GrupoTrabajo($id: UUID!) {
    gruposTrabajo(filter: {id: {eq: $id}}) {
      id
      nombre
      descripcion
      tipo {
        id
        nombre
      }
      activo
      fechaCreacion
      coordinador {
        id
        nombre
        apellido1
        email
      }
      miembros {
        id
        miembro {
          id
          nombre
          apellido1
          email
        }
        rol {
          id
          nombre
        }
      }
      reuniones {
        id
        fecha
        lugar
        acta
      }
    }
  }
`

// Query para tipos de grupo
export const GET_TIPOS_GRUPO = `
  query TiposGrupo {
    tiposGrupo {
      id
      nombre
      descripcion
      activo
    }
  }
`

// Query para roles de grupo
export const GET_ROLES_GRUPO = `
  query RolesGrupo {
    rolesGrupo {
      id
      nombre
      descripcion
      activo
    }
  }
`
