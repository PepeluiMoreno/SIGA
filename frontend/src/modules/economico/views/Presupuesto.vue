<template>
  <AppLayout title="Presupuestos" subtitle="Planificación presupuestaria anual y partidas">

    <!-- Línea temporal de ejercicios (clicable) -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm px-4 py-3 mb-4">
      <div class="flex items-center justify-between mb-1">
        <h2 class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Ejercicios</h2>
        <router-link to="/economico/presupuesto-evolucion"
          class="text-xs text-indigo-600 hover:underline whitespace-nowrap">
          Ver evolución ↗
        </router-link>
      </div>
      <LineaTiempoPresupuesto
        :ejercicios="ejerciciosTimeline"
        :seleccionado="ejercicioActual"
        @select="irAEjercicio"
      />
    </div>

    <!-- Selector de borradores del ejercicio (varios borradores posibles) -->
    <div v-if="!loading && planificacion && puedeCrear && !hayDefinitiva"
      class="flex items-center gap-2 mb-3 flex-wrap">
      <span class="text-xs font-medium text-slate-500">Borradores:</span>
      <button v-for="p in planesEjercicio" :key="p.id"
        @click="seleccionarPlan(p.id)"
        :class="['text-xs px-2.5 py-1 rounded border', p.id === planificacion.id
          ? 'bg-indigo-600 text-white border-indigo-600'
          : 'bg-white text-slate-600 border-slate-300 hover:bg-slate-50']">
        {{ p.nombre }}
      </button>
      <button @click="crearOtroBorrador" :disabled="ocupado"
        class="text-xs px-2.5 py-1 rounded border border-dashed border-slate-300 text-slate-500 hover:bg-slate-50 disabled:opacity-50">
        + nuevo
      </button>
      <button @click="abrirCreador"
        class="text-xs px-2.5 py-1 rounded border border-dashed border-slate-300 text-slate-500 hover:bg-slate-50">
        + clonar otro
      </button>
    </div>

    <EstadoCarga v-if="loading" />

    <!-- Creador de presupuesto: nuevo / clonar / prorrogar (panel unificado) -->
    <div v-if="!loading && mostrarCreador" class="mb-4 max-w-2xl mx-auto">
      <CreadorPresupuesto
        :ejercicio="ejercicioActual"
        :ratio-cuota="ratioCuota"
        :puede-clonarse="hayPlanEjercicioAnterior"
        :puede-prorrogarse="puedeAprobar && hayDefinitivaAnterior"
        :ocupado="ocupado"
        @cancel="mostrarCreador = false"
        @modo-cambiado="onModoCreador"
        @crear="onCrearPresupuesto"
      />
    </div>

    <!-- Sin presupuesto del ejercicio: ofrecer crearlo -->
    <div v-if="!loading && !planificacion && !mostrarCreador" class="bg-white rounded-lg shadow border border-gray-200 p-8">

      <!-- Aviso si no hay cuota configurada para el ejercicio -->
      <div v-if="puedeCrear && cuotaEjercicio === null"
        class="mb-5 bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-800">
        <p class="font-semibold mb-1">No hay cuota establecida para {{ ejercicioActual }}</p>
        <p>Para elaborar el presupuesto de ingresos primero debes
          <router-link to="/economico/cuotas-ejercicio" class="underline font-medium hover:text-amber-900">
            configurar la cuota del ejercicio {{ ejercicioActual }}
          </router-link>.
        </p>
      </div>

      <div class="text-center">
        <p class="font-medium text-gray-700 mb-1">No hay presupuesto para {{ ejercicioActual }}</p>
        <p class="text-sm text-gray-500 mb-4">Crea la planificación anual para empezar a presupuestar.</p>
        <button v-if="puedeCrear && cuotaEjercicio !== null" @click="abrirCreador"
          class="px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700">
          Crear presupuesto {{ ejercicioActual }}
        </button>
        <p v-else-if="puedeCrear && cuotaEjercicio === null" class="text-xs text-slate-500 mt-2">
          Establece la cuota para poder crear el presupuesto.
        </p>
      </div>
    </div>

    <AccordionGroup v-if="!loading && planificacion">
      <!-- Panel 1: Cabecera y estado -->
      <AccordionPanel :default-open="true">
        <template #title>
          <div class="flex items-center gap-3">
            <h2 class="text-sm font-semibold text-slate-800">Presupuesto {{ planificacion.ejercicio }}</h2>
            <span class="text-xs px-2 py-0.5 rounded-full text-white" :style="{ backgroundColor: estadoColor }">
              {{ estadoNombre }}
            </span>
            <span v-if="planificacion.esProrroga"
              class="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">
              Prórroga de {{ planificacion.ejercicioOrigenProrroga }}
            </span>
          </div>
        </template>

        <div class="px-5 py-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <div class="bg-green-50 rounded-lg p-3">
              <p class="text-xs text-green-700">Ingresos previstos</p>
              <p class="text-lg font-semibold text-green-800">{{ eur(planificacion.presupuestoIngresos) }}</p>
            </div>
            <div class="bg-red-50 rounded-lg p-3">
              <p class="text-xs text-red-700">Gastos previstos</p>
              <p class="text-lg font-semibold text-red-800">{{ eur(planificacion.presupuestoGastos) }}</p>
            </div>
            <div class="rounded-lg p-3" :class="planificacion.saldoPresupuestado >= 0 ? 'bg-blue-50' : 'bg-amber-50'">
              <p class="text-xs" :class="planificacion.saldoPresupuestado >= 0 ? 'text-blue-700' : 'text-amber-700'">Saldo</p>
              <p class="text-lg font-semibold" :class="planificacion.saldoPresupuestado >= 0 ? 'text-blue-800' : 'text-amber-800'">
                {{ eur(planificacion.saldoPresupuestado) }}
              </p>
            </div>
            <div class="bg-purple-50 rounded-lg p-3">
              <p class="text-xs text-purple-700">Ejecución</p>
              <p class="text-lg font-semibold text-purple-800">{{ planificacion.porcentajeEjecucion }}%</p>
            </div>
          </div>

          <!-- Botones de transición según el estado -->
          <div v-if="puedeGestionar" class="flex flex-wrap gap-2">
            <button v-if="estadoCodigo === 'BORRADOR'" @click="transicion('proponer')" :disabled="ocupado"
              class="btn-estado bg-blue-600 hover:bg-blue-700">Proponer</button>
            <button v-if="estadoCodigo === 'PROPUESTO'" @click="transicion('devolver')" :disabled="ocupado"
              class="btn-estado bg-gray-500 hover:bg-gray-600">Volver a borrador</button>
            <button v-if="estadoCodigo === 'PROPUESTO' && puedeAprobar" @click="transicion('aprobar')" :disabled="ocupado"
              class="btn-estado bg-green-600 hover:bg-green-700">Aprobar</button>
            <button v-if="estadoCodigo === 'APROBADO' && puedeAprobar" @click="transicion('ejecutar')" :disabled="ocupado"
              class="btn-estado bg-purple-600 hover:bg-purple-700">Iniciar ejecución</button>
            <button v-if="estadoCodigo === 'EN_EJECUCION' && puedeAprobar" @click="transicion('cerrar')" :disabled="ocupado"
              class="btn-estado bg-gray-800 hover:bg-gray-900">Cerrar ejercicio</button>
            <button v-if="esBorradorEliminable" @click="eliminarBorrador" :disabled="ocupado"
              class="btn-estado bg-red-600 hover:bg-red-700 ml-auto">Eliminar borrador</button>
          </div>
          <p v-if="planificacion.fechaAprobacion" class="text-xs text-gray-400 mt-2">
            Aprobado el {{ planificacion.fechaAprobacion }}
          </p>

        </div>
      </AccordionPanel>

      <!-- Panel 2: Ingresos -->
      <AccordionPanel title="Ingresos" :count="partidasIngreso.length">
        <PartidasPorCategoria
          tipo="INGRESO"
          :partidas="partidasIngreso"
          :categorias="categorias"
          :editable="editable"
          @crear="crearPartida"
          @actualizar="actualizarPartida"
          @eliminar="eliminarPartida"
        />
      </AccordionPanel>

      <!-- Panel 3: Gastos -->
      <AccordionPanel title="Gastos" :count="partidasGasto.length">
        <PartidasPorCategoria
          tipo="GASTO"
          :partidas="partidasGasto"
          :categorias="categorias"
          :editable="editable"
          @crear="crearPartida"
          @actualizar="actualizarPartida"
          @eliminar="eliminarPartida"
        />
      </AccordionPanel>

      <!-- Panel: Alertas (solo en aprobado/ejecución, no en cerrado) -->
      <AccordionPanel v-if="esAprobadoOEjecucion && alertas.length" title="Alertas" :count="alertas.length" :default-open="true">
        <div class="px-5 py-4 space-y-2">
          <div v-for="a in alertas" :key="a.partidaId"
            class="flex items-start gap-2 text-sm rounded-lg px-3 py-2"
            :class="a.tipoAlerta === 'SOBREEJECUTADA' ? 'bg-red-50 text-red-700' : 'bg-amber-50 text-amber-700'">
            <span class="font-medium">{{ a.codigo }} — {{ a.nombre }}:</span>
            <span>{{ a.mensaje }}</span>
          </div>
        </div>
      </AccordionPanel>

      <!-- Panel: Modificaciones presupuestarias (solo aprobado/ejecución, no en cerrado) -->
      <AccordionPanel v-if="esAprobadoOEjecucion" title="Modificaciones presupuestarias"
        :count="modificaciones.length" :default-open="false">
        <ModificacionesPresupuestarias
          :modificaciones="modificaciones"
          :partidas="partidas"
          :puede-modificar="puedeAprobar && esAprobadoOEjecucion"
          @registrar="registrarModificacion"
        />
      </AccordionPanel>

      <!-- Panel 4: Seguimiento de ejecución — abierto por defecto en CERRADO -->
      <AccordionPanel title="Seguimiento de ejecución" :default-open="estadoCodigo === 'CERRADO'">
        <div class="px-5 py-4">
          <p class="text-sm text-gray-500 mb-3">
            Comparativa de lo presupuestado frente a lo ejecutado realmente, por partida.
          </p>
          <div v-if="!desviaciones.length" class="text-center text-gray-400 py-6 text-sm">
            Aún no hay datos de ejecución.
          </div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-50 text-xs text-gray-500">
                <tr>
                  <th class="px-3 py-2 text-left">Partida</th>
                  <th class="px-3 py-2 text-right">Presupuestado</th>
                  <th class="px-3 py-2 text-right">Ejecutado</th>
                  <th class="px-3 py-2 text-right">Disponible</th>
                  <th class="px-3 py-2 text-right">Desviación</th>
                  <th class="px-3 py-2 text-center">% Ejec.</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="d in desviaciones" :key="d.partidaId" class="hover:bg-gray-50">
                  <td class="px-3 py-2">
                    <span class="text-xs text-gray-400 font-mono mr-1">{{ d.codigo }}</span>{{ d.nombre }}
                  </td>
                  <td class="px-3 py-2 text-right">{{ eur(d.presupuestado) }}</td>
                  <td class="px-3 py-2 text-right">{{ eur(d.ejecutado) }}</td>
                  <td class="px-3 py-2 text-right" :class="d.disponible < 0 ? 'text-red-600 font-medium' : ''">{{ eur(d.disponible) }}</td>
                  <td class="px-3 py-2 text-right" :class="d.desviacion > 0 ? 'text-red-600' : 'text-green-600'">{{ eur(d.desviacion) }}</td>
                  <td class="px-3 py-2 text-center">
                    <span class="text-xs px-1.5 py-0.5 rounded"
                      :class="d.porcentajeEjecucion > 100 ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600'">
                      {{ d.porcentajeEjecucion }}%
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </AccordionPanel>

      <!-- Panel: Comparativa interanual -->
      <AccordionPanel title="Comparativa interanual" :default-open="false">
        <div class="px-5 py-4">
          <p class="text-sm text-gray-500 mb-3">
            Partidas de {{ planificacion.ejercicio }} frente a {{ planificacion.ejercicio - 1 }}.
          </p>
          <div v-if="!comparativa.length" class="text-center text-gray-400 py-6 text-sm">
            No hay presupuesto del ejercicio anterior para comparar.
          </div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-50 text-xs text-gray-500">
                <tr>
                  <th class="px-3 py-2 text-left">Partida</th>
                  <th class="px-3 py-2 text-right">{{ planificacion.ejercicio - 1 }}</th>
                  <th class="px-3 py-2 text-right">{{ planificacion.ejercicio }}</th>
                  <th class="px-3 py-2 text-right">Variación</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="c in comparativa" :key="c.codigo" class="hover:bg-gray-50">
                  <td class="px-3 py-2">
                    <span class="text-xs text-gray-400 font-mono mr-1">{{ c.codigo }}</span>{{ c.nombre }}
                  </td>
                  <td class="px-3 py-2 text-right text-gray-500">{{ eur(c.importeAnterior) }}</td>
                  <td class="px-3 py-2 text-right">{{ eur(c.importeActual) }}</td>
                  <td class="px-3 py-2 text-right" :class="c.variacion > 0 ? 'text-green-600' : c.variacion < 0 ? 'text-red-600' : 'text-gray-400'">
                    {{ c.variacion >= 0 ? '+' : '' }}{{ eur(c.variacion) }}
                    <span v-if="c.variacionPorcentaje !== null" class="text-xs">({{ c.variacionPorcentaje >= 0 ? '+' : '' }}{{ c.variacionPorcentaje }}%)</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </AccordionPanel>

      <!-- Panel: Liquidación — abierto por defecto en CERRADO -->
      <AccordionPanel title="Liquidación del presupuesto" :default-open="estadoCodigo === 'CERRADO'">
        <div class="px-5 py-4">
          <p class="text-sm text-gray-500 mb-3">
            Resumen previsto frente a ejecutado del ejercicio, para incorporar a la Memoria
            de las cuentas anuales.
          </p>
          <div v-if="liquidacion" class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="bg-gray-50 rounded-lg p-3">
              <p class="text-xs text-gray-500 mb-1">Ingresos</p>
              <p class="text-sm">Previsto: {{ eur(liquidacion.ingresosPrevistos) }}</p>
              <p class="text-sm">Ejecutado: <strong>{{ eur(liquidacion.ingresosEjecutados) }}</strong></p>
            </div>
            <div class="bg-gray-50 rounded-lg p-3">
              <p class="text-xs text-gray-500 mb-1">Gastos</p>
              <p class="text-sm">Previsto: {{ eur(liquidacion.gastosPrevistos) }}</p>
              <p class="text-sm">Ejecutado: <strong>{{ eur(liquidacion.gastosEjecutados) }}</strong></p>
            </div>
            <div class="bg-blue-50 rounded-lg p-3">
              <p class="text-xs text-blue-700 mb-1">Resultado</p>
              <p class="text-sm">Previsto: {{ eur(liquidacion.resultadoPrevisto) }}</p>
              <p class="text-sm">Ejecutado: <strong>{{ eur(liquidacion.resultadoEjecutado) }}</strong></p>
            </div>
            <div class="bg-purple-50 rounded-lg p-3 flex flex-col justify-center">
              <p class="text-xs text-purple-700 mb-1">Grado de ejecución de gastos</p>
              <p class="text-2xl font-semibold text-purple-800">{{ liquidacion.gradoEjecucionGastos }}%</p>
            </div>
          </div>
        </div>
      </AccordionPanel>
    </AccordionGroup>

    <!-- Modal de confirmación reutilizable -->
    <ConfirmActionModal
      v-model="modal.abierto"
      :titulo="modal.titulo"
      :mensaje="modal.mensaje"
      :etiqueta-confirmar="modal.etiquetaConfirmar"
      :variante="modal.variante"
      @confirm="onConfirmModal"
      @cancel="onCancelModal"
    />
  </AppLayout>
</template>

<script setup>
import { useToast } from '@/composables/useToast'
import { ref, computed, watch, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import AccordionGroup from '@/components/common/AccordionGroup.vue'
import AccordionPanel from '@/components/common/AccordionPanel.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import LineaTiempoPresupuesto from '@/components/economico/LineaTiempoPresupuesto.vue'
import CreadorPresupuesto from '@/components/economico/CreadorPresupuesto.vue'
import PartidasPorCategoria from '@/modules/economico/components/PartidasPorCategoria.vue'
import ModificacionesPresupuestarias from '@/modules/economico/components/ModificacionesPresupuestarias.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import { usePermisos } from '@/composables/usePermisos.js'
import {
  GET_PLANIFICACIONES, GET_PARTIDAS, GET_INFORME_DESVIACIONES, GET_ESTADOS_PLANIFICACION,
  CREAR_PLANIFICACION, CREAR_PARTIDA, ACTUALIZAR_PARTIDA, ELIMINAR_PARTIDA,
  ELIMINAR_PLANIFICACION,
  PROPONER_PRESUPUESTO, APROBAR_PRESUPUESTO, INICIAR_EJECUCION_PRESUPUESTO,
  CERRAR_PRESUPUESTO, DEVOLVER_A_BORRADOR,
  GET_MODIFICACIONES, GET_ALERTAS, REGISTRAR_MODIFICACION,
  GET_COMPARATIVA_INTERANUAL, GET_LIQUIDACION, CLONAR_PRESUPUESTO, PRORROGAR_PRESUPUESTO,
  GET_RATIO_VARIACION_CUOTA,
} from '@/graphql/queries/presupuestos.js'
import { GET_CONFIG_CUOTA_EJERCICIO } from '@/graphql/queries/economico'
import ConfirmActionModal from '@/components/common/ConfirmActionModal.vue'
const toast = useToast()

const { query, mutation } = useGraphQL()
const { tienePermiso } = usePermisos()

// ── Modal de confirmación genérico ──────────────────────────────────────────
const modal = ref({
  abierto: false, titulo: '', mensaje: '',
  etiquetaConfirmar: 'Confirmar', variante: 'aviso', _resolver: null,
})
const confirmarAccion = (opts) => new Promise((resolve) => {
  modal.value = {
    abierto: true,
    titulo: opts.titulo,
    mensaje: opts.mensaje,
    etiquetaConfirmar: opts.etiquetaConfirmar || 'Confirmar',
    variante: opts.variante || 'aviso',
    _resolver: resolve,
  }
})
const onConfirmModal = () => { const r = modal.value._resolver; modal.value.abierto = false; r?.(true) }
const onCancelModal  = () => { const r = modal.value._resolver; modal.value.abierto = false; r?.(false) }

const puedeCrear = computed(() => tienePermiso('ECO_PRESUPUESTO_CREAR'))
const puedeGestionar = computed(() => tienePermiso('ECO_PRESUPUESTO_CREAR'))
const puedeAprobar = computed(() => tienePermiso('ECO_PRESUPUESTO_APROBAR'))

const loading = ref(false)
const ocupado = ref(false)
const planificacion = ref(null)
const planesEjercicio = ref([])   // todos los presupuestos (borradores incl.) del ejercicio
const todosPlanes = ref([])       // todos los presupuestos de todos los ejercicios (para el timeline)
const partidas = ref([])
const desviaciones = ref([])
const estados = ref([])
const categorias = ref([])
const modificaciones = ref([])
const alertas = ref([])
const comparativa = ref([])
const liquidacion = ref(null)

const _hoy = new Date().getFullYear()
const _mes  = new Date().getMonth() + 1   // 1-12
const ejercicioActual = ref(_hoy)
const todosEjercicios = ref([])
const nuevoEjercicio = computed(() => ejercicioActual.value)
const mostrarCreador = ref(false)
const ratioCuota = ref(null)
const cuotaEjercicio = ref(undefined)  // undefined=cargando, null=no existe, objeto=existe

// ¿Hay algún presupuesto del ejercicio anterior para clonar?
const hayPlanEjercicioAnterior = computed(() =>
  todosPlanes.value.some(p => p.ejercicio === ejercicioActual.value - 1))
// ¿El ejercicio anterior tiene un presupuesto definitivo (aprobado+) para prorrogar?
const hayDefinitivaAnterior = computed(() =>
  todosPlanes.value.some(p =>
    p.ejercicio === ejercicioActual.value - 1 &&
    ['APROBADO', 'EN_EJECUCION', 'CERRADO'].includes(codigoEstadoDe(p))))

async function cargarRatioCuota() {
  ratioCuota.value = null
  try {
    const data = await query(GET_RATIO_VARIACION_CUOTA, {
      ejercicioOrigen: nuevoEjercicio.value - 1,
      ejercicioNuevo: nuevoEjercicio.value,
    })
    ratioCuota.value = data.ratioVariacionCuota
  } catch {
    ratioCuota.value = { disponible: false }
  }
}

function abrirCreador() {
  mostrarCreador.value = true
}

// Cuando el usuario elige el modo "clonar" en el creador, cargamos el ratio de cuota
function onModoCreador(modo) {
  if (modo === 'clonar' && ratioCuota.value === null) cargarRatioCuota()
}

// El creador emite { modo, factor }
async function onCrearPresupuesto({ modo, factor }) {
  if (modo === 'nuevo')          await crearPlanificacion()
  else if (modo === 'clonar')    await clonarDelAnterior(factor)
  else if (modo === 'prorrogar') await prorrogarDelAnterior()
  mostrarCreador.value = false
}

const partidasIngreso = computed(() => partidas.value.filter(p => p.tipo === 'INGRESO'))
const partidasGasto = computed(() => partidas.value.filter(p => p.tipo === 'GASTO'))

const estadoActual = computed(() => estados.value.find(e => e.id === planificacion.value?.estadoId))
const estadoCodigo = computed(() => estadoActual.value?.codigo ?? 'BORRADOR')
const estadoNombre = computed(() => estadoActual.value?.nombre ?? '—')
const estadoColor = computed(() => estadoActual.value?.color ?? '#9ca3af')

const codigoEstadoDe = (plan) =>
  estados.value.find(e => e.id === plan?.estadoId)?.codigo ?? 'BORRADOR'

// Datos para la línea de tiempo de presupuesto: un nodo por ejercicio con su estado más relevante.
// Para cada año se elige el plan definitivo (aprobado+) o, si solo hay borradores,
// el estado del primero. Si no hay ningún plan, estado null (nodo "+", crear).
const ejerciciosTimeline = computed(() =>
  todosEjercicios.value.map((anio) => {
    const delAnio = todosPlanes.value.filter(p => p.ejercicio === anio)
    if (!delAnio.length) return { anio, estado: null }
    const definitivo = delAnio.find(p =>
      ['APROBADO', 'EN_EJECUCION', 'CERRADO'].includes(codigoEstadoDe(p)))
    return { anio, estado: codigoEstadoDe(definitivo ?? delAnio[0]) }
  })
)

// ¿El ejercicio ya tiene un presupuesto definitivo (aprobado o posterior)?
const hayDefinitiva = computed(() =>
  planesEjercicio.value.some(p => ['APROBADO', 'EN_EJECUCION', 'CERRADO'].includes(codigoEstadoDe(p))))
// El plan mostrado es un borrador eliminable
const esBorradorEliminable = computed(() =>
  planificacion.value && ['BORRADOR', 'PROPUESTO'].includes(estadoCodigo.value))
// Solo se editan partidas mientras el presupuesto no está aprobado
const editable = computed(() => puedeGestionar.value && ['BORRADOR', 'PROPUESTO'].includes(estadoCodigo.value))
const esAprobadoOEjecucion = computed(() => ['APROBADO', 'EN_EJECUCION'].includes(estadoCodigo.value))

const eur = (n) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n || 0)

const irAEjercicio = async (ej) => {
  ejercicioActual.value = ej
  mostrarCreador.value = false
  ratioCuota.value = null
  await cargar()
}

const cargar = async () => {
  loading.value = true
  cuotaEjercicio.value = undefined
  try {
    const [dataEstados, dataPlanes, dataCuota] = await Promise.all([
      query(GET_ESTADOS_PLANIFICACION),
      query(GET_PLANIFICACIONES),
      query(GET_CONFIG_CUOTA_EJERCICIO, { ejercicio: ejercicioActual.value }),
    ])
    estados.value = dataEstados?.estadosPlanificacion ?? []
    const planes = dataPlanes?.planificaciones ?? []
    todosPlanes.value = planes
    cuotaEjercicio.value = (dataCuota?.importesCuotaAnio ?? [])[0] ?? null
    // Construir lista de ejercicios disponibles (existentes + año actual; siguiente solo desde oct.)
    const ejerciciosExistentes = planes.map(p => p.ejercicio)
    const base = _mes >= 10 ? [_hoy, _hoy + 1] : [_hoy]
    const conjunto = new Set([...ejerciciosExistentes, ...base])
    todosEjercicios.value = [...conjunto].sort((a, b) => a - b)
    // Todos los presupuestos del ejercicio (puede haber varios borradores)
    planesEjercicio.value = planes.filter(p => p.ejercicio === ejercicioActual.value)
    planificacion.value = elegirPlanRelevante(planesEjercicio.value)
    if (planificacion.value) await cargarDetalle()
  } catch (e) {
    console.error('Error cargando presupuesto:', e?.message || e)
  } finally {
    loading.value = false
  }
}

const cargarDetalle = async () => {
  const id = planificacion.value.id
  const ej = planificacion.value.ejercicio
  const [dataPart, dataDesv, dataMod, dataAlert, dataComp, dataLiq] = await Promise.all([
    query(GET_PARTIDAS, { planificacionId: id }),
    query(GET_INFORME_DESVIACIONES, { planificacionId: id }),
    query(GET_MODIFICACIONES, { planificacionId: id }),
    query(GET_ALERTAS, { planificacionId: id }),
    query(GET_COMPARATIVA_INTERANUAL, { ejercicio: ej }),
    query(GET_LIQUIDACION, { ejercicio: ej }),
  ])
  partidas.value = dataPart?.partidasPresupuestarias ?? []
  desviaciones.value = dataDesv?.informeDesviaciones ?? []
  modificaciones.value = dataMod?.modificacionesPresupuestarias ?? []
  alertas.value = dataAlert?.alertasPresupuestarias ?? []
  comparativa.value = dataComp?.comparativaInteranual ?? []
  const liq = dataLiq?.liquidacionPresupuestaria
  liquidacion.value = liq?.existe ? liq : null
}

const recargarPlan = async () => {
  const data = await query(GET_PLANIFICACIONES)
  const planes = data?.planificaciones ?? []
  planificacion.value = planes.find(p => p.id === planificacion.value?.id) ?? planificacion.value
}

// De entre los presupuestos del ejercicio, elige el definitivo (aprobado+) o el primer borrador.
function elegirPlanRelevante(lista) {
  if (!lista.length) return null
  const definitiva = lista.find(p =>
    ['APROBADO', 'EN_EJECUCION', 'CERRADO'].includes(codigoEstadoDe(p)))
  return definitiva ?? lista[0]
}

const seleccionarPlan = async (planId) => {
  const elegido = planesEjercicio.value.find(p => p.id === planId)
  if (!elegido) return
  planificacion.value = elegido
  await cargarDetalle()
}

const eliminarBorrador = async () => {
  if (!planificacion.value) return
  const ok = await confirmarAccion({
    titulo: 'Eliminar borrador',
    mensaje: `¿Eliminar el borrador «${planificacion.value.nombre}»? Esta acción no se puede deshacer.`,
    etiquetaConfirmar: 'Eliminar',
    variante: 'critica',
  })
  if (!ok) return
  ocupado.value = true
  try {
    await mutation(ELIMINAR_PLANIFICACION, { planificacionId: planificacion.value.id })
    await cargar()
  } catch (e) {
    console.error(e?.message || e)
  } finally {
    ocupado.value = false
  }
}

const crearOtroBorrador = async () => {
  ocupado.value = true
  try {
    const n = planesEjercicio.value.length + 1
    await mutation(CREAR_PLANIFICACION, {
      data: { ejercicio: ejercicioActual.value, nombre: `Presupuesto ${ejercicioActual.value} — borrador ${n}` },
    })
    await cargar()
  } catch (e) {
    console.error(e?.message || e)
    toast.error(e?.message || 'No se pudo crear el borrador')
  } finally {
    ocupado.value = false
  }
}

const crearPlanificacion = async () => {
  ocupado.value = true
  try {
    await mutation(CREAR_PLANIFICACION, {
      data: { ejercicio: nuevoEjercicio.value, nombre: `Presupuesto ${nuevoEjercicio.value}` },
    })
    await cargar()
  } catch (e) {
    console.error(e?.message || e)
  } finally {
    ocupado.value = false
  }
}

const crearPartida = async (datos) => {
  await mutation(CREAR_PARTIDA, {
    data: { planificacionId: planificacion.value.id, ...datos },
  })
  await cargarDetalle()
  await recargarPlan()
}

const actualizarPartida = async (datos) => {
  await mutation(ACTUALIZAR_PARTIDA, { data: datos })
  await cargarDetalle()
  await recargarPlan()
}

const eliminarPartida = async (partidaId) => {
  await mutation(ELIMINAR_PARTIDA, { partidaId })
  await cargarDetalle()
  await recargarPlan()
}

const transicion = async (cual) => {
  ocupado.value = true
  const mut = {
    proponer: PROPONER_PRESUPUESTO, aprobar: APROBAR_PRESUPUESTO,
    ejecutar: INICIAR_EJECUCION_PRESUPUESTO, cerrar: CERRAR_PRESUPUESTO,
    devolver: DEVOLVER_A_BORRADOR,
  }[cual]
  try {
    await mutation(mut, { planificacionId: planificacion.value.id })
    await recargarPlan()
  } catch (e) {
    console.error(e?.message || e)
  } finally {
    ocupado.value = false
  }
}

const registrarModificacion = async (datos) => {
  await mutation(REGISTRAR_MODIFICACION, {
    data: { planificacionId: planificacion.value.id, ...datos },
  })
  await cargarDetalle()
  await recargarPlan()
}

const clonarDelAnterior = async (factor = null) => {
  ocupado.value = true
  try {
    await mutation(CLONAR_PRESUPUESTO, {
      ejercicioOrigen: nuevoEjercicio.value - 1,
      ejercicioNuevo: nuevoEjercicio.value,
      factor,
    })
    await cargar()
    toast.success(`Presupuesto ${nuevoEjercicio.value} creado clonando ${nuevoEjercicio.value - 1}`)
  } catch (e) {
    console.error(e?.message || e)
    toast.error(e?.message || 'No se pudo clonar el presupuesto')
  } finally {
    ocupado.value = false
  }
}

const prorrogarDelAnterior = async () => {
  ocupado.value = true
  try {
    await mutation(PRORROGAR_PRESUPUESTO, {
      ejercicioOrigen: nuevoEjercicio.value - 1, ejercicioNuevo: nuevoEjercicio.value,
    })
    await cargar()
    toast.success(`Presupuesto ${nuevoEjercicio.value - 1} prorrogado a ${nuevoEjercicio.value}`)
  } catch (e) {
    console.error(e?.message || e)
    toast.error(e?.message || 'No se pudo prorrogar el presupuesto')
  } finally {
    ocupado.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.btn-estado {
  @apply px-3 py-1.5 text-sm font-medium text-white rounded-lg disabled:opacity-50;
}
</style>
