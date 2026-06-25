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

        <!-- Datos personales (sección única, como la ficha de socio) -->
        <div class="bg-white border border-slate-200 rounded-xl p-5">
          <h2 class="text-sm font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <span class="w-1.5 h-5 rounded-full bg-indigo-500"></span>
            Datos personales
          </h2>
          <div class="flex flex-col sm:flex-row gap-6">
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
        </div>

        <!-- Representante legal (solo persona jurídica) -->
        <div v-if="esPJ" class="bg-white border border-slate-200 rounded-xl p-5 mt-3">
          <h2 class="text-sm font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <span class="w-1.5 h-5 rounded-full bg-amber-500"></span>
            Representante legal
          </h2>
          <div v-if="representante" class="flex items-center gap-4 group">
            <AvatarImg :src="representante.fotoUrl" :nombre="representante.nombre" :apellido="representante.apellido1" size="lg" shape="round" />
            <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-sm flex-1">
              <Campo label="Nombre" :valor="[representante.nombre, representante.apellido1, representante.apellido2].filter(Boolean).join(' ')" />
              <Campo label="Documento" :valor="[representante.tipoDocumento, representante.numeroDocumento].filter(Boolean).join(' ')" />
              <Campo label="Email" :valor="representante.email" />
              <Campo label="Teléfono" :valor="representante.telefono" />
            </dl>
            <button type="button" @click="verContacto(representante.id)"
              class="shrink-0 p-1.5 rounded text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors opacity-0 group-hover:opacity-100"
              title="Ver ficha del representante">
              <EyeIcon class="w-5 h-5" />
            </button>
          </div>
          <p v-else class="text-sm text-slate-400">Sin representante legal asignado.</p>
        </div>
      </template>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { EyeIcon } from '@heroicons/vue/24/outline'
import AppLayout from '@/components/common/AppLayout.vue'
import AvatarImg from '@/components/common/AvatarImg.vue'
import { graphqlClient } from '@/graphql/client.js'
import { GET_CONTACTO, VINCULACIONES_DE_CONTACTO } from '@/graphql/queries/contactos.js'

const Campo = (props) => h('div', {}, [
  h('dt', { class: 'text-xs text-slate-400' }, props.label),
  h('dd', { class: 'text-slate-800' }, props.valor != null && props.valor !== '' ? String(props.valor) : '—'),
])
Campo.props = ['label', 'valor']

const route = useRoute()
const router = useRouter()
function verContacto(id) { router.push(`/contactos/${id}`) }
const contacto = ref(null)
const representante = ref(null)
const vinculaciones = ref([])
const cargando = ref(true)
const error = ref('')

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
    representante.value = null
    if (contacto.value) {
      const vd = await graphqlClient.request(VINCULACIONES_DE_CONTACTO, { contactoId: id })
      vinculaciones.value = vd.vinculacionesDeContacto || []
      // El representante legal (de una PJ) es otro contacto: se carga aparte por su id
      // (ContactoType no expone la relación, solo representanteLegalId).
      if (contacto.value.representanteLegalId) {
        const rd = await graphqlClient.request(GET_CONTACTO, { id: contacto.value.representanteLegalId })
        representante.value = (rd.contactos || [])[0] || null
      }
    }
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'No se pudo cargar la ficha.'
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
</script>
