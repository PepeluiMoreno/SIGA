import { ref, computed } from 'vue'

/**
 * Selección múltiple para datagrids (estilo WordPress): mantiene un conjunto de
 * ids seleccionados sobre el resultado filtrado actual.
 *
 * @param {() => Array} getItems  función que devuelve los items filtrados visibles
 * @param {(item) => string} getId  extractor de id (por defecto item.id)
 */
export function useSeleccionMultiple(getItems, getId = (x) => x.id) {
  const seleccionados = ref(new Set())

  const idsActuales = computed(() => getItems().map(getId))
  const count = computed(() => seleccionados.value.size)
  const algoSeleccionado = computed(() => seleccionados.value.size > 0)
  // Todos los del resultado filtrado actual están seleccionados.
  const todoSeleccionado = computed(() =>
    idsActuales.value.length > 0 && idsActuales.value.every((id) => seleccionados.value.has(id))
  )

  function estaSeleccionado(id) {
    return seleccionados.value.has(id)
  }
  function toggle(id) {
    const s = new Set(seleccionados.value)
    s.has(id) ? s.delete(id) : s.add(id)
    seleccionados.value = s
  }
  function seleccionarTodos() {
    seleccionados.value = new Set(idsActuales.value)
  }
  function limpiar() {
    seleccionados.value = new Set()
  }
  function toggleTodos() {
    todoSeleccionado.value ? limpiar() : seleccionarTodos()
  }
  // Items completos seleccionados (no solo ids), respetando el resultado actual.
  function itemsSeleccionados() {
    return getItems().filter((it) => seleccionados.value.has(getId(it)))
  }

  return {
    seleccionados, count, algoSeleccionado, todoSeleccionado,
    estaSeleccionado, toggle, seleccionarTodos, limpiar, toggleTodos, itemsSeleccionados,
  }
}
