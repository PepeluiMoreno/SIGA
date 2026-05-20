// Queries GraphQL del módulo de Presidencia
// Agrega datos de secretaría, membresía y económico

// ── ACUERDOS PENDIENTES (de secretaría) ──────────────────────────────────────

export const GET_ACUERDOS_PENDIENTES_PRES = `
  query AcuerdosPendientesPresidencia {
    acuerdosPendientes {
      id
      numero
      descripcion
      estadoEjecucionCodigo
      responsableId
      fechaLimiteEjecucion
    }
  }
`

// ── ACTAS PENDIENTES DE APROBACIÓN ───────────────────────────────────────────

export const GET_ACTAS_PENDIENTES_PRES = `
  query ActasPendientesPresidencia {
    actasPendientesAprobacion {
      id
      numero
      anio
      estadoCodigo
    }
  }
`

// ── PRÓXIMAS REUNIONES ───────────────────────────────────────────────────────

export const GET_PROXIMAS_REUNIONES = `
  query ProximasReuniones($anio: Int) {
    reuniones(anio: $anio, estadoCodigo: "CONVOCADA") {
      id
      tipoReunionId
      numeroConvocatoria
      anio
      fechaConvocatoria
      fechaCelebracion
      lugar
      esTelematica
    }
  }
`

// ── CONVENIOS PRÓXIMOS A VENCER ───────────────────────────────────────────────

export const GET_CONVENIOS_VENCER = `
  query ConveniosProximosAVencer {
    convenios(estado: "VIGENTE", proximosAVencerDias: 60) {
      id
      referencia
      titulo
      entidadContraparte
      fechaFin
      renovacionAutomatica
    }
  }
`

// ── MANDATOS VIGENTES (de membresía) ─────────────────────────────────────────

export const GET_MANDATOS_VIGENTES = `
  query MandatosVigentes {
    historialNombramientos(filter: {
      eliminado: { eq: false },
      estado: { eq: "ACTIVO" }
    }) {
      id
      miembro {
        id
        nombre
        apellido1
      }
      cargo {
        id
        nombre
      }
      agrupacion {
        id
        nombre
      }
      fechaInicio
      fechaFin
    }
  }
`

// ── SOCIOS ACTIVOS (para KPI) ─────────────────────────────────────────────────

export const GET_KPI_SOCIOS = `
  query KpiSocios {
    miembros(filter: { eliminado: { eq: false } }) {
      id
      activo
      fechaAlta
    }
  }
`

// ── ÚLTIMO SNAPSHOT LIBRO SOCIOS ─────────────────────────────────────────────

export const GET_ULTIMO_LIBRO_SOCIOS = `
  query UltimoLibroSocios {
    libroSociosSnapshots {
      id
      fechaCorte
      totalSociosActivos
      totalSociosBaja
      totalSociosHistorico
    }
  }
`
