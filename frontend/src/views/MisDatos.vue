<template>
  <AppLayout title="Mis datos" subtitle="Tu perfil y datos personales en la organización">

    <EstadoCarga v-if="cargando" mensaje="Cargando tu perfil…" />

    <div v-else class="page-body">
      <div v-if="!perfil?.miembroId"
        class="card px-5 py-4 text-sm text-slate-500">
        Cuenta {{ perfil?.tipoVinculacionNombre || 'sin tipo' }}. No requiere membresía.
      </div>

      <template v-else>
        <MiembroDetail
          :miembro-id-prop="perfil.miembroId"
          :modo-propio="true"
        />

        <!-- Historial de vinculaciones: la trayectoria del socio con la asociación -->
        <section v-if="vinculaciones.length" class="card px-5 py-4 mt-4">
          <h2 class="text-sm font-semibold text-slate-700 mb-3">Mi historial de vinculaciones</h2>
          <ul class="divide-y divide-slate-100 text-sm">
            <li v-for="v in vinculaciones" :key="v.id" class="py-2 flex items-center justify-between">
              <span class="font-medium text-slate-800">{{ v.tipoVinculacion ? v.tipoVinculacion.nombre : '—' }}</span>
              <span class="text-xs text-slate-500">
                {{ v.fechaInicio || '?' }} → {{ v.fechaFin || 'vigente' }}
                <span class="ml-1 text-slate-400">({{ v.estado }})</span>
              </span>
            </li>
          </ul>
        </section>
      </template>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import MiembroDetail from '@/components/miembros/MiembroDetail.vue'
import { graphqlClient } from '@/graphql/client.js'
import { VINCULACIONES_DE_CONTACTO } from '@/graphql/queries/contactos.js'

const MI_PERFIL = `
  query MiPerfil {
    miPerfil {
      id email activo ultimoAcceso
      miembroId tipoVinculacionId tipoVinculacionNombre entidadVinculacion
    }
  }
`

const cargando = ref(true)
const perfil   = ref(null)
const vinculaciones = ref([])

onMounted(async () => {
  try {
    const data = await graphqlClient.request(MI_PERFIL)
    perfil.value = data.miPerfil
    if (perfil.value?.miembroId) {
      const vd = await graphqlClient.request(VINCULACIONES_DE_CONTACTO, { contactoId: perfil.value.miembroId })
      vinculaciones.value = vd.vinculacionesDeContacto || []
    }
  } finally {
    cargando.value = false
  }
})
</script>
