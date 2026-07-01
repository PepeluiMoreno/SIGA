<template>
  <AppLayout title="Nuevo grupo de trabajo" subtitle="Crear un nuevo equipo">
    <template #actions>
      <FormActions submit-text="Crear grupo" :loading="guardando"
        :disabled="!form.nombre || !form.tipoGrupoId || !form.agrupacionId"
        @cancel="$router.push('/grupos')" @submit="guardar" />
    </template>

    <div class="w-full">
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
          <SelectorAgrupacion v-model="form.agrupacionId" :agrupaciones="agrupaciones" />
          <p class="mt-1 text-xs text-slate-400">Fija el ámbito del que se eligen los integrantes: no podrá entrar quien pertenezca a otra agrupación.</p>
          <!-- Aviso: la agrupación elegida no tiene coordinador/cargo nombrado -->
          <div v-if="form.agrupacionId && !agrupacionTieneCoordinador"
            class="mt-2 flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
            <ExclamationTriangleIcon class="w-4 h-4 mt-0.5 shrink-0" />
            <span>Esta agrupación territorial no tiene coordinador nombrado. Puedes crear el grupo igualmente y designar su coordinador entre los integrantes.</span>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Coordinador del grupo</label>
          <select v-model="form.coordinadorId" :disabled="!form.agrupacionId"
            class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-slate-50 disabled:text-slate-400">
            <option value="">{{ form.agrupacionId ? (candidatos.length ? 'Sin designar de momento' : 'No hay candidatos en este ámbito') : 'Elige antes la agrupación' }}</option>
            <option v-for="c in candidatos" :key="c.id" :value="c.id">
              {{ c.nombre }} {{ c.apellido1 || '' }} — {{ colectivoLabel(c.colectivo) }}
            </option>
          </select>
          <p class="mt-1 text-xs text-slate-400">Se elige entre los candidatos del ámbito de la agrupación. También podrás designarlo después entre los miembros.</p>
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

      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import AppLayout from '@/components/common/AppLayout.vue'
import FormActions from '@/components/common/FormActions.vue'
import SelectorAgrupacion from '@/components/common/SelectorAgrupacion.vue'
import { graphqlClient } from '@/graphql/client'
import { GET_TIPOS_GRUPO } from '@/modules/actividades/graphql/grupos.js'

// Resolver manual con validación de tipo_grupo_id (evita el IntegrityError NOT NULL).
const GQL_CREAR_GRUPO = `
  mutation CrearGrupoTrabajoSeguro(
    $nombre: String!
    $tipoGrupoId: UUID
    $agrupacionId: UUID
    $coordinadorId: UUID
    $descripcion: String
    $objetivo: String
    $fechaInicio: Date
    $fechaFin: Date
  ) {
    crearGrupoTrabajoSeguro(
      nombre: $nombre
      tipoGrupoId: $tipoGrupoId
      agrupacionId: $agrupacionId
      coordinadorId: $coordinadorId
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
    unidadesOrganizativas {
      id nombre activo agrupacionPadreId
      tipoUnidad { id nombre }
    }
    coordinacionesTerritoriales {
      agrupacionId
    }
  }
`

const GQL_CANDIDATOS = `
  query CandidatosParaGrupoAlta($agrupacionId: UUID) {
    candidatosGrupo(agrupacionId: $agrupacionId) {
      id nombre apellido1 colectivo
    }
  }
`

const router = useRouter()
const tipos = ref([])
const agrupaciones = ref([])
const coordinaciones = ref([])   // agrupaciones con coordinador nombrado
const candidatos = ref([])
const guardando = ref(false)
const error = ref('')

const form = ref({
  nombre: '',
  tipoGrupoId: '',
  agrupacionId: null,
  coordinadorId: '',
  descripcion: '',
  objetivo: '',
  fechaInicio: '',
  fechaFin: '',
})

// ¿La agrupación elegida tiene coordinador/cargo territorial nombrado?
const agrupacionTieneCoordinador = computed(() =>
  !!form.value.agrupacionId &&
  coordinaciones.value.some(c => c.agrupacionId === form.value.agrupacionId)
)

const COLECTIVO_LABEL = { VOLUNTARIO: 'Voluntario', CONTRATADO: 'Contratado', COORDINADOR: 'Coord. de campaña' }
const colectivoLabel = (c) => COLECTIVO_LABEL[c] || c

// Al cambiar la agrupación, recargar candidatos del ámbito y limpiar el coordinador.
watch(() => form.value.agrupacionId, async (agrId) => {
  form.value.coordinadorId = ''
  candidatos.value = []
  if (!agrId) return
  try {
    const data = await graphqlClient.request(GQL_CANDIDATOS, { agrupacionId: agrId })
    candidatos.value = data.candidatosGrupo ?? []
  } catch { candidatos.value = [] }
})

onMounted(async () => {
  const [dataTipos, dataAgr] = await Promise.all([
    graphqlClient.request(GET_TIPOS_GRUPO),
    graphqlClient.request(GQL_AGRUPACIONES),
  ])
  tipos.value = (dataTipos.tiposGrupo ?? []).filter(t => t.activo)
  agrupaciones.value = (dataAgr.unidadesOrganizativas ?? []).filter(a => a.activo !== false)
  coordinaciones.value = dataAgr.coordinacionesTerritoriales ?? []
})

async function guardar() {
  error.value = ''
  guardando.value = true
  try {
    const vars = {
      nombre: form.value.nombre,
      tipoGrupoId: form.value.tipoGrupoId || null,
      agrupacionId: form.value.agrupacionId || null,
      coordinadorId: form.value.coordinadorId || null,
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
