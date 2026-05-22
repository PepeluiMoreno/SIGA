<template>
  <AppLayout title="Donaciones" subtitle="Registro, cobro y certificados fiscales (Ley 49/2002)">

    <FilterBar
      v-model="filtros"
      v-model:search="busqueda"
      search-placeholder="Buscar por donante, NIF o nº certificado…"
      create-label="+ Nueva donación"
      :fields="camposFiltro"
      :description="descripcionFiltros"
      @create="abrirModalAlta()"
    >
      <template #extra>
        <button @click="abrirModalCertificados()" class="btn-secondary text-xs">
          Emitir certificados anuales…
        </button>
      </template>
    </FilterBar>

    <div class="text-xs text-slate-500 mt-2 mb-3 px-1 flex items-center gap-3 flex-wrap">
      <span>{{ donacionesFiltradas.length }} de {{ donaciones.length }} donaciones</span>
      <span class="text-slate-300">·</span>
      <span class="text-green-700"><strong>{{ contarEstado('COBRADA') }}</strong> cobradas</span>
      <span class="text-amber-700"><strong>{{ contarEstado('REGISTRADA') }}</strong> registradas</span>
      <span class="text-slate-500"><strong>{{ contarEstado('ANULADA') }}</strong> anuladas</span>
      <span class="text-slate-300">·</span>
      <span class="text-slate-600">
        Total recibido <strong class="font-mono">{{ fmt(totalRecibidoFiltrado) }}</strong>
      </span>
      <span class="text-slate-300">·</span>
      <span class="text-slate-600">
        Certificadas <strong>{{ contarCertificadas() }}</strong> · sin certificar <strong>{{ contarSinCertificar() }}</strong>
      </span>
    </div>

    <div v-if="loading" class="py-12 text-center text-slate-400 text-sm">Cargando…</div>

    <div v-else-if="donacionesFiltradas.length" class="bg-white border border-slate-200 rounded-xl overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-slate-50 text-slate-600 text-xs uppercase">
          <tr>
            <th class="px-3 py-2 text-left">Fecha</th>
            <th class="px-3 py-2 text-left">Donante</th>
            <th class="px-3 py-2 text-center">Tipo</th>
            <th class="px-3 py-2 text-right">Importe</th>
            <th class="px-3 py-2 text-left">Concepto</th>
            <th class="px-3 py-2 text-center">Estado</th>
            <th class="px-3 py-2 text-center">Cert.</th>
            <th class="px-3 py-2 text-center w-8"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="d in donacionesFiltradas" :key="d.id" class="hover:bg-slate-50 cursor-pointer"
              @click="abrirDetalle(d)">
            <td class="px-3 py-1.5 text-xs text-slate-600">{{ fechaFmt(d.fecha) }}</td>
            <td class="px-3 py-1.5">
              <div class="font-medium text-slate-800">{{ donanteNombre(d) || '—' }}</div>
              <div v-if="d.donanteDni" class="text-[10px] text-slate-500 font-mono">{{ d.donanteDni }}</div>
            </td>
            <td class="px-3 py-1.5 text-center">
              <span :class="badgeTipo(d.tipo)" class="text-[10px] uppercase rounded-full px-2 py-0.5">
                {{ d.tipo === 'ESPECIE' ? 'B · Especie' : 'A · Dineraria' }}
              </span>
            </td>
            <td class="px-3 py-1.5 text-right font-mono">{{ fmt(importeDonacion(d)) }}</td>
            <td class="px-3 py-1.5 text-slate-600 text-xs truncate max-w-xs">
              {{ d.concepto?.nombre || (d.tipo === 'ESPECIE' ? d.descripcionEspecie : '—') }}
            </td>
            <td class="px-3 py-1.5 text-center">
              <span :class="badgeEstado(d.estado?.nombre)" class="text-[10px] uppercase rounded-full px-2 py-0.5">
                {{ d.estado?.nombre || '—' }}
              </span>
            </td>
            <td class="px-3 py-1.5 text-center">
              <span v-if="d.certificadoEmitido" class="text-green-600 font-mono text-[10px]">
                {{ d.numeroCertificado || '✓' }}
              </span>
              <span v-else class="text-slate-300">—</span>
            </td>
            <td class="px-3 py-1.5 text-center text-slate-400">›</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-else class="text-center text-slate-400 py-12 text-sm border border-dashed border-slate-200 rounded-xl">
      No hay donaciones con los filtros aplicados.
    </p>

    <ErrorAlert v-if="error" :message="error" />

    <!-- ────────────────────────────────────────────────────────────────────── -->
    <!-- Modal: nueva donación                                                  -->
    <!-- ────────────────────────────────────────────────────────────────────── -->
    <div v-if="modalAlta" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" @click.self="modalAlta = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-2xl flex flex-col max-h-[90vh]">
        <div class="px-6 py-4 border-b border-slate-200">
          <h3 class="font-semibold text-slate-800">Nueva donación</h3>
          <p class="text-xs text-slate-500 mt-0.5">
            Las donaciones con NIF y no anónimas son certificables a efectos fiscales.
          </p>
        </div>
        <div class="px-6 py-5 space-y-3 overflow-y-auto">
          <!-- Tipo + Carácter -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label">Tipo *</label>
              <select v-model="formAlta.tipo" class="input">
                <option value="DINERARIA">Dineraria (clave A)</option>
                <option value="ESPECIE">En especie (clave B)</option>
              </select>
            </div>
            <div>
              <label class="label">Carácter *</label>
              <select v-model="formAlta.caracter" class="input">
                <option value="PUNTUAL">Puntual</option>
                <option value="RECURRENTE" disabled>Recurrente (v2)</option>
              </select>
            </div>
          </div>

          <!-- Donante -->
          <div class="border border-slate-200 rounded-lg p-3 bg-slate-50">
            <div class="text-xs font-medium text-slate-700 mb-2">Donante</div>
            <div class="grid grid-cols-3 gap-2 mb-2">
              <label class="flex items-center gap-1.5 text-xs text-slate-700">
                <input type="radio" v-model="formAlta.donanteTipo" value="MIEMBRO" />
                <span>Socio</span>
              </label>
              <label class="flex items-center gap-1.5 text-xs text-slate-700">
                <input type="radio" v-model="formAlta.donanteTipo" value="EXTERNO" />
                <span>Externo</span>
              </label>
              <label class="flex items-center gap-1.5 text-xs text-slate-700">
                <input type="checkbox" v-model="formAlta.anonima" />
                <span>Anónima (no certificable)</span>
              </label>
            </div>
            <div v-if="formAlta.donanteTipo === 'MIEMBRO' && !formAlta.anonima" class="grid grid-cols-1 gap-2">
              <div>
                <label class="label">Socio *</label>
                <select v-model="formAlta.miembroId" class="input">
                  <option :value="null">— Selecciona socio —</option>
                  <option v-for="m in miembros" :key="m.id" :value="m.id">
                    {{ socioFullName(m) }}{{ m.numeroDocumento ? ` · ${m.numeroDocumento}` : '' }}
                  </option>
                </select>
              </div>
            </div>
            <div v-if="formAlta.donanteTipo === 'EXTERNO' && !formAlta.anonima" class="grid grid-cols-2 gap-2">
              <div class="col-span-2">
                <label class="label">Nombre del donante *</label>
                <input v-model="formAlta.donanteNombre" class="input" placeholder="Nombre o razón social" />
              </div>
              <div>
                <label class="label">NIF (para certificado)</label>
                <input v-model="formAlta.donanteDni" class="input" placeholder="12345678A o G87654321" />
              </div>
              <div>
                <label class="label">Email</label>
                <input v-model="formAlta.donanteEmail" type="email" class="input" />
              </div>
              <div class="col-span-2">
                <label class="label">Teléfono</label>
                <input v-model="formAlta.donanteTelefono" class="input" />
              </div>
            </div>
            <div v-if="formAlta.anonima" class="text-xs text-amber-700 bg-amber-50 p-2 rounded">
              Las donaciones anónimas no son certificables fiscalmente (Ley 49/2002 art. 24).
            </div>
          </div>

          <!-- Importe / Valoración -->
          <div class="grid grid-cols-2 gap-3">
            <div v-if="formAlta.tipo === 'DINERARIA'">
              <label class="label">Importe (€) *</label>
              <input type="number" step="0.01" min="0" v-model.number="formAlta.importe" class="input" />
            </div>
            <div v-else>
              <label class="label">Valoración del bien (€) *</label>
              <input type="number" step="0.01" min="0" v-model.number="formAlta.valoracion" class="input" />
            </div>
            <div>
              <label class="label">Fecha *</label>
              <input type="date" v-model="formAlta.fechaDonacion" class="input" />
            </div>
          </div>

          <!-- Específico ESPECIE -->
          <div v-if="formAlta.tipo === 'ESPECIE'" class="grid grid-cols-1 gap-2">
            <div>
              <label class="label">Descripción del bien *</label>
              <textarea v-model="formAlta.descripcionEspecie" rows="2" class="input"
                        placeholder="Equipo informático, libros, mobiliario…" />
            </div>
            <div>
              <label class="label">Documento de valoración / tasación (URL o ruta)</label>
              <input v-model="formAlta.documentoValoracion" class="input" placeholder="https://… o ruta del PDF" />
            </div>
          </div>

          <!-- Modo de pago + concepto -->
          <div class="grid grid-cols-2 gap-3">
            <div v-if="formAlta.tipo === 'DINERARIA'">
              <label class="label">Modo de ingreso</label>
              <select v-model="formAlta.modoIngreso" class="input">
                <option :value="null">— Selecciona —</option>
                <option value="TRANSFERENCIA">Transferencia</option>
                <option value="EFECTIVO">Efectivo</option>
                <option value="BIZUM">Bizum</option>
                <option value="TARJETA">Tarjeta</option>
                <option value="SEPA">SEPA</option>
              </select>
            </div>
            <div>
              <label class="label">Concepto / Campaña</label>
              <select v-model="formAlta.conceptoId" class="input">
                <option :value="null">— Sin concepto —</option>
                <option v-for="c in conceptos" :key="c.id" :value="c.id">{{ c.nombre }}</option>
              </select>
            </div>
          </div>

          <div v-if="formAlta.tipo === 'DINERARIA'">
            <label class="label">Referencia del pago</label>
            <input v-model="formAlta.referenciaPago" class="input"
                   placeholder="Núm. transferencia, ticket, ID de Bizum…" />
          </div>

          <!-- Cobrar al guardar -->
          <div class="border border-slate-200 rounded-lg p-3 bg-indigo-50/50">
            <label class="flex items-center gap-2 text-sm text-slate-700">
              <input type="checkbox" v-model="formAlta.cobrarInmediato" />
              <span>Marcar como cobrada en este momento (el caso más frecuente)</span>
            </label>
            <div v-if="formAlta.cobrarInmediato && formAlta.tipo === 'DINERARIA'" class="mt-2">
              <label class="label">Cuenta bancaria de destino *</label>
              <select v-model="formAlta.cuentaBancariaId" class="input">
                <option :value="null">— Selecciona cuenta —</option>
                <option v-for="c in cuentasBancarias" :key="c.id" :value="c.id">
                  {{ c.nombre }}{{ c.iban ? ` — ${c.iban}` : '' }}
                </option>
              </select>
            </div>
            <p class="text-xs text-slate-500 mt-2">
              Al cobrarla se genera el apunte de tesorería y el asiento contable
              (Debe 572 / Haber 730).
            </p>
          </div>

          <div>
            <label class="label">Observaciones</label>
            <textarea v-model="formAlta.observaciones" rows="2" class="input" />
          </div>

          <ErrorAlert v-if="formAlta.error" :message="formAlta.error" />
        </div>
        <div class="px-6 py-4 border-t border-slate-200 flex justify-end gap-2">
          <button @click="modalAlta = false" class="btn-secondary text-sm">Cancelar</button>
          <button @click="guardarAlta()" :disabled="ocupado" class="btn-primary text-sm">
            {{ ocupado ? 'Guardando…' : (formAlta.cobrarInmediato ? 'Registrar y cobrar' : 'Registrar') }}
          </button>
        </div>
      </div>
    </div>

    <!-- ────────────────────────────────────────────────────────────────────── -->
    <!-- Modal: detalle de donación                                             -->
    <!-- ────────────────────────────────────────────────────────────────────── -->
    <div v-if="donacionDetalle" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
         @click.self="donacionDetalle = null">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg flex flex-col">
        <div class="px-6 py-4 border-b border-slate-200 flex justify-between items-start">
          <div>
            <h3 class="font-semibold text-slate-800">
              {{ donanteNombre(donacionDetalle) || 'Donación' }}
            </h3>
            <p class="text-xs text-slate-500 mt-0.5">
              <span :class="badgeEstado(donacionDetalle.estado?.nombre)" class="text-[10px] uppercase rounded-full px-2 py-0.5">
                {{ donacionDetalle.estado?.nombre || '—' }}
              </span>
              <span class="ml-2" :class="badgeTipo(donacionDetalle.tipo)">
                {{ donacionDetalle.tipo === 'ESPECIE' ? 'En especie' : 'Dineraria' }}
              </span>
            </p>
          </div>
          <button @click="donacionDetalle = null" class="text-slate-400 hover:text-slate-700 text-xl leading-none">×</button>
        </div>
        <div class="px-6 py-5 space-y-3 text-sm">
          <dl class="grid grid-cols-2 gap-3">
            <div class="col-span-2">
              <dt class="text-xs text-slate-500">Donante</dt>
              <dd class="font-medium text-slate-800">{{ donanteNombre(donacionDetalle) || '—' }}</dd>
              <dd v-if="donacionDetalle.donanteDni" class="font-mono text-xs text-slate-500">{{ donacionDetalle.donanteDni }}</dd>
            </div>
            <div>
              <dt class="text-xs text-slate-500">Fecha</dt>
              <dd>{{ fechaFmt(donacionDetalle.fecha) }}</dd>
            </div>
            <div>
              <dt class="text-xs text-slate-500">Importe</dt>
              <dd class="font-mono">{{ fmt(importeDonacion(donacionDetalle)) }}</dd>
            </div>
            <div v-if="donacionDetalle.concepto">
              <dt class="text-xs text-slate-500">Concepto</dt>
              <dd>{{ donacionDetalle.concepto?.nombre }}</dd>
            </div>
            <div v-if="donacionDetalle.modoIngreso">
              <dt class="text-xs text-slate-500">Modo de ingreso</dt>
              <dd>{{ donacionDetalle.modoIngreso }}</dd>
            </div>
            <div v-if="donacionDetalle.referenciaPago" class="col-span-2">
              <dt class="text-xs text-slate-500">Referencia de pago</dt>
              <dd class="font-mono text-xs">{{ donacionDetalle.referenciaPago }}</dd>
            </div>
            <div v-if="donacionDetalle.tipo === 'ESPECIE' && donacionDetalle.descripcionEspecie" class="col-span-2">
              <dt class="text-xs text-slate-500">Descripción del bien</dt>
              <dd class="text-xs whitespace-pre-wrap">{{ donacionDetalle.descripcionEspecie }}</dd>
            </div>
            <div v-if="donacionDetalle.numeroCertificado" class="col-span-2">
              <dt class="text-xs text-slate-500">Certificado</dt>
              <dd class="font-mono text-green-700">
                {{ donacionDetalle.numeroCertificado }}
                <span v-if="donacionDetalle.fechaCertificado" class="text-xs text-slate-500">
                  ({{ fechaFmt(donacionDetalle.fechaCertificado) }})
                </span>
              </dd>
            </div>
            <div v-if="donacionDetalle.anonima" class="col-span-2">
              <dd class="text-xs text-amber-700 bg-amber-50 p-2 rounded">
                Donación anónima — no certificable.
              </dd>
            </div>
            <div v-if="donacionDetalle.observaciones" class="col-span-2">
              <dt class="text-xs text-slate-500">Observaciones</dt>
              <dd class="text-xs whitespace-pre-wrap">{{ donacionDetalle.observaciones }}</dd>
            </div>
          </dl>

          <!-- Form marcar cobrada -->
          <div v-if="modalCobrar" class="border-t border-slate-200 pt-3 space-y-2">
            <h4 class="font-medium text-sm text-slate-700">Marcar como cobrada</h4>
            <div v-if="donacionDetalle.tipo === 'DINERARIA'">
              <label class="label">Cuenta bancaria de destino *</label>
              <select v-model="formCobrar.cuentaBancariaId" class="input">
                <option :value="null">— Selecciona cuenta —</option>
                <option v-for="c in cuentasBancarias" :key="c.id" :value="c.id">
                  {{ c.nombre }}{{ c.iban ? ` — ${c.iban}` : '' }}
                </option>
              </select>
            </div>
            <div>
              <label class="label">Fecha cobro *</label>
              <input type="date" v-model="formCobrar.fechaCobro" class="input" />
            </div>
            <ErrorAlert v-if="formCobrar.error" :message="formCobrar.error" />
            <p class="text-xs text-slate-500">
              Se generan el apunte de tesorería y el asiento contable (Debe 572 / Haber 730).
            </p>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-slate-200 flex flex-wrap justify-end gap-2">
          <template v-if="!modalCobrar">
            <button v-if="donacionDetalle.estado?.nombre === 'REGISTRADA'"
                    @click="abrirCobrar()" class="btn-secondary text-xs">
              Marcar cobrada
            </button>
            <button v-if="donacionDetalle.estado?.nombre !== 'ANULADA'"
                    @click="anular(donacionDetalle)" :disabled="ocupado" class="btn-danger text-xs">
              Anular
            </button>
          </template>
          <template v-else>
            <button @click="modalCobrar = false" class="btn-secondary text-xs">Cancelar</button>
            <button @click="confirmarCobrada()" :disabled="ocupado" class="btn-primary text-xs">
              {{ ocupado ? 'Cobrando…' : 'Confirmar cobro' }}
            </button>
          </template>
        </div>
      </div>
    </div>

    <!-- ────────────────────────────────────────────────────────────────────── -->
    <!-- Modal: emitir certificados anuales                                     -->
    <!-- ────────────────────────────────────────────────────────────────────── -->
    <div v-if="modalCertificados" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
         @click.self="modalCertificados = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-2xl flex flex-col max-h-[90vh]">
        <div class="px-6 py-4 border-b border-slate-200">
          <h3 class="font-semibold text-slate-800">Emitir certificados anuales</h3>
          <p class="text-xs text-slate-500 mt-0.5">
            Donantes con donaciones COBRADAS del ejercicio agrupadas por clave (A·Dineraria / B·Especie).
          </p>
        </div>
        <div class="px-6 py-4 border-b border-slate-200 bg-slate-50 flex items-center gap-3">
          <label class="text-xs text-slate-700">Ejercicio:</label>
          <input type="number" v-model.number="ejercicioCert" :min="2000" :max="2099"
                 class="input !w-28" @change="cargarCertificables()" />
          <button @click="cargarCertificables()" class="btn-secondary text-xs">Recalcular</button>
        </div>
        <div class="px-6 py-3 overflow-y-auto flex-1">
          <p v-if="cargandoCertificables" class="text-center text-slate-400 text-sm py-4">Calculando…</p>
          <p v-else-if="!certificables.length" class="text-center text-slate-400 text-sm py-4">
            No hay donaciones COBRADAS con NIF en {{ ejercicioCert }}.
          </p>
          <table v-else class="w-full text-sm">
            <thead class="bg-slate-50 text-slate-600 text-xs uppercase">
              <tr>
                <th class="px-2 py-1 text-left">Donante</th>
                <th class="px-2 py-1 text-center">Clave</th>
                <th class="px-2 py-1 text-right">Donaciones</th>
                <th class="px-2 py-1 text-right">Total</th>
                <th class="px-2 py-1 text-center">Estado</th>
                <th class="px-2 py-1 text-center"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="c in certificables" :key="c.nif + c.tipo">
                <td class="px-2 py-1.5">
                  <div class="text-sm">{{ c.nombre || '—' }}</div>
                  <div class="text-[10px] font-mono text-slate-500">{{ c.nif }}</div>
                </td>
                <td class="px-2 py-1.5 text-center">
                  <span :class="badgeTipo(c.tipo)" class="text-[10px] uppercase rounded-full px-2 py-0.5">
                    {{ c.tipo === 'ESPECIE' ? 'B' : 'A' }}
                  </span>
                </td>
                <td class="px-2 py-1.5 text-right text-xs">{{ c.nDonaciones }}</td>
                <td class="px-2 py-1.5 text-right font-mono text-sm">{{ fmt(c.total) }}</td>
                <td class="px-2 py-1.5 text-center">
                  <span v-if="c.todasCertificadas" class="text-[10px] text-green-700">Ya certificadas</span>
                  <span v-else class="text-[10px] text-amber-700">Pendiente</span>
                </td>
                <td class="px-2 py-1.5 text-center">
                  <button @click="emitirCert(c)" :disabled="ocupado" class="btn-secondary text-[10px] !py-1 !px-2">
                    {{ c.todasCertificadas ? 'Re-emitir' : 'Emitir PDF' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="px-6 py-4 border-t border-slate-200 flex justify-end gap-2">
          <button @click="modalCertificados = false" class="btn-secondary text-sm">Cerrar</button>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { useToast } from '@/composables/useToast'
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import { useGraphQL } from '@/composables/useGraphQL'
import {
const toast = useToast()
  GET_DONACIONES,
  GET_DONACION_CONCEPTOS,
  REGISTRAR_DONACION,
  MARCAR_DONACION_COBRADA,
  ANULAR_DONACION,
  LISTAR_DONACIONES_CERTIFICABLES,
  EMITIR_CERTIFICADO_DONACION_ANUAL,
  GET_CUENTAS_BANCARIAS_ACTIVAS,
  GET_MIEMBROS_PARA_GASTO,
} from '@/graphql/queries/financiero'

const { query, mutation, loading } = useGraphQL()

const donaciones = ref([])
const conceptos = ref([])
const cuentasBancarias = ref([])
const miembros = ref([])
const error = ref('')
const ocupado = ref(false)

// Detalle
const donacionDetalle = ref(null)
const modalCobrar = ref(false)
const formCobrar = ref({ cuentaBancariaId: null, fechaCobro: '', error: '' })

// Alta
const modalAlta = ref(false)
const formAlta = ref(_emptyAlta())

// Certificados
const modalCertificados = ref(false)
const certificables = ref([])
const cargandoCertificables = ref(false)
const ejercicioCert = ref(new Date().getFullYear())

// Filtros
const busqueda = ref('')
const filtros = ref({ ejercicio: null, tipo: [], estado: [], certificado: null })

function _emptyAlta() {
  return {
    tipo: 'DINERARIA',
    caracter: 'PUNTUAL',
    donanteTipo: 'EXTERNO',
    miembroId: null,
    donanteNombre: '',
    donanteDni: '',
    donanteEmail: '',
    donanteTelefono: '',
    importe: null,
    valoracion: null,
    fechaDonacion: new Date().toISOString().split('T')[0],
    modoIngreso: null,
    referenciaPago: '',
    conceptoId: null,
    descripcionEspecie: '',
    documentoValoracion: '',
    anonima: false,
    observaciones: '',
    cobrarInmediato: true,
    cuentaBancariaId: null,
    error: '',
  }
}

const camposFiltro = computed(() => [
  {
    key: 'ejercicio', label: 'Ejercicio', type: 'select',
    options: anosDisponibles.value.map(y => ({ value: y, label: String(y) })),
    allLabel: 'Todos los ejercicios',
  },
  {
    key: 'tipo', label: 'Tipo', type: 'multiselect',
    options: [
      { value: 'DINERARIA', label: 'A · Dineraria' },
      { value: 'ESPECIE',   label: 'B · En especie' },
    ],
    allLabel: 'Ambos tipos',
  },
  {
    key: 'estado', label: 'Estado', type: 'multiselect',
    options: [
      { value: 'REGISTRADA', label: 'Registrada' },
      { value: 'COBRADA',    label: 'Cobrada' },
      { value: 'ANULADA',    label: 'Anulada' },
    ],
    allLabel: 'Todos los estados',
  },
  {
    key: 'certificado', label: 'Certificado', type: 'select',
    options: [
      { value: 'SI', label: 'Certificadas' },
      { value: 'NO', label: 'Sin certificar' },
    ],
    allLabel: 'Indiferente',
  },
])

const descripcionFiltros = computed(() => {
  const parts = []
  if (filtros.value.ejercicio) parts.push(`ejercicio ${filtros.value.ejercicio}`)
  if (filtros.value.tipo?.length) parts.push(`${filtros.value.tipo.length} tipo(s)`)
  if (filtros.value.estado?.length) parts.push(`${filtros.value.estado.length} estado(s)`)
  return parts.join(' · ')
})

const anosDisponibles = computed(() =>
  [...new Set(donaciones.value.map(d => d.fecha?.substring(0, 4)).filter(Boolean))]
    .map(Number).sort((a, b) => b - a)
)

const donacionesFiltradas = computed(() => {
  const q = (busqueda.value || '').toLowerCase().trim()
  return donaciones.value.filter(d => {
    if (filtros.value.ejercicio && !d.fecha?.startsWith(String(filtros.value.ejercicio))) return false
    if (filtros.value.tipo?.length && !filtros.value.tipo.includes(d.tipo)) return false
    if (filtros.value.estado?.length && !filtros.value.estado.includes(d.estado?.nombre)) return false
    if (filtros.value.certificado === 'SI' && !d.certificadoEmitido) return false
    if (filtros.value.certificado === 'NO' && d.certificadoEmitido) return false
    if (q) {
      const nombre = donanteNombre(d).toLowerCase()
      const dni = (d.donanteDni || '').toLowerCase()
      const cert = (d.numeroCertificado || '').toLowerCase()
      if (!nombre.includes(q) && !dni.includes(q) && !cert.includes(q)) return false
    }
    return true
  })
})

const totalRecibidoFiltrado = computed(() =>
  donacionesFiltradas.value
    .filter(d => d.estado?.nombre === 'COBRADA')
    .reduce((s, d) => s + Number(importeDonacion(d) || 0), 0)
)

const contarEstado = (e) => donaciones.value.filter(d => d.estado?.nombre === e).length
const contarCertificadas = () => donaciones.value.filter(d => d.certificadoEmitido).length
const contarSinCertificar = () =>
  donaciones.value.filter(d => d.estado?.nombre === 'COBRADA' && !d.anonima && !d.certificadoEmitido).length

// ── Carga ──────────────────────────────────────────────────────────────────
const cargar = async () => {
  error.value = ''
  try {
    const data = await query(GET_DONACIONES)
    donaciones.value = (data.donaciones || []).slice().sort((a, b) =>
      (b.fecha || '').localeCompare(a.fecha || '')
    )
  } catch (e) {
    error.value = 'Error al cargar las donaciones'
    console.error(e)
  }
}

const cargarAuxiliares = async () => {
  try {
    const [c, b, m] = await Promise.all([
      query(GET_DONACION_CONCEPTOS),
      query(GET_CUENTAS_BANCARIAS_ACTIVAS),
      query(GET_MIEMBROS_PARA_GASTO),
    ])
    conceptos.value = (c.donacionConceptos || []).filter(x => x.activo)
    cuentasBancarias.value = (b.cuentasBancarias || []).filter(c => c.activa)
    miembros.value = m.miembros || []
  } catch (e) {
    console.error('Error cargando auxiliares:', e)
  }
}

// ── Alta ───────────────────────────────────────────────────────────────────
const abrirModalAlta = () => {
  formAlta.value = _emptyAlta()
  if (cuentasBancarias.value.length === 1) {
    formAlta.value.cuentaBancariaId = cuentasBancarias.value[0].id
  }
  modalAlta.value = true
}

const guardarAlta = async () => {
  formAlta.value.error = ''
  const f = formAlta.value
  // Validaciones cliente
  if (f.tipo === 'DINERARIA' && (!f.importe || f.importe <= 0)) {
    f.error = 'Introduce un importe positivo.'; return
  }
  if (f.tipo === 'ESPECIE') {
    if (!f.valoracion || f.valoracion <= 0) { f.error = 'Introduce la valoración del bien.'; return }
    if (!f.descripcionEspecie?.trim()) { f.error = 'Describe el bien donado.'; return }
  }
  if (!f.anonima && f.donanteTipo === 'MIEMBRO' && !f.miembroId) {
    f.error = 'Selecciona el socio donante.'; return
  }
  if (!f.anonima && f.donanteTipo === 'EXTERNO' && !f.donanteNombre?.trim()) {
    f.error = 'Indica el nombre del donante.'; return
  }
  if (f.cobrarInmediato && f.tipo === 'DINERARIA' && !f.cuentaBancariaId) {
    f.error = 'Indica la cuenta bancaria de destino para cobrar la donación dineraria.'; return
  }

  ocupado.value = true
  try {
    await mutation(REGISTRAR_DONACION, {
      importe: Number(f.tipo === 'DINERARIA' ? f.importe : (f.valoracion || 0)),
      fechaDonacion: f.fechaDonacion,
      tipo: f.tipo,
      caracter: f.caracter,
      miembroId: f.donanteTipo === 'MIEMBRO' && !f.anonima ? f.miembroId : null,
      donanteNombre: f.donanteTipo === 'EXTERNO' && !f.anonima ? f.donanteNombre || null : null,
      donanteDni: f.donanteTipo === 'EXTERNO' && !f.anonima ? f.donanteDni || null : null,
      donanteEmail: f.donanteTipo === 'EXTERNO' && !f.anonima ? f.donanteEmail || null : null,
      donanteTelefono: f.donanteTipo === 'EXTERNO' && !f.anonima ? f.donanteTelefono || null : null,
      conceptoId: f.conceptoId || null,
      modoIngreso: f.tipo === 'DINERARIA' ? (f.modoIngreso || null) : null,
      referenciaPago: f.tipo === 'DINERARIA' ? (f.referenciaPago || null) : null,
      descripcionEspecie: f.tipo === 'ESPECIE' ? f.descripcionEspecie : null,
      valoracion: f.tipo === 'ESPECIE' ? Number(f.valoracion) : null,
      documentoValoracion: f.tipo === 'ESPECIE' ? (f.documentoValoracion || null) : null,
      anonima: !!f.anonima,
      observaciones: f.observaciones || null,
      cobrarInmediato: !!f.cobrarInmediato,
      cuentaBancariaId: f.cobrarInmediato && f.tipo === 'DINERARIA' ? f.cuentaBancariaId : null,
    })
    modalAlta.value = false
    await cargar()
  } catch (e) {
    f.error = e.message || 'Error al registrar la donación'
  } finally { ocupado.value = false }
}

// ── Detalle / cobro / anulación ────────────────────────────────────────────
const abrirDetalle = (d) => {
  donacionDetalle.value = d
  modalCobrar.value = false
}

const abrirCobrar = () => {
  formCobrar.value = {
    cuentaBancariaId: donacionDetalle.value.tipo === 'DINERARIA' && cuentasBancarias.value.length === 1
      ? cuentasBancarias.value[0].id : null,
    fechaCobro: new Date().toISOString().split('T')[0],
    error: '',
  }
  modalCobrar.value = true
}

const confirmarCobrada = async () => {
  formCobrar.value.error = ''
  if (donacionDetalle.value.tipo === 'DINERARIA' && !formCobrar.value.cuentaBancariaId) {
    formCobrar.value.error = 'Selecciona la cuenta bancaria'; return
  }
  if (!formCobrar.value.fechaCobro) {
    formCobrar.value.error = 'Indica la fecha de cobro'; return
  }
  ocupado.value = true
  try {
    await mutation(MARCAR_DONACION_COBRADA, {
      donacionId: donacionDetalle.value.id,
      cuentaBancariaId: formCobrar.value.cuentaBancariaId,
      fechaCobro: formCobrar.value.fechaCobro,
    })
    modalCobrar.value = false
    donacionDetalle.value = null
    await cargar()
  } catch (e) {
    formCobrar.value.error = e.message || 'Error al registrar el cobro'
  } finally { ocupado.value = false }
}

const anular = async (d) => {
  const motivo = prompt(`¿Anular la donación de ${donanteNombre(d) || 'donante'}? Indica el motivo (opcional):`)
  if (motivo === null) return
  ocupado.value = true
  try {
    await mutation(ANULAR_DONACION, { donacionId: d.id, motivo: motivo || null })
    donacionDetalle.value = null
    await cargar()
  } catch (e) {
    error.value = e.message || 'Error al anular'
  } finally { ocupado.value = false }
}

// ── Certificados anuales ──────────────────────────────────────────────────
const abrirModalCertificados = async () => {
  modalCertificados.value = true
  await cargarCertificables()
}

const cargarCertificables = async () => {
  cargandoCertificables.value = true
  try {
    const data = await mutation(LISTAR_DONACIONES_CERTIFICABLES, { ejercicio: ejercicioCert.value })
    certificables.value = data.listarDonacionesCertificables || []
  } catch (e) {
    console.error(e)
    certificables.value = []
  } finally { cargandoCertificables.value = false }
}

const emitirCert = async (c) => {
  ocupado.value = true
  try {
    const data = await mutation(EMITIR_CERTIFICADO_DONACION_ANUAL, {
      ejercicio: ejercicioCert.value,
      nifDonante: c.nif,
      tipo: c.tipo,
    })
    const { numero, pdfBase64 } = data.emitirCertificadoDonacionAnual
    // Descargar PDF
    const bin = atob(pdfBase64)
    const buf = new Uint8Array(bin.length)
    for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i)
    const blob = new Blob([buf], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${numero}.pdf`
    a.click()
    URL.revokeObjectURL(url)
    await Promise.all([cargar(), cargarCertificables()])
  } catch (e) {
    toast.error(e.message || 'Error al emitir el certificado')
  } finally { ocupado.value = false }
}

// ── Helpers ────────────────────────────────────────────────────────────────
const donanteNombre = (d) => {
  if (d.anonima) return 'Anónima'
  return d.donanteNombre || '—'
}
const importeDonacion = (d) => d.tipo === 'ESPECIE' ? (d.valoracion ?? 0) : (d.importe ?? 0)
const socioFullName = (m) => `${m.nombre || ''} ${m.apellido1 || ''} ${m.apellido2 || ''}`.trim()
const fmt = (v) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(v ?? 0)
const fechaFmt = (d) => d ? new Intl.DateTimeFormat('es-ES').format(new Date(d + 'T12:00:00')) : '—'

const badgeEstado = (e) => ({
  REGISTRADA: 'bg-amber-100 text-amber-700',
  COBRADA: 'bg-green-100 text-green-700',
  ANULADA: 'bg-slate-100 text-slate-500',
}[e] || 'bg-slate-100 text-slate-500')

const badgeTipo = (t) => ({
  DINERARIA: 'bg-indigo-100 text-indigo-700',
  ESPECIE: 'bg-sky-100 text-sky-700',
}[t] || 'bg-slate-100 text-slate-500')

onMounted(async () => {
  await Promise.all([cargar(), cargarAuxiliares()])
})
</script>

<style scoped>
.btn-primary   { @apply px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed; }
.btn-secondary { @apply px-3 py-1.5 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 text-sm font-medium disabled:opacity-50; }
.btn-danger    { @apply px-3 py-1.5 bg-white border border-red-300 text-red-600 rounded-lg hover:bg-red-50 text-sm font-medium disabled:opacity-50; }
.label         { @apply block text-xs font-medium text-slate-700 mb-1; }
.input         { @apply w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent; }
</style>
