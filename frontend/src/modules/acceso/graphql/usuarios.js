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
  mutation CrearUsuario($email: String!, $password: String!, $activo: Boolean) {
    crearUsuario(email: $email, password: $password, activo: $activo) {
      id
      email
      activo
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
