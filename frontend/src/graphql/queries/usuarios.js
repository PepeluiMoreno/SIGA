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

// Mutation para crear usuario
export const CREAR_USUARIO = `
  mutation CrearUsuario(
    $email: String!
    $password: String
    $activo: Boolean
    $miembroId: UUID
    $tipoVinculacionId: UUID
    $entidadVinculacion: String
    $enviarEmailBienvenida: Boolean
  ) {
    crearUsuario(
      email: $email
      password: $password
      activo: $activo
      miembroId: $miembroId
      tipoVinculacionId: $tipoVinculacionId
      entidadVinculacion: $entidadVinculacion
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
      requiereEntidad
      activo
    }
  }
`

export const GET_MIEMBROS_SIMPLE = `
  query MiembrosSimple {
    miembros: socios {
      id
      nombre
      apellido1
      apellido2
      email
      tipoMiembro { id nombre }
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
