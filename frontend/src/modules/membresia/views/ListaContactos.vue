<template>
  <AppLayout title="Contactos" subtitle="Directorio de personas y entidades">
    <div class="p-4 sm:p-6 max-w-7xl mx-auto">
      <div class="flex items-center justify-end mb-4">
        <span class="text-sm text-slate-500">{{ contactosFiltrados.length }} de {{ contactos.length }}</span>
      </div>

    <!-- Filtros -->
    <div class="flex flex-wrap gap-2 mb-4">
      <input
        v-model="busqueda"
        type="text"
        placeholder="Buscar por nombre, razón social, email o documento…"
        class="flex-1 min-w-[14rem] px-3 py-2 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
      />
      <select v-model="filtroTipo" class="px-3 py-2 border border-slate-300 rounded-md text-sm bg-white">
        <option value="TODOS">Todos los tipos</option>
        <option value="PERSONA_FISICA">Personas físicas</option>
        <option value="PERSONA_JURIDICA">Personas jurídicas</option>
      </select>
      <select v-model="filtroFaceta" class="px-3 py-2 border border-slate-300 rounded-md text-sm bg-white">
        <option value="TODOS">Todas las vinculaciones</option>
        <option v-for="f in facetasDisponibles" :key="f.codigo" :value="f.codigo">{{ f.nombre }}</option>
      </select>
    </div>

    <!-- Estados -->
    <div v-if="cargando" class="text-center py-12 text-slate-400 text-sm">Cargando contactos…</div>
    <div v-else-if="error" class="rounded-md bg-red-50 border border-red-200 p-4 text-sm text-red-800">{{ error }}</div>
    <div v-else-if="!contactosFiltrados.length" class="text-center py-12 text-slate-400 text-sm">
      No hay contactos que coincidan con el filtro.
    </div>

    <!-- Tabla -->
    <div v-else class="overflow-x-auto border border-slate-200 rounded-lg">
      <table class="min-w-full divide-y divide-slate-200 text-sm">
        <thead class="bg-slate-50">
          <tr class="text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">
            <th class="px-4 py-3">Tipo</th>
            <th class="px-4 py-3">Nombre / Razón social</th>
            <th class="px-4 py-3">Documento</th>
            <th class="px-4 py-3">Contacto</th>
            <th class="px-4 py-3">Vinculaciones vigentes</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="c in contactosFiltrados" :key="c.id"
            class="hover:bg-purple-50 cursor-pointer"
            @click="abrirFicha(c.id)">
            <td class="px-4 py-3">
              <span
                class="inline-block px-2 py-0.5 rounded text-xs font-medium"
                :class="c.tipo === 'PERSONA_JURIDICA' ? 'bg-amber-100 text-amber-800' : 'bg-sky-100 text-sky-800'"
              >{{ c.tipo === 'PERSONA_JURIDICA' ? 'PJ' : 'PF' }}</span>
            </td>
            <td class="px-4 py-3 font-medium text-purple-700">
              {{ nombreMostrado(c) }}
            </td>
            <td class="px-4 py-3 text-slate-600">{{ c.numeroDocumento || c.cif || '—' }}</td>
            <td class="px-4 py-3 text-slate-600">
              <div>{{ c.email || '—' }}</div>
              <div class="text-xs text-slate-400">{{ c.telefono || '' }}</div>
            </td>
            <td class="px-4 py-3">
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="v in facetasVigentes(c)"
                  :key="v.id"
                  class="inline-block px-2 py-0.5 rounded text-xs font-medium"
                  :class="colorFaceta(v.tipoVinculacion && v.tipoVinculacion.codigo)"
                >{{ v.tipoVinculacion ? v.tipoVinculacion.nombre : '—' }}</span>
                <span v-if="!facetasVigentes(c).length" class="text-xs text-slate-400">sin vinculaciones</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import { graphqlClient } from '@/graphql/client.js'
import { GET_CONTACTOS } from '@/graphql/queries/contactos.js'

const router = useRouter()
function abrirFicha(id) {
  router.push(`/contactos/${id}`)
}

const contactos = ref([])
const cargando = ref(true)
const error = ref('')
const busqueda = ref('')
const filtroTipo = ref('TODOS')
const filtroFaceta = ref('TODOS')

const _COLORES = {
  SOCIO: 'bg-emerald-100 text-emerald-800',
  VOLUNTARIO: 'bg-purple-100 text-purple-800',
  DONANTE: 'bg-rose-100 text-rose-800',
  FIRMANTE: 'bg-slate-100 text-slate-700',
  SIMPATIZANTE: 'bg-indigo-100 text-indigo-800',
  EMPLEADO: 'bg-orange-100 text-orange-800',
}
function colorFaceta(codigo) {
  return _COLORES[codigo] || 'bg-slate-100 text-slate-700'
}

function nombreMostrado(c) {
  if (c.tipo === 'PERSONA_JURIDICA') return c.razonSocial || c.nombre || '—'
  return [c.nombre, c.apellido1, c.apellido2].filter(Boolean).join(' ') || '—'
}

// Vinculaciones vigentes = sin fecha de fin (la faceta está abierta).
function facetasVigentes(c) {
  return (c.vinculaciones || []).filter((v) => !v.fechaFin)
}

// Catálogo de facetas presentes, RELACIONADO con el tipo de persona elegido:
// solo se ofrecen las facetas que de hecho tienen contactos de ese tipo, de modo
// que no aparezcan combinaciones sin sentido (p.ej. una faceta solo de PF cuando
// se filtra por personas jurídicas).
const facetasDisponibles = computed(() => {
  const mapa = new Map()
  for (const c of contactos.value) {
    if (filtroTipo.value !== 'TODOS' && c.tipo !== filtroTipo.value) continue
    for (const v of facetasVigentes(c)) {
      const tv = v.tipoVinculacion
      if (tv && !mapa.has(tv.codigo)) mapa.set(tv.codigo, { codigo: tv.codigo, nombre: tv.nombre })
    }
  }
  return [...mapa.values()].sort((a, b) => a.nombre.localeCompare(b.nombre))
})

// Si al cambiar el tipo de persona la faceta elegida deja de tener sentido,
// se reinicia a "Todas".
watch(filtroTipo, () => {
  if (filtroFaceta.value !== 'TODOS' && !facetasDisponibles.value.some((f) => f.codigo === filtroFaceta.value)) {
    filtroFaceta.value = 'TODOS'
  }
})

const contactosFiltrados = computed(() => {
  const q = busqueda.value.trim().toLowerCase()
  return contactos.value.filter((c) => {
    if (filtroTipo.value !== 'TODOS' && c.tipo !== filtroTipo.value) return false
    if (filtroFaceta.value !== 'TODOS') {
      const tiene = facetasVigentes(c).some((v) => v.tipoVinculacion && v.tipoVinculacion.codigo === filtroFaceta.value)
      if (!tiene) return false
    }
    if (q) {
      const heno = [
        nombreMostrado(c), c.email, c.telefono, c.numeroDocumento, c.cif,
      ].filter(Boolean).join(' ').toLowerCase()
      if (!heno.includes(q)) return false
    }
    return true
  })
})

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const data = await graphqlClient.request(GET_CONTACTOS, {
      filter: { eliminado: { eq: false } },
    })
    contactos.value = data.contactos || []
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'No se pudieron cargar los contactos.'
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
</script>
