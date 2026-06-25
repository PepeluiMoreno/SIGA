// Queries GraphQL del directorio de Contactos (modelo CRM contacto-céntrico).
// Un Contacto es la identidad (PERSONA_FISICA | PERSONA_JURIDICA). Sus facetas
// (socio, voluntario, …) son `vinculaciones`. Strawberry expone camelCase.

// Listado del directorio. Trae identidad + facetas (para badges) en una query.
// `filter` admite icontains (búsqueda), tipo, y filtrado por faceta vía
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

// Facetas de un contacto con el detalle de su satélite (para la ficha).
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

// --- Mutaciones de facetas (alta/cierre de vinculación) ---
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
