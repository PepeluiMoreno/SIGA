// Queries GraphQL para el módulo de miembros
// IMPORTANTE: Strawberry convierte nombres a camelCase automáticamente
// NO usar campos 'codigo' - solo se identifican por UUID
// Strawchemy no usa limit/offset, usa filtros automáticos generados

// Query para obtener miembros
export const GET_MIEMBROS = `
  query Miembros {
    miembros(filter: { eliminado: { eq: false } }) {
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
      usuario {
        id
        email
        activo
        ultimoAcceso
        tipoVinculacion { id nombre }
        roles {
          id
          activo
          agrupacionId
          rol {
            id
            nombre
            tipo
          }
        }
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
        tipoUnidad { id nombre naturaleza vinculo }
      }
      fechaAlta
      fechaBaja
      activo
      esSocioHonor
      esVoluntario
      datosAnonimizados
      tieneAcceso
    }
  }
`

// Nombramientos activos (coordinadores, presidentes...) — para badges en lista
export const GET_NOMBRAMIENTOS_ACTIVOS = `
  query NombramientosActivos {
    historialNombramientos(filter: { estado: { eq: "ACTIVO" }, eliminado: { eq: false } }) {
      id miembroId
      rol { nombre codigo }
      agrupacion { id nombre }
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
      paisDocumentoId
      paisDomicilioId
      paisNacimientoId
      provinciaId
      formaPagoId
      nombre
      apellido1
      apellido2
      sexo
      fechaNacimiento
      tipoDocumento
      numeroDocumento
      email
      telefono
      telefono2
      direccion
      localidad
      codigoPostal
      iban
      swiftBic
      referenciaPago
      esSocioHonor
      esVoluntario
      activo
      fechaAlta
      fechaBaja
      motivoBajaTexto
      observaciones
      solicitaSupresionDatos
      datosAnonimizados
      fechaSolicitudSupresion
      fechaLimiteRetencion
      fechaAnonimizacion
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
      fotoUrl
      fechaCreacion
      fechaModificacion
      tipoMiembro { id nombre }
      estado { id nombre color }
      agrupacion { id nombre }
      motivoBajaRel { id nombre }
      usuario {
        id
        email
        activo
        ultimoAcceso
        roles {
          id
          activo
          agrupacionId
          rol { id nombre tipo descripcion }
        }
      }
    }
  }
`

export const CREATE_MIEMBRO = `
  mutation CrearMiembro($data: MiembroCreateInput!) {
    crearMiembro(data: $data) {
      id
      nombre
      apellido1
      apellido2
      email
      telefono
      tipoMiembro { id nombre }
      estado { id nombre }
      agrupacion { id nombre }
      fechaAlta
      activo
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
export const GET_TIPOS_MIEMBRO = `
  query TiposMiembro {
    tiposMiembro {
      id
      nombre
      descripcion
      requiereCuota
      puedeVotar
      activo
      orden
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
    unidadesOrganizativas {
      id
      nombre
      nombreCorto
      tipoId
      tipoUnidad { id nombre naturaleza vinculo nivel }
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

// Query para obtener formas de pago
export const GET_FORMAS_PAGO = `
  query FormasPago {
    formasPago(filter: {activo: {eq: true}}) {
      id
      codigo
      nombre
      descripcion
      activo
    }
  }
`
