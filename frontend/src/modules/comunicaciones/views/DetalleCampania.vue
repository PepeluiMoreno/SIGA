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

        <WorkflowBar
          :estado-nombre="campania.estado?.nombre || ''"
          :transiciones-disponibles="transicionesDisponibles"
          :cargando="cargandoTransicion"
          :es-final="esFinal"
          @transicion="ejecutarTransicion"
        />

        <!-- ══ 1 · DATOS GENERALES ════════════════════════════════════════════ -->
        <section :class="cardCls">
          <div :class="fixedHeader">
            <span class="shrink-0 w-1.5 h-5 rounded-full bg-purple-500"></span>
            <h2 :class="titleCls">Datos generales</h2>
            <div class="ml-auto">
              <router-link v-if="esEditable" :to="`/campanias/${campania.id}/editar`"
                class="inline-flex items-center gap-1.5 h-8 px-3 text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 text-xs font-medium rounded-lg transition-colors">
                <PencilSquareIcon class="w-3.5 h-3.5" /> Editar
              </router-link>
              <span v-else class="inline-flex items-center gap-1.5 h-8 px-3 text-slate-400 text-xs font-medium">
                <LockClosedIcon class="w-3.5 h-3.5" />
                {{ esCerrada ? 'Campaña cerrada' : 'Solo lectura' }}
              </span>
            </div>
          </div>
          <div class="px-5 py-4 grid grid-cols-12 gap-x-3 gap-y-3">

            <div class="col-span-5">
              <label :class="lbl">Nombre</label>
              <div :class="ro">{{ campania.nombre || '—' }}</div>
            </div>
            <div class="col-span-5">
              <label :class="lbl">Tipo</label>
              <div :class="ro">{{ campania.tipoCampania?.nombre || '—' }}</div>
            </div>
            <div class="col-span-2">
              <label :class="lbl">Estado</label>
              <div :class="ro">
                <span v-if="campania.estado"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border"
                  :style="badgeStyle(campania.estado.color)">
                  {{ campania.estado.nombre }}
                </span>
                <span v-else class="text-slate-400">—</span>
              </div>
            </div>

            <div class="col-span-4">
              <label :class="lbl">Ámbito de la campaña</label>
              <div :class="ro">{{ campania.agrupacion?.nombre || 'General (todas las agrupaciones)' }}</div>
            </div>
            <div class="col-span-4">
              <label :class="lbl">Lema</label>
              <div :class="ro">{{ campania.lema || '—' }}</div>
            </div>
            <div class="col-span-4">
              <label :class="lbl">URL externa</label>
              <div :class="ro">
                <a v-if="campania.urlExterna"
                  :href="campania.urlExterna" target="_blank" rel="noopener noreferrer"
                  class="text-indigo-600 hover:text-indigo-800 truncate inline-flex items-center gap-1">
                  {{ campania.urlExterna }} <ArrowTopRightOnSquareIcon class="w-3.5 h-3.5 shrink-0" />
                </a>
                <span v-else class="text-slate-400">—</span>
              </div>
            </div>

          </div>
        </section>

        <!-- ══ 2 · PLANIFICACIÓN TEMPORAL ════════════════════════════════════ -->
        <section :class="cardCls">
          <button type="button" @click="togglePanel('plan')" :class="accordionBtn(open.plan)">
            <span class="flex items-center gap-3">
              <span class="shrink-0 w-1.5 h-5 rounded-full bg-sky-500"></span>
              <h2 :class="titleCls">Planificación temporal</h2>
            </span>
            <ChevronDownIcon :class="chevronCls(open.plan)" />
          </button>
          <div v-show="open.plan" class="px-5 py-4">
            <div class="flex flex-wrap gap-4 items-end">
              <div class="w-52">
                <label :class="lbl">Periodicidad</label>
                <div :class="ro">{{ labelPeriodicidad(campania.periodicidad) }}</div>
              </div>
              <div class="w-36">
                <label :class="lbl">Fecha de inicio</label>
                <div :class="ro">{{ fmtFecha(campania.fechaInicioPlan) || '—' }}</div>
              </div>
              <div v-if="campania.periodicidad !== 'permanente'" class="w-36">
                <label :class="lbl">Fecha de fin</label>
                <div :class="ro">{{ fmtFecha(campania.fechaFinPlan) || '—' }}</div>
              </div>
            </div>
            <div v-if="campania.fechaInicioReal || campania.fechaFinReal"
              class="flex flex-wrap gap-4 items-end mt-3 pt-3 border-t border-slate-100">
              <div class="w-36">
                <label :class="lbl">Inicio real</label>
                <div :class="ro">{{ fmtFecha(campania.fechaInicioReal) || '—' }}</div>
              </div>
              <div class="w-36">
                <label :class="lbl">Fin real</label>
                <div :class="ro">{{ fmtFecha(campania.fechaFinReal) || '—' }}</div>
              </div>
            </div>
            <div v-if="campania.canales?.length" class="mt-3 pt-3 border-t border-slate-100">
              <label :class="lbl">Canales de difusión</label>
              <div class="flex flex-wrap gap-2 mt-1">
                <span v-for="c in campania.canales" :key="c.id"
                  class="inline-flex items-center px-3 py-1 bg-sky-50 text-sky-700 border border-sky-200 text-xs font-medium rounded-full">
                  {{ c.canal.nombre }}
                </span>
              </div>
            </div>
          </div>
        </section>

        <!-- ══ 3 · DESCRIPCIÓN Y OBJETIVOS ══════════════════════════════════ -->
        <section :class="cardCls">
          <button type="button" @click="togglePanel('desc')" :class="accordionBtn(open.desc)">
            <span class="flex items-center gap-3">
              <span class="shrink-0 w-1.5 h-5 rounded-full bg-violet-500"></span>
              <h2 :class="titleCls">Descripción y objetivos</h2>
            </span>
            <ChevronDownIcon :class="chevronCls(open.desc)" />
          </button>
          <div v-show="open.desc" class="px-5 py-4 space-y-3">
            <div>
              <label :class="lbl">Descripción corta</label>
              <div :class="ro">{{ campania.descripcionCorta || '—' }}</div>
            </div>
            <div class="grid grid-cols-5 gap-4">
              <div class="col-span-3">
                <label :class="lbl">Descripción completa</label>
                <div :class="roL">{{ campania.descripcionLarga || '—' }}</div>
              </div>
              <div class="col-span-2">
                <label :class="lbl">Objetivo principal</label>
                <div :class="roL">{{ campania.objetivoPrincipal || '—' }}</div>
              </div>
            </div>
            <!-- Metas -->
            <div v-if="campania.metas?.length">
              <label :class="lbl">Metas de la campaña</label>
              <div class="rounded-lg border border-slate-200 overflow-hidden">
                <div class="grid grid-cols-12 gap-2 px-4 py-2 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  <span class="col-span-5">Tipo de meta</span>
                  <span class="col-span-2">Unidad</span>
                  <span class="col-span-2 text-right">Planificado</span>
                  <span class="col-span-3 text-right">Real</span>
                </div>
                <div v-for="(m, i) in campania.metas" :key="m.id"
                  class="grid grid-cols-12 gap-2 px-4 py-2.5 items-center border-b border-slate-100 last:border-0"
                  :class="i % 2 === 0 ? 'bg-white' : 'bg-slate-50/40'">
                  <div class="col-span-5 text-sm text-slate-800">{{ m.tipoMeta?.nombre || '—' }}</div>
                  <div class="col-span-2 text-xs text-slate-500">{{ m.tipoMeta?.unidadMedida || '—' }}</div>
                  <div class="col-span-2 text-sm text-slate-700 text-right tabular-nums font-medium">{{ m.valorPlanificado ?? '—' }}</div>
                  <div class="col-span-3 text-right">
                    <span v-if="m.valorReal !== null && m.valorReal !== undefined"
                      class="text-sm font-semibold tabular-nums"
                      :class="Number(m.valorReal) >= Number(m.valorPlanificado) ? 'text-emerald-700' : 'text-amber-600'">
                      {{ m.valorReal }}
                    </span>
                    <span v-else class="text-xs text-slate-400 italic">Pendiente</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- ══ 4 · PRESUPUESTO ════════════════════════════════════════════════ -->
        <section :class="cardCls">
          <button type="button" @click="togglePanel('presupuesto')" :class="accordionBtn(open.presupuesto)">
            <span class="flex items-center gap-3">
              <span class="shrink-0 w-1.5 h-5 rounded-full bg-emerald-500"></span>
              <h2 :class="titleCls">Presupuesto</h2>
              <span v-if="campania.presupuestoEstimado"
                class="px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold rounded-full tabular-nums">
                {{ fmtEur(campania.presupuestoEstimado) }}
              </span>
            </span>
            <ChevronDownIcon :class="chevronCls(open.presupuesto)" />
          </button>
          <div v-show="open.presupuesto" class="px-5 py-4 space-y-4">
            <div class="flex flex-wrap gap-4">
              <div class="w-52">
                <label :class="lbl">Presupuesto estimado</label>
                <div :class="ro">{{ campania.presupuestoEstimado ? fmtEur(campania.presupuestoEstimado) : '—' }}</div>
              </div>
              <div v-if="campania.presupuestoEjecutado !== null && campania.presupuestoEjecutado !== undefined" class="w-52">
                <label :class="lbl">Presupuesto ejecutado</label>
                <div :class="ro">{{ fmtEur(campania.presupuestoEjecutado) }}</div>
              </div>
            </div>
            <div v-if="campania.partidasPresupuesto?.length">
              <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Partidas</p>
              <div class="rounded-lg border border-slate-200 overflow-hidden">
                <div class="grid grid-cols-12 gap-2 px-4 py-2 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  <span class="col-span-5">Concepto</span>
                  <span class="col-span-2">Tipo</span>
                  <span class="col-span-2 text-right">Estimado</span>
                  <span class="col-span-3 text-right">Real</span>
                </div>
                <div v-for="(p, i) in campania.partidasPresupuesto" :key="p.id"
                  class="grid grid-cols-12 gap-2 px-4 py-2.5 items-center border-b border-slate-100 last:border-0"
                  :class="i % 2 === 0 ? 'bg-white' : 'bg-slate-50/40'">
                  <div class="col-span-5 text-sm text-slate-800 truncate">{{ p.concepto }}</div>
                  <div class="col-span-2">
                    <span class="text-xs px-1.5 py-0.5 rounded-full font-medium"
                      :class="p.tipoPartida === 'ingreso' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'">
                      {{ p.tipoPartida === 'ingreso' ? 'Ingreso' : 'Gasto' }}
                    </span>
                  </div>
                  <div class="col-span-2 text-sm text-slate-700 text-right tabular-nums font-medium">
                    {{ fmtEur(p.importeEstimado) }}
                  </div>
                  <div class="col-span-3 text-right">
                    <span v-if="p.importeReal !== null && p.importeReal !== undefined"
                      class="text-sm font-semibold tabular-nums text-slate-800">
                      {{ fmtEur(p.importeReal) }}
                    </span>
                    <span v-else class="text-xs text-slate-400 italic">Pendiente</span>
                  </div>
                </div>
              </div>
            </div>
            <p v-else class="text-sm text-slate-400 italic text-center py-4">Sin partidas de presupuesto registradas.</p>
          </div>
        </section>

        <!-- ══ 5 · RECURSOS HUMANOS ══════════════════════════════════════════ -->
        <section :class="cardCls">
          <button type="button" @click="togglePanel('rrhh')" :class="accordionBtn(open.rrhh)">
            <span class="flex items-center gap-3">
              <span class="shrink-0 w-1.5 h-5 rounded-full bg-amber-500"></span>
              <h2 :class="titleCls">Recursos humanos</h2>
            </span>
            <ChevronDownIcon :class="chevronCls(open.rrhh)" />
          </button>
          <div v-show="open.rrhh" class="px-5 py-4 space-y-4">
            <div class="w-72">
              <label :class="lbl">Responsable</label>
              <div :class="ro">
                <span v-if="campania.responsable" class="flex items-center gap-2">
                  <span class="w-6 h-6 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 text-xs font-semibold shrink-0">
                    {{ iniciales(campania.responsable) }}
                  </span>
                  {{ campania.responsable.nombre }} {{ campania.responsable.apellido1 }}
                </span>
                <span v-else class="text-slate-400">—</span>
              </div>
            </div>

            <!-- Equipos de trabajo -->
            <div v-if="cargandoEquipos" class="py-4 flex justify-center">
              <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-600"></div>
            </div>
            <div v-else-if="grupos.length">
              <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Equipos de trabajo</p>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div v-for="g in grupos" :key="g.id"
                  class="border border-slate-200 rounded-lg p-3">
                  <div class="flex justify-between items-start">
                    <div>
                      <p class="text-sm font-medium text-slate-900">{{ g.nombre }}</p>
                      <p class="text-xs text-slate-500 mt-0.5">{{ g.tipoGrupo?.nombre }}</p>
                    </div>
                    <span class="text-xs font-medium px-2 py-0.5 rounded-full shrink-0"
                      :class="g.activo ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'">
                      {{ g.activo ? 'Activo' : 'Inactivo' }}
                    </span>
                  </div>
                  <p v-if="g.coordinador" class="mt-1.5 text-xs text-slate-500">
                    Coordinador: {{ g.coordinador.nombre }} {{ g.coordinador.apellido1 }}
                  </p>
                  <p v-if="g.miembros?.length" class="mt-1 text-xs text-slate-400">
                    {{ g.miembros.length }} miembro{{ g.miembros.length !== 1 ? 's' : '' }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- ══ 6 · ACTIVIDADES ════════════════════════════════════════════════ -->
        <section :class="cardCls">
          <button type="button" @click="togglePanel('actividades')" :class="accordionBtn(open.actividades)">
            <span class="flex items-center gap-3">
              <span class="shrink-0 w-1.5 h-5 rounded-full bg-indigo-500"></span>
              <h2 :class="titleCls">Actividades</h2>
              <span v-if="actividades.length"
                class="px-2 py-0.5 bg-indigo-50 text-indigo-700 border border-indigo-200 text-xs font-semibold rounded-full">
                {{ actividades.length }}
              </span>
            </span>
            <ChevronDownIcon :class="chevronCls(open.actividades)" />
          </button>
          <div v-show="open.actividades">
            <div class="flex items-center justify-between px-5 py-2.5 border-b border-slate-100 bg-slate-50/50">
              <span></span>
              <button v-if="tienePermiso('ACT_CREATE')"
                @click="abrirModalActividad()"
                class="inline-flex items-center gap-1.5 h-8 px-3 text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 text-xs font-medium rounded-lg transition-colors">
                <PlusIcon class="w-3.5 h-3.5" /> Nueva actividad
              </button>
            </div>

            <div v-if="cargandoActividades" class="px-5 py-6 flex justify-center">
              <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-600"></div>
            </div>
            <div v-else-if="!actividades.length" class="px-5 py-8 text-center text-sm text-slate-400">
              Sin actividades planificadas para esta campaña.
            </div>
            <div v-else>
              <div class="grid grid-cols-12 gap-2 px-5 py-2 border-b border-slate-100 bg-slate-50/70">
                <span class="col-span-1"></span>
                <span class="col-span-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Actividad</span>
                <span class="col-span-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">Tipo</span>
                <span class="col-span-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">Estado</span>
                <span class="col-span-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">Fecha</span>
                <span class="col-span-1 text-xs font-semibold text-slate-400 uppercase tracking-wider">Tareas</span>
                <span class="col-span-1"></span>
              </div>
              <div v-for="act in actividades" :key="act.id">
                <div class="grid grid-cols-12 gap-2 px-5 py-3 items-center border-b border-slate-50 hover:bg-slate-50 transition-colors cursor-pointer"
                  @click="toggleExpand(act.id)">
                  <div class="col-span-1 flex justify-center">
                    <ChevronRightIcon class="w-4 h-4 text-slate-400 transition-transform"
                      :class="expandedSet.has(act.id) ? 'rotate-90' : ''" />
                  </div>
                  <div class="col-span-3 min-w-0">
                    <p class="text-sm font-medium text-slate-800 truncate">{{ act.nombre }}</p>
                    <p v-if="act.responsable" class="text-xs text-slate-400 mt-0.5">👤 {{ act.responsable.nombre }} {{ act.responsable.apellido1 }}</p>
                    <p v-else-if="act.grupo" class="text-xs text-slate-400 mt-0.5">👥 {{ act.grupo.nombre }}</p>
                  </div>
                  <div class="col-span-2">
                    <span class="text-xs text-slate-600 bg-slate-100 px-2 py-0.5 rounded-full">
                      {{ act.tipoActividad?.nombre || '—' }}
                    </span>
                  </div>
                  <div class="col-span-2">
                    <span class="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full border"
                      :style="badgeStyle(act.estado?.color)">
                      {{ act.estado?.nombre || '—' }}
                    </span>
                  </div>
                  <div class="col-span-2 text-xs text-slate-500">
                    {{ fmtFechaCorta(act.fechaInicio) }}
                    <span v-if="act.fechaFin && act.fechaFin !== act.fechaInicio"> — {{ fmtFechaCorta(act.fechaFin) }}</span>
                  </div>
                  <div class="col-span-1 text-xs text-slate-500 text-center">{{ act.tareas?.length || 0 }}</div>
                  <div class="col-span-1 flex justify-end" @click.stop>
                    <button @click="abrirModalActividad(act)"
                      class="p-1.5 rounded-lg text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors">
                      <PencilSquareIcon class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
                <div v-if="expandedSet.has(act.id)"
                  class="bg-slate-50 border-b border-slate-100 px-8 py-3 space-y-2">
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Tareas</span>
                    <button @click="abrirModalTarea(act.id)"
                      class="inline-flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 font-medium">
                      <PlusIcon class="w-3 h-3" /> Nueva tarea
                    </button>
                  </div>
                  <div v-if="!act.tareas?.length" class="text-xs text-slate-400 py-2">Sin tareas. Añade la primera.</div>
                  <div v-else>
                    <div class="grid grid-cols-12 gap-2 pb-1 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                      <span class="col-span-4">Título</span>
                      <span class="col-span-2">Estado</span>
                      <span class="col-span-3">Asignado a</span>
                      <span class="col-span-2 text-right">Horas</span>
                      <span class="col-span-1"></span>
                    </div>
                    <div v-for="t in act.tareas" :key="t.id"
                      class="grid grid-cols-12 gap-2 py-1.5 items-center border-t border-slate-100">
                      <div class="col-span-4 flex items-center gap-2">
                        <span class="w-1.5 h-1.5 rounded-full shrink-0"
                          :class="{ 'bg-red-400': t.prioridad === 1, 'bg-amber-400': t.prioridad === 2, 'bg-slate-300': t.prioridad === 3 }">
                        </span>
                        <span class="text-xs text-slate-700 truncate">{{ t.titulo }}</span>
                      </div>
                      <div class="col-span-2">
                        <span class="inline-flex items-center px-1.5 py-0.5 text-xs font-medium rounded-full border"
                          :style="badgeStyle(t.estado?.color)">
                          {{ t.estado?.nombre || '—' }}
                        </span>
                      </div>
                      <div class="col-span-3 text-xs text-slate-500 truncate">
                        <span v-if="t.responsable">👤 {{ t.responsable.nombre }} {{ t.responsable.apellido1 }}</span>
                        <span v-else-if="t.grupo">👥 {{ t.grupo.nombre }}</span>
                        <span v-else class="text-slate-300">—</span>
                      </div>
                      <div class="col-span-2 text-xs text-slate-400 text-right">
                        {{ t.horasEstimadas ? t.horasEstimadas + 'h' : '—' }}
                        <span v-if="t.horasReales" class="text-indigo-500"> / {{ t.horasReales }}h</span>
                      </div>
                      <div class="col-span-1"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>


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

        <!-- Bloque financiero -->
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
                <div class="w-36 shrink-0">
                  <input v-model.number="p.importeReal" type="number" min="0" step="0.01"
                    class="h-9 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-right tabular-nums"
                    placeholder="0.00" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Bloque operativo -->
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
              <div class="w-36 shrink-0">
                <input v-model.number="m.valorReal" type="number" min="0" step="1"
                  class="h-9 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-right tabular-nums"
                  :placeholder="m.unidad" />
              </div>
            </div>
          </div>
        </div>

        <!-- Valoración -->
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
          <div class="flex items-start gap-3">
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
              <dl class="mt-3 grid grid-cols-4 gap-3 text-center">
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
            :disabled="modalNotif.cargandoPlantillas || modalNotif.cargandoPreview" :class="inp">
            <option v-if="modalNotif.cargandoPlantillas" value="">Cargando plantillas…</option>
            <option v-else-if="!modalNotif.plantillas.length" value="">No hay plantillas para campañas</option>
            <option v-for="p in modalNotif.plantillas" :key="p.id" :value="p.codigo">
              {{ p.nombre }}<template v-if="p.descripcion"> — {{ p.descripcion }}</template>
            </option>
          </select>
        </div>
        <div>
          <label :class="lbl">Asunto <span class="text-red-400">*</span></label>
          <input v-model="modalNotif.asunto" type="text" :class="inp" placeholder="Asunto del correo" />
        </div>
        <div>
          <label :class="lbl">Cuerpo (HTML) <span class="text-red-400">*</span></label>
          <textarea v-model="modalNotif.cuerpoHtml" rows="14"
            class="w-full px-3 py-2 text-xs font-mono border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50"
            placeholder="Cuerpo HTML del correo"></textarea>
        </div>
        <p v-if="modalNotif.error" class="text-xs text-red-600">{{ modalNotif.error }}</p>
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

  <!-- ── Modal actividad ──────────────────────────────────────────────────── -->
  <div v-if="modalAct.visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200">
        <h3 class="text-base font-semibold text-slate-900">
          {{ modalAct.modo === 'editar' ? 'Editar actividad' : 'Nueva actividad' }}
        </h3>
        <button @click="modalAct.visible = false" class="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors">
          <XMarkIcon class="w-4 h-4" />
        </button>
      </div>
      <div class="px-6 py-5 space-y-4">
        <div class="grid grid-cols-3 gap-3">
          <div class="col-span-2">
            <label :class="lbl">Nombre <span class="text-red-400">*</span></label>
            <input v-model="modalAct.form.nombre" type="text" :class="inp" placeholder="Nombre de la actividad" autofocus />
          </div>
          <div>
            <label :class="lbl">Estado <span class="text-red-400">*</span></label>
            <select v-model="modalAct.form.estadoId" :class="inp">
              <option value="">— Seleccionar —</option>
              <option v-for="e in estadosActividad" :key="e.id" :value="e.id">{{ e.nombre }}</option>
            </select>
          </div>
        </div>
        <div class="grid grid-cols-3 gap-3">
          <div>
            <label :class="lbl">Tipo <span class="text-red-400">*</span></label>
            <select v-model="modalAct.form.tipoActividadId" :class="inp">
              <option value="">— Seleccionar —</option>
              <option v-for="t in tiposActividad" :key="t.id" :value="t.id">{{ t.nombre }}</option>
            </select>
          </div>
          <div>
            <label :class="lbl">Fecha inicio</label>
            <input v-model="modalAct.form.fechaInicio" type="date" :class="inp" />
          </div>
          <div>
            <label :class="lbl">Fecha fin</label>
            <input v-model="modalAct.form.fechaFin" type="date" :class="inp" />
          </div>
        </div>
        <div class="grid grid-cols-3 gap-3">
          <div class="col-span-2">
            <label :class="lbl">Lugar</label>
            <input v-model="modalAct.form.lugar" type="text" :class="inp"
              :disabled="modalAct.form.esOnline" placeholder="Dirección o nombre del espacio" />
          </div>
          <div class="flex items-end pb-2 gap-2">
            <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer select-none">
              <input type="checkbox" v-model="modalAct.form.esOnline" class="rounded text-indigo-600" />
              Es online
            </label>
          </div>
        </div>
        <div v-if="modalAct.form.esOnline">
          <label :class="lbl">URL de acceso online</label>
          <input v-model="modalAct.form.urlOnline" type="url" :class="inp" placeholder="https://meet.google.com/…" />
        </div>
        <div>
          <label :class="lbl">Asignación</label>
          <div class="flex gap-3">
            <label v-for="op in ASIGNACION_OPTS" :key="op.value"
              class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer select-none">
              <input type="radio" :value="op.value" v-model="modalAct.form.asignacion" class="text-indigo-600" />
              {{ op.label }}
            </label>
          </div>
          <div class="mt-2">
            <select v-if="modalAct.form.asignacion === 'individual'" v-model="modalAct.form.responsableId" :class="inp">
              <option value="">— Seleccionar miembro —</option>
              <option v-for="m in miembrosList" :key="m.id" :value="m.id">{{ m.nombre }} {{ m.apellido1 }}</option>
            </select>
            <select v-else-if="modalAct.form.asignacion === 'grupo'" v-model="modalAct.form.grupoId" :class="inp">
              <option value="">— Seleccionar equipo —</option>
              <option v-for="g in grupos" :key="g.id" :value="g.id">{{ g.nombre }}</option>
            </select>
          </div>
        </div>
        <div>
          <label :class="lbl">Descripción</label>
          <textarea v-model="modalAct.form.descripcion" rows="3" :class="inp" placeholder="Descripción de la actividad…"></textarea>
        </div>
        <p v-if="modalAct.error" class="text-xs text-red-600">{{ modalAct.error }}</p>
      </div>
      <div class="flex justify-end gap-2 px-6 py-4 border-t border-slate-100">
        <button @click="modalAct.visible = false"
          class="h-9 px-4 text-sm font-medium text-slate-600 hover:text-slate-900">Cancelar</button>
        <button @click="guardarActividad" :disabled="modalAct.submitting"
          class="h-9 px-5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold rounded-lg inline-flex items-center gap-2">
          <span v-if="modalAct.submitting" class="animate-spin rounded-full h-3.5 w-3.5 border-2 border-white border-t-transparent"></span>
          {{ modalAct.modo === 'editar' ? 'Guardar cambios' : 'Crear actividad' }}
        </button>
      </div>
    </div>
  </div>

  <!-- ── Modal tarea ──────────────────────────────────────────────────────── -->
  <div v-if="modalTarea.visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-lg">
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200">
        <h3 class="text-base font-semibold text-slate-900">Nueva tarea</h3>
        <button @click="modalTarea.visible = false" class="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100">
          <XMarkIcon class="w-4 h-4" />
        </button>
      </div>
      <div class="px-6 py-5 space-y-4">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label :class="lbl">Título <span class="text-red-400">*</span></label>
            <input v-model="modalTarea.form.titulo" type="text" :class="inp" placeholder="Título de la tarea" autofocus />
          </div>
          <div>
            <label :class="lbl">Estado <span class="text-red-400">*</span></label>
            <select v-model="modalTarea.form.estadoId" :class="inp">
              <option value="">— Seleccionar —</option>
              <option v-for="e in estadosTarea" :key="e.id" :value="e.id">{{ e.nombre }}</option>
            </select>
          </div>
        </div>
        <div class="grid grid-cols-3 gap-3">
          <div>
            <label :class="lbl">Prioridad</label>
            <select v-model="modalTarea.form.prioridad" :class="inp">
              <option :value="1">Alta</option>
              <option :value="2">Media</option>
              <option :value="3">Baja</option>
            </select>
          </div>
          <div>
            <label :class="lbl">Horas estimadas</label>
            <input v-model.number="modalTarea.form.horasEstimadas" type="number" min="0" step="0.5" :class="inp" placeholder="0" />
          </div>
          <div>
            <label :class="lbl">Fecha límite</label>
            <input v-model="modalTarea.form.fechaLimite" type="date" :class="inp" />
          </div>
        </div>
        <div>
          <label :class="lbl">Asignación</label>
          <div class="flex gap-3 mb-2">
            <label v-for="op in ASIGNACION_OPTS" :key="op.value"
              class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer select-none">
              <input type="radio" :value="op.value" v-model="modalTarea.form.asignacion" class="text-indigo-600" />
              {{ op.label }}
            </label>
          </div>
          <select v-if="modalTarea.form.asignacion === 'individual'" v-model="modalTarea.form.responsableId" :class="inp">
            <option value="">— Seleccionar miembro —</option>
            <option v-for="m in miembrosList" :key="m.id" :value="m.id">{{ m.nombre }} {{ m.apellido1 }}</option>
          </select>
          <select v-else-if="modalTarea.form.asignacion === 'grupo'" v-model="modalTarea.form.grupoId" :class="inp">
            <option value="">— Seleccionar equipo —</option>
            <option v-for="g in grupos" :key="g.id" :value="g.id">{{ g.nombre }}</option>
          </select>
        </div>
        <p v-if="modalTarea.error" class="text-xs text-red-600">{{ modalTarea.error }}</p>
      </div>
      <div class="flex justify-end gap-2 px-6 py-4 border-t border-slate-100">
        <button @click="modalTarea.visible = false"
          class="h-9 px-4 text-sm font-medium text-slate-600 hover:text-slate-900">Cancelar</button>
        <button @click="guardarTarea" :disabled="modalTarea.submitting"
          class="h-9 px-5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold rounded-lg inline-flex items-center gap-2">
          <span v-if="modalTarea.submitting" class="animate-spin rounded-full h-3.5 w-3.5 border-2 border-white border-t-transparent"></span>
          Crear tarea
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  PencilSquareIcon, ArrowTopRightOnSquareIcon, LockClosedIcon,
  PlusIcon, ChevronRightIcon, ChevronDownIcon, XMarkIcon,
  EnvelopeIcon, CheckBadgeIcon,
} from '@heroicons/vue/24/outline'
import AppLayout from '@/components/common/AppLayout.vue'
import WorkflowBar from '@/components/common/WorkflowBar.vue'
import RecursosTab from '@/components/campanias/tabs/RecursosTab.vue'
import { graphqlClient } from '@/graphql/client'
import { GET_CAMPANIA } from '@/modules/comunicaciones/graphql/queries.js'
import { TRANSICIONAR_CAMPANIA, APROBAR_CAMPANIA } from '@/modules/actividades/graphql/queries.js'
import {
  GET_PLANTILLAS_CAMPANIA,
  PREVISUALIZAR_NOTIFICACION_CAMPANIA,
  ENVIAR_NOTIFICACION_CAMPANIA,
  CERRAR_CAMPANIA,
} from '@/modules/comunicaciones/graphql/queries.js'
import { badgeStyle } from '@/utils/badge'
import { usePermisos } from '@/composables/usePermisos.js'

const { tienePermiso } = usePermisos()
const route = useRoute()

// ── Estilos (mismos que CampaniaForm) ────────────────────────────────────────
const cardCls     = 'rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden'
const fixedHeader = 'flex items-center gap-3 px-5 py-3.5 border-b border-slate-200'
const titleCls    = 'text-sm font-semibold text-slate-800'
const lbl         = 'block text-sm font-medium text-slate-700 mb-1.5'

// Campos de sólo lectura — visualmente idénticos a los inputs del formulario
const ro  = 'h-10 w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-slate-50 text-slate-800 flex items-center overflow-hidden'
const roL = 'w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-slate-50 text-slate-800 leading-relaxed whitespace-pre-line min-h-[80px]'

// Inputs usados en los modales
const inp = 'h-10 w-full px-3 py-2 text-sm border border-slate-300 rounded-lg transition-all ' +
            'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ' +
            'bg-white placeholder:text-slate-300 disabled:bg-slate-50 disabled:text-slate-400'

// ── Acordeones ───────────────────────────────────────────────────────────────
const open = reactive({ plan: true, desc: true, presupuesto: false, rrhh: false, actividades: true })

function togglePanel(key) { open[key] = !open[key] }

const accordionBtn = (isOpen) =>
  'w-full flex items-center justify-between px-5 py-3.5 hover:bg-slate-50/60 transition-colors ' +
  (isOpen ? 'border-b border-slate-200' : '')
const chevronCls = (isOpen) =>
  'w-4 h-4 text-slate-400 transition-transform duration-200 ' + (isOpen ? 'rotate-180' : '')

// ── Constantes ───────────────────────────────────────────────────────────────
const PERIODICIDADES = [
  { value: 'anual',      label: 'Anual' },
  { value: 'permanente', label: 'Permanente' },
  { value: 'puntual',    label: 'Puntual' },
  { value: 'semestral',  label: 'Semestral' },
]
const labelPeriodicidad = (v) => PERIODICIDADES.find(p => p.value === v)?.label ?? v ?? '—'

const ASIGNACION_OPTS = [
  { value: 'ninguna',    label: 'Sin asignar' },
  { value: 'individual', label: 'Responsable individual' },
  { value: 'grupo',      label: 'Equipo de trabajo' },
]


// ── Estado ───────────────────────────────────────────────────────────────────
const cargando           = ref(true)
const error              = ref(null)
const campania           = ref(null)
const actividades        = ref([])
const grupos             = ref([])
const miembrosMap        = ref({})
const estadosCampania    = ref([])
const tiposActividad     = ref([])
const estadosActividad   = ref([])
const estadosTarea       = ref([])
const cargandoEquipos    = ref(false)
const cargandoActividades = ref(false)
const cargandoTransicion  = ref(false)

const expandedSet = ref(new Set())
const toggleExpand = (id) => {
  const s = new Set(expandedSet.value)
  s.has(id) ? s.delete(id) : s.add(id)
  expandedSet.value = s
}

// ── Modales ──────────────────────────────────────────────────────────────────
const _actForm = () => ({
  id: null, nombre: '', tipoActividadId: '', estadoId: '',
  descripcion: '', fechaInicio: '', fechaFin: '',
  esOnline: false, lugar: '', urlOnline: '',
  asignacion: 'ninguna', responsableId: '', grupoId: '',
})
const modalAct = ref({ visible: false, modo: 'crear', form: _actForm(), submitting: false, error: null })

const _tareaForm = () => ({
  titulo: '', estadoId: '', prioridad: 2,
  horasEstimadas: null, fechaLimite: '',
  asignacion: 'ninguna', responsableId: '', grupoId: '',
})
const modalTarea = ref({ visible: false, actividadId: null, form: _tareaForm(), submitting: false, error: null })

const modalAprobacion = ref({ visible: false, titulo: '', notas: '', placeholder: '', btnLabel: '', esRechazo: false, estadoId: null, tipo: '' })
const modalCierre = ref({
  visible: false,
  estadoId: null,
  presupuestoEjecutado: null,
  resultadosMetas: [],
  resultadosPartidas: [],
  valoracion: '',
})

const modalNotif = ref({
  visible: false, cargandoPlantillas: false, cargandoPreview: false, enviando: false,
  plantillas: [], plantillaCodigo: '', asunto: '', cuerpoHtml: '',
  totalDestinatarios: 0, resultado: null, error: null,
})

// ── Computed ─────────────────────────────────────────────────────────────────
const titulo    = computed(() => campania.value?.nombre ?? '')
const subtitulo = computed(() => campania.value?.tipoCampania?.nombre ?? '')
const esFinal    = computed(() => {
  const n = (campania.value?.estado?.nombre || '').toLowerCase()
  return n.includes('finaliz') || n.includes('cancelad')
})
const esCerrada  = computed(() => esFinal.value)
const esEditable = computed(() => {
  const n = (campania.value?.estado?.nombre || '').toLowerCase()
  return n.includes('borrador')
})
const miembrosList = computed(() =>
  Object.values(miembrosMap.value).sort((a, b) =>
    `${a.nombre} ${a.apellido1}`.localeCompare(`${b.nombre} ${b.apellido1}`, 'es')
  )
)

const cierreCompleto = computed(() => {
  const c = modalCierre.value
  if (c.presupuestoEjecutado === null || c.presupuestoEjecutado === undefined || c.presupuestoEjecutado === '') return false
  if (c.resultadosMetas.some(m => m.valorReal === null || m.valorReal === undefined || m.valorReal === '')) return false
  if (c.resultadosPartidas.some(p => p.importeReal === null || p.importeReal === undefined || p.importeReal === '')) return false
  return true
})


function indiceEstado(nombre) {
  const n = (nombre || '').toLowerCase()
  if (n.includes('borrador'))  return 0
  if (n.includes('programad')) return 1
  if (n.includes('curso'))     return 2
  if (n.includes('pausad'))    return 3
  if (n.includes('finaliz'))   return 4
  if (n.includes('cancelad'))  return 5
  return -1
}
const indiceCampania = computed(() => indiceEstado(campania.value?.estado?.nombre))

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
function iniciales(r) {
  return `${r.nombre?.[0] ?? ''}${r.apellido1?.[0] ?? ''}`.toUpperCase()
}
const fmtFecha = (d) => d
  ? new Date(d).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
  : ''
const fmtFechaCorta = (d) => d
  ? new Date(d).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
  : '—'
const fmtEur = (n) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n || 0)

// ── GQL inline ───────────────────────────────────────────────────────────────
const GQL_ACTIVIDADES = `
  query ActividadesCampania($campaniaId: UUID!) {
    actividades(filter: { campaniaId: { eq: $campaniaId }, eliminado: { eq: false } }) {
      id nombre descripcion
      tipoActividad { id nombre }
      estado { id nombre color }
      fechaInicio fechaFin
      lugar esOnline urlOnline presupuestoEstimado
      responsable { id nombre apellido1 }
      grupo { id nombre }
      tareas {
        id titulo prioridad
        estado { id nombre color }
        responsable { id nombre apellido1 }
        grupo { id nombre }
        horasEstimadas horasReales fechaLimite
      }
    }
  }
`
const GQL_CATALOGOS_ACT = `
  query CatalogosActividad {
    tiposAccion(filter: { activo: { eq: true } }) { id nombre }
    estadosAccion { id nombre color orden activo }
    estadosTarea { id nombre color orden activo }
  }
`
const GQL_CREAR_ACT = `
  mutation CrearActividad($data: ActividadCreateData!) {
    crearActividad(data: $data) { id nombre }
  }
`
const GQL_ACTUALIZAR_ACT = `
  mutation ActualizarActividad($data: ActividadUpdateData!) {
    actualizarActividad(data: $data) { id nombre }
  }
`
const GQL_CREAR_TAREA = `
  mutation CrearTarea($data: TareaCreateData!) {
    crearTarea(data: $data) { id titulo }
  }
`
const GQL_GRUPOS = `
  query GruposCampania($campaniaId: UUID!) {
    gruposTrabajo(filter: { campaniaId: { eq: $campaniaId } }) {
      id nombre activo
      tipoGrupo { id nombre }
      coordinador { id nombre apellido1 }
      miembros { id activo }
    }
  }
`
const GQL_MIEMBROS = `query MiembrosNombre { miembros { id nombre apellido1 apellido2 } }`
const GQL_ESTADOS  = `query EstadosCampania { estadosCampania { id nombre } }`

// ── Modal actividad ───────────────────────────────────────────────────────────
function abrirModalActividad(act = null) {
  if (act) {
    modalAct.value = {
      visible: true, modo: 'editar', error: null, submitting: false,
      form: {
        id: act.id, nombre: act.nombre,
        tipoActividadId: act.tipoActividad?.id || '',
        estadoId: act.estado?.id || '',
        descripcion: act.descripcion || '',
        fechaInicio: act.fechaInicio || '', fechaFin: act.fechaFin || '',
        esOnline: act.esOnline || false, lugar: act.lugar || '', urlOnline: act.urlOnline || '',
        asignacion: act.grupo ? 'grupo' : act.responsable ? 'individual' : 'ninguna',
        responsableId: act.responsable?.id || '', grupoId: act.grupo?.id || '',
      },
    }
  } else {
    const def = estadosActividad.value.find(e => e.nombre.toLowerCase().includes('borrador')) ?? estadosActividad.value[0]
    modalAct.value = { visible: true, modo: 'crear', error: null, submitting: false,
      form: { ..._actForm(), estadoId: def?.id || '' } }
  }
}

async function guardarActividad() {
  const f = modalAct.value.form
  if (!f.nombre?.trim()) { modalAct.value.error = 'El nombre es obligatorio'; return }
  if (!f.tipoActividadId) { modalAct.value.error = 'Selecciona un tipo'; return }
  if (!f.estadoId) { modalAct.value.error = 'Selecciona un estado'; return }
  modalAct.value.submitting = true
  modalAct.value.error = null
  try {
    const base = {
      nombre: f.nombre.trim(), tipoActividadId: f.tipoActividadId, estadoId: f.estadoId,
      campaniaId: campania.value.id, descripcion: f.descripcion || null,
      fechaInicio: f.fechaInicio || null, fechaFin: f.fechaFin || null,
      esOnline: f.esOnline, lugar: !f.esOnline ? (f.lugar || null) : null,
      urlOnline: f.esOnline ? (f.urlOnline || null) : null,
      responsableId: f.asignacion === 'individual' ? (f.responsableId || null) : null,
      grupoId: f.asignacion === 'grupo' ? (f.grupoId || null) : null,
    }
    if (modalAct.value.modo === 'editar')
      await graphqlClient.request(GQL_ACTUALIZAR_ACT, { data: { id: f.id, ...base } })
    else
      await graphqlClient.request(GQL_CREAR_ACT, { data: base })
    modalAct.value.visible = false
    await cargarActividades()
  } catch (e) {
    modalAct.value.error = e?.response?.errors?.[0]?.message || 'Error al guardar'
  } finally {
    modalAct.value.submitting = false
  }
}

// ── Modal tarea ───────────────────────────────────────────────────────────────
function abrirModalTarea(actividadId) {
  const def = estadosTarea.value.find(e => e.nombre.toLowerCase().includes('pend')) ?? estadosTarea.value[0]
  modalTarea.value = { visible: true, actividadId, error: null, submitting: false,
    form: { ..._tareaForm(), estadoId: def?.id || '' } }
}

async function guardarTarea() {
  const f = modalTarea.value.form
  if (!f.titulo?.trim()) { modalTarea.value.error = 'El título es obligatorio'; return }
  if (!f.estadoId) { modalTarea.value.error = 'Selecciona un estado'; return }
  modalTarea.value.submitting = true
  modalTarea.value.error = null
  try {
    await graphqlClient.request(GQL_CREAR_TAREA, {
      data: {
        titulo: f.titulo.trim(), estadoId: f.estadoId, actividadId: modalTarea.value.actividadId,
        prioridad: f.prioridad, horasEstimadas: f.horasEstimadas || null,
        fechaLimite: f.fechaLimite || null,
        responsableId: f.asignacion === 'individual' ? (f.responsableId || null) : null,
        grupoId: f.asignacion === 'grupo' ? (f.grupoId || null) : null,
      },
    })
    modalTarea.value.visible = false
    await cargarActividades()
  } catch (e) {
    modalTarea.value.error = e?.response?.errors?.[0]?.message || 'Error al crear la tarea'
  } finally {
    modalTarea.value.submitting = false
  }
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
    } catch (e) { alert(e?.response?.errors?.[0]?.message || 'Error') }
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
  } catch (e) { alert(e?.response?.errors?.[0]?.message || 'Error') }
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
  } catch (e) { alert(e?.response?.errors?.[0]?.message || 'Error') }
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

async function cargarActividades() {
  cargandoActividades.value = true
  try {
    const data = await graphqlClient.request(GQL_ACTIVIDADES, { campaniaId: route.params.id })
    actividades.value = data.actividades ?? []
  } catch (e) { console.error('Error actividades:', e) }
  finally { cargandoActividades.value = false }
}

async function cargarTodo() {
  cargando.value = true
  await cargarCampania()
  if (!error.value) {
    cargandoEquipos.value    = true
    cargandoActividades.value = true
    const [dataG, dataM, dataE, dataA, dataCat] = await Promise.allSettled([
      graphqlClient.request(GQL_GRUPOS,       { campaniaId: route.params.id }),
      graphqlClient.request(GQL_MIEMBROS),
      graphqlClient.request(GQL_ESTADOS),
      graphqlClient.request(GQL_ACTIVIDADES,  { campaniaId: route.params.id }),
      graphqlClient.request(GQL_CATALOGOS_ACT),
    ])
    grupos.value           = dataG.value?.gruposTrabajo ?? []
    actividades.value      = dataA.value?.actividades ?? []
    tiposActividad.value   = (dataCat.value?.tiposAccion ?? []).sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
    estadosActividad.value = (dataCat.value?.estadosAccion ?? []).filter(e => e.activo).sort((a, b) => (a.orden ?? 99) - (b.orden ?? 99))
    estadosTarea.value     = (dataCat.value?.estadosTarea ?? []).filter(e => e.activo).sort((a, b) => (a.orden ?? 99) - (b.orden ?? 99))
    const map = {}
    for (const m of dataM.value?.miembros ?? []) map[m.id] = m
    miembrosMap.value     = map
    estadosCampania.value = dataE.value?.estadosCampania ?? []
    cargandoEquipos.value    = false
    cargandoActividades.value = false
  }
  cargando.value = false
}

onMounted(cargarTodo)
</script>
