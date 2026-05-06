import { defineStore } from 'pinia'
import { graphqlClient } from '@/graphql/client.js'

const QUERY = `
  query {
    appInitialized
    parametrosOrganizacion { logo nombre }
  }
`

export const useOrgConfigStore = defineStore('orgConfig', {
  state: () => ({
    logo: '',
    nombre: '',
    initialized: null, // null = unknown, true/false once fetched
    loaded: false,
  }),
  actions: {
    async fetchConfig() {
      if (this.loaded) return
      try {
        const data = await graphqlClient.request(QUERY)
        this.initialized = data.appInitialized
        this.logo = data.parametrosOrganizacion.logo ?? ''
        this.nombre = data.parametrosOrganizacion.nombre ?? ''
        this.loaded = true
      } catch {
        // backend temporarily unavailable — leave initialized as null
      }
    },
    async checkInitialized() {
      if (this.initialized !== null) return this.initialized
      await this.fetchConfig()
      return this.initialized ?? true // fail open: don't block the app if backend is down
    },
    setLogo(logo) {
      this.logo = logo
    },
    markInitialized(nombre, logo) {
      this.initialized = true
      this.nombre = nombre
      this.logo = logo
      this.loaded = true
    },
  },
})
