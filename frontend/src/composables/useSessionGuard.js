/**
 * Vigilante de caducidad de sesión — singleton para toda la aplicación.
 *
 * AppLayout se instancia en cada vista y varias quedan retenidas en
 * <keep-alive>, por lo que su `onUnmounted` no se ejecuta. Si el
 * temporizador viviera por instancia se acumularían intervalos zombis
 * que nunca se limpian y que siguen disparando el cierre de sesión
 * incluso tras volver a entrar. Por eso la vigilancia es un único
 * intervalo de ámbito de módulo, idempotente: arranca una sola vez y
 * se detiene al cerrar sesión.
 */
import { ref } from 'vue'

import router from '@/router'
import { useAuthStore } from '@/stores/auth.js'
import { useOrgConfigStore } from '@/stores/orgConfig.js'

const sessionTime = ref('0m')
let checkTimer = null
let lastActivity = Date.now()

function resetActivity() {
  lastActivity = Date.now()
}

/** Marca de inicio de sesión — persistida en localStorage; se crea si falta. */
function sessionStart() {
  const stored = localStorage.getItem('session_start_time')
  if (stored) {
    const n = parseInt(stored, 10)
    if (!Number.isNaN(n)) return n
  }
  const now = Date.now()
  localStorage.setItem('session_start_time', String(now))
  return now
}

function updateDisplay() {
  const minutes = Math.floor((Date.now() - sessionStart()) / 60000)
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  sessionTime.value = h > 0 ? `${h}h ${m}m` : `${m}m`
}

function check() {
  updateDisplay()
  const org = useOrgConfigStore()
  const now = Date.now()
  const inactividad = org.sessionInactividad
  const maximo = org.sessionMaximo
  const expirada =
    (inactividad > 0 && now - lastActivity > inactividad * 60000) ||
    (maximo > 0 && now - sessionStart() > maximo * 60000)
  if (expirada) {
    stopSessionGuard()
    useAuthStore().clearAuth()
    if (window.location.pathname !== '/login') router.push('/login')
  }
}

/** Arranca la vigilancia. Idempotente: si ya está en marcha, no hace nada. */
export function startSessionGuard() {
  if (checkTimer) return
  lastActivity = Date.now()
  sessionStart()
  updateDisplay()
  checkTimer = setInterval(check, 60000)
  window.addEventListener('mousemove', resetActivity)
  window.addEventListener('keydown', resetActivity)
  window.addEventListener('click', resetActivity)
}

/** Detiene la vigilancia y limpia la marca de inicio de sesión. */
export function stopSessionGuard() {
  if (checkTimer) {
    clearInterval(checkTimer)
    checkTimer = null
  }
  window.removeEventListener('mousemove', resetActivity)
  window.removeEventListener('keydown', resetActivity)
  window.removeEventListener('click', resetActivity)
  localStorage.removeItem('session_start_time')
  sessionTime.value = '0m'
}

/** Para usar desde AppLayout: arranca la vigilancia y expone el contador. */
export function useSessionGuard() {
  startSessionGuard()
  return { sessionTime }
}
