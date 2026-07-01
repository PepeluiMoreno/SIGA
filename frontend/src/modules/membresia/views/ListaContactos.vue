<template>
  <AppLayout :title="tituloVista" :subtitle="subtitulo" fluid>
    <template v-if="tienePermiso('CONTACTO_CREAR')" #actions>
      <router-link :to="altaTo"
        class="inline-flex items-center gap-1.5 h-8 px-3 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors">
        <span class="text-base leading-none">+</span>
        Nuevo
      </router-link>
    </template>

    <!-- Patrón general: filtro lateral colapsable (FilterRail) + resultados -->
    <div class="flex flex-col lg:flex-row gap-4 items-start">
      <FilterRail storage-key="contactos">
        <FilterBar
          vertical
          v-model="filters"
          v-model:search="searchQuery"
          search-placeholder="Buscar por nombre, razón social, email o documento…"
          :fields="filterFields"
          @clear="limpiarFiltros" />
        <!-- Buscador geográfico: filtra por municipio/provincia -->
        <div class="mt-3 pt-3 border-t border-slate-100">
          <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">Ubicación</p>
          <EntidadGeograficaSelect v-model="filtroGeografico" :editing="true" :niveles="[2, 3]" />
        </div>
      </FilterRail>

      <!-- Columna de resultados -->
      <div class="flex-1 min-w-0 w-full">
        <div class="flex items-center justify-end mb-3">
          <span class="text-sm text-slate-500">{{ contactosFiltrados.length }} de {{ contactos.length }}</span>
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
                <th class="px-4 py-3">Nombre / Razón social</th>
                <th class="px-4 py-3">Documento</th>
                <th class="px-4 py-3">Contacto</th>
                <th class="px-4 py-3 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="c in contactosFiltrados" :key="c.id"
                class="hover:bg-purple-50 cursor-pointer"
                @click="abrirFicha(c.id)">
                <td class="px-4 py-3">
                  <div class="flex flex-wrap items-center gap-1.5">
                    <span class="font-medium text-purple-700">{{ nombreMostrado(c) }}</span>
                    <!-- Solo las personas jurídicas se etiquetan; las físicas no llevan badge de tipo -->
                    <span v-if="c.tipo === 'PERSONA_JURIDICA'"
                      class="inline-block px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800">Persona jurídica</span>
                    <!-- Badges de vinculación + condiciones derivadas, tras el nombre -->
                    <span
                      v-for="v in vinculacionesVigentes(c)"
                      :key="v.id"
                      class="inline-block px-2 py-0.5 rounded text-xs font-medium"
                      :class="colorVinculacion(v.tipoVinculacion && v.tipoVinculacion.codigo)"
                    >{{ v.tipoVinculacion ? v.tipoVinculacion.nombre : '—' }}</span>
                    <span v-if="condicionesDe(c.id).esParticipante" class="inline-block px-2 py-0.5 rounded text-xs font-medium bg-sky-100 text-sky-700">Participante</span>
                    <span v-if="condicionesDe(c.id).esDonante" class="inline-block px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-700">Donante</span>
                  </div>
                </td>
                <td class="px-4 py-3 text-slate-600">{{ c.numeroDocumento || c.cif || '—' }}</td>
                <td class="px-4 py-3 text-slate-600">
                  <div>{{ c.email || '—' }}</div>
                  <div class="text-xs text-slate-400">{{ c.telefono || '' }}</div>
                </td>
                <td class="px-4 py-3">
                  <RowActions show-view
                    :show-edit="tienePermiso('CONTACTO_EDITAR')"
                    :show-delete="tienePermiso('CONTACTO_ELIMINAR')"
                    @view="abrirFicha(c.id)"
                    @edit="abrirFicha(c.id)"
                    @delete="eliminarContacto(c)" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import FilterRail from '@/components/common/FilterRail.vue'
import RowActions from '@/components/common/RowActions.vue'
import EntidadGeograficaSelect from '@/components/common/EntidadGeograficaSelect.vue'
import { useToast } from '@/composables/useToast'
import { useOrgConfigStore } from '@/stores/orgConfig.js'
import { usePermisos } from '@/composables/usePermisos.js'
import { graphqlClient } from '@/graphql/client.js'
import { GET_CONTACTOS, GET_CONDICIONES_CONTACTOS, ELIMINAR_CONTACTO } from '@/graphql/queries/contactos.js'

// `colectivo` fija esta vista a un subconjunto del directorio (escisión de Contactos):
//  - SOCIOS: contactos con vinculación SOCIO vigente (excluye aspirantes).
//  - PERSONAL: colectivo de servicio (EMPLEADO/AUTONOMO/EMPLEADO_EXTERNO).
//  - null / CONTACTOS: el resto (sin afiliación de socio ni de servicio): participación,
//    simpatizantes, organizaciones amigas y contactos sueltos.
const props = defineProps({
  colectivo: { type: String, default: null },  // 'SOCIO' | 'PERSONAL' | null
})

const COLECTIVO_SOCIO = ['SOCIO']
const COLECTIVO_PERSONAL = ['EMPLEADO', 'AUTONOMO', 'EMPLEADO_EXTERNO']
const TITULOS = {
  SOCIO:    { titulo: 'Socios',     sub: 'Personas con vinculación de socio' },
  PERSONAL: { titulo: 'Personal',   sub: 'Personal contratado y colaborador de servicio' },
}

const router = useRouter()
const { tienePermiso } = usePermisos()
const orgConfig = useOrgConfigStore()
const tituloVista = computed(() => TITULOS[props.colectivo]?.titulo || 'Contactos')
const subtitulo = computed(() => TITULOS[props.colectivo]?.sub ||
  `Directorio de personas y entidades relacionadas de algún modo con ${orgConfig.nombre || 'la asociación'}`)

// Alta según el colectivo de la vista. El botón dice siempre "Nuevo" (el título de
// la vista ya da el contexto); solo cambia la ruta de destino: en Socios se da de
// alta un socio (vista de miembro), en Personal/Contactos un contacto.
const altaTo = computed(() => (props.colectivo === 'SOCIO' ? '/miembros/nuevo' : '/contactos/nuevo'))

// Códigos de vinculación de socio/personal (para clasificar cada contacto).
function codigosVigentes(c) {
  return vinculacionesVigentes(c).map(v => v.tipoVinculacion?.codigo).filter(Boolean)
}
function esColectivo(c, codigos) {
  const cods = codigosVigentes(c)
  return codigos.some(x => cods.includes(x))
}
function abrirFicha(id) {
  // Un socio abre su ficha de socio (DetalleMiembro); el resto, la ficha de contacto.
  router.push(props.colectivo === 'SOCIO' ? `/miembros/${id}` : `/contactos/${id}`)
}

const toast = useToast()
// Borrado desde la fila. RowActions ya pide confirmación; aquí solo se ejecuta.
async function eliminarContacto(c) {
  try {
    await graphqlClient.request(ELIMINAR_CONTACTO, { id: c.id })
    contactos.value = contactos.value.filter(x => x.id !== c.id)
    toast.success('Contacto eliminado.')
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'No se pudo eliminar el contacto')
  }
}

const contactos = ref([])
const cargando = ref(true)
const error = ref('')

const searchQuery = ref('')
const filters = ref({ tipos: [], vinculaciones: [] })
const filtroGeografico = ref(null)   // entidad geográfica (municipio/provincia)

const _COLORES = {
  SOCIO: 'bg-emerald-100 text-emerald-800',
  VOLUNTARIO: 'bg-purple-100 text-purple-800',
  DONANTE: 'bg-rose-100 text-rose-800',
  FIRMANTE: 'bg-slate-100 text-slate-700',
  SIMPATIZANTE: 'bg-indigo-100 text-indigo-800',
  EMPLEADO: 'bg-orange-100 text-orange-800',
}
function colorVinculacion(codigo) {
  return _COLORES[codigo] || 'bg-slate-100 text-slate-700'
}

function nombreMostrado(c) {
  if (c.tipo === 'PERSONA_JURIDICA') return c.razonSocial || c.nombre || '—'
  return [c.nombre, c.apellido1, c.apellido2].filter(Boolean).join(' ') || '—'
}

// Vinculaciones vigentes = sin fecha de fin (la vinculación está abierta).
function vinculacionesVigentes(c) {
  return (c.vinculaciones || []).filter((v) => !v.fechaFin)
}

// Opciones de vinculación por vista. Un socio puede acumular condiciones
// (donante/voluntario/firmante); en Contactos (cajón mixto) además simpatizante.
const OPCIONES_VINC_SOCIO = [
  { value: 'DONANTE', label: 'Donantes' },
  { value: 'VOLUNTARIO', label: 'Voluntarios' },
  { value: 'FIRMANTE', label: 'Firmantes' },
]
const OPCIONES_VINC_CONTACTOS = [
  { value: 'DONANTE', label: 'Donante' },
  { value: 'FIRMANTE', label: 'Firmante' },
  { value: 'SIMPATIZANTE', label: 'Simpatizante' },
]

const filterFields = computed(() => {
  const campos = []
  // El tipo de persona (física/jurídica) solo aporta en el cajón mixto de Contactos
  // y en Personal; en Socios lo relevante es la vinculación/condición.
  if (props.colectivo !== 'SOCIO') {
    campos.push({
      key: 'tipos',
      label: 'Tipo de persona',
      type: 'multiselect',
      options: [
        { value: 'PERSONA_FISICA', label: 'Personas físicas' },
        { value: 'PERSONA_JURIDICA', label: 'Personas jurídicas' },
      ],
      allLabel: 'Todos los tipos',
      width: 'w-56',
    })
  }
  // Filtro por vinculación: en Socios (condiciones acumuladas) y en Contactos
  // (cajón mixto). En Personal el colectivo es fijo (contratado): no aplica.
  if (props.colectivo === 'SOCIO' || !props.colectivo) {
    campos.push({
      key: 'vinculaciones',
      label: 'Vinculación',
      type: 'multiselect',
      options: props.colectivo === 'SOCIO' ? OPCIONES_VINC_SOCIO : OPCIONES_VINC_CONTACTOS,
      allLabel: 'Cualquier vinculación',
      width: 'w-56',
    })
  }
  return campos
})

// El filtro de vinculación de la vista Contactos es fijo (Donante/Firmante/
// Simpatizante); no depende del tipo de persona, así que no hay que depurarlo.

function limpiarFiltros() {
  filters.value = { tipos: [], vinculaciones: [] }
  searchQuery.value = ''
  filtroGeografico.value = null
}

const contactosFiltrados = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  return contactos.value.filter((c) => {
    // Escisión por colectivo:
    if (props.colectivo === 'SOCIO' && !esColectivo(c, COLECTIVO_SOCIO)) return false
    if (props.colectivo === 'PERSONAL' && !esColectivo(c, COLECTIVO_PERSONAL)) return false
    // Vista "Contactos" (colectivo null): excluye socios y personal (esos tienen su vista).
    if (!props.colectivo && (esColectivo(c, COLECTIVO_SOCIO) || esColectivo(c, COLECTIVO_PERSONAL))) return false
    if (filters.value.tipos.length && !filters.value.tipos.includes(c.tipo)) return false
    if (filtroGeografico.value && c.entidadGeograficaId !== filtroGeografico.value) return false
    if (filters.value.vinculaciones.length) {
      // DONANTE/FIRMANTE son condiciones DERIVADAS (participación/donación);
      // VOLUNTARIO/SIMPATIZANTE son vinculaciones formales. Un contacto pasa si
      // cumple cualquiera de las seleccionadas (OR).
      const cond = condicionesDe(c.id)
      const codsVinc = new Set(vinculacionesVigentes(c).map((v) => v.tipoVinculacion?.codigo).filter(Boolean))
      const cumple = filters.value.vinculaciones.some((sel) => {
        if (sel === 'DONANTE') return cond.esDonante
        if (sel === 'FIRMANTE') return cond.esFirmante
        return codsVinc.has(sel)   // VOLUNTARIO, SIMPATIZANTE (u otra vinculación formal)
      })
      if (!cumple) return false
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

// Condiciones derivadas (firmante/participante/donante) por contacto, en batch.
const condicionesMap = ref({})
const SIN_COND = { esParticipante: false, esFirmante: false, esDonante: false }
function condicionesDe(id) {
  return condicionesMap.value[id] || SIN_COND
}
async function cargarCondiciones(ids) {
  if (!ids.length) { condicionesMap.value = {}; return }
  try {
    const data = await graphqlClient.request(GET_CONDICIONES_CONTACTOS, { contactoIds: ids })
    const map = {}
    for (const it of (data.condicionesContactos || [])) map[it.contactoId] = it
    condicionesMap.value = map
  } catch (e) { /* silencioso: los badges son informativos */ }
}

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const data = await graphqlClient.request(GET_CONTACTOS, {
      filter: { eliminado: { eq: false } },
    })
    contactos.value = data.contactos || []
    cargarCondiciones(contactos.value.map((c) => c.id))
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'No se pudieron cargar los contactos.'
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
</script>
