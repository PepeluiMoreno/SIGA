import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

const MAX_EVENTS = 20
const REDACTED = '[redacted]'

function isDebugEnabled() {
  const envEnabled = import.meta.env.VITE_DEBUG_UI === 'true'
  if (envEnabled) return true

  if (typeof window === 'undefined') return false
  return new URLSearchParams(window.location.search).get('debug') === '1'
}

function redactValue(value, seen = new WeakSet()) {
  if (value == null) return value

  if (typeof value === 'string') {
    return value.length > 300 ? `${value.slice(0, 300)}...` : value
  }

  if (typeof value !== 'object') return value
  if (seen.has(value)) return '[circular]'
  seen.add(value)

  if (Array.isArray(value)) {
    return value.map((item) => redactValue(item, seen))
  }

  const redacted = {}
  for (const [key, nested] of Object.entries(value)) {
    if (/pass|token|authorization|secret|jwt/i.test(key)) {
      redacted[key] = REDACTED
    } else {
      redacted[key] = redactValue(nested, seen)
    }
  }
  return redacted
}

function serializeError(error) {
  if (!error) return { message: 'Unknown error' }
  if (typeof error === 'string') return { message: error }

  return redactValue({
    name: error.name,
    message: error.message,
    stack: error.stack,
    response: error.response,
    cause: error.cause,
  })
}

export const useDebugStore = defineStore('debug', () => {
  const enabled = ref(isDebugEnabled())
  const expanded = ref(false)
  const events = ref([])
  const snapshot = ref({
    route: '',
    graphqlEndpoint: '(unknown)',
    hasToken: false,
    storedUser: null,
  })

  const sessionSnapshot = computed(() => snapshot.value)

  function refreshSnapshot() {
    if (typeof window === 'undefined') return

    const token = localStorage.getItem('siga_token')
    const user = localStorage.getItem('siga_user')

    let parsedUser = null
    if (user) {
      try {
        parsedUser = redactValue(JSON.parse(user))
      } catch {
        parsedUser = '[invalid-json]'
      }
    }

    snapshot.value = {
      route: `${window.location.pathname}${window.location.search}`,
      graphqlEndpoint: window.__SIGA_GRAPHQL_ENDPOINT__ || '(unknown)',
      hasToken: Boolean(token),
      storedUser: parsedUser,
    }
  }

  function toggleExpanded() {
    expanded.value = !expanded.value
  }

  function clearEvents() {
    events.value = []
  }

  function pushEvent(entry) {
    if (!enabled.value) return

    refreshSnapshot()
    events.value = [
      {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        timestamp: new Date().toISOString(),
        ...entry,
      },
      ...events.value,
    ].slice(0, MAX_EVENTS)
  }

  function addEvent(type, message, meta = null) {
    pushEvent({
      type,
      message,
      meta: meta ? redactValue(meta) : null,
    })
  }

  function captureError(type, error, meta = null) {
    pushEvent({
      type,
      message: error?.message || String(error),
      error: serializeError(error),
      meta: meta ? redactValue(meta) : null,
    })
  }

  function copySummary() {
    const summary = JSON.stringify(
      {
        enabled: enabled.value,
        snapshot: sessionSnapshot.value,
        events: events.value,
      },
      null,
      2,
    )

    return navigator.clipboard.writeText(summary)
  }

  return {
    enabled,
    expanded,
    events,
    sessionSnapshot,
    refreshSnapshot,
    toggleExpanded,
    clearEvents,
    addEvent,
    captureError,
    copySummary,
  }
})
