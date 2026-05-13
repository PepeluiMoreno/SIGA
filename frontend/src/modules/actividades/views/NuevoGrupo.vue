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
          <label class="block text-sm font-medium text-slate-700 mb-1">Descripción</label>
          <textarea v-model="form.descripcion" rows="3"
            class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Objetivo</label>
          <textarea v-model="form.objetivo" rows="2"
            class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" />
        </div>

        <div class="grid grid-cols-2 gap-4">
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

        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

        <div class="flex justify-end gap-3 pt-2 border-t border-slate-100">
          <router-link to="/grupos"
            class="px-4 py-2 text-sm text-slate-600 border border-slate-300 rounded-lg hover:bg-slate-50">
            Cancelar
          </router-link>
          <button @click="guardar" :disabled="guardando || !form.nombre || !form.tipoGrupoId"
            class="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50">
            {{ guardando ? 'Guardando…' : 'Crear grupo' }}
          </button>
        </div>

      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import { graphqlClient } from '@/graphql/client'
import { GET_TIPOS_GRUPO } from '@/modules/actividades/graphql/grupos.js'

const GQL_CREAR_GRUPO = `
  mutation CrearGrupoTrabajo($data: GrupoTrabajoCreateInput!) {
    crearGrupoTrabajo(data: $data) {
      id
      nombre
    }
  }
`

const router = useRouter()
const tipos = ref([])
const guardando = ref(false)
const error = ref('')

const form = ref({
  nombre: '',
  tipoGrupoId: '',
  descripcion: '',
  objetivo: '',
  fechaInicio: '',
  fechaFin: '',
})

onMounted(async () => {
  const data = await graphqlClient.request(GET_TIPOS_GRUPO)
  tipos.value = (data.tiposGrupo ?? []).filter(t => t.activo)
})

async function guardar() {
  error.value = ''
  guardando.value = true
  try {
    const data = {
      nombre: form.value.nombre,
      tipoGrupoId: form.value.tipoGrupoId,
      descripcion: form.value.descripcion || null,
      objetivo: form.value.objetivo || null,
      fechaInicio: form.value.fechaInicio || null,
      fechaFin: form.value.fechaFin || null,
      activo: true,
    }
    const res = await graphqlClient.request(GQL_CREAR_GRUPO, { data })
    router.push(`/grupos/${res.crearGrupoTrabajo.id}`)
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message ?? 'Error al crear el grupo'
  } finally {
    guardando.value = false
  }
}
</script>
