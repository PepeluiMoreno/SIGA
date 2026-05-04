// Queries GraphQL para el módulo financiero
// IMPORTANTE: Strawberry usa camelCase automáticamente
// NO usar campos 'codigo' - solo se identifican por UUID
// Strawchemy no usa limit/offset, usa filtros automáticos generados

// Query para obtener cuotas anuales
export const GET_CUOTAS_ANUALES = `
  query CuotasAnuales {
    cuotasAnuales {
      id
      ejercicio
      importe
      importePagado
      fechaPago
      modoIngreso
      miembro {
        id
        nombre
        apellido1
        apellido2
      }
      estado {
        id
        nombre
        color
      }
      agrupacion {
        id
        nombre
      }
      fechaCreacion
    }
  }
`

// Query para obtener cuotas por miembro
export const GET_CUOTAS_BY_MIEMBRO = `
  query CuotasByMiembro($miembroId: UUID!) {
    cuotasAnuales(filter: {miembroId: {eq: $miembroId}}) {
      id
      ejercicio
      importe
      importePagado
      fechaPago
      modoIngreso
      estado {
        id
        nombre
        color
      }
    }
  }
`

// Query para obtener donaciones
export const GET_DONACIONES = `
  query Donaciones {
    donaciones {
      id
      fecha
      importe
      gastos
      donanteNombre
      donanteDni
      concepto {
        id
        nombre
      }
      estado {
        id
        nombre
      }
      campania {
        id
        nombre
      }
      certificadoEmitido
      anonima
      observaciones
      fechaCreacion
    }
  }
`

// Query para obtener conceptos de donación
export const GET_DONACION_CONCEPTOS = `
  query DonacionConceptos {
    donacionConceptos {
      id
      nombre
      descripcion
      activo
    }
  }
`

// Query para obtener remesas
export const GET_REMESAS = `
  query Remesas {
    remesas {
      id
      referencia
      fechaCreacion
      fechaEnvio
      fechaCobro
      importeTotal
      gastos
      numOrdenes
      estado {
        id
        nombre
      }
      archivoSepa
      observaciones
    }
  }
`

// Query para obtener órdenes de cobro
export const GET_ORDENES_COBRO = `
  query OrdenesCobro {
    ordenesCobro {
      id
      importe
      fechaProcesamiento
      remesa {
        id
        referencia
      }
      cuota {
        id
        ejercicio
        miembro {
          id
          nombre
          apellido1
        }
      }
      estado {
        id
        nombre
      }
    }
  }
`

// Query para importes de cuota por año
export const GET_IMPORTES_CUOTA = `
  query ImportesCuotaAnio {
    importesCuotaAnio {
      id
      ejercicio
      importe
      nombreCuota
      observaciones
      tipoMiembro {
        id
        nombre
      }
      activo
    }
  }
`

// Query para estados financieros (catálogos)
export const GET_ESTADOS_CUOTA = `
  query EstadosCuota {
    estadosCuota {
      id
      nombre
      descripcion
      color
      orden
      activo
    }
  }
`

export const GET_ESTADOS_DONACION = `
  query EstadosDonacion {
    estadosDonacion {
      id
      nombre
      descripcion
      activo
    }
  }
`

export const GET_ESTADOS_REMESA = `
  query EstadosRemesa {
    estadosRemesa {
      id
      nombre
      descripcion
      activo
    }
  }
`

export const GET_ESTADOS_ORDEN_COBRO = `
  query EstadosOrdenCobro {
    estadosOrdenCobro {
      id
      nombre
      descripcion
      activo
    }
  }
`
