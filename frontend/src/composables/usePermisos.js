import { ref } from 'vue'
import { graphqlClient } from '@/graphql/client.js'

const MIS_TRANSACCIONES = `
  query MisTransacciones {
    misTransacciones
  }
`

const _codigos = ref(new Set())
const _loaded = ref(false)

export function usePermisos() {
  async function cargar() {
    try {
      const data = await graphqlClient.request(MIS_TRANSACCIONES)
      _codigos.value = new Set(data.misTransacciones || [])
      _loaded.value = true
    } catch {
      _codigos.value = new Set()
    }
  }

  function limpiar() {
    _codigos.value = new Set()
    _loaded.value = false
  }

  function tienePermiso(codigo) {
    return _codigos.value.has(codigo)
  }

  function tieneAlguno(...codigos) {
    return codigos.some(c => _codigos.value.has(c))
  }

  function tieneTodos(...codigos) {
    return codigos.every(c => _codigos.value.has(c))
  }

  return { cargar, limpiar, tienePermiso, tieneAlguno, tieneTodos, codigos: _codigos, loaded: _loaded }
}
