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


          <!-- Presidencia -->
          <div>
            <h3 class="help-section-title">
              <span class="help-badge bg-purple-100 text-purple-700">Presidencia</span>
            </h3>
            <p class="help-text">
              Cuadro de mando ejecutivo que agrega en una sola pantalla el estado real de la
              organización: acuerdos pendientes, próximas reuniones, composición de la junta
              directiva y convenios próximos a vencer. No requiere entrar en cada módulo —
              la información relevante aparece sola, y las alertas desaparecen cuando el
              problema se resuelve.
            </p>

            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mt-3 mb-1">Flujo de trabajo</p>
            <p class="help-text">
              El cuadro de mando es de solo lectura: recoge datos de Secretaría y Membresía
              y los presenta priorizados. Las <strong>alertas críticas</strong> aparecen automáticamente
              cuando hay actas sin aprobar, acuerdos con plazo vencido, mandatos próximos a
              expirar o convenios sin renovación automática. Desde cada alerta hay un enlace
              directo a la pantalla donde actuar. En <strong>Seguimiento de acuerdos</strong> se puede
              actualizar el estado de ejecución de cualquier acuerdo directamente desde
              presidencia sin ir a secretaría.
            </p>

            <ul class="help-list">
              <li><strong>Cuadro de mando</strong> — alertas automáticas, cuatro indicadores clave
                (socios, acuerdos, reuniones, cargos) y paneles de próximas reuniones y mandatos vigentes.</li>
              <li><strong>Seguimiento de acuerdos</strong> — vista ejecutiva con filtros por estado
                (Pendiente, En curso, Completado, Archivado) y actualización directa.</li>
              <li><strong>Mandatos y cargos</strong> — composición actualizada de los órganos de gobierno,
                con aviso automático cuando un mandato vence en menos de 90 días.</li>
            </ul>
          </div>

          <!-- Secretaría -->
          <div>
            <h3 class="help-section-title">
              <span class="help-badge bg-indigo-100 text-indigo-700">Secretaría</span>
            </h3>
            <p class="help-text">
              Núcleo administrativo y legal de la asociación. Cubre las obligaciones que impone
              la Ley Orgánica 1/2002: Libro de Socios, Libro de Actas, gestión de órganos de
              gobierno y custodia de la documentación institucional.
            </p>

            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mt-3 mb-1">Reuniones — flujo y estados</p>
            <p class="help-text">
              Una reunión es una actividad puntual del órgano de gobierno, no adscrita a
              ninguna campaña. Puede ser <strong>periódica</strong> (la Asamblea General Ordinaria, que se
              celebra una vez al año) o <strong>puntual</strong> (Asamblea Extraordinaria, reunión de Junta,
              Comisión). Cada tipo tiene configurada la antelación mínima de convocatoria y
              los umbrales de quórum según sus estatutos.
            </p>
            <p class="help-text">
              Cada reunión avanza por estos estados en orden:
            </p>
            <ol class="help-list list-decimal">
              <li>
                <strong>Convocada</strong> — se registra fecha, lugar o plataforma telemática, orden del día y,
                si procede, fecha de segunda convocatoria. El sistema acepta asistencia presencial,
                telemática, por representación o excusada.
              </li>
              <li>
                <strong>Celebrada</strong> — se introducen los datos reales: número de socios totales,
                presentes y representados, y qué convocatoria se utilizó. El sistema calcula el quórum
                automáticamente (primera convocatoria: 50% por defecto; segunda: cualquier número).
                Se registran los puntos del orden del día y los acuerdos con su votación
                (mayoría simple, absoluta, dos tercios o unanimidad).
              </li>
              <li>
                <strong>Acta en borrador</strong> — el secretario redacta el acta. En este estado puede
                editarse libremente.
              </li>
              <li>
                <strong>Acta aprobada</strong> — el acta se aprueba en la siguiente reunión del mismo
                órgano, como exige la Ley 1/2002. Se registra la fecha y la reunión en la que
                fue aprobada.
              </li>
            </ol>
            <p class="help-text mt-2">
              Una reunión convocada puede <strong>cancelarse</strong> en cualquier momento antes de celebrarse.
              Las reuniones canceladas quedan en el historial pero no generan acta.
            </p>

            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mt-3 mb-1">Actas — flujo y firma</p>
            <p class="help-text">
              Cada reunión celebrada genera exactamente un acta, numerada correlativamente por
              tipo de órgano y año (por ejemplo, la tercera acta de Junta Directiva de 2025 es
              la nº 3/2025). El flujo es:
            </p>
            <ol class="help-list list-decimal">
              <li><strong>Borrador</strong> — redacción libre, todavía modificable.</li>
              <li><strong>Aprobada</strong> — ratificada en la reunión siguiente, con fecha de aprobación registrada.</li>
              <li><strong>Firmada</strong> — firma del secretario/a con el visto bueno del presidente/a.
                A partir de este estado el acta es documento oficial.</li>
            </ol>
            <p class="help-text mt-2">
              Desde cualquier acta aprobada o firmada se puede emitir un
              <strong>certificado de acuerdo</strong> para presentar ante terceros (bancos, Registro de
              Asociaciones, organismos públicos). Cada certificado recibe una referencia
              automática <em>CERT-AAAA-NNN</em> y lleva la firma del secretario/a con el visto
              bueno del presidente/a.
            </p>

            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mt-3 mb-1">Acuerdos — seguimiento de ejecución</p>
            <p class="help-text">
              Cada acuerdo adoptado en una reunión queda registrado con su resultado de votación
              (aprobado, rechazado, retirado o aplazado) y pasa a un flujo de seguimiento
              independiente para controlar su ejecución:
            </p>
            <ol class="help-list list-decimal">
              <li><strong>Pendiente</strong> — adoptado, aún no iniciado.</li>
              <li><strong>En curso</strong> — en ejecución, con responsable y fecha límite opcionales.</li>
              <li><strong>Completado</strong> — ejecutado satisfactoriamente.</li>
              <li><strong>Archivado</strong> — cerrado sin ejecución (retirado, superseded o sin efecto).</li>
            </ol>
            <p class="help-text mt-2">
              Los acuerdos con plazo vencido se señalan automáticamente en el cuadro de mando
              de presidencia como alerta crítica.
            </p>

            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mt-3 mb-1">Libro de Socios</p>
            <p class="help-text">
              La Ley 1/2002 obliga a mantener un Libro de Socios actualizado y disponible para
              inspección en cualquier momento. En SIGA, el libro se genera bajo demanda: se
              indica una fecha de corte (por defecto hoy) y un motivo (asamblea anual, inspección
              registral, cierre de ejercicio…). El sistema toma el censo en ese instante, registra
              los totales y guarda el snapshot con su fecha de generación. El historial completo
              de todas las generaciones queda disponible para acreditar el censo ante la autoridad
              registral en cualquier fecha pasada.
            </p>

            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mt-3 mb-1">Convenios y delegaciones</p>
            <p class="help-text">
              Registra los acuerdos de colaboración, patrocinios, adhesiones a redes y contratos
              firmados por la asociación, con referencia automática <em>CONV-AAAA-NNN</em>. El sistema
              avisa en el cuadro de mando cuando un convenio está a menos de 60 días de su fecha
              de fin. Los convenios sin renovación automática requieren acción explícita; los que
              tienen renovación automática se señalan para que la dirección confirme o denuncie
              el contrato con el preaviso configurado.
            </p>
            <p class="help-text">
              Las <strong>delegaciones de firma</strong> registran quién está autorizado a actuar en nombre
              de la asociación, para qué actos, con qué límite de importe y durante qué período.
              La revocación de una delegación queda registrada con fecha de efecto. Cada delegación
              puede vincularse al acuerdo de junta que la autoriza.
            </p>
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
