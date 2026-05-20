<template>
  <AppLayout title="Presidencia" subtitle="Cuadro de mando ejecutivo">

    <EstadoCarga v-if="loading" mensaje="Cargando cuadro de mando…" />

    <template v-else>

      <!-- ── Bloque de alertas críticas ── -->
      <section v-if="alertas.length > 0" class="mb-8">
        <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Alertas</h2>
        <div class="space-y-2">
          <div v-for="a in alertas" :key="a.id"
            class="flex items-start gap-3 rounded-xl border px-4 py-3 text-sm"
            :class="a.clase">
            <span class="text-base flex-shrink-0 mt-0.5">{{ a.icono }}</span>
            <div class="flex-1 min-w-0">
              <p class="font-medium">{{ a.titulo }}</p>
              <p class="text-xs mt-0.5 opacity-80">{{ a.detalle }}</p>
            </div>
            <router-link :to="a.ruta"
              class="flex-shrink-0 text-xs font-medium underline underline-offset-2 opacity-70 hover:opacity-100 transition-opacity">
              Ver →
            </router-link>
          </div>
        </div>
      </section>

      <!-- ── KPIs ── -->
      <section class="mb-8">
        <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Estado general</h2>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div v-for="kpi in kpis" :key="kpi.label"
            class="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex flex-col gap-1">
            <span class="text-2xl">{{ kpi.icono }}</span>
            <p class="text-2xl font-bold text-gray-900 mt-1">{{ kpi.valor }}</p>
            <p class="text-xs text-gray-500 leading-tight">{{ kpi.label }}</p>
            <p v-if="kpi.sub" class="text-xs font-medium mt-0.5" :class="kpi.subClase ?? 'text-gray-400'">
              {{ kpi.sub }}
            </p>
          </div>
        </div>
      </section>

      <!-- ── Columnas: Acuerdos + Reuniones ── -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">

        <!-- Acuerdos pendientes -->
        <section class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
            <h2 class="font-semibold text-gray-900">Acuerdos pendientes</h2>
            <router-link to="/secretaria/acuerdos"
              class="text-xs text-purple-600 hover:text-purple-800 font-medium transition-colors">
              Ver todos →
            </router-link>
          </div>
          <div v-if="acuerdos.length === 0" class="px-5 py-8 text-center text-sm text-gray-400">
            No hay acuerdos pendientes de ejecutar 🎉
          </div>
          <ul v-else class="divide-y divide-gray-100">
            <li v-for="a in acuerdos.slice(0, 5)" :key="a.id" class="px-5 py-3 flex items-start gap-3">
              <span :class="badgeEjecucion(a.estadoEjecucionCodigo)"
                class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium flex-shrink-0 mt-0.5">
                {{ etiquetaEjecucion(a.estadoEjecucionCodigo) }}
              </span>
              <div class="flex-1 min-w-0">
                <p class="text-sm text-gray-800 truncate">{{ a.descripcion }}</p>
                <p v-if="a.fechaLimiteEjecucion"
                  class="text-xs mt-0.5"
                  :class="vencido(a.fechaLimiteEjecucion) ? 'text-red-600 font-medium' : 'text-gray-400'">
                  {{ vencido(a.fechaLimiteEjecucion) ? '⚠ Vencido · ' : '' }}{{ formatFecha(a.fechaLimiteEjecucion) }}
                </p>
              </div>
            </li>
          </ul>
          <div v-if="acuerdos.length > 5" class="px-5 py-2 bg-gray-50 text-xs text-gray-500 text-center">
            Y {{ acuerdos.length - 5 }} más…
          </div>
        </section>

        <!-- Próximas reuniones -->
        <section class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
            <h2 class="font-semibold text-gray-900">Próximas reuniones</h2>
            <router-link to="/secretaria/reuniones"
              class="text-xs text-purple-600 hover:text-purple-800 font-medium transition-colors">
              Ver todas →
            </router-link>
          </div>
          <div v-if="reuniones.length === 0" class="px-5 py-8 text-center text-sm text-gray-400">
            No hay reuniones convocadas próximamente
          </div>
          <ul v-else class="divide-y divide-gray-100">
            <li v-for="r in reuniones.slice(0, 5)" :key="r.id" class="px-5 py-3 flex items-center gap-3">
              <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-purple-50 border border-purple-100 flex flex-col items-center justify-center text-center">
                <span class="text-xs font-bold text-purple-700 leading-none">{{ diaFecha(r.fechaCelebracion ?? r.fechaConvocatoria) }}</span>
                <span class="text-xs text-purple-500 leading-none">{{ mesFecha(r.fechaCelebracion ?? r.fechaConvocatoria) }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-800 truncate">{{ nombreTipoReunion(r.tipoReunionId) }}</p>
                <p class="text-xs text-gray-400">
                  {{ r.esTelematica ? '📹 Telemática' : (r.lugar ?? 'Sin lugar definido') }}
                </p>
              </div>
            </li>
          </ul>
        </section>
      </div>

      <!-- ── Mandatos de la Junta ── -->
      <section class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden mb-8">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 class="font-semibold text-gray-900">Mandatos vigentes</h2>
          <router-link to="/membresia/junta"
            class="text-xs text-purple-600 hover:text-purple-800 font-medium transition-colors">
            Gestionar →
          </router-link>
        </div>
        <div v-if="mandatos.length === 0" class="px-5 py-8 text-center text-sm text-gray-400">
          No hay mandatos activos registrados
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-100 text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cargo</th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Miembro</th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Desde</th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hasta</th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="m in mandatos" :key="m.id" class="hover:bg-gray-50 transition-colors">
                <td class="px-4 py-2 font-medium text-gray-900">{{ m.cargo?.nombre ?? '—' }}</td>
                <td class="px-4 py-2 text-gray-600">{{ m.miembro?.nombre }} {{ m.miembro?.apellido1 }}</td>
                <td class="px-4 py-2 text-gray-500 text-xs">{{ formatFecha(m.fechaInicio) }}</td>
                <td class="px-4 py-2 text-xs" :class="proximoVencimiento(m.fechaFin) ? 'text-amber-600 font-medium' : 'text-gray-500'">
                  {{ m.fechaFin ? formatFecha(m.fechaFin) : 'Indefinido' }}
                  <span v-if="proximoVencimiento(m.fechaFin)" class="ml-1">⚠</span>
                </td>
                <td class="px-4 py-2">
                  <span class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700">
                    Activo
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ── Convenios próximos a vencer ── -->
      <section v-if="conveniosVencer.length > 0"
        class="bg-white rounded-xl border border-amber-200 shadow-sm overflow-hidden mb-8">
        <div class="px-5 py-4 border-b border-amber-100 flex items-center justify-between bg-amber-50">
          <h2 class="font-semibold text-amber-900">Convenios próximos a vencer <span class="text-amber-600 font-normal text-sm">(60 días)</span></h2>
          <router-link to="/secretaria/convenios"
            class="text-xs text-amber-700 hover:text-amber-900 font-medium transition-colors">
            Ver todos →
          </router-link>
        </div>
        <ul class="divide-y divide-amber-50">
          <li v-for="c in conveniosVencer" :key="c.id" class="px-5 py-3 flex items-center gap-4">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">{{ c.titulo }}</p>
              <p class="text-xs text-gray-500">{{ c.entidadContraparte }} · Ref: {{ c.referencia }}</p>
            </div>
            <div class="text-right flex-shrink-0">
              <p class="text-sm font-semibold text-amber-700">{{ formatFecha(c.fechaFin) }}</p>
              <p v-if="c.renovacionAutomatica" class="text-xs text-blue-500">↻ Automática</p>
              <p v-else class="text-xs text-amber-500">Requiere acción</p>
            </div>
          </li>
        </ul>
      </section>

    </template>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import { executeQuery } from '@/graphql/client'
import {
  GET_ACUERDOS_PENDIENTES_PRES,
  GET_ACTAS_PENDIENTES_PRES,
  GET_PROXIMAS_REUNIONES,
  GET_CONVENIOS_VENCER,
  GET_MANDATOS_VIGENTES,
  GET_ULTIMO_LIBRO_SOCIOS,
} from '@/graphql/queries/presidencia.js'
import { GET_TIPOS_REUNION } from '@/graphql/queries/secretaria.js'

const loading = ref(true)

// Datos cargados
const acuerdos        = ref([])
const actasPendientes = ref([])
const reuniones       = ref([])
const conveniosVencer = ref([])
const mandatos        = ref([])
const ultimoSnapshot  = ref(null)
const tiposReunion    = ref([])

// ── Helpers ──────────────────────────────────────────────────────────────────

const formatFecha  = (s) => s ? new Date(s).toLocaleDateString('es-ES') : '—'
const diaFecha     = (s) => s ? new Date(s).getDate().toString().padStart(2, '0') : '—'
const mesFecha     = (s) => s ? new Date(s).toLocaleDateString('es-ES', { month: 'short' }).replace('.', '') : '—'
const vencido      = (s) => s && new Date(s) < new Date()
const diasRestantes = (s) => {
  if (!s) return null
  const diff = Math.ceil((new Date(s) - new Date()) / 86400000)
  return diff
}
const proximoVencimiento = (s) => {
  const dias = diasRestantes(s)
  return dias !== null && dias >= 0 && dias <= 90
}
const nombreTipoReunion = (id) => tiposReunion.value.find(t => t.id === id)?.nombre ?? '—'

const ESTADOS_EJEC = [
  { codigo: 'PENDIENTE',  etiqueta: 'Pendiente',  clase: 'bg-yellow-100 text-yellow-700' },
  { codigo: 'EN_CURSO',   etiqueta: 'En curso',   clase: 'bg-blue-100 text-blue-700' },
  { codigo: 'COMPLETADO', etiqueta: 'Completado', clase: 'bg-green-100 text-green-700' },
  { codigo: 'ARCHIVADO',  etiqueta: 'Archivado',  clase: 'bg-gray-100 text-gray-500' },
]
const badgeEjecucion   = (c) => ESTADOS_EJEC.find(e => e.codigo === c)?.clase ?? 'bg-gray-100 text-gray-500'
const etiquetaEjecucion = (c) => ESTADOS_EJEC.find(e => e.codigo === c)?.etiqueta ?? c

// ── KPIs ─────────────────────────────────────────────────────────────────────

const kpis = computed(() => {
  const snap = ultimoSnapshot.value
  const acuerdosVencidos = acuerdos.value.filter(a => vencido(a.fechaLimiteEjecucion)).length
  const mandatosProximos = mandatos.value.filter(m => proximoVencimiento(m.fechaFin)).length

  return [
    {
      icono: '👥',
      valor: snap?.totalSociosActivos ?? '—',
      label: 'Socios activos',
      sub: snap ? `${snap.totalSociosHistorico} total histórico` : null,
      subClase: 'text-gray-400',
    },
    {
      icono: '📋',
      valor: acuerdos.value.length,
      label: 'Acuerdos pendientes',
      sub: acuerdosVencidos > 0 ? `${acuerdosVencidos} con plazo vencido` : 'Al día',
      subClase: acuerdosVencidos > 0 ? 'text-red-600' : 'text-green-600',
    },
    {
      icono: '📅',
      valor: reuniones.value.length,
      label: 'Reuniones convocadas',
      sub: actasPendientes.value.length > 0
        ? `${actasPendientes.value.length} acta${actasPendientes.value.length > 1 ? 's' : ''} pendiente${actasPendientes.value.length > 1 ? 's' : ''}`
        : 'Sin actas pendientes',
      subClase: actasPendientes.value.length > 0 ? 'text-amber-600' : 'text-green-600',
    },
    {
      icono: '🏛️',
      valor: mandatos.value.length,
      label: 'Cargos en vigor',
      sub: mandatosProximos > 0 ? `${mandatosProximos} mandato${mandatosProximos > 1 ? 's' : ''} próximo a vencer` : 'Sin vencimientos próximos',
      subClase: mandatosProximos > 0 ? 'text-amber-600' : 'text-green-600',
    },
  ]
})

// ── Alertas críticas ─────────────────────────────────────────────────────────

const alertas = computed(() => {
  const lista = []

  // Actas pendientes de aprobación
  if (actasPendientes.value.length > 0) {
    lista.push({
      id: 'actas-pendientes',
      icono: '📄',
      titulo: `${actasPendientes.value.length} acta${actasPendientes.value.length > 1 ? 's' : ''} pendiente${actasPendientes.value.length > 1 ? 's' : ''} de aprobación`,
      detalle: 'Deben aprobarse en la siguiente reunión del órgano correspondiente.',
      ruta: '/secretaria/actas',
      clase: 'bg-amber-50 border-amber-200 text-amber-800',
    })
  }

  // Acuerdos con plazo vencido
  const vencidos = acuerdos.value.filter(a => vencido(a.fechaLimiteEjecucion))
  if (vencidos.length > 0) {
    lista.push({
      id: 'acuerdos-vencidos',
      icono: '⚠️',
      titulo: `${vencidos.length} acuerdo${vencidos.length > 1 ? 's' : ''} con plazo de ejecución vencido`,
      detalle: 'Revisa el estado de ejecución y actualiza o archiva los acuerdos afectados.',
      ruta: '/secretaria/acuerdos',
      clase: 'bg-red-50 border-red-200 text-red-800',
    })
  }

  // Mandatos próximos a vencer (< 90 días)
  const mandatosProx = mandatos.value.filter(m => proximoVencimiento(m.fechaFin))
  if (mandatosProx.length > 0) {
    const nombres = mandatosProx
      .map(m => m.cargo?.nombre)
      .filter(Boolean)
      .slice(0, 3)
      .join(', ')
    lista.push({
      id: 'mandatos-proximos',
      icono: '🏛️',
      titulo: `Mandato${mandatosProx.length > 1 ? 's' : ''} próximo${mandatosProx.length > 1 ? 's' : ''} a vencer: ${nombres}`,
      detalle: 'Convoca renovación o tramita los nombramientos correspondientes.',
      ruta: '/membresia/junta',
      clase: 'bg-blue-50 border-blue-200 text-blue-800',
    })
  }

  // Convenios próximos a vencer sin renovación automática
  const convNoAuto = conveniosVencer.value.filter(c => !c.renovacionAutomatica)
  if (convNoAuto.length > 0) {
    lista.push({
      id: 'convenios-vencer',
      icono: '📝',
      titulo: `${convNoAuto.length} convenio${convNoAuto.length > 1 ? 's' : ''} vence${convNoAuto.length > 1 ? 'n' : ''} en los próximos 60 días sin renovación automática`,
      detalle: 'Revisa las condiciones y decide si renovar, renegociar o dejar vencer.',
      ruta: '/secretaria/convenios',
      clase: 'bg-orange-50 border-orange-200 text-orange-800',
    })
  }

  return lista
})

// ── Carga ────────────────────────────────────────────────────────────────────

const cargar = async () => {
  loading.value = true
  const anio = new Date().getFullYear()
  try {
    const [
      dataAcuerdos,
      dataActas,
      dataReuniones,
      dataConvenios,
      dataMandatos,
      dataSnapshot,
      dataTipos,
    ] = await Promise.allSettled([
      executeQuery(GET_ACUERDOS_PENDIENTES_PRES),
      executeQuery(GET_ACTAS_PENDIENTES_PRES),
      executeQuery(GET_PROXIMAS_REUNIONES, { anio }),
      executeQuery(GET_CONVENIOS_VENCER),
      executeQuery(GET_MANDATOS_VIGENTES),
      executeQuery(GET_ULTIMO_LIBRO_SOCIOS),
      executeQuery(GET_TIPOS_REUNION),
    ])

    // Promise.allSettled: usar .value si fulfilled, ignorar si rejected
    acuerdos.value        = dataAcuerdos.status       === 'fulfilled' ? dataAcuerdos.value?.acuerdosPendientes ?? []        : []
    actasPendientes.value = dataActas.status           === 'fulfilled' ? dataActas.value?.actasPendientesAprobacion ?? []   : []
    reuniones.value       = dataReuniones.status       === 'fulfilled' ? dataReuniones.value?.reuniones ?? []               : []
    conveniosVencer.value = dataConvenios.status       === 'fulfilled' ? dataConvenios.value?.convenios ?? []               : []
    mandatos.value        = dataMandatos.status        === 'fulfilled' ? dataMandatos.value?.historialNombramientos ?? []   : []
    ultimoSnapshot.value  = dataSnapshot.status        === 'fulfilled' ? (dataSnapshot.value?.libroSociosSnapshots ?? [])[0] ?? null : null
    tiposReunion.value    = dataTipos.status           === 'fulfilled' ? dataTipos.value?.tiposReunion ?? []                : []

  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>
