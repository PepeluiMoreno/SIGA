<template>
  <AppLayout :title="titulo" :subtitle="subtitulo">

    <div v-if="cargando" class="flex items-center justify-center py-20">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-sm font-medium text-red-800">Error al cargar la campaña</p>
      <p class="text-sm text-red-700 mt-1">{{ error.message }}</p>
      <button @click="cargarTodo" class="mt-2 text-sm text-red-600 hover:text-red-500">Intentar de nuevo</button>
    </div>

    <template v-else-if="campania">
      <div class="space-y-3">

        <!-- WorkflowBar -->
        <WorkflowBar
          :estado-nombre="campania.estado?.nombre || ''"
          :transiciones-disponibles="transicionesDisponibles"
          :cargando="cargandoTransicion"
          :es-final="esFinal"
          @transicion="ejecutarTransicion"
        />

        <!-- KPI Bar -->
        <CampaniaKpiBar :campania="campania" />

        <!-- Botones de acción global -->
        <div class="flex items-center justify-end gap-2">
          <button
            v-if="!campania.notificacionEnviada && esEditable"
            @click="abrirModalNotificacion"
            class="inline-flex items-center gap-1.5 h-8 px-3 text-xs font-medium text-indigo-600 hover:bg-indigo-50 border border-indigo-200 rounded-lg transition-colors"
          >
            <EnvelopeIcon class="w-3.5 h-3.5" /> Notificar membresía
          </button>
          <span
            v-else-if="campania.notificacionEnviada"
            class="inline-flex items-center gap-1.5 h-8 px-3 text-xs font-medium text-green-700 bg-green-50 border border-green-200 rounded-lg"
          >
            <CheckBadgeIcon class="w-3.5 h-3.5" /> Notificación enviada
          </span>
          <button @click="abrirModalClonar"
            class="inline-flex items-center gap-1.5 h-8 px-3 text-xs font-medium text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 border border-slate-200 rounded-lg transition-colors">
            <DocumentDuplicateIcon class="w-3.5 h-3.5" /> Clonar
          </button>
          <button v-if="esEliminable && tienePermiso('CAMP_DELETE')"
            @click="confirmarEliminar = true"
            class="inline-flex items-center gap-1.5 h-8 px-3 text-xs font-medium text-slate-400 hover:text-red-600 hover:bg-red-50 border border-slate-200 rounded-lg transition-colors">
            <TrashIcon class="w-3.5 h-3.5" /> Eliminar
          </button>
          <router-link v-if="esEditable" :to="`/campanias/${campania.id}/editar`"
            class="inline-flex items-center gap-1.5 h-8 px-3 text-xs font-medium text-indigo-600 hover:bg-indigo-50 border border-indigo-200 rounded-lg transition-colors">
            <PencilSquareIcon class="w-3.5 h-3.5" /> Editar
          </router-link>
        </div>

        <!-- 4 Acordeones -->
        <AccordionGroup>

          <!-- ══ 1 · DATOS GENERALES ══════════════════════════════════════════ -->
          <AccordionPanel title="Datos generales" color="violet" :default-open="true">
            <div class="px-5 py-4 grid grid-cols-12 gap-x-4 gap-y-3">

              <div class="col-span-10">
                <label :class="lbl">Nombre</label>
                <div :class="ro">{{ campania.nombre || '—' }}</div>
              </div>
              <div class="col-span-2">
                <label :class="lbl">Estado</label>
                <div :class="ro">
                  <span v-if="campania.estado"
                    class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold"
                    :style="{ background: campania.estado.color + '20', color: campania.estado.color }">
                    {{ campania.estado.nombre }}
                  </span>
                </div>
              </div>

              <div class="col-span-4">
                <label :class="lbl">Tipo de campaña</label>
                <div :class="ro">{{ campania.tipoCampania?.nombre || '—' }}</div>
              </div>
              <div class="col-span-4">
                <label :class="lbl">Ámbito</label>
                <div :class="ro">{{ campania.agrupacion?.nombre || 'General (todas las agrupaciones)' }}</div>
              </div>
              <div class="col-span-4">
                <label :class="lbl">Responsable</label>
                <div :class="ro">
                  {{ campania.responsable ? `${campania.responsable.nombre} ${campania.responsable.apellido1}` : '—' }}
                </div>
              </div>

              <div class="col-span-6">
                <label :class="lbl">Lema</label>
                <div :class="ro">{{ campania.lema || '—' }}</div>
              </div>
              <div class="col-span-6">
                <label :class="lbl">URL externa</label>
                <div :class="ro">
                  <a v-if="campania.urlExterna" :href="campania.urlExterna" target="_blank" rel="noopener noreferrer"
                    class="text-indigo-600 hover:text-indigo-800 truncate inline-flex items-center gap-1">
                    {{ campania.urlExterna }} <ArrowTopRightOnSquareIcon class="w-3.5 h-3.5 shrink-0" />
                  </a>
                  <span v-else class="text-slate-400">—</span>
                </div>
              </div>

              <div class="col-span-12">
                <label :class="lbl">Descripción corta</label>
                <div :class="roL">{{ campania.descripcionCorta || '—' }}</div>
              </div>
              <div class="col-span-12">
                <label :class="lbl">Descripción completa</label>
                <div :class="roL">{{ campania.descripcionLarga || '—' }}</div>
              </div>
              <div class="col-span-12">
                <label :class="lbl">Objetivo principal</label>
                <div :class="roL">{{ campania.objetivoPrincipal || '—' }}</div>
              </div>

            </div>
          </AccordionPanel>

          <!-- ══ 2 · PRESUPUESTO ══════════════════════════════════════════════ -->
          <AccordionPanel title="Presupuesto" color="emerald">
            <div class="px-5 py-4">
              <div v-if="campania.partidasPresupuesto?.length" class="space-y-3">
                <div class="overflow-x-auto -mx-1"><<table class="w-full text-sm">
                  <thead>
                    <tr class="text-xs text-slate-400 uppercase border-b border-slate-100">
                      <th class="text-left font-medium pb-2">Concepto</th>
                      <th class="text-left font-medium pb-2 w-20">Tipo</th>
                      <th class="text-right font-medium pb-2 w-full sm:w-28">Estimado</th>
                      <th class="text-right font-medium pb-2 w-full sm:w-28">Real</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="p in campania.partidasPresupuesto" :key="p.id" class="border-b border-slate-50">
                      <td class="py-2 text-slate-700">{{ p.concepto }}</td>
                      <td class="py-2">
                        <span class="text-xs px-1.5 py-0.5 rounded"
                          :class="p.tipoPartida === 'gasto' ? 'bg-red-50 text-red-600' : 'bg-emerald-50 text-emerald-600'">
                          {{ p.tipoPartida === 'gasto' ? 'Gasto' : 'Ingreso' }}
                        </span>
                      </td>
                      <td class="py-2 text-right tabular-nums text-slate-700">{{ p.importeEstimado != null ? fmtEur(p.importeEstimado) : '—' }}</td>
                      <td class="py-2 text-right tabular-nums text-slate-700">{{ p.importeReal != null ? fmtEur(p.importeReal) : '—' }}</td>
                    </tr>
                  </tbody>
                  <tfoot>
                    <tr class="border-t-2 border-slate-200">
                      <td colspan="2" class="pt-2 text-xs font-semibold text-slate-500 uppercase tracking-wide">Total gastos estimados</td>
                      <td class="pt-2 text-right font-bold tabular-nums text-emerald-700">
                        {{ fmtEur(campania.partidasPresupuesto.filter(p => p.tipoPartida === 'gasto').reduce((s, p) => s + (p.importeEstimado || 0), 0)) }}
                      </td>
                      <td></td>
                    </tr>
                  </tfoot>
                </table></div>
              </div>
              <p v-else class="text-sm text-slate-400 italic py-3">Sin partidas presupuestarias definidas.</p>
            </div>
          </AccordionPanel>

          <!-- ══ 3 · CALENDARIO Y ACTIVIDADES ══════════════════════════════════ -->
          <AccordionPanel title="Calendario y actividades" color="indigo" :default-open="true">
            <div class="px-5 py-4 space-y-4">

              <!-- Fechas de campaña -->
              <div class="grid grid-cols-1 sm:grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                <div>
                  <label :class="lbl">Periodicidad</label>
                  <div :class="ro">{{ labelPeriodicidad(campania.periodicidad) }}</div>
                </div>
                <div>
                  <label :class="lbl">Fecha inicio plan</label>
                  <div :class="ro">{{ fmtFecha(campania.fechaInicioPlan) || '—' }}</div>
                </div>
                <div>
                  <label :class="lbl">Fecha fin plan</label>
                  <div :class="ro">{{ fmtFecha(campania.fechaFinPlan) || '—' }}</div>
                </div>
                <div v-if="campania.fechaInicioReal || campania.fechaFinReal">
                  <label :class="lbl">Fechas reales</label>
                  <div :class="ro">
                    {{ fmtFecha(campania.fechaInicioReal) || '—' }}
                    <template v-if="campania.fechaFinReal"> – {{ fmtFecha(campania.fechaFinReal) }}</template>
                  </div>
                </div>
              </div>

              <!-- Cabecera agenda + botón nueva actividad -->
              <div class="flex items-center justify-between border-t border-slate-100 pt-4">
                <h3 class="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                  Actividades ({{ actividades.length }})
                </h3>
                <router-link v-if="esEditable"
                  :to="`/actividades/nueva?campaniaId=${campania.id}&campaniaNombre=${encodeURIComponent(campania.nombre)}`"
                  class="inline-flex items-center gap-1.5 h-7 px-3 text-xs font-medium text-indigo-600 hover:bg-indigo-50 border border-indigo-200 rounded-lg transition-colors">
                  <PlusIcon class="w-3.5 h-3.5" />
                  Nueva actividad
                </router-link>
              </div>

              <!-- Lista agenda -->
              <div v-if="!actividades.length"
                class="text-sm text-slate-400 italic py-6 text-center border border-dashed border-slate-200 rounded-xl">
                Esta campaña no tiene actividades todavía.
              </div>
              <div v-else class="rounded-xl border border-slate-200 overflow-hidden divide-y divide-slate-100">
                <template v-for="(act, i) in actividades" :key="act.id">

                  <!-- Separador de fecha (cuando cambia) -->
                  <div v-if="i === 0 || act.fechaInicio !== actividades[i-1].fechaInicio"
                    class="flex items-center gap-2 px-4 py-1.5 bg-slate-50 border-b border-slate-200">
                    <span v-if="act.fechaInicio"
                      class="text-xs font-semibold text-slate-500">
                      {{ fmtDiaSemana(act.fechaInicio) }}, {{ fmtDia(act.fechaInicio) }} {{ fmtMes(act.fechaInicio) }}
                    </span>
                    <span v-else class="text-xs font-medium text-slate-400 italic">Sin fecha asignada</span>
                  </div>

                  <!-- Fila actividad -->
                  <div class="bg-white">
                    <div class="flex items-center gap-2 px-3 py-2.5 cursor-pointer select-none hover:bg-slate-50/70 transition-colors group"
                      @click="toggleActExpand(act.id)">
                      <!-- Chevron -->
                      <ChevronRightIcon class="w-3.5 h-3.5 shrink-0 transition-transform" />
                      <!-- Hora -->
                      <span class="shrink-0 w-[88px] text-xs text-slate-400 tabular-nums font-mono">
                        <template v-if="act.horaInicio">{{ fmtHora(act.horaInicio) }}<template v-if="act.horaFin"> – {{ fmtHora(act.horaFin) }}</template></template>
                      </span>
                      <!-- Nombre -->
                      <span class="flex-1 text-sm font-medium text-slate-800 truncate">{{ act.nombre }}</span>
                      <!-- Meta: tareas + horas -->
                      <span v-if="act.tareas?.length" class="shrink-0 hidden sm:flex items-center gap-1 text-xs text-slate-400">
                        <ClipboardDocumentIcon class="w-3 h-3" />
                        {{ act.tareas.length }}
                        <template v-if="act.tareas.some(t => t.horasEstimadas)">
                          · <span class="text-amber-600 font-medium">{{ act.tareas.reduce((s, t) => s + (t.horasEstimadas || 0), 0) }}h</span>
                        </template>
                      </span>
                      <!-- Tipo -->
                      <span v-if="act.tipoActividad"
                        class="shrink-0 hidden md:inline-flex px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-600">
                        {{ act.tipoActividad.nombre }}
                      </span>
                      <!-- Estado -->
                      <span v-if="act.estado"
                        class="shrink-0 inline-flex px-2 py-0.5 rounded-full text-xs font-semibold"
                        :style="{ background: act.estado.color + '22', color: act.estado.color }">
                        {{ act.estado.nombre }}
                      </span>
                      <!-- Ficha -->
                      <router-link :to="`/actividades/${act.id}`" @click.stop
                        class="shrink-0 opacity-0 group-hover:opacity-100 transition-opacity text-xs font-medium text-indigo-600 hover:text-indigo-800 px-2 py-1 rounded hover:bg-indigo-50">
                        Ficha →
                      </router-link>
                    </div>

                    <!-- Panel expandido -->
                    <div v-if="expandedActs.has(act.id)" class="border-t border-slate-100">

                      <!-- Info general si la hay -->
                      <div v-if="act.descripcion || act.responsable || act.lugar || act.esOnline"
                        class="px-10 py-2.5 flex flex-wrap gap-x-6 gap-y-1 text-xs text-slate-500 bg-indigo-50/30 border-b border-slate-100">
                        <span v-if="act.descripcion" class="w-full text-slate-600">{{ act.descripcion }}</span>
                        <span v-if="act.responsable">Resp: <span class="font-medium text-slate-700">{{ act.responsable.nombre }} {{ act.responsable.apellido1 }}</span></span>
                        <span v-if="act.lugar || act.esOnline">Lugar: <span class="font-medium text-slate-700">{{ act.esOnline ? 'Online' : act.lugar }}</span></span>
                        <span v-if="act.presupuestoEstimado">Presupuesto: <span class="font-medium text-slate-700">{{ fmtEur(act.presupuestoEstimado) }} €</span></span>
                      </div>

                      <!-- Tabla de tareas -->
                      <div v-if="act.tareas?.length" class="divide-y divide-slate-50">
                        <div v-for="(t, ti) in act.tareas" :key="t.id"
                          class="flex items-center gap-2 pl-10 pr-4 py-2 hover:bg-slate-50/50 transition-colors">
                          <!-- Conector árbol -->
                          <span class="shrink-0 text-slate-200 text-xs select-none font-mono">{{ ti === act.tareas.length - 1 ? '└' : '├' }}</span>
                          <!-- Dot estado -->
                          <span class="shrink-0 w-1.5 h-1.5 rounded-full mt-px"
                            :style="{ background: t.estado?.color || '#cbd5e1' }"></span>
                          <!-- Título -->
                          <span class="flex-1 text-sm text-slate-700">{{ t.titulo }}</span>
                          <!-- Prioridad -->
                          <span v-if="t.prioridad && t.prioridad !== 'normal' && t.prioridad !== 'media'"
                            class="shrink-0 text-[10px] font-semibold px-1.5 py-0.5 rounded"
                            :class="t.prioridad === 'alta' ? 'bg-red-50 text-red-500' : 'bg-slate-100 text-slate-400'">
                            {{ t.prioridad }}
                          </span>
                          <!-- Horas estimadas -->
                          <span class="shrink-0 w-8 text-right text-xs font-semibold tabular-nums"
                            :class="t.horasEstimadas ? 'text-amber-600' : 'text-slate-200'">
                            {{ t.horasEstimadas ? t.horasEstimadas + 'h' : '—' }}
                          </span>
                          <!-- Horas reales -->
                          <span v-if="t.horasReales" class="shrink-0 text-xs text-emerald-600 tabular-nums font-medium">
                            ({{ t.horasReales }}h real)
                          </span>
                          <!-- Responsable -->
                          <span v-if="t.responsable" class="shrink-0 text-xs text-slate-400 truncate max-w-[100px]">
                            {{ t.responsable.nombre }} {{ t.responsable.apellido1 }}
                          </span>
                          <!-- Estado badge -->
                          <span v-if="t.estado"
                            class="shrink-0 inline-flex px-1.5 py-0.5 rounded-full text-[10px] font-semibold"
                            :style="{ background: (t.estado.color || '#94a3b8') + '22', color: t.estado.color || '#94a3b8' }">
                            {{ t.estado.nombre }}
                          </span>
                        </div>
                      </div>
                      <div v-else class="pl-10 pr-4 py-2 text-xs text-slate-400 italic">Sin tareas.</div>

                      <!-- Participantes (compacto) -->
                      <div v-if="act.participaciones?.length"
                        class="pl-10 pr-4 py-2 flex flex-wrap gap-1.5 border-t border-slate-50">
                        <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wide self-center mr-1">Participantes:</span>
                        <span v-for="p in act.participaciones" :key="p.id"
                          class="inline-flex items-center gap-1 px-2 py-0.5 text-xs bg-white border border-slate-200 rounded-full text-slate-600">
                          {{ p.miembro ? `${p.miembro.nombre} ${p.miembro.apellido1}` : p.nombreExterno || 'Externo' }}
                          <span v-if="p.horasAportadas" class="text-amber-600 font-medium">{{ p.horasAportadas }}h</span>
                        </span>
                      </div>

                    </div>
                  </div>
                </template>
              </div>

            </div>
          </AccordionPanel>

          <!-- ══ 4 · COMUNICACIÓN Y METAS ════════════════════════════════════ -->
          <AccordionPanel title="Comunicación y metas" color="sky">
            <div class="px-5 py-4 space-y-5">

              <!-- Canales de difusión -->
              <div>
                <label :class="lbl">Canales de difusión</label>
                <div v-if="campania.canales?.length" class="flex flex-wrap gap-2 mt-1">
                  <span v-for="c in campania.canales" :key="c.id"
                    class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-sky-50 text-sky-700 border border-sky-200">
                    {{ c.canal?.nombre }}
                  </span>
                </div>
                <p v-else class="text-sm text-slate-400 italic mt-1">Sin canales definidos</p>
              </div>

              <!-- Metas -->
              <div v-if="campania.metas?.length">
                <label :class="lbl">Metas de la campaña</label>
                <div class="overflow-x-auto -mx-1"><<table class="w-full text-sm mt-1">
                  <thead>
                    <tr class="text-xs text-slate-400 uppercase border-b border-slate-100">
                      <th class="text-left font-medium pb-2">Tipo de meta</th>
                      <th class="text-left font-medium pb-2">Unidad</th>
                      <th class="text-right font-medium pb-2">Planificado</th>
                      <th class="text-right font-medium pb-2">Real</th>
                      <th class="text-right font-medium pb-2">%</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="m in campania.metas" :key="m.id" class="border-b border-slate-50">
                      <td class="py-2 text-slate-700">{{ m.tipoMeta?.nombre }}</td>
                      <td class="py-2 text-slate-500">{{ m.tipoMeta?.unidadMedida }}</td>
                      <td class="py-2 text-right text-slate-700">{{ m.valorPlanificado }}</td>
                      <td class="py-2 text-right">
                        <span v-if="m.valorReal != null" class="text-slate-700">{{ m.valorReal }}</span>
                        <span v-else class="text-slate-300">—</span>
                      </td>
                      <td class="py-2 text-right">
                        <span v-if="m.valorReal != null && m.valorPlanificado"
                          class="text-xs font-semibold"
                          :class="pctMeta(m) >= 100 ? 'text-green-600' : 'text-amber-600'">
                          {{ pctMeta(m) }}%
                        </span>
                        <span v-else class="text-slate-300">—</span>
                      </td>
                    </tr>
                  </tbody>
                </table></div>
              </div>
              <p v-else class="text-sm text-slate-400 italic">Sin metas definidas</p>

              <!-- Foto de campaña -->
              <div v-if="campania.fotoUrl">
                <label :class="lbl">Infografía / imagen</label>
                <img :src="campania.fotoUrl" alt="Infografía campaña"
                  class="max-h-48 rounded-lg border border-slate-200 object-contain" />
              </div>

            </div>
          </AccordionPanel>

          <!-- ══ 4 · VALORACIÓN Y CIERRE ════════════════════════════════════= -->
          <AccordionPanel title="Valoración y cierre" color="emerald">
            <div class="px-5 py-4 space-y-5">

              <!-- Presupuesto ejecutado -->
              <div class="grid grid-cols-1 sm:grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                <div>
                  <label :class="lbl">Presupuesto estimado</label>
                  <div :class="ro">{{ fmtEur(campania.presupuestoEstimado) }}</div>
                </div>
                <div>
                  <label :class="lbl">Presupuesto ejecutado</label>
                  <div :class="ro">{{ campania.presupuestoEjecutado != null ? fmtEur(campania.presupuestoEjecutado) : '—' }}</div>
                </div>
                <div>
                  <label :class="lbl">Objetivos cumplidos</label>
                  <div :class="ro">
                    <span v-if="campania.objetivosCumplidos === true" class="text-green-600 font-semibold">Sí</span>
                    <span v-else-if="campania.objetivosCumplidos === false" class="text-red-500 font-semibold">No</span>
                    <span v-else class="text-slate-400">—</span>
                  </div>
                </div>
                <div v-if="aprobadoPor">
                  <label :class="lbl">Aprobado por</label>
                  <div :class="ro">{{ aprobadoPor }}</div>
                </div>
              </div>

              <!-- Valoración -->
              <div>
                <label :class="lbl">Valoración</label>
                <div :class="roL">{{ campania.valoracion || '—' }}</div>
              </div>

            </div>
          </AccordionPanel>

        </AccordionGroup>

      </div>
    </template>

  </AppLayout>

  <!-- ── Modal aprobación ─────────────────────────────────────────────────── -->
  <div v-if="modalAprobacion.visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6 space-y-4">
      <h3 class="text-base font-semibold text-slate-900">{{ modalAprobacion.titulo }}</h3>
      <div>
        <label class="block text-xs font-medium text-slate-700 mb-1">Notas (opcional)</label>
        <textarea v-model="modalAprobacion.notas" rows="3"
          class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          :placeholder="modalAprobacion.placeholder"></textarea>
      </div>
      <div class="flex justify-end gap-2 pt-2 border-t border-slate-100">
        <button @click="modalAprobacion.visible = false"
          class="h-9 px-4 text-sm font-medium text-slate-600 hover:text-slate-900">Cancelar</button>
        <button @click="confirmarAprobacion" :disabled="cargandoTransicion"
          class="h-9 px-5 text-sm font-medium rounded-lg text-white disabled:opacity-50"
          :class="modalAprobacion.esRechazo ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'">
          {{ cargandoTransicion ? '…' : modalAprobacion.btnLabel }}
        </button>
      </div>
    </div>
  </div>

  <!-- ── Modal cierre ─────────────────────────────────────────────────────── -->
  <div v-if="modalCierre.visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200">
        <h3 class="text-base font-semibold text-slate-900">Cerrar campaña</h3>
        <button @click="modalCierre.visible = false" class="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100">
          <XMarkIcon class="w-4 h-4" />
        </button>
      </div>
      <div class="px-6 py-5 space-y-5">

        <div class="space-y-3">
          <h4 class="text-xs font-semibold text-emerald-700 uppercase tracking-wider flex items-center gap-2">
            <span class="w-1.5 h-4 rounded-full bg-emerald-500 shrink-0"></span>
            Cierre financiero <span class="text-red-400 font-normal normal-case tracking-normal">* obligatorio</span>
          </h4>
          <div class="w-60">
            <label class="block text-xs font-medium text-slate-700 mb-1">
              Presupuesto ejecutado total (€) <span class="text-red-400">*</span>
            </label>
            <input v-model.number="modalCierre.presupuestoEjecutado" type="number" min="0" step="0.01"
              class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="0.00" />
          </div>
          <div v-if="modalCierre.resultadosPartidas.length">
            <p class="text-xs text-slate-500 mb-2">Importe real por partida:</p>
            <div class="space-y-2">
              <div v-for="p in modalCierre.resultadosPartidas" :key="p.partidaId"
                class="flex items-center gap-3 p-3 rounded-lg border border-slate-200 bg-slate-50/50">
                <div class="flex-1 min-w-0">
                  <p class="text-sm text-slate-800 truncate">{{ p.concepto }}</p>
                  <span class="text-xs font-medium px-1.5 py-0.5 rounded-full mt-0.5 inline-block"
                    :class="p.tipo === 'ingreso' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'">
                    {{ p.tipo === 'ingreso' ? 'Ingreso' : 'Gasto' }}
                  </span>
                </div>
                <div class="w-full sm:w-36 shrink-0">
                  <input v-model.number="p.importeReal" type="number" min="0" step="0.01"
                    class="h-9 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-right tabular-nums"
                    placeholder="0.00" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="modalCierre.resultadosMetas.length" class="space-y-3">
          <h4 class="text-xs font-semibold text-violet-700 uppercase tracking-wider flex items-center gap-2">
            <span class="w-1.5 h-4 rounded-full bg-violet-500 shrink-0"></span>
            Cierre operativo <span class="text-red-400 font-normal normal-case tracking-normal">* obligatorio</span>
          </h4>
          <div class="space-y-2">
            <div v-for="m in modalCierre.resultadosMetas" :key="m.metaId"
              class="flex items-center gap-3 p-3 rounded-lg border border-slate-200 bg-slate-50/50">
              <div class="flex-1 min-w-0">
                <p class="text-sm text-slate-800">{{ m.tipo }}</p>
                <p class="text-xs text-slate-500 mt-0.5">
                  Planificado: <span class="font-medium">{{ m.planificado }} {{ m.unidad }}</span>
                </p>
              </div>
              <div class="w-full sm:w-36 shrink-0">
                <input v-model.number="m.valorReal" type="number" min="0" step="1"
                  class="h-9 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-right tabular-nums"
                  :placeholder="m.unidad" />
              </div>
            </div>
          </div>
        </div>

        <div>
          <label class="block text-xs font-medium text-slate-700 mb-1">Valoración general (opcional)</label>
          <textarea v-model="modalCierre.valoracion" rows="3"
            class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
            placeholder="Resumen de resultados, lecciones aprendidas…"></textarea>
        </div>

      </div>
      <div class="flex justify-end gap-2 px-6 py-4 border-t border-slate-100">
        <button @click="modalCierre.visible = false"
          class="h-9 px-4 text-sm font-medium text-slate-600 hover:text-slate-900">Cancelar</button>
        <button @click="confirmarCierre" :disabled="cargandoTransicion || !cierreCompleto"
          class="h-9 px-5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg">
          {{ cargandoTransicion ? '…' : 'Cerrar campaña' }}
        </button>
      </div>
    </div>
  </div>

  <!-- ── Modal notificación ────────────────────────────────────────────────── -->
  <div v-if="modalNotif.visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200">
        <h3 class="text-base font-semibold text-slate-900 flex items-center gap-2">
          <EnvelopeIcon class="w-5 h-5 text-indigo-600" />
          Notificar campaña a la membresía
        </h3>
        <button @click="modalNotif.visible = false"
          class="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors">
          <XMarkIcon class="w-4 h-4" />
        </button>
      </div>
      <div v-if="modalNotif.resultado" class="px-6 py-5 space-y-4">
        <div class="rounded-lg p-4"
          :class="modalNotif.resultado.simulado ? 'bg-amber-50 border border-amber-200' : 'bg-green-50 border border-green-200'">
          <div class="flex flex-wrap items-start gap-3">
            <CheckBadgeIcon class="w-5 h-5 shrink-0 mt-0.5"
              :class="modalNotif.resultado.simulado ? 'text-amber-600' : 'text-green-600'" />
            <div class="flex-1">
              <p class="text-sm font-semibold"
                :class="modalNotif.resultado.simulado ? 'text-amber-900' : 'text-green-900'">
                {{ modalNotif.resultado.simulado ? 'Envío simulado' : 'Notificación enviada' }}
              </p>
              <p v-if="modalNotif.resultado.mensaje" class="text-xs mt-1"
                :class="modalNotif.resultado.simulado ? 'text-amber-800' : 'text-green-800'">
                {{ modalNotif.resultado.mensaje }}
              </p>
              <dl class="mt-3 grid grid-cols-2 lg:grid-cols-4 gap-3 text-center">
                <div><dt class="text-xs text-slate-500">Total</dt><dd class="text-lg font-semibold text-slate-800">{{ modalNotif.resultado.total }}</dd></div>
                <div><dt class="text-xs text-slate-500">Enviados</dt><dd class="text-lg font-semibold text-green-700">{{ modalNotif.resultado.enviados }}</dd></div>
                <div><dt class="text-xs text-slate-500">Fallidos</dt><dd class="text-lg font-semibold text-red-600">{{ modalNotif.resultado.fallidos }}</dd></div>
                <div><dt class="text-xs text-slate-500">Sin email</dt><dd class="text-lg font-semibold text-slate-500">{{ modalNotif.resultado.sinEmail }}</dd></div>
              </dl>
            </div>
          </div>
        </div>
        <div class="flex justify-end pt-2 border-t border-slate-100">
          <button @click="modalNotif.visible = false"
            class="h-9 px-5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg">Cerrar</button>
        </div>
      </div>
      <div v-else class="px-6 py-5 space-y-4">
        <div class="flex items-center justify-between bg-indigo-50/60 border border-indigo-100 rounded-lg px-4 py-2.5">
          <div class="flex items-center gap-2">
            <span class="text-xs text-slate-600">Destinatarios estimados:</span>
            <span class="inline-flex items-center px-2 py-0.5 text-xs font-semibold rounded-full bg-indigo-100 text-indigo-700">
              {{ modalNotif.totalDestinatarios }} miembro{{ modalNotif.totalDestinatarios !== 1 ? 's' : '' }}
            </span>
          </div>
          <span v-if="modalNotif.cargandoPreview" class="text-xs text-slate-400 inline-flex items-center gap-1.5">
            <span class="animate-spin rounded-full h-3 w-3 border-2 border-indigo-400 border-t-transparent"></span>
            Generando previsualización…
          </span>
        </div>
        <div>
          <label :class="lbl">Plantilla</label>
          <select v-model="modalNotif.plantillaCodigo" @change="cargarPreviewNotificacion"
            :disabled="modalNotif.cargandoPlantillas || modalNotif.cargandoPreview"
            class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <option v-if="modalNotif.cargandoPlantillas" value="">Cargando plantillas…</option>
            <option v-else-if="!modalNotif.plantillas.length" value="">No hay plantillas para campañas</option>
            <option v-for="p in modalNotif.plantillas" :key="p.id" :value="p.codigo">
              {{ p.nombre }}<template v-if="p.descripcion"> — {{ p.descripcion }}</template>
            </option>
          </select>
        </div>
        <div>
          <label :class="lbl">Asunto <span class="text-red-400">*</span></label>
          <input v-model="modalNotif.asunto" type="text"
            class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Asunto del correo" />
        </div>
        <div>
          <label :class="lbl">Cuerpo (HTML) <span class="text-red-400">*</span></label>
          <textarea v-model="modalNotif.cuerpoHtml" rows="14"
            class="w-full px-3 py-2 text-xs font-mono border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50"
            placeholder="Cuerpo HTML del correo"></textarea>
        </div>
        <ErrorAlert v-if="modalNotif.error" :message="modalNotif.error" />
      </div>
      <div v-if="!modalNotif.resultado" class="flex justify-end gap-2 px-6 py-4 border-t border-slate-100">
        <button @click="modalNotif.visible = false"
          class="h-9 px-4 text-sm font-medium text-slate-600 hover:text-slate-900">Cancelar</button>
        <button @click="enviarNotificacion"
          :disabled="modalNotif.enviando || modalNotif.cargandoPreview || !modalNotif.totalDestinatarios"
          class="h-9 px-5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold rounded-lg inline-flex items-center gap-2">
          <span v-if="modalNotif.enviando" class="animate-spin rounded-full h-3.5 w-3.5 border-2 border-white border-t-transparent"></span>
          <EnvelopeIcon v-else class="w-4 h-4" />
          Enviar a {{ modalNotif.totalDestinatarios }} miembro{{ modalNotif.totalDestinatarios !== 1 ? 's' : '' }}
        </button>
      </div>
    </div>
  </div>

  <!-- ── Modal confirmar eliminación ─────────────────────────────────────── -->
  <div v-if="confirmarEliminar" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-sm p-6 space-y-4">
      <h3 class="text-base font-semibold text-slate-900">¿Eliminar campaña?</h3>
      <p class="text-sm text-slate-600">
        Se eliminará «<strong>{{ campania.nombre }}</strong>». Esta acción no se puede deshacer.
      </p>
      <div class="flex justify-end gap-2 pt-2 border-t border-slate-100">
        <button @click="confirmarEliminar = false"
          class="h-9 px-4 text-sm font-medium text-slate-600 hover:text-slate-900">Cancelar</button>
        <button @click="eliminarCampania" :disabled="eliminando"
          class="h-9 px-5 bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg">
          {{ eliminando ? '…' : 'Eliminar' }}
        </button>
      </div>
    </div>
  </div>

  <!-- ── Modal clonar campaña ─────────────────────────────────────────────── -->
  <div v-if="modalClonar.visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-lg p-6 space-y-5">
      <div class="flex items-center justify-between">
        <h3 class="text-base font-semibold text-slate-900">Clonar campaña</h3>
        <button @click="modalClonar.visible = false" class="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100">
          <XMarkIcon class="w-5 h-5" />
        </button>
      </div>

      <div class="space-y-4">
        <!-- Nombre -->
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1.5">Nombre del clon</label>
          <input v-model="modalClonar.nombre" type="text" maxlength="200"
            class="h-10 w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white placeholder:text-slate-300" />
        </div>

        <!-- Desplazamiento de fechas -->
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1.5">Desplazamiento de fechas</label>
          <div class="flex items-center gap-2">
            <input v-model.number="modalClonar.offsetValor" type="number" min="0" step="1"
              class="h-10 w-24 px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-center tabular-nums" />
            <select v-model="modalClonar.offsetUnidad"
              class="h-10 px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white">
              <option value="dias">días</option>
              <option value="semanas">semanas</option>
              <option value="meses">meses (aprox.)</option>
            </select>
            <span class="text-xs text-slate-400">desplaza todas las fechas</span>
          </div>
        </div>

        <!-- Qué incluir -->
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2">Incluir en el clon</label>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-y-2 gap-x-4">
            <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
              <input type="checkbox" v-model="modalClonar.incluirMetas" class="accent-indigo-600 rounded" />
              Metas de la campaña
            </label>
            <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
              <input type="checkbox" v-model="modalClonar.incluirPartidas" class="accent-indigo-600 rounded" />
              Partidas de presupuesto
            </label>
            <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
              <input type="checkbox" v-model="modalClonar.incluirCanales" class="accent-indigo-600 rounded" />
              Canales de difusión
            </label>
            <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
              <input type="checkbox" v-model="modalClonar.incluirActividades" class="accent-indigo-600 rounded" />
              Actividades y tareas
            </label>
          </div>
        </div>
      </div>

      <div v-if="modalClonar.error" class="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
        {{ modalClonar.error }}
      </div>

      <div class="flex justify-end gap-2 pt-1 border-t border-slate-100">
        <button @click="modalClonar.visible = false"
          class="h-9 px-4 text-sm font-medium text-slate-600 hover:text-slate-900">Cancelar</button>
        <button @click="ejecutarClonar" :disabled="modalClonar.clonando || !modalClonar.nombre.trim()"
          class="h-9 px-5 inline-flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg">
          <span v-if="modalClonar.clonando" class="animate-spin rounded-full h-3.5 w-3.5 border-[2px] border-white border-t-transparent"></span>
          <DocumentDuplicateIcon v-else class="w-3.5 h-3.5" />
          Clonar campaña
        </button>
      </div>
    </div>
  </div>

</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { useToast } from '@/composables/useToast'
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  PencilSquareIcon, ArrowTopRightOnSquareIcon,
  TrashIcon, EnvelopeIcon, CheckBadgeIcon, XMarkIcon, DocumentDuplicateIcon,
} from '@heroicons/vue/24/outline'
import AppLayout from '@/components/common/AppLayout.vue'
import WorkflowBar from '@/components/common/WorkflowBar.vue'
import AccordionGroup from '@/components/common/AccordionGroup.vue'
import AccordionPanel from '@/components/common/AccordionPanel.vue'
import CampaniaKpiBar from '@/modules/comunicaciones/components/CampaniaKpiBar.vue'
import { graphqlClient } from '@/graphql/client'
import { GET_CAMPANIA, GET_PLANTILLAS_CAMPANIA, PREVISUALIZAR_NOTIFICACION_CAMPANIA, ENVIAR_NOTIFICACION_CAMPANIA, CERRAR_CAMPANIA, CLONAR_CAMPANIA } from '@/modules/comunicaciones/graphql/queries.js'
import { TRANSICIONAR_CAMPANIA, APROBAR_CAMPANIA } from '@/modules/actividades/graphql/queries.js'
import { usePermisos } from '@/composables/usePermisos.js'
const toast = useToast()

const { tienePermiso } = usePermisos()
const route  = useRoute()
const router = useRouter()

// ── Estilos ───────────────────────────────────────────────────────────────────
const lbl = 'block text-sm font-medium text-slate-700 mb-1.5'
const ro  = 'h-10 w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-slate-50 text-slate-800 flex items-center overflow-hidden'
const roL = 'w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-slate-50 text-slate-800 leading-relaxed whitespace-pre-line min-h-[80px]'

// ── Estado ───────────────────────────────────────────────────────────────────
const cargando          = ref(true)
const error             = ref(null)
const campania          = ref(null)
const estadosCampania   = ref([])
const cargandoTransicion = ref(false)
// ── Modales ──────────────────────────────────────────────────────────────────
const modalAprobacion = ref({ visible: false, titulo: '', notas: '', placeholder: '', btnLabel: '', esRechazo: false, estadoId: null, tipo: '' })
const modalCierre = ref({
  visible: false, estadoId: null,
  presupuestoEjecutado: null,
  resultadosMetas: [], resultadosPartidas: [], valoracion: '',
})
const modalNotif = ref({
  visible: false, cargandoPlantillas: false, cargandoPreview: false, enviando: false,
  plantillas: [], plantillaCodigo: '', asunto: '', cuerpoHtml: '',
  totalDestinatarios: 0, resultado: null, error: null,
})
const eliminando        = ref(false)
const confirmarEliminar = ref(false)
const modalClonar = ref({
  visible: false, clonando: false, error: null,
  nombre: '', offsetValor: 0, offsetUnidad: 'dias',
  incluirMetas: true, incluirPartidas: true, incluirCanales: true, incluirActividades: true,
})

// ── Agenda: actividades expandibles ──────────────────────────────────────────
const expandedActs = ref(new Set())
function toggleActExpand(id) {
  if (expandedActs.value.has(id)) expandedActs.value.delete(id)
  else expandedActs.value.add(id)
  expandedActs.value = new Set(expandedActs.value)
}

// ── Computed ─────────────────────────────────────────────────────────────────
const titulo    = computed(() => campania.value?.nombre ?? '')
const subtitulo = computed(() => campania.value?.tipoCampania?.nombre ?? '')

const actividades = computed(() => {
  const list = campania.value?.actividades ?? []
  return [...list].sort((a, b) => {
    const da = a.fechaInicio ?? '9999-99-99'
    const db = b.fechaInicio ?? '9999-99-99'
    if (da !== db) return da.localeCompare(db)
    const ha = a.horaInicio ?? '99:99'
    const hb = b.horaInicio ?? '99:99'
    return ha.localeCompare(hb)
  })
})

const esFinal = computed(() => {
  const n = (campania.value?.estado?.nombre || '').toLowerCase()
  return n.includes('finaliz') || n.includes('cancelad')
})
const esCerrada  = computed(() => esFinal.value)
const esEditable = computed(() => !esCerrada.value)
const esEliminable = computed(() => {
  const n = (campania.value?.estado?.nombre || '').toLowerCase()
  return n.includes('borrador')
})

const aprobadoPor = computed(() => {
  const a = campania.value?.aprobadoPor
  return a ? `${a.nombre} ${a.apellido1}` : null
})

const cierreCompleto = computed(() => {
  const c = modalCierre.value
  if (c.presupuestoEjecutado === null || c.presupuestoEjecutado === undefined || c.presupuestoEjecutado === '') return false
  if (c.resultadosMetas.some(m => m.valorReal === null || m.valorReal === undefined || m.valorReal === '')) return false
  if (c.resultadosPartidas.some(p => p.importeReal === null || p.importeReal === undefined || p.importeReal === '')) return false
  return true
})

const transicionesDisponibles = computed(() => {
  if (!campania.value || !estadosCampania.value.length) return []
  const n    = (campania.value.estado?.nombre || '').toLowerCase()
  const find = (s) => estadosCampania.value.find(e => e.nombre.toLowerCase().includes(s))
  if (n.includes('borrador')) {
    const prog = find('programad')
    return prog ? [{ label: 'Enviar para aprobación', estado: prog, icono: 'send', tipo: 'aprobar' }] : []
  }
  if (n.includes('programad')) {
    const curso = find('curso')
    return curso ? [{ label: 'Iniciar campaña', estado: curso, icono: 'play', tipo: 'transicion' }] : []
  }
  if (n.includes('curso')) {
    const final = find('finaliz')
    const pausa = find('pausad')
    return [
      pausa ? { label: 'Pausar', estado: pausa, icono: 'reject', tipo: 'transicion', estilo: 'bg-amber-50 text-amber-700 hover:bg-amber-100' } : null,
      final ? { label: 'Finalizar', estado: final, icono: 'close', tipo: 'cerrar' } : null,
    ].filter(Boolean)
  }
  if (n.includes('pausad')) {
    const curso = find('curso')
    return curso ? [{ label: 'Reactivar', estado: curso, icono: 'play', tipo: 'transicion' }] : []
  }
  return []
})

// ── Formato ──────────────────────────────────────────────────────────────────
const PERIODICIDADES = [
  { value: 'anual', label: 'Anual' },
  { value: 'permanente', label: 'Permanente' },
  { value: 'puntual', label: 'Puntual' },
  { value: 'semestral', label: 'Semestral' },
]
const labelPeriodicidad = (v) => PERIODICIDADES.find(p => p.value === v)?.label ?? v ?? '—'

const fmtFecha = (d) => d
  ? new Date(d).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
  : ''

const _parseDate = (d) => d ? new Date(d + 'T12:00:00') : null
const fmtDia  = (d) => _parseDate(d)?.toLocaleDateString('es-ES', { day: 'numeric' }) ?? '—'
const fmtMes  = (d) => _parseDate(d)?.toLocaleDateString('es-ES', { month: 'short' }) ?? ''
const fmtDiaSemana = (d) => _parseDate(d)?.toLocaleDateString('es-ES', { weekday: 'short' }) ?? ''
const fmtHora = (h) => h ? h.slice(0, 5) : null
const fmtEur = (n) =>
  new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n || 0)

function pctMeta(m) {
  if (!m.valorPlanificado) return 0
  return Math.round((m.valorReal / m.valorPlanificado) * 100)
}

// ── Modal notificación ────────────────────────────────────────────────────────
async function abrirModalNotificacion() {
  modalNotif.value = {
    visible: true, cargandoPlantillas: true, cargandoPreview: false, enviando: false,
    plantillas: [], plantillaCodigo: '', asunto: '', cuerpoHtml: '',
    totalDestinatarios: 0, resultado: null, error: null,
  }
  try {
    const data = await graphqlClient.request(GET_PLANTILLAS_CAMPANIA)
    const lista = data.plantillasEmail ?? []
    modalNotif.value.plantillas = lista
    if (lista.length) {
      modalNotif.value.plantillaCodigo = lista[0].codigo
      await cargarPreviewNotificacion()
    }
  } catch (e) {
    modalNotif.value.error = e?.response?.errors?.[0]?.message || 'Error al cargar plantillas'
  } finally {
    modalNotif.value.cargandoPlantillas = false
  }
}

async function cargarPreviewNotificacion() {
  modalNotif.value.cargandoPreview = true
  modalNotif.value.error = null
  try {
    const data = await graphqlClient.request(PREVISUALIZAR_NOTIFICACION_CAMPANIA, {
      campaniaId: campania.value.id,
      plantillaCodigo: modalNotif.value.plantillaCodigo || null,
    })
    const p = data.previsualizarNotificacionCampania
    modalNotif.value.asunto = p.asunto
    modalNotif.value.cuerpoHtml = p.cuerpoHtml
    modalNotif.value.totalDestinatarios = p.totalDestinatarios
  } catch (e) {
    modalNotif.value.error = e?.response?.errors?.[0]?.message || 'Error al generar previsualización'
  } finally {
    modalNotif.value.cargandoPreview = false
  }
}

async function enviarNotificacion() {
  if (!modalNotif.value.asunto?.trim() || !modalNotif.value.cuerpoHtml?.trim()) {
    modalNotif.value.error = 'El asunto y el cuerpo son obligatorios'
    return
  }
  modalNotif.value.enviando = true
  modalNotif.value.error = null
  try {
    const data = await graphqlClient.request(ENVIAR_NOTIFICACION_CAMPANIA, {
      campaniaId: campania.value.id,
      asunto: modalNotif.value.asunto,
      cuerpoHtml: modalNotif.value.cuerpoHtml,
    })
    modalNotif.value.resultado = data.enviarNotificacionCampania
    await cargarCampania()
  } catch (e) {
    modalNotif.value.error = e?.response?.errors?.[0]?.message || 'Error al enviar la notificación'
  } finally {
    modalNotif.value.enviando = false
  }
}

// ── Workflow ──────────────────────────────────────────────────────────────────
async function ejecutarTransicion(t) {
  if (t.tipo === 'aprobar') {
    modalAprobacion.value = { visible: true, titulo: 'Aprobar campaña', notas: '', placeholder: 'Observaciones…', btnLabel: 'Aprobar', esRechazo: false, estadoId: t.estado.id, tipo: 'aprobar' }
  } else if (t.tipo === 'cerrar') {
    modalCierre.value = {
      visible: true,
      estadoId: t.estado.id,
      presupuestoEjecutado: campania.value.presupuestoEjecutado ?? null,
      resultadosMetas: (campania.value.metas || []).map(m => ({
        metaId: m.id,
        valorReal: m.valorReal ?? null,
        tipo: m.tipoMeta?.nombre || '',
        unidad: m.tipoMeta?.unidadMedida || '',
        planificado: m.valorPlanificado,
      })),
      resultadosPartidas: (campania.value.partidasPresupuesto || []).map(p => ({
        partidaId: p.id,
        importeReal: p.importeReal ?? null,
        concepto: p.concepto,
        tipo: p.tipoPartida,
      })),
      valoracion: campania.value.valoracion || '',
    }
  } else {
    cargandoTransicion.value = true
    try {
      await graphqlClient.request(TRANSICIONAR_CAMPANIA, { id: campania.value.id, estadoId: t.estado.id })
      await cargarCampania()
    } catch (e) { toast.error(e?.response?.errors?.[0]?.message || 'Error') }
    finally { cargandoTransicion.value = false }
  }
}

async function confirmarAprobacion() {
  cargandoTransicion.value = true
  try {
    const mut = modalAprobacion.value.tipo === 'aprobar' ? APROBAR_CAMPANIA : TRANSICIONAR_CAMPANIA
    await graphqlClient.request(mut, { id: campania.value.id, estadoId: modalAprobacion.value.estadoId, notas: modalAprobacion.value.notas || null })
    modalAprobacion.value.visible = false
    await cargarCampania()
  } catch (e) { toast.error(e?.response?.errors?.[0]?.message || 'Error') }
  finally { cargandoTransicion.value = false }
}

async function confirmarCierre() {
  cargandoTransicion.value = true
  try {
    await graphqlClient.request(CERRAR_CAMPANIA, {
      id: campania.value.id,
      estadoId: modalCierre.value.estadoId,
      presupuestoEjecutado: modalCierre.value.presupuestoEjecutado,
      resultadosMetas: modalCierre.value.resultadosMetas.map(m => ({
        metaId: m.metaId,
        valorReal: m.valorReal,
      })),
      resultadosPartidas: modalCierre.value.resultadosPartidas.map(p => ({
        partidaId: p.partidaId,
        importeReal: p.importeReal,
      })),
      valoracion: modalCierre.value.valoracion || null,
    })
    modalCierre.value.visible = false
    await cargarCampania()
  } catch (e) { toast.error(e?.response?.errors?.[0]?.message || 'Error') }
  finally { cargandoTransicion.value = false }
}

// ── Carga ─────────────────────────────────────────────────────────────────────
async function cargarCampania() {
  error.value = null
  try {
    const data = await graphqlClient.request(GET_CAMPANIA, { id: route.params.id })
    if (!data.campanias?.length) throw new Error('Campaña no encontrada')
    campania.value = data.campanias[0]
  } catch (err) { error.value = err }
}

async function cargarTodo() {
  cargando.value = true
  await cargarCampania()
  if (!error.value) {
    try {
      const data = await graphqlClient.request('query EstadosCampania { estadosCampania { id nombre } }')
      estadosCampania.value = data.estadosCampania ?? []
    } catch (e) { console.error('Error estados campania:', e) }
  }
  cargando.value = false
}

// ── Eliminar campaña ──────────────────────────────────────────────────────────
const GQL_ELIMINAR = `mutation EliminarCampania($id: UUID!) { eliminarCampanias(filter: { id: { eq: $id } }) { id } }`

async function eliminarCampania() {
  eliminando.value = true
  try {
    await graphqlClient.request(GQL_ELIMINAR, { id: campania.value.id })
    router.push('/campanias')
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error al eliminar la campaña')
  } finally {
    eliminando.value = false
    confirmarEliminar.value = false
  }
}

function abrirModalClonar() {
  modalClonar.value = {
    visible: true, clonando: false, error: null,
    nombre: `${campania.value.nombre} (copia)`,
    offsetValor: 0, offsetUnidad: 'dias',
    incluirMetas: true, incluirPartidas: true, incluirCanales: true, incluirActividades: true,
  }
}

async function ejecutarClonar() {
  const mc = modalClonar.value
  if (!mc.nombre.trim()) return
  mc.clonando = true
  mc.error = null
  try {
    const factores = { dias: 1, semanas: 7, meses: 30 }
    const offsetDias = (mc.offsetValor || 0) * (factores[mc.offsetUnidad] ?? 1)
    const res = await graphqlClient.request(CLONAR_CAMPANIA, {
      campaniaId: campania.value.id,
      nombre: mc.nombre.trim(),
      offsetDias,
      incluirActividades: mc.incluirActividades,
    })
    const nuevaId = res.clonarCampania?.id
    modalClonar.value.visible = false
    if (nuevaId) router.push(`/campanias/${nuevaId}`)
  } catch (e) {
    mc.error = e?.response?.errors?.[0]?.message || 'Error al clonar la campaña'
  } finally {
    mc.clonando = false
  }
}

onMounted(cargarTodo)
</script>
