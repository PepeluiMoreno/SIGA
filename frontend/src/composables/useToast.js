/**
 * useToast — sistema de notificaciones toast global.
 *
 * Uso básico:
 *   const toast = useToast()
 *   toast.success('Guardado correctamente')
 *   toast.error('No se pudo guardar')
 *
 * Con acción "Deshacer":
 *   toast.success('Miembro eliminado', {
 *     accion: { label: 'Deshacer', callback: () => restaurarMiembro(id) },
 *     duration: 6000,
 *   })
 */
import { ref } from 'vue'

const toasts = ref([])
let nextId = 0

function add(message, type = 'info', options = {}) {
  const duration = options.duration ?? (type === 'error' ? 6000 : 4000)
  const id = ++nextId
  const toast = {
    id,
    message,
    type,
    accion: options.accion ?? null,  // { label: string, callback: fn }
  }
  toasts.value.push(toast)

  let timer = null
  if (duration > 0) {
    timer = setTimeout(() => remove(id), duration)
  }

  // Si hay acción de deshacer, cancelar el timer al ejecutarla
  if (toast.accion) {
    const originalCallback = toast.accion.callback
    toast.accion.callback = () => {
      if (timer) clearTimeout(timer)
      remove(id)
      originalCallback()
    }
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
    success: (msg, opts = {}) => add(msg, 'success', typeof opts === 'number' ? { duration: opts } : opts),
    error:   (msg, opts = {}) => add(msg, 'error',   typeof opts === 'number' ? { duration: opts } : opts),
    info:    (msg, opts = {}) => add(msg, 'info',    typeof opts === 'number' ? { duration: opts } : opts),
    warning: (msg, opts = {}) => add(msg, 'warning', typeof opts === 'number' ? { duration: opts } : opts),
    remove,
  }
}
