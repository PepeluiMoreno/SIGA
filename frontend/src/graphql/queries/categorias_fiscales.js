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
