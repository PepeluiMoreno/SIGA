<template>
  <!-- Hub de Tesorería: 4 acordeones según estándares profesionales del rol -->
  <AppLayout title="Tesorería" subtitle="Cobros, pagos, conciliación bancaria y configuración del módulo económico">

    <!-- Cabecera: selector de ejercicio + cuenta bancaria activa siempre visibles -->
    <div class="bg-white border border-slate-200 rounded-xl p-4 mb-5 flex flex-wrap items-end gap-4">
      <div>
        <label class="label">Ejercicio</label>
        <select v-model.number="ejercicio" class="input-sm w-full sm:w-28" @change="cargarKpis">
          <option v-for="y in ejercicios" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
      <div class="flex-1 min-w-[240px]">
        <label class="label">Cuenta bancaria</label>
        <select v-model="cuentaActivaId" class="input-sm w-full" @change="cargarKpis">
          <option v-for="c in cuentasBancarias" :key="c.id" :value="c.id">
            {{ c.nombre }} · {{ ibanFmt(c.iban) }} ({{ fmt(c.saldoActual || 0) }})
          </option>
        </select>
      </div>
      <div class="text-right ml-auto">
        <div class="text-xs text-slate-500">Saldo total consolidado</div>
        <div class="text-2xl font-bold" :class="saldoTotal >= 0 ? 'text-slate-900' : 'text-red-600'">
          {{ fmt(saldoTotal) }}
        </div>
      </div>
    </div>

    <LoadSpinner v-if="loading" />

    <AccordionGroup v-else>
      <!-- ════════ CAJA Y BANCOS ════════ -->
      <AccordionPanel
        v-if="permitido(['FIN_REPORTS'])"
        title="Caja y bancos"
        :count="kpi.numCuentas"
        :default-open="true"
      >
        <template #title>
          <div class="flex items-center gap-3">
            <span class="text-base">🏦</span>
            <h2 class="text-sm font-semibold text-slate-800">Caja y bancos</h2>
          </div>
        </template>

        <div class="p-5 grid grid-cols-1 md:grid-cols-1 sm:grid-cols-2 gap-3">
          <Bloque
            titulo="Saldos consolidados"
            :resumen="`${kpi.numCuentas} cuenta(s) activas · ${fmt(saldoTotal)}`"
          />
          <Bloque
            titulo="Movimientos recientes"
            :resumen="`${kpi.movimientosUltimos30Dias} apuntes en últimos 30 días`"
            accion="Registro de ingreso"
            secundario="Registro de gasto"
            @accion="abrirRegistroManual('INGRESO')"
            @secundario="abrirRegistroManual('GASTO')"
          />
          <Bloque
            titulo="Conciliación bancaria"
            :resumen="`${kpi.apuntesSinConciliar} apuntes sin conciliar · ${kpi.periodosAbiertos} período(s) abierto(s)`"
            accion="Conciliar"
            @accion="abrirConciliacion"
          />
        </div>
      </AccordionPanel>

      <!-- ════════ CUENTAS A COBRAR ════════ -->
      <AccordionPanel
        v-if="permitido(['CUOT_GENERATE','REM_CREATE','RCB_FAIL_NOTIFY','DON_CREATE','RCB_LIST'])"
        title="Cuentas a cobrar"
        :count="kpi.recibosFallidosSinNotificar + kpi.remesasEnviadasPendientes"
      >
        <template #title>
          <div class="flex items-center gap-3">
            <span class="text-base">📥</span>
            <h2 class="text-sm font-semibold text-slate-800">Cuentas a cobrar</h2>
          </div>
        </template>

        <div class="p-5 grid grid-cols-1 md:grid-cols-1 sm:grid-cols-2 gap-3">
          <Bloque
            v-if="permitido(['CUOT_GENERATE'])"
            titulo="Cuotas pendientes"
            :resumen="`${kpi.cuotasPendientes} pendientes · ${fmt(kpi.cuotasPendientesImporte)}`"
            accion="Ver cuotas"
            @accion="abrirCuotas"
          />
          <Bloque
            v-if="permitido(['CUOT_GENERATE','RCB_LIST'])"
            titulo="Recibos"
            :resumen="`${kpi.recibosEmitidos} emitidos · ${kpi.recibosCobrados} cobrados · ${kpi.recibosFallidos} fallidos`"
            accion="Emitir lote desde Remesas"
            @accion="abrirRemesas"
          />
          <Bloque
            v-if="permitido(['REM_CREATE'])"
            titulo="Remesas SEPA"
            :resumen="`${kpi.remesasTotal} remesas · ${kpi.remesasBorrador} borrador · ${kpi.remesasEnviadasPendientes} enviadas pendientes`"
            accion="Abrir Remesas"
            secundario="Nueva remesa"
            @accion="abrirRemesas"
            @secundario="abrirRemesas"
          />
          <Bloque
            v-if="permitido(['REM_CREATE'])"
            titulo="Liquidación bancaria"
            :resumen="kpi.remesasEnviadasPendientes > 0
              ? `${kpi.remesasEnviadasPendientes} remesa(s) esperando respuesta del banco (pain.002/camt.054)`
              : 'Sin remesas pendientes de liquidar'"
            :accion="kpi.remesasEnviadasPendientes > 0 ? 'Ir a liquidar' : null"
            @accion="abrirRemesas"
          />
          <Bloque
            v-if="permitido(['RCB_FAIL_NOTIFY'])"
            titulo="Comunicación de fallidos"
            :resumen="`${kpi.recibosFallidosSinNotificar} recibo(s) FALLIDO sin notificar al socio`"
            :accion="kpi.recibosFallidosSinNotificar > 0 ? 'Comunicar' : null"
            @accion="abrirComunicarFallidos"
          />
          <Bloque
            v-if="permitido(['DON_CREATE'])"
            titulo="Donaciones"
            :resumen="`${kpi.donacionesEjercicio} donaciones en ${ejercicio} · certificados fiscales Modelo 182`"
            accion="Abrir Donaciones"
            @accion="abrirDonaciones"
          />
        </div>
      </AccordionPanel>

      <!-- ════════ CUENTAS A PAGAR ════════ -->
      <AccordionPanel
        v-if="permitido(['FIN_REPORTS'])"
        title="Cuentas a pagar"
        :count="kpi.justificantesPresentados"
      >
        <template #title>
          <div class="flex items-center gap-3">
            <span class="text-base">📤</span>
            <h2 class="text-sm font-semibold text-slate-800">Cuentas a pagar</h2>
          </div>
        </template>

        <div class="p-5 grid grid-cols-1 md:grid-cols-1 sm:grid-cols-2 gap-3">
          <Bloque
            titulo="Justificantes de gasto de socios"
            :resumen="`${kpi.justificantesPresentados} presentados · ${kpi.justificantesAprobados} aprobados · ${kpi.justificantesPagados} pagados`"
            accion="Gestionar justificantes"
            @accion="modalJustificantes = true"
          />
          <Bloque
            titulo="Pagos manuales"
            resumen="Registrar transferencia/efectivo de la entidad. El gasto se imputa a una actividad (de campaña o permanente) para la Memoria anual."
            accion="Registro de gasto"
            @accion="abrirRegistroManual('GASTO')"
          />
          <Bloque
            titulo="XML SEPA Direct Debit (pain.008)"
            resumen="Generación automática de remesas para cobro domiciliado SEPA. Implementado y operativo desde Remesas (Cuentas a cobrar)"
            accion="Ir a Remesas"
            @accion="abrirRemesas"
          />
        </div>
      </AccordionPanel>

      <!-- ════════ CONFIGURACIÓN ════════ -->
      <AccordionPanel
        v-if="permitido(['CUOT_EJERCICIO_CONFIG','CUOT_MOTIVO_REDUC_MGMT','FIN_REPORTS'])"
        title="Configuración"
      >
        <template #title>
          <div class="flex items-center gap-3">
            <span class="text-base">⚙️</span>
            <h2 class="text-sm font-semibold text-slate-800">Configuración</h2>
          </div>
        </template>

        <div class="p-5 grid grid-cols-1 md:grid-cols-1 sm:grid-cols-2 gap-3">
          <Bloque
            v-if="permitido(['CUOT_EJERCICIO_CONFIG'])"
            titulo="Cuotas del ejercicio"
            :resumen="kpi.cuotaBase
              ? `Cuota base ${fmt(kpi.cuotaBase)} · ${kpi.cuotasGeneradas} cuotas generadas`
              : `Sin configurar — establece la cuota base de ${ejercicio}`"
            accion="Configurar"
            @accion="abrirCuotasEjercicio"
          />
          <Bloque
            v-if="permitido(['CUOT_MOTIVO_REDUC_MGMT'])"
            titulo="Motivos de reducción de cuota"
            :resumen="`${kpi.numMotivosReduccion} motivo(s) activos en catálogo`"
            accion="Gestionar"
            @accion="abrirMotivosReduccion"
          />
          <Bloque
            titulo="Conceptos de donación"
            :resumen="`${kpi.numConceptosDonacion} concepto(s) en catálogo`"
            accion="Catálogos"
            @accion="abrirConceptosDonacion"
          />
          <Bloque
            titulo="Reglas contables"
            resumen="Reglas que asignan las cuentas del Debe/Haber a cada tipo y origen de movimiento al generar los asientos automáticos."
            accion="Gestionar reglas"
            @accion="abrirReglasContables"
          />
        </div>
      </AccordionPanel>

      <!-- ════════ REDUCCIONES DE CUOTA ════════ -->
      <AccordionPanel v-if="permitido(['CUOT_EXEMPT'])" title="Reducciones de cuota">
        <template #title>
          <div class="flex items-center gap-3">
            <span class="text-base">🧾</span>
            <h2 class="text-sm font-semibold text-slate-800">Reducciones de cuota</h2>
          </div>
        </template>
        <SolicitudesReduccionCuota />
      </AccordionPanel>

      <!-- ════════ CUMPLIMIENTOS LEGALES ════════ -->
      <AccordionPanel
        v-if="permitido(['FIN_REPORTS'])"
        title="Cumplimientos legales"
      >
        <template #title>
          <div class="flex items-center gap-3">
            <span class="text-base">📜</span>
            <h2 class="text-sm font-semibold text-slate-800">Cumplimientos legales</h2>
          </div>
        </template>

        <div class="p-5 grid grid-cols-1 md:grid-cols-1 sm:grid-cols-2 gap-3">
          <Bloque
            titulo="Libros contables"
            resumen="Libro Diario, asientos contables y plan de cuentas (Cód. Comercio art. 25.1)."
            accion="Abrir Contabilidad"
            @accion="abrirContabilidad"
          />
          <Bloque
            titulo="Cierre del ejercicio"
            resumen="Regularización (grupos 6 y 7 → cta 129), asiento de cierre y apertura del ejercicio siguiente."
            accion="Abrir cierre"
            @accion="abrirCierre"
          />
          <Bloque
            titulo="Cuentas Anuales"
            resumen="Balance PCESFL, Cuenta de Resultados (Excedente), Memoria económica y depósito de cuentas."
            accion="Abrir Cuentas Anuales"
            @accion="abrirCuentasAnuales"
          />
          <Bloque
            titulo="Modelo 182 — Donaciones"
            resumen="Ley 49/2002 — declaración informativa de donativos recibidos para que el donante los deduzca."
            accion="Abrir Modelo 182"
            @accion="abrirModelo182"
          />
        </div>
      </AccordionPanel>
    </AccordionGroup>

    <!-- ────────────────────────────────────────────────────────────────────── -->
    <!-- Modal: Registrar movimiento manual (gasto / ingreso directo)           -->
    <!-- ────────────────────────────────────────────────────────────────────── -->
    <div v-if="modalMovimiento" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
         @click.self="modalMovimiento = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-xl flex flex-col max-h-[90vh]">
        <div class="px-6 py-4 border-b border-slate-200">
          <h3 class="font-semibold text-slate-800">
            Registro de {{ formMovimiento.tipo === 'GASTO' ? 'gasto' : 'ingreso' }}
          </h3>
          <p class="text-xs text-slate-500 mt-0.5">
            Todo movimiento de tesorería se imputa a una actividad (de campaña o permanente).
          </p>
        </div>
        <div class="px-6 py-5 space-y-3 overflow-y-auto">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="label">Tipo *</label>
              <select v-model="formMovimiento.tipo" class="input">
                <option value="GASTO">Gasto</option>
                <option value="INGRESO">Ingreso</option>
              </select>
            </div>
            <div>
              <label class="label">Fecha *</label>
              <input type="date" v-model="formMovimiento.fecha" class="input" />
            </div>
          </div>

          <div>
            <label class="label">Cuenta bancaria *</label>
            <select v-model="formMovimiento.cuentaId" class="input">
              <option :value="null">— Selecciona cuenta —</option>
              <option v-for="c in cuentasBancarias.filter(x => x.activa)" :key="c.id" :value="c.id">
                {{ c.nombre }}{{ c.iban ? ' — ' + ibanFmt(c.iban) : '' }} · Saldo {{ fmt(c.saldoActual) }}
              </option>
            </select>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="label">Importe (€) *</label>
              <input type="number" step="0.01" min="0" v-model.number="formMovimiento.importe" class="input" />
            </div>
            <div>
              <label class="label">Referencia externa</label>
              <input v-model="formMovimiento.referenciaExterna" class="input"
                     placeholder="Núm. transferencia, factura, ticket…" />
            </div>
          </div>

          <div>
            <label class="label">Concepto *</label>
            <input v-model="formMovimiento.concepto" class="input"
                   :placeholder="formMovimiento.tipo === 'GASTO' ? 'Alquiler oficina marzo, factura proveedor X…' : 'Patrocinio, ingreso por curso…'" />
          </div>

          <!-- Imputación a actividad (obligatoria — para Memoria anual por actividad/campaña) -->
          <ImputacionActividadPicker
            v-model="imputacionMovimiento"
            :campanias="campanias"
            :actividades="actividades"
            tooltip="El balance económico de la Memoria anual se construye por actividad y campaña. Si no hay una actividad apropiada, créala primero en el módulo Actividades (p. ej. una permanente «Estructura» o «Administración»)."
          />

          <div>
            <label class="label">Observaciones</label>
            <textarea v-model="formMovimiento.observaciones" rows="2" class="input" />
          </div>

          <ErrorAlert v-if="formMovimiento.error" :message="formMovimiento.error" />
          <p class="text-xs text-slate-500">
            Se generan automáticamente el apunte de caja y el asiento contable correspondiente.
          </p>
        </div>
        <div class="px-6 py-4 border-t border-slate-200 flex justify-end gap-2">
          <button @click="modalMovimiento = false" class="btn-secondary text-sm">Cancelar</button>
          <button @click="confirmarMovimiento()" :disabled="ocupado" class="btn-primary text-sm">
            {{ ocupado ? 'Registrando…' : 'Registrar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: gestión de justificantes de gasto de socios -->
    <div v-if="modalJustificantes" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
         @click.self="modalJustificantes = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-6xl flex flex-col max-h-[90vh]">
        <div class="px-6 py-4 border-b border-slate-200 flex justify-between items-center">
          <h3 class="font-semibold text-slate-800">Justificantes de gasto de socios</h3>
          <button @click="modalJustificantes = false"
                  class="text-slate-400 hover:text-slate-700 text-xl leading-none">×</button>
        </div>
        <div class="px-6 py-5 overflow-y-auto">
          <JustificantesGastoPanel modo="GESTION" />
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { ref, computed, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import LoadSpinner from '@/components/common/LoadSpinner.vue'
import AccordionPanel from '@/components/common/AccordionPanel.vue'
import AccordionGroup from '@/components/common/AccordionGroup.vue'
import ImputacionActividadPicker from '@/components/common/ImputacionActividadPicker.vue'
import JustificantesGastoPanel from '@/components/common/JustificantesGastoPanel.vue'
import SolicitudesReduccionCuota from './SolicitudesReduccionCuota.vue'
import { useTesoreria } from '@/composables/useTesoreria'
import { useGraphQL } from '@/composables/useGraphQL'
import { usePermisos } from '@/composables/usePermisos'
import { GET_ACTIVIDADES_PARA_GASTO } from '@/graphql/queries/economico'
import { GET_CAMPANIAS } from '@/graphql/queries/campanias'

// ── Sub-componente Bloque (card con acción) ────────────────────────────────
const Bloque = {
  props: ['titulo', 'resumen', 'accion', 'secundario'],
  emits: ['accion', 'secundario'],
  setup(props, { emit }) {
    return () => h('div', {
      class: 'rounded-lg border border-slate-200 bg-white p-4 hover:shadow-sm transition',
    }, [
      h('div', { class: 'flex items-start justify-between gap-3' }, [
        h('div', { class: 'min-w-0 flex-1' }, [
          h('h3', { class: 'font-medium text-slate-800 text-sm' }, props.titulo),
          h('p', { class: 'text-xs text-slate-500 mt-1' }, props.resumen),
        ]),
        h('div', { class: 'flex flex-col gap-1 shrink-0' }, [
          props.accion ? h('button', {
            class: 'px-3 py-1 bg-indigo-600 text-white rounded text-xs font-medium hover:bg-indigo-700',
            onClick: () => emit('accion'),
          }, props.accion) : null,
          props.secundario ? h('button', {
            class: 'px-3 py-1 bg-white border border-slate-300 text-slate-700 rounded text-xs font-medium hover:bg-slate-50',
            onClick: () => emit('secundario'),
          }, props.secundario) : null,
        ].filter(Boolean)),
      ]),
    ])
  },
}

// ── Sub-componente BloquePlaceholder (Próximamente, atenuado) ──────────────
const BloquePlaceholder = {
  props: ['titulo', 'resumen'],
  setup(props) {
    return () => h('div', {
      class: 'rounded-lg border border-dashed border-slate-200 bg-slate-50/40 p-4 opacity-70',
    }, [
      h('div', { class: 'flex items-start justify-between gap-3' }, [
        h('div', { class: 'min-w-0 flex-1' }, [
          h('h3', { class: 'font-medium text-slate-600 text-sm' }, props.titulo),
          h('p', { class: 'text-xs text-slate-400 mt-1' }, props.resumen),
        ]),
        h('span', {
          class: 'shrink-0 text-[10px] uppercase font-semibold bg-amber-100 text-amber-700 px-2 py-0.5 rounded',
        }, 'Próximamente'),
      ]),
    ])
  },
}

// ── Estado ──────────────────────────────────────────────────────────────────
const router = useRouter()
const { tienePermiso } = usePermisos()
const { query } = useGraphQL()

const {
  cuentasBancarias,
  obtenerCuentasBancarias,
  saldoTotal,
  registrarApunte,
} = useTesoreria()

// ── Registro manual de movimientos ─────────────────────────────────────────
const modalMovimiento = ref(false)
const modalJustificantes = ref(false)
const ocupado = ref(false)
const actividades = ref([])
const campanias = ref([])
const formMovimiento = ref(_emptyMovimiento())

function _emptyMovimiento() {
  return {
    tipo: 'GASTO',
    fecha: new Date().toISOString().split('T')[0],
    cuentaId: null,
    importe: null,
    concepto: '',
    referenciaExterna: '',
    observaciones: '',
    modoImputacion: 'CAMPANIA',  // CAMPANIA | FUERA
    tipoFuera: 'PERMANENTE',     // PERMANENTE | PUNTUAL | RECURRENTE
    actividadId: null,
    campaniaId: null,
    error: '',
  }
}

// Imputación (puente bidireccional con el formulario; el componente picker es
// el dueño de la UI, este v-model concentra los 4 campos taxonómicos en uno).
const imputacionMovimiento = computed({
  get: () => ({
    modo:        formMovimiento.value.modoImputacion,
    campaniaId:  formMovimiento.value.campaniaId,
    actividadId: formMovimiento.value.actividadId,
    tipoFuera:   formMovimiento.value.tipoFuera,
  }),
  set: (v) => {
    formMovimiento.value.modoImputacion = v.modo
    formMovimiento.value.campaniaId     = v.campaniaId
    formMovimiento.value.actividadId    = v.actividadId
    formMovimiento.value.tipoFuera      = v.tipoFuera
  },
})

const cargarImputables = async () => {
  try {
    const [a, c] = await Promise.all([
      query(GET_ACTIVIDADES_PARA_GASTO),
      query(GET_CAMPANIAS),
    ])
    actividades.value = (a.actividades || []).slice().sort((x, y) => x.nombre.localeCompare(y.nombre))
    campanias.value = (c.campanias || []).slice().sort((x, y) => x.nombre.localeCompare(y.nombre))
  } catch (e) {
    console.error('Error cargando actividades/campañas:', e?.message || e)
  }
}

const abrirRegistroManual = (tipo) => {
  formMovimiento.value = _emptyMovimiento()
  formMovimiento.value.tipo = tipo
  if (cuentasBancarias.value.length === 1) {
    formMovimiento.value.cuentaId = cuentasBancarias.value[0].id
  } else if (cuentaActivaId.value) {
    formMovimiento.value.cuentaId = cuentaActivaId.value
  }
  modalMovimiento.value = true
}

const confirmarMovimiento = async () => {
  const f = formMovimiento.value
  f.error = ''
  if (!f.cuentaId) { f.error = 'Selecciona la cuenta bancaria'; return }
  if (!f.importe || f.importe <= 0) { f.error = 'Indica un importe positivo'; return }
  if (!f.concepto?.trim()) { f.error = 'Indica el concepto del movimiento'; return }
  if (!f.actividadId) {
    f.error = f.modoImputacion === 'CAMPANIA'
      ? 'Selecciona la campaña y la actividad a la que se imputa.'
      : 'Selecciona la actividad fuera de campaña a la que se imputa.'
    return
  }
  // Derivar campania_id desde la actividad elegida (coherencia garantizada).
  const actividad = actividades.value.find(a => a.id === f.actividadId)
  const campaniaIdDerivada = actividad?.campaniaId || null

  ocupado.value = true
  try {
    await registrarApunte({
      cuentaId: f.cuentaId,
      fecha: f.fecha,
      importe: Number(f.importe),
      tipo: f.tipo,
      concepto: f.concepto.trim(),
      origen: 'MANUAL',
      referenciaExterna: f.referenciaExterna || null,
      observaciones: f.observaciones || null,
      actividadId: f.actividadId,
      campaniaId: campaniaIdDerivada,
    })
    modalMovimiento.value = false
    await Promise.all([obtenerCuentasBancarias(), cargarKpis()])
  } catch (e) {
    f.error = e.message || 'Error al registrar el movimiento'
  } finally { ocupado.value = false }
}

const anoActual = new Date().getFullYear()
const ejercicios = [anoActual + 1, anoActual, anoActual - 1, anoActual - 2]
const ejercicio = ref(anoActual)
const cuentaActivaId = ref('')
const loading = ref(true)

// KPI consolidado
const kpi = ref({
  numCuentas: 0,
  movimientosUltimos30Dias: 0,
  apuntesSinConciliar: 0,
  periodosAbiertos: 0,
  cuotasPendientes: 0,
  cuotasPendientesImporte: 0,
  recibosEmitidos: 0,
  recibosCobrados: 0,
  recibosFallidos: 0,
  recibosFallidosSinNotificar: 0,
  remesasTotal: 0,
  remesasBorrador: 0,
  remesasEnviadasPendientes: 0,
  donacionesEjercicio: 0,
  justificantesPresentados: 0,
  justificantesAprobados: 0,
  justificantesPagados: 0,
  cuotaBase: 0,
  cuotasGeneradas: 0,
  numMotivosReduccion: 0,
  numConceptosDonacion: 0,
})

// ── Helpers ─────────────────────────────────────────────────────────────────
const fmt = (v) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(v || 0)
const ibanFmt = (iban) => iban ? iban.slice(0, 4) + ' **** ' + iban.slice(-4) : ''

const permitido = (codigos) => codigos.some(c => tienePermiso(c))

// ── Carga de KPIs ──────────────────────────────────────────────────────────
const cargarKpis = async () => {
  loading.value = true
  try {
    const data = await query(QUERY_KPIS_TESORERIA, { ejercicio: ejercicio.value })
    const e = ejercicio.value
    // Filtrado en cliente por ejercicio donde aplica
    const cuotasEj = (data.cuotasAnuales || []).filter(c => c.ejercicio === e)
    const recibosEj = (data.recibos || []).filter(r => r.ejercicio === e)
    const remesasEj = (data.remesas || []).filter(r => (r.fechaCobro || '').startsWith(String(e)))
    const donacionesEj = (data.donaciones || []).filter(d => (d.fecha || '').startsWith(String(e)))
    // Apuntes últimos 30 días
    const limiteFecha = new Date()
    limiteFecha.setDate(limiteFecha.getDate() - 30)
    const limite = limiteFecha.toISOString().slice(0, 10)
    const apuntes30 = (data.apuntesCaja || []).filter(a => (a.fecha || '') >= limite)

    kpi.value = {
      numCuentas: (data.cuentasBancarias || []).filter(c => c.activa).length,
      movimientosUltimos30Dias: apuntes30.length,
      apuntesSinConciliar: (data.apuntesCaja || []).filter(a => !a.conciliado).length,
      periodosAbiertos: (data.conciliacionesBancarias || []).length,
      cuotasPendientes: cuotasEj.filter(c => c.estado?.nombre === 'Pendiente').length,
      cuotasPendientesImporte: cuotasEj
        .filter(c => c.estado?.nombre === 'Pendiente')
        .reduce((s, c) => s + (parseFloat(c.importe) - parseFloat(c.importePagado || 0)), 0),
      recibosEmitidos: recibosEj.length,
      recibosCobrados: recibosEj.filter(r => r.estado === 'COBRADO').length,
      recibosFallidos: recibosEj.filter(r => r.estado === 'FALLIDO').length,
      recibosFallidosSinNotificar: recibosEj.filter(r => r.estado === 'FALLIDO' && !r.fechaAvisoFallido).length,
      remesasTotal: remesasEj.length,
      remesasBorrador: remesasEj.filter(r => r.estado?.nombre === 'Borrador').length,
      remesasEnviadasPendientes: remesasEj.filter(r => r.estado?.nombre === 'Enviada').length,
      donacionesEjercicio: donacionesEj.length,
      justificantesPresentados: (data.justificantesGasto || []).filter(j => j.estado === 'PRESENTADO').length,
      justificantesAprobados: (data.justificantesGasto || []).filter(j => j.estado === 'APROBADO').length,
      justificantesPagados: (data.justificantesGasto || []).filter(j => j.estado === 'PAGADO').length,
      cuotaBase: parseFloat((data.importesCuotaAnio || [])[0]?.importe || 0),
      cuotasGeneradas: cuotasEj.length,
      numMotivosReduccion: (data.motivosReduccionCuota || []).filter(m => m.activo).length,
      numConceptosDonacion: (data.donacionConceptos || []).filter(c => c.activo).length,
    }
  } catch (e) {
    console.error('Error cargando KPIs Tesorería:', e?.message || e)
  } finally {
    loading.value = false
  }
}

// Query consolidada — sin filtros para evitar issues con strawchemy.filter vacíos.
// Filtramos en cliente por ejercicio. Es seguro: volúmenes pequeños (miles).
const QUERY_KPIS_TESORERIA = `
  query KpisTesoreria($ejercicio: Int!) {
    cuentasBancarias { id activa nombre iban saldoActual }
    apuntesCaja { id fecha conciliado }
    conciliacionesBancarias { id }
    cuotasAnuales { id ejercicio importe importePagado estado { nombre } }
    recibos { id ejercicio estado fechaAvisoFallido }
    remesas { id fechaCobro estado { id nombre } }
    donaciones { id fecha }
    justificantesGasto { id estado }
    importesCuotaAnio(filter: {
      ejercicio: { eq: $ejercicio },
      codigoCuota: { eq: "BASE" }
    }) { id importe }
    motivosReduccionCuota { id activo }
    donacionConceptos { id activo }
  }
`

// ── Navegación a vistas detalle (solo a rutas que existen) ────────────────
const abrirCuotas = () => router.push('/economico/cuotas')
const abrirRemesas = () => router.push('/economico/remesas')
const abrirComunicarFallidos = () => router.push('/economico/comunicacion-fallidos')
const abrirDonaciones = () => router.push('/economico/donaciones')
const abrirCuotasEjercicio = () => router.push('/economico/cuotas-ejercicio')
const abrirMotivosReduccion = () => router.push('/parametrizacion/motivos-reduccion-cuota')
const abrirConceptosDonacion = () => router.push('/parametrizacion/catalogos')
const abrirPresupuesto = () => router.push('/economico/presupuesto')
const abrirConciliacion = () => router.push('/economico/conciliacion')
const abrirContabilidad = () => router.push('/economico/contabilidad')
const abrirCuentasAnuales = () => router.push('/economico/cuentas-anuales')
const abrirModelo182 = () => router.push('/economico/modelo-182')
const abrirReglasContables = () => router.push('/economico/reglas-contables')
const abrirCierre = () => router.push('/economico/cierre-ejercicio')

// ── Lifecycle ───────────────────────────────────────────────────────────────
onMounted(async () => {
  await obtenerCuentasBancarias()
  if (cuentasBancarias.value.length) {
    cuentaActivaId.value = cuentasBancarias.value[0].id
  }
  await Promise.all([cargarKpis(), cargarImputables()])
})
</script>

<style scoped>
.label         { @apply block text-xs font-medium text-slate-600 mb-1; }
.input         { @apply w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent; }
.input-sm      { @apply px-3 py-1.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400; }
.btn-primary   { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed; }
.btn-secondary { @apply px-3 py-1.5 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 text-sm font-medium disabled:opacity-50; }
</style>
