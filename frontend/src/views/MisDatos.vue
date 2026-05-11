<template>
  <AppLayout title="Mis datos" subtitle="Tu perfil y datos personales en la organización">

    <div v-if="cargando" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>

    <template v-else>
      <div v-if="!perfil?.miembroId"
        class="rounded-xl border border-slate-200 bg-slate-50 px-5 py-4 text-sm text-slate-500">
        Cuenta {{ perfil?.tipoVinculacionNombre || 'sin tipo' }}. No requiere membresía.
      </div>

      <MiembroDetail
        v-else
        :miembro-id-prop="perfil.miembroId"
        :modo-propio="true"
      />
    </template>

  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import MiembroDetail from '@/components/miembros/MiembroDetail.vue'
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
