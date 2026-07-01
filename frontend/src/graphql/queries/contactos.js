// Queries GraphQL del directorio de Contactos (modelo CRM contacto-céntrico).
// Un Contacto es la identidad (PERSONA_FISICA | PERSONA_JURIDICA). Sus vinculaciones
// (socio, voluntario, …) son `vinculaciones`. Strawberry expone camelCase.

// Listado del directorio. Trae identidad + vinculaciones (para badges) en una query.
// `filter` admite icontains (búsqueda), tipo, y filtrado por vinculación vía
// `vinculaciones: { tipoVinculacion: { codigo: { eq } }, fechaFin: { isNull } }`.
export const GET_CONTACTOS = `
  query Contactos($filter: ContactoFilter) {
    contactos(filter: $filter) {
      id
      tipo
      nombre
      apellido1
      apellido2
      razonSocial
      email
      telefono
      numeroDocumento
      cif
      agrupacionId
      activo
      vinculaciones {
        id
        estado
        fechaInicio
        fechaFin
        tipoVinculacion { id codigo nombre ambito }
      }
    }
  }
`

// Un contacto por id (identidad completa).
export const GET_CONTACTO = `
  query Contacto($id: UUID!) {
    contactos(filter: { id: { eq: $id } }) {
      id
      tipo
      nombre
      apellido1
      apellido2
      razonSocial
      tipoDocumento
      numeroDocumento
      cif
      tipoEntidadJuridicaId
      actividadPrincipal
      representanteLegalId
      sexo
      fechaNacimiento
      profesion
      nivelEstudiosId
      direccion
      codigoPostal
      localidad
      provinciaId
      entidadGeograficaId
      paisDomicilioId
      telefono
      telefono2
      email
      agrupacionId
      fotoUrl
      activo
    }
  }
`

// Vinculaciones de un contacto con el detalle de su satélite (para la ficha).
export const VINCULACIONES_DE_CONTACTO = `
  query VinculacionesDeContacto($contactoId: UUID!) {
    vinculacionesDeContacto(contactoId: $contactoId) {
      id
      estado
      fechaInicio
      fechaFin
      agrupacionId
      tipoVinculacion { id codigo nombre ambito requiereSatelite }
      socio {
        id
        numeroSocio
        cuotaMensual
        iban
        esHonor
        estadoSocio
      }
      voluntario {
        id
        disponibilidad
        horasDisponiblesSemana
        intereses
        puedeConducir
        vehiculoPropio
        disponibilidadViajar
      }
    }
  }
`

// --- Mutaciones de identidad ---
export const CREAR_CONTACTO = `
  mutation CrearContacto($data: ContactoCreateInput!) {
    crearContacto(data: $data) { id tipo nombre razonSocial }
  }
`

export const ACTUALIZAR_CONTACTO = `
  mutation ActualizarContacto($data: ContactoUpdateInput!) {
    actualizarContacto(data: $data) { id tipo nombre razonSocial }
  }
`

// Baja lógica (soft delete): retira el contacto del directorio (eliminado=true).
export const ELIMINAR_CONTACTO = `
  mutation EliminarContacto($id: UUID!) {
    eliminarContacto(id: $id) { id }
  }
`

// --- Mutaciones de vinculaciones (alta/cierre de vinculación) ---
export const ALTA_VINCULACION_SOCIO = `
  mutation AltaVinculacionSocio($data: AltaVinculacionSocioInput!) {
    altaVinculacionSocio(data: $data) {
      id estado tipoVinculacion { codigo } socio { numeroSocio }
    }
  }
`

export const ALTA_VINCULACION_VOLUNTARIO = `
  mutation AltaVinculacionVoluntario($data: AltaVinculacionVoluntarioInput!) {
    altaVinculacionVoluntario(data: $data) {
      id estado tipoVinculacion { codigo } voluntario { disponibilidad }
    }
  }
`

export const CERRAR_VINCULACION = `
  mutation CerrarVinculacion($vinculacionId: UUID!, $fechaCierre: Date) {
    cerrarVinculacion(vinculacionId: $vinculacionId, fechaCierre: $fechaCierre) {
      id estado fechaFin
    }
  }
`

// Condiciones DERIVADAS de un contacto (firmante/participante/donante),
// calculadas de sus registros. Para los badges de la ficha del contacto.
export const GET_CONDICIONES_CONTACTO = `
  query CondicionesContacto($contactoId: UUID!) {
    condicionesContacto(contactoId: $contactoId) {
      esParticipante
      esFirmante
      esDonante
      nFirmas
      nParticipaciones
      nDonaciones
    }
  }
`

// Condiciones derivadas de VARIOS contactos (batch, para el listado).
export const GET_CONDICIONES_CONTACTOS = `
  query CondicionesContactos($contactoIds: [UUID!]!) {
    condicionesContactos(contactoIds: $contactoIds) {
      contactoId
      esParticipante
      esFirmante
      esDonante
    }
  }
`
