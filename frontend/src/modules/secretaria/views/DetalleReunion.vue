<template>
  <AppLayout :title="tituloReunion" :subtitle="subtituloReunion" icon="🗓️">

    <DetailHeader fallback="/secretaria/reuniones" back-text="Volver a reuniones" />

    <EstadoCarga v-if="loading" mensaje="Cargando la reunión…" />

    <ErrorAlert v-else-if="error" :message="error" :retry-action="true" @retry="cargar" />

    <div v-else-if="reunion" class="page-body">

      <!-- ── Cabecera de la reunión ─────────────────────────────────────── -->
      <div class="card p-5">
        <div class="flex flex-wrap items-center gap-2 mb-3">
          <span class="font-semibold text-gray-900">{{ nombreTipo }}</span>
          <span class="text-sm text-gray-400">nº {{ reunion.numeroConvocatoria }}/{{ reunion.anio }}</span>
          <span :class="badgeEstado(reunion.estadoCodigo)"
            class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium">
            {{ etiquetaEstado(reunion.estadoCodigo) }}
          </span>
          <span v-if="reunion.esTelematica"
            class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
            Telemática
          </span>
        </div>
        <dl class="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
          <div>
            <dt class="text-xs text-gray-400">Órgano</dt>
            <dd class="text-gray-800">{{ nombreOrgano }}</dd>
          </div>
          <div>
            <dt class="text-xs text-gray-400">Fecha de convocatoria</dt>
            <dd class="text-gray-800">{{ formatFecha(reunion.fechaConvocatoria) }}</dd>
          </div>
          <div>
            <dt class="text-xs text-gray-400">Fecha de celebración</dt>
            <dd class="text-gray-800">{{ formatFechaHora(reunion.fechaCelebracion) }}</dd>
          </div>
          <div>
            <dt class="text-xs text-gray-400">Lugar</dt>
            <dd class="text-gray-800">{{ reunion.lugar || '—' }}</dd>
          </div>
        </dl>
      </div>

      <!-- ── Orden del día ──────────────────────────────────────────────── -->
      <div class="card p-0">
        <div class="px-5 py-3 border-b border-gray-100 flex items-center justify-between gap-3">
          <h2 class="text-sm font-semibold text-gray-900">Orden del día</h2>
          <button v-if="tienePermiso('SEC_REUNION_EDITAR')" @click="abrirPunto"
            class="inline-flex items-center gap-1.5 h-8 px-3 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors">
            <PlusIcon class="w-4 h-4" /> Añadir punto
          </button>
        </div>
        <!-- Sin paginar (`porPagina=0`) a propósito: el orden del día es una
             secuencia — partirlo en páginas rompería la lectura del temario, y
             la sección de acuerdos de más abajo recorre estos mismos puntos. -->
        <ResponsiveTable
          :columnas="columnasPuntos"
          :filas="puntos"
          :por-pagina="0"
          vacio-texto="La reunión aún no tiene puntos en el orden del día">
          <template #cell-titulo="{ fila: p }">
            <div class="text-sm font-medium text-gray-900">{{ p.titulo }}</div>
            <div v-if="p.descripcion" class="text-xs text-gray-400 truncate">{{ p.descripcion }}</div>
          </template>
          <template #cell-tipo="{ fila: p }">
            <span class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600">
              {{ etiquetaTipoPunto(p.tipo) }}
            </span>
          </template>
          <template #cell-acuerdos="{ fila: p }">
            {{ acuerdosDePunto(p.id).length }}
          </template>
        </ResponsiveTable>
      </div>

      <!-- ── Asistentes ─────────────────────────────────────────────────── -->
      <div class="card p-0">
        <div class="px-5 py-3 border-b border-gray-100 flex items-center justify-between gap-3">
          <h2 class="text-sm font-semibold text-gray-900">Asistentes</h2>
          <button v-if="tienePermiso('SEC_REUNION_REGISTRAR_ASIST')" @click="abrirAsistente"
            class="inline-flex items-center gap-1.5 h-8 px-3 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors">
            <PlusIcon class="w-4 h-4" /> Registrar asistente
          </button>
        </div>
        <p v-if="asistentesNoLegibles"
          class="mx-5 mt-4 text-xs text-amber-800 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
          El backend no puede devolver hoy la lista de asistentes de secretaría: el campo
          <code>asistentesReunion</code> del esquema está ocupado por los asistentes a reuniones de
          grupo de trabajo. Registrar asistentes sí funciona; abajo se muestran los de esta sesión.
        </p>
        <ResponsiveTable
          :columnas="columnasAsistentes"
          :filas="asistentes"
          :orden-inicial="{ key: 'miembro', dir: 'asc' }"
          vacio-texto="Aún no se ha registrado ningún asistente">
          <template #cell-miembro="{ fila: a }">
            <span class="text-sm text-gray-900">{{ nombreMiembro(a.miembroId) }}</span>
          </template>
          <template #cell-tipoAsistencia="{ fila: a }">
            <span :class="badgeAsistencia(a.tipoAsistencia)"
              class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium">
              {{ etiquetaAsistencia(a.tipoAsistencia) }}
            </span>
          </template>
          <template #cell-representadoPor="{ fila: a }">
            {{ a.representadoPorId ? nombreMiembro(a.representadoPorId) : '—' }}
          </template>
          <template #cell-cargo="{ fila: a }">{{ a.cargo || '—' }}</template>
        </ResponsiveTable>
      </div>

      <!-- ── Acuerdos, agrupados por punto del orden del día ─────────────── -->
      <div class="card p-0">
        <div class="px-5 py-3 border-b border-gray-100">
          <h2 class="text-sm font-semibold text-gray-900">Acuerdos</h2>
          <p class="text-xs text-gray-400 mt-0.5">
            Un nombramiento nace de un acuerdo: fíjalo (a quién y qué cargo) y ejecútalo cuando el acta esté aprobada.
          </p>
        </div>

        <div v-if="!puntos.length" class="px-5 py-8 text-center text-sm text-gray-400">
          Añade primero un punto al orden del día: los acuerdos cuelgan de él.
        </div>

        <div v-else class="divide-y divide-gray-100">
          <div v-for="p in puntos" :key="p.id" class="px-5 py-4">
            <div class="flex items-start justify-between gap-3 mb-2">
              <div class="min-w-0">
                <p class="text-sm font-medium text-gray-900">{{ p.orden }}. {{ p.titulo }}</p>
                <p v-if="p.descripcion" class="text-xs text-gray-400">{{ p.descripcion }}</p>
              </div>
              <button v-if="tienePermiso('SEC_ACUERDO_CREAR')" @click="abrirAcuerdo(p)"
                class="shrink-0 inline-flex items-center gap-1.5 h-8 px-3 text-xs font-semibold text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-lg hover:bg-indigo-100 transition-colors">
                <PlusIcon class="w-3.5 h-3.5" /> Registrar acuerdo
              </button>
            </div>

            <p v-if="!acuerdosDePunto(p.id).length" class="text-xs text-gray-400 italic">
              Sin acuerdos en este punto.
            </p>

            <div v-else class="space-y-2 mt-2">
              <div v-for="a in acuerdosDePunto(p.id)" :key="a.id"
                class="border border-gray-200 rounded-lg p-3">
                <div class="flex flex-wrap items-center gap-2 mb-1">
                  <span class="text-xs text-gray-400">Acuerdo nº {{ a.numero }}</span>
                  <span :class="badgeResultado(a.resultado)"
                    class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium">
                    {{ etiquetaResultado(a.resultado) }}
                  </span>
                  <span class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600">
                    Mayoría {{ etiquetaMayoria(a.tipoMayoria) }}
                  </span>
                </div>
                <p class="text-sm text-gray-800">{{ a.descripcion }}</p>

                <!-- Solo un acuerdo APROBADO produce efecto: fijarlo y ejecutarlo. -->
                <div v-if="a.resultado === 'APROBADO'" class="mt-3 flex flex-wrap items-center gap-2">
                  <button v-if="tienePermiso('SEC_ACUERDO_CREAR')" @click="abrirNombramiento(a)"
                    class="inline-flex items-center gap-1.5 h-8 px-3 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors">
                    <UserPlusIcon class="w-4 h-4 text-slate-500" /> Fijar nombramiento / cese
                  </button>
                  <button v-if="tienePermiso('MEMBRESIA_CARGO_ASIGNAR')" @click="ejecutar(a)"
                    :disabled="ejecutando === a.id"
                    class="inline-flex items-center gap-1.5 h-8 px-3 text-xs font-semibold text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors">
                    <BoltIcon class="w-4 h-4" />
                    {{ ejecutando === a.id ? 'Ejecutando…' : 'Ejecutar acuerdo' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Drawer: añadir punto del orden del día ───────────────────────── -->
    <AppDrawer v-model="drawerPunto" title="Añadir punto al orden del día" size="md" storage-key="sec-punto">
      <div class="space-y-4">
        <AppFormField label="Título" required>
          <AppInput v-model="formPunto.titulo" placeholder="Aprobación de las cuentas anuales…" />
        </AppFormField>
        <AppFormField label="Descripción">
          <AppTextarea v-model="formPunto.descripcion" :rows="3" />
        </AppFormField>
        <AppFormField label="Tipo">
          <AppSelect v-model="formPunto.tipo" :options="OPCIONES_TIPO_PUNTO" />
        </AppFormField>
      </div>
      <template #footer>
        <button @click="drawerPunto = false"
          class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">
          Cancelar
        </button>
        <button @click="guardarPunto" :disabled="guardando"
          class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50">
          {{ guardando ? 'Guardando…' : 'Añadir' }}
        </button>
      </template>
    </AppDrawer>

    <!-- ── Drawer: registrar asistente ──────────────────────────────────── -->
    <AppDrawer v-model="drawerAsistente" title="Registrar asistente" size="md" storage-key="sec-asistente">
      <div class="space-y-4">
        <AppFormField label="Miembro" required>
          <SelectorMiembro v-model="formAsistente.miembroId" :miembros="miembros" />
        </AppFormField>
        <AppFormField label="Tipo de asistencia">
          <AppSelect v-model="formAsistente.tipoAsistencia" :options="OPCIONES_ASISTENCIA" />
        </AppFormField>
        <AppFormField
          v-if="formAsistente.tipoAsistencia === 'REPRESENTADO'"
          label="Representado por"
          help="Miembro que ejerce la representación">
          <SelectorMiembro v-model="formAsistente.representadoPorId" :miembros="miembros" />
        </AppFormField>
        <AppFormField label="Cargo con el que asiste">
          <AppInput v-model="formAsistente.cargo" placeholder="Presidencia, Secretaría…" width="md" />
        </AppFormField>
      </div>
      <template #footer>
        <button @click="drawerAsistente = false"
          class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">
          Cancelar
        </button>
        <button @click="guardarAsistente" :disabled="guardando"
          class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50">
          {{ guardando ? 'Guardando…' : 'Registrar' }}
        </button>
      </template>
    </AppDrawer>

    <!-- ── Drawer: registrar acuerdo ────────────────────────────────────── -->
    <AppDrawer v-model="drawerAcuerdo" title="Registrar acuerdo"
      :subtitle="puntoActivo ? `${puntoActivo.orden}. ${puntoActivo.titulo}` : ''"
      size="lg" storage-key="sec-acuerdo">
      <div class="space-y-4">
        <AppFormField label="Descripción del acuerdo" required>
          <AppTextarea v-model="formAcuerdo.descripcion" :rows="3"
            placeholder="Se acuerda nombrar a … como …" />
        </AppFormField>
        <AppFormGrid cols="2">
          <AppFormField label="Tipo de mayoría">
            <AppSelect v-model="formAcuerdo.tipoMayoria" :options="OPCIONES_MAYORIA" />
          </AppFormField>
          <AppFormField label="Resultado">
            <AppSelect v-model="formAcuerdo.resultado" :options="OPCIONES_RESULTADO" />
          </AppFormField>
        </AppFormGrid>
        <AppFormGrid cols="3">
          <AppFormField label="Votos a favor">
            <AppInput v-model.number="formAcuerdo.votosFavor" type="number" min="0" width="xs" />
          </AppFormField>
          <AppFormField label="Votos en contra">
            <AppInput v-model.number="formAcuerdo.votosContra" type="number" min="0" width="xs" />
          </AppFormField>
          <AppFormField label="Abstenciones">
            <AppInput v-model.number="formAcuerdo.abstenciones" type="number" min="0" width="xs" />
          </AppFormField>
        </AppFormGrid>
      </div>
      <template #footer>
        <button @click="drawerAcuerdo = false"
          class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">
          Cancelar
        </button>
        <button @click="guardarAcuerdo" :disabled="guardando"
          class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50">
          {{ guardando ? 'Guardando…' : 'Registrar' }}
        </button>
      </template>
    </AppDrawer>

    <!-- ── Drawer: fijar nombramiento / cese del acuerdo ─────────────────── -->
    <AppDrawer v-model="drawerNombramiento" title="Fijar nombramiento o cese"
      subtitle="Adjunta al acuerdo a quién nombra o cesa y para qué cargo"
      size="lg" storage-key="sec-nombramiento">
      <div class="space-y-4">
        <p v-if="acuerdoActivo" class="text-xs text-gray-500 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2">
          Acuerdo nº {{ acuerdoActivo.numero }} — {{ acuerdoActivo.descripcion }}
        </p>
        <AppFormField label="Tipo">
          <AppSelect v-model="formNombramiento.tipoCodigo" :options="OPCIONES_TIPO_NOMBRAMIENTO" />
        </AppFormField>
        <AppFormField label="Miembro" required>
          <SelectorMiembro v-model="formNombramiento.miembroId" :miembros="miembros" />
        </AppFormField>
        <AppFormField label="Cargo" required>
          <AppSelect v-model="formNombramiento.cargoId" :options="opcionesCargo" />
        </AppFormField>
        <AppFormField label="Agrupación" help="Ámbito territorial del cargo (opcional)">
          <SelectorAgrupacion v-model="formNombramiento.agrupacionId" :agrupaciones="unidades" />
        </AppFormField>
        <AppFormGrid cols="2">
          <AppFormField label="Fecha de inicio" required>
            <AppInput v-model="formNombramiento.fechaInicio" type="date" width="sm" />
          </AppFormField>
          <AppFormField label="Fecha de fin">
            <AppInput v-model="formNombramiento.fechaFin" type="date" width="sm" />
          </AppFormField>
        </AppFormGrid>
      </div>
      <template #footer>
        <button @click="drawerNombramiento = false"
          class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">
          Cancelar
        </button>
        <button @click="guardarNombramiento" :disabled="guardando"
          class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50">
          {{ guardando ? 'Guardando…' : 'Fijar' }}
        </button>
      </template>
    </AppDrawer>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import AppDrawer from '@/components/common/AppDrawer.vue'
import AppFormField from '@/components/common/AppFormField.vue'
import AppFormGrid from '@/components/common/AppFormGrid.vue'
import AppInput from '@/components/common/AppInput.vue'
import AppSelect from '@/components/common/AppSelect.vue'
import AppTextarea from '@/components/common/AppTextarea.vue'
import DetailHeader from '@/components/common/DetailHeader.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import ResponsiveTable from '@/components/common/ResponsiveTable.vue'
import SelectorMiembro from '@/components/common/SelectorMiembro.vue'
import SelectorAgrupacion from '@/components/common/SelectorAgrupacion.vue'
import { usePermisos } from '@/composables/usePermisos.js'
import { useToast } from '@/composables/useToast.js'
import { useConfirm } from '@/composables/useConfirm.js'
import { useUnidadesOrganizativas } from '@/composables/useUnidadesOrganizativas.js'
import { executeQuery, executeMutation } from '@/graphql/client'
import {
  GET_REUNIONES, GET_TIPOS_REUNION, GET_MIEMBROS_LIGERO,
  GET_PUNTOS_ORDEN_DIA, AGREGAR_PUNTO_ORDEN_DIA,
  GET_ASISTENTES_REUNION, REGISTRAR_ASISTENTE_REUNION,
  GET_ACUERDOS_DE_REUNION, REGISTRAR_ACUERDO,
  FIJAR_NOMBRAMIENTO_DE_ACUERDO, EJECUTAR_ACUERDO,
} from '@/graphql/queries/secretaria.js'
import { GET_CARGOS } from '@/graphql/queries/organos.js'
import { PlusIcon, UserPlusIcon, BoltIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const { tienePermiso } = usePermisos()
const toast = useToast()
const confirm = useConfirm()
const { unidades, cargarArbol } = useUnidadesOrganizativas()

const reunionId = route.params.id

const loading   = ref(false)
const error     = ref('')
const guardando = ref(false)
const ejecutando = ref(null)

const reunion    = ref(null)
const tipos      = ref([])
const puntos     = ref([])
const asistentes = ref([])
const acuerdos   = ref([])
const miembros   = ref([])
const cargos     = ref([])
// Si la carga de asistentes falla, se avisa sin tumbar la página.
const asistentesNoLegibles = ref(false)

const puntoActivo   = ref(null)
const acuerdoActivo = ref(null)

const drawerPunto        = ref(false)
const drawerAsistente    = ref(false)
const drawerAcuerdo      = ref(false)
const drawerNombramiento = ref(false)

// ── Catálogos de la vista ────────────────────────────────────────────────────
const OPCIONES_TIPO_PUNTO = [
  { value: 'ORDINARIO',   label: 'Ordinario' },
  { value: 'EXTRAORDINARIO', label: 'Extraordinario' },
  { value: 'INFORMATIVO', label: 'Informativo' },
  { value: 'RUEGOS',      label: 'Ruegos y preguntas' },
]
const OPCIONES_ASISTENCIA = [
  { value: 'PRESENCIAL',  label: 'Presencial' },
  { value: 'TELEMATICA',  label: 'Telemática' },
  { value: 'REPRESENTADO', label: 'Representado' },
  { value: 'EXCUSADO',    label: 'Excusado' },
]
const OPCIONES_MAYORIA = [
  { value: 'SIMPLE',      label: 'Simple' },
  { value: 'ABSOLUTA',    label: 'Absoluta' },
  { value: 'CUALIFICADA', label: 'Cualificada' },
  { value: 'UNANIMIDAD',  label: 'Unanimidad' },
]
const OPCIONES_RESULTADO = [
  { value: 'APROBADO',  label: 'Aprobado' },
  { value: 'RECHAZADO', label: 'Rechazado' },
  { value: 'RETIRADO',  label: 'Retirado' },
  { value: 'APLAZADO',  label: 'Aplazado' },
]
const OPCIONES_TIPO_NOMBRAMIENTO = [
  { value: 'NOMBRAMIENTO', label: 'Nombramiento' },
  { value: 'CESE',         label: 'Cese' },
]
const ESTADOS_REUNION = {
  CONVOCADA:     { etiqueta: 'Convocada',        clase: 'bg-blue-100 text-blue-700' },
  CELEBRADA:     { etiqueta: 'Celebrada',        clase: 'bg-yellow-100 text-yellow-700' },
  ACTA_BORRADOR: { etiqueta: 'Acta en borrador', clase: 'bg-orange-100 text-orange-700' },
  ACTA_APROBADA: { etiqueta: 'Acta aprobada',    clase: 'bg-green-100 text-green-700' },
  CANCELADA:     { etiqueta: 'Cancelada',        clase: 'bg-gray-100 text-gray-500' },
}

const opcionesCargo = computed(() =>
  cargos.value.map(c => ({ value: c.id, label: c.nombre }))
)

// ── Formularios ──────────────────────────────────────────────────────────────
const formPunto = ref({ titulo: '', descripcion: '', tipo: 'ORDINARIO' })
const formAsistente = ref({ miembroId: null, tipoAsistencia: 'PRESENCIAL', representadoPorId: null, cargo: '' })
const formAcuerdo = ref({
  descripcion: '', tipoMayoria: 'SIMPLE', resultado: 'APROBADO',
  votosFavor: 0, votosContra: 0, abstenciones: 0,
})
const formNombramiento = ref({
  tipoCodigo: 'NOMBRAMIENTO', miembroId: null, cargoId: '',
  agrupacionId: null, fechaInicio: '', fechaFin: '',
})

// ── Columnas ─────────────────────────────────────────────────────────────────
const columnasPuntos = [
  { key: 'orden',    label: '#',        align: 'center', width: '4rem' },
  { key: 'titulo',   label: 'Punto' },
  { key: 'tipo',     label: 'Tipo',     align: 'center' },
  { key: 'acuerdos', label: 'Acuerdos', align: 'center' },
]
const columnasAsistentes = [
  { key: 'miembro',         label: 'Miembro', ordenable: true, valorOrden: a => nombreMiembro(a.miembroId) },
  { key: 'tipoAsistencia',  label: 'Asistencia', align: 'center', ordenable: true },
  { key: 'representadoPor', label: 'Representado por' },
  { key: 'cargo',           label: 'Cargo' },
]

// ── Derivados ────────────────────────────────────────────────────────────────
const nombreTipo = computed(() =>
  tipos.value.find(t => t.id === reunion.value?.tipoReunionId)?.nombre ?? 'Reunión'
)
const nombreOrgano = computed(() =>
  tipos.value.find(t => t.id === reunion.value?.tipoReunionId)?.tipoOrganoNombre ?? '—'
)
const tituloReunion = computed(() =>
  reunion.value ? `${nombreTipo.value} nº ${reunion.value.numeroConvocatoria}/${reunion.value.anio}` : 'Reunión'
)
const subtituloReunion = computed(() =>
  reunion.value ? `${nombreOrgano.value} · ${formatFecha(reunion.value.fechaConvocatoria)}` : ''
)

const formatFecha     = (s) => s ? new Date(s).toLocaleDateString('es-ES') : '—'
const formatFechaHora = (s) => s ? new Date(s).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' }) : '—'

const etiquetaEstado = (e) => ESTADOS_REUNION[e]?.etiqueta ?? e
const badgeEstado    = (e) => ESTADOS_REUNION[e]?.clase ?? 'bg-gray-100 text-gray-500'
const etiquetaTipoPunto = (t) => OPCIONES_TIPO_PUNTO.find(o => o.value === t)?.label ?? t
const etiquetaAsistencia = (t) => OPCIONES_ASISTENCIA.find(o => o.value === t)?.label ?? t
const etiquetaMayoria = (m) => OPCIONES_MAYORIA.find(o => o.value === m)?.label ?? m
const etiquetaResultado = (r) => r ? (OPCIONES_RESULTADO.find(o => o.value === r)?.label ?? r) : 'Sin resultado'

const badgeAsistencia = (t) => ({
  PRESENCIAL:   'bg-green-100 text-green-700',
  TELEMATICA:   'bg-blue-100 text-blue-700',
  REPRESENTADO: 'bg-purple-100 text-purple-700',
  EXCUSADO:     'bg-gray-100 text-gray-500',
}[t] ?? 'bg-gray-100 text-gray-500')

const badgeResultado = (r) => ({
  APROBADO:  'bg-green-100 text-green-700',
  RECHAZADO: 'bg-red-100 text-red-700',
  RETIRADO:  'bg-gray-100 text-gray-500',
  APLAZADO:  'bg-amber-100 text-amber-700',
}[r] ?? 'bg-gray-100 text-gray-500')

const nombreMiembro = (id) => {
  const m = miembros.value.find(x => x.id === id)
  return m ? `${m.nombre} ${m.apellido1 ?? ''} ${m.apellido2 ?? ''}`.trim() : '—'
}
const acuerdosDePunto = (puntoId) => acuerdos.value.filter(a => a.puntoOrdenDiaId === puntoId)

const mensajeError = (e) => e?.response?.errors?.[0]?.message ?? e?.message ?? 'Error inesperado'

// ── Carga ────────────────────────────────────────────────────────────────────
// Vista de DETALLE: no está en el keep-alive de App.vue, así que carga en
// `onMounted` (un `onActivated` no llegaría a dispararse nunca).
async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const [dTipos, dReuniones] = await Promise.all([
      executeQuery(GET_TIPOS_REUNION),
      executeQuery(GET_REUNIONES, {}),
    ])
    tipos.value = dTipos?.tiposReunion ?? []
    reunion.value = (dReuniones?.reuniones ?? []).find(r => r.id === reunionId) ?? null
    if (!reunion.value) {
      // La query `reuniones` filtra por año por defecto en la lista; aquí pedimos
      // sin filtro, así que si no aparece es que no existe.
      error.value = 'No se ha encontrado la reunión'
      return
    }
    await recargarContenido()
  } catch (e) {
    error.value = mensajeError(e)
  } finally {
    loading.value = false
  }
}

async function recargarContenido() {
  const [dPuntos, dAcuerdos] = await Promise.all([
    executeQuery(GET_PUNTOS_ORDEN_DIA, { reunionId }),
    executeQuery(GET_ACUERDOS_DE_REUNION, { reunionId }),
  ])
  puntos.value   = dPuntos?.puntosOrdenDia ?? []
  acuerdos.value = dAcuerdos?.acuerdosDeReunion ?? []
  await recargarAsistentes()
}

// Los asistentes se cargan aparte y sin tumbar la página si fallan.
// (La query se llama `asistentesDeReunion`, no `asistentesReunion`: ese nombre ya lo
//  ocupa el CRUD de asistentes a reuniones de GRUPO DE TRABAJO y eclipsaba a este.)
async function recargarAsistentes() {
  try {
    const d = await executeQuery(GET_ASISTENTES_REUNION, { reunionId })
    asistentes.value = d?.asistentesDeReunion ?? []
    asistentesNoLegibles.value = false
  } catch {
    asistentesNoLegibles.value = true
  }
}

async function cargarAuxiliares() {
  try {
    const [dMiembros, dCargos] = await Promise.all([
      executeQuery(GET_MIEMBROS_LIGERO),
      executeQuery(GET_CARGOS),
    ])
    miembros.value = dMiembros?.miembros ?? []
    cargos.value = (dCargos?.cargos ?? []).filter(c => c.activo !== false)
    await cargarArbol()
  } catch (e) {
    toast.error(mensajeError(e))
  }
}

// ── Orden del día ────────────────────────────────────────────────────────────
function abrirPunto() {
  formPunto.value = { titulo: '', descripcion: '', tipo: 'ORDINARIO' }
  drawerPunto.value = true
}

async function guardarPunto() {
  if (!formPunto.value.titulo.trim()) { toast.error('El punto necesita un título'); return }
  guardando.value = true
  try {
    await executeMutation(AGREGAR_PUNTO_ORDEN_DIA, {
      reunionId,
      titulo: formPunto.value.titulo.trim(),
      descripcion: formPunto.value.descripcion || null,
      orden: null,               // sin orden explícito, el backend lo añade al final
      tipo: formPunto.value.tipo,
    })
    drawerPunto.value = false
    await recargarContenido()
    toast.success('Punto añadido al orden del día')
  } catch (e) {
    toast.error(mensajeError(e))
  } finally {
    guardando.value = false
  }
}

// ── Asistentes ───────────────────────────────────────────────────────────────
function abrirAsistente() {
  formAsistente.value = { miembroId: null, tipoAsistencia: 'PRESENCIAL', representadoPorId: null, cargo: '' }
  drawerAsistente.value = true
}

async function guardarAsistente() {
  if (!formAsistente.value.miembroId) { toast.error('Selecciona el miembro que asiste'); return }
  guardando.value = true
  try {
    const d = await executeMutation(REGISTRAR_ASISTENTE_REUNION, {
      reunionId,
      miembroId: formAsistente.value.miembroId,
      tipoAsistencia: formAsistente.value.tipoAsistencia,
      representadoPorId: formAsistente.value.tipoAsistencia === 'REPRESENTADO'
        ? (formAsistente.value.representadoPorId || null) : null,
      cargo: formAsistente.value.cargo || null,
    })
    drawerAsistente.value = false
    // La mutación devuelve el asistente creado: se pinta al instante, sin esperar
    // a la recarga.
    const creado = d?.registrarAsistenteReunion
    if (creado) asistentes.value = [...asistentes.value.filter(a => a.id !== creado.id), creado]
    await recargarAsistentes()
    toast.success('Asistente registrado')
  } catch (e) {
    toast.error(mensajeError(e))
  } finally {
    guardando.value = false
  }
}

// ── Acuerdos ─────────────────────────────────────────────────────────────────
function abrirAcuerdo(punto) {
  puntoActivo.value = punto
  formAcuerdo.value = {
    descripcion: '', tipoMayoria: 'SIMPLE', resultado: 'APROBADO',
    votosFavor: 0, votosContra: 0, abstenciones: 0,
  }
  drawerAcuerdo.value = true
}

async function guardarAcuerdo() {
  if (!formAcuerdo.value.descripcion.trim()) { toast.error('Describe el acuerdo adoptado'); return }
  guardando.value = true
  try {
    await executeMutation(REGISTRAR_ACUERDO, {
      data: {
        puntoOrdenDiaId: puntoActivo.value.id,
        descripcion: formAcuerdo.value.descripcion.trim(),
        tipoMayoria: formAcuerdo.value.tipoMayoria,
        resultado: formAcuerdo.value.resultado,
        votosFavor: formAcuerdo.value.votosFavor || 0,
        votosContra: formAcuerdo.value.votosContra || 0,
        abstenciones: formAcuerdo.value.abstenciones || 0,
      },
    })
    drawerAcuerdo.value = false
    await recargarContenido()
    toast.success('Acuerdo registrado')
  } catch (e) {
    toast.error(mensajeError(e))
  } finally {
    guardando.value = false
  }
}

// ── El acuerdo produce el mandato ────────────────────────────────────────────
function abrirNombramiento(acuerdo) {
  acuerdoActivo.value = acuerdo
  formNombramiento.value = {
    tipoCodigo: 'NOMBRAMIENTO', miembroId: null, cargoId: '',
    agrupacionId: reunion.value?.agrupacionId ?? null,
    fechaInicio: new Date().toISOString().slice(0, 10),
    fechaFin: '',
  }
  drawerNombramiento.value = true
}

async function guardarNombramiento() {
  const f = formNombramiento.value
  if (!f.miembroId)   { toast.error('Selecciona el miembro'); return }
  if (!f.cargoId)     { toast.error('Selecciona el cargo'); return }
  if (!f.fechaInicio) { toast.error('Indica la fecha de inicio'); return }
  guardando.value = true
  try {
    await executeMutation(FIJAR_NOMBRAMIENTO_DE_ACUERDO, {
      acuerdoId: acuerdoActivo.value.id,
      miembroId: f.miembroId,
      cargoId: f.cargoId,
      fechaInicio: f.fechaInicio,
      agrupacionId: f.agrupacionId || null,
      fechaFin: f.fechaFin || null,
      tipoCodigo: f.tipoCodigo,
    })
    drawerNombramiento.value = false
    toast.success(f.tipoCodigo === 'CESE'
      ? 'Cese fijado en el acuerdo. Ejecútalo para cerrar el mandato.'
      : 'Nombramiento fijado en el acuerdo. Ejecútalo para crear el mandato.')
  } catch (e) {
    // El backend explica por qué no se puede (p. ej. el acuerdo ya se ejecutó).
    toast.error(mensajeError(e))
  } finally {
    guardando.value = false
  }
}

async function ejecutar(acuerdo) {
  const ok = await confirm({
    titulo: '¿Ejecutar el acuerdo?',
    mensaje: 'Dará efecto real al acuerdo: creará el mandato (o lo cerrará, si es un cese) '
           + 'y derivará los roles del cargo. Exige acuerdo aprobado y acta aprobada.',
    variante: 'aviso',
    etiquetaConfirmar: 'Sí, ejecutar',
  })
  if (!ok) return

  ejecutando.value = acuerdo.id
  try {
    await executeMutation(EJECUTAR_ACUERDO, { acuerdoId: acuerdo.id, exigirActaAprobada: true })
    await recargarContenido()
    toast.success('Acuerdo ejecutado: el mandato ya está en vigor')
  } catch (e) {
    // El error del backend es información valiosa («la reunión no tiene acta»,
    // «el acta no está aprobada», «el acuerdo no es ejecutable»): se muestra tal cual.
    toast.error(mensajeError(e))
  } finally {
    ejecutando.value = null
  }
}

onMounted(async () => {
  await cargar()
  await cargarAuxiliares()
})
</script>
