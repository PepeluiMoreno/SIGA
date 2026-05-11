<template>
  <AppLayout title="Ayuda" subtitle="Documentación y soporte">
    <div class="space-y-4">

      <!-- Contacto de soporte -->
      <section class="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div class="px-5 py-3 bg-purple-50 border-b border-purple-100 flex items-center gap-2">
          <PhoneIcon class="w-4 h-4 text-purple-600 flex-shrink-0" />
          <h2 class="text-xs font-bold text-purple-800 uppercase tracking-wide">Servicio de soporte</h2>
        </div>
        <div class="px-5 py-4 flex flex-col sm:flex-row gap-5">
          <div class="flex-1 space-y-3">
            <p class="text-sm text-gray-600 leading-relaxed">
              Si encuentras algún problema, tienes dudas sobre el funcionamiento de la aplicación
              o deseas proponer mejoras, el equipo de soporte está a tu disposición. No dudes en
              contactar — tu opinión es fundamental para seguir mejorando SIGA.
            </p>
            <div class="flex flex-wrap gap-4 pt-1">
              <a href="mailto:soporte@siga.app"
                class="flex items-center gap-2 text-sm text-purple-700 hover:text-purple-900 font-medium transition-colors group">
                <span class="w-7 h-7 rounded-full bg-purple-100 group-hover:bg-purple-200 flex items-center justify-center transition-colors flex-shrink-0">
                  <EnvelopeIcon class="w-3.5 h-3.5 text-purple-600" />
                </span>
                soporte@siga.app
              </a>
              <a href="tel:+34900000000"
                class="flex items-center gap-2 text-sm text-purple-700 hover:text-purple-900 font-medium transition-colors group">
                <span class="w-7 h-7 rounded-full bg-purple-100 group-hover:bg-purple-200 flex items-center justify-center transition-colors flex-shrink-0">
                  <PhoneIcon class="w-3.5 h-3.5 text-purple-600" />
                </span>
                +34 900 000 000
              </a>
            </div>
            <p class="text-xs text-gray-400">Horario de atención: lunes a viernes de 9:00 a 18:00 h</p>
          </div>
          <div class="sm:w-52 bg-purple-50 rounded-lg p-3.5 flex flex-col items-center justify-center text-center gap-1.5 border border-purple-100">
            <ChatBubbleLeftEllipsisIcon class="w-8 h-8 text-purple-400" />
            <p class="text-xs font-semibold text-purple-800">¿Tienes sugerencias?</p>
            <p class="text-xs text-purple-600 leading-tight">
              Tu experiencia de uso nos ayuda a priorizar las mejoras. ¡Cuéntanoslo!
            </p>
          </div>
        </div>
      </section>

      <!-- Documentación -->
      <section class="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div class="px-5 py-3 bg-purple-50 border-b border-purple-100 flex items-center gap-2">
          <BookOpenIcon class="w-4 h-4 text-purple-600 flex-shrink-0" />
          <h2 class="text-xs font-bold text-purple-800 uppercase tracking-wide">Guía de uso</h2>
        </div>
        <div class="px-5 py-5 prose prose-sm prose-gray max-w-none space-y-5">

          <div class="bg-gray-50 border border-gray-100 rounded-lg px-4 py-3">
            <p class="text-sm text-gray-700 leading-relaxed m-0">
              <strong>SIGA</strong> (Sistema de Información para la Gestión de Asociaciones) es una
              plataforma integral diseñada para facilitar la administración de entidades sin ánimo
              de lucro: asociaciones, fundaciones y federaciones. Centraliza en un único entorno
              toda la información sobre personas, actividades, comunicaciones y economía de la organización.
            </p>
          </div>

          <!-- Membresía -->
          <div>
            <h3 class="help-section-title">
              <span class="help-badge bg-violet-100 text-violet-700">Membresía</span>
            </h3>
            <p class="help-text">
              Gestiona el padrón de miembros de la organización: altas, bajas y modificaciones.
              Cada miembro dispone de una ficha detallada con datos personales, de contacto,
              historial de membresía y documentos adjuntos.
            </p>
            <ul class="help-list">
              <li><strong>Lista de miembros</strong> — búsqueda y filtrado avanzado por estado, tipo, agrupación o cualquier dato.</li>
              <li><strong>Ficha de miembro</strong> — acceso a toda la información, historial de cargos, actividades y cuotas.</li>
              <li><strong>Agrupaciones</strong> — estructura territorial o funcional de la entidad (sedes, delegaciones, grupos locales).</li>
            </ul>
          </div>

          <!-- Actividades -->
          <div>
            <h3 class="help-section-title">
              <span class="help-badge bg-blue-100 text-blue-700">Actividades</span>
            </h3>
            <p class="help-text">
              Organiza eventos, talleres, jornadas y grupos de trabajo. Permite registrar
              participantes, llevar el control de asistencia y vincular actividades a miembros o agrupaciones.
            </p>
            <ul class="help-list">
              <li><strong>Eventos</strong> — planificación, inscripción y seguimiento de asistencia.</li>
              <li><strong>Grupos</strong> — comisiones, equipos de trabajo o grupos temáticos con miembros asignados.</li>
            </ul>
          </div>

          <!-- Comunicaciones -->
          <div>
            <h3 class="help-section-title">
              <span class="help-badge bg-teal-100 text-teal-700">Comunicaciones</span>
            </h3>
            <p class="help-text">
              Crea y gestiona campañas de comunicación dirigidas a segmentos específicos de la
              membresía: convocatorias, circulares, boletines o recordatorios de pago.
            </p>
            <ul class="help-list">
              <li><strong>Campañas</strong> — diseño, segmentación de destinatarios y envío de mensajes masivos.</li>
              <li><strong>Seguimiento</strong> — estado de cada campaña y registro de envíos.</li>
            </ul>
          </div>

          <!-- Económico -->
          <div>
            <h3 class="help-section-title">
              <span class="help-badge bg-amber-100 text-amber-700">Económico</span>
            </h3>
            <p class="help-text">
              Módulo financiero adaptado a las necesidades de entidades no lucrativas. Cubre desde
              la gestión de cuotas hasta la contabilidad conforme al Plan General de Contabilidad
              para entidades sin fines lucrativos (RD 1491/2011 para fundaciones).
            </p>
            <ul class="help-list">
              <li><strong>Cuotas</strong> — generación, seguimiento y reclamación de cuotas de membresía.</li>
              <li><strong>Tesorería</strong> — registro de ingresos y gastos, conciliación bancaria.</li>
              <li><strong>Remesas</strong> — generación de ficheros SEPA para domiciliaciones bancarias.</li>
              <li><strong>Presupuesto</strong> — elaboración y seguimiento del presupuesto anual.</li>
              <li><strong>Donaciones</strong> — registro y justificación de donativos.</li>
              <li><strong>Contabilidad</strong> — libro diario y estados financieros (si se activa la contabilidad extendida).</li>
            </ul>
          </div>

          <!-- Administración -->
          <div>
            <h3 class="help-section-title">
              <span class="help-badge bg-slate-100 text-slate-700">Administración</span>
            </h3>
            <p class="help-text">
              Control de acceso basado en roles y permisos. Define quién puede ver y hacer qué
              dentro de la aplicación, adaptándolo a la estructura y responsabilidades de tu organización.
            </p>
            <ul class="help-list">
              <li><strong>Usuarios</strong> — gestión de cuentas, contraseñas y estado de acceso.</li>
              <li><strong>Roles</strong> — creación de perfiles de acceso con permisos granulares por módulo y operación.</li>
            </ul>
          </div>

          <!-- Configuración -->
          <div>
            <h3 class="help-section-title">
              <span class="help-badge bg-rose-100 text-rose-700">Configuración</span>
            </h3>
            <p class="help-text">
              Personaliza SIGA para que refleje la identidad y las particularidades de tu entidad:
              nombre, logotipo, estructura organizativa, denominaciones propias, tema visual y
              parámetros de autenticación.
            </p>
            <ul class="help-list">
              <li><strong>Parámetros generales</strong> — datos de la organización, sede social, redes sociales y apariencia.</li>
              <li><strong>Catálogos</strong> — tipos de miembro, estados, motivos de baja y demás tablas de referencia.</li>
            </ul>
          </div>

          <!-- Invitación a sugerencias -->
          <div class="bg-purple-50 border border-purple-100 rounded-lg px-4 py-3.5 mt-2">
            <p class="text-sm text-purple-900 leading-relaxed m-0">
              <strong>¿Echamos algo en falta?</strong> SIGA es un proyecto en evolución continua.
              Si detectas algo que no funciona como esperas, o tienes ideas para mejorarlo,
              por favor contacta con el servicio de soporte — cada sugerencia se evalúa y
              las más valoradas se incorporan en las próximas versiones.
            </p>
          </div>

        </div>
      </section>

    </div>
  </AppLayout>
</template>

<script setup>
import AppLayout from '@/components/common/AppLayout.vue'
import { PhoneIcon, EnvelopeIcon, BookOpenIcon, ChatBubbleLeftEllipsisIcon } from '@heroicons/vue/24/outline'
</script>

<style scoped>
.help-section-title {
  @apply flex items-center gap-2 mb-1.5 mt-0;
}
.help-badge {
  @apply inline-block text-xs font-bold uppercase tracking-wide px-2.5 py-0.5 rounded-full;
}
.help-text {
  @apply text-sm text-gray-600 leading-relaxed mb-2;
}
.help-list {
  @apply space-y-0.5 pl-4 list-disc text-sm text-gray-600;
}
.help-list li {
  @apply leading-relaxed;
}
</style>
