// Queries y mutations GraphQL de categorías fiscales (contabilidad simplificada)

export const GET_CATEGORIAS_FISCALES = `
  query CategoriasFiscales($tipo: String, $activasSolo: Boolean) {
    categoriasFiscales(tipo: $tipo, activasSolo: $activasSolo) {
      id
      codigo
      nombre
      descripcion
      tipo
      computaModelo182
      computaModelo347
      casillaModelo
      orden
      color
      activa
    }
  }
`

export const CREAR_CATEGORIA_FISCAL = `
  mutation CrearCategoriaFiscal($data: CrearCategoriaFiscalInput!) {
    crearCategoriaFiscal(data: $data) {
      id
      codigo
      nombre
      tipo
    }
  }
`

export const ACTUALIZAR_CATEGORIA_FISCAL = `
  mutation ActualizarCategoriaFiscal($data: ActualizarCategoriaFiscalInput!) {
    actualizarCategoriaFiscal(data: $data) {
      id
      codigo
      nombre
      tipo
      activa
    }
  }
`

export const ELIMINAR_CATEGORIA_FISCAL = `
  mutation EliminarCategoriaFiscal($categoriaId: UUID!) {
    eliminarCategoriaFiscal(categoriaId: $categoriaId)
  }
`

// ── REGLAS DE CATEGORIZACIÓN ──────────────────────────────────────────────────

export const GET_REGLAS_CATEGORIZACION = `
  query ReglasCategorizacion($activasSolo: Boolean) {
    reglasCategorizacion(activasSolo: $activasSolo) {
      id
      patron
      tipoCoincidencia
      tipoApunte
      categoriaFiscalId
      orden
      descripcion
      activa
    }
  }
`

export const GET_APUNTES_SIN_CLASIFICAR = `
  query ApuntesSinClasificar($ejercicio: Int) {
    apuntesSinClasificar(ejercicio: $ejercicio)
  }
`

export const CREAR_REGLA_CATEGORIZACION = `
  mutation CrearReglaCategorizacion($data: CrearReglaCategorizacionInput!) {
    crearReglaCategorizacion(data: $data) {
      id
      patron
      tipoCoincidencia
    }
  }
`

export const ACTUALIZAR_REGLA_CATEGORIZACION = `
  mutation ActualizarReglaCategorizacion($data: ActualizarReglaCategorizacionInput!) {
    actualizarReglaCategorizacion(data: $data) {
      id
      patron
      activa
    }
  }
`

export const ELIMINAR_REGLA_CATEGORIZACION = `
  mutation EliminarReglaCategorizacion($reglaId: UUID!) {
    eliminarReglaCategorizacion(reglaId: $reglaId)
  }
`

export const CLASIFICAR_APUNTES_PENDIENTES = `
  mutation ClasificarApuntesPendientes($ejercicio: Int, $forzar: Boolean) {
    clasificarApuntesPendientes(ejercicio: $ejercicio, forzar: $forzar) {
      procesados
      clasificados
    }
  }
`

export const ASIGNAR_CATEGORIA_MASIVA = `
  mutation AsignarCategoriaMasiva($apunteIds: [UUID!]!, $categoriaFiscalId: UUID!) {
    asignarCategoriaMasiva(apunteIds: $apunteIds, categoriaFiscalId: $categoriaFiscalId)
  }
`
