<template>
  <AppLayout title="Estructura y órganos"
             subtitle="Niveles territoriales, denominaciones y órganos de gobierno">

    <div class="flex flex-col space-y-3 pb-4">

      <!-- 1. Estructura territorial (editor autónomo, con su propio radiogroup) -->
      <AccordionPanel title="Estructura territorial" :default-open="true">
        <div class="px-5 py-4">
          <EstructuraOrganizativaEditor :mostrar-radiogroup="true" />
        </div>
      </AccordionPanel>

      <!-- 2. Órgano de gobierno -->
      <AccordionPanel title="Órgano de gobierno" :default-open="true">
        <div class="px-5 py-4 space-y-4">
          <fieldset class="rounded-xl border border-slate-200 px-4 pt-2 pb-4">
            <legend class="px-1.5 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
              Denominación del órgano de gobierno (singular / plural)
            </legend>
            <div class="mt-1">
              <div class="flex items-center gap-2 max-w-xl">
                <input v-model="denominacionOrgano" type="text" class="input w-0 flex-1"
                       placeholder="junta directiva" maxlength="40" />
                <span class="text-slate-400 text-sm flex-shrink-0">/</span>
                <input v-model="denominacionOrganoPlural" type="text" class="input w-0 flex-1"
                       placeholder="juntas directivas" maxlength="40" />
              </div>
              <p class="mt-1 text-[11px] text-slate-400">p.ej. junta directiva · patronato · comité ejecutivo</p>
            </div>
          </fieldset>

          <div class="flex items-center gap-3">
            <button type="button" :disabled="guardando" @click="guardarOrgano"
              class="h-8 px-4 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors">
              {{ guardando ? 'Guardando…' : 'Guardar' }}
            </button>
            <span v-if="errorCarga" class="text-sm text-red-600">{{ errorCarga }}</span>
          </div>
        </div>
      </AccordionPanel>

    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import AccordionPanel from '@/components/common/AccordionPanel.vue'
import EstructuraOrganizativaEditor from '@/components/configuracion/EstructuraOrganizativaEditor.vue'
import { graphqlClient } from '@/graphql/client.js'
import { useOrgConfigStore } from '@/stores/orgConfig.js'
import { useToast } from '@/composables/useToast'

defineOptions({ name: 'EstructuraOrganizativa' })

const toast = useToast()
const orgConfigStore = useOrgConfigStore()

const denominacionOrgano = ref('')
const denominacionOrganoPlural = ref('')
const guardando = ref(false)
const errorCarga = ref('')

const QUERY_ORGANO = `
  query {
    parametrosOrganizacion {
      denominacionOrganoGobierno denominacionOrganoGobiernoPlural
    }
  }
`

const MUTATION_GUARDAR = `
  mutation GuardarParametros($datos: ParametrosOrganizacionInput!) {
    guardarParametrosOrganizacion(datos: $datos) {
      denominacionOrganoGobierno denominacionOrganoGobiernoPlural
    }
  }
`

onMounted(async () => {
  try {
    const data = await graphqlClient.request(QUERY_ORGANO)
    const p = data.parametrosOrganizacion
    denominacionOrgano.value       = p.denominacionOrganoGobierno       ?? 'junta directiva'
    denominacionOrganoPlural.value = p.denominacionOrganoGobiernoPlural ?? 'juntas directivas'
  } catch (e) {
    errorCarga.value = e?.response?.errors?.[0]?.message
      ?? 'No se pudieron cargar las denominaciones del órgano de gobierno.'
  }
})

async function guardarOrgano() {
  if (guardando.value) return
  guardando.value = true
  try {
    // Merge parcial en backend (los campos omitidos no se pisan): mandamos SOLO estas dos.
    await graphqlClient.request(MUTATION_GUARDAR, {
      datos: {
        denominacionOrganoGobierno:       denominacionOrgano.value,
        denominacionOrganoGobiernoPlural: denominacionOrganoPlural.value,
      }
    })
    await orgConfigStore.refreshConfig()
    toast.success('Denominación del órgano de gobierno guardada')
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message ?? 'Error al guardar')
  } finally {
    guardando.value = false
  }
}
</script>

<style scoped>
.input {
  @apply w-full h-10 rounded-lg border border-slate-300 px-3 text-sm text-slate-900
         placeholder:text-slate-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500
         focus:outline-none transition-colors bg-white;
}
</style>
