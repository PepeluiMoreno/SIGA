<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4" @click.self="$emit('close')">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[92vh] flex flex-col">
        <!-- Cabecera tipo "Redactar" de un webmail -->
        <div class="flex items-center justify-between px-5 py-3 border-b border-slate-200 bg-slate-50 rounded-t-xl">
          <h3 class="text-sm font-semibold text-slate-800">Redactar mensaje</h3>
          <button @click="$emit('close')" class="p-1 rounded text-slate-400 hover:text-slate-600 hover:bg-slate-200">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto">
          <!-- Plantilla pre-redactada -->
          <div class="flex items-center gap-2 px-5 py-2 border-b border-slate-100">
            <span class="text-xs text-slate-500 w-16 shrink-0">Plantilla</span>
            <select v-model="plantillaSel" @change="aplicarPlantilla"
              class="flex-1 h-8 px-2 text-sm border border-slate-200 rounded bg-white focus:outline-none focus:ring-1 focus:ring-indigo-400">
              <option value="">Redactar mensaje nuevo…</option>
              <option v-for="p in plantillas" :key="p.id" :value="p.id">{{ p.nombre }}</option>
            </select>
          </div>

          <!-- Para: chips quitables -->
          <div class="flex items-start gap-2 px-5 py-2 border-b border-slate-100">
            <span class="text-xs text-slate-500 w-16 shrink-0 pt-1.5">Para</span>
            <div class="flex-1 flex flex-wrap gap-1.5">
              <span v-for="d in paraLista" :key="d.id"
                class="inline-flex items-center gap-1 pl-2 pr-1 py-0.5 text-xs bg-indigo-50 border border-indigo-200 rounded-full text-indigo-700">
                {{ d.email }}
                <button @click="quitarPara(d.id)" class="text-indigo-400 hover:text-red-500" title="Quitar">
                  <XMarkIcon class="w-3 h-3" />
                </button>
              </span>
              <span v-if="!paraLista.length" class="text-xs text-slate-400 italic pt-0.5">Sin destinatarios con email.</span>
            </div>
            <button v-if="!mostrarCcCco" type="button" @click="mostrarCcCco = true"
              class="text-xs text-slate-500 hover:text-indigo-600 shrink-0 pt-1.5">CC/CCO</button>
          </div>

          <!-- CC / CCO (emails sueltos, separados por coma) -->
          <template v-if="mostrarCcCco">
            <div class="flex items-center gap-2 px-5 py-2 border-b border-slate-100">
              <span class="text-xs text-slate-500 w-16 shrink-0">CC</span>
              <input v-model="ccTexto" type="text" placeholder="correo1@ejemplo.com, correo2@ejemplo.com"
                class="flex-1 h-8 px-2 text-sm border border-slate-200 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400" />
            </div>
            <div class="flex items-center gap-2 px-5 py-2 border-b border-slate-100">
              <span class="text-xs text-slate-500 w-16 shrink-0">CCO</span>
              <input v-model="ccoTexto" type="text" placeholder="copia oculta…"
                class="flex-1 h-8 px-2 text-sm border border-slate-200 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400" />
            </div>
          </template>

          <!-- Asunto -->
          <div class="flex items-center gap-2 px-5 py-2 border-b border-slate-100">
            <span class="text-xs text-slate-500 w-16 shrink-0">Asunto</span>
            <input v-model="asunto" type="text" placeholder="Asunto del mensaje"
              class="flex-1 h-8 px-2 text-sm border-0 focus:outline-none focus:ring-0" />
          </div>

          <!-- Cuerpo: editor enriquecido tipo webmail -->
          <div class="px-5 py-3">
            <EditorTextoRico v-model="cuerpo" placeholder="Escribe el mensaje…" />
          </div>

          <!-- Pie del mensaje (firma) -->
          <div class="px-5 pb-3">
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-medium text-slate-500">Pie del mensaje (firma)</span>
              <button type="button" @click="mostrarPie = !mostrarPie" class="text-xs text-indigo-600 hover:underline">
                {{ mostrarPie ? 'Ocultar' : 'Editar' }}
              </button>
            </div>
            <EditorTextoRico v-if="mostrarPie" v-model="pie" placeholder="Firma / datos de la asociación…" />
            <p v-else class="text-xs text-slate-400 italic">Se añadirá el pie al final del mensaje.</p>
          </div>

          <div v-if="error" class="mx-5 mb-3 rounded-lg bg-red-50 border border-red-200 px-3 py-2.5 text-sm text-red-700 flex items-start gap-2">
            <ExclamationTriangleIcon class="w-4 h-4 mt-0.5 shrink-0" />
            <span>{{ error }}</span>
          </div>
        </div>

        <!-- Acciones -->
        <div class="flex items-center justify-between gap-2 px-5 py-3 border-t border-slate-200 bg-slate-50 rounded-b-xl">
          <span class="text-xs text-slate-400">
            {{ paraLista.length }} destinatario{{ paraLista.length === 1 ? '' : 's' }}
            <template v-if="sinEmail"> · {{ sinEmail }} sin email</template>
          </span>
          <div class="flex items-center gap-2">
            <button @click="$emit('close')"
              class="h-9 px-4 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50">
              Descartar
            </button>
            <button @click="enviar" :disabled="enviando || !puedeEnviar"
              class="inline-flex items-center gap-2 h-9 px-5 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50">
              <PaperAirplaneIcon v-if="!enviando" class="w-4 h-4" />
              <span v-else class="animate-spin rounded-full h-3.5 w-3.5 border-[2px] border-white border-t-transparent"></span>
              {{ enviando ? 'Enviando…' : 'Enviar' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
/**
 * ModalEnviarMensaje — compositor de correo tipo cliente webmail: Para con chips
 * quitables, CC/CCO, asunto, cuerpo con editor enriquecido y pie del mensaje
 * (firma). Envía por el SMTP de Parámetros Generales; si no está configurado, el
 * backend devuelve el error y se muestra.
 */
import { ref, computed } from 'vue'
import { XMarkIcon, ExclamationTriangleIcon, PaperAirplaneIcon } from '@heroicons/vue/24/outline'
import EditorTextoRico from '@/components/common/EditorTextoRico.vue'
import { graphqlClient } from '@/graphql/client'

const props = defineProps({
  destinatarios: { type: Array, default: () => [] },  // [{ id, nombre, email }]
})
const emit = defineEmits(['close', 'enviado'])

// Destinatarios "Para": los que tienen email, quitables uno a uno.
const quitados = ref(new Set())
const paraLista = computed(() =>
  props.destinatarios.filter((d) => d.email && !quitados.value.has(d.id))
)
const sinEmail = computed(() => props.destinatarios.filter((d) => !d.email).length)
function quitarPara(id) { quitados.value = new Set([...quitados.value, id]) }

const mostrarCcCco = ref(false)
const ccTexto = ref('')
const ccoTexto = ref('')
const parseEmails = (t) => t.split(',').map((e) => e.trim()).filter(Boolean)

const plantillas = ref([])   // catálogo por rol post-MVP; de momento vacío
const plantillaSel = ref('')
const asunto = ref('')
const cuerpo = ref('')
const mostrarPie = ref(false)
const pie = ref('')
const enviando = ref(false)
const error = ref('')

const puedeEnviar = computed(() =>
  (paraLista.value.length || parseEmails(ccTexto.value).length || parseEmails(ccoTexto.value).length) &&
  asunto.value.trim() && cuerpo.value.trim()
)

function aplicarPlantilla() {
  const p = plantillas.value.find((x) => x.id === plantillaSel.value)
  if (p) { asunto.value = p.asunto || asunto.value; cuerpo.value = p.cuerpo || cuerpo.value }
}

const MUTATION = `
  mutation EnviarMensaje($contactoIds: [UUID!]!, $asunto: String!, $cuerpoHtml: String!, $cc: [String!], $cco: [String!]) {
    enviarMensajeContactos(contactoIds: $contactoIds, asunto: $asunto, cuerpoHtml: $cuerpoHtml, cc: $cc, cco: $cco) {
      enviados total sinEmail errores
    }
  }
`
async function enviar() {
  enviando.value = true
  error.value = ''
  try {
    // Cuerpo = mensaje + pie (separados por una línea).
    const cuerpoHtml = pie.value.trim()
      ? `${cuerpo.value}<br><br><hr>${pie.value}`
      : cuerpo.value
    const data = await graphqlClient.request(MUTATION, {
      contactoIds: paraLista.value.map((d) => d.id),
      asunto: asunto.value.trim(),
      cuerpoHtml,
      cc: parseEmails(ccTexto.value),
      cco: parseEmails(ccoTexto.value),
    })
    emit('enviado', data.enviarMensajeContactos)
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'No se pudo enviar el mensaje.'
  } finally {
    enviando.value = false
  }
}
</script>
