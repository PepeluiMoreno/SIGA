// Queries y mutations GraphQL para ÓRGANOS DE GOBIERNO.
//
// El modelo organizativo se configura POR NIVEL TERRITORIAL, no por agrupación:
//   NivelOrganizativo (Delegación) → NivelOrgano (su Junta Directiva)
//                                  → NivelOrganoCargo (Presidencia 1, Secretaría 2…)
// Las agrupaciones REALES instancian ese modelo (Organo / OrganoCargo); eso es
// poblamiento y vive en la ficha de la agrupación, no en configuración.
//
// Convención strawchemy del proyecto (ver queries/catalogos.js):
//   - create: crearX(data: XCreateInput!)
//   - update: actualizarX(data: XUpdateInput!)  ← el id viaja DENTRO de `data`
//   - delete: eliminarXs(filter: XFilter!)       ← filter { id: { eq } }
// Strawberry expone todo en camelCase automáticamente.

// El árbol de niveles lo carga `useUnidadesOrganizativas` (GET_TIPOS_UNIDADES_
// ORGANIZATIVAS): es el mismo `nivelesOrganizativos`, y el editor de estructura
// ya lo tiene en memoria. Aquí solo vive lo específico de órganos.

// =============================================
// ÓRGANOS DE UN NIVEL (el MODELO, no instancias)
// =============================================

export const GET_NIVELES_ORGANOS = `
  query NivelesOrganos($nivelId: UUID!) {
    nivelesOrganos(filter: { nivelId: { eq: $nivelId } }) {
      id
      nivelId
      tipoOrganoId
      activo
      tipoOrgano {
        id
        nombre
        composicion
      }
      composicion {
        id
        cargoId
        ordenProtocolario
        cargo {
          id
          nombre
        }
      }
    }
  }
`

/** Fija QUÉ órganos tiene un nivel. Reemplaza la lista; los que se
 *  mantienen conservan su composición. */
export const ESTABLECER_ORGANOS_DE_NIVEL = `
  mutation EstablecerOrganosDeNivel($nivelId: UUID!, $tipoOrganoIds: [UUID!]!) {
    establecerOrganosDeNivel(nivelId: $nivelId, tipoOrganoIds: $tipoOrganoIds)
  }
`

/** Copia el modelo organizativo (órganos + composición) de un nivel a otro.
 *  Se usa al crear un subnivel: hereda el modelo del padre. Salta los órganos
 *  que el destino ya tenga. Devuelve cuántos órganos copió. */
export const HEREDAR_MODELO_DE_NIVEL = `
  mutation HeredarModeloDeNivel($nivelOrigenId: UUID!, $nivelDestinoId: UUID!) {
    heredarModeloDeNivel(nivelOrigenId: $nivelOrigenId, nivelDestinoId: $nivelDestinoId)
  }
`

/** Reemplaza la composición de ese órgano EN ESE NIVEL. */
export const ESTABLECER_COMPOSICION_NIVEL_ORGANO = `
  mutation EstablecerComposicionNivelOrgano($nivelOrganoId: UUID!, $cargos: [CargoOrdenInput!]!) {
    establecerComposicionNivelOrgano(nivelOrganoId: $nivelOrganoId, cargos: $cargos)
  }
`

// =============================================
// TIPOS DE ÓRGANO (catálogo)
// =============================================

export const GET_TIPOS_ORGANO = `
  query TiposOrgano {
    tiposOrgano {
      id
      nombre
      descripcion
      denominacionSingular
      denominacionPlural
      composicion
      sistema
      activo
    }
  }
`

export const CREATE_TIPO_ORGANO = `
  mutation CrearTipoOrgano($data: TipoOrganoCreateInput!) {
    crearTipoOrgano(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_TIPO_ORGANO = `
  mutation ActualizarTipoOrgano($data: TipoOrganoUpdateInput!) {
    actualizarTipoOrgano(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_TIPO_ORGANO = `
  mutation EliminarTipoOrgano($filter: TipoOrganoFilter!) {
    eliminarTiposOrgano(filter: $filter) {
      id
    }
  }
`

// =============================================
// CARGOS (catálogo)
// =============================================

export const GET_CARGOS = `
  query Cargos {
    cargos {
      id
      nombre
      descripcion
      activo
      tipoUnidadId
      requiereAprobacion
      maxSimultaneos
      duracionMaximaMeses
    }
  }
`

export const CREATE_CARGO = `
  mutation CrearCargo($data: CargoCreateInput!) {
    crearCargo(data: $data) {
      id
      nombre
    }
  }
`

export const UPDATE_CARGO = `
  mutation ActualizarCargo($data: CargoUpdateInput!) {
    actualizarCargo(data: $data) {
      id
      nombre
    }
  }
`

export const DELETE_CARGO = `
  mutation EliminarCargo($filter: CargoFilter!) {
    eliminarCargos(filter: $filter) {
      id
    }
  }
`
