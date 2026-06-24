/**
 * useFocusTrap — gestiona el foco de teclado de un overlay modal
 * (diálogo, drawer, popover a pantalla completa).
 *
 * Al activarse:
 *   - Guarda el elemento que tenía el foco.
 *   - Mueve el foco al primer elemento enfocable del contenedor
 *     (o al propio contenedor si no hay ninguno).
 *   - Bloquea el scroll del <body> (con recuento, soporta overlays anidados).
 *
 * Mientras está activo:
 *   - Atrapa Tab / Shift+Tab dentro del contenedor (foco cíclico).
 *
 * Al desactivarse o desmontarse:
 *   - Restaura el foco al elemento previo.
 *   - Libera el bloqueo de scroll.
 *
 * El contenedor debe ser enfocable como respaldo: añádele tabindex="-1".
 *
 * Uso:
 *   const panel = ref(null)
 *   useFocusTrap(panel, () => props.modelValue)
 *
 *   <div ref="panel" tabindex="-1"> ... </div>
 *
 * @param {import('vue').Ref<HTMLElement|null>} containerRef  Contenedor del overlay.
 * @param {(() => boolean)|import('vue').Ref<boolean>} isActive  Estado abierto/cerrado.
 */
import { watch, nextTick, onBeforeUnmount } from 'vue'

const FOCUSABLE = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(',')

// Bloqueo de scroll compartido entre instancias (overlays anidados).
let lockCount = 0
let scrollPrev = ''

function bloquearScroll() {
  if (lockCount === 0) {
    scrollPrev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
  }
  lockCount += 1
}

function liberarScroll() {
  lockCount = Math.max(0, lockCount - 1)
  if (lockCount === 0) document.body.style.overflow = scrollPrev
}

export function useFocusTrap(containerRef, isActive) {
  let focoPrevio = null
  let activo = false

  function enfocables() {
    const el = containerRef.value
    if (!el) return []
    return Array.from(el.querySelectorAll(FOCUSABLE)).filter(
      (n) => n.offsetParent !== null || n === document.activeElement,
    )
  }

  function onKeydown(e) {
    if (e.key !== 'Tab' || !containerRef.value) return
    const items = enfocables()
    if (items.length === 0) {
      e.preventDefault()
      containerRef.value.focus()
      return
    }
    const primero = items[0]
    const ultimo = items[items.length - 1]
    const dentro = containerRef.value.contains(document.activeElement)
    if (e.shiftKey) {
      if (!dentro || document.activeElement === primero) {
        e.preventDefault()
        ultimo.focus()
      }
    } else if (!dentro || document.activeElement === ultimo) {
      e.preventDefault()
      primero.focus()
    }
  }

  async function activar() {
    if (activo) return
    activo = true
    focoPrevio = document.activeElement
    bloquearScroll()
    document.addEventListener('keydown', onKeydown, true)
    await nextTick()
    const items = enfocables()
    ;(items[0] ?? containerRef.value)?.focus?.()
  }

  function desactivar() {
    if (!activo) return
    activo = false
    document.removeEventListener('keydown', onKeydown, true)
    liberarScroll()
    if (focoPrevio && typeof focoPrevio.focus === 'function') {
      focoPrevio.focus()
    }
    focoPrevio = null
  }

  const stop = watch(
    () => (typeof isActive === 'function' ? isActive() : isActive?.value),
    (abierto) => (abierto ? activar() : desactivar()),
    { immediate: true },
  )

  onBeforeUnmount(() => {
    stop()
    desactivar()
  })

  return { activar, desactivar }
}
