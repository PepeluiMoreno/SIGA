import { defineStore } from 'pinia'
import { graphqlClient } from '@/graphql/client.js'


const QUERY = `
  query {
    appInitialized
    parametrosOrganizacion {
      logo nombre tipoUnidadOrganizativa
      denominacionMiembro denominacionMiembroPlural
      denominacionOrganoGobierno denominacionOrganoGobiernoPlural
      sessionInactividadMinutos sessionMaximoMinutos
      tema fuentePrincipal usaPresupuesto chatActivo
    }
    temasUi {
      id nombre slug
      t50 t100 t200 t300 t400 t500 t600 t700 t800 t900
      sidebar topbar pageBg cardBg textMain textMuted borderColor
      sistema activo
    }
  }
`

export const useOrgConfigStore = defineStore('orgConfig', {
  state: () => ({
    logo: '',
    nombre: '',
    tipoAgrupacion: '',
    miembro: 'socio',
    miembros: 'socios',
    organoGobierno: 'junta directiva',
    organoGobiernoPl: 'juntas directivas',
    sessionInactividad: 30,
    sessionMaximo: 480,
    tema: 'violeta',
    fuentePrincipal: 'Inter',
    temas: [],
    usaPresupuesto: false,
    chatActivo: false,
    initialized: null,
    loaded: false,
  }),
  getters: {
    Miembro: (s) => s.miembro ? s.miembro.charAt(0).toUpperCase() + s.miembro.slice(1) : 'Socio',
    Miembros: (s) => s.miembros ? s.miembros.charAt(0).toUpperCase() + s.miembros.slice(1) : 'Socios',
    OrganoGobierno: (s) => s.organoGobierno ? s.organoGobierno.charAt(0).toUpperCase() + s.organoGobierno.slice(1) : 'Junta Directiva',
    OrganoGobiernoPl: (s) => s.organoGobiernoPl ? s.organoGobiernoPl.charAt(0).toUpperCase() + s.organoGobiernoPl.slice(1) : 'Juntas Directivas',
    temaActivo: (s) => s.temas.find(t => t.slug === s.tema) ?? null,
  },
  actions: {
    async fetchConfig() {
      if (this.loaded && this.temas.length) return
      try {
        const data = await graphqlClient.request(QUERY)
        this.initialized = data.appInitialized
        this.temas = (data.temasUi ?? []).filter(t => t.activo)
        const p = data.parametrosOrganizacion
        this.logo             = p.logo ?? ''
        this.nombre           = p.nombre ?? ''
        this.tipoAgrupacion   = p.tipoUnidadOrganizativa ?? ''
        this.miembro          = p.denominacionMiembro       ?? 'socio'
        this.miembros         = p.denominacionMiembroPlural ?? 'socios'
        this.organoGobierno   = p.denominacionOrganoGobierno       ?? 'junta directiva'
        this.organoGobiernoPl = p.denominacionOrganoGobiernoPlural ?? 'juntas directivas'
        this.sessionInactividad = p.sessionInactividadMinutos ?? 30
        this.sessionMaximo      = p.sessionMaximoMinutos ?? 480
        this.tema            = p.tema         ?? 'violeta'
        this.fuentePrincipal = p.fuentePrincipal ?? 'Inter'
        this.usaPresupuesto  = p.usaPresupuesto ?? false
        this.chatActivo      = p.chatActivo ?? false
        const temaObj = this.temas.find(t => t.slug === this.tema)
        this.applyTheme(temaObj ?? this.tema, this.fuentePrincipal)
        this.loaded = true
      } catch {
        // backend temporarily unavailable — leave initialized as null
      }
    },
    async refreshConfig() {
      this.loaded = false
      await this.fetchConfig()
    },
    async checkInitialized() {
      if (this.initialized !== null) return this.initialized
      await this.fetchConfig()
      return this.initialized ?? true
    },
    setLogo(logo) {
      this.logo = logo
    },
    setTemas(temas) {
      this.temas = temas
    },
    markInitialized(nombre, logo, tipoAgrupacion) {
      this.initialized = true
      this.nombre = nombre
      this.logo = logo
      if (tipoAgrupacion !== undefined) this.tipoAgrupacion = tipoAgrupacion
      this.loaded = true
    },
    // temaObj: full tema object from DB (camelCase fields) OR a slug string (fallback)
    applyTheme(temaObj, font) {
      const el = document.documentElement

      if (temaObj && typeof temaObj === 'object') {
        this.tema = temaObj.slug
        el.dataset.theme = temaObj.slug
        const vars = {
          '--t-50':      temaObj.t50,
          '--t-100':     temaObj.t100,
          '--t-200':     temaObj.t200,
          '--t-300':     temaObj.t300,
          '--t-400':     temaObj.t400,
          '--t-500':     temaObj.t500,
          '--t-600':     temaObj.t600,
          '--t-700':     temaObj.t700,
          '--t-800':     temaObj.t800,
          '--t-900':     temaObj.t900,
          '--t-sidebar': temaObj.sidebar,
          '--t-topbar':  temaObj.topbar,
          '--t-page-bg': temaObj.pageBg,
          '--t-card-bg': temaObj.cardBg,
          '--t-text-main':   temaObj.textMain,
          '--t-text-muted':  temaObj.textMuted,
          '--t-border':      temaObj.borderColor,
        }
        for (const [k, v] of Object.entries(vars)) {
          if (v) el.style.setProperty(k, v)
        }
      } else if (typeof temaObj === 'string') {
        this.tema = temaObj
        el.dataset.theme = temaObj
      }

      this.fuentePrincipal = font
      el.style.setProperty('--font-main', `'${font}', sans-serif`)
      if (font && font !== 'Inter') {
        const id = `gfont-${font.replace(/ /g, '-')}`
        if (!document.getElementById(id)) {
          const link = Object.assign(document.createElement('link'), {
            id, rel: 'stylesheet',
            href: `https://fonts.googleapis.com/css2?family=${font.replace(/ /g, '+')}:wght@400;500;600;700&display=swap`,
          })
          document.head.appendChild(link)
        }
      }
    },
    invalidate() {
      this.loaded = false
    },
  },
})
