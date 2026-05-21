/**
 * useConfirm — reemplaza window.confirm() con el ConfirmActionModal.
 *
 * Requiere que <ConfirmHost /> esté montado en App.vue (se encarga de mostrar el modal).
 *
 * Uso:
 *   const confirm = useConfirm()
 *   const ok = await confirm({
 *     titulo: '¿Anular remesa?',
 *     mensaje: 'Esta acción no se puede deshacer.',
 *     variante: 'critica',
 *     etiquetaConfirmar: 'Sí, anular',
 *   })
 *   if (!ok) return
 */
import { ref, shallowRef } from 'vue'

const state = ref({
  visible: false,
  titulo:  '',
  mensaje: '',
  variante: 'aviso',
  etiquetaConfirmar: 'Confirmar',
  etiquetaCancelar:  'Cancelar',
})

let _resolve = null

/** Uso interno desde ConfirmHost */
export const _confirmState = state

export function _resolveConfirm(value) {
  if (_resolve) {
    _resolve(value)
    _resolve = null
  }
  state.value.visible = false
}

export function useConfirm() {
  return function confirm(opts = {}) {
    state.value = {
      visible: true,
      titulo:  opts.titulo  ?? '¿Confirmar acción?',
      mensaje: opts.mensaje ?? '',
      variante: opts.variante ?? 'aviso',
      etiquetaConfirmar: opts.etiquetaConfirmar ?? 'Confirmar',
      etiquetaCancelar:  opts.etiquetaCancelar  ?? 'Cancelar',
    }
    return new Promise((resolve) => {
      _resolve = resolve
    })
  }
}
