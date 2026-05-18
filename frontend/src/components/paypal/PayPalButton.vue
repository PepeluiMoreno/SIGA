<template>
  <div>
    <!-- Botón PayPal cargado por el SDK oficial -->
    <div v-if="!completado" id="paypal-button-container" ref="container"></div>
    <div v-else class="pago-completado">
      <div class="icono">✓</div>
      <p class="titulo">Pago completado</p>
      <p class="subtitulo">{{ mensajeExito }}</p>
    </div>
    <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  importe: { type: Number, required: true },
  concepto: { type: String, required: true },
  moneda: { type: String, default: 'EUR' },
  cuotaId: { type: String, default: null },
  miembroId: { type: String, default: null },
  cuentaBancariaId: { type: String, default: null },
  clientId: { type: String, required: true },  // PAYPAL_CLIENT_ID del .env frontend
})

const emit = defineEmits(['pago-completado', 'pago-cancelado', 'error'])

const container = ref(null)
const completado = ref(false)
const mensajeExito = ref('')
const errorMsg = ref('')
const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

// ─── Cargar SDK de PayPal dinámicamente ──────────────────────────────────────
function cargarSDKPayPal(clientId, moneda) {
  return new Promise((resolve, reject) => {
    if (window.paypal) { resolve(window.paypal); return }
    const script = document.createElement('script')
    script.src = `https://www.paypal.com/sdk/js?client-id=${clientId}&currency=${moneda}&intent=capture`
    script.onload = () => resolve(window.paypal)
    script.onerror = () => reject(new Error('No se pudo cargar el SDK de PayPal'))
    document.head.appendChild(script)
  })
}

onMounted(async () => {
  try {
    const paypal = await cargarSDKPayPal(props.clientId, props.moneda)

    paypal.Buttons({
      style: {
        color: 'blue',
        shape: 'rect',
        label: 'pay',
        height: 45,
      },

      // 1. Crear la orden en nuestro backend
      createOrder: async () => {
        const resp = await fetch(`${API_BASE}/api/paypal/create-order`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            importe: props.importe,
            concepto: props.concepto,
            moneda: props.moneda,
            cuota_id: props.cuotaId ?? null,
            miembro_id: props.miembroId ?? null,
          }),
        })
        if (!resp.ok) throw new Error('Error creando la orden')
        const data = await resp.json()
        return data.order_id
      },

      // 2. Capturar el pago tras la aprobación del pagador
      onApprove: async (data) => {
        const resp = await fetch(`${API_BASE}/api/paypal/capture-order/${data.orderID}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            cuota_id: props.cuotaId ?? null,
            miembro_id: props.miembroId ?? null,
            cuenta_bancaria_id: props.cuentaBancariaId ?? null,
          }),
        })
        if (!resp.ok) {
          const err = await resp.json()
          throw new Error(err.detail || 'Error capturando el pago')
        }
        const resultado = await resp.json()
        completado.value = true
        mensajeExito.value = `${resultado.importe} ${resultado.moneda} recibidos correctamente.`
        emit('pago-completado', resultado)
      },

      onCancel: () => {
        emit('pago-cancelado')
      },

      onError: (err) => {
        errorMsg.value = 'Ocurrió un error en el proceso de pago. Inténtalo de nuevo.'
        emit('error', err)
      },
    }).render(container.value)

  } catch (e) {
    errorMsg.value = e.message
  }
})
</script>

<style scoped>
.pago-completado {
  text-align: center;
  padding: 2rem;
  background: #f0fdf4;
  border: 2px solid #86efac;
  border-radius: 12px;
}
.icono { font-size: 3rem; color: #16a34a; }
.titulo { font-weight: 700; font-size: 1.2rem; color: #15803d; margin: 0.5rem 0 0.25rem; }
.subtitulo { color: #166534; font-size: 0.95rem; margin: 0; }
.error { color: #dc2626; font-size: 0.9rem; margin-top: 0.5rem; }
</style>
