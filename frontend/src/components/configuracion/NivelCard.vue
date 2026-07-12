<template>
  <div class="branch">
    <article class="terr"
      :data-d="Math.min(depth, 3)"
      :data-open="String(ctx.estaAbiertoNivel(nivel.id))">

      <div class="head" @click="ctx.alternarNivel(nivel.id)">
        <span class="caret">▼</span>
        <span class="dot" :title="`Nivel ${depth + 1}`">{{ romano(depth) }}</span>
        <!-- Mientras editas, el título refleja EN VIVO lo que escribes. -->
        <span class="nm">{{ nombreVivo || 'Sin nombre' }}</span>
        <span v-if="ambitoVivo" class="amb">→ {{ ambitoVivo }}</span>
        <span class="sp"></span>
        <span v-if="nOrganos" class="pill ok num">
          {{ nOrganos }} órgano{{ nOrganos === 1 ? '' : 's' }} ·
          {{ nCargos }} cargo{{ nCargos === 1 ? '' : 's' }}
        </span>
        <span v-else-if="nOrganos === 0" class="pill todo">sin modelo</span>

        <!-- Todas las acciones de ESTE nivel viven en un único menú: dos
             afordancias para lo mismo (lápiz suelto + menú) sería ruido. -->
        <div class="menu" @click.stop>
          <button type="button" class="ico" title="Más acciones"
            :disabled="!ctx.editable.value || ctx.guardando.value"
            :aria-expanded="String(menuActivo === 'nivel')"
            @click="alternarMenu('nivel')">
            <EllipsisHorizontalIcon class="w-4 h-4" />
          </button>
          <div v-if="menuActivo === 'nivel'" class="pop" @click="cerrarMenu">
            <div v-for="(g, gi) in grupos" :key="g.titulo" class="grp">
              <hr v-if="gi" class="sep" />
              <p class="gt">{{ g.titulo }}</p>
              <button v-for="a in g.items" :key="a.key" type="button"
                class="mi" :class="{ danger: a.variant === 'danger' }"
                :disabled="a.disabled" :title="a.title || ''"
                @click="ejecutar(a.key)">
                <component :is="a.icon" class="w-3.5 h-3.5" />
                {{ a.label }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ══ Edición IN SITU de los datos del nivel ══════════════════════════
           Sin drawer: la tarjeta se convierte en su propio formulario. -->
      <form v-if="editando" class="edit-form" @submit.prevent="guardar">
        <label class="fld">
          <span>Nombre del nivel</span>
          <input ref="inputNombre" v-model="fNombre" type="text" :disabled="ctx.guardando.value"
            placeholder="p.ej. Provincial" />
        </label>
        <label class="fld">
          <span>Ámbito geográfico</span>
          <select v-model="fAmbitoId" :disabled="ctx.guardando.value">
            <option value="">— sin ámbito —</option>
            <option v-for="a in ctx.ambitos.value" :key="a.id" :value="a.id">{{ a.nombre }}</option>
          </select>
        </label>
        <label class="fld">
          <span>Denominación (singular)</span>
          <input v-model="fDenomSingular" type="text" :disabled="ctx.guardando.value"
            placeholder="p.ej. Agrupación Provincial" />
        </label>
        <label class="fld">
          <span>Denominación (plural)</span>
          <input v-model="fDenomPlural" type="text" :disabled="ctx.guardando.value"
            placeholder="p.ej. Agrupaciones Provinciales" />
        </label>
        <div class="acts">
          <button type="button" class="fbtn ghost" :disabled="ctx.guardando.value" @click="cancelar">
            Cancelar
          </button>
          <button type="submit" class="fbtn" :disabled="ctx.guardando.value || !fNombre.trim()">
            {{ ctx.guardando.value ? 'Guardando…' : 'Guardar' }}
          </button>
        </div>
      </form>

      <div class="body"><div class="inner">
        <EstadoCarga v-if="ctx.cargandoNivel.value[nivel.id]" mensaje="Cargando órganos del nivel…" />

        <template v-else>
          <div v-if="organos.length" class="organs">
            <div v-for="o in organos" :key="o.id"
              class="org" :data-open="String(ctx.estaAbiertoOrgano(o.id))">
              <div class="oh" @click="ctx.alternarOrgano(o.id)">
                <span class="ocaret">▼</span>
                <span class="on">{{ o.tipoOrgano?.nombre ?? '—' }}</span>
                <span class="k" :class="ctx.esPleno(o) ? 'pleno' : 'cargos'">
                  {{ ctx.esPleno(o) ? 'Pleno' : 'Cargos' }}
                </span>
                <span class="osp"></span>

                <!-- Mismo esquema que el nivel: un único menú ⋯ con grupos -->
                <div class="menu" @click.stop>
                  <button type="button" class="ico ico-sm" title="Más acciones"
                    :disabled="!ctx.editable.value || ctx.guardandoOrganos.value"
                    :aria-expanded="String(menuActivo === `org:${o.id}`)"
                    @click="alternarMenu(`org:${o.id}`)">
                    <EllipsisHorizontalIcon class="w-3.5 h-3.5" />
                  </button>
                  <div v-if="menuActivo === `org:${o.id}`" class="pop" @click="cerrarMenu">
                    <div v-for="(g, gi) in gruposOrgano(o)" :key="g.titulo" class="grp">
                      <hr v-if="gi" class="sep" />
                      <p class="gt">{{ g.titulo }}</p>
                      <button v-for="a in g.items" :key="a.key" type="button"
                        class="mi" :class="{ danger: a.variant === 'danger' }"
                        :disabled="a.disabled" :title="a.title || ''"
                        @click="ejecutarOrgano(a.key, o)">
                        <component :is="a.icon" class="w-3.5 h-3.5" />
                        {{ a.label }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <div class="obody"><div class="oinner">
                <div v-if="ctx.esPleno(o)" class="pl-empty">
                  Composición abierta — el pleno de socios con derecho a voto.
                </div>
                <template v-else>
                  <!-- Los cargos NO son una jerarquía: son la composición del órgano,
                       una lista de pares ordenada alfabéticamente. -->
                  <ul v-if="composicion(o).length" class="posts">
                    <li v-for="c in composicion(o)" :key="c.cargoId">
                      <span class="rl">{{ c.cargo?.nombre ?? ctx.nombreCargo(c.cargoId) }}</span>
                      <span v-if="ctx.maxDe(c.cargoId)" class="mx num">máx. {{ ctx.maxDe(c.cargoId) }}</span>
                      <!-- Una sola acción ⇒ icono directo, sin menú ⋯ -->
                      <button type="button" class="ico ico-xs del" title="Eliminar cargo"
                        :disabled="!ctx.editable.value || guardandoComposicion"
                        @click.stop="quitarCargo(o, c.cargoId)">
                        <TrashIcon class="w-3.5 h-3.5" />
                      </button>
                    </li>
                  </ul>
                  <div v-else class="pl-empty">Sin cargos definidos todavía.</div>

                  <!-- Selector in situ para añadir un cargo a la composición -->
                  <div v-if="anadiendoEn === o.id" class="addrow" @click.stop>
                    <AppSelect v-model="cargoNuevoId" :options="opcionesCargos(o)"
                      placeholder="Selecciona un cargo…" width="md" />
                    <button type="button" class="fbtn"
                      :disabled="!cargoNuevoId || guardandoComposicion" @click="confirmarAnadirCargo(o)">
                      {{ guardandoComposicion ? 'Añadiendo…' : 'Añadir' }}
                    </button>
                    <button type="button" class="fbtn ghost" :disabled="guardandoComposicion"
                      @click="anadiendoEn = null">Cancelar</button>
                  </div>
                </template>
              </div></div>
            </div>
          </div>

          <!-- Añadir un órgano es una acción sobre el MODELO del nivel: vive en su
               menú ⋯, no como botón suelto dentro de la tarjeta. -->
          <div v-else class="noorg">
            Este nivel no tiene órganos: añádelos desde el menú ⋯ del nivel.
          </div>
        </template>
      </div></div>
    </article>

    <!-- RECURSIÓN: la misma tarjeta, un nivel más abajo -->
    <NivelCard v-for="h in (nivel.hijos ?? [])" :key="h.id" :nivel="h" :depth="depth + 1" />
  </div>
</template>

<script setup>
import { ref, computed, inject, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import AppSelect from '@/components/common/AppSelect.vue'
import {
  PlusIcon, TrashIcon, PencilSquareIcon, ArrowUpIcon, ArrowsUpDownIcon,
  ArrowUturnDownIcon, EllipsisHorizontalIcon,
} from '@heroicons/vue/24/outline'

defineOptions({ name: 'NivelCard' })

const props = defineProps({
  nivel: { type: Object, required: true },
  depth: { type: Number, default: 0 },
})

// Todo el contexto compartido (catálogos, flags, plegado, acciones) lo provee el
// editor: con una tarjeta recursiva, el prop-drilling sería insufrible.
const ctx = inject('estructuraCtx')

const ROMANOS = ['I', 'II', 'III', 'IV', 'V', 'VI']
const romano = (d) => ROMANOS[d] ?? String(d + 1)

const organos  = computed(() => ctx.organosPorNivel.value[props.nivel.id] ?? [])
const nOrganos = computed(() => ctx.organosPorNivel.value[props.nivel.id]?.length ?? null)
const nCargos  = computed(() =>
  organos.value.reduce((s, o) => s + (o.composicion?.length ?? 0), 0))

// ── Edición IN SITU de los datos del nivel ───────────────────────────────────
// El estado es LOCAL de cada tarjeta: la cascada es recursiva, así que cada
// nivel se edita por su cuenta sin pisar a los demás.
const editando       = ref(false)
const fNombre        = ref('')
const fAmbitoId      = ref('')
const fDenomSingular = ref('')
const fDenomPlural   = ref('')

// Vista previa EN VIVO: mientras editas, la cabecera refleja lo que escribes,
// sin esperar a guardar. Fuera del modo edición, muestra el dato persistido.
const nombreVivo = computed(() =>
  editando.value ? fNombre.value : (props.nivel.nombre ?? ''))

const ambitoVivo = computed(() => {
  if (editando.value) {
    const a = ctx.ambitos.value.find(x => x.id === fAmbitoId.value)
    return a?.nombre || fDenomSingular.value || ''
  }
  return props.nivel.ambitoGeografico?.nombre || props.nivel.denominacionSingular || ''
})
const inputNombre    = ref(null)

function abrirEdicion() {
  if (!ctx.editable.value || ctx.guardando.value) return
  const n = props.nivel
  fNombre.value        = n.nombre ?? ''
  fAmbitoId.value      = n.ambitoGeograficoId ?? ''
  fDenomSingular.value = n.denominacionSingular ?? ''
  fDenomPlural.value   = n.denominacionPlural ?? ''
  editando.value = true
  nextTick(() => inputNombre.value?.focus())
}

const cancelar = () => { editando.value = false }

async function guardar() {
  if (!fNombre.value.trim() || ctx.guardando.value) return
  const ok = await ctx.guardarNivel(props.nivel, {
    nombre: fNombre.value,
    ambitoGeograficoId: fAmbitoId.value,
    denominacionSingular: fDenomSingular.value,
    denominacionPlural: fDenomPlural.value,
  })
  if (ok) editando.value = false
}

// Un nivel recién creado se pinta ya con su formulario abierto (para nombrarlo).
watch(() => ctx.nivelAEditar.value, (id) => {
  if (id && id === props.nivel.id) {
    ctx.nivelAEditar.value = null
    abrirEdicion()
  }
}, { immediate: true })

// ── Menús compactos de acciones (⋯) ──────────────────────────────────────────
// Un ÚNICO menú abierto a la vez en toda la tarjeta: la clave identifica cuál
// ('nivel', `org:<id>`, `cargo:<orgId>:<cargoId>`). Abrir uno cierra el otro
// sin necesidad de un ref por cada fila.
const menuActivo = ref(null)
const cerrarMenu = () => { menuActivo.value = null }
const alternarMenu = (k) => { menuActivo.value = menuActivo.value === k ? null : k }
onMounted(() => document.addEventListener('click', cerrarMenu))
onBeforeUnmount(() => document.removeEventListener('click', cerrarMenu))

// Mismas guardas que antes calculaba el `acciones` computed del editor.
// El menú separa dos naturalezas distintas: lo que este nivel ES (sus datos, su
// existencia) y dónde ESTÁ en el árbol (su topología). Mezclarlas confundía.
const grupos = computed(() => {
  const n   = props.nivel
  const d   = props.depth
  const sin = !ctx.permiteSubniveles.value   // distribuida ⇒ no se anidan subniveles
  return [
    {
      titulo: 'Este nivel',
      items: [
        { key: 'editar', label: 'Editar datos', icon: PencilSquareIcon,
          disabled: editando.value,
          title: editando.value ? 'Ya estás editando este nivel' : '' },
        { key: 'eliminar', label: 'Eliminar nivel', icon: TrashIcon, variant: 'danger',
          disabled: !ctx.puedeEliminar(n, d) },
      ],
    },
    {
      titulo: 'Estructura del árbol',
      items: [
        { key: 'hijo', label: 'Añadir nivel inferior', icon: PlusIcon,
          disabled: sin,
          title: sin ? 'En estructura distribuida los subniveles se definen en cada agrupación' : '' },
        { key: 'hermano', label: 'Añadir al mismo nivel', icon: PlusIcon,
          disabled: !ctx.puedeHermano(n) },
        { key: 'superior', label: 'Insertar encima', icon: ArrowsUpDownIcon,
          disabled: !ctx.puedeSuperior(n) || sin },
        { key: 'subir', label: 'Subir un nivel', icon: ArrowUpIcon,
          disabled: !ctx.puedeSubir(n, d) },
        { key: 'anidar', label: 'Anidar en el anterior', icon: ArrowUturnDownIcon,
          disabled: !ctx.hermanoAnterior(n) || sin },
      ],
    },
    {
      titulo: 'Modelo organizativo',
      items: [
        { key: 'anadirOrgano', label: 'Añadir órgano', icon: PlusIcon,
          disabled: ctx.guardandoOrganos.value },
      ],
    },
  ]
})

function ejecutar(key) {
  const n = props.nivel
  if (key === 'editar')        abrirEdicion()
  else if (key === 'hijo')     ctx.anadirHijo(n)
  else if (key === 'hermano')  ctx.anadirHermano(n)
  else if (key === 'superior') ctx.anadirSuperior(n)
  else if (key === 'subir')    ctx.promover(n)
  else if (key === 'anidar')   ctx.demover(n)
  else if (key === 'eliminar') ctx.eliminarNivel(n)
  else if (key === 'anadirOrgano') ctx.abrirAnadirOrgano(n)
}

// ── Menú del ÓRGANO ──────────────────────────────────────────────────────────
// Mismo esquema de grupos que el nivel: lo que el órgano ES (su pertenencia al
// nivel) y de qué se COMPONE. Un pleno no se compone de cargos ⇒ sin 2.º grupo.
const gruposOrgano = (o) => {
  const g = [
    {
      titulo: 'Este órgano',
      items: [
        { key: 'quitar', label: 'Eliminar', icon: TrashIcon, variant: 'danger',
          disabled: ctx.guardandoOrganos.value },
      ],
    },
  ]
  if (!ctx.esPleno(o)) {
    const libres = cargosDisponibles(o)
    g.push({
      titulo: 'Composición',
      items: [
        { key: 'anadirCargo', label: 'Añadir cargo', icon: PlusIcon,
          disabled: !libres.length || guardandoComposicion.value,
          title: libres.length ? '' : 'Todos los cargos del catálogo ya están en este órgano' },
      ],
    })
  }
  return g
}

function ejecutarOrgano(key, o) {
  if (key === 'quitar')           ctx.quitarOrganoDelNivel(props.nivel, o)
  else if (key === 'anadirCargo') abrirAnadirCargo(o)
}

// ── Composición de cargos del órgano ─────────────────────────────────────────
// La composición NO es una jerarquía protocolaria: es la lista de cargos que
// forman el órgano, todos pares entre sí. Se muestra ORDENADA ALFABÉTICAMENTE.
// El backend sigue guardando un `ordenProtocolario` (lo deriva `guardarComposicion`
// del orden de la lista que le pasamos), pero aquí ni se enseña ni se edita.
const guardandoComposicion = ref(false)
const anadiendoEn  = ref(null)   // id del órgano cuyo selector está abierto
const cargoNuevoId = ref('')

const nombreDe = (c) => c.cargo?.nombre ?? ctx.nombreCargo(c.cargoId)

const composicion = (o) =>
  [...(o.composicion ?? [])].sort((a, b) => nombreDe(a).localeCompare(nombreDe(b), 'es'))

const cargosDisponibles = (o) => {
  const usados = new Set((o.composicion ?? []).map(c => c.cargoId))
  return ctx.cargos.value.filter(c => c.activo !== false && !usados.has(c.id))
}
const opcionesCargos = (o) =>
  cargosDisponibles(o).map(c => ({ value: c.id, label: c.nombre }))

function abrirAnadirCargo(o) {
  cargoNuevoId.value = ''
  anadiendoEn.value  = o.id
  ctx.abrirOrgano?.(o.id)
}

/** Persiste la composición entera (siempre en orden alfabético). */
async function persistir(o, lista, msg) {
  guardandoComposicion.value = true
  try {
    const ok = await ctx.guardarComposicion(props.nivel, o, lista.map(id => ({ cargoId: id })))
    if (ok && msg) ctx.toastOk(msg)
    return ok
  } finally {
    guardandoComposicion.value = false
  }
}

/** Ids de la composición, en el mismo orden alfabético con el que se pintan. */
const idsDe = (o) => composicion(o).map(c => c.cargoId)

/** Reordena alfabéticamente por nombre de cargo antes de persistir. */
const alfabetico = (ids) =>
  [...ids].sort((a, b) => ctx.nombreCargo(a).localeCompare(ctx.nombreCargo(b), 'es'))

async function confirmarAnadirCargo(o) {
  if (!cargoNuevoId.value) return
  const nombre = ctx.nombreCargo(cargoNuevoId.value)
  const ok = await persistir(o, alfabetico([...idsDe(o), cargoNuevoId.value]),
    `«${nombre}» añadido a la composición`)
  if (ok) { anadiendoEn.value = null; cargoNuevoId.value = '' }
}

async function quitarCargo(o, cargoId) {
  if (!ctx.editable.value || guardandoComposicion.value) return
  const nombre = ctx.nombreCargo(cargoId)
  await persistir(o, idsDe(o).filter(id => id !== cargoId), `«${nombre}» eliminado del órgano`)
}
</script>

<style scoped>
/* Los tokens --t-* los inyecta el tema activo (orgConfig.applyTheme) en :root.
   Aquí solo se declaran los que NO son del tema (semánticos y sombras). */
.branch {
  --ok: #059669; --ok-bg: #ecfdf5;
  --todo: #d97706; --todo-bg: #fffbeb; --danger: #dc2626;
  --sh: 0 1px 2px rgba(17,24,39,.05);
  --sh-lift: 0 6px 20px -6px color-mix(in srgb, var(--t-600) 28%, transparent);
  display: flex; flex-direction: column; gap: 20px;
}
.num { font-variant-numeric: tabular-nums }

/* ══ Tarjeta territorial ═══════════════════════════════════════════════════
   Proporción contenida (no barras anchas), escalonada por profundidad, unida
   al padre por riel + codo. */
.terr {
  position: relative; border: 1px solid var(--t-border); border-radius: 12px;
  background: var(--t-card-bg); transition: border-color .15s, box-shadow .15s;
  width: min(560px, 100%);
}
.terr:hover { border-color: var(--t-300); box-shadow: var(--sh-lift) }

/* Jerarquía territorial exagerada: sangría + riel vertical + codo grueso.
   El grosor del borde izquierdo decrece con la profundidad. */
.terr[data-d="0"] { border-left: 6px solid var(--t-600) }
.terr[data-d="1"] { margin-left: 80px;  border-left: 5px solid var(--t-500) }
.terr[data-d="2"] { margin-left: 160px; border-left: 4px solid var(--t-400) }
.terr[data-d="3"] { margin-left: 240px; border-left: 3px solid var(--t-300) }
.terr[data-d]:not([data-d="0"])::after {
  content: ""; position: absolute; left: -44px; top: -40px; height: calc(40px + 23px);
  width: 3px; background: var(--t-200); border-radius: 3px;
}
.terr[data-d]:not([data-d="0"])::before {
  content: ""; position: absolute; left: -44px; top: 22px; height: 3px; width: 44px;
  background: var(--t-200); border-radius: 3px;
}
.terr[data-d="2"]::after, .terr[data-d="2"]::before,
.terr[data-d="3"]::after, .terr[data-d="3"]::before { background: var(--t-100) }

/* cabecera clicable: pliega / despliega */
.terr > .head {
  display: flex; align-items: center; gap: 10px; padding: 12px 13px; cursor: pointer;
  user-select: none; border-radius: 11px;
}
.terr > .head:hover { background: var(--t-50) }
.terr .caret {
  flex: 0 0 auto; width: 16px; color: var(--t-text-muted); font-size: 10px; line-height: 1;
  transition: transform .18s ease;
}
.terr[data-open="false"] .caret { transform: rotate(-90deg) }
/* cuerpo plegable (grid trick: sin alturas mágicas) */
.terr > .body { display: grid; grid-template-rows: 1fr; transition: grid-template-rows .22s ease }
.terr[data-open="false"] > .body { grid-template-rows: 0fr }
.terr > .body > .inner { overflow: hidden; min-height: 0 }
/* Los menús ⋯ del órgano y del cargo viven DENTRO del cuerpo plegable, que
   recorta para que la animación de plegado funcione. Abierto, deja desbordar
   (si no, el desplegable saldría cortado). */
.terr[data-open="true"] > .body > .inner { overflow: visible }
/* medalla de profundidad: I, II, III */
.terr .dot {
  flex: 0 0 auto; width: 22px; height: 22px; border-radius: 6px; display: grid; place-items: center;
  font-size: 9.5px; font-weight: 800; letter-spacing: .04em;
  background: var(--t-100); color: var(--t-700); border: 1px solid var(--t-200);
}
.terr[data-d="0"] .dot { background: var(--t-600); color: #fff; border-color: var(--t-600) }
.terr[data-d="1"] .dot { background: var(--t-200); color: var(--t-700) }
.terr .nm { font-size: 14px; font-weight: 700; letter-spacing: -.01em; color: var(--t-text-main) }
.terr[data-d="0"] .nm { font-size: 15px; font-weight: 800 }
.terr .amb { font-size: 11.5px; color: var(--t-text-muted) }
.terr .sp { flex: 1 }
.pill {
  font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 999px;
  border: 1px solid transparent; white-space: nowrap;
}
.pill.ok { color: var(--ok); background: var(--ok-bg); border-color: color-mix(in srgb, var(--ok) 22%, transparent) }
.pill.todo { color: var(--todo); background: var(--todo-bg); border-color: color-mix(in srgb, var(--todo) 25%, transparent) }
.ico {
  width: 28px; height: 28px; display: grid; place-items: center; border-radius: 7px;
  border: 1px solid var(--t-border); background: none; cursor: pointer;
  color: var(--t-text-muted); font-size: 13px; flex: 0 0 auto;
}
.ico:hover:not(:disabled) { border-color: var(--t-400); color: var(--t-700); background: var(--t-50) }
.ico:disabled { opacity: .35; cursor: not-allowed }
.ico-sm { width: 24px; height: 24px }
.ico-xs { width: 20px; height: 20px; border-color: transparent; border-radius: 5px }

/* ══ Menú compacto de acciones (nivel · órgano) ════════════════════════════
   UN solo componente visual para los dos. La fila de cargo no tiene menú: su
   única acción (eliminar) es un icono directo. */
.menu { position: relative; flex: 0 0 auto }
.pop {
  position: absolute; top: calc(100% + 5px); right: 0; z-index: 20; min-width: 210px;
  display: flex; flex-direction: column; padding: 4px; border-radius: 10px;
  background: var(--t-card-bg); border: 1px solid var(--t-border);
  box-shadow: 0 12px 28px -10px rgba(17,24,39,.35);
}
.pop .mi {
  display: flex; align-items: center; gap: 8px; padding: 7px 9px; border: 0; border-radius: 7px;
  background: none; cursor: pointer; font: inherit; font-size: 12px; font-weight: 600;
  color: var(--t-text-main); text-align: left; white-space: nowrap;
}
.pop .mi:hover:not(:disabled) { background: var(--t-50); color: var(--t-700) }
.pop .sep { margin: 5px 0; border: 0; border-top: 1px solid var(--t-border) }
/* encabezado de grupo: nombra la naturaleza de las acciones que agrupa */
.pop .gt {
  margin: 0; padding: 4px 10px 3px;
  font-size: 9.5px; font-weight: 700; letter-spacing: .07em; text-transform: uppercase;
  color: var(--t-text-muted);
}
.pop .mi:disabled { opacity: .35; cursor: not-allowed }
.pop .mi.danger { color: var(--danger) }
.pop .mi.danger:hover:not(:disabled) { background: color-mix(in srgb, var(--danger) 8%, transparent); color: var(--danger) }

/* Selector in situ para añadir un cargo a la composición del órgano */
.addrow {
  display: flex; align-items: center; gap: 7px; flex-wrap: wrap;
  margin: 0 10px 10px; padding: 8px 9px;
  border: 1px dashed var(--t-border); border-radius: 8px;
}

/* ══ Formulario de datos del nivel, in situ dentro de la tarjeta ════════════
   Denso, rejilla de 2 columnas: no debe empujar el modelo organizativo fuera
   de la vista. */
.edit-form {
  display: grid; grid-template-columns: 1fr 1fr; gap: 9px 12px;
  margin: 0 13px 12px; padding: 11px 12px 12px;
  border: 1px solid var(--t-200); border-radius: 9px; background: var(--t-50);
}
.edit-form .fld { display: flex; flex-direction: column; gap: 3px; min-width: 0 }
.edit-form .fld > span {
  font-size: 10px; font-weight: 700; letter-spacing: .04em; text-transform: uppercase;
  color: var(--t-text-muted);
}
.edit-form input, .edit-form select {
  width: 100%; box-sizing: border-box; padding: 6px 8px; font: inherit; font-size: 12.5px;
  color: var(--t-text-main); background: var(--t-card-bg);
  border: 1px solid var(--t-border); border-radius: 7px;
}
.edit-form input:focus, .edit-form select:focus {
  outline: none; border-color: var(--t-500); box-shadow: 0 0 0 3px var(--t-100);
}
.edit-form input:disabled, .edit-form select:disabled { opacity: .55; cursor: not-allowed }
.edit-form .acts { grid-column: 1 / -1; display: flex; justify-content: flex-end; gap: 7px; margin-top: 2px }
.fbtn {
  padding: 6px 14px; border-radius: 7px; border: 0; cursor: pointer; font: inherit;
  font-size: 12px; font-weight: 650; background: var(--t-600); color: #fff;
}
.fbtn:hover:not(:disabled) { background: var(--t-700) }
.fbtn:disabled { opacity: .45; cursor: not-allowed }
.fbtn.ghost { background: none; color: var(--t-text-muted); border: 1px solid var(--t-border) }
.fbtn.ghost:hover:not(:disabled) { background: var(--t-card-bg); color: var(--t-700) }
@media (max-width: 520px) { .edit-form { grid-template-columns: 1fr } }

/* ══ Arbolito de órganos DENTRO de la tarjeta ═══════════════════════════════ */
.organs { padding: 0 13px 12px 13px; display: flex; flex-direction: column; gap: 8px }
/* Sin `overflow:hidden`: los menús ⋯ del órgano y del cargo tienen que poder
   desbordar la subtarjeta. El redondeo se hace en las piezas, no recortando. */
.org { border: 1px solid var(--t-border); border-radius: 8px; background: var(--t-page-bg) }
.org > .oh {
  display: flex; align-items: center; gap: 8px; padding: 7px 10px; background: var(--t-card-bg);
  border-bottom: 1px solid var(--t-border); cursor: pointer; user-select: none;
  border-radius: 7px 7px 0 0;
}
.org[data-open="false"] > .oh { border-radius: 7px }
.org > .oh:hover { background: var(--t-50) }
.org .ocaret {
  flex: 0 0 auto; width: 14px; color: var(--t-text-muted); font-size: 9px; line-height: 1;
  transition: transform .18s ease;
}
.org[data-open="false"] .ocaret { transform: rotate(-90deg) }
.org[data-open="false"] > .oh { border-bottom: 0 }
.org .obody { display: grid; grid-template-rows: 1fr; transition: grid-template-rows .2s ease }
.org[data-open="false"] .obody { grid-template-rows: 0fr }
.org .obody > .oinner { overflow: hidden; min-height: 0 }
.org[data-open="true"] .obody > .oinner { overflow: visible }
/* El ÓRGANO es el contenedor: pesa más que los cargos que lo componen. */
.org .on { font-size: 13.5px; font-weight: 700; color: var(--t-text-main) }
.k {
  font-size: 9px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
  padding: 2px 5px; border-radius: 4px; white-space: nowrap;
}
.k.cargos { color: var(--t-700); background: var(--t-100) }
.k.pleno { color: var(--ok); background: var(--ok-bg) }
.org .osp { flex: 1 }

/* Lista de cargos: NO hay jerarquía. Todos los cargos son pares ⇒ misma sangría,
   mismo peso, sin medallas ni codos. Solo una lista sobria, en orden alfabético. */
.posts { list-style: none; margin: 0; padding: 9px 10px 11px 10px }
.posts li {
  display: flex; align-items: center; gap: 9px; padding: 3px 0; font-size: 12.5px;
  color: var(--t-text-muted);
}
/* .rl empuja: `máx.` y la papelera quedan pegados al margen derecho */
.posts li .rl { flex: 1; min-width: 0; font-weight: 550; color: var(--t-text-main) }
.posts li .mx { flex: 0 0 auto; font-size: 10px; color: var(--t-text-muted) }
/* Afordancia discreta: la papelera solo aparece al pasar por encima de la fila. */
.posts li .del { opacity: 0; transition: opacity .12s; color: var(--t-text-muted) }
.posts li:hover .del, .posts li .del:focus-visible { opacity: 1 }
.posts li .del:hover:not(:disabled) {
  color: var(--danger); border-color: transparent;
  background: color-mix(in srgb, var(--danger) 8%, transparent);
}
.pl-empty { padding: 8px 10px 10px; font-size: 11.5px; color: var(--t-text-muted); font-style: italic }
.noorg { padding: 2px 13px 12px; font-size: 12px; color: var(--t-text-muted) }

@media (prefers-reduced-motion: reduce) { .terr *, .org * { transition: none !important } }
</style>
