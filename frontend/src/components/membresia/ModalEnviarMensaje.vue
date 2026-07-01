<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4" @click.self="$emit('close')">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        <!-- Cabecera -->
        <div class="flex items-center justify-between px-5 py-3.5 border-b border-slate-200">
          <h3 class="text-sm font-semibold text-slate-800">Redactar mensaje</h3>
          <button @click="$emit('close')" class="p-1 rounded text-slate-400 hover:text-slate-600 hover:bg-slate-100">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto px-5 py-4 space-y-3">
          <!-- Plantilla pre-redactada (arriba). El catálogo por rol es post-MVP;
               de momento solo la opción de redactar libremente. -->
          <div>
            <label class="block text-xs font-medium text-slate-500 mb-1">Mensaje preestablecido</label>
            <select v-model="plantillaSel" @change="aplicarPlantilla"
              class="w-full h-9 px-2.5 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="">Redactar mensaje nuevo…</option>
              <option v-for="p in plantillas" :key="p.id" :value="p.id">{{ p.nombre }}</option>
            </select>
          </div>

          <!-- Para: emails de los seleccionados (chips) -->
          <div>
            <label class="block text-xs font-medium text-slate-500 mb-1">Para ({{ conEmail.length }})</label>
            <div class="flex flex-wrap gap-1.5 rounded-lg border border-slate-200 bg-slate-50 px-2 py-1.5 max-h-24 overflow-y-auto">
              <span v-for="d in conEmail" :key="d.id"
                class="inline-flex items-center gap-1 px-2 py-0.5 text-xs bg-white border border-slate-200 rounded-full text-slate-700">
                {{ d.email }}
              </span>
              <span v-if="!conEmail.length" class="text-xs text-slate-400 italic">Ningún destinatario con email.</span>
            </div>
            <p v-if="sinEmail" class="mt-1 text-xs text-amber-600">
              {{ sinEmail }} seleccionado{{ sinEmail === 1 ? '' : 's' }} sin email (no recibirá{{ sinEmail === 1 ? '' : 'n' }}).
            </p>
          </div>

          <!-- Asunto -->
          <div>
            <label class="block text-xs font-medium text-slate-500 mb-1">Asunto</label>
            <input v-model="asunto" type="text" placeholder="Asunto del mensaje"
              class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>

          <!-- Cuerpo: editable in situ como un webmail -->
          <div>
            <label class="block text-xs font-medium text-slate-500 mb-1">Mensaje</label>
            <textarea v-model="cuerpo" rows="10" placeholder="Escribe el mensaje…"
              class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg resize-y focus:outline-none focus:ring-2 focus:ring-indigo-500"></textarea>
          </div>

          <div v-if="error" class="rounded-lg bg-red-50 border border-red-200 px-3 py-2.5 text-sm text-red-700 flex items-start gap-2">
            <ExclamationTriangleIcon class="w-4 h-4 mt-0.5 shrink-0" />
            <span>{{ error }}</span>
          </div>
        </div>

        <!-- Acciones -->
        <div class="flex items-center justify-end gap-2 px-5 py-3.5 border-t border-slate-200">
          <button @click="$emit('close')"
            class="h-9 px-4 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50">
            Cancelar
          </button>
          <button @click="enviar" :disabled="enviando || !conEmail.length || !asunto.trim() || !cuerpo.trim()"
            class="inline-flex items-center gap-2 h-9 px-4 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50">
            <span v-if="enviando" class="animate-spin rounded-full h-3.5 w-3.5 border-[2px] border-white border-t-transparent"></span>
            {{ enviando ? 'Enviando…' : `Enviar a ${conEmail.length}` }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
/**
 * ModalEnviarMensaje — redacción tipo webmail para enviar un email a varios
 * contactos. Arriba, un selector de mensaje preestablecido (plantilla pre-
 * redactada, catálogo por rol post-MVP); el cuerpo se edita in situ. Los emails
 * de los destinatarios se muestran en "Para". Envía por el SMTP de Parámetros
 * Generales; si no está configurado, el backend devuelve el error y se muestra.
 */
import { ref, computed } from 'vue'
import { XMarkIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import { graphqlClient } from '@/graphql/client'

const props = defineProps({
  // Contactos seleccionados: [{ id, nombre, email }]
  destinatarios: { type: Array, default: () => [] },
})
const emit = defineEmits(['close', 'enviado'])

const conEmail = computed(() => props.destinatarios.filter((d) => d.email))
const sinEmail = computed(() => props.destinatarios.length - conEmail.value.length)

const plantillas = ref([])   // MVP: vacío (catálogo por rol es post-MVP)
const plantillaSel = ref('')
const asunto = ref('')
const cuerpo = ref('')
const enviando = ref(false)
const error = ref('')

function aplicarPlantilla() {
  const p = plantillas.value.find((x) => x.id === plantillaSel.value)
  if (p) { asunto.value = p.asunto || asunto.value; cuerpo.value = p.cuerpo || cuerpo.value }
}

const MUTATION = `
  mutation EnviarMensaje($contactoIds: [UUID!]!, $asunto: String!, $cuerpoHtml: String!) {
    enviarMensajeContactos(contactoIds: $contactoIds, asunto: $asunto, cuerpoHtml: $cuerpoHtml) {
      enviados total sinEmail errores
    }
  }
`
async function enviar() {
  enviando.value = true
  error.value = ''
  try {
    // El cuerpo se manda como HTML sencillo (saltos de línea → <br>).
    const cuerpoHtml = cuerpo.value.replace(/\n/g, '<br>')
    const data = await graphqlClient.request(MUTATION, {
      contactoIds: conEmail.value.map((d) => d.id),
      asunto: asunto.value.trim(),
      cuerpoHtml,
    })
    emit('enviado', data.enviarMensajeContactos)
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'No se pudo enviar el mensaje.'
  } finally {
    enviando.value = false
  }
}
</script>
