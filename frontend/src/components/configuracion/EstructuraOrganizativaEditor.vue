<template>
  <div>
    <ErrorAlert v-if="errorMsg" :message="errorMsg" class="mb-3" />

    <!-- Mutabilidad: estructura en uso ⇒ read-only hasta desbloquear -->
    <div v-if="estructuraProtegida && !desbloqueado"
      class="mb-4 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2.5 flex items-start gap-3">
      <span class="text-amber-600 text-lg leading-none flex-shrink-0">🔒</span>
      <div class="min-w-0 flex-1">
        <p class="text-sm font-medium text-amber-800">Estructura en uso</p>
        <p class="text-xs text-amber-700 leading-snug mt-0.5">
          Hay {{ nUnidadesUso }} unidad{{ nUnidadesUso === 1 ? '' : 'es' }}<template v-if="nSociosUso"> y {{ nSociosUso }} {{ orgConfig.miembros }}</template> creadas.
          Cambiar los niveles puede reorganizar datos: al borrar un nivel, sus unidades pasan al nivel padre.
        </p>
      </div>
      <button type="button" @click="desbloqueado = true"
        class="flex-shrink-0 text-xs font-medium px-3 py-1.5 rounded-lg border border-amber-300 text-amber-800 hover:bg-amber-100">
        Modificar estructura
      </button>
    </div>
    <div v-else-if="estructuraProtegida && desbloqueado"
      class="mb-3 flex items-center gap-2 text-xs text-amber-700">
      <span>✏️ Editando una estructura en uso — las operaciones con impacto piden confirmación.</span>
      <button type="button" @click="desbloqueado = false" class="text-amber-800 underline hover:text-amber-900">Bloquear</button>
    </div>

    <!-- Modelo de estructura (solo en uso embebido; en Parámetros lo pinta el padre arriba) -->
    <fieldset v-if="mostrarRadiogroup && nodoRaizActual" class="rounded-xl border border-slate-200 bg-white px-3 pt-1.5 pb-3 mb-4">
      <legend class="px-1.5 text-[11px] font-medium text-slate-500">
        Modelo de estructura de «{{ nodoRaizActual.nombre }}»
      </legend>
      <div class="flex flex-col sm:flex-row gap-2.5 mt-1">
        <label class="flex-1 flex items-start gap-2.5 rounded-lg border p-3 cursor-pointer transition-colors"
          :class="!distribuida ? 'border-indigo-400 bg-indigo-50/60 ring-1 ring-indigo-200' : 'border-slate-200 hover:bg-slate-50'">
          <input type="radio" class="mt-0.5 accent-indigo-600" :checked="!distribuida" :disabled="guardando || !editable" @change="setDistribuida(false)" />
          <span class="min-w-0">
            <span class="block text-sm font-medium text-slate-800">Centralizada</span>
            <span class="block text-xs text-slate-500 leading-snug mt-0.5">La estructura interna se define aquí, igual para todas las unidades.</span>
          </span>
        </label>
        <label class="flex-1 flex items-start gap-2.5 rounded-lg border p-3 cursor-pointer transition-colors"
          :class="distribuida ? 'border-indigo-400 bg-indigo-50/60 ring-1 ring-indigo-200' : 'border-slate-200 hover:bg-slate-50'">
          <input type="radio" class="mt-0.5 accent-indigo-600" :checked="distribuida" :disabled="guardando || !editable" @change="setDistribuida(true)" />
          <span class="min-w-0">
            <span class="block text-sm font-medium text-slate-800">Distribuida</span>
            <span class="block text-xs text-slate-500 leading-snug mt-0.5">El responsable de cada unidad define la subestructura de su propio ámbito, desde la ficha de su agrupación.</span>
          </span>
        </label>
      </div>
    </fieldset>

    <!-- ══ CASCADA RECURSIVA DE TARJETAS TERRITORIALES ══════════════════════
         Cada tarjeta ES un nivel: sus datos, SUS ACCIONES y su modelo
         organizativo dentro; y se repinta a sí misma para sus hijos. -->
    <div class="ladder">
      <p v-if="!raices.length" class="text-sm text-slate-400 italic py-6">
        Aún no hay niveles definidos.
      </p>

      <NivelCard v-for="r in raices" :key="r.id" :nivel="r" :depth="0" />

      <!-- Fuera de toda tarjeta: no pertenece a ningún nivel -->
      <button type="button" class="addroot"
        :disabled="!editable || guardando || (scoped && !nodoScope)"
        @click="scoped ? añadirHijo(nodoScope) : añadirRaiz()">
        <PlusIcon class="w-3.5 h-3.5" />
        {{ scoped ? 'Añadir subnivel' : 'Añadir nivel raíz' }}
      </button>
    </div>
  </div>

  <!-- Drawer: añadir órgano al modelo del nivel -->
  <AppDrawer v-model="drawerOrgano" title="Añadir órgano al nivel" size="md">
    <div class="space-y-4">
      <p class="text-sm text-slate-500">
        Se añadirá al <strong class="text-slate-700">modelo</strong> del nivel
        <strong class="text-slate-700">{{ nivelOrganoNuevo?.nombre }}</strong>.
        Después definirás de qué cargos se compone.
      </p>
      <div>
        <label class="block text-xs font-medium text-slate-600 mb-1">
          Tipo de órgano <span class="text-red-400">*</span>
        </label>
        <AppSelect v-model="tipoOrganoNuevoId" :options="opcionesTipos" placeholder="Selecciona un tipo…" />
        <p class="mt-1 text-[11px] text-slate-400">Solo aparecen los tipos que este nivel aún no tiene.</p>
      </div>
      <p v-if="errorOrgano" class="text-xs text-red-600">{{ errorOrgano }}</p>
    </div>
    <template #footer>
      <button type="button" @click="drawerOrgano = false"
        class="px-4 py-1.5 text-sm border border-slate-300 rounded-md text-slate-700 hover:bg-slate-50 transition-colors">
        Cancelar
      </button>
      <button type="button" :disabled="guardandoOrganos || !tipoOrganoNuevoId" @click="anadirOrgano"
        class="px-4 py-1.5 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors">
        {{ guardandoOrganos ? 'Añadiendo…' : 'Añadir órgano' }}
      </button>
    </template>
  </AppDrawer>

  <!-- Modal confirmación de borrado -->
  <Teleport to="body">
    <div v-if="pendingDelete" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-5 max-w-sm w-full mx-4">
        <h3 class="font-semibold text-gray-900 mb-3">Eliminar nivel «{{ pendingDelete.nombre }}»</h3>
        <p v-if="pendingDelete.nHijos > 0 || pendingDelete.nUnidades > 0"
          class="text-sm text-amber-800 bg-amber-50 border border-amber-200 rounded p-3 mb-4">
          <strong>Atención:</strong> este nivel tiene
          <template v-if="pendingDelete.nHijos > 0">
            {{ pendingDelete.nHijos }} subnivel{{ pendingDelete.nHijos > 1 ? 'es' : '' }}
          </template>
          <template v-if="pendingDelete.nHijos > 0 && pendingDelete.nUnidades > 0"> y </template>
          <template v-if="pendingDelete.nUnidades > 0">
            {{ pendingDelete.nUnidades }} órgano{{ pendingDelete.nUnidades > 1 ? 's' : '' }} asignado{{ pendingDelete.nUnidades > 1 ? 's' : '' }}
          </template>.
          Se reasignarán al nivel padre antes de eliminar.
        </p>
        <p v-else class="text-sm text-gray-500 mb-4">Esta acción no se puede deshacer.</p>
        <p class="text-xs text-slate-500 mb-4">
          También se borrará el <strong>modelo organizativo</strong> del nivel (sus órganos y su composición).
        </p>
        <div class="flex justify-end gap-2">
          <button type="button" @click="pendingDelete = null"
            class="text-sm px-3 py-1.5 border border-gray-200 rounded hover:bg-gray-50">Cancelar</button>
          <button type="button" @click="confirmarEliminar" :disabled="guardando"
            class="text-sm px-3 py-1.5 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-40">
            {{ pendingDelete.nHijos > 0 || pendingDelete.nUnidades > 0 ? 'Reasignar y eliminar' : 'Eliminar' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>

</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import AppDrawer from '@/components/common/AppDrawer.vue'
import AppSelect from '@/components/common/AppSelect.vue'
import NivelCard from '@/components/configuracion/NivelCard.vue'
import { PlusIcon } from '@heroicons/vue/24/outline'
import { ref, computed, onMounted, provide } from 'vue'
import { graphqlClient } from '@/graphql/client.js'
import { useUnidadesOrganizativas } from '@/composables/useUnidadesOrganizativas'
import { useOrgConfigStore } from '@/stores/orgConfig'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { GET_AMBITOS_GEOGRAFICOS } from '@/graphql/queries/catalogos.js'
import * as OQ from '@/graphql/queries/organos.js'

const props = defineProps({
  // Ancla opcional. Si se indica, el editor solo muestra/edita el subárbol que
  // cuelga de este nivel; reutilizable en la edición de cada agrupación, que
  // arranca en su propio nivel geográfico. Sin prop = árbol completo (matriz).
  nivelRaizId: { type: String, default: null },
  // Si es false, el editor no pinta su radiogroup centralizada/distribuida
  // (lo pinta el contenedor, p.ej. Parámetros Generales lo coloca arriba).
  mostrarRadiogroup: { type: Boolean, default: true },
  // Cuando se edita la subestructura de una agrupación (estructura distribuida),
  // su id: los niveles creados le pertenecen (unidad_id) y el editor solo muestra
  // las plantillas globales (unidad_id NULL) + los niveles propios de esa unidad.
  unidadId: { type: String, default: null },
})

const { tipos, unidades, miembros, cargarTipos, cargarArbol, crearTipo, actualizarTipo, actualizarUnidad, eliminarTipo } = useUnidadesOrganizativas()
const orgConfig = useOrgConfigStore()
const toast = useToast()
const confirm = useConfirm()

const mensajeError = (e, porDefecto) =>
  e?.response?.errors?.[0]?.message ?? e?.message ?? porDefecto

async function recargarConfig() {
  orgConfig.invalidate()
  await orgConfig.fetchConfig()
}

// Nivel que debe abrirse en modo edición in situ (p.ej. uno recién creado, para
// nombrarlo enseguida). La tarjeta lo consume y lo suelta.
const nivelAEditar  = ref(null)
const guardando     = ref(false)
const errorMsg      = ref('')
const pendingDelete = ref(null)

const ambitos = ref([])
const ambitosOrdenados = computed(() =>
  [...ambitos.value].sort((a, b) => a.granularidad - b.granularidad)
)

async function cargarAmbitos() {
  try {
    const data = await graphqlClient.request(GET_AMBITOS_GEOGRAFICOS)
    ambitos.value = data.ambitosGeograficos ?? []
  } catch { /* no bloquea */ }
}

const tiposTerritoriales = computed(() =>
  tipos.value.filter(t => t.naturaleza === 'TERRITORIAL' &&
    // plantillas globales (unidad_id NULL) + niveles propios de esta unidad (si scoped)
    (t.unidadId == null || t.unidadId === props.unidadId))
)

const buildTree = (lista) => {
  const map = {}
  const raices = []
  lista.forEach(t => { map[t.id] = { ...t, hijos: [] } })
  lista.forEach(t => {
    if (t.padreTipoId && map[t.padreTipoId]) {
      map[t.padreTipoId].hijos.push(map[t.id])
    } else {
      raices.push(map[t.id])
    }
  })
  return raices
}

const raicesReales = computed(() => buildTree(tiposTerritoriales.value))

const buscarNodo = (nodos, id) => {
  for (const n of nodos) {
    if (n.id === id) return n
    const f = buscarNodo(n.hijos || [], id)
    if (f) return f
  }
  return null
}

// Nodo ancla del scope (si se indicó nivelRaizId)
const nodoScope = computed(() =>
  props.nivelRaizId ? buscarNodo(raicesReales.value, props.nivelRaizId) : null
)

// Raíces efectivas: con scope, solo el nodo ancla; sin scope, las raíces reales
const raices = computed(() =>
  nodoScope.value ? [nodoScope.value] : raicesReales.value
)

const scoped = computed(() => !!props.nivelRaizId)

// Nodo cuya bandera centralizada/distribuida gobierna este editor (recursivo:
// cada nivel decide cómo se organiza el subárbol que cuelga de él)
const nodoRaizActual = computed(() =>
  nodoScope.value ?? (raicesReales.value.length ? raicesReales.value[0] : null)
)
const distribuida = computed(() => !!nodoRaizActual.value?.estructuraDistribuida)
// En distribuida NO se anidan subniveles en el editor global (Parámetros): se
// delegan a cada agrupación. Pero en el editor de una agrupación (scoped) SÍ se
// añaden — es precisamente donde la unidad define su propia subestructura.
const permiteSubniveles = computed(() => scoped.value || !distribuida.value)

// ── Recorridos del árbol (sin aplanarlo: la recursión ES la jerarquía) ───────
/** Todos los descendientes de un nodo, de más profundo a más superficial. */
const descendientes = (nodo, depth = 0, out = []) => {
  for (const h of nodo.hijos ?? []) {
    out.push({ nodo: h, depth: depth + 1 })
    descendientes(h, depth + 1, out)
  }
  return out
}

/** Recorre todos los nodos del subárbol visible (raíces + descendientes). */
const recorrer = (fn) => {
  const visita = (n, depth) => {
    fn(n, depth)
    ;(n.hijos ?? []).forEach(h => visita(h, depth + 1))
  }
  raices.value.forEach(r => visita(r, 0))
}

// Niveles que se borrarían al pasar a distribuida (de segundo nivel hacia abajo)

const setDistribuida = async (val) => {
  const nodo = nodoRaizActual.value
  if (!nodo || guardando.value || distribuida.value === val) return
  // Distribuir NO destruye nada: solo delega la competencia sobre la subestructura.
  // Los niveles existentes se conservan; cambia QUIÉN los edita (ver aplicarDistribuida).
  await aplicarDistribuida(val)
}

// Cambia el modelo de estructura. DISTRIBUIDA **no destruye nada**: es una
// delegación de competencia. La subestructura por debajo de este nivel deja de
// definirla la matriz central y pasa a definirla el responsable de cada unidad,
// desde la ficha de su agrupación (editor acotado con `unidadId`), sobre su
// propio subárbol. El backend ya lo respalda: los niveles con `unidad_id` solo
// los toca quien tiene esa unidad en su ámbito (assert_unidad_en_ambito), y los
// de `unidad_id = NULL` son la plantilla global. Reversible.
const aplicarDistribuida = async (val) => {
  const nodo = nodoRaizActual.value
  if (!nodo) return
  guardando.value = true
  errorMsg.value  = ''
  try {
    await actualizarTipo({ id: nodo.id, estructuraDistribuida: val })
    await recargarConfig()
    await cargarOrganosDeTodos()
  } catch (e) {
    errorMsg.value = mensajeError(e, 'Error al cambiar el modelo de estructura')
  } finally {
    guardando.value = false
  }
}

// ── Guardas de límite del scope ───────────────────────────────────────────────
// (la profundidad la aporta la tarjeta: ella sabe a qué altura se pinta)
const esAncla       = (item) => scoped.value && item.id === props.nivelRaizId
const puedeSubir    = (item, depth) => depth > 0 && !(scoped.value && item.padreTipoId === props.nivelRaizId)
const puedeSuperior = (item) => !esAncla(item)
const puedeEliminar = (item, depth) => !esAncla(item) && (depth > 0 || raices.value.length > 1)
const puedeHermano  = (item) => !esAncla(item)

/** Hermano inmediatamente anterior (mismo padre) — objetivo del "anidar". */
const hermanoAnterior = (nodo) => {
  const hermanos = nodo.padreTipoId
    ? (buscarNodo(raices.value, nodo.padreTipoId)?.hijos ?? [])
    : raices.value
  const idx = hermanos.findIndex(h => h.id === nodo.id)
  return idx > 0 ? hermanos[idx - 1] : null
}

// ── Plegado de tarjetas (nivel) y de órganos ─────────────────────────────────
const abiertoNivel  = ref({})   // id nivel  → bool
const abiertoOrgano = ref({})   // id órgano → bool
const estaAbiertoNivel  = (id) => abiertoNivel.value[id] ?? true
const estaAbiertoOrgano = (id) => abiertoOrgano.value[id] ?? true

function alternarNivel(id) {
  abiertoNivel.value = { ...abiertoNivel.value, [id]: !estaAbiertoNivel(id) }
}

function alternarOrgano(id) {
  abiertoOrgano.value = { ...abiertoOrgano.value, [id]: !estaAbiertoOrgano(id) }
}

/** Despliega un órgano (al añadirle un cargo, el selector debe verse). */
function abrirOrgano(id) {
  abiertoOrgano.value = { ...abiertoOrgano.value, [id]: true }
}

// ── Datos del nivel (edición IN SITU dentro de la tarjeta) ───────────────────
// El formulario vive en NivelCard (estado local por tarjeta); el editor solo
// aporta la mutación, el catálogo de ámbitos y el refresco del árbol.

// Marca un nivel recién creado para que su tarjeta abra el formulario sola.
const seleccionarYEditar = (nuevo) => {
  if (!nuevo) return
  nivelAEditar.value = nuevo.id
}

/** Guarda los datos del nivel. Devuelve true si se guardó (la tarjeta cierra su form). */
const guardarNivel = async (nivel, datos) => {
  if (!nivel?.id || !datos?.nombre?.trim()) return false
  guardando.value = true
  errorMsg.value  = ''
  try {
    await actualizarTipo({
      id: nivel.id,
      nombre: datos.nombre.trim(),
      ambitoGeograficoId: datos.ambitoGeograficoId || null,
      denominacionSingular: datos.denominacionSingular?.trim() || null,
      denominacionPlural: datos.denominacionPlural?.trim() || null,
    })
    await recargarConfig()
    toast.success('Nivel guardado')
    return true
  } catch (e) {
    errorMsg.value = mensajeError(e, 'Error al guardar el nivel')
    return false
  } finally {
    guardando.value = false
  }
}

// Sube el nodo un nivel (pasa a ser hermano de su padre)
const promover = async (nodo) => {
  if (!nodo.padreTipoId) return
  guardando.value = true
  errorMsg.value  = ''
  try {
    const parent = tipos.value.find(t => t.id === nodo.padreTipoId)
    await actualizarTipo({ id: nodo.id, padreTipoId: parent?.padreTipoId || null })
    await recargarConfig()
  } catch (e) {
    errorMsg.value = mensajeError(e, 'Error al subir nivel')
  } finally {
    guardando.value = false
  }
}

// Baja el nodo un nivel (pasa a ser hijo del hermano anterior)
const demover = async (nodo) => {
  const prev = hermanoAnterior(nodo)
  if (!prev) return
  guardando.value = true
  errorMsg.value  = ''
  try {
    await actualizarTipo({ id: nodo.id, padreTipoId: prev.id })
    await recargarConfig()
  } catch (e) {
    errorMsg.value = mensajeError(e, 'Error al bajar nivel')
  } finally {
    guardando.value = false
  }
}

// Inserta un nuevo nivel ENTRE el nodo y su padre (splice hacia arriba)
const añadirSuperior = async (nodo) => {
  guardando.value = true
  errorMsg.value  = ''
  try {
    const nuevo = await crearTipo({
      nombre: 'Nuevo nivel',
      naturaleza: 'TERRITORIAL',
      vinculo: nodo.vinculo ?? 'INTERNA',
      padreTipoId: nodo.padreTipoId || null,
      activo: true,
      unidadId: props.unidadId,
    })
    await actualizarTipo({ id: nodo.id, padreTipoId: nuevo.id })
    await recargarConfig()
    await cargarOrganosDeNivel(nuevo.id)
    seleccionarYEditar(nuevo)
  } catch (e) {
    errorMsg.value = mensajeError(e, 'Error al insertar nivel superior')
  } finally {
    guardando.value = false
  }
}

// Añade un nivel inferior (hijo directo). Tras crearlo se ofrece heredar el
// modelo organizativo del padre: lo normal es que un subnivel replique los
// órganos del nivel del que cuelga, y luego se ajuste.
const añadirHijo = async (padre) => {
  guardando.value = true
  errorMsg.value  = ''
  let nuevo = null
  try {
    nuevo = await crearTipo({
      nombre: 'Nuevo subnivel',
      naturaleza: 'TERRITORIAL',
      vinculo: 'INTERNA',
      padreTipoId: padre.id,
      activo: true,
      unidadId: props.unidadId,
    })
    await recargarConfig()
    await cargarOrganosDeNivel(nuevo.id)
    seleccionarYEditar(nuevo)
  } catch (e) {
    errorMsg.value = mensajeError(e, 'Error al crear subnivel')
  } finally {
    guardando.value = false
  }
  if (nuevo) await ofrecerHerencia(padre, nuevo)
}

// Añade un nivel al mismo nivel que el dado (mismo padre = hermano)
const añadirHermano = async (nodo) => {
  guardando.value = true
  errorMsg.value  = ''
  try {
    const nuevo = await crearTipo({
      nombre: 'Nuevo nivel',
      naturaleza: 'TERRITORIAL',
      vinculo: nodo.vinculo ?? 'INTERNA',
      padreTipoId: nodo.padreTipoId || null,
      activo: true,
      unidadId: props.unidadId,
    })
    await recargarConfig()
    await cargarOrganosDeNivel(nuevo.id)
    seleccionarYEditar(nuevo)
  } catch (e) {
    errorMsg.value = mensajeError(e, 'Error al crear nivel')
  } finally {
    guardando.value = false
  }
}

// Añade un nivel raíz (sin padre)
const añadirRaiz = async () => {
  guardando.value = true
  errorMsg.value  = ''
  try {
    const nuevo = await crearTipo({
      nombre: 'Nuevo nivel',
      naturaleza: 'TERRITORIAL',
      vinculo: 'INTERNA',
      padreTipoId: null,
      activo: true,
      unidadId: props.unidadId,
    })
    await recargarConfig()
    await cargarOrganosDeNivel(nuevo.id)
    seleccionarYEditar(nuevo)
  } catch (e) {
    errorMsg.value = mensajeError(e, 'Error al crear nivel raíz')
  } finally {
    guardando.value = false
  }
}

const iniciarEliminar = (nodo) => {
  const nHijos    = tipos.value.filter(t => t.padreTipoId === nodo.id).length
  const nUnidades = unidades.value.filter(u => u.tipoId === nodo.id).length
  pendingDelete.value = { ...nodo, nHijos, nUnidades }
}

const confirmarEliminar = async () => {
  const nodo = pendingDelete.value
  if (!nodo) return
  guardando.value = true
  errorMsg.value  = ''
  try {
    const childTipos    = tipos.value.filter(t => t.padreTipoId === nodo.id)
    const childUnidades = unidades.value.filter(u => u.tipoId === nodo.id)
    for (const child of childTipos) {
      await actualizarTipo({ id: child.id, padreTipoId: nodo.padreTipoId || null })
    }
    for (const unit of childUnidades) {
      await actualizarUnidad({ id: unit.id, tipoId: nodo.padreTipoId || null })
    }
    await eliminarTipo(nodo.id)
    await recargarConfig()
    // El modelo organizativo del nivel se borra en cascada en BD: soltamos su
    // caché para no dejar en pantalla órganos de un nivel inexistente.
    olvidarNivel(nodo.id)
    if (nivelAEditar.value === nodo.id) nivelAEditar.value = null
    pendingDelete.value = null
    toast.success(`Nivel «${nodo.nombre}» eliminado`)
  } catch (e) {
    errorMsg.value = mensajeError(e, 'Error al eliminar')
  } finally {
    guardando.value = false
  }
}

// ═══ MODELO ORGANIZATIVO ══════════════════════════════════════════════════════
// Qué órganos tiene cada nivel y de qué cargos se compone cada uno. Es MODELO:
// las agrupaciones reales lo instancian, aquí no se habla de personas.

const cargos      = ref([])
const tiposOrgano = ref([])

const organosPorNivel  = ref({})   // id nivel → [nivelOrgano]
const cargandoNivel    = ref({})   // id nivel → bool
const guardandoOrganos = ref(false)

const drawerOrgano     = ref(false)
const nivelOrganoNuevo  = ref(null)   // nivel al que se le añade el órgano
const tipoOrganoNuevoId = ref('')
const errorOrgano       = ref('')

const esPleno = (no) => (no?.tipoOrgano?.composicion ?? 'CARGOS') === 'PLENO'
const rangoDe = (i) => Math.min(i + 1, 4)

const nombreCargo = (id) => cargos.value.find(c => c.id === id)?.nombre ?? '—'
const maxDe = (id) => cargos.value.find(c => c.id === id)?.maxSimultaneos ?? null

const composicionOrdenada = (no) =>
  [...(no.composicion ?? [])].sort(
    (a, b) => (a.ordenProtocolario ?? 0) - (b.ordenProtocolario ?? 0))

/** Tipos de órgano que el nivel destino aún NO tiene (un órgano por tipo y nivel). */
const tiposDisponibles = computed(() => {
  const nivelId = nivelOrganoNuevo.value?.id
  const usados = new Set((organosPorNivel.value[nivelId] ?? []).map(no => no.tipoOrganoId))
  return tiposOrgano.value.filter(t => t.activo !== false && !usados.has(t.id))
})

const opcionesTipos = computed(() =>
  tiposDisponibles.value.map(t => ({
    value: t.id,
    label: `${t.nombre} — ${t.composicion === 'PLENO' ? 'pleno' : 'por cargos'}`,
  }))
)

function abrirAnadirOrgano(nivel) {
  nivelOrganoNuevo.value  = nivel
  tipoOrganoNuevoId.value = ''
  errorOrgano.value = ''
  drawerOrgano.value = true
}

/** Reemplaza el conjunto de tipos del nivel. Los que se mantienen conservan su composición. */
async function establecerTipos(nivelId, tipoOrganoIds) {
  await graphqlClient.request(OQ.ESTABLECER_ORGANOS_DE_NIVEL, { nivelId, tipoOrganoIds })
}

async function anadirOrgano() {
  const nivel = nivelOrganoNuevo.value
  if (!tipoOrganoNuevoId.value || !nivel) return
  guardandoOrganos.value = true
  errorOrgano.value = ''
  const nuevoTipoId = tipoOrganoNuevoId.value
  try {
    const actuales = (organosPorNivel.value[nivel.id] ?? []).map(no => no.tipoOrganoId)
    await establecerTipos(nivel.id, [...actuales, nuevoTipoId])
    drawerOrgano.value = false
    await cargarOrganosDeNivel(nivel.id)
    abiertoNivel.value = { ...abiertoNivel.value, [nivel.id]: true }
    const nombre = tiposOrgano.value.find(t => t.id === nuevoTipoId)?.nombre ?? 'Órgano'
    toast.success(`«${nombre}» añadido al modelo de ${nivel.nombre}`)
  } catch (e) {
    errorOrgano.value = mensajeError(e, 'Error al añadir el órgano al nivel.')
  } finally {
    guardandoOrganos.value = false
  }
}

async function quitarOrganoDelNivel(nivel, no) {
  const nombre = no.tipoOrgano?.nombre ?? 'este órgano'
  const ok = await confirm({
    titulo: `¿Quitar «${nombre}» del nivel?`,
    mensaje: `Dejará de formar parte del modelo del nivel «${nivel.nombre}» `
      + 'y se perderá la composición de cargos que le hayas definido.',
    variante: 'critica',
    etiquetaConfirmar: 'Sí, quitar',
  })
  if (!ok) return

  guardandoOrganos.value = true
  try {
    const restantes = (organosPorNivel.value[nivel.id] ?? [])
      .filter(o => o.id !== no.id).map(o => o.tipoOrganoId)
    await establecerTipos(nivel.id, restantes)
    await cargarOrganosDeNivel(nivel.id)
    toast.success(`«${nombre}» quitado del modelo de ${nivel.nombre}`)
  } catch (e) {
    toast.error(mensajeError(e, `No se pudo quitar «${nombre}».`))
  } finally {
    guardandoOrganos.value = false
  }
}

/** Al crear un subnivel, ofrecer copiar el modelo organizativo del padre. */
async function ofrecerHerencia(padre, nuevo) {
  try {
    const nOrganos = (organosPorNivel.value[padre.id] ?? []).length
    if (!nOrganos) return
    const ok = await confirm({
      titulo: 'Heredar el modelo organizativo',
      mensaje: `¿Copiar el modelo organizativo de «${padre.nombre}» (${nOrganos} `
        + `órgano${nOrganos === 1 ? '' : 's'}) al nuevo nivel? Podrás ajustarlo después.`,
      etiquetaConfirmar: 'Sí, heredar',
      etiquetaCancelar: 'Empezar en blanco',
    })
    if (!ok) return
    const res = await graphqlClient.request(OQ.HEREDAR_MODELO_DE_NIVEL, {
      nivelOrigenId: padre.id,
      nivelDestinoId: nuevo.id,
    })
    const copiados = res.heredarModeloDeNivel ?? 0
    await cargarOrganosDeNivel(nuevo.id)
    toast.success(`${copiados} órgano${copiados === 1 ? '' : 's'} copiado${copiados === 1 ? '' : 's'} de «${padre.nombre}»`)
  } catch (e) {
    toast.error(mensajeError(e, 'No se pudo heredar el modelo del nivel padre.'))
  }
}

// ── Carga de órganos ─────────────────────────────────────────────────────────
async function cargarOrganosDeNivel(nivelId) {
  if (!nivelId) return
  cargandoNivel.value = { ...cargandoNivel.value, [nivelId]: true }
  try {
    const data = await graphqlClient.request(OQ.GET_NIVELES_ORGANOS, { nivelId })
    const lista = (data.nivelesOrganos ?? []).slice()
      .sort((a, b) => (a.tipoOrgano?.nombre ?? '').localeCompare(b.tipoOrgano?.nombre ?? '', 'es'))
    organosPorNivel.value = { ...organosPorNivel.value, [nivelId]: lista }
  } catch (e) {
    toast.error(mensajeError(e, 'No se pudieron cargar los órganos del nivel.'))
  } finally {
    const { [nivelId]: _fuera, ...resto } = cargandoNivel.value
    cargandoNivel.value = resto
  }
}

async function cargarOrganosDeTodos() {
  const ids = []
  recorrer(n => ids.push(n.id))
  await Promise.all(ids.map(id => cargarOrganosDeNivel(id)))
}

function olvidarNivel(id) {
  const { [id]: _o, ...restoO } = organosPorNivel.value
  organosPorNivel.value = restoO
}

// ── Composición de cargos de un órgano ───────────────────────────────────────
// El orden de la lista ES el orden protocolario (índice + 1): la tarjeta reordena
// / añade / quita y manda la composición COMPLETA; aquí solo se persiste.
/** @param cargos [{ cargoId }] ya en el orden deseado. */
async function guardarComposicion(nivel, no, comp) {
  if (!no || esPleno(no)) return false
  try {
    await graphqlClient.request(OQ.ESTABLECER_COMPOSICION_NIVEL_ORGANO, {
      nivelOrganoId: no.id,
      cargos: comp.map((c, i) => ({ cargoId: c.cargoId, ordenProtocolario: i + 1 })),
    })
    await cargarOrganosDeNivel(nivel.id)
    return true
  } catch (e) {
    toast.error(mensajeError(e, 'Error al guardar la composición.'))
    return false
  }
}

async function cargarCatalogosOrganos() {
  try {
    const [dc, dt] = await Promise.all([
      graphqlClient.request(OQ.GET_CARGOS),
      graphqlClient.request(OQ.GET_TIPOS_ORGANO),
    ])
    cargos.value = (dc.cargos ?? []).slice().sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
    tiposOrgano.value = (dt.tiposOrgano ?? []).slice().sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
  } catch (e) {
    toast.error(mensajeError(e, 'No se pudieron cargar los catálogos de órganos.'))
  }
}

// Mutabilidad post-arranque: la estructura se "protege" cuando ya está en uso (hay
// unidades instanciadas). El editor queda read-only hasta pulsar "Modificar estructura".
// Las operaciones con impacto (borrar/anidar) ya confirman aparte con conteos reales.
const nUnidadesUso = computed(() => unidades.value.length)
const nSociosUso   = computed(() => miembros.value.length)
const estructuraProtegida = computed(() => nUnidadesUso.value > 0)
const desbloqueado = ref(false)
const editable = computed(() => !estructuraProtegida.value || desbloqueado.value)
defineExpose({ estructuraProtegida, distribuida, setDistribuida, nodoRaizActual })

// ═══ CONTEXTO PARA LAS TARJETAS RECURSIVAS ════════════════════════════════════
// La tarjeta se repinta a sí misma a cualquier profundidad: pasar todo esto por
// props sería prop-drilling insufrible. Solo `nivel` y `depth` van por props.
provide('estructuraCtx', {
  // estado compartido (refs/computed: se consumen con .value en la tarjeta)
  editable, guardando, guardandoOrganos, permiteSubniveles,
  organosPorNivel, cargandoNivel,
  // catálogo para el select de ámbito del formulario in situ
  ambitos: ambitosOrdenados,
  // nivel que debe abrir su formulario nada más pintarse (recién creado)
  nivelAEditar,
  // plegado
  estaAbiertoNivel, alternarNivel, estaAbiertoOrgano, alternarOrgano, abrirOrgano,
  // guardas de habilitación
  puedeSubir, puedeSuperior, puedeEliminar, puedeHermano, hermanoAnterior,
  // datos del nivel: el formulario es local a la tarjeta, la mutación es de aquí
  guardarNivel,
  eliminarNivel: iniciarEliminar,
  anadirHijo: añadirHijo,
  anadirHermano: añadirHermano,
  anadirSuperior: añadirSuperior,
  promover, demover,
  // modelo organizativo del nivel
  abrirAnadirOrgano, quitarOrganoDelNivel,
  // composición de cargos (la tarjeta reordena; aquí solo se persiste)
  cargos, guardarComposicion,
  toastOk: (m) => toast.success(m),
  esPleno, rangoDe, nombreCargo, maxDe, composicionOrdenada,
})

onMounted(async () => {
  await Promise.all([cargarTipos(), cargarArbol(), cargarAmbitos(), cargarCatalogosOrganos()])
  if (!props.nivelRaizId && tiposTerritoriales.value.length === 0) {
    await crearTipo({
      nombre: 'Asociación',
      naturaleza: 'TERRITORIAL',
      vinculo: 'INTERNA',
      activo: true,
      unidadId: props.unidadId,
    })
  }
  // La cascada muestra TODOS los niveles con su modelo dentro: se cargan todos.
  await cargarOrganosDeTodos()
})
</script>

<style scoped>
/* El editor solo orquesta: la cascada. Todo lo visual de una tarjeta (y de su
   modelo organizativo) vive en NivelCard.vue, que se repinta a sí misma. */
.ladder {
  padding: 4px 0 8px;
  display: flex; flex-direction: column; gap: 20px;
}
.addroot {
  align-self: flex-start; display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 14px; border: 1px dashed var(--t-border); border-radius: 9px;
  background: none; cursor: pointer; font: inherit; font-size: 12px; font-weight: 600;
  color: var(--t-text-muted);
}
.addroot:hover:not(:disabled) { border-color: var(--t-400); color: var(--t-700); background: var(--t-50) }
.addroot:disabled { opacity: .4; cursor: not-allowed }
</style>
