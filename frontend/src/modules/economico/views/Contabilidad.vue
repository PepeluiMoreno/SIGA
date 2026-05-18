<template>
  <AppLayout title="Contabilidad" subtitle="Plan de cuentas PCESFL 2013, asientos y balances">

    <!-- KPIs -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-blue-50 rounded-lg p-4 border border-blue-100">
        <p class="text-xs text-gray-500">Cuentas activas</p>
        <p class="text-xl font-bold text-blue-600">{{ cuentasContables.length }}</p>
      </div>
      <div class="bg-purple-50 rounded-lg p-4 border border-purple-100">
        <p class="text-xs text-gray-500">Asientos confirmados</p>
        <p class="text-xl font-bold text-purple-600">{{ asientosConfirmados.length }}</p>
      </div>
      <div class="bg-yellow-50 rounded-lg p-4 border border-yellow-100">
        <p class="text-xs text-gray-500">En borrador</p>
        <p class="text-xl font-bold text-yellow-600">{{ asientosBorrador.length }}</p>
      </div>
      <div class="bg-green-50 rounded-lg p-4 border border-green-100">
        <p class="text-xs text-gray-500">Ejercicio</p>
        <p class="text-xl font-bold text-green-600">{{ ejercicioActual }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 mb-6">
      <nav class="-mb-px flex space-x-6">
        <button v-for="tab in tabs" :key="tab.id"
          @click="activeTab = tab.id"
          :class="[activeTab === tab.id ? 'border-purple-500 text-purple-600' : 'border-transparent text-gray-500 hover:text-gray-700', 'py-3 px-1 border-b-2 font-medium text-sm']"
        >{{ tab.icon }} {{ tab.name }}</button>
      </nav>
    </div>

    <!-- Tab Plan de Cuentas -->
    <div v-if="activeTab === 'plan'">
      <div class="flex justify-between items-center mb-4">
        <div class="flex items-center gap-3">
          <h3 class="font-semibold text-gray-800">Plan de cuentas PCESFL 2013</h3>
          <select v-model="filtroTipoCuenta" class="input-sm">
            <option value="">Todos los tipos</option>
            <option value="ACTIVO">Activo</option>
            <option value="PASIVO">Pasivo</option>
            <option value="PATRIMONIO">Patrimonio</option>
            <option value="GASTO">Gasto</option>
          </select>
        </div>
        <button @click="abrirNuevaCuenta" class="btn-primary">+ Nueva cuenta</button>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Código</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Nombre</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Tipo</th>
              <th class="px-3 py-2 text-center text-xs font-medium text-gray-500">Nivel</th>
              <th class="px-3 py-2 text-center text-xs font-medium text-gray-500">Asientos</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="c in cuentasFiltradas" :key="c.id" class="hover:bg-gray-50"
              :class="{ 'font-semibold': c.nivel === 1, 'pl-4': c.nivel === 2, 'pl-8': c.nivel >= 3 }">
              <td class="px-3 py-2 font-mono text-gray-600" :style="{ paddingLeft: (c.nivel * 12) + 'px' }">{{ c.codigo }}</td>
              <td class="px-3 py-2 text-gray-900">{{ c.nombre }}</td>
              <td class="px-3 py-2">
                <span class="text-xs rounded px-1.5 py-0.5" :class="badgeTipo(c.tipo)">{{ c.tipo }}</span>
              </td>
              <td class="px-3 py-2 text-center text-gray-500">{{ c.nivel }}</td>
              <td class="px-3 py-2 text-center">
                <span v-if="c.permiteAsiento" class="text-green-500 text-sm">✓</span>
                <span v-else class="text-gray-300 text-sm">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-if="!cuentasFiltradas.length" class="text-center text-gray-400 py-8">
        No hay cuentas contables. Inicializa el plan de cuentas PCESFL 2013.
      </p>
    </div>

    <!-- Tab Asientos -->
    <div v-if="activeTab === 'asientos'">
      <div class="flex justify-between items-center mb-4">
        <div class="flex items-center gap-3">
          <h3 class="font-semibold text-gray-800">Asientos contables</h3>
          <select v-model="filtroEjercicio" class="input-sm" @change="recargarAsientos">
            <option v-for="y in ejerciciosDisponibles" :key="y" :value="y">{{ y }}</option>
          </select>
          <select v-model="filtroEstado" class="input-sm" @change="recargarAsientos">
            <option value="">Todos</option>
            <option value="BORRADOR">Borrador</option>
            <option value="CONFIRMADO">Confirmado</option>
            <option value="ANULADO">Anulado</option>
          </select>
        </div>
        <button @click="abrirNuevoAsiento" class="btn-primary">+ Nuevo asiento</button>
      </div>

      <div v-if="asientosContables.length" class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Nº</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Fecha</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Glosa</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Tipo</th>
              <th class="px-3 py-2 text-center text-xs font-medium text-gray-500">Estado</th>
              <th class="px-3 py-2 text-center text-xs font-medium text-gray-500">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="a in asientosContables" :key="a.id" class="hover:bg-gray-50">
              <td class="px-3 py-2 font-mono text-gray-500">{{ String(a.numeroAsiento).padStart(4, '0') }}</td>
              <td class="px-3 py-2 text-gray-600 whitespace-nowrap">{{ fechaFmt(a.fecha) }}</td>
              <td class="px-3 py-2 text-gray-900">{{ a.glosa }}</td>
              <td class="px-3 py-2 text-xs text-gray-500">{{ a.tipoAsiento }}</td>
              <td class="px-3 py-2 text-center">
                <span class="text-xs rounded px-2 py-0.5" :class="badgeEstado(a.estado)">{{ a.estado }}</span>
              </td>
              <td class="px-3 py-2 text-center">
                <button v-if="a.estado === 'BORRADOR'" @click="confirmarAsiento(a.id)"
                  class="text-xs text-green-600 hover:underline mr-2">Confirmar</button>
                <button v-if="a.estado !== 'ANULADO'" @click="anularAsiento(a.id)"
                  class="text-xs text-red-500 hover:underline">Anular</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="text-center text-gray-400 py-8">No hay asientos para el ejercicio {{ filtroEjercicio }}.</p>
    </div>

    <!-- Tab Balances -->
    <div v-if="activeTab === 'balances'">
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-semibold text-gray-800">Balances de sumas y saldos</h3>
        <button @click="generarBalance" :disabled="generandoBalance" class="btn-primary">
          {{ generandoBalance ? 'Generando…' : '↻ Generar balance' }}
        </button>
      </div>
      <p class="text-sm text-gray-500 mb-4">
        Genera el balance de sumas y saldos acumulado a la fecha actual para el ejercicio {{ ejercicioActual }}.
      </p>

      <div v-if="balancesContables.length" class="space-y-3">
        <div v-for="b in balancesContables" :key="b.id" class="border rounded-lg p-4 bg-white">
          <div class="flex justify-between items-center">
            <div>
              <p class="font-medium text-gray-800">Ejercicio {{ b.ejercicio }}</p>
              <p class="text-xs text-gray-400">Generado el {{ fechaFmt(b.fechaGeneracion) }}</p>
            </div>
            <div class="text-right">
              <div class="grid grid-cols-3 gap-6 text-sm">
                <div><p class="text-xs text-gray-500">Total debe</p><p class="font-bold text-gray-900">{{ fmt(b.totalDebe) }}</p></div>
                <div><p class="text-xs text-gray-500">Total haber</p><p class="font-bold text-gray-900">{{ fmt(b.totalHaber) }}</p></div>
                <div>
                  <p class="text-xs text-gray-500">Diferencia</p>
                  <p class="font-bold" :class="(b.totalDebe - b.totalHaber) === 0 ? 'text-green-600' : 'text-red-600'">
                    {{ fmt(b.totalDebe - b.totalHaber) }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <p v-else class="text-center text-gray-400 py-8">No hay balances generados.</p>
    </div>

    <LoadSpinner v-if="loading" />

    <!-- MODAL: Nueva cuenta contable -->
    <div v-if="modalCuenta" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="modalCuenta = false">
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
        <h3 class="text-lg font-semibold mb-4">Nueva cuenta contable</h3>
        <div class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label">Código *</label>
              <input v-model="formCuenta.codigo" class="input font-mono" placeholder="Ej: 572" />
            </div>
            <div>
              <label class="label">Nivel *</label>
              <select v-model="formCuenta.nivel" class="input">
                <option :value="1">1 — Grupo</option>
                <option :value="2">2 — Subgrupo</option>
                <option :value="3">3 — Cuenta</option>
              </select>
            </div>
          </div>
          <div>
            <label class="label">Nombre *</label>
            <input v-model="formCuenta.nombre" class="input" placeholder="Ej: Bancos e instituciones de crédito" />
          </div>
          <div>
            <label class="label">Tipo *</label>
            <select v-model="formCuenta.tipo" class="input">
              <option value="ACTIVO">Activo</option>
              <option value="PASIVO">Pasivo</option>
              <option value="PATRIMONIO">Patrimonio</option>
              <option value="INGRESO">Ingreso</option>
              <option value="GASTO">Gasto</option>
            </select>
          </div>
          <div class="flex items-center gap-2">
            <input type="checkbox" v-model="formCuenta.esDotacion" id="dotacion" />
            <label for="dotacion" class="text-sm text-gray-700">Es elemento de dotación fundacional</label>
          </div>
          <div>
            <label class="label">Descripción</label>
            <textarea v-model="formCuenta.descripcion" class="input h-16" />
          </div>
        </div>
        <p v-if="errorModal" class="text-red-600 text-sm mt-2">{{ errorModal }}</p>
        <div class="flex justify-end gap-3 mt-5">
          <button @click="modalCuenta = false" class="btn-secondary">Cancelar</button>
          <button @click="guardarCuenta" :disabled="guardando" class="btn-primary">
            {{ guardando ? 'Guardando…' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- MODAL: Nuevo asiento -->
    <div v-if="modalAsiento" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="modalAsiento = false">
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-lg mx-4">
        <h3 class="text-lg font-semibold mb-4">Nuevo asiento contable</h3>
        <div class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label">Ejercicio *</label>
              <input type="number" v-model="formAsiento.ejercicio" class="input" />
            </div>
            <div>
              <label class="label">Fecha *</label>
              <input type="date" v-model="formAsiento.fecha" class="input" />
            </div>
          </div>
          <div>
            <label class="label">Glosa (descripción) *</label>
            <input v-model="formAsiento.glosa" class="input" placeholder="Descripción del asiento" />
          </div>
          <div>
            <label class="label">Tipo</label>
            <select v-model="formAsiento.tipoAsiento" class="input">
              <option value="GESTION">Gestión</option>
              <option value="APERTURA">Apertura</option>
              <option value="REGULARIZACION">Regularización</option>
              <option value="CIERRE">Cierre</option>
            </select>
          </div>
          <div>
            <label class="label">Observaciones</label>
            <textarea v-model="formAsiento.observaciones" class="input h-16" />
          </div>
          <p class="text-xs text-gray-500">El asiento se crea en estado BORRADOR. Añade los apuntes debe/haber y luego confírmalo.</p>
        </div>
        <p v-if="errorModal" class="text-red-600 text-sm mt-2">{{ errorModal }}</p>
        <div class="flex justify-end gap-3 mt-5">
          <button @click="modalAsiento = false" class="btn-secondary">Cancelar</button>
          <button @click="guardarAsiento" :disabled="guardando" class="btn-primary">
            {{ guardando ? 'Creando…' : 'Crear asiento' }}
          </button>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import LoadSpinner from '@/components/common/LoadSpinner.vue'
import { useContabilidad } from '@/composables/useContabilidad'

const {
  cuentasContables,
  asientosContables,
  balancesContables,
  loading,
  obtenerPlanCuentas,
  obtenerAsientos,
  obtenerBalances,
  crearCuentaContable,
  crearAsiento,
  confirmarAsientoContable,
  anularAsientoContable,
  generarBalanceContable,
} = useContabilidad()

const activeTab = ref('plan')
const filtroTipoCuenta = ref('')
const filtroEjercicio = ref(new Date().getFullYear())
const filtroEstado = ref('')
const generandoBalance = ref(false)

const modalCuenta = ref(false)
const modalAsiento = ref(false)
const guardando = ref(false)
const errorModal = ref('')

const formCuenta = ref({ codigo: '', nombre: '', tipo: 'ACTIVO', nivel: 3, esDotacion: false, descripcion: '' })
const formAsiento = ref({ ejercicio: new Date().getFullYear(), fecha: new Date().toISOString().split('T')[0], glosa: '', tipoAsiento: 'GESTION', observaciones: '' })

const tabs = [
  { id: 'plan', name: 'Plan de cuentas', icon: '📋' },
  { id: 'asientos', name: 'Asientos', icon: '📝' },
  { id: 'balances', name: 'Balances', icon: '⚖️' },
]

const ejercicioActual = computed(() => new Date().getFullYear())
const ejerciciosDisponibles = computed(() => {
  const year = new Date().getFullYear()
  return [year, year - 1, year - 2]
})

const asientosConfirmados = computed(() => asientosContables.value.filter(a => a.estado === 'CONFIRMADO'))
const asientosBorrador = computed(() => asientosContables.value.filter(a => a.estado === 'BORRADOR'))
const cuentasFiltradas = computed(() => {
  if (!filtroTipoCuenta.value) return cuentasContables.value
  return cuentasContables.value.filter(c => c.tipo === filtroTipoCuenta.value)
})

const fmt = (val) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(val ?? 0)
const fechaFmt = (d) => d ? new Intl.DateTimeFormat('es-ES').format(new Date(d)) : ''

const badgeTipo = (tipo) => ({
  'ACTIVO': 'bg-blue-100 text-blue-700',
  'PASIVO': 'bg-red-100 text-red-700',
  'PATRIMONIO': 'bg-purple-100 text-purple-700',
  'INGRESO': 'bg-green-100 text-green-700',
  'GASTO': 'bg-orange-100 text-orange-700',
}[tipo] || 'bg-gray-100 text-gray-600')

const badgeEstado = (estado) => ({
  'BORRADOR': 'bg-yellow-100 text-yellow-700',
  'CONFIRMADO': 'bg-green-100 text-green-700',
  'ANULADO': 'bg-red-100 text-red-600',
}[estado] || 'bg-gray-100 text-gray-600')

const recargarAsientos = async () => {
  await obtenerAsientos(filtroEjercicio.value)
}

const abrirNuevaCuenta = () => {
  formCuenta.value = { codigo: '', nombre: '', tipo: 'ACTIVO', nivel: 3, esDotacion: false, descripcion: '' }
  errorModal.value = ''
  modalCuenta.value = true
}

const abrirNuevoAsiento = () => {
  formAsiento.value = { ejercicio: filtroEjercicio.value, fecha: new Date().toISOString().split('T')[0], glosa: '', tipoAsiento: 'GESTION', observaciones: '' }
  errorModal.value = ''
  modalAsiento.value = true
}

const guardarCuenta = async () => {
  errorModal.value = ''
  if (!formCuenta.value.codigo || !formCuenta.value.nombre) {
    errorModal.value = 'Código y nombre son obligatorios'
    return
  }
  guardando.value = true
  try {
    await crearCuentaContable(formCuenta.value)
    modalCuenta.value = false
    await obtenerPlanCuentas()
  } catch (e) {
    errorModal.value = e.message || 'Error al guardar la cuenta'
  } finally {
    guardando.value = false
  }
}

const guardarAsiento = async () => {
  errorModal.value = ''
  if (!formAsiento.value.glosa || !formAsiento.value.fecha) {
    errorModal.value = 'Glosa y fecha son obligatorias'
    return
  }
  guardando.value = true
  try {
    await crearAsiento(formAsiento.value)
    modalAsiento.value = false
    await recargarAsientos()
  } catch (e) {
    errorModal.value = e.message || 'Error al crear el asiento'
  } finally {
    guardando.value = false
  }
}

const confirmarAsiento = async (asientoId) => {
  if (!confirm('¿Confirmar este asiento? Verifica que debe = haber.')) return
  try {
    await confirmarAsientoContable(asientoId)
    await recargarAsientos()
  } catch (e) {
    alert(e.message || 'Error: el asiento no cuadra o ya está confirmado')
  }
}

const anularAsiento = async (asientoId) => {
  if (!confirm('¿Anular este asiento? Esta acción no se puede deshacer.')) return
  try {
    await anularAsientoContable(asientoId)
    await recargarAsientos()
  } catch (e) {
    alert(e.message || 'Error al anular el asiento')
  }
}

const generarBalance = async () => {
  if (!confirm(`¿Generar balance de sumas y saldos para el ejercicio ${ejercicioActual.value}?`)) return
  generandoBalance.value = true
  try {
    await generarBalanceContable(ejercicioActual.value)
    await obtenerBalances()
    alert('Balance generado correctamente')
  } catch (e) {
    alert(e.message || 'Error al generar el balance')
  } finally {
    generandoBalance.value = false
  }
}

onMounted(async () => {
  await obtenerPlanCuentas()
  await recargarAsientos()
  await obtenerBalances()
})
</script>

<style scoped>
.btn-primary { @apply px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed; }
.btn-secondary { @apply px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm font-medium; }
.label { @apply block text-sm font-medium text-gray-700 mb-1; }
.input { @apply w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent; }
.input-sm { @apply px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400; }
</style>
