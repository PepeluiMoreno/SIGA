import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { gql } from 'graphql-request'

import { graphqlClient, setAuthToken } from '@/graphql/client.js'
import { useDebugStore } from '@/stores/debug.js'
import { usePermisos } from '@/composables/usePermisos.js'

const LOGIN_MUTATION = gql`
  mutation Login($email: String!, $password: String!) {
    login(email: $email, password: $password) {
      token
      user {
        id
        email
        username
        activo
        miembroId
      }
    }
  }
`

// Query `me` para refrescar el user del backend si el cache del localStorage
// está desactualizado (p.ej. tras añadir nuevos campos al UserPayload).
const ME_QUERY = gql`
  query Me {
    me {
      id
      email
      username
      activo
      miembroId
    }
  }
`

// Perfil del miembro vinculado al usuario (para el avatar del sidebar).
const MIEMBRO_PERFIL_QUERY = gql`
  query MiembroPerfil($id: UUID!) {
    miembros: socios(contactoId: $id) {
      fotoUrl nombre apellido1
    }
  }
`

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  const permisos = usePermisos()

  // "Recordarme": si el usuario lo marca, la sesión se guarda en localStorage
  // (sobrevive al cierre del navegador); si no, en sessionStorage (se borra al
  // cerrar la pestaña/navegador). Al arrancar leemos del almacén que la tenga.
  const token = ref(localStorage.getItem('siga_token') || sessionStorage.getItem('siga_token'))
  const user = ref(JSON.parse(
    localStorage.getItem('siga_user') || sessionStorage.getItem('siga_user') || 'null'
  ))

  /** Almacén activo: aquel donde reside el token de sesión actual. */
  function activeStorage() {
    return localStorage.getItem('siga_token') ? localStorage : sessionStorage
  }

  /**
   * Sincroniza `user` con los datos vigentes del backend.
   * Útil cuando el localStorage tiene un user antiguo al que le faltan campos
   * que se han añadido al backend (p.ej. miembroId).
   */
  async function refreshUser() {
    if (!token.value) return null
    try {
      const data = await graphqlClient.request(ME_QUERY)
      if (!data?.me) return null
      const merged = { ...(user.value || {}), ...data.me }
      user.value = merged
      activeStorage().setItem('siga_user', JSON.stringify(merged))
      return merged
    } catch (e) {
      // Si el token está caducado el cliente ya gestiona la limpieza.
      console.warn('refreshUser falló:', e?.message || e)
      return null
    }
  }

  // Restore session on page load
  if (token.value) {
    setAuthToken(token.value)
    permisos.cargar()
    // Refrescar de forma asíncrona — sin bloquear el arranque
    refreshUser().then(() => cargarPerfilMiembro())
  }

  const isAuthenticated = computed(() => !!token.value)
  const userName = computed(() =>
    user.value?.email?.split('@')[0] || user.value?.username || 'Usuario'
  )
  const userInitials = computed(() => {
    const base = user.value?.email || user.value?.username || 'US'
    return base.slice(0, 2).toUpperCase()
  })

  // Perfil del miembro vinculado (avatar del sidebar). Estado compartido para
  // que al cambiar la foto desde Mis datos el sidebar se actualice sin recargar.
  const userFotoUrl = ref(null)
  const userNombre = ref('')
  const userApellido = ref('')

  async function cargarPerfilMiembro() {
    const miembroId = user.value?.miembroId
    if (!miembroId) {
      userFotoUrl.value = null; userNombre.value = ''; userApellido.value = ''
      return
    }
    try {
      const data = await graphqlClient.request(MIEMBRO_PERFIL_QUERY, { id: miembroId })
      const m = data?.miembros?.[0]
      if (m) {
        userFotoUrl.value = m.fotoUrl || null
        userNombre.value = m.nombre || ''
        userApellido.value = m.apellido1 || ''
      }
    } catch (e) {
      console.warn('cargarPerfilMiembro falló:', e?.message || e)
    }
  }

  /** Actualiza la foto del usuario en sesión (tras subir una nueva en Mis datos). */
  function setUserFoto(url) {
    // El backend reescribe el mismo filename, así que la URL no cambia: se añade
    // un parámetro de cache-bust para forzar la recarga de la imagen.
    userFotoUrl.value = url ? `${url.split('?')[0]}?t=${Date.now()}` : null
  }

  function setAuth(authData, remember = true) {
    token.value = authData.token
    user.value = authData.user
    // Limpiar ambos almacenes para no dejar una sesión obsoleta duplicada
    localStorage.removeItem('siga_token')
    localStorage.removeItem('siga_user')
    sessionStorage.removeItem('siga_token')
    sessionStorage.removeItem('siga_user')
    const store = remember ? localStorage : sessionStorage
    store.setItem('siga_token', authData.token)
    store.setItem('siga_user', JSON.stringify(authData.user))
    setAuthToken(authData.token)
    permisos.cargar()
    cargarPerfilMiembro()
    try {
      useDebugStore().refreshSnapshot()
    } catch {
      // noop outside debug mode or before Pinia is active
    }
  }

  function clearAuth() {
    token.value = null
    user.value = null
    userFotoUrl.value = null
    userNombre.value = ''
    userApellido.value = ''
    localStorage.removeItem('siga_token')
    localStorage.removeItem('siga_user')
    sessionStorage.removeItem('siga_token')
    sessionStorage.removeItem('siga_user')
    setAuthToken(null)
    permisos.limpiar()
    try {
      useDebugStore().refreshSnapshot()
    } catch {
      // noop outside debug mode or before Pinia is active
    }
  }

  async function login(email, password, remember = true) {
    const data = await graphqlClient.request(LOGIN_MUTATION, { email, password })
    setAuth({ token: data.login.token, user: data.login.user }, remember)
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
    userFotoUrl,
    userNombre,
    userApellido,
    cargarPerfilMiembro,
    setUserFoto,
    login,
    logout,
    setAuth,
    clearAuth,
    refreshUser,
  }
})
