<template>
  <AppLayout title="Mis datos" subtitle="Tu perfil y datos personales en la organización">

    <EstadoCarga v-if="cargando" mensaje="Cargando tu perfil…" />

    <div v-else class="page-body">
      <div v-if="!perfil?.miembroId"
        class="card px-5 py-4 text-sm text-slate-500">
        Cuenta {{ perfil?.tipoVinculacionNombre || 'sin tipo' }}. No requiere membresía.
      </div>

      <template v-else>
        <DetalleMiembro
          :miembro-id-prop="perfil.miembroId"
          :modo-propio="true"
        />

        <!-- Trayectoria del socio (componente reutilizable, también en ficha admin y Junta) -->
        <HistorialVinculaciones
          :contacto-id="perfil.miembroId"
          titulo="Mi historial de vinculación"
          class="card px-5 py-4 mt-4"
        />
      </template>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import EstadoCarga from '@/components/common/EstadoCarga.vue'
import DetalleMiembro from '@/components/miembros/DetalleMiembro.vue'
import HistorialVinculaciones from '@/components/miembros/HistorialVinculaciones.vue'
import { graphqlClient } from '@/graphql/client.js'

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

onMounted(async () => {
  try {
    const data = await graphqlClient.request(MI_PERFIL)
    perfil.value = data.miPerfil
  } finally {
    cargando.value = false
  }
})
</script>
