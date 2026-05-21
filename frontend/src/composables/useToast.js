/**
 * useToast — sistema de notificaciones toast global.
 *
 * Uso en cualquier componente:
 *   import { useToast } from '@/composables/useToast'
 *   const toast = useToast()
 *   toast.success('Guardado correctamente')
 *   toast.error('No se pudo guardar')
 *   toast.info('Procesando...')
 *   toast.warning('Revisa los datos')
 */
import { ref } from 'vue'

const toasts = ref([])
let nextId = 0

function add(message, type = 'info', duration = 4000) {
  const id = ++nextId
  toasts.value.push({ id, message, type })
  if (duration > 0) {
    setTimeout(() => remove(id), duration)
  }
  return id
}

function remove(id) {
  const idx = toasts.value.findIndex(t => t.id === id)
  if (idx !== -1) toasts.value.splice(idx, 1)
}

export function useToast() {
  return {
    toasts,
    success: (msg, duration)  => add(msg, 'success', duration),
    error:   (msg, duration)  => add(msg, 'error',   duration ?? 6000),
    info:    (msg, duration)  => add(msg, 'info',    duration),
    warning: (msg, duration)  => add(msg, 'warning', duration),
    remove,
  }
}
