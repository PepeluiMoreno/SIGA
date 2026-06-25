<template>
  <AppLayout title="Ficha de contacto" :subtitle="esPJ ? 'Persona jurídica' : 'Persona física'">
    <div class="p-4 sm:p-6 max-w-6xl mx-auto">

      <div v-if="cargando" class="text-center py-12 text-slate-400 text-sm">Cargando ficha…</div>
      <div v-else-if="error" class="rounded-md bg-red-50 border border-red-200 p-4 text-sm text-red-800">{{ error }}</div>
      <div v-else-if="!contacto" class="text-center py-12 text-slate-400 text-sm">Contacto no encontrado.</div>

      <template v-else>
        <!-- Tarjeta de contacto (arriba a la derecha, estilo flowww) -->
        <div class="flex justify-end mb-4">
          <div class="flex items-center gap-3 bg-white border border-slate-200 rounded-lg px-4 py-2.5 shadow-sm">
            <AvatarImg :src="contacto.fotoUrl" :nombre="contacto.nombre" :apellido="contacto.apellido1" size="lg" shape="round" />
            <div class="text-sm leading-tight">
              <div class="font-medium text-slate-800">{{ titulo }}</div>
              <div class="text-slate-500">{{ contacto.telefono || contacto.email || '—' }}</div>
              <div class="flex items-center gap-2">
                <span v-if="numeroSocio" class="text-slate-400 text-xs">Nº {{ numeroSocio }}</span>
                <span v-if="!contacto.activo" class="text-xs text-red-600">inactivo</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Pestañas (mismo contenedor que la ficha de socio) -->
        <div class="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <TabsNavigation :tabs="tabs" :active-tab="tab" @tab-change="tab = $event" />

        <div class="p-5" style="background-color: var(--t-tabsheet-bg, #f1edfb)">
          <!-- TAB: Datos -->
          <div v-show="tab === 'datos'" class="flex flex-col sm:flex-row gap-6">
            <AvatarImg :src="contacto.fotoUrl" :nombre="contacto.nombre" :apellido="contacto.apellido1" size="2xl" shape="carnet" />
            <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-sm flex-1">
              <template v-if="esPJ">
                <Campo label="Razón social" :valor="contacto.razonSocial" />
                <Campo label="CIF" :valor="contacto.cif" />
                <Campo label="Actividad principal" :valor="contacto.actividadPrincipal" />
              </template>
              <template v-else>
                <Campo label="Nombre" :valor="[contacto.nombre, contacto.apellido1, contacto.apellido2].filter(Boolean).join(' ')" />
                <Campo label="Documento" :valor="docFmt" />
                <Campo label="Sexo" :valor="contacto.sexo" />
                <Campo label="Fecha de nacimiento" :valor="contacto.fechaNacimiento" />
                <Campo label="Profesión" :valor="contacto.profesion" />
              </template>
              <Campo label="Email" :valor="contacto.email" />
              <Campo label="Teléfono" :valor="contacto.telefono" />
              <Campo label="Dirección" :valor="[contacto.direccion, contacto.codigoPostal, contacto.localidad].filter(Boolean).join(', ')" />
            </dl>
          </div>

          <!-- TAB: Vinculaciones (datagrid) -->
          <div v-show="tab === 'vinculaciones'">
            <h2 class="text-sm font-semibold text-slate-700 mb-3">Vinculación con {{ nombreOrg }}</h2>
            <div v-if="!vinculaciones.length" class="text-sm text-slate-400">Sin vinculaciones registradas.</div>
            <table v-else class="min-w-full divide-y divide-slate-200 text-sm">
              <thead class="bg-slate-50">
                <tr class="text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">
                  <th class="px-4 py-2.5">Vinculación</th>
                  <th class="px-4 py-2.5">Desde</th>
                  <th class="px-4 py-2.5">Hasta</th>
                  <th class="px-4 py-2.5 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr
                  v-for="v in vinculaciones"
                  :key="v.id"
                  class="hover:bg-purple-50 cursor-pointer"
                  :class="vinculacionSel && vinculacionSel.id === v.id ? 'bg-purple-50' : ''"
                  @click="vinculacionSel = v"
                >
                  <td class="px-4 py-2.5">
                    <span class="inline-block px-2 py-0.5 rounded text-xs font-medium" :class="colorFaceta(v.tipoVinculacion && v.tipoVinculacion.codigo)">
                      {{ v.tipoVinculacion ? v.tipoVinculacion.nombre : '—' }}
                    </span>
                  </td>
                  <td class="px-4 py-2.5 text-slate-600">{{ v.fechaInicio || '—' }}</td>
                  <td class="px-4 py-2.5 text-slate-600">{{ v.fechaFin || 'vigente' }}</td>
                  <td class="px-4 py-2.5 text-right">
                    <button class="text-purple-600 hover:text-purple-800 text-xs font-medium" @click.stop="vinculacionSel = v">Ver</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- TAB: Historial -->
          <div v-show="tab === 'historial'">
            <HistorialVinculaciones :vinculaciones="vinculaciones" titulo="Trayectoria completa" />
          </div>
        </div>
        </div>
      </template>
    </div>

    <!-- Drawer: detalle de una vinculación -->
    <div v-if="vinculacionSel" class="fixed inset-0 z-40">
      <div class="absolute inset-0 bg-black/30" @click="vinculacionSel = null"></div>
      <aside class="absolute right-0 top-0 h-full w-full max-w-md bg-white shadow-xl p-5 overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-base font-semibold text-slate-800">Detalle de vinculación</h3>
          <button class="text-slate-400 hover:text-slate-600 text-xl leading-none" @click="vinculacionSel = null">×</button>
        </div>
        <div class="flex items-center gap-2 mb-4">
          <span class="inline-block px-2 py-0.5 rounded text-xs font-medium" :class="colorFaceta(vinculacionSel.tipoVinculacion && vinculacionSel.tipoVinculacion.codigo)">
            {{ vinculacionSel.tipoVinculacion ? vinculacionSel.tipoVinculacion.nombre : '—' }}
          </span>
          <span class="text-xs text-slate-500">{{ vinculacionSel.fechaInicio || '?' }} → {{ vinculacionSel.fechaFin || 'vigente' }} ({{ vinculacionSel.estado }})</span>
        </div>
        <dl v-if="vinculacionSel.socio" class="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
          <Campo label="Nº socio" :valor="vinculacionSel.socio.numeroSocio" />
          <Campo label="Situación" :valor="vinculacionSel.socio.estadoSocio" />
          <Campo label="Cuota" :valor="vinculacionSel.socio.cuotaMensual != null ? vinculacionSel.socio.cuotaMensual + ' €' : null" />
          <Campo label="IBAN" :valor="vinculacionSel.socio.iban" />
          <Campo label="Honor" :valor="vinculacionSel.socio.esHonor ? 'Sí' : null" />
        </dl>
        <dl v-else-if="vinculacionSel.voluntario" class="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
          <Campo label="Disponibilidad" :valor="vinculacionSel.voluntario.disponibilidad" />
          <Campo label="Horas/semana" :valor="vinculacionSel.voluntario.horasDisponiblesSemana" />
          <Campo label="Intereses" :valor="vinculacionSel.voluntario.intereses" />
          <Campo label="Conduce" :valor="vinculacionSel.voluntario.puedeConducir ? 'Sí' : null" />
          <Campo label="Vehículo propio" :valor="vinculacionSel.voluntario.vehiculoPropio ? 'Sí' : null" />
        </dl>
        <p v-else class="text-sm text-slate-400">Esta vinculación no tiene datos adicionales.</p>
      </aside>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import AvatarImg from '@/components/common/AvatarImg.vue'
import TabsNavigation from '@/components/common/TabsNavigation.vue'
import HistorialVinculaciones from '@/components/miembros/HistorialVinculaciones.vue'
import { useOrgConfigStore } from '@/stores/orgConfig.js'
import { graphqlClient } from '@/graphql/client.js'
import { GET_CONTACTO, VINCULACIONES_DE_CONTACTO } from '@/graphql/queries/contactos.js'

const Campo = (props) => h('div', {}, [
  h('dt', { class: 'text-xs text-slate-400' }, props.label),
  h('dd', { class: 'text-slate-800' }, props.valor != null && props.valor !== '' ? String(props.valor) : '—'),
])
Campo.props = ['label', 'valor']

const route = useRoute()
const orgConfig = useOrgConfigStore()
const contacto = ref(null)
const vinculaciones = ref([])
const cargando = ref(true)
const error = ref('')
const tab = ref('datos')
const vinculacionSel = ref(null)

const tabs = [
  { id: 'datos', name: 'Datos', icon: '👤' },
  { id: 'vinculaciones', name: 'Vinculaciones', icon: '🔗' },
  { id: 'historial', name: 'Historial', icon: '🕘' },
]

const _COLORES = {
  SOCIO: 'bg-emerald-100 text-emerald-800',
  SOCIO_ASPIRANTE: 'bg-yellow-100 text-yellow-800',
  VOLUNTARIO: 'bg-purple-100 text-purple-800',
  DONANTE: 'bg-rose-100 text-rose-800',
  FIRMANTE: 'bg-slate-100 text-slate-700',
  SIMPATIZANTE: 'bg-indigo-100 text-indigo-800',
  EMPLEADO: 'bg-orange-100 text-orange-800',
}
function colorFaceta(codigo) { return _COLORES[codigo] || 'bg-slate-100 text-slate-700' }

const nombreOrg = computed(() => orgConfig.nombre || 'la asociación')
const esPJ = computed(() => contacto.value?.tipo === 'PERSONA_JURIDICA')
const titulo = computed(() => {
  const c = contacto.value
  if (!c) return 'Contacto'
  return esPJ.value ? (c.razonSocial || c.nombre) : [c.nombre, c.apellido1, c.apellido2].filter(Boolean).join(' ')
})
const docFmt = computed(() => {
  const c = contacto.value
  return c ? ([c.tipoDocumento, c.numeroDocumento].filter(Boolean).join(' ') || null) : null
})
const numeroSocio = computed(() => {
  const v = vinculaciones.value.find((x) => x.socio && x.socio.numeroSocio)
  return v ? v.socio.numeroSocio : null
})

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const id = route.params.id
    const data = await graphqlClient.request(GET_CONTACTO, { id })
    contacto.value = (data.contactos || [])[0] || null
    if (contacto.value) {
      const vd = await graphqlClient.request(VINCULACIONES_DE_CONTACTO, { contactoId: id })
      vinculaciones.value = vd.vinculacionesDeContacto || []
    }
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'No se pudo cargar la ficha.'
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
</script>
