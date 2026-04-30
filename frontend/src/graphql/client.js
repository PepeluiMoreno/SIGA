import { GraphQLClient } from 'graphql-request'

// Por defecto el SPA y la API se sirven en el mismo host detrás de Traefik:
// el frontend hace requests a /api/graphql (Traefik strippa /api → backend /graphql).
// VITE_GRAPHQL_URL solo se usa para desarrollo cuando el backend corre en otro puerto.
const GRAPHQL_ENDPOINT = import.meta.env.VITE_GRAPHQL_URL || '/api/graphql'

export const graphqlClient = new GraphQLClient(GRAPHQL_ENDPOINT, {
  headers: {
    'Content-Type': 'application/json',
  },
})

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
