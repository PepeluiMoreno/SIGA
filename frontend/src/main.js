import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from '@/router'
import '@/style.css'
import App from '@/App.vue'
import { useDebugStore } from '@/stores/debug.js'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

const debugStore = useDebugStore(pinia)

if (debugStore.enabled) {
  debugStore.refreshSnapshot()

  window.addEventListener('error', (event) => {
    debugStore.captureError('window.error', event.error || new Error(event.message), {
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
    })
  })

  window.addEventListener('unhandledrejection', (event) => {
    debugStore.captureError('unhandledrejection', event.reason, {
      reasonType: typeof event.reason,
    })
  })

  debugStore.addEvent('debug', 'Modo debug UI activado')
}

app.mount('#app')
