import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { gql } from 'graphql-request'

import { graphqlClient, setAuthToken } from '@/graphql/client.js'
import { useDebugStore } from '@/stores/debug.js'

const LOGIN_MUTATION = gql`
  mutation Login($email: String!, $password: String!) {
    login(email: $email, password: $password) {
      token
      user {
        id
        email
        activo
      }
    }
  }
`

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()

  const token = ref(localStorage.getItem('siga_token'))
  const user = ref(JSON.parse(localStorage.getItem('siga_user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)
  const userName = computed(() => user.value?.email?.split('@')[0] || 'Usuario')
  const userInitials = computed(() => {
    const email = user.value?.email || 'US'
    return email.slice(0, 2).toUpperCase()
  })

  function setAuth(authData) {
    token.value = authData.token
    user.value = authData.user
    localStorage.setItem('siga_token', authData.token)
    localStorage.setItem('siga_user', JSON.stringify(authData.user))
    setAuthToken(authData.token)
    try {
      useDebugStore().refreshSnapshot()
    } catch {
      // noop outside debug mode or before Pinia is active
    }
  }

  function clearAuth() {
    token.value = null
    user.value = null
    localStorage.removeItem('siga_token')
    localStorage.removeItem('siga_user')
    setAuthToken(null)
    try {
      useDebugStore().refreshSnapshot()
    } catch {
      // noop outside debug mode or before Pinia is active
    }
  }

  async function login(email, password) {
    const data = await graphqlClient.request(LOGIN_MUTATION, { email, password })
    setAuth({ token: data.login.token, user: data.login.user })
    return data.login.user
  }

  async function logout() {
    clearAuth()
    router.push('/login')
  }

  return {
    token,
    user,
    isAuthenticated,
    userName,
    userInitials,
    login,
    logout,
    setAuth,
    clearAuth,
  }
})
