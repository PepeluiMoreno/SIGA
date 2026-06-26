// Queries GraphQL para el módulo de usuarios
// IMPORTANTE: Strawberry usa camelCase automáticamente
// NO usar campos 'codigo' - solo se identifican por UUID

// Query para obtener usuarios
export const GET_USUARIOS = `
  query Usuarios {
    usuarios {
      id
      email
      activo
      ultimoAcceso
    }
  }
`

// Mutation para crear usuario.
// La cuenta se asocia al contacto elegido (miembroId = id de contacto). La
// vinculación con la organización ya la tiene el contacto; aquí solo se le dota
// de credenciales de acceso.
export const CREAR_USUARIO = `
  mutation CrearUsuario(
    $email: String!
    $password: String
    $activo: Boolean
    $miembroId: UUID
    $enviarEmailBienvenida: Boolean
  ) {
    crearUsuario(
      email: $email
      password: $password
      activo: $activo
      miembroId: $miembroId
      enviarEmailBienvenida: $enviarEmailBienvenida
    ) {
      id
      email
      activo
    }
  }
`

// Desactivar usuario (activo=False; reversible, no va a la papelera).
export const DESACTIVAR_USUARIO = `
  mutation DesactivarUsuario($id: UUID!) {
    desactivarUsuario(id: $id)
  }
`

// Eliminar usuario: soft-delete (papelera) por defecto, o hard-delete si hard=true.
// El hard-delete se deniega por motivos de auditoría si el usuario creó/modificó
// registros; en ese caso el backend devuelve un error explicativo.
export const ELIMINAR_USUARIO = `
  mutation EliminarUsuario($id: UUID!, $hard: Boolean) {
    eliminarUsuario(id: $id, hard: $hard)
  }
`

export const GET_TIPOS_VINCULACION = `
  query TiposVinculacion {
    tiposVinculacion {
      id
      nombre
      requiereSatelite
      permiteCuenta
      activo
    }
  }
`

// Contactos a los que se puede dotar de cuenta de usuario, filtrables por tipo de
// vínculo y por texto. Cada uno indica si ya tiene cuenta (tieneAcceso).
export const GET_CONTACTOS_DOTABLES = `
  query ContactosDotables($tipoVinculacionId: UUID, $texto: String) {
    contactosDotables(tipoVinculacionId: $tipoVinculacionId, texto: $texto) {
      id
      tipo
      nombre
      apellido1
      apellido2
      razonSocial
      email
      telefono
      tipoVinculacionId
      tipoVinculacionNombre
      tipoVinculacionCodigo
      agrupacion { id nombre }
      tieneAcceso
    }
  }
`

// Query para obtener un usuario por ID
export const GET_USUARIO_BY_ID = `
  query Usuario($id: UUID!) {
    usuarios(filter: {id: {eq: $id}}) {
      id
      nombre
      email
      activo
      ultimoAcceso
      fechaCreacion
      fechaModificacion
      miembro {
        id
        nombre
        apellido1
      }
    }
  }
`

// Query para obtener roles de usuario
export const GET_USUARIO_ROLES = `
  query UsuarioRoles {
    usuarioRoles {
      id
      nombre
      descripcion
      permisos
      activo
    }
  }
`
