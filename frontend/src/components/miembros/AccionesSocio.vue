<template>
  <!-- Acciones de ciclo de vida del socio, gateadas por permiso (mismo código que el
       resolver). Se renderiza solo si hay alguna acción aplicable. -->
  <div v-if="mostrar" class="flex items-center gap-2 flex-wrap">
    <AppButton v-if="mostrarSuspender" size="sm" variant="secondary"
      :loading="procesando" @click="suspender">Suspender</AppButton>

    <AppButton v-if="mostrarReactivar" size="sm" variant="secondary"
      :loading="procesando" @click="reactivar">Reactivar</AppButton>

    <AppButton v-if="mostrarBaja" size="sm" variant="danger"
      :loading="procesando" @click="darDeBaja">Dar de baja</AppButton>

    <AppButton v-if="mostrarConvertir" size="sm" variant="primary"
      :loading="procesando" @click="convertir">Convertir en socio</AppButton>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import AppButton from '@/components/common/AppButton.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import { useToast } from '@/composables/useToast'
import { useConfirm, usePrompt } from '@/composables/useConfirm'
import { usePermisos } from '@/composables/usePermisos'
import { VINCULACIONES_DE_CONTACTO } from '@/graphql/queries/contactos.js'
import {
  SUSPENDER_SOCIO, REACTIVAR_SOCIO, DAR_DE_BAJA_SOCIO, CONVERTIR_SIMPATIZANTE_EN_SOCIO,
} from '@/graphql/queries/socioGestion.js'

const props = defineProps({
  contactoId: { type: String, required: true },
})
const emit = defineEmits(['cambio'])

const { query, mutation } = useGraphQL()
const toast = useToast()
const confirm = useConfirm()
const prompt = usePrompt()
const { tienePermiso } = usePermisos()

const vinculaciones = ref([])
const procesando = ref(false)

// Vinculación SOCIO más reciente y SIMPATIZANTE vigente.
const vincSocio = computed(() =>
  vinculaciones.value.find(v => v.tipoVinculacion?.codigo === 'SOCIO'))
const vincSimpatizante = computed(() =>
  vinculaciones.value.find(v => v.tipoVinculacion?.codigo === 'SIMPATIZANTE' && !v.fechaFin && v.estado === 'activa'))

const socioActivo = computed(() =>
  vincSocio.value && vincSocio.value.estado === 'activa' && !vincSocio.value.fechaFin
  && (vincSocio.value.socio?.estadoSocio ?? 'activo') === 'activo')
const socioInactivo = computed(() =>
  vincSocio.value && !socioActivo.value)  // suspendido, de baja o cerrada

const mostrarSuspender = computed(() => socioActivo.value && tienePermiso('MEMBRESIA_MIEMBRO_SUSPENDER'))
const mostrarBaja = computed(() => socioActivo.value && tienePermiso('MEMBRESIA_MIEMBRO_BAJA'))
const mostrarReactivar = computed(() => socioInactivo.value && tienePermiso('MEMBRESIA_MIEMBRO_BAJA'))
const mostrarConvertir = computed(() =>
  vincSimpatizante.value && !socioActivo.value && tienePermiso('MEMBRESIA_MIEMBRO_CREAR'))
const mostrar = computed(() =>
  mostrarSuspender.value || mostrarBaja.value || mostrarReactivar.value || mostrarConvertir.value)

async function cargar() {
  if (!props.contactoId) return
  try {
    const data = await query(VINCULACIONES_DE_CONTACTO, { contactoId: props.contactoId })
    vinculaciones.value = data.vinculacionesDeContacto || []
  } catch { /* silencioso: sin datos no se muestran acciones */ }
}

async function _run(doc, vars, okMsg) {
  procesando.value = true
  try {
    await mutation(doc, vars)
    toast.success(okMsg)
    await cargar()
    emit('cambio')
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'La operación no se pudo completar')
  } finally {
    procesando.value = false
  }
}

async function suspender() {
  const ok = await confirm({
    titulo: 'Suspender socio',
    mensaje: '¿Suspender temporalmente a este socio? Se puede reactivar después.',
    etiquetaConfirmar: 'Suspender',
  })
  if (!ok) return
  await _run(SUSPENDER_SOCIO, { contactoId: props.contactoId }, 'Socio suspendido.')
}

async function reactivar() {
  const ok = await confirm({
    titulo: 'Reactivar socio',
    mensaje: '¿Reactivar a este socio como activo de pleno derecho?',
    etiquetaConfirmar: 'Reactivar',
  })
  if (!ok) return
  await _run(REACTIVAR_SOCIO, { contactoId: props.contactoId }, 'Socio reactivado.')
}

async function darDeBaja() {
  const motivo = await prompt({
    titulo: 'Dar de baja al socio',
    label: 'Motivo de la baja (opcional)',
    variante: 'peligro',
    etiquetaConfirmar: 'Dar de baja',
  })
  if (motivo === null) return  // cancelado
  await _run(DAR_DE_BAJA_SOCIO,
    { contactoId: props.contactoId, fechaBaja: null, motivoBajaId: null, motivoBajaTexto: motivo || null },
    'Socio dado de baja.')
}

async function convertir() {
  const ok = await confirm({
    titulo: 'Convertir en socio',
    mensaje: '¿Convertir a este simpatizante en socio? Se creará su vinculación de socio y se cerrará la de simpatizante. Los datos económicos (cuota/IBAN) se completan luego en su ficha.',
    etiquetaConfirmar: 'Convertir',
  })
  if (!ok) return
  await _run(CONVERTIR_SIMPATIZANTE_EN_SOCIO, { contactoId: props.contactoId }, 'Simpatizante convertido en socio.')
}

onMounted(cargar)
watch(() => props.contactoId, cargar)
</script>
