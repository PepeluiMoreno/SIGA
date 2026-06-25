<template>
  <AppDrawer
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :title="titulo"
    :subtitle="subtitulo"
    size="xl"
    storage-key="ficha-contacto"
  >
    <div v-if="cargando" class="text-center py-12 text-slate-400 text-sm">Cargando ficha…</div>
    <div v-else-if="error" class="rounded-md bg-red-50 border border-red-200 p-4 text-sm text-red-800">{{ error }}</div>

    <template v-else-if="contacto">
      <!-- Cabecera compacta: foto + identidad -->
      <div class="flex items-start gap-4 mb-5">
        <AvatarImg :src="contacto.fotoUrl" :nombre="contacto.nombre" :apellido="contacto.apellido1" size="xl" shape="carnet" />
        <div class="min-w-0">
          <h3 class="text-lg font-semibold text-slate-900 truncate">{{ titulo }}</h3>
          <div class="mt-1 flex flex-wrap items-center gap-1.5">
            <span class="inline-block px-2 py-0.5 rounded text-xs font-medium"
              :class="esPJ ? 'bg-amber-100 text-amber-800' : 'bg-sky-100 text-sky-800'">
              {{ esPJ ? 'Persona jurídica' : 'Persona física' }}
            </span>
            <span v-if="numeroSocio" class="text-xs text-slate-400">Nº {{ numeroSocio }}</span>
            <span v-if="!contacto.activo" class="text-xs text-red-600">inactivo</span>
          </div>
          <p v-if="contacto.email || contacto.telefono" class="mt-1.5 text-sm text-slate-500">
            {{ [contacto.email, contacto.telefono].filter(Boolean).join(' · ') }}
          </p>
        </div>
      </div>

      <!-- Pestañas -->
      <TabsNavigation :tabs="tabs" :active-tab="tab" @tab-change="tab = $event" />

      <div class="pt-5">
        <!-- TAB: Datos -->
        <dl v-show="tab === 'datos'" class="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-3.5">
          <template v-if="esPJ">
            <Campo label="Razón social" :valor="contacto.razonSocial" />
            <Campo label="CIF" :valor="contacto.cif" />
            <Campo label="Actividad principal" :valor="contacto.actividadPrincipal" />
          </template>
          <template v-else>
            <Campo label="Documento" :valor="docFmt" />
            <Campo label="Sexo" :valor="contacto.sexo" />
            <Campo label="Fecha de nacimiento" :valor="contacto.fechaNacimiento" />
            <Campo label="Profesión" :valor="contacto.profesion" />
          </template>
          <Campo label="Email" :valor="contacto.email" />
          <Campo label="Teléfono" :valor="contacto.telefono" />
          <Campo class="sm:col-span-2" label="Dirección"
            :valor="[contacto.direccion, contacto.codigoPostal, contacto.localidad].filter(Boolean).join(', ')" />
        </dl>

        <!-- TAB: Vinculaciones -->
        <div v-show="tab === 'vinculaciones'">
          <div v-if="!vinculaciones.length" class="text-sm text-slate-400 py-2">Sin vinculaciones registradas.</div>
          <ul v-else class="divide-y divide-slate-100">
            <li v-for="v in vinculaciones" :key="v.id" class="py-2.5">
              <button class="w-full flex items-center justify-between gap-3 text-left group"
                @click="expandida = expandida === v.id ? null : v.id">
                <span class="flex items-center gap-2 min-w-0">
                  <span class="inline-block px-2 py-0.5 rounded text-xs font-medium shrink-0"
                    :class="colorFaceta(v.tipoVinculacion && v.tipoVinculacion.codigo)">
                    {{ v.tipoVinculacion ? v.tipoVinculacion.nombre : '—' }}
                  </span>
                  <span class="text-xs text-slate-500 truncate">
                    {{ v.fechaInicio || '?' }} → {{ v.fechaFin || 'vigente' }}
                  </span>
                </span>
                <ChevronDownIcon class="w-4 h-4 text-slate-400 transition-transform shrink-0"
                  :class="expandida === v.id ? 'rotate-180' : ''" />
              </button>

              <!-- Detalle satélite inline -->
              <dl v-if="expandida === v.id && v.socio"
                class="mt-2 ml-1 grid grid-cols-2 gap-x-6 gap-y-2 rounded-lg bg-slate-50 border border-slate-100 p-3">
                <Campo label="Nº socio" :valor="v.socio.numeroSocio" />
                <Campo label="Situación" :valor="v.socio.estadoSocio" />
                <Campo label="Cuota" :valor="v.socio.cuotaMensual != null ? v.socio.cuotaMensual + ' €' : null" />
                <Campo label="IBAN" :valor="v.socio.iban" />
              </dl>
              <dl v-else-if="expandida === v.id && v.voluntario"
                class="mt-2 ml-1 grid grid-cols-2 gap-x-6 gap-y-2 rounded-lg bg-slate-50 border border-slate-100 p-3">
                <Campo label="Disponibilidad" :valor="v.voluntario.disponibilidad" />
                <Campo label="Horas/semana" :valor="v.voluntario.horasDisponiblesSemana" />
                <Campo label="Intereses" :valor="v.voluntario.intereses" />
              </dl>
              <p v-else-if="expandida === v.id" class="mt-2 ml-1 text-xs text-slate-400">
                Sin datos adicionales.
              </p>
            </li>
          </ul>
        </div>

        <!-- TAB: Historial -->
        <div v-show="tab === 'historial'">
          <HistorialVinculaciones :vinculaciones="vinculaciones" titulo="Trayectoria completa" />
        </div>
      </div>
    </template>
  </AppDrawer>
</template>

<script setup>
import { ref, computed, watch, h } from 'vue'
import { ChevronDownIcon } from '@heroicons/vue/24/outline'
import AppDrawer from '@/components/common/AppDrawer.vue'
import AvatarImg from '@/components/common/AvatarImg.vue'
import TabsNavigation from '@/components/common/TabsNavigation.vue'
import HistorialVinculaciones from '@/components/miembros/HistorialVinculaciones.vue'
import { graphqlClient } from '@/graphql/client.js'
import { GET_CONTACTO, VINCULACIONES_DE_CONTACTO } from '@/graphql/queries/contactos.js'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  contactoId: { type: String, default: null },
})
defineEmits(['update:modelValue'])

const Campo = (props) => h('div', {}, [
  h('dt', { class: 'text-[11px] uppercase tracking-wide text-slate-400 font-medium mb-0.5' }, props.label),
  h('dd', { class: 'text-sm text-slate-800' }, props.valor != null && props.valor !== '' ? String(props.valor) : '—'),
])
Campo.props = ['label', 'valor']

const contacto = ref(null)
const vinculaciones = ref([])
const cargando = ref(false)
const error = ref('')
const tab = ref('datos')
const expandida = ref(null)

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

const esPJ = computed(() => contacto.value?.tipo === 'PERSONA_JURIDICA')
const titulo = computed(() => {
  const c = contacto.value
  if (!c) return 'Contacto'
  return esPJ.value ? (c.razonSocial || c.nombre) : [c.nombre, c.apellido1, c.apellido2].filter(Boolean).join(' ')
})
const subtitulo = computed(() => esPJ.value ? 'Persona jurídica' : 'Persona física')
const docFmt = computed(() => {
  const c = contacto.value
  return c ? ([c.tipoDocumento, c.numeroDocumento].filter(Boolean).join(' ') || null) : null
})
const numeroSocio = computed(() => {
  const v = vinculaciones.value.find((x) => x.socio && x.socio.numeroSocio)
  return v ? v.socio.numeroSocio : null
})

async function cargar(id) {
  if (!id) return
  cargando.value = true
  error.value = ''
  contacto.value = null
  vinculaciones.value = []
  tab.value = 'datos'
  expandida.value = null
  try {
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

// Cargar al abrir el drawer con un id.
watch(
  () => [props.modelValue, props.contactoId],
  ([open, id]) => { if (open && id) cargar(id) },
  { immediate: true },
)
</script>
