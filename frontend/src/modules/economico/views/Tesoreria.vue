<template>
  <AppLayout title="Tesorería" subtitle="Cuentas bancarias, movimientos y conciliaciones">

    <!-- KPIs -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-green-50 rounded-lg p-4 border border-green-100">
        <p class="text-xs text-gray-500">Saldo total</p>
        <p class="text-xl font-bold text-green-600">{{ fmt(saldoTotal) }}</p>
      </div>
      <div class="bg-blue-50 rounded-lg p-4 border border-blue-100">
        <p class="text-xs text-gray-500">Cuentas activas</p>
        <p class="text-xl font-bold text-blue-600">{{ cuentasBancarias.length }}</p>
      </div>
      <div class="bg-purple-50 rounded-lg p-4 border border-purple-100">
        <p class="text-xs text-gray-500">Conciliados</p>
        <p class="text-xl font-bold text-purple-600">{{ totales.totalConciliados }}</p>
      </div>
      <div class="bg-yellow-50 rounded-lg p-4 border border-yellow-100">
        <p class="text-xs text-gray-500">Por conciliar</p>
        <p class="text-xl font-bold text-yellow-600">{{ totales.totalNoConciliados }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 mb-6">
      <nav class="-mb-px flex space-x-6">
        <button
          v-for="tab in tabs" :key="tab.id"
          @click="activeTab = tab.id"
          :class="[activeTab === tab.id ? 'border-purple-500 text-purple-600' : 'border-transparent text-gray-500 hover:text-gray-700', 'py-3 px-1 border-b-2 font-medium text-sm']"
        >{{ tab.icon }} {{ tab.name }}</button>
      </nav>
    </div>

    <!-- Tab Cuentas -->
    <div v-if="activeTab === 'cuentas'">
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-semibold text-gray-800">Cuentas bancarias</h3>
        <button @click="abrirNuevaCuenta" class="btn-primary">+ Nueva cuenta</button>
      </div>

      <div v-if="cuentasBancarias.length" class="space-y-3">
        <div
          v-for="c in cuentasBancarias" :key="c.id"
          @click="seleccionarCuenta(c)"
          class="border rounded-lg p-4 bg-white hover:bg-gray-50 cursor-pointer"
          :class="cuentaSeleccionada?.id === c.id ? 'border-purple-400 ring-1 ring-purple-300' : 'border-gray-200'"
        >
          <div class="flex justify-between items-start">
            <div>
              <h4 class="font-semibold text-gray-900">{{ c.nombre }}</h4>
              <p class="text-sm text-gray-500 font-mono">{{ ibanFmt(c.iban) }}</p>
              <p class="text-xs text-gray-400 mt-1">{{ c.bancoNombre }}</p>
              <span v-if="c.agrupacion" class="inline-block mt-1 px-1.5 py-0.5 text-xs bg-indigo-50 text-indigo-600 border border-indigo-200 rounded-full">
                {{ c.agrupacion.nombre }}
              </span>
              <span v-else class="inline-block mt-1 px-1.5 py-0.5 text-xs bg-slate-50 text-slate-400 border border-slate-200 rounded-full">
                Organización
              </span>
            </div>
            <div class="text-right">
              <p class="text-lg font-bold text-gray-900">{{ fmt(c.saldoActual) }}</p>
              <span :class="c.activa ? 'text-green-600' : 'text-gray-400'" class="text-xs">
                {{ c.activa ? '● Activa' : '○ Inactiva' }}
              </span>
            </div>
          </div>
        </div>
      </div>
      <p v-else class="text-center text-gray-400 py-8">No hay cuentas bancarias registradas.</p>
    </div>

    <!-- Tab Movimientos -->
    <div v-if="activeTab === 'movimientos'">
      <div class="flex justify-between items-center mb-4">
        <div class="flex items-center gap-3">
          <h3 class="font-semibold text-gray-800">Movimientos</h3>
          <span v-if="cuentaSeleccionada" class="text-xs bg-purple-100 text-purple-700 rounded px-2 py-1">
            {{ cuentaSeleccionada.nombre }}
          </span>
        </div>
        <button v-if="cuentaSeleccionada" @click="abrirNuevoMovimiento" class="btn-primary">+ Nuevo movimiento</button>
      </div>

      <!-- Selector de cuenta si no hay ninguna seleccionada -->
      <div v-if="!cuentaSeleccionada" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
        <p class="text-sm text-yellow-700">Selecciona una cuenta en la pestaña "Cuentas" para ver sus movimientos.</p>
      </div>

      <!-- Filtros -->
      <div v-if="cuentaSeleccionada" class="flex gap-3 mb-4">
        <input type="date" v-model="filtroFechaInicio" class="input-sm" @change="recargarMovimientos">
        <input type="date" v-model="filtroFechaFin" class="input-sm" @change="recargarMovimientos">
        <select v-model="filtroTipo" class="input-sm" @change="recargarMovimientos">
          <option value="">Todos</option>
          <option value="INGRESO">Ingresos</option>
          <option value="GASTO">Gastos</option>
        </select>
      </div>

      <div v-if="apuntesCaja.length" class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Fecha</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Concepto</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Origen</th>
              <th class="px-3 py-2 text-right text-xs font-medium text-gray-500">Importe</th>
              <th class="px-3 py-2 text-center text-xs font-medium text-gray-500">Conciliado</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="m in movimientosFiltrados" :key="m.id" class="hover:bg-gray-50">
              <td class="px-3 py-2 text-gray-600 whitespace-nowrap">{{ fechaFmt(m.fecha) }}</td>
              <td class="px-3 py-2 text-gray-900">{{ m.concepto }}</td>
              <td class="px-3 py-2">
                <span v-if="m.origen" class="text-xs bg-gray-100 text-gray-600 rounded px-1.5 py-0.5">{{ m.origen }}</span>
              </td>
              <td class="px-3 py-2 text-right font-medium"
                :class="m.tipo === 'INGRESO' ? 'text-green-600' : 'text-red-600'">
                {{ m.tipo === 'INGRESO' ? '+' : '-' }}{{ fmt(m.importe) }}
              </td>
              <td class="px-3 py-2 text-center">
                <span v-if="m.conciliado" class="text-green-500 text-lg">✓</span>
                <button v-else @click="conciliarMovimiento(m.id)" class="text-xs text-purple-600 hover:underline">Conciliar</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else-if="cuentaSeleccionada" class="text-center text-gray-400 py-8">No hay movimientos para esta cuenta.</p>
    </div>

    <!-- Tab Remesas -->
    <div v-if="activeTab === 'remesas'">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <!-- Panel izquierdo: Generar nueva remesa -->
        <div class="bg-white border border-slate-200 rounded-xl p-5">
          <h3 class="font-semibold text-slate-800 mb-4">Generar nueva remesa SEPA</h3>
          <div class="space-y-3">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="label">Ejercicio *</label>
                <input type="number" v-model.number="formRemesa.ejercicio" class="input" :min="2000" :max="2099" />
              </div>
              <div>
                <label class="label">Fecha de cobro *</label>
                <input type="date" v-model="formRemesa.fechaCobro" class="input" />
              </div>
            </div>
            <div>
              <label class="label">Agrupación territorial</label>
              <select v-model="formRemesa.agrupacionId" class="input">
                <option :value="null">— Toda la organización —</option>
                <option v-for="u in unidades" :key="u.id" :value="u.id">{{ u.nombre }}</option>
              </select>
            </div>
            <div>
              <label class="label">Observaciones</label>
              <textarea v-model="formRemesa.observaciones" class="input h-16" />
            </div>

            <!-- Preview cuotas pendientes -->
            <div v-if="cuotasPendientesPreview.length" class="bg-slate-50 rounded-lg p-3 text-sm">
              <p class="font-medium text-slate-700 mb-1">
                {{ cuotasPendientesPreview.length }} cuotas pendientes —
                <span class="text-green-700 font-semibold">{{ fmt(totalPreview) }}</span>
              </p>
            </div>
            <div v-else-if="previewCargado" class="text-sm text-amber-600 bg-amber-50 p-3 rounded-lg">
              No hay cuotas pendientes para el ejercicio y agrupación indicados.
            </div>

            <p v-if="errorRemesa" class="text-red-600 text-sm">{{ errorRemesa }}</p>
            <div class="flex gap-2 pt-1">
              <button @click="previsualizarCuotas" :disabled="guardandoRemesa" class="btn-secondary flex-1">
                Vista previa
              </button>
              <button @click="generarRemesa" :disabled="guardandoRemesa || !cuotasPendientesPreview.length" class="btn-primary flex-1">
                {{ guardandoRemesa ? 'Generando…' : 'Generar remesa' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Panel derecho: Remesas históricas -->
        <div class="bg-white border border-slate-200 rounded-xl p-5">
          <div class="flex justify-between items-center mb-4">
            <h3 class="font-semibold text-slate-800">Remesas</h3>
            <select v-model="filtroEjercicioRemesa" class="input-sm w-28">
              <option value="">Todas</option>
              <option v-for="y in ejerciciosDisponibles" :key="y" :value="y">{{ y }}</option>
            </select>
          </div>
          <div v-if="remesasFiltradas.length" class="space-y-2 max-h-[480px] overflow-y-auto pr-1">
            <div
              v-for="r in remesasFiltradas" :key="r.id"
              class="border rounded-lg p-3 hover:bg-slate-50 cursor-pointer"
              :class="remesaSeleccionada?.id === r.id ? 'border-indigo-400 bg-indigo-50' : 'border-slate-200'"
              @click="remesaSeleccionada = r"
            >
              <div class="flex justify-between items-start">
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium text-slate-800 truncate">{{ r.referencia.replace('SEPA_ISO20022CORE_','').replace('.xml','') }}</p>
                  <p class="text-xs text-slate-500 mt-0.5">
                    Cobro: {{ fechaFmt(r.fechaCobro) }} · {{ r.numOrdenes }} órdenes
                    <span v-if="r.agrupacion" class="ml-1 text-indigo-500">· {{ r.agrupacion.nombre }}</span>
                  </p>
                </div>
                <div class="text-right flex-shrink-0 ml-3">
                  <p class="text-sm font-bold text-slate-900">{{ fmt(r.importeTotal) }}</p>
                  <span :class="estadoRemesaClass(r.estado?.nombre)" class="text-xs px-1.5 py-0.5 rounded-full">
                    {{ r.estado?.nombre }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          <p v-else class="text-center text-slate-400 py-8 text-sm">No hay remesas.</p>

          <!-- Acciones sobre la remesa seleccionada -->
          <div v-if="remesaSeleccionada" class="mt-4 pt-4 border-t border-slate-100 flex flex-wrap gap-2">
            <a :href="`/api/remesas/${remesaSeleccionada.id}/sepa-xml`"
              class="btn-secondary text-sm"
              :download="`remesa_${remesaSeleccionada.id.slice(0,8)}.xml`">
              ↓ Descargar XML SEPA
            </a>
            <button
              v-if="remesaSeleccionada.estado?.nombre === 'Borrador'"
              @click="enviarRemesa(remesaSeleccionada.id)"
              :disabled="guardandoRemesa"
              class="btn-secondary text-sm">
              Marcar enviada
            </button>
            <button
              v-if="remesaSeleccionada.estado?.nombre === 'Enviada' && cuentaSeleccionada"
              @click="liquidarRemesaSeleccionada"
              :disabled="guardandoRemesa"
              class="btn-primary text-sm">
              {{ guardandoRemesa ? 'Liquidando…' : 'Liquidar (registrar cobro)' }}
            </button>
            <p v-if="remesaSeleccionada.estado?.nombre === 'Enviada' && !cuentaSeleccionada"
              class="text-xs text-amber-600 self-center">
              Selecciona una cuenta en la pestaña Cuentas para liquidar.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab Conciliaciones -->
    <div v-if="activeTab === 'conciliaciones'">
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-semibold text-gray-800">Conciliaciones bancarias</h3>
        <button v-if="cuentaSeleccionada" @click="abrirNuevaConciliacion" class="btn-primary">+ Nueva conciliación</button>
      </div>

      <div v-if="!cuentaSeleccionada" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
        <p class="text-sm text-yellow-700">Selecciona una cuenta en la pestaña "Cuentas".</p>
      </div>

      <div v-if="conciliaciones.length" class="space-y-3">
        <div v-for="c in conciliaciones" :key="c.id" class="border rounded-lg p-4 bg-white">
          <div class="flex justify-between items-center">
            <div>
              <p class="font-medium text-gray-800">{{ fechaFmt(c.fechaInicio) }} — {{ fechaFmt(c.fechaFin) }}</p>
              <p class="text-sm text-gray-500 mt-1">
                Extracto: {{ fmt(c.saldoFinalExtracto) }} | Sistema: {{ fmt(c.saldoFinalSistema) }}
              </p>
            </div>
            <div class="text-right">
              <p class="text-sm font-semibold" :class="c.diferencia == 0 ? 'text-green-600' : 'text-red-600'">
                Diferencia: {{ fmt(c.diferencia) }}
              </p>
              <div v-if="c.conciliado">
                <span class="text-xs text-green-600">✓ Conciliada</span>
              </div>
              <button v-else-if="c.diferencia == 0" @click="confirmarConciliacion(c.id)"
                class="mt-1 text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200">
                Confirmar
              </button>
            </div>
          </div>
        </div>
      </div>
      <p v-else-if="cuentaSeleccionada" class="text-center text-gray-400 py-8">No hay conciliaciones.</p>
    </div>

    <LoadSpinner v-if="loading" />

    <!-- MODAL: Nueva cuenta bancaria -->
    <div v-if="modalCuenta" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="modalCuenta = false">
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
        <h3 class="text-lg font-semibold mb-4">Nueva cuenta bancaria</h3>
        <div class="space-y-3">
          <div>
            <label class="label">Nombre *</label>
            <input v-model="formCuenta.nombre" class="input" placeholder="Ej: Cuenta corriente principal" />
          </div>
          <div>
            <label class="label">IBAN *</label>
            <input v-model="formCuenta.iban" class="input font-mono" placeholder="ES00 0000 0000 0000 0000 0000" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label">Banco</label>
              <input v-model="formCuenta.bancoNombre" class="input" placeholder="Nombre del banco" />
            </div>
            <div>
              <label class="label">BIC/SWIFT</label>
              <input v-model="formCuenta.bicSwift" class="input" placeholder="BKBKESMMXXX" />
            </div>
          </div>
          <div>
            <label class="label">Titular</label>
            <input v-model="formCuenta.titular" class="input" />
          </div>
          <div>
            <label class="label">Agrupación territorial</label>
            <select v-model="formCuenta.agrupacionId" class="input">
              <option :value="null">— Cuenta de la organización —</option>
              <option v-for="u in unidades" :key="u.id" :value="u.id">{{ u.nombre }}</option>
            </select>
          </div>
          <div>
            <label class="label">Descripción</label>
            <textarea v-model="formCuenta.descripcion" class="input h-20" />
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

    <!-- MODAL: Nuevo movimiento -->
    <div v-if="modalMovimiento" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="modalMovimiento = false">
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
        <h3 class="text-lg font-semibold mb-4">Registrar movimiento</h3>
        <div class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label">Fecha *</label>
              <input type="date" v-model="formMovimiento.fecha" class="input" />
            </div>
            <div>
              <label class="label">Tipo *</label>
              <select v-model="formMovimiento.tipo" class="input">
                <option value="INGRESO">Ingreso</option>
                <option value="GASTO">Gasto</option>
              </select>
            </div>
          </div>
          <div>
            <label class="label">Importe (€) *</label>
            <input type="number" v-model="formMovimiento.importe" step="0.01" min="0.01" class="input" />
          </div>
          <div>
            <label class="label">Concepto *</label>
            <input v-model="formMovimiento.concepto" class="input" placeholder="Descripción del movimiento" />
          </div>
          <div>
            <label class="label">Origen</label>
            <select v-model="formMovimiento.origen" class="input">
              <option value="">Manual</option>
              <option value="CUOTA">Cuota</option>
              <option value="DONACION">Donación</option>
              <option value="REMESA">Remesa</option>
              <option value="PAGO">Pago online</option>
            </select>
          </div>
          <div>
            <label class="label">Referencia externa</label>
            <input v-model="formMovimiento.referenciaExterna" class="input" placeholder="Nº de referencia del banco" />
          </div>
          <div>
            <label class="label">Observaciones</label>
            <textarea v-model="formMovimiento.observaciones" class="input h-16" />
          </div>
        </div>
        <p v-if="errorModal" class="text-red-600 text-sm mt-2">{{ errorModal }}</p>
        <div class="flex justify-end gap-3 mt-5">
          <button @click="modalMovimiento = false" class="btn-secondary">Cancelar</button>
          <button @click="guardarMovimiento" :disabled="guardando" class="btn-primary">
            {{ guardando ? 'Registrando…' : 'Registrar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- MODAL: Nueva conciliación -->
    <div v-if="modalConciliacion" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="modalConciliacion = false">
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
        <h3 class="text-lg font-semibold mb-4">Nueva conciliación bancaria</h3>
        <p class="text-sm text-gray-500 mb-4">Introduce los saldos del extracto bancario para el período a conciliar.</p>
        <div class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label">Fecha inicio *</label>
              <input type="date" v-model="formConciliacion.fechaInicio" class="input" />
            </div>
            <div>
              <label class="label">Fecha fin *</label>
              <input type="date" v-model="formConciliacion.fechaFin" class="input" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label">Saldo inicial extracto (€) *</label>
              <input type="number" v-model="formConciliacion.saldoInicialExtracto" step="0.01" class="input" />
            </div>
            <div>
              <label class="label">Saldo final extracto (€) *</label>
              <input type="number" v-model="formConciliacion.saldoFinalExtracto" step="0.01" class="input" />
            </div>
          </div>
          <div>
            <label class="label">Observaciones</label>
            <textarea v-model="formConciliacion.observaciones" class="input h-16" />
          </div>
        </div>
        <p v-if="errorModal" class="text-red-600 text-sm mt-2">{{ errorModal }}</p>
        <div class="flex justify-end gap-3 mt-5">
          <button @click="modalConciliacion = false" class="btn-secondary">Cancelar</button>
          <button @click="guardarConciliacion" :disabled="guardando" class="btn-primary">
            {{ guardando ? 'Creando…' : 'Crear conciliación' }}
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
import { useTesoreria } from '@/composables/useTesoreria'
import { useUnidadesOrganizativas } from '@/composables/useUnidadesOrganizativas'
import { useGraphQL } from '@/composables/useGraphQL'

const {
  cuentasBancarias,
  apuntesCaja,
  conciliaciones,
  loading,
  error,
  obtenerCuentasBancarias,
  obtenerApuntesCaja,
  obtenerConciliaciones,
  crearCuentaBancaria,
  registrarApunte,
  crearConciliacion,
  confirmarConciliacionPeriodo,
  marcarApunteConciliado,
  calcularTotales,
  saldoTotal,
} = useTesoreria()

const { unidades } = useUnidadesOrganizativas()

const { query: gqlQuery, mutation: gqlMutation } = useGraphQL()

const activeTab = ref('cuentas')
const cuentaSeleccionada = ref(null)
const filtroFechaInicio = ref('')
const filtroFechaFin = ref('')
const filtroTipo = ref('')

// ── Remesas ────────────────────────────────────────────────────────────────
const remesas = ref([])
const remesaSeleccionada = ref(null)
const filtroEjercicioRemesa = ref('')
const guardandoRemesa = ref(false)
const errorRemesa = ref('')
const cuotasPendientesPreview = ref([])
const previewCargado = ref(false)
const formRemesa = ref({
  ejercicio: new Date().getFullYear(),
  fechaCobro: '',
  agrupacionId: null,
  observaciones: '',
})

const totalPreview = computed(() =>
  cuotasPendientesPreview.value.reduce((s, c) => s + (parseFloat(c.importe) - parseFloat(c.importePagado || 0)), 0)
)

const ejerciciosDisponibles = computed(() => {
  const years = [...new Set(remesas.value.map(r => r.fechaCobro?.slice(0, 4)).filter(Boolean))]
  return years.sort().reverse()
})

const remesasFiltradas = computed(() =>
  filtroEjercicioRemesa.value
    ? remesas.value.filter(r => r.fechaCobro?.startsWith(filtroEjercicioRemesa.value))
    : remesas.value
)

const estadoRemesaClass = (nombre) => {
  const map = {
    'Borrador': 'bg-slate-100 text-slate-600',
    'Generada': 'bg-blue-100 text-blue-700',
    'Enviada':  'bg-amber-100 text-amber-700',
    'Procesada':'bg-green-100 text-green-700',
    'Rechazada':'bg-red-100 text-red-700',
    'Parcial':  'bg-orange-100 text-orange-700',
  }
  return map[nombre] || 'bg-slate-100 text-slate-500'
}

const obtenerRemesas = async () => {
  const data = await gqlQuery(`
    query { remesas {
      id referencia importeTotal gastos numOrdenes
      fechaCreacion fechaCobro fechaEnvio
      estado { id nombre }
      agrupacion { id nombre }
    }}
  `)
  remesas.value = (data.remesas || []).sort((a, b) => b.fechaCobro?.localeCompare(a.fechaCobro))
}

const previsualizarCuotas = async () => {
  errorRemesa.value = ''
  previewCargado.value = false
  cuotasPendientesPreview.value = []
  try {
    const vars = { ejercicio: formRemesa.value.ejercicio, agrupacionId: formRemesa.value.agrupacionId || null }
    const data = await gqlQuery(`
      query CuotasPendientes($ejercicio: Int!, $agrupacionId: UUID) {
        cuotasAnuales(filter: {
          ejercicio: { eq: $ejercicio }
          ${formRemesa.value.agrupacionId ? 'agrupacionId: { eq: $agrupacionId }' : ''}
          estado: { nombre: { eq: "Pendiente" } }
        }) { id importe importePagado miembro { nombre apellido1 } }
      }
    `, vars)
    cuotasPendientesPreview.value = data.cuotasAnuales || []
    previewCargado.value = true
  } catch (e) {
    errorRemesa.value = e.message || 'Error al previsualizar'
  }
}

const generarRemesa = async () => {
  if (!formRemesa.value.fechaCobro) { errorRemesa.value = 'Indica la fecha de cobro'; return }
  guardandoRemesa.value = true
  errorRemesa.value = ''
  try {
    await gqlMutation(`
      mutation GenerarRemesa($ejercicio: Int!, $fechaCobro: Date!, $agrupacionId: UUID, $obs: String) {
        generarRemesaSepa(ejercicio: $ejercicio, fechaCobro: $fechaCobro, agrupacionId: $agrupacionId, observaciones: $obs)
      }
    `, {
      ejercicio: formRemesa.value.ejercicio,
      fechaCobro: formRemesa.value.fechaCobro,
      agrupacionId: formRemesa.value.agrupacionId || null,
      obs: formRemesa.value.observaciones || null,
    })
    cuotasPendientesPreview.value = []
    previewCargado.value = false
    await obtenerRemesas()
  } catch (e) {
    errorRemesa.value = e.message || 'Error al generar la remesa'
  } finally {
    guardandoRemesa.value = false
  }
}

const enviarRemesa = async (remesaId) => {
  guardandoRemesa.value = true
  try {
    await gqlMutation(`mutation($id: UUID!) { marcarRemesaEnviada(remesaId: $id) }`, { id: remesaId })
    await obtenerRemesas()
    remesaSeleccionada.value = remesas.value.find(r => r.id === remesaId) || null
  } catch (e) {
    errorRemesa.value = e.message || 'Error'
  } finally {
    guardandoRemesa.value = false
  }
}

const liquidarRemesaSeleccionada = async () => {
  if (!cuentaSeleccionada.value || !remesaSeleccionada.value) return
  guardandoRemesa.value = true
  try {
    await gqlMutation(`
      mutation($remesaId: UUID!, $cuentaId: UUID!) {
        liquidarRemesa(remesaId: $remesaId, cuentaBancariaId: $cuentaId)
      }
    `, { remesaId: remesaSeleccionada.value.id, cuentaId: cuentaSeleccionada.value.id })
    await obtenerRemesas()
    await obtenerCuentasBancarias()
    remesaSeleccionada.value = remesas.value.find(r => r.id === remesaSeleccionada.value.id) || null
  } catch (e) {
    errorRemesa.value = e.message || 'Error al liquidar'
  } finally {
    guardandoRemesa.value = false
  }
}

// Modales
const modalCuenta = ref(false)
const modalMovimiento = ref(false)
const modalConciliacion = ref(false)
const guardando = ref(false)
const errorModal = ref('')

// Formularios
const formCuenta = ref({ nombre: '', iban: '', bancoNombre: '', bicSwift: '', titular: '', agrupacionId: null, descripcion: '' })
const formMovimiento = ref({ fecha: new Date().toISOString().split('T')[0], tipo: 'INGRESO', importe: '', concepto: '', origen: '', referenciaExterna: '', observaciones: '' })
const formConciliacion = ref({ fechaInicio: '', fechaFin: '', saldoInicialExtracto: 0, saldoFinalExtracto: 0, observaciones: '' })

const tabs = [
  { id: 'cuentas', name: 'Cuentas', icon: '🏦' },
  { id: 'movimientos', name: 'Movimientos', icon: '💸' },
  { id: 'remesas', name: 'Remesas', icon: '📋' },
  { id: 'conciliaciones', name: 'Conciliaciones', icon: '✓' },
]

const totales = computed(() => calcularTotales.value)

const movimientosFiltrados = computed(() => {
  return apuntesCaja.value.filter(m => {
    if (filtroTipo.value && m.tipo !== filtroTipo.value) return false
    if (filtroFechaInicio.value && m.fecha < filtroFechaInicio.value) return false
    if (filtroFechaFin.value && m.fecha > filtroFechaFin.value) return false
    return true
  })
})

// Helpers de formato
const fmt = (val) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(val ?? 0)
const fechaFmt = (d) => d ? new Intl.DateTimeFormat('es-ES').format(new Date(d)) : ''
const ibanFmt = (iban) => iban ? (iban.slice(0, 4) + ' **** **** **** ' + iban.slice(-4)) : ''

// Acciones
const seleccionarCuenta = async (cuenta) => {
  cuentaSeleccionada.value = cuenta
  activeTab.value = 'movimientos'
  await recargarMovimientos()
}

const recargarMovimientos = async () => {
  if (!cuentaSeleccionada.value) return
  await obtenerApuntesCaja(cuentaSeleccionada.value.id)
}

// Modales
const abrirNuevaCuenta = () => {
  formCuenta.value = { nombre: '', iban: '', bancoNombre: '', bicSwift: '', titular: '', agrupacionId: null, descripcion: '' }
  errorModal.value = ''
  modalCuenta.value = true
}

const abrirNuevoMovimiento = () => {
  formMovimiento.value = { fecha: new Date().toISOString().split('T')[0], tipo: 'INGRESO', importe: '', concepto: '', origen: '', referenciaExterna: '', observaciones: '' }
  errorModal.value = ''
  modalMovimiento.value = true
}

const abrirNuevaConciliacion = () => {
  formConciliacion.value = { fechaInicio: '', fechaFin: '', saldoInicialExtracto: 0, saldoFinalExtracto: 0, observaciones: '' }
  errorModal.value = ''
  modalConciliacion.value = true
}

// Guardar
const guardarCuenta = async () => {
  errorModal.value = ''
  if (!formCuenta.value.nombre || !formCuenta.value.iban) {
    errorModal.value = 'Nombre e IBAN son obligatorios'
    return
  }
  guardando.value = true
  try {
    await crearCuentaBancaria(formCuenta.value)
    modalCuenta.value = false
    await obtenerCuentasBancarias()
  } catch (e) {
    errorModal.value = e.message || 'Error al guardar la cuenta'
  } finally {
    guardando.value = false
  }
}

const guardarMovimiento = async () => {
  errorModal.value = ''
  if (!formMovimiento.value.concepto || !formMovimiento.value.importe) {
    errorModal.value = 'Concepto e importe son obligatorios'
    return
  }
  guardando.value = true
  try {
    await registrarApunte({
      cuentaId: cuentaSeleccionada.value.id,
      ...formMovimiento.value,
      importe: parseFloat(formMovimiento.value.importe),
      origen: formMovimiento.value.origen || null,
    })
    modalMovimiento.value = false
    await recargarMovimientos()
    await obtenerCuentasBancarias()
  } catch (e) {
    errorModal.value = e.message || 'Error al registrar el movimiento'
  } finally {
    guardando.value = false
  }
}

const guardarConciliacion = async () => {
  errorModal.value = ''
  if (!formConciliacion.value.fechaInicio || !formConciliacion.value.fechaFin) {
    errorModal.value = 'Las fechas son obligatorias'
    return
  }
  guardando.value = true
  try {
    await crearConciliacion({
      cuentaBancariaId: cuentaSeleccionada.value.id,
      ...formConciliacion.value,
      saldoInicialExtracto: parseFloat(formConciliacion.value.saldoInicialExtracto),
      saldoFinalExtracto: parseFloat(formConciliacion.value.saldoFinalExtracto),
    })
    modalConciliacion.value = false
    await obtenerConciliaciones(cuentaSeleccionada.value.id)
  } catch (e) {
    errorModal.value = e.message || 'Error al crear la conciliación'
  } finally {
    guardando.value = false
  }
}

const conciliarMovimiento = async (apunteId) => {
  if (!confirm('¿Marcar este movimiento como conciliado?')) return
  try {
    await marcarApunteConciliado(apunteId)
    await recargarMovimientos()
  } catch (e) {
    alert(e.message || 'Error al conciliar')
  }
}

const confirmarConciliacion = async (conciliacionId) => {
  if (!confirm('¿Confirmar esta conciliación?')) return
  try {
    await confirmarConciliacionPeriodo(conciliacionId)
    await obtenerConciliaciones(cuentaSeleccionada.value.id)
  } catch (e) {
    alert(e.message || 'Error al confirmar')
  }
}

onMounted(async () => {
  await obtenerCuentasBancarias()
  await obtenerRemesas()
})
</script>

<style scoped>
.btn-primary { @apply px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed; }
.btn-secondary { @apply px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm font-medium; }
.label { @apply block text-sm font-medium text-gray-700 mb-1; }
.input { @apply w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent; }
.input-sm { @apply px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400; }
</style>
PayPal
 cuenta_haber_codigo, descripcion, orden, activa
 Busca regla específica primero, luego comodín (origen=NULL)
 Idempotente: solo inserta si la tabla está vacía
 ReglaContableFilter
 Muestra origen (o 'Comodín'), tipo, cuentas, descripción, orden, estado
 Ruta: /reglas-contables
 recibo_cuota(cuota_id) → PDF A4 con datos socio, ejercicio, importe
 recibo_apunte(apunte_id) → PDF justificante de movimiento
 HTML → PDF via WeasyPrint (pip install weasyprint)
 Props: importe, concepto, moneda, cuotaId, miembroId, cuentaBancariaId, clientId
 Emits: pago-completado, pago-cancelado, error
 PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET
 PAYPAL_MODE=sandbox|live
 PAYPAL_WEBHOOK_ID
.../b1c2d3e4f5a6_add_reglas_contables.py      |  56 ++++
backend/app/api/__init__.py                   |   1 +
backend/app/api/paypal.py                     | 164 +++++++++++
backend/app/api/recibos.py                    |  66 +++++
.../app/domains/financiero/models/__init__.py |   2 +
.../models/contabilidad/__init__.py           |   2 +
.../models/contabilidad/regla_contable.py     |  44 +++
.../domains/financiero/services/__init__.py   |   3 +-
.../financiero/services/registro_contable.py  |  77 +++---
.../services/reglas_contables_service.py      |  94 +++++++
backend/app/graphql/inputs_auto.py            |  16 ++
backend/app/graphql/mutations.py              |   5 +
backend/app/graphql/schema_simple.py          |   1 +
backend/app/graphql/types_auto.py             |   8 +
.../seeding/reglas_contables_default.py       |  50 ++++
backend/app/services/paypal_service.py        | 259 ++++++++++++++++++
backend/app/services/pdf/__init__.py          |   1 +
backend/app/services/pdf/recibo_service.py    | 246 +++++++++++++++++
backend/main.py                               |   7 +
.../src/components/paypal/PayPalButton.vue    | 126 +++++++++
frontend/src/router/index.js                  |   1 +
.../src/views/financiero/ReglasContables.vue  | 199 ++++++++++++++
22 files changed, 1390 insertions(+), 38 deletions(-)
create mode 100644 backend/alembic/versions/b1c2d3e4f5a6_add_reglas_contables.py
create mode 100644 backend/app/api/__init__.py
create mode 100644 backend/app/api/paypal.py
create mode 100644 backend/app/api/recibos.py
create mode 100644 backend/app/domains/financiero/models/contabilidad/regla_contable.py
create mode 100644 backend/app/domains/financiero/services/reglas_contables_service.py
create mode 100644 backend/app/scripts/seeding/reglas_contables_default.py
create mode 100644 backend/app/services/paypal_service.py
create mode 100644 backend/app/services/pdf/__init__.py
create mode 100644 backend/app/services/pdf/recibo_service.py
create mode 100644 frontend/src/components/paypal/PayPalButton.vue
create mode 100644 frontend/src/views/financiero/ReglasContables.vue
