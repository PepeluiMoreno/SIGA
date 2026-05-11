import { ref } from 'vue'
import { useGraphQL } from './useGraphQL'
import {
  GET_TIPOS_UNIDADES_ORGANIZATIVAS,
  GET_AGRUPACIONES_TERRITORIALES,
  CREATE_TIPO_UNIDAD_ORGANIZATIVA,
  UPDATE_TIPO_UNIDAD_ORGANIZATIVA,
  DELETE_TIPO_UNIDAD_ORGANIZATIVA,
  CREATE_AGRUPACION_TERRITORIAL,
  UPDATE_AGRUPACION_TERRITORIAL,
} from '@/graphql/queries/catalogos'

const ARCHIVAR_AGRUPACION = `
  mutation ArchivarAgrupacion($id: UUID!) {
    archivarAgrupacionTerritorial(id: $id) { id }
  }
`

export function useUnidadesOrganizativas() {
  const { query, mutation, loading, error } = useGraphQL()
  const tipos = ref([])
  const unidades = ref([])
  const coordinaciones = ref([])
  const miembros = ref([])

  const cargarTipos = async () => {
    const data = await query(GET_TIPOS_UNIDADES_ORGANIZATIVAS)
    tipos.value = (data.tiposUnidadesOrganizativas || []).sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
    return tipos.value
  }

  const cargarArbol = async () => {
    const data = await query(GET_AGRUPACIONES_TERRITORIALES)
    unidades.value = data.agrupacionesTerritoriales || []
    coordinaciones.value = data.coordinacionesTerritoriales || []
    miembros.value = data.miembros || []
    return unidades.value
  }

  const construirArbol = (lista) => {
    const map = {}
    const raices = []
    lista.forEach(n => { map[n.id] = { ...n, hijos: [] } })
    lista.forEach(n => {
      if (n.agrupacionPadreId && map[n.agrupacionPadreId]) {
        map[n.agrupacionPadreId].hijos.push(map[n.id])
      } else {
        raices.push(map[n.id])
      }
    })
    return raices
  }

  const crearTipo = async ({ nombre, naturaleza, vinculo, nivel = null, padreTipoId = null, activo = true }) => {
    await mutation(CREATE_TIPO_UNIDAD_ORGANIZATIVA, { nombre, naturaleza, vinculo, nivel, padreTipoId, activo })
    await cargarTipos()
  }

  const actualizarTipo = async (data) => {
    const res = await mutation(UPDATE_TIPO_UNIDAD_ORGANIZATIVA, { data })
    await cargarTipos()
    return res.actualizarTipoUnidadOrganizativa
  }

  const eliminarTipo = async (id) => {
    await mutation(DELETE_TIPO_UNIDAD_ORGANIZATIVA, { filter: { id: { eq: id } } })
    await cargarTipos()
  }

  const crearUnidad = async (data) => {
    const res = await mutation(CREATE_AGRUPACION_TERRITORIAL, { data })
    await cargarArbol()
    return res.crearAgrupacionTerritorial
  }

  const actualizarUnidad = async (data) => {
    const res = await mutation(UPDATE_AGRUPACION_TERRITORIAL, { data })
    await cargarArbol()
    return res.actualizarAgrupacionTerritorial
  }

  const archivarUnidad = async (id) => {
    await mutation(ARCHIVAR_AGRUPACION, { id })
    await cargarArbol()
  }

  return {
    tipos, unidades, coordinaciones, miembros, loading, error,
    cargarTipos, cargarArbol, construirArbol,
    crearTipo, actualizarTipo, eliminarTipo,
    crearUnidad, actualizarUnidad, archivarUnidad,
  }
}
