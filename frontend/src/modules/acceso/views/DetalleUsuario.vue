<template>
  <AppLayout :title="titulo" :subtitle="usuario?.usuario?.username || 'Cuenta de usuario'">
    <EstadoCarga v-if="cargando" mensaje="Cargando cuenta…" />

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800">
      {{ error }}
      <button @click="cargar" class="ml-3 underline font-medium hover:no-underline">Reintentar</button>
    </div>

    <div v-else-if="usuario" class="max-w-xl">

      <!-- Datos de la cuenta -->
      <section class="rounded-xl border border-slate-200 bg-white">
        <div class="flex items-center gap-3 px-4 py-3 border-b border-slate-100">
          <span class="shrink-0 w-1.5 h-5 rounded-full bg-indigo-500"></span>
          <h2 class="text-sm font-semibold text-slate-800">Datos de la cuenta</h2>
        </div>
        <dl class="grid grid-cols-3 gap-x-3 gap-y-3 text-sm px-4 py-4">
          <dt class="text-slate-500">Usuario</dt>
          <dd class="col-span-2 font-mono text-slate-800">{{ usuario.usuario?.username || '—' }}</dd>

          <dt class="text-slate-500">Email</dt>
          <dd class="col-span-2 text-slate-800 break-all">{{ usuario.usuario?.email || usuario.email || '—' }}</dd>

          <dt class="text-slate-500">Vinculación</dt>
          <dd class="col-span-2">
            <span v-if="usuario.vinculacionNombre"
              class="inline-flex px-2 py-0.5 text-xs font-medium rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100">
              {{ etiquetaVinculacion(usuario) }}
            </span>
            <span v-else class="text-slate-400">—</span>
          </dd>

          <dt class="text-slate-500">Acceso</dt>
          <dd class="col-span-2 flex items-center gap-2">
            <button v-if="puedeEliminar"
              @click="toggleAcceso"
              :disabled="alternando"
              :title="usuario.usuario?.activo ? 'Desactivar acceso' : 'Reactivar acceso'"
              class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none"
              :class="[usuario.usuario?.activo ? 'bg-green-500' : 'bg-gray-300', alternando ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer']">
              <span class="inline-block h-3 w-3 transform rounded-full bg-white transition-transform shadow-sm"
                :class="usuario.usuario?.activo ? 'translate-x-5' : 'translate-x-1'"></span>
            </button>
            <span class="text-xs font-medium"
              :class="usuario.usuario?.activo ? 'text-green-700' : 'text-red-600'">
              {{ usuario.usuario?.activo ? 'Activo' : 'Inactivo' }}
            </span>
          </dd>

          <dt class="text-slate-500">Último acceso</dt>
          <dd class="col-span-2 text-slate-800">{{ formatFecha(usuario.usuario?.ultimoAcceso) || 'Nunca' }}</dd>
        </dl>
      </section>

      <!-- Los roles NO se asignan a la cuenta: se derivan de los cargos que ejerce
           la persona (vía mandato). La gestión de mandatos/cargos es el punto de
           gobernanza; hasta que exista, esta ficha no muestra ni edita roles. -->

    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import { graphqlClient } from '@/graphql/client.js'
import { usePermisos } from '@/composables/usePermisos.js'
import { useOrgConfigStore } from '@/stores/orgConfig'
import { useToast } from '@/composables/useToast'
import { nombreTipoVinculacion } from '@/utils/tipoVinculacion.js'
import { GET_CUENTAS_ACCESO } from '@/graphql/queries/miembros.js'
import { ACTIVAR_USUARIO, DESACTIVAR_USUARIO } from '@/graphql/queries/usuarios.js'

defineOptions({ name: 'DetalleUsuario' })

const route = useRoute()
const { tienePermiso } = usePermisos()
const orgConfig = useOrgConfigStore()
const toast = useToast()

const usuario     = ref(null)     // fila SocioVista con .usuario
const cargando    = ref(false)
const error       = ref('')
const alternando  = ref(false)

const titulo = computed(() =>
  usuario.value
    ? `${usuario.value.apellido1 ?? ''} ${usuario.value.apellido2 ?? ''}${usuario.value.apellido1 ? ',' : ''} ${usuario.value.nombre ?? ''}`.trim()
    : 'Cuenta de usuario')

const etiquetaVinculacion = (m) =>
  m.vinculacionTipoCodigo
    ? nombreTipoVinculacion(m.vinculacionTipoCodigo, orgConfig, m.vinculacionNombre)
    : m.vinculacionNombre

const puedeEliminar = computed(() =>
  !!usuario.value?.usuario
  && usuario.value.usuario.username !== 'superadmin'
  && tienePermiso('ACCESO_USUARIO_ELIMINAR'))

function formatFecha(f) {
  if (!f) return ''
  return new Date(f).toLocaleString('es-ES', { day: 'numeric', month: 'numeric', year: '2-digit', hour: '2-digit', minute: '2-digit' })
}

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const cuentasData = await graphqlClient.request(GET_CUENTAS_ACCESO)
    const fila = (cuentasData?.miembros ?? []).find(m => m.id === route.params.id)
    if (!fila) { error.value = 'Cuenta no encontrada'; return }
    usuario.value = fila
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'No se pudo cargar la cuenta.'
  } finally {
    cargando.value = false
  }
}

async function toggleAcceso() {
  if (alternando.value) return
  const u = usuario.value.usuario
  const activando = !u.activo
  alternando.value = true
  try {
    await graphqlClient.request(activando ? ACTIVAR_USUARIO : DESACTIVAR_USUARIO, { id: u.id })
    u.activo = activando
    toast.success(activando ? 'Acceso reactivado' : 'Acceso desactivado')
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'No se pudo cambiar el acceso')
  } finally {
    alternando.value = false
  }
}

// Vista de detalle (NO cacheada): se monta y desmonta en cada visita, así que la
// carga va en `onMounted`. `onActivated` solo se dispara en vistas dentro de
// keep-alive (las listas); aquí nunca correría. Mismo patrón que DetalleMiembro.
onMounted(cargar)
</script>
