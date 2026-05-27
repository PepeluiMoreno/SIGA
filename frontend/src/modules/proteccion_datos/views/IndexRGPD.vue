<template>
  <AppLayout
    title="Protección de Datos (RGPD)"
    subtitle="Módulo transversal de cumplimiento RGPD / LOPDGDD">

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-2">

      <router-link
        v-for="card in cards"
        :key="card.to"
        :to="card.to"
        class="block bg-white border border-slate-200 rounded-lg p-5 hover:border-indigo-400 hover:shadow-sm transition-all">
        <div class="flex items-start gap-3">
          <component :is="card.icon" class="w-8 h-8 text-indigo-600 shrink-0" />
          <div class="min-w-0">
            <h3 class="text-sm font-semibold text-slate-900">{{ card.titulo }}</h3>
            <p class="text-xs text-slate-500 mt-1">{{ card.descripcion }}</p>
            <p class="text-[11px] text-indigo-600 font-medium mt-2">{{ card.fase }}</p>
          </div>
        </div>
      </router-link>

    </div>
  </AppLayout>
</template>

<script setup>
import AppLayout from '@/components/common/AppLayout.vue'
import {
  BuildingOffice2Icon,
  ClipboardDocumentListIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  UserIcon,
  ShieldExclamationIcon,
  EyeIcon,
} from '@heroicons/vue/24/outline'

const cards = [
  {
    titulo: 'Encargados del tratamiento',
    descripcion: 'Proveedores que tratan datos por cuenta de la organización (art. 28).',
    fase: 'Fase 1',
    to: '/rgpd/encargados',
    icon: BuildingOffice2Icon,
  },
  {
    titulo: 'Registro de Actividades (RAT)',
    descripcion: 'Inventario formal de tratamientos de datos (art. 30).',
    fase: 'Fase 1',
    to: '/rgpd/actividades',
    icon: ClipboardDocumentListIcon,
  },
  {
    titulo: 'Cláusulas informativas',
    descripcion: 'Textos versionados que se muestran al interesado (art. 13/14).',
    fase: 'Fase 4',
    to: '/rgpd/clausulas',
    icon: DocumentTextIcon,
  },
  {
    titulo: 'Consentimientos',
    descripcion: 'Consentimientos otorgados y retirados (art. 7).',
    fase: 'Fase 4',
    to: '/rgpd/consentimientos',
    icon: CheckCircleIcon,
  },
  {
    titulo: 'Solicitudes de derechos',
    descripcion: 'ARSULIPO: Acceso, Rectificación, Supresión, Limitación, Portabilidad, Oposición (art. 15-22).',
    fase: 'Fase 3',
    to: '/rgpd/solicitudes',
    icon: UserIcon,
  },
  {
    titulo: 'Brechas de seguridad',
    descripcion: 'Incidencias + asistente de notificación AEPD 72 h (art. 33/34).',
    fase: 'Fase 5',
    to: '/rgpd/brechas',
    icon: ShieldExclamationIcon,
  },
  {
    titulo: 'Auditoría de accesos',
    descripcion: 'Log append-only de accesos a datos personales (art. 5.2).',
    fase: 'Fase 6',
    to: '/rgpd/auditoria',
    icon: EyeIcon,
  },
]
</script>
