<template>
  <AppLayout :title="titulo" subtitle="Ficha 360° del contacto">
    <div class="p-4 sm:p-6 max-w-5xl mx-auto">
      <div class="mb-4">
        <router-link to="/contactos" class="text-sm text-purple-600 hover:text-purple-800">← Volver al directorio</router-link>
      </div>

      <div v-if="cargando" class="text-center py-12 text-slate-400 text-sm">Cargando ficha…</div>
      <div v-else-if="error" class="rounded-md bg-red-50 border border-red-200 p-4 text-sm text-red-800">{{ error }}</div>
      <div v-else-if="!contacto" class="text-center py-12 text-slate-400 text-sm">Contacto no encontrado.</div>

      <template v-else>
        <!-- Cabecera con foto tamaño carnet -->
        <div class="flex items-start gap-4 mb-6">
          <img
            v-if="contacto.fotoUrl"
            :src="contacto.fotoUrl"
            alt="Foto del contacto"
            class="w-24 h-32 object-cover rounded-md border border-slate-300 shadow-sm flex-shrink-0"
          />
          <div
            v-else
            class="w-24 h-32 rounded-md border border-dashed border-slate-300 flex items-center justify-center text-xs text-slate-400 flex-shrink-0"
          >sin foto</div>
          <div class="flex items-center gap-3 pt-1">
            <span
              class="inline-block px-2 py-0.5 rounded text-xs font-medium"
              :class="esPJ ? 'bg-amber-100 text-amber-800' : 'bg-sky-100 text-sky-800'"
            >{{ esPJ ? 'Persona jurídica' : 'Persona física' }}</span>
            <h1 class="text-lg font-semibold text-slate-800">{{ titulo }}</h1>
            <span v-if="!contacto.activo" class="text-xs text-red-600">(inactivo)</span>
          </div>
        </div>

        <!-- Identidad -->
        <section class="border border-slate-200 rounded-lg mb-5">
          <h2 class="px-4 py-2 border-b border-slate-100 text-sm font-semibold text-slate-700 bg-slate-50">Identidad</h2>
          <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 p-4 text-sm">
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
        </section>

        <!-- Facetas vigentes -->
        <section class="mb-5">
          <h2 class="text-sm font-semibold text-slate-700 mb-2">Facetas vigentes</h2>
          <div v-if="!facetasVigentes.length" class="text-sm text-slate-400">Este contacto no tiene facetas vigentes.</div>
          <div v-else class="space-y-3">
            <div v-for="v in facetasVigentes" :key="v.id" class="border border-slate-200 rounded-lg p-4">
              <div class="flex items-center gap-2 mb-2">
                <span class="inline-block px-2 py-0.5 rounded text-xs font-medium" :class="colorFaceta(v.tipoVinculacion && v.tipoVinculacion.codigo)">
                  {{ v.tipoVinculacion ? v.tipoVinculacion.nombre : '—' }}
                </span>
                <span class="text-xs text-slate-400">desde {{ v.fechaInicio || '—' }}</span>
              </div>
              <!-- Satélite socio -->
              <dl v-if="v.socio" class="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-1 text-sm">
                <Campo label="Nº socio" :valor="v.socio.numeroSocio" />
                <Campo label="Situación" :valor="v.socio.estadoSocio" />
                <Campo label="Cuota" :valor="v.socio.cuotaMensual != null ? v.socio.cuotaMensual + ' €' : null" />
                <Campo label="IBAN" :valor="v.socio.iban || (mostrarIbanOculto ? '— (sin permiso)' : null)" />
                <Campo label="Honor" :valor="v.socio.esHonor ? 'Sí' : null" />
              </dl>
              <!-- Satélite voluntario -->
              <dl v-else-if="v.voluntario" class="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-1 text-sm">
                <Campo label="Disponibilidad" :valor="v.voluntario.disponibilidad" />
                <Campo label="Horas/semana" :valor="v.voluntario.horasDisponiblesSemana" />
                <Campo label="Intereses" :valor="v.voluntario.intereses" />
                <Campo label="Conduce" :valor="v.voluntario.puedeConducir ? 'Sí' : null" />
                <Campo label="Vehículo propio" :valor="v.voluntario.vehiculoPropio ? 'Sí' : null" />
              </dl>
              <p v-else class="text-xs text-slate-400">Sin datos adicionales.</p>
            </div>
          </div>
        </section>

        <!-- Historial: mismo componente reutilizable que en Mis datos y Junta -->
        <HistorialVinculaciones v-if="facetasCerradas.length" :vinculaciones="facetasCerradas" titulo="Historial" />
      </template>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import HistorialVinculaciones from '@/components/miembros/HistorialVinculaciones.vue'
import { graphqlClient } from '@/graphql/client.js'
import { GET_CONTACTO, VINCULACIONES_DE_CONTACTO } from '@/graphql/queries/contactos.js'

// Componente de presentación inline para "etiqueta: valor".
const Campo = (props) => h('div', {}, [
  h('dt', { class: 'text-xs text-slate-400' }, props.label),
  h('dd', { class: 'text-slate-800' }, props.valor != null && props.valor !== '' ? String(props.valor) : '—'),
])
Campo.props = ['label', 'valor']

const route = useRoute()
const contacto = ref(null)
const vinculaciones = ref([])
const cargando = ref(true)
const error = ref('')

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
const docFmt = computed(() => {
  const c = contacto.value
  if (!c) return null
  return [c.tipoDocumento, c.numeroDocumento].filter(Boolean).join(' ') || null
})
const facetasVigentes = computed(() => vinculaciones.value.filter((v) => !v.fechaFin))
const facetasCerradas = computed(() => vinculaciones.value.filter((v) => v.fechaFin))
// Si hay faceta de socio sin IBAN, mostramos el aviso de "sin permiso" en vez de un hueco mudo.
const mostrarIbanOculto = computed(() => facetasVigentes.value.some((v) => v.socio && !v.socio.iban))

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
