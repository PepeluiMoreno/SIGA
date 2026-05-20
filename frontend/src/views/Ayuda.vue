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

            <!-- Detalle por flujo de trabajo -->
            <details class="help-detail mt-3">
              <summary class="help-detail-summary">
                Flujo · Cuotas del ejercicio (configuración y generación)
              </summary>
              <div class="help-detail-body">
                <p class="help-text">
                  Cada ejercicio se decide cuánto pagan los socios. SIGA usa un modelo simple:
                  una <strong>cuota base</strong> única para el año, con rebajas opcionales según el tipo
                  de socio (joven, jubilado, en paro, honorífico…) modeladas como porcentajes de reducción.
                </p>

                <p class="help-subtitle">Paso 1 — Catálogo de motivos de reducción</p>
                <p class="help-text">
                  En <em>Configuración → Catálogos → Motivos de reducción de cuota</em>, define las
                  rebajas posibles (código, nombre, porcentaje 0–100). Reglas:
                </p>
                <ul class="help-list">
                  <li>
                    Un motivo con <strong>%≥100</strong> (por ejemplo <em>HONOR</em>) significa que los socios
                    con ese tipo no pagan cuota: el sistema NO genera <em>CuotaAnual</em> para ellos.
                  </li>
                  <li>
                    Una vez se haya emitido al menos un recibo con cuotas que usan un motivo, su
                    <strong>porcentaje queda congelado</strong>. La razón: lo emitido al socio debe coincidir
                    con la rebaja registrada; cambiarla retroactivamente rompe la trazabilidad. Para alterar
                    la rebaja de un socio concreto: anula su cuota, cámbiale el motivo (cambiando su
                    TipoMiembro) y re-emite.
                  </li>
                </ul>

                <p class="help-subtitle">Paso 2 — Asignar motivo al tipo de miembro</p>
                <p class="help-text">
                  En <em>Configuración → Catálogos → Tipos de miembro</em>, cada tipo lleva un selector
                  <strong>"Motivo de reducción"</strong>. Si lo dejas vacío, los miembros de ese tipo pagan
                  la cuota base completa.
                </p>

                <p class="help-subtitle">Paso 3 — Configurar la cuota base del ejercicio</p>
                <p class="help-text">
                  En <em>Económico → Cuotas del ejercicio</em>, panel izquierdo:
                </p>
                <ol class="help-list-ord">
                  <li>Selecciona el ejercicio.</li>
                  <li>Indica el <strong>importe base</strong> (lo que paga un socio sin reducción).</li>
                  <li>Opcionalmente clona del año anterior como punto de partida.</li>
                  <li>Pulsa <strong>Guardar configuración</strong>.</li>
                </ol>

                <p class="help-subtitle">Paso 4 — Previsualizar y generar las cuotas</p>
                <p class="help-text">
                  En el panel derecho de la misma pantalla:
                </p>
                <ol class="help-list-ord">
                  <li>
                    Verás un desglose por tipo de miembro con el número de socios, el importe unitario
                    tras aplicar la reducción y el total esperado. Los tipos con motivo del 100% aparecen
                    listados aparte como <em>excluidos</em>.
                  </li>
                  <li>
                    Si ya hay cuotas creadas para ese ejercicio, te aparecerá el número y se saltarán en
                    el siguiente paso (idempotencia: nunca duplica cuotas).
                  </li>
                  <li>
                    Pulsa <strong>Generar cuotas del ejercicio</strong>. Se crea una <em>CuotaAnual</em>
                    en estado <em>Pendiente</em> por cada socio activo. A partir de aquí, esas cuotas son
                    la entrada del flujo de emisión de recibos y de generación de remesa.
                  </li>
                </ol>

                <p class="help-subtitle">Permisos</p>
                <p class="help-text">
                  Las acciones de configurar el ejercicio, gestionar motivos y generar cuotas están
                  reservadas al <strong>tesorero de la organización matriz</strong>. Los tesoreros de
                  agrupación pueden consultar pero no modificar el catálogo común.
                </p>
              </div>
            </details>

            <details class="help-detail mt-3">
              <summary class="help-detail-summary">
                Flujo · Emisión de recibos (paso previo a la remesa)
              </summary>
              <div class="help-detail-body">
                <p class="help-text">
                  Tras generar las cuotas del ejercicio, el siguiente paso es <strong>emitir los recibos
                  formales</strong> a cada socio. El recibo es el documento numerado que justifica el
                  cobro: lleva un correlativo (<span class="font-mono">REC-{prefijo}-AAAA-NNNNN</span>),
                  el concepto, el importe y el estado. Es la pieza que se incluye en la remesa SEPA o
                  que el tesorero descarga en PDF si el socio pide un duplicado.
                </p>

                <p class="help-subtitle">Procedimiento recomendado</p>
                <ol class="help-list-ord">
                  <li><strong>Emite el lote</strong> a primeros del año, una vez configuradas las cuotas.</li>
                  <li><strong>Revisa y corrige</strong> durante el periodo que necesites: anular recibos erróneos,
                      marcar como cobrados los que ya pagaron por transferencia, etc.</li>
                  <li><strong>Genera la remesa SEPA</strong> cuando los recibos estén listos. La remesa toma los
                      recibos en estado <em>EMITIDO</em> con modo de cobro SEPA cuyas cuotas siguen Pendiente.</li>
                </ol>

                <p class="help-subtitle">Paso 1 — Emitir el lote</p>
                <p class="help-text">
                  Ve a <em>Económico → Recibos</em>, pulsa <strong>+ Emitir lote</strong> e indica:
                </p>
                <ul class="help-list">
                  <li><strong>Ejercicio</strong>: el año al que corresponden los recibos.</li>
                  <li><strong>Tipo</strong>: Cuota ordinaria (lo habitual) o Extraordinaria (derrama, congresal).</li>
                  <li><strong>Concepto</strong>: texto libre que aparecerá en el recibo y en el cargo bancario.</li>
                  <li><strong>Fecha de vencimiento</strong>: opcional, para marcar plazo de pago.</li>
                </ul>
                <p class="help-text">
                  El sistema crea un recibo por cada cuota Pendiente del ejercicio que aún no tenga
                  recibo. Es <strong>idempotente</strong>: si lanzas el lote dos veces, no se duplican.
                </p>

                <p class="help-subtitle">Paso 2 — Revisar y actuar sobre cada recibo</p>
                <p class="help-text">
                  En el listado puedes filtrar por ejercicio, tipo, estado o buscar por nombre/email. Al
                  hacer clic en una fila se abre el detalle con cuatro acciones disponibles según el estado:
                </p>
                <ul class="help-list">
                  <li>
                    <strong>↓ PDF</strong>: descarga el recibo (resguardo A5 estilo bancario) para
                    imprimirlo o adjuntarlo a un email manual.
                  </li>
                  <li>
                    <strong>Marcar cobrado</strong>: solo si el recibo no está cobrado ni anulado. Indica
                    el modo (transferencia, efectivo, tarjeta…) y la fecha del cobro. Se genera el apunte
                    de caja y el asiento contable correspondientes.
                  </li>
                  <li>
                    <strong>Enviar al socio</strong>: envía el PDF por email usando una plantilla del
                    módulo de Comunicación Interna. Requiere que el administrador haya creado una
                    plantilla con módulo <em>económico</em>.
                  </li>
                  <li>
                    <strong>Anular</strong>: deja el recibo en estado <em>ANULADO</em> y la cuota vuelve
                    a Pendiente (si era una cuota ordinaria). Se solicita un motivo. No disponible para
                    recibos ya cobrados.
                  </li>
                </ul>

                <p class="help-subtitle">Paso 3 — Generar la remesa SEPA</p>
                <p class="help-text">
                  Cuando los recibos estén revisados, ve a <em>Económico → Remesas</em> y crea una
                  nueva remesa Ordinaria. El sistema incluirá los recibos EMITIDO con modo SEPA y
                  cuotas Pendientes (ver el flujo "Generación y envío de remesa SEPA").
                </p>

                <p class="help-subtitle">Códigos que verás</p>
                <p class="help-text">
                  El número de recibo lleva el prefijo de tu agrupación territorial cuando la
                  organización es descentralizada (<span class="font-mono">REC-MAD-2025-00042</span>) o
                  un formato simple si la tesorería es central (<span class="font-mono">REC-2025-00042</span>).
                  La secuencia se reinicia cada ejercicio dentro de cada serie.
                </p>
              </div>
            </details>

            <details class="help-detail mt-3">
              <summary class="help-detail-summary">
                Flujo · Donaciones (registro, cobro y certificado fiscal)
              </summary>
              <div class="help-detail-body">
                <p class="help-text">
                  La entidad puede recibir <strong>donaciones</strong> de socios o de terceros, en
                  dinero o en bienes (donaciones en especie). Por estar acogida al régimen de la
                  <strong>Ley 49/2002</strong> (entidades sin fines lucrativos), las donaciones son
                  deducibles para el donante en su IRPF (personas físicas) o Impuesto de Sociedades
                  (personas jurídicas), siempre que la entidad emita el correspondiente
                  <strong>certificado anual</strong>.
                </p>

                <p class="help-subtitle">Diferencia con cuotas y subvenciones</p>
                <ul class="help-list">
                  <li><strong>Cuotas</strong> — obligación periódica del socio. Van por el flujo de recibos y remesas.</li>
                  <li><strong>Donaciones</strong> — aportación voluntaria sin contraprestación. Van por este flujo.</li>
                  <li><strong>Subvenciones</strong> — fondos públicos o privados con destino específico. Se registran directamente como apunte de caja en tesorería (pendiente flujo dedicado).</li>
                </ul>

                <p class="help-subtitle">Tipos de donación (clave fiscal)</p>
                <ul class="help-list">
                  <li><strong>A · Dineraria</strong> — dinero (transferencia, efectivo, Bizum, tarjeta…). Importe = lo entregado.</li>
                  <li><strong>B · En especie</strong> — bienes (equipos informáticos, libros, mobiliario…). Requiere descripción del bien y valoración (tasación) documentada.</li>
                </ul>

                <p class="help-subtitle">Procedimiento — Registrar una donación</p>
                <ol class="help-list-ord">
                  <li>Ve a <em>Económico → Donaciones</em> y pulsa <strong>+ Nueva donación</strong>.</li>
                  <li>
                    Elige el <strong>tipo</strong> (Dineraria / En especie) y el <strong>donante</strong>:
                    <ul class="help-list">
                      <li><strong>Socio</strong> — selecciónalo del desplegable; su NIF se toma de la ficha.</li>
                      <li><strong>Externo</strong> — rellena nombre y NIF (este último es imprescindible si se quiere certificar fiscalmente).</li>
                      <li><strong>Anónima</strong> — marca la casilla; no se podrá certificar pero sí queda registrada.</li>
                    </ul>
                  </li>
                  <li>
                    Indica el <strong>importe</strong> (dineraria) o la <strong>valoración + descripción del bien</strong> (especie).
                    En especie es muy recomendable adjuntar la URL del documento de tasación.
                  </li>
                  <li>
                    Selecciona el <strong>concepto</strong> o campaña asociada (si la donación se enmarca en una recogida de fondos concreta).
                  </li>
                  <li>
                    Si el dinero ya está en la cuenta, marca <strong>"Cobrar al guardar"</strong> y selecciona la
                    cuenta bancaria de destino. Es el caso del 80% de las donaciones (D6.2).
                  </li>
                  <li>
                    Confirma. La donación queda en estado <em>REGISTRADA</em>, y si has cobrado en el acto, pasa a
                    <em>COBRADA</em> generando automáticamente el apunte de tesorería y el asiento contable
                    Debe <span class="font-mono">572 (Bancos)</span> /
                    Haber <span class="font-mono">730 (Ingresos por donaciones)</span>.
                  </li>
                </ol>

                <p class="help-subtitle">Procedimiento — Marcar como cobrada (si quedó REGISTRADA)</p>
                <p class="help-text">
                  Abre el detalle de la donación y pulsa <strong>Marcar cobrada</strong>. Indica cuenta bancaria
                  (solo dineraria) y fecha de cobro real. Se generan el apunte y el asiento descritos arriba.
                </p>

                <p class="help-subtitle">Procedimiento — Emitir certificados anuales (enero)</p>
                <p class="help-text">
                  En enero, antes de presentar el Modelo 182 a la AEAT, hay que emitir los certificados anuales
                  para los donantes (Ley 49/2002 art. 24).
                </p>
                <ol class="help-list-ord">
                  <li>En <em>Donaciones</em> pulsa <strong>Emitir certificados anuales…</strong>.</li>
                  <li>
                    Selecciona el ejercicio. El sistema agrupa por <strong>(NIF + tipo)</strong> — si un mismo
                    donante hizo aportaciones dinerarias y en especie, recibirá dos certificados separados
                    (clave A y clave B).
                  </li>
                  <li>
                    Para cada donante listado pulsa <strong>Emitir PDF</strong>. Se descarga un PDF firmable
                    con número correlativo <span class="font-mono">CERT-AAAA-NNNNN</span> conforme a la
                    Ley 49/2002 art. 24. Las donaciones quedan marcadas como certificadas en el sistema.
                  </li>
                  <li>
                    Envía el PDF al donante (manualmente o, en el futuro, vía módulo de Comunicación Interna).
                  </li>
                </ol>

                <p class="help-subtitle">Donaciones anulables</p>
                <p class="help-text">
                  Si una donación se anula (devolución por error, retirada del donante…), abre su detalle y
                  pulsa <strong>Anular</strong>. Si tenía asiento contable generado, queda en estado anulado
                  (no se borra, se mantiene la trazabilidad).
                </p>

                <p class="help-subtitle">Estados de la donación</p>
                <ul class="help-list">
                  <li><strong>REGISTRADA</strong> — compromiso anotado, dinero aún no recibido.</li>
                  <li><strong>COBRADA</strong> — dinero (o bien) ya en la entidad, con apunte y asiento contable.</li>
                  <li><strong>ANULADA</strong> — donación anulada, asiento revertido si procede.</li>
                </ul>

                <p class="help-subtitle">Permisos</p>
                <p class="help-text">
                  El rol <strong>tesorero</strong> tiene los permisos
                  <span class="font-mono">DON_LIST</span>,
                  <span class="font-mono">DON_CREATE</span> y
                  <span class="font-mono">DON_CERT</span>. La emisión de certificados es función exclusiva
                  del tesorero (D6.4).
                </p>

                <p class="help-subtitle">¿Y los donativos recurrentes?</p>
                <p class="help-text">
                  Las donaciones periódicas con domiciliación SEPA (un donante que aporta X € al mes) están
                  previstas para la próxima versión: el modelo ya contempla el campo <em>carácter
                  RECURRENTE</em> pero todavía no se generan cargos automáticos. Mientras, regístralas
                  manualmente cuando lleguen.
                </p>
              </div>
            </details>

            <details class="help-detail mt-3">
              <summary class="help-detail-summary">
                Flujo · Modelo 182 (declaración fiscal de donaciones)
              </summary>
              <div class="help-detail-body">
                <p class="help-text">
                  El <strong>Modelo 182</strong> es la declaración informativa anual que la entidad
                  presenta a la AEAT con todas las donaciones recibidas. Sin esta declaración, los
                  donantes pierden la deducción en IRPF/IS y la entidad incumple su obligación fiscal
                  (Ley 49/2002 art. 24, art. 198 LGT — sanción 200–20.000 €).
                </p>

                <p class="help-subtitle">Plazo</p>
                <p class="help-text">
                  Enero del año siguiente al del ejercicio declarado. Por ejemplo, las donaciones de
                  2025 se declaran en enero de 2026.
                </p>

                <p class="help-subtitle">Qué se declara</p>
                <p class="help-text">
                  Solo las donaciones con donante <strong>identificable fiscalmente</strong>: las que
                  tienen NIF (del miembro o externo) y no son anónimas. El sistema agrega
                  automáticamente por NIF y deduce si es persona física (DNI, NIE) o jurídica (CIF).
                </p>

                <p class="help-subtitle">Procedimiento</p>
                <ol class="help-list-ord">
                  <li>Ve a <em>Económico → Modelo 182</em>.</li>
                  <li>
                    Selecciona el ejercicio. El sistema calcula al vuelo el agregado y muestra:
                    donantes incluibles, donaciones excluidas (con motivo) e importe total.
                  </li>
                  <li>
                    Si hay donaciones excluidas y puedes completar el NIF que les falta, hazlo en la
                    ficha de la donación o del miembro y pulsa <strong>Recalcular</strong>.
                  </li>
                  <li>
                    Pulsa <strong>↓ Fichero AEAT (TXT)</strong>. Se descarga el fichero en formato
                    posicional ISO-8859-1 listo para subir a la sede electrónica de la AEAT.
                  </li>
                  <li>
                    Opcionalmente descarga el <strong>↓ PDF resumen</strong> para archivo interno y
                    revisión por la junta.
                  </li>
                  <li>Sube el TXT a la sede electrónica de la AEAT y recibe el acuse de recibo.</li>
                  <li>
                    Vuelve a SIGA, pulsa <strong>Registrar presentación</strong> e introduce: fecha de
                    envío, código que devuelve la AEAT y opcionalmente la URL del PDF del acuse.
                    Queda registrado en el histórico.
                  </li>
                </ol>

                <p class="help-subtitle">Permisos</p>
                <p class="help-text">
                  La generación y el registro de presentaciones del Modelo 182 son del rol
                  <strong>tesorero</strong>. El AUDITOR puede consultar el histórico.
                </p>
              </div>
            </details>

            <details class="help-detail mt-3">
              <summary class="help-detail-summary">
                Flujo · Cuentas Anuales (Memoria, aprobación y depósito)
              </summary>
              <div class="help-detail-body">
                <p class="help-text">
                  Tras cerrar contablemente el ejercicio (flujo Cierre), hay que preparar las
                  <strong>Cuentas Anuales</strong>: el documento legal que recoge el Balance, la
                  Cuenta de Resultados y la Memoria económica del año, y que se deposita ante el
                  organismo competente (Protectorado para fundaciones, Registro de Asociaciones para
                  asociaciones, Tribunal de Cuentas para partidos políticos).
                </p>

                <p class="help-subtitle">Los tres documentos</p>
                <ol class="help-list-ord">
                  <li>
                    <strong>Balance PCESFL</strong> — estructura oficial (Activo / Pasivo y Patrimonio
                    Neto) según el Plan Contable de Entidades Sin Fines Lucrativos. El sistema lo
                    calcula automáticamente del ejercicio cerrado.
                  </li>
                  <li>
                    <strong>Cuenta de Resultados</strong> — formato Excedente PCESFL (no "Beneficio"):
                    ingresos − gastos = excedente del ejercicio. También se calcula automáticamente.
                  </li>
                  <li>
                    <strong>Memoria económica</strong> — los <b>12 apartados obligatorios</b> según
                    RD 1491/2011 norma 4ª. Cada apartado es texto libre con datos del ejercicio. Es
                    la parte más larga: la redacta el tesorero apartado a apartado.
                  </li>
                </ol>

                <p class="help-subtitle">Procedimiento</p>
                <ol class="help-list-ord">
                  <li>Ve a <em>Económico → Cuentas Anuales</em>.</li>
                  <li>
                    Selecciona el ejercicio cerrado y pulsa <strong>+ Generar CCAA del ejercicio</strong>.
                    El sistema toma una foto del balance y la cuenta de resultados y crea las CCAA
                    en estado <em>BORRADOR</em>.
                  </li>
                  <li>
                    Entra en el detalle y rellena los <strong>12 apartados de la Memoria</strong>.
                    Cada apartado lleva una guía sobre qué incluir según el PCESFL. Puedes guardar
                    apartado por apartado.
                  </li>
                  <li>
                    Cuando esté completo, la <strong>junta directiva lo aprueba en acta</strong>. El
                    presidente/vicepresidente registra la aprobación con la referencia del acta.
                    Estado pasa a <em>APROBADAS</em>; el contenido queda inmutable.
                  </li>
                  <li>
                    El tesorero o secretario lleva las CCAA al registro competente y, al recibir el
                    acuse, lo registra en SIGA con la fecha de depósito y la URL del PDF. Estado pasa
                    a <em>DEPOSITADAS</em>.
                  </li>
                  <li>
                    Puedes descargar el documento en <strong>PDF</strong> en cualquier momento
                    (estado BORRADOR, APROBADAS o DEPOSITADAS) — incluye portada, Balance, Cuenta de
                    Resultados y los 12 apartados de la Memoria.
                  </li>
                </ol>

                <p class="help-subtitle">Permisos</p>
                <ul class="help-list">
                  <li><strong>Tesorero</strong>: prepara la Memoria, lleva las CCAA al registro y registra el depósito.</li>
                  <li><strong>Presidente / Vicepresidente</strong>: aprueba en nombre de la junta.</li>
                  <li><strong>Secretario</strong>: alternativamente puede registrar el depósito.</li>
                  <li>Auditor: solo lectura.</li>
                </ul>

                <p class="help-subtitle">Reapertura excepcional</p>
                <p class="help-text">
                  Si se detecta un error material en las CCAA aprobadas o depositadas, el tesorero
                  puede <strong>reabrirlas</strong> con un motivo justificado. Vuelven a BORRADOR y
                  hay que recorrer otra vez el flujo. Es excepcional — Ley 50/2002 sanciona la
                  reformulación injustificada.
                </p>
              </div>
            </details>

            <details class="help-detail mt-3">
              <summary class="help-detail-summary">
                Flujo · Cierre de ejercicio (regularización → cierre → apertura)
              </summary>
              <div class="help-detail-body">
                <p class="help-text">
                  Cada año, una vez registrados todos los movimientos del ejercicio, hay que
                  <strong>cerrar contablemente</strong> el año. Es un acto formal: tras él, los
                  asientos del ejercicio quedan inmutables y el sistema arrastra los saldos al
                  ejercicio siguiente. Sin cierre no se pueden depositar las cuentas anuales.
                </p>

                <p class="help-subtitle">Pre-requisitos antes de cerrar</p>
                <ul class="help-list">
                  <li>Todos los asientos del ejercicio en estado <em>CONFIRMADO</em> (sin borradores).</li>
                  <li>Balance cuadrado (Σ debe = Σ haber).</li>
                  <li>Conciliación bancaria completa: ningún apunte sin emparejar con su línea del extracto.</li>
                </ul>

                <p class="help-subtitle">Las tres acciones del cierre</p>
                <ol class="help-list-ord">
                  <li>
                    <strong>Asiento de regularización</strong> — salda las cuentas de gastos (grupo 6)
                    e ingresos (grupo 7) contra la cuenta <span class="font-mono">129 Excedente del
                    ejercicio</span>. Tras este asiento, el excedente queda calculado.
                  </li>
                  <li>
                    <strong>Asiento de cierre</strong> — cierra el balance saldando todas las cuentas
                    de activo, pasivo y patrimonio neto. El ejercicio queda <em>cerrado e inmutable</em>:
                    no se pueden añadir, modificar ni anular asientos en ese año.
                  </li>
                  <li>
                    <strong>Asiento de apertura</strong> del ejercicio siguiente — abre el año nuevo
                    con los saldos del balance arrastrados del ejercicio que se acaba de cerrar.
                  </li>
                </ol>

                <p class="help-subtitle">Procedimiento</p>
                <ol class="help-list-ord">
                  <li>Ve a <em>Económico → Cierre del ejercicio</em>.</li>
                  <li>
                    Mira el <strong>checklist</strong>: te indica qué pasos están hechos y cuáles
                    bloqueantes faltan. Si hay puntos en rojo, resuélvelos antes de continuar
                    (confirmar borradores, completar conciliación).
                  </li>
                  <li>Pulsa <strong>1. Generar regularización</strong>.</li>
                  <li>Pulsa <strong>2. Generar cierre</strong>.</li>
                  <li>Pulsa <strong>3. Generar apertura</strong> del ejercicio siguiente.</li>
                  <li>
                    Descarga el <strong>Libro Diario</strong> y revisa el <strong>Balance PCESFL</strong>
                    y la <strong>Cuenta de Resultados</strong> que el sistema calcula. Son los
                    documentos base para preparar las Cuentas Anuales que se depositan ante el
                    Protectorado o el Tribunal de Cuentas.
                  </li>
                </ol>

                <p class="help-subtitle">Permisos</p>
                <p class="help-text">
                  La ejecución del cierre está reservada al <strong>tesorero de la matriz</strong>.
                  Los tesoreros de agrupación pueden consultar el estado, los documentos y el balance,
                  pero no ejecutar los asientos. El rol AUDITOR tiene acceso de solo lectura.
                </p>
              </div>
            </details>

            <details class="help-detail mt-3">
              <summary class="help-detail-summary">
                Flujo · Conciliación bancaria
              </summary>
              <div class="help-detail-body">
                <p class="help-text">
                  Cada mes hay que comprobar que el saldo de la cuenta corriente en SIGA coincide
                  exactamente con el saldo real del banco. Para eso se concilia: se empareja cada
                  apunte registrado en SIGA con la línea correspondiente del extracto bancario.
                </p>

                <p class="help-subtitle">Cómo se hace</p>
                <ol class="help-list-ord">
                  <li>Ve a <em>Económico → Conciliación bancaria</em>.</li>
                  <li>Selecciona la cuenta bancaria que quieres conciliar.</li>
                  <li>
                    Importa el extracto: descarga del portal del banco un fichero en formato
                    <strong>Norma 43</strong> (típicamente <span class="font-mono">.Q43</span>) o
                    en <strong>CSV</strong> con columnas <em>fecha, importe, concepto, referencia</em>,
                    y súbelo con los botones <strong>↑ Importar Norma 43</strong> o
                    <strong>↑ Importar CSV</strong>.
                  </li>
                  <li>
                    Verás dos columnas lado a lado: <strong>apuntes del sistema</strong> pendientes
                    de conciliar (izquierda) y <strong>líneas del extracto</strong> bancario (derecha).
                  </li>
                  <li>
                    Selecciona un apunte y la línea del extracto que le corresponde, comprueba que
                    los importes cuadran y pulsa <strong>Emparejar →</strong>. Los dos quedan
                    marcados como conciliados.
                  </li>
                  <li>
                    Repite hasta que no queden líneas pendientes en ninguna de las dos columnas. Si
                    una línea no tiene contrapartida, investiga (puede ser una comisión que aún no
                    has registrado, o un cobro que aún no ha llegado al banco).
                  </li>
                </ol>

                <p class="help-subtitle">Cierre mensual</p>
                <p class="help-text">
                  Cuando hayas emparejado todo el mes, confirma la conciliación del período (saldo
                  inicial + movimientos = saldo final). Eso firma ese mes y deja el control en
                  positivo para auditoría.
                </p>

                <p class="help-subtitle">Importante: bloqueo en el cierre de ejercicio</p>
                <p class="help-text">
                  No puedes cerrar el ejercicio anual si quedan apuntes sin conciliar. Es un requisito
                  legal (PCESFL norma 9ª — imagen fiel). Antes del cierre, asegúrate de conciliar todos
                  los meses del año.
                </p>

                <p class="help-subtitle">Open Banking (opcional)</p>
                <p class="help-text">
                  En <em>Parámetros Generales → Funcionalidades</em> puedes activar
                  <strong>Conciliación bancaria automática (Open Banking)</strong>. Si está
                  habilitada, el sistema descarga los movimientos del banco automáticamente vía
                  API PSD2 (Enable Banking) — el tesorero no tiene que descargar ningún fichero. El
                  emparejamiento entre apuntes y líneas sigue siendo manual en ambos casos. (Integración
                  Enable Banking en desarrollo; mientras tanto, la importación manual de Norma 43 / CSV
                  funciona siempre.)
                </p>
              </div>
            </details>

            <details class="help-detail mt-3">
              <summary class="help-detail-summary">
                Flujo · Justificantes de gasto (tres firmas)
              </summary>
              <div class="help-detail-body">
                <p class="help-text">
                  Cualquier miembro que haya pagado algo en nombre de la organización (taxi, dieta,
                  alquiler de material, ticket de un evento, etc.) presenta un justificante de gasto. Antes
                  de cobrarlo, el justificante recorre <strong>tres firmas</strong>: la persona que lo presenta,
                  el responsable de la actividad a la que se imputa y el tesorero.
                </p>

                <p class="help-subtitle">Las tres firmas</p>
                <ul class="help-list">
                  <li>
                    <strong>Presentar</strong> (cualquier miembro activo): rellenas concepto, importe, fecha
                    del gasto y la actividad a la que se imputa. Opcionalmente adjuntas la factura/ticket
                    (recomendado, pero no obligatorio en la primera versión).
                  </li>
                  <li>
                    <strong>Aceptar</strong> (responsable de la actividad): confirma que ese gasto se
                    realizó realmente para esa actividad. No estás aprobando el pago, solo dando luz verde
                    para que el tesorero lo evalúe.
                  </li>
                  <li>
                    <strong>Aprobar</strong> (tesorero central o del ámbito): revisa la factura y el importe,
                    y da el visto bueno final. Cuando se paga, registra la cuenta de origen, el modo y
                    la fecha. Se genera el apunte de caja y el asiento contable automáticamente.
                  </li>
                </ul>

                <p class="help-subtitle">Procedimiento de presentación</p>
                <ol class="help-list-ord">
                  <li>Ve a <em>Mis datos → Datos económicos → Justificantes de gasto</em>.</li>
                  <li>Pulsa <strong>+ Presentar gasto</strong>.</li>
                  <li>
                    Selecciona la <strong>actividad</strong> a la que se imputa el gasto.
                  </li>
                  <li>
                    Elige la <strong>categoría de gasto</strong>: la cuenta contable del plan PCESFL del
                    grupo 6 a la que se imputa (e.g. <span class="font-mono">621</span> Arrendamientos,
                    <span class="font-mono">624</span> Transportes, <span class="font-mono">626</span>
                    Servicios bancarios, <span class="font-mono">629</span> Otros servicios). Es
                    obligatorio (D7.7) — si dudas, pregunta al tesorero.
                  </li>
                  <li>
                    Indica el <strong>concepto</strong>, el <strong>importe</strong> y la
                    <strong>fecha</strong> del gasto. Si tienes la factura escaneada, pega su URL.
                  </li>
                  <li>
                    Pulsa <strong>Presentar</strong>. El justificante queda en estado
                    <em>PRESENTADO</em> y el responsable de la actividad debe revisarlo.
                  </li>
                </ol>

                <p class="help-subtitle">Atajo para tesoreros: presentar a petición del socio</p>
                <p class="help-text">
                  Si eres tesorero y un socio te trae una factura en persona (no tiene acceso a la app
                  o prefiere que tú la registres), al abrir <strong>+ Presentar gasto</strong> activa la
                  casilla <em>"Presentar a petición de un socio"</em> y selecciona el socio que pagó.
                  El justificante se da de alta directamente en estado <em>ACEPTADO</em> (saltando la
                  firma del responsable de la actividad). Tú figuras como aceptador. Sigues necesitando
                  aprobarlo y registrar el pago como pasos posteriores.
                </p>

                <p class="help-subtitle">Pendientes de tu visto bueno</p>
                <p class="help-text">
                  Si eres responsable de alguna actividad o tesorero, activa el filtro
                  <strong>"Pendientes de mi visto bueno"</strong> en el listado para ver solo los justificantes
                  que esperan tu firma. Al abrir el detalle, los botones disponibles dependen de tu rol y
                  del estado del justificante.
                </p>

                <p class="help-subtitle">Cancelar un justificante</p>
                <p class="help-text">
                  Mientras esté en <em>PRESENTADO</em>, el propio presentador puede anularlo desde el
                  detalle (botón <strong>Anular</strong>). Una vez aceptado o rechazado, solo el tesorero
                  puede gestionarlo.
                </p>

                <p class="help-subtitle">Códigos y series</p>
                <p class="help-text">
                  El número de justificante toma como prefijo la agrupación de la actividad asociada
                  (<span class="font-mono">JUST-MAD-2025-00012</span> si pertenece a la agrupación MAD)
                  o se queda como número simple si la actividad es global
                  (<span class="font-mono">JUST-2025-00012</span>).
                </p>
              </div>
            </details>

            <details class="help-detail mt-3">
              <summary class="help-detail-summary">
                Flujo · Cobro manual (transferencia / efectivo / tarjeta)
              </summary>
              <div class="help-detail-body">
                <p class="help-text">
                  Cuando un socio paga su cuota fuera del circuito SEPA — por transferencia, en efectivo
                  o con tarjeta — el cobro se registra desde el propio recibo. Una sola pantalla, una
                  sola acción: el sistema actualiza el recibo, la cuota, la cuenta bancaria y el
                  asiento contable en una transacción.
                </p>

                <p class="help-subtitle">Procedimiento</p>
                <ol class="help-list-ord">
                  <li>Ve a <em>Económico → Recibos</em> y localiza el recibo del socio (busca por nombre o número).</li>
                  <li>Abre el detalle del recibo y pulsa <strong>Marcar cobrado</strong>.</li>
                  <li>
                    Rellena los datos:
                    <ul class="help-list">
                      <li><strong>Cuenta bancaria de destino</strong>: en qué cuenta entra el dinero.</li>
                      <li><strong>Modo cobro</strong>: Transferencia, Efectivo, Tarjeta o Manual.</li>
                      <li><strong>Fecha cobro</strong>: la fecha real del ingreso (no la del registro).</li>
                      <li><strong>Referencia</strong> (opcional): núm. de transferencia, ticket de caja, etc.</li>
                    </ul>
                  </li>
                  <li>Confirma. El recibo pasa a <em>COBRADO</em>, la cuota pasa a <em>Cobrada</em> y se
                      crea un apunte de caja con su asiento contable Debe <span class="font-mono">572</span> /
                      Haber <span class="font-mono">721</span>.</li>
                </ol>

                <p class="help-subtitle">Cobros sin recibo previo (caso excepcional)</p>
                <p class="help-text">
                  Si tienes que registrar un cobro que no corresponde a una cuota anual (por ejemplo,
                  una derrama puntual o el pago de una inscripción a formación), primero emite un
                  <strong>recibo individual extraordinario</strong> desde la misma pantalla de Recibos
                  ("+ Emitir lote" con tipo Extraordinaria), y a continuación márcalo cobrado siguiendo
                  los pasos de arriba.
                </p>

                <p class="help-subtitle">Para subvenciones, donaciones y otros ingresos no-cuota</p>
                <p class="help-text">
                  Esos no entran por aquí. Las donaciones tienen su propio flujo (registro en
                  <em>Económico → Donaciones</em>) y las subvenciones se registran desde el módulo
                  Tesorería como apunte de caja directo. Este flujo es solo para cobros de cuotas o
                  conceptos análogos vinculados a un recibo.
                </p>
              </div>
            </details>

            <details class="help-detail mt-3">
              <summary class="help-detail-summary">
                Flujo · Generación y envío de remesa SEPA
              </summary>
              <div class="help-detail-body">
                <p class="help-text">
                  Procedimiento para crear el lote de cobros SEPA del ejercicio, generar el fichero XML que se sube
                  al banco y dejar la remesa lista para que llegue la respuesta del banco (cobros y fallidos).
                </p>

                <p class="help-subtitle">Antes de empezar (única vez)</p>
                <ul class="help-list">
                  <li>
                    Rellena los <strong>4 datos del acreedor SEPA</strong> en <em>Parámetros Generales → SEPA</em>:
                    nombre del acreedor, IBAN de la cuenta donde se ingresarán los cobros, BIC del banco y el
                    Identificador SEPA de la organización (formato <span class="font-mono">ES77ZZZNNNNNNNNN</span>,
                    proporcionado por tu banco o Hacienda).
                  </li>
                  <li>
                    Asegúrate de que los socios que pagan por domiciliación tienen el <strong>IBAN</strong>
                    registrado en su ficha. Los que no lo tengan quedarán excluidos automáticamente de la remesa.
                  </li>
                </ul>

                <p class="help-subtitle">Paso 1 — Crear la remesa</p>
                <ol class="help-list-ord">
                  <li>Ve a <em>Remesas</em> y pulsa <strong>+ Nueva remesa</strong>.</li>
                  <li>
                    Elige el <strong>tipo</strong>:
                    <ul class="help-list">
                      <li><strong>Ordinaria</strong> — cobro anual de cuotas pendientes del ejercicio. Solo se permite una activa por ejercicio.</li>
                      <li><strong>Extraordinaria</strong> — cargo único con concepto e importe libres (derramas, congresales).</li>
                      <li><strong>Reenvío de fallidos</strong> — vuelve a presentar las órdenes que fallaron en una remesa anterior.</li>
                    </ul>
                  </li>
                  <li>
                    Rellena los parámetros. Para una remesa <strong>ordinaria</strong>: ejercicio, fecha de cobro,
                    concepto y secuencia SEPA. La fecha de cobro debe ser al menos <strong>2 días</strong> después
                    de hoy (si es cobro recurrente RCUR) o <strong>14 días</strong> (si es la primera vez FRST).
                  </li>
                  <li>
                    Pulsa <strong>Previsualizar</strong>. Verás cuántas cuotas se incluirán, el importe total y la
                    lista de las que se han excluido y por qué (sin IBAN o ya están en otra remesa activa). Si la
                    lista de excluidos te interesa, puedes cancelar, completar IBANes y volver a intentarlo.
                  </li>
                  <li>
                    Pulsa <strong>Crear remesa</strong>. La remesa nace en estado <em>Borrador</em> y se emiten en
                    bloque los recibos asociados con modo de cobro <em>SEPA</em>.
                  </li>
                </ol>

                <p class="help-subtitle">Paso 2 — Generar el XML y enviarlo al banco</p>
                <ol class="help-list-ord">
                  <li>
                    En la remesa Borrador, despliega las acciones y pulsa <strong>↓ XML SEPA</strong>. Se descarga
                    el fichero <span class="font-mono">pain.008.001.02</span> con todas las órdenes.
                  </li>
                  <li>Sube ese fichero al portal de banca electrónica de tu entidad bancaria.</li>
                  <li>
                    Una vez confirmado por el banco, pulsa <strong>Marcar enviada</strong> para registrar la fecha
                    de envío. La remesa pasa al estado <em>Enviada</em> y queda a la espera de la respuesta del banco.
                  </li>
                </ol>

                <p class="help-subtitle">Paso 3 — Liquidar el cobro</p>
                <p class="help-text">
                  Cuando el banco devuelve el fichero de respuesta (<span class="font-mono">pain.002</span> o
                  <span class="font-mono">camt.054</span>), pulsa <strong>Liquidar cobro</strong> en la remesa
                  Enviada. Este paso es el que registra los ingresos en la contabilidad — ver el detalle en el
                  flujo de Liquidación de remesa (próximamente).
                </p>

                <p class="help-subtitle">Acciones disponibles según estado</p>
                <ul class="help-list">
                  <li><strong>Borrador / Generada / Enviada</strong> — descargar XML, marcar enviada, anular.</li>
                  <li><strong>Enviada</strong> — además, liquidar el cobro tras la respuesta del banco.</li>
                  <li><strong>Procesada / Parcial</strong> — generar remesa de reenvío si quedaron fallidos.</li>
                </ul>

                <p class="help-subtitle">Anular una remesa</p>
                <p class="help-text">
                  Solo se puede anular si NO está procesada todavía (Borrador, Generada o Enviada). Al anular:
                  las cuotas asociadas vuelven a estar libres para incluirse en otra remesa y los recibos
                  emitidos pasan a estado <em>Anulado</em>.
                </p>

                <p class="help-subtitle">Códigos que verás en este flujo</p>
                <p class="help-text">
                  Hay dos códigos distintos que es útil conocer:
                </p>
                <ul class="help-list">
                  <li>
                    <strong>Número de recibo</strong> — formato <span class="font-mono">REC-{prefijo}-2025-00042</span>,
                    donde <em>prefijo</em> son las iniciales de tu agrupación territorial (si la organización está
                    descentralizada) o se omite si la tesorería es centralizada. Identifica al recibo emitido al socio
                    y es lo que se usa si el socio pide un duplicado.
                  </li>
                  <li>
                    <strong>Referencia SEPA</strong> que aparece en el extracto bancario del socio: formato
                    <span class="font-mono">REM-2025-005-042</span>, donde
                    <span class="font-mono">REM-2025-005</span> es el código de la remesa y
                    <span class="font-mono">042</span> es el número de orden dentro de ella. Si un socio te pregunta
                    por un cargo en su cuenta, búscalo por esa referencia en el detalle de la remesa.
                  </li>
                </ul>
              </div>
            </details>
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
.help-list-ord {
  @apply space-y-1 pl-5 list-decimal text-sm text-gray-600 mb-2;
}
.help-list li,
.help-list-ord li {
  @apply leading-relaxed;
}
.help-subtitle {
  @apply text-xs font-semibold uppercase tracking-wide text-amber-700 mt-3 mb-1;
}
.help-detail {
  @apply border border-amber-200 bg-amber-50/40 rounded-lg overflow-hidden;
}
.help-detail-summary {
  @apply px-4 py-2 text-sm font-medium text-amber-800 cursor-pointer hover:bg-amber-100/60 transition-colors;
}
.help-detail-body {
  @apply px-4 py-3 border-t border-amber-200 bg-white;
}
</style>
