// Queries GraphQL para el módulo de grupos de trabajo
// Strawberry/strawchemy usa camelCase automáticamente desde snake_case del modelo

export const GET_GRUPOS = `
  query GruposTrabajo {
    gruposTrabajo {
      id
      nombre
      descripcion
      tipoGrupo {
        id
        nombre
      }
      coordinador {
        id
        nombre
        apellido1
      }
      agrupacion {
        id
        nombre
      }
      activo
      fechaCreacion
    }
  }
`

export const GET_GRUPO_BY_ID = `
  query GrupoTrabajo($id: UUID!) {
    gruposTrabajo(filter: {id: {eq: $id}}) {
      id
      nombre
      descripcion
      tipoGrupo {
        id
        nombre
        descripcion
        esPermanente
      }
      coordinador {
        id
        nombre
        apellido1
        email
      }
      agrupacion {
        id
        nombre
      }
      fechaInicio
      fechaFin
      objetivo
      presupuestoAsignado
      presupuestoEjecutado
      activo
      fechaCreacion
      miembros {
        id
        miembroId
        rolGrupo {
          id
          nombre
          esCoordinador
        }
        activo
        fechaIncorporacion
      }
      reuniones {
        id
        fecha
        lugar
        acta
        realizada
      }
    }
  }
`

export const GET_TIPOS_GRUPO = `
  query TiposGrupo {
    tiposGrupo {
      id
      nombre
      descripcion
      esPermanente
      activo
    }
  }
`

export const GET_ROLES_GRUPO = `
  query RolesGrupo {
    rolesGrupo {
      id
      nombre
      descripcion
      esCoordinador
      puedeEditar
      puedeAprobarGastos
      activo
    }
  }
`
