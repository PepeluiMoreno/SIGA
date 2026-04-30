import { GraphQLClient } from 'graphql-request'
import { useDebugStore } from '@/stores/debug.js'

// Por defecto el SPA y la API se sirven en el mismo host detrás de Traefik:
// el frontend hace requests a /api/graphql (Traefik strippa /api → backend /graphql).
// VITE_GRAPHQL_URL solo se usa para desarrollo cuando el backend corre en otro puerto.
function resolveGraphqlEndpoint() {
  const configured = import.meta.env.VITE_GRAPHQL_URL
  if (configured) return configured

  if (typeof window !== 'undefined' && window.location?.origin) {
    return new URL('/api/graphql', window.location.origin).toString()
  }

  return '/api/graphql'
}

const GRAPHQL_ENDPOINT = resolveGraphqlEndpoint()
if (typeof window !== 'undefined') {
  window.__SIGA_GRAPHQL_ENDPOINT__ = GRAPHQL_ENDPOINT
}

export const graphqlClient = new GraphQLClient(GRAPHQL_ENDPOINT, {
  headers: {
    'Content-Type': 'application/json',
  },
})

const originalRequest = graphqlClient.request.bind(graphqlClient)
graphqlClient.request = async function patchedRequest(document, variables, requestHeaders) {
  let debugStore = null

  try {
    debugStore = useDebugStore()
  } catch {
    debugStore = null
  }

  const operation = typeof document === 'string' ? document.slice(0, 120) : 'graphql-document'

  if (debugStore?.enabled) {
    debugStore.addEvent('graphql.request', 'Enviando petición GraphQL', {
      endpoint: GRAPHQL_ENDPOINT,
      operation,
      variables,
    })
  }

  try {
    const result = await originalRequest(document, variables, requestHeaders)
    if (debugStore?.enabled) {
      debugStore.addEvent('graphql.success', 'Petición GraphQL completada', {
        endpoint: GRAPHQL_ENDPOINT,
        operation,
      })
    }
    return result
  } catch (error) {
    if (debugStore?.enabled) {
      debugStore.captureError('graphql.error', error, {
        endpoint: GRAPHQL_ENDPOINT,
        operation,
        variables,
      })
    }
    throw error
  }
}

export function setAuthToken(token) {
  if (token) {
    graphqlClient.setHeader('Authorization', `Bearer ${token}`)
  } else {
    graphqlClient.setHeader('Authorization', '')
  }
}

// Inicializa el header desde localStorage en la carga del módulo.
const _stored = localStorage.getItem('siga_token')
if (_stored) setAuthToken(_stored)

export async function executeQuery(query, variables = {}) {
  return graphqlClient.request(query, variables)
}

export async function executeMutation(mutation, variables = {}) {
  return graphqlClient.request(mutation, variables)
}
