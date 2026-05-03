// Queries y mutaciones GraphQL para administración de roles, transacciones y funcionalidades

export const GET_ROLES = `
  query Roles {
    roles {
      id
      codigo
      nombre
      descripcion
      tipo
      nivel
      activo
      sistema
      transacciones {
        id
      }
      funcionalidades {
        id
      }
    }
  }
`

export const GET_ROL_CON_PERMISOS = `
  query RolConPermisos($id: UUID!) {
    roles(filter: { id: { eq: $id } }) {
      id
      codigo
      nombre
      descripcion
      tipo
      nivel
      activo
      sistema
      transacciones {
        id
        transaccion {
          id
          codigo
          nombre
          descripcion
          modulo
          tipo
          activa
        }
      }
    }
  }
`

export const GET_ROL_CON_FUNCIONALIDADES = `
  query RolConFuncionalidades($id: UUID!) {
    roles(filter: { id: { eq: $id } }) {
      id
      codigo
      nombre
      descripcion
      tipo
      nivel
      activo
      sistema
      funcionalidades {
        id
        funcionalidad {
          id
          codigo
          nombre
          descripcion
          modulo
          activa
          sistema
          transacciones {
            ambito
            transaccion {
              id
              codigo
              nombre
              tipo
            }
          }
        }
      }
    }
  }
`

export const GET_TRANSACCIONES_TODAS = `
  query TransaccionesTodas {
    transacciones(filter: { activa: { eq: true } }) {
      id
      codigo
      nombre
      descripcion
      modulo
      tipo
    }
  }
`

export const GET_FUNCIONALIDADES_TODAS = `
  query FuncionalidadesTodas {
    funcionalidades(filter: { activa: { eq: true } }) {
      id
      codigo
      nombre
      descripcion
      modulo
      activa
      sistema
      transacciones {
        ambito
        transaccion {
          id
          codigo
          nombre
          tipo
        }
      }
    }
  }
`

export const ASIGNAR_TRANSACCION = `
  mutation AsignarTransaccion($data: RolTransaccionCreateInput!) {
    crearRolTransaccion(data: $data) {
      id
      transaccion {
        id
        codigo
      }
    }
  }
`

export const REVOCAR_TRANSACCION = `
  mutation RevocarRolTransaccion($filter: RolTransaccionFilter!) {
    eliminarRolesTransacciones(filter: $filter) {
      id
    }
  }
`

export const ASIGNAR_FUNCIONALIDAD = `
  mutation AsignarFuncionalidad($data: RolFuncionalidadCreateInput!) {
    crearRolFuncionalidad(data: $data) {
      id
      funcionalidad {
        id
        codigo
      }
    }
  }
`

export const REVOCAR_FUNCIONALIDAD = `
  mutation RevocarFuncionalidad($filter: RolFuncionalidadFilter!) {
    eliminarRolesFuncionalidades(filter: $filter) {
      id
    }
  }
`
