<template>
  <AppLayout title="Nuevo grupo de trabajo" subtitle="Crear un nuevo equipo">
    <div class="max-w-2xl mx-auto">
      <div class="bg-white rounded-lg shadow p-6 space-y-5">

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Nombre <span class="text-red-500">*</span></label>
          <input v-model="form.nombre" type="text" maxlength="200"
            class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Tipo de grupo <span class="text-red-500">*</span></label>
          <select v-model="form.tipoGrupoId"
            class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <option value="">Seleccionar tipo…</option>
            <option v-for="t in tipos" :key="t.id" :value="t.id">{{ t.nombre }}</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Agrupación territorial <span class="text-red-500">*</span></label>
          <select v-model="form.agrupacionId"
            class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <option value="">Seleccionar agrupación…</option>
            <option v-for="a in agrupaciones" :key="a.id" :value="a.id">{{ a.nombre }}</option>
          </select>
          <p class="mt-1 text-xs text-slate-400">Fija el ámbito del que se eligen los integrantes: no podrá entrar quien pertenezca a otra agrupación.</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Descripción</label>
          <textarea v-model="form.descripcion" rows="3"
            class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Objetivo</label>
          <textarea v-model="form.objetivo" rows="2"
            class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Fecha inicio</label>
            <input v-model="form.fechaInicio" type="date"
              class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Fecha fin</label>
            <input v-model="form.fechaFin" type="date"
              class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
        </div>

        <ErrorAlert v-if="error" :message="error" />

        <div class="flex justify-end gap-3 pt-2 border-t border-slate-100">
          <router-link to="/grupos"
            class="px-4 py-2 text-sm text-slate-600 border border-slate-300 rounded-lg hover:bg-slate-50">
            Cancelar
          </router-link>
          <button @click="guardar" :disabled="guardando || !form.nombre || !form.tipoGrupoId || !form.agrupacionId"
            class="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50">
            {{ guardando ? 'Guardando…' : 'Crear grupo' }}
          </button>
        </div>

      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import { graphqlClient } from '@/graphql/client'
import { GET_TIPOS_GRUPO } from '@/modules/actividades/graphql/grupos.js'

// Resolver manual con validación de tipo_grupo_id (evita el IntegrityError NOT NULL).
const GQL_CREAR_GRUPO = `
  mutation CrearGrupoTrabajoSeguro(
    $nombre: String!
    $tipoGrupoId: UUID
    $agrupacionId: UUID
    $descripcion: String
    $objetivo: String
    $fechaInicio: Date
    $fechaFin: Date
  ) {
    crearGrupoTrabajoSeguro(
      nombre: $nombre
      tipoGrupoId: $tipoGrupoId
      agrupacionId: $agrupacionId
      descripcion: $descripcion
      objetivo: $objetivo
      fechaInicio: $fechaInicio
      fechaFin: $fechaFin
    ) {
      id
      nombre
    }
  }
`

const GQL_AGRUPACIONES = `
  query AgrupacionesParaGrupo {
    unidadesOrganizativas { id nombre activo }
  }
`

const router = useRouter()
const tipos = ref([])
const agrupaciones = ref([])
const guardando = ref(false)
const error = ref('')

const form = ref({
  nombre: '',
  tipoGrupoId: '',
  agrupacionId: '',
  descripcion: '',
  objetivo: '',
  fechaInicio: '',
  fechaFin: '',
})

onMounted(async () => {
  const [dataTipos, dataAgr] = await Promise.all([
    graphqlClient.request(GET_TIPOS_GRUPO),
    graphqlClient.request(GQL_AGRUPACIONES),
  ])
  tipos.value = (dataTipos.tiposGrupo ?? []).filter(t => t.activo)
  agrupaciones.value = (dataAgr.unidadesOrganizativas ?? []).filter(a => a.activo !== false)
})

async function guardar() {
  error.value = ''
  guardando.value = true
  try {
    const vars = {
      nombre: form.value.nombre,
      tipoGrupoId: form.value.tipoGrupoId || null,
      agrupacionId: form.value.agrupacionId || null,
      descripcion: form.value.descripcion || null,
      objetivo: form.value.objetivo || null,
      fechaInicio: form.value.fechaInicio || null,
      fechaFin: form.value.fechaFin || null,
    }
    const res = await graphqlClient.request(GQL_CREAR_GRUPO, vars)
    router.push(`/grupos/${res.crearGrupoTrabajoSeguro.id}`)
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message ?? 'Error al crear el grupo'
  } finally {
    guardando.value = false
  }
}
</script>
