// Queries GraphQL para el módulo de miembros
// IMPORTANTE: Strawberry convierte nombres a camelCase automáticamente
// NO usar campos 'codigo' - solo se identifican por UUID
// Strawchemy no usa limit/offset, usa filtros automáticos generados

// Query para obtener miembros
export const GET_MIEMBROS = `
  query Miembros {
    miembros {
      id
      nombre
      apellido1
      apellido2
      sexo
      email
      telefono
      telefono2
      fechaNacimiento
      tipoMiembro {
        id
        nombre
        requiereCuota
      }
      estado {
        id
        nombre
        color
      }
      motivoBajaRel {
        id
        nombre
      }
      agrupacion {
        id
        nombre
        tipo
      }
      fechaAlta
      fechaBaja
      activo
      esVoluntario
      datosAnonimizados
    }
  }
`

// Query para obtener un miembro por ID
export const GET_MIEMBRO_BY_ID = `
  query Miembro($id: UUID!) {
    miembros(filter: {id: {eq: $id}}) {
      id
      tipoMiembroId
      estadoId
      motivoBajaId
      agrupacionId
      cargoId
      paisDocumentoId
      paisDomicilioId
      provinciaId
      nombre
      apellido1
      apellido2
      sexo
      fechaNacimiento
      email
      telefono
      telefono2
      tipoDocumento
      numeroDocumento
      tipoMiembro {
        id
        nombre
        requiereCuota
        puedeVotar
      }
      estado {
        id
        nombre
        color
      }
      motivoBajaRel {
        id
        nombre
      }
      motivoBajaTexto
      agrupacion {
        id
        nombre
        tipo
      }
      fechaAlta
      fechaBaja
      direccion
      codigoPostal
      localidad
      provincia {
        id
        nombre
      }
      paisDomicilio {
        id
        nombre
      }
      paisDocumento {
        id
        nombre
      }
      cargo {
        id
        nombre
      }
      iban
      esVoluntario
      disponibilidad
      horasDisponiblesSemana
      profesion
      nivelEstudios
      intereses
      observaciones
      solicitaSupresionDatos
      fechaSolicitudSupresion
      fechaLimiteRetencion
      datosAnonimizados
      fechaAnonimizacion
      activo
      fechaCreacion
      fechaModificacion
    }
  }
`

export const UPDATE_MIEMBRO = `
  mutation ActualizarMiembro($data: MiembroUpdateInput!) {
    actualizarMiembro(data: $data) {
      id
      nombre
      apellido1
      apellido2
    }
  }
`

// Query para obtener tipos de miembro
// TODO: Añadir 'orden' tras ejecutar migración Alembic
export const GET_TIPOS_MIEMBRO = `
  query TiposMiembro {
    tiposMiembro {
      id
      nombre
      descripcion
      requiereCuota
      puedeVotar
      activo
    }
  }
`

// Query para obtener estados de miembro
export const GET_ESTADOS_MIEMBRO = `
  query EstadosMiembro {
    estadosMiembro {
      id
      nombre
      descripcion
      color
      orden
      activo
    }
  }
`

// Query para obtener motivos de baja
export const GET_MOTIVOS_BAJA = `
  query MotivosBaja {
    motivosBaja {
      id
      nombre
      descripcion
      requiereDocumentacion
      activo
    }
  }
`

export const GET_TIPOS_CARGO = `
  query TiposCargo {
    tiposCargo {
      id
      codigo
      nombre
      activo
    }
  }
`

// Query para obtener agrupaciones territoriales
export const GET_AGRUPACIONES = `
  query Agrupaciones {
    agrupacionesTerritoriales {
      id
      nombre
      nombreCorto
      tipo
      nivel
      telefono
      email
      web
      activo
      agrupacionPadreId
    }
  }
`

// Query para contar miembros (estadísticas básicas)
export const GET_MIEMBROS_COUNT = `
  query MiembrosCount {
    miembros {
      id
    }
  }
`
