// Queries GraphQL para el módulo de miembros
// IMPORTANTE: Strawberry convierte nombres a camelCase automáticamente
// NO usar campos 'codigo' - solo se identifican por UUID
// Strawchemy no usa limit/offset, usa filtros automáticos generados

// Query para obtener miembros
export const GET_MIEMBROS = `
  query Miembros {
    miembros: socios {
      id
      nombre
      apellido1
      apellido2
      fotoUrl
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
        tipoVinculacionId
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

// Cuentas de acceso (TODOS los usuarios) — para la vista de gestión de usuarios.
// A diferencia de GET_MIEMBROS (que parte de `socios`), parte de `cuentasAcceso`,
// que lista toda cuenta tenga o no vinculación de socio (incluida la de sistema sin
// contacto). Misma forma de datos que GET_MIEMBROS para que la vista no cambie.
export const GET_CUENTAS_ACCESO = `
  query CuentasAcceso {
    miembros: cuentasAcceso {
      id
      nombre
      apellido1
      apellido2
      fotoUrl
      email
      telefono
      usuario {
        id
        email
        activo
        ultimoAcceso
        tipoVinculacionId
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
      agrupacion {
        id
        nombre
        tipoUnidad { id nombre naturaleza vinculo }
      }
      activo
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
    miembros: socios(contactoId: $id) {
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
      motivoReduccionId
      incrementoCuota
      incrementoCuotaObs
      tipoMiembro { id nombre }
      estado { id nombre color }
      agrupacion { id nombre }
      motivoBajaRel { id nombre }
      motivoReduccion { id codigo nombre porcentajeReduccion excluyeCuota }
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

// Autoservicio: el usuario logueado edita SUS PROPIOS datos personales. No exige el
// permiso administrativo MEMBRESIA_MIEMBRO_EDITAR; opera siempre sobre el contacto del
// usuario en sesión (el backend ignora cualquier id y solo aplica campos personales).
export const UPDATE_MIS_DATOS = `
  mutation ActualizarMisDatos($data: MiembroUpdateInput!) {
    actualizarMisDatos(data: $data) {
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
    miembros: socios {
      id
    }
  }
`

// Query para obtener formas de pago.
// Nota: FormaPagoFilter no expone campos (strawchemy lo genera vacío), así que
// no se puede filtrar por `activo` en el servidor; se traen todas y, si hace
// falta, se filtra por `activo` en el cliente.
export const GET_FORMAS_PAGO = `
  query FormasPago {
    formasPago {
      id
      codigo
      nombre
      descripcion
      activo
    }
  }
`
