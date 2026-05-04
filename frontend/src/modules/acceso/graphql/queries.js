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

// ==================== JUNTAS DIRECTIVAS ====================

export const GET_JUNTA_ACTIVA = `
  query JuntaActiva($agrupacionId: UUID!) {
    juntasDirectivas(filter: { agrupacionId: { eq: $agrupacionId }, activa: { eq: true } }) {
      id
      nombre
      fechaConstitucion
      fechaDisolucion
      activa
      observaciones
      cargos {
        id
        posicion
        fechaInicio
        fechaFin
        activo
        tipoCargo {
          id
          codigo
          nombre
          permiteMultiples
          orden
        }
        miembro {
          id
          nombre
          apellido1
          apellido2
          email
        }
      }
    }
  }
`

export const GET_HISTORIAL_JUNTA = `
  query HistorialJunta($juntaId: UUID!) {
    historialCargosJunta(filter: { juntaId: { eq: $juntaId } }) {
      id
      posicion
      fechaInicio
      fechaFin
      motivoCambio
      tipoCargo {
        id
        codigo
        nombre
      }
      miembro {
        id
        nombre
        apellido1
        apellido2
      }
    }
  }
`

export const GET_TIPOS_CARGO = `
  query TiposCargo {
    tiposCargo(filter: { activo: { eq: true } }) {
      id
      codigo
      nombre
      descripcion
      orden
      permiteMultiples
    }
  }
`

export const CONSTITUIR_JUNTA = `
  mutation ConstituirJunta(
    $agrupacionId: UUID!
    $nombre: String!
    $fechaConstitucion: Date!
    $observaciones: String
  ) {
    constituirJunta(
      agrupacionId: $agrupacionId
      nombre: $nombre
      fechaConstitucion: $fechaConstitucion
      observaciones: $observaciones
    )
  }
`

export const ASIGNAR_CARGO = `
  mutation AsignarCargo(
    $juntaId: UUID!
    $miembroId: UUID!
    $tipoCargaId: UUID!
    $fechaInicio: Date!
    $posicion: Int
    $usuarioId: UUID
  ) {
    asignarCargo(
      juntaId: $juntaId
      miembroId: $miembroId
      tipoCargaId: $tipoCargaId
      fechaInicio: $fechaInicio
      posicion: $posicion
      usuarioId: $usuarioId
    )
  }
`

export const REVOCAR_CARGO = `
  mutation RevocarCargo(
    $cargoJuntaId: UUID!
    $fechaFin: Date!
    $motivo: String
    $usuarioId: UUID
  ) {
    revocarCargo(
      cargoJuntaId: $cargoJuntaId
      fechaFin: $fechaFin
      motivo: $motivo
      usuarioId: $usuarioId
    )
  }
`
