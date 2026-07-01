<template>
  <AppLayout :title="tituloPagina" :subtitle="esPJ ? 'Persona jurídica' : 'Persona física'">
    <!-- Acciones en el topbar -->
    <template #actions>
      <FormActions v-if="editing"
        :submit-text="isCreate ? 'Crear contacto' : 'Guardar cambios'"
        :variant="isCreate ? 'green' : 'indigo'"
        :loading="guardando" :disabled="!formValido"
        @cancel="cancelar" @submit="guardar" />
      <template v-else-if="contacto">
        <button v-if="tienePermiso('CONTACTO_EDITAR')" type="button" @click="entrarEdicion"
          class="h-8 px-3 text-sm font-medium text-indigo-600 border border-slate-300 rounded-lg hover:bg-slate-50">
          Editar
        </button>
        <button v-if="tienePermiso('CONTACTO_ELIMINAR')" type="button" @click="toggleBaja"
          class="h-8 px-3 text-sm font-medium border border-slate-300 rounded-lg hover:bg-slate-50"
          :class="contacto.activo ? 'text-amber-600' : 'text-emerald-600'">
          {{ contacto.activo ? 'Dar de baja' : 'Reactivar' }}
        </button>
        <button v-if="tienePermiso('CONTACTO_ELIMINAR')" type="button" @click="eliminarContacto"
          class="h-8 px-3 text-sm font-medium text-red-600 border border-red-200 rounded-lg hover:bg-red-50">
          Eliminar
        </button>
      </template>
    </template>

    <div class="p-4 sm:p-6 w-3/4 mx-auto">
      <div v-if="cargando" class="text-center py-12 text-slate-400 text-sm">Cargando ficha…</div>
      <div v-else-if="error" class="rounded-md bg-red-50 border border-red-200 p-4 text-sm text-red-800">{{ error }}</div>
      <div v-else-if="!isCreate && !contacto" class="text-center py-12 text-slate-400 text-sm">Contacto no encontrado.</div>

      <template v-else>
        <!-- Tipo (solo en alta) -->
        <div v-if="isCreate" class="bg-white border border-slate-200 rounded-xl p-5 mb-3">
          <span class="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Tipo de contacto</span>
          <div class="flex gap-2">
            <button type="button" v-for="t in tiposPersona" :key="t.value" @click="form.tipo = t.value"
              :class="['px-3 py-1.5 text-sm rounded-lg border transition-colors',
                form.tipo === t.value ? 'bg-indigo-50 border-indigo-300 text-indigo-700 font-medium' : 'bg-white border-slate-300 text-slate-600 hover:border-slate-400']">
              {{ t.label }}
            </button>
          </div>
        </div>

        <!-- Datos personales -->
        <div class="bg-white border border-slate-200 rounded-xl p-5">
          <h2 class="text-sm font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <span class="w-1.5 h-5 rounded-full bg-indigo-500"></span>
            Datos personales
            <span v-if="!isCreate && contacto && !contacto.activo" class="ml-1 px-2 py-0.5 text-xs rounded-full bg-red-100 text-red-700">inactivo</span>
          </h2>

          <div class="flex items-center gap-4 mb-4">
            <AvatarImg :src="fotoActual" :nombre="form.nombre || form.razonSocial" :apellido="form.apellido1" size="2xl" :shape="esPJ ? 'carnet' : 'round'" />
            <label v-if="editing" class="inline-flex items-center gap-1.5 h-8 px-3 text-xs font-medium text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-lg cursor-pointer hover:bg-indigo-100 transition-colors">
              Cambiar foto
              <input type="file" accept="image/*" class="hidden" @change="onFotoChange" />
            </label>
          </div>

          <!-- Condiciones DERIVADAS (no vinculaciones): se calculan de los registros -->
          <div v-if="!isCreate && condiciones && (condiciones.esParticipante || condiciones.esDonante)" class="flex flex-wrap gap-2 mb-4">
            <span v-if="condiciones.esParticipante" class="px-2 py-0.5 text-xs font-medium rounded-full bg-sky-100 text-sky-700" :title="`${condiciones.nParticipaciones} participación(es)`">Participante</span>
            <span v-if="condiciones.esFirmante" class="px-2 py-0.5 text-xs font-medium rounded-full bg-teal-100 text-teal-700" :title="`${condiciones.nFirmas} firma(s)`">Firmante</span>
            <span v-if="condiciones.esDonante" class="px-2 py-0.5 text-xs font-medium rounded-full bg-amber-100 text-amber-700" :title="`${condiciones.nDonaciones} donación(es)`">Donante</span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3">
            <template v-if="esPJ">
              <FieldText v-model="form.razonSocial" label="Razón social *" :editing="editing" />
              <FieldText v-model="form.cif" label="CIF" :editing="editing" />
              <FieldText v-model="form.actividadPrincipal" label="Actividad principal" :editing="editing" class="sm:col-span-2" />
            </template>
            <template v-else>
              <FieldText v-model="form.nombre" label="Nombre *" :editing="editing" />
              <FieldText v-model="form.apellido1" label="Primer apellido" :editing="editing" />
              <FieldText v-model="form.apellido2" label="Segundo apellido" :editing="editing" />
              <FieldSelect v-model="form.sexo" label="Sexo" :editing="editing" :options="sexoOptions" />
              <FieldText v-model="form.fechaNacimiento" label="Fecha de nacimiento" type="date" :editing="editing" />
              <FieldText v-model="form.profesion" label="Profesión" :editing="editing" />
              <FieldSelect v-model="form.tipoDocumento" label="Tipo de documento" :editing="editing" :options="tipoDocumentoOptions" />
              <FieldText v-model="form.numeroDocumento" label="Nº documento" :editing="editing" />
            </template>

            <FieldText v-model="form.email" label="Email" type="email" :editing="editing" />
            <FieldText v-model="form.telefono" label="Teléfono" :editing="editing" />
            <FieldText v-model="form.telefono2" label="Tel. alternativo" :editing="editing" />
            <FieldText v-model="form.direccion" label="Dirección" :editing="editing" class="sm:col-span-2" />
            <FieldText v-model="form.codigoPostal" label="Código postal" :editing="editing" />
            <EntidadGeograficaSelect v-model="form.entidadGeograficaId" label="Ubicación (municipio / provincia)"
              :editing="editing" :niveles="[2, 3]" class="sm:col-span-2" />
          </div>
        </div>

        <!-- Representante legal (solo persona jurídica) -->
        <div v-if="esPJ" class="bg-white border border-slate-200 rounded-xl p-5 mt-3">
          <h2 class="text-sm font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <span class="w-1.5 h-5 rounded-full bg-amber-500"></span>
            Representante legal
          </h2>

          <!-- Alta: el representante se da de alta como PF junto con la PJ -->
          <div v-if="isCreate" class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3">
            <p class="sm:col-span-2 -mt-1 text-xs text-slate-400">
              Al crear la persona jurídica se da de alta también a su representante como persona física.
            </p>
            <FieldText v-model="repForm.nombre" label="Nombre del representante *" editing />
            <FieldText v-model="repForm.apellido1" label="Primer apellido" editing />
            <FieldText v-model="repForm.apellido2" label="Segundo apellido" editing />
            <FieldSelect v-model="repForm.tipoDocumento" label="Tipo de documento" :options="tipoDocumentoOptions" editing />
            <FieldText v-model="repForm.numeroDocumento" label="Nº documento" editing />
            <FieldText v-model="repForm.email" label="Email" type="email" editing />
            <FieldText v-model="repForm.telefono" label="Teléfono" editing />
          </div>

          <!-- Edición: reasignar a otra persona física existente -->
          <div v-else-if="editMode">
            <label class="block text-xs font-medium text-slate-500 mb-1">Representante (persona física)</label>
            <select v-model="form.representanteLegalId"
              class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg bg-white text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30">
              <option value="">— Sin representante —</option>
              <option v-for="c in pfContactos" :key="c.id" :value="c.id">{{ nombrePF(c) }}</option>
            </select>
          </div>

          <!-- Vista: datos del representante + ojo a su ficha -->
          <div v-else-if="representante" class="flex items-center gap-4 group">
            <AvatarImg :src="representante.fotoUrl" :nombre="representante.nombre" :apellido="representante.apellido1" size="lg" shape="round" />
            <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-sm flex-1">
              <Campo label="Nombre" :valor="nombrePF(representante)" />
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

        <!-- Historial: vinculaciones + condiciones derivadas -->
        <div v-if="!isCreate && !editMode" class="bg-white border border-slate-200 rounded-xl p-5 mt-3">
          <h2 class="text-sm font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <span class="w-1.5 h-5 rounded-full bg-indigo-500"></span>
            Historial de vinculaciones
          </h2>
          <HistorialVinculaciones :contacto-id="route.params.id" />

          <!-- Condiciones derivadas de actos (participaciones, firmas, donaciones) -->
          <div v-if="condiciones && (condiciones.esParticipante || condiciones.esFirmante || condiciones.esDonante)"
            class="mt-4 pt-4 border-t border-slate-100">
            <p class="text-xs font-medium text-slate-500 mb-2">Actividad registrada</p>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
              <div v-if="condiciones.esParticipante" class="rounded-lg border border-sky-200 bg-sky-50/50 px-3 py-2">
                <p class="text-lg font-semibold text-sky-800">{{ condiciones.nParticipaciones }}</p>
                <p class="text-xs text-sky-700">participación(es)</p>
              </div>
              <div v-if="condiciones.esFirmante" class="rounded-lg border border-teal-200 bg-teal-50/50 px-3 py-2">
                <p class="text-lg font-semibold text-teal-800">{{ condiciones.nFirmas }}</p>
                <p class="text-xs text-teal-700">firma(s)</p>
              </div>
              <div v-if="condiciones.esDonante" class="rounded-lg border border-amber-200 bg-amber-50/50 px-3 py-2">
                <p class="text-lg font-semibold text-amber-800">{{ condiciones.nDonaciones }}</p>
                <p class="text-xs text-amber-700">donación(es)</p>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { EyeIcon } from '@heroicons/vue/24/outline'
import AppLayout from '@/components/common/AppLayout.vue'
import AvatarImg from '@/components/common/AvatarImg.vue'
import HistorialVinculaciones from '@/components/miembros/HistorialVinculaciones.vue'
import { usePermisos } from '@/composables/usePermisos.js'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { graphqlClient } from '@/graphql/client.js'
import { GET_CONTACTO, GET_CONTACTOS, CREAR_CONTACTO, ACTUALIZAR_CONTACTO, ELIMINAR_CONTACTO, GET_CONDICIONES_CONTACTO } from '@/graphql/queries/contactos.js'
import EntidadGeograficaSelect from '@/components/common/EntidadGeograficaSelect.vue'
import FormActions from '@/components/common/FormActions.vue'
import FieldText from '@/components/common/form/FieldText.vue'
import FieldSelect from '@/components/common/form/FieldSelect.vue'
import { useAuthStore } from '@/stores/auth.js'

// ── Componentes de campo: input en edición, texto en vista ──────────────────
const fmtCampo = (v) => (v === null || v === undefined || v === '' ? '—' : String(v))

const Campo = (props) => h('div', {}, [
  h('dt', { class: 'text-xs text-slate-400' }, props.label),
  h('dd', { class: 'text-slate-800' }, fmtCampo(props.valor)),
])
Campo.props = ['label', 'valor']

const route = useRoute()
const router = useRouter()
const { tienePermiso } = usePermisos()
const toast = useToast()
const confirmar = useConfirm()

const isCreate = computed(() => route.name === 'NuevoContacto' || !route.params.id)
const editMode = ref(false)
const editing = computed(() => isCreate.value || editMode.value)

const cargando = ref(false)
const error = ref('')
const guardando = ref(false)
const contacto = ref(null)
const representante = ref(null)
const condiciones = ref(null)  // badges derivados: firmante/participante/donante
const todosContactos = ref([])
const authStore = useAuthStore()
const fotoUrl = ref('')
const fotoFilePendiente = ref(null)   // alta: se sube tras crear (aún no hay id)
const fotoPreview = ref('')
const fotoActual = computed(() => fotoPreview.value || fotoUrl.value || null)

const form = reactive({
  tipo: 'PERSONA_FISICA',
  nombre: '', apellido1: '', apellido2: '', razonSocial: '',
  tipoDocumento: '', numeroDocumento: '', sexo: '', fechaNacimiento: '', profesion: '',
  cif: '', actividadPrincipal: '', representanteLegalId: '',
  email: '', telefono: '', telefono2: '', direccion: '', codigoPostal: '', localidad: '',
  provinciaId: '', entidadGeograficaId: null,
})

// La ubicación se captura con EntidadGeograficaSelect (municipio/provincia
// unificados); ya no hace falta cargar el catálogo de provincias por separado.

// Alta de PJ: el representante legal se da de alta como PF junto con la entidad.
const repForm = reactive({
  nombre: '', apellido1: '', apellido2: '',
  tipoDocumento: '', numeroDocumento: '', email: '', telefono: '',
})

const tiposPersona = [
  { value: 'PERSONA_FISICA', label: 'Persona física' },
  { value: 'PERSONA_JURIDICA', label: 'Persona jurídica' },
]
const sexoOptions = [
  { value: 'H', label: 'Hombre' },
  { value: 'M', label: 'Mujer' },
  { value: 'X', label: 'Otro / no especificado' },
]
const tipoDocumentoOptions = [
  { value: 'DNI', label: 'DNI' }, { value: 'NIE', label: 'NIE' }, { value: 'NIF', label: 'NIF' },
  { value: 'TIE', label: 'TIE' }, { value: 'PASAPORTE', label: 'Pasaporte' }, { value: 'OTRO', label: 'Otro' },
]

const esPJ = computed(() => form.tipo === 'PERSONA_JURIDICA')
const tituloPagina = computed(() => {
  if (isCreate.value) return 'Nuevo contacto'
  return esPJ.value ? (form.razonSocial || 'Contacto') : [form.nombre, form.apellido1, form.apellido2].filter(Boolean).join(' ') || 'Contacto'
})
const pfContactos = computed(() =>
  todosContactos.value
    .filter((c) => c.tipo !== 'PERSONA_JURIDICA' && c.id !== route.params.id)
    .sort((a, b) => nombrePF(a).localeCompare(nombrePF(b), 'es'))
)
const formValido = computed(() => {
  if (esPJ.value) {
    if (!form.razonSocial.trim()) return false
    // En alta, el representante (PF) se crea junto con la PJ: requiere al menos su nombre.
    if (isCreate.value && !repForm.nombre.trim()) return false
    return true
  }
  return !!form.nombre.trim()
})

function nombrePF(c) {
  return [c?.nombre, c?.apellido1, c?.apellido2].filter(Boolean).join(' ') || '—'
}

function poblarForm(c) {
  form.tipo = c.tipo || 'PERSONA_FISICA'
  for (const k of Object.keys(form)) {
    if (k === 'tipo') continue
    if (c[k] != null) form[k] = c[k]
  }
  fotoUrl.value = c.fotoUrl || ''
}

async function subirFotoAlServidor(id, file) {
  const fd = new FormData()
  fd.append('file', file)
  const resp = await fetch(`/api/upload/foto-miembro/${id}`, {
    method: 'POST', headers: { Authorization: `Bearer ${authStore.token}` }, body: fd,
  })
  if (!resp.ok) throw new Error('upload')
  const data = await resp.json()
  return data.fotoUrl
}
async function onFotoChange(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  if (isCreate.value) {
    // Sin id todavía: se sube tras crear el contacto.
    fotoFilePendiente.value = file
    fotoPreview.value = URL.createObjectURL(file)
    return
  }
  try {
    const url = await subirFotoAlServidor(route.params.id, file)
    fotoUrl.value = `${url}?t=${Date.now()}`
    toast.success('Foto actualizada.')
  } catch {
    toast.error('No se pudo subir la foto.')
  }
}

async function cargar() {
  if (isCreate.value) return
  cargando.value = true
  error.value = ''
  try {
    const data = await graphqlClient.request(GET_CONTACTO, { id: route.params.id })
    contacto.value = (data.contactos || [])[0] || null
    if (contacto.value) {
      poblarForm(contacto.value)
      cargarCondiciones(contacto.value.id)
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

// Condiciones derivadas (no vinculaciones): se calculan de los registros.
async function cargarCondiciones(id) {
  condiciones.value = null
  try {
    const data = await graphqlClient.request(GET_CONDICIONES_CONTACTO, { contactoId: id })
    condiciones.value = data.condicionesContacto || null
  } catch (e) { /* silencioso: los badges son informativos */ }
}

async function cargarPFParaRepresentante() {
  if (todosContactos.value.length) return
  try {
    const data = await graphqlClient.request(GET_CONTACTOS, { filter: { eliminado: { eq: false } } })
    todosContactos.value = data.contactos || []
  } catch { /* el selector quedará vacío */ }
}

// El payload solo envía valores con contenido (los vacíos van como null → no se tocan).
function payload() {
  const out = {}
  for (const k of Object.keys(form)) {
    if (k === 'tipo') continue
    const v = form[k]
    out[k] = (v === '' || v === undefined) ? null : v
  }
  return out
}
function repPayload() {
  const out = {}
  for (const k of Object.keys(repForm)) {
    const v = repForm[k]
    out[k] = (v === '' || v === undefined) ? null : v
  }
  return out
}

async function guardar() {
  if (!formValido.value || guardando.value) return
  guardando.value = true
  try {
    if (isCreate.value) {
      const data = { tipo: form.tipo, ...payload() }
      // Alta de PJ: primero su representante como PF, luego la PJ apuntando a él.
      if (esPJ.value && repForm.nombre.trim()) {
        const rep = await graphqlClient.request(CREAR_CONTACTO, { data: { tipo: 'PERSONA_FISICA', ...repPayload() } })
        data.representanteLegalId = rep.crearContacto.id
      }
      const r = await graphqlClient.request(CREAR_CONTACTO, { data })
      if (fotoFilePendiente.value) {
        try { await subirFotoAlServidor(r.crearContacto.id, fotoFilePendiente.value) } catch { /* se puede reintentar al editar */ }
      }
      toast.success(esPJ.value ? 'Persona jurídica y su representante creados.' : 'Contacto creado.')
      router.push(`/contactos/${r.crearContacto.id}`)
    } else {
      await graphqlClient.request(ACTUALIZAR_CONTACTO, { data: { id: route.params.id, ...payload() } })
      toast.success('Contacto actualizado.')
      editMode.value = false
      representante.value = null
      await cargar()
    }
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'No se pudo guardar el contacto.')
  } finally {
    guardando.value = false
  }
}

function cancelar() {
  if (isCreate.value) { router.push('/contactos'); return }
  editMode.value = false
  if (contacto.value) poblarForm(contacto.value)
}

async function toggleBaja() {
  const dar = contacto.value.activo
  const ok = await confirmar({
    titulo: dar ? '¿Dar de baja el contacto?' : '¿Reactivar el contacto?',
    mensaje: dar ? 'El contacto quedará inactivo (baja lógica).' : 'El contacto volverá a estar activo.',
    variante: dar ? 'aviso' : 'info',
  })
  if (!ok) return
  try {
    await graphqlClient.request(ACTUALIZAR_CONTACTO, { data: { id: route.params.id, activo: !dar } })
    toast.success(dar ? 'Contacto dado de baja.' : 'Contacto reactivado.')
    await cargar()
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'No se pudo cambiar el estado.')
  }
}

async function eliminarContacto() {
  const ok = await confirmar({
    titulo: '¿Eliminar el contacto?',
    mensaje: 'Se retirará del directorio (baja lógica). Podrá recuperarse en base de datos; la purga definitiva compete al módulo RGPD.',
    variante: 'critica',
  })
  if (!ok) return
  try {
    await graphqlClient.request(ELIMINAR_CONTACTO, { id: route.params.id })
    toast.success('Contacto eliminado.')
    router.push('/contactos')
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'No se pudo eliminar el contacto.')
  }
}

function verContacto(id) { router.push(`/contactos/${id}`) }

// Al entrar en edición de una PJ existente, carga las PF para el selector de reasignación.
function entrarEdicion() {
  editMode.value = true
  if (esPJ.value) cargarPFParaRepresentante()
}

onMounted(() => { cargar() })
</script>
