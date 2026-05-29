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
import { ref } from 'vue'

const state = ref({
  visible: false,
  titulo:  '',
  mensaje: '',
  variante: 'aviso',
  etiquetaConfirmar: 'Confirmar',
  etiquetaCancelar:  'Cancelar',
  modo: 'confirm',     // 'confirm' (sí/no) | 'prompt' (captura de texto)
  input: null,         // { label, placeholder, multiline, requerido } cuando modo='prompt'
  inputValue: '',
})

let _resolve = null

/** Uso interno desde ConfirmHost */
export const _confirmState = state

export function _resolveConfirm(ok) {
  if (_resolve) {
    const value = state.value.modo === 'prompt'
      ? (ok ? state.value.inputValue : null)   // texto al aceptar, null al cancelar
      : ok                                     // booleano en modo confirmación
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
      modo: 'confirm', input: null, inputValue: '',
    }
    return new Promise((resolve) => { _resolve = resolve })
  }
}

/**
 * usePrompt — sustituto de window.prompt() con el mismo modal.
 * Resuelve con el texto introducido (string) al aceptar, o null al cancelar.
 *
 *   const motivo = await usePrompt()({ titulo:'Anular', label:'Motivo', requerido:true })
 *   if (motivo === null) return  // cancelado
 */
export function usePrompt() {
  return function prompt(opts = {}) {
    state.value = {
      visible: true,
      titulo:  opts.titulo  ?? 'Indica un valor',
      mensaje: opts.mensaje ?? '',
      variante: opts.variante ?? 'aviso',
      etiquetaConfirmar: opts.etiquetaConfirmar ?? 'Aceptar',
      etiquetaCancelar:  opts.etiquetaCancelar  ?? 'Cancelar',
      modo: 'prompt',
      input: {
        label: opts.label ?? '',
        placeholder: opts.placeholder ?? '',
        multiline: opts.multiline ?? true,
        requerido: opts.requerido ?? false,
      },
      inputValue: opts.valorInicial ?? '',
    }
    return new Promise((resolve) => { _resolve = resolve })
  }
}
