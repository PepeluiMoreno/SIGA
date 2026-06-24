// Queries GraphQL para el dashboard
// IMPORTANTE: Strawberry usa camelCase automáticamente
// Estas queries dependen de las queries reales disponibles en el backend

// Query básica para obtener estadísticas usando queries existentes
export const GET_DASHBOARD_MIEMBROS = `
  query DashboardMiembros {
    miembros: socios {
      id
      activo
      esVoluntario
      fechaAlta
      tipoMiembro {
        id
        nombre
      }
      estado {
        id
        nombre
      }
    }
  }
`

export const GET_DASHBOARD_CAMPANIAS = `
  query DashboardCampanias {
    campanias {
      id
      nombre
      estado {
        id
        nombre
      }
      fechaInicioPlan
      fechaFinPlan
    }
  }
`

export const GET_DASHBOARD_GRUPOS = `
  query DashboardGrupos {
    gruposTrabajo {
      id
      nombre
      activo
      tipo {
        id
        nombre
      }
    }
  }
`

// Query para test de conexión
export const TEST_CONNECTION = `
  query TestConnection {
    tiposMiembro {
      id
      nombre
    }
  }
`
