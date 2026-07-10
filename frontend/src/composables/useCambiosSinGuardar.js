/**
 * useCambiosSinGuardar — avisa antes de abandonar una vista de edición con
 * cambios sin guardar. Cubre las dos vías de salida:
 *   - navegación interna (router) → modal de confirmación (useConfirm)
 *   - cerrar/recargar la pestaña   → aviso nativo del navegador (beforeunload)
 *
 * La vista aporta una función que dice si hay cambios pendientes. Lo normal es
 * comparar un snapshot del formulario con su estado actual, pero cualquier
 * predicado vale.
 *
 * Uso:
 *   const form = reactive({ ... })
 *   let original = ''
 *   const marcarLimpio = () => { original = JSON.stringify(form) }
 *   onMounted(marcarLimpio)                       // tras cargar los datos
 *   const { estaSucio } = useCambiosSinGuardar(() => JSON.stringify(form) !== original)
 *   async function guardar() { ...; marcarLimpio() }   // limpio tras guardar
 *
 * Con un ref booleano que ya lleves:
 *   const hayCambios = ref(false)
 *   useCambiosSinGuardar(hayCambios)
 *
 * IMPORTANTE: tras guardar (o descartar) hay que dejar el estado «limpio», o el
 * aviso saltará al salir aunque ya no haya nada pendiente.
 */
import { computed, onBeforeUnmount, unref } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import { useConfirm } from '@/composables/useConfirm'

export function useCambiosSinGuardar(fuente, opts = {}) {
  const confirm = useConfirm()

  // `fuente` puede ser un ref/computed booleano o una función predicado.
  const estaSucio = computed(() =>
    typeof fuente === 'function' ? !!fuente() : !!unref(fuente)
  )

  // ── Salida por navegación interna ──────────────────────────────────────────
  onBeforeRouteLeave(async () => {
    if (!estaSucio.value) return true
    const seguir = await confirm({
      titulo: opts.titulo ?? '¿Salir sin guardar?',
      mensaje: opts.mensaje ?? 'Hay cambios sin guardar. Si sales ahora se perderán.',
      variante: 'critica',
      etiquetaConfirmar: opts.etiquetaConfirmar ?? 'Salir sin guardar',
      etiquetaCancelar: opts.etiquetaCancelar ?? 'Seguir editando',
    })
    return seguir === true   // false/null → cancela la navegación
  })

  // ── Salida por cerrar/recargar la pestaña ──────────────────────────────────
  // El navegador solo permite el diálogo nativo (no se puede personalizar).
  function onBeforeUnload(e) {
    if (!estaSucio.value) return
    e.preventDefault()
    e.returnValue = ''   // requerido por Chrome para mostrar el aviso
  }
  window.addEventListener('beforeunload', onBeforeUnload)
  onBeforeUnmount(() => window.removeEventListener('beforeunload', onBeforeUnload))

  return { estaSucio }
}
