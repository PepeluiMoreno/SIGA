<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-purple-100 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-lg p-8 space-y-6">
      <h1 class="text-xl font-bold text-center text-gray-900">Pago de cuota de socio</h1>

      <!-- Cargando -->
      <div v-if="cargando" class="text-center text-gray-500 py-8">
        Cargando los datos de tu cuota…
      </div>

      <!-- Error (token inválido/caducado, etc.) -->
      <div v-else-if="error" class="text-center py-6">
        <p class="text-red-600 font-medium">{{ error }}</p>
        <p class="mt-2 text-sm text-gray-500">
          Si el enlace ha caducado, contacta con la organización para recibir uno nuevo.
        </p>
      </div>

      <!-- Ya pagada -->
      <div v-else-if="info.pagada" class="text-center py-6 bg-green-50 border-2 border-green-200 rounded-xl">
        <div class="text-4xl text-green-600">✓</div>
        <p class="mt-2 font-semibold text-green-800">Tu cuota de {{ info.ejercicio }} ya está pagada.</p>
        <p class="text-sm text-green-700">¡Gracias por tu apoyo!</p>
      </div>

      <!-- Pago completado en esta sesión -->
      <div v-else-if="completado" class="text-center py-6 bg-green-50 border-2 border-green-200 rounded-xl">
        <div class="text-4xl text-green-600">✓</div>
        <p class="mt-2 font-semibold text-green-800">{{ mensajeExito }}</p>
      </div>

      <!-- Formulario de pago -->
      <template v-else>
        <div class="rounded-xl border border-gray-200 divide-y divide-gray-100 text-sm">
          <div class="flex justify-between px-4 py-3">
            <span class="text-gray-500">Socio/a</span>
            <span class="font-medium text-gray-900">{{ info.nombre_socio }}</span>
          </div>
          <div class="flex justify-between px-4 py-3">
            <span class="text-gray-500">Ejercicio</span>
            <span class="font-medium text-gray-900">{{ info.ejercicio }}</span>
          </div>
          <div class="flex justify-between px-4 py-3">
            <span class="text-gray-500">Importe pendiente</span>
            <span class="font-bold text-gray-900">{{ info.pendiente }} €</span>
          </div>
        </div>

        <div v-if="!info.paypal_client_id" class="text-center text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-lg p-3">
          El pago online no está disponible en este momento. Puedes pagar por
          transferencia contactando con la organización.
        </div>
        <div v-else>
          <div ref="paypalContainer"></div>
          <p v-if="errorPago" class="mt-2 text-sm text-red-600 text-center">{{ errorPago }}</p>
        </div>

        <p class="text-xs text-gray-400 text-center">
          El importe lo fija la organización según tu cuota; el pago se procesa de
          forma segura a través de PayPal (admite tarjeta sin cuenta PayPal).
        </p>
      </template>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

const route = useRoute()
const token = route.query.token ?? ''

const cargando = ref(true)
const error = ref('')
const errorPago = ref('')
const info = ref({})
const completado = ref(false)
const mensajeExito = ref('')
const paypalContainer = ref(null)

function cargarSDKPayPal(clientId) {
  return new Promise((resolve, reject) => {
    if (window.paypal) { resolve(window.paypal); return }
    const script = document.createElement('script')
    script.src = `https://www.paypal.com/sdk/js?client-id=${encodeURIComponent(clientId)}&currency=EUR&intent=capture`
    script.onload = () => resolve(window.paypal)
    script.onerror = () => reject(new Error('No se pudo cargar el SDK de PayPal'))
    document.head.appendChild(script)
  })
}

async function montarBotonesPayPal() {
  const paypal = await cargarSDKPayPal(info.value.paypal_client_id)
  paypal.Buttons({
    style: { color: 'blue', shape: 'rect', label: 'pay', height: 45 },

    // El backend crea la orden derivando el importe del pendiente de la cuota.
    createOrder: async () => {
      const resp = await fetch(`${API_BASE}/api/publico/pago-cuota/crear-orden`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
      })
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}))
        throw new Error(err.detail || 'No se pudo iniciar el pago')
      }
      const data = await resp.json()
      return data.order_id
    },

    onApprove: async (data) => {
      const resp = await fetch(`${API_BASE}/api/publico/pago-cuota/capturar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, order_id: data.orderID }),
      })
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}))
        throw new Error(err.detail || 'No se pudo completar el pago')
      }
      const resultado = await resp.json()
      completado.value = true
      mensajeExito.value = resultado.mensaje
    },

    onError: () => {
      errorPago.value = 'Ocurrió un error en el proceso de pago. Inténtalo de nuevo.'
    },
  }).render(paypalContainer.value)
}

onMounted(async () => {
  if (!token) {
    error.value = 'Falta el enlace de pago. Usa el enlace que recibiste por email.'
    cargando.value = false
    return
  }
  try {
    const resp = await fetch(`${API_BASE}/api/publico/pago-cuota?token=${encodeURIComponent(token)}`)
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}))
      throw new Error(err.detail || 'No se pudieron cargar los datos de la cuota.')
    }
    info.value = await resp.json()
    cargando.value = false
    if (!info.value.pagada && info.value.paypal_client_id) {
      await nextTick()  // el contenedor del botón aparece tras el re-render
      await montarBotonesPayPal()
    }
  } catch (e) {
    error.value = e.message
    cargando.value = false
  }
})
</script>
