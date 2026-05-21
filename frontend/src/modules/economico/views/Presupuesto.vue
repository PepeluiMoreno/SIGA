<template>
  <AppLayout title="Presupuesto" subtitle="Planificación presupuestaria anual y partidas">
    <LoadSpinner v-if="loading" />

    <!-- Sin presupuesto del ejercicio: ofrecer crearlo -->
    <div v-else-if="!planificacion" class="bg-white rounded-lg shadow border border-gray-200 p-8 text-center">
      <p class="font-medium text-gray-700 mb-1">No hay presupuesto para {{ ejercicioActual }}</p>
      <p class="text-sm text-gray-500 mb-4">Crea la planificación anual para empezar a presupuestar.</p>
      <div v-if="puedeCrear" class="flex items-center justify-center gap-2">
        <input v-model.number="nuevoEjercicio" type="number"
          class="input-sm w-28 text-center" />
        <button @click="crearPlanificacion"
          class="px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700">
          Crear presupuesto {{ nuevoEjercicio }}
        </button>
      </div>
    </div>

    <AccordionGroup v-else>
      <!-- Panel 1: Cabecera y estado -->
      <AccordionPanel :default-open="true">
        <template #title>
          <div class="flex items-center gap-3">
            <h2 class="text-sm font-semibold text-slate-800">Presupuesto {{ planificacion.ejercicio }}</h2>
            <span class="text-xs px-2 py-0.5 rounded-full text-white" :style="{ backgroundColor: estadoColor }">
              {{ estadoNombre }}
            </span>
          </div>
        </template>

        <div class="px-5 py-4">
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
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

          <p v-if="planificacion.saldoPresupuestado !== 0" class="text-xs mb-3"
            :class="planificacion.saldoPresupuestado > 0 ? 'text-blue-600' : 'text-amber-600'">
            {{ planificacion.saldoPresupuestado > 0
              ? 'El presupuesto prevé superávit (más ingresos que gastos).'
              : 'El presupuesto prevé déficit (más gastos que ingresos).' }}
          </p>

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
          </div>
          <p v-if="planificacion.fechaAprobacion" class="text-xs text-gray-400 mt-2">
            Aprobado el {{ planificacion.fechaAprobacion }}
          </p>

          <!-- Control de disponibilidad (aprobado/ejecución) -->
          <label v-if="esAprobadoOEjecucion && puedeAprobar"
            class="flex items-center gap-2 mt-3 cursor-pointer select-none text-sm text-gray-600">
            <input type="checkbox" :checked="planificacion.controlDisponibilidad"
              @change="toggleControl($event.target.checked)"
              class="w-4 h-4 text-purple-600 rounded focus:ring-purple-500" />
            Avisar al control presupuestario cuando una partida se desvíe
            <span class="text-xs text-gray-400">(no bloquea el gasto)</span>
          </label>
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

      <!-- Panel: Alertas (solo si hay) -->
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

      <!-- Panel: Modificaciones presupuestarias (solo aprobado/ejecución) -->
      <AccordionPanel v-if="esAprobadoOEjecucion" title="Modificaciones presupuestarias"
        :count="modificaciones.length" :default-open="false">
        <ModificacionesPresupuestarias
          :modificaciones="modificaciones"
          :partidas="partidas"
          :puede-modificar="puedeAprobar && esAprobadoOEjecucion"
          @registrar="registrarModificacion"
        />
      </AccordionPanel>

      <!-- Panel 4: Seguimiento de ejecución (desviaciones) -->
      <AccordionPanel title="Seguimiento de ejecución" :default-open="false">
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
    </AccordionGroup>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import AccordionGroup from '@/components/common/AccordionGroup.vue'
import AccordionPanel from '@/components/common/AccordionPanel.vue'
import LoadSpinner from '@/components/common/LoadSpinner.vue'
import PartidasPorCategoria from '@/modules/economico/components/PartidasPorCategoria.vue'
import ModificacionesPresupuestarias from '@/modules/economico/components/ModificacionesPresupuestarias.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import { usePermisos } from '@/composables/usePermisos.js'
import {
  GET_PLANIFICACIONES, GET_PARTIDAS, GET_INFORME_DESVIACIONES, GET_ESTADOS_PLANIFICACION,
  CREAR_PLANIFICACION, CREAR_PARTIDA, ACTUALIZAR_PARTIDA, ELIMINAR_PARTIDA,
  PROPONER_PRESUPUESTO, APROBAR_PRESUPUESTO, INICIAR_EJECUCION_PRESUPUESTO,
  CERRAR_PRESUPUESTO, DEVOLVER_A_BORRADOR,
  GET_MODIFICACIONES, GET_ALERTAS, REGISTRAR_MODIFICACION, ESTABLECER_CONTROL_DISPONIBILIDAD,
} from '@/graphql/queries/presupuestos.js'

const { query, mutation } = useGraphQL()
const { tienePermiso } = usePermisos()

const puedeCrear = computed(() => tienePermiso('ECO_PRESUPUESTO_CREAR'))
const puedeGestionar = computed(() => tienePermiso('ECO_PRESUPUESTO_CREAR'))
const puedeAprobar = computed(() => tienePermiso('ECO_PRESUPUESTO_APROBAR'))

const loading = ref(false)
const ocupado = ref(false)
const planificacion = ref(null)
const partidas = ref([])
const desviaciones = ref([])
const estados = ref([])
const categorias = ref([])
const modificaciones = ref([])
const alertas = ref([])

const ejercicioActual = new Date().getFullYear()
const nuevoEjercicio = ref(ejercicioActual)

const partidasIngreso = computed(() => partidas.value.filter(p => p.tipo === 'INGRESO'))
const partidasGasto = computed(() => partidas.value.filter(p => p.tipo === 'GASTO'))

const estadoActual = computed(() => estados.value.find(e => e.id === planificacion.value?.estadoId))
const estadoCodigo = computed(() => estadoActual.value?.codigo ?? 'BORRADOR')
const estadoNombre = computed(() => estadoActual.value?.nombre ?? '—')
const estadoColor = computed(() => estadoActual.value?.color ?? '#9ca3af')
// Solo se editan partidas mientras el presupuesto no está aprobado
const editable = computed(() => puedeGestionar.value && ['BORRADOR', 'PROPUESTO'].includes(estadoCodigo.value))
const esAprobadoOEjecucion = computed(() => ['APROBADO', 'EN_EJECUCION'].includes(estadoCodigo.value))

const eur = (n) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n || 0)

const cargar = async () => {
  loading.value = true
  try {
    const [dataEstados, dataPlanes] = await Promise.all([
      query(GET_ESTADOS_PLANIFICACION),
      query(GET_PLANIFICACIONES),
    ])
    estados.value = dataEstados?.estadosPlanificacion ?? []
    const planes = dataPlanes?.planificaciones ?? []
    // Tomar el del ejercicio actual, o el más reciente
    planificacion.value = planes.find(p => p.ejercicio === ejercicioActual) ?? planes[0] ?? null
    if (planificacion.value) await cargarDetalle()
  } catch (e) {
    console.error('Error cargando presupuesto:', e?.message || e)
  } finally {
    loading.value = false
  }
}

const cargarDetalle = async () => {
  const id = planificacion.value.id
  const [dataPart, dataDesv, dataMod, dataAlert] = await Promise.all([
    query(GET_PARTIDAS, { planificacionId: id }),
    query(GET_INFORME_DESVIACIONES, { planificacionId: id }),
    query(GET_MODIFICACIONES, { planificacionId: id }),
    query(GET_ALERTAS, { planificacionId: id }),
  ])
  partidas.value = dataPart?.partidasPresupuestarias ?? []
  desviaciones.value = dataDesv?.informeDesviaciones ?? []
  modificaciones.value = dataMod?.modificacionesPresupuestarias ?? []
  alertas.value = dataAlert?.alertasPresupuestarias ?? []
}

const recargarPlan = async () => {
  const data = await query(GET_PLANIFICACIONES)
  const planes = data?.planificaciones ?? []
  planificacion.value = planes.find(p => p.id === planificacion.value?.id) ?? planificacion.value
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

const toggleControl = async (activo) => {
  await mutation(ESTABLECER_CONTROL_DISPONIBILIDAD, {
    planificacionId: planificacion.value.id, activo,
  })
  await recargarPlan()
}

onMounted(cargar)
</script>

<style scoped>
.btn-estado {
  @apply px-3 py-1.5 text-sm font-medium text-white rounded-lg disabled:opacity-50;
}
</style>
