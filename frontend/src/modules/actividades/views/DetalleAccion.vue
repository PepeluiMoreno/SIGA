<template>
  <AppLayout :title="accion?.nombre || 'Actividad'" :subtitle="accion?.tipoActividad?.nombre || ''">
    <div class="max-w-5xl">

    <div v-if="loading" class="flex items-center justify-center py-20">
      <LoadSpinner />
    </div>

    <div v-else-if="!accion" class="py-20 text-center text-slate-400">Actividad no encontrada.</div>

    <div v-else class="space-y-4">

      <!-- Breadcrumb campaña -->
      <div v-if="accion.campania" class="flex items-center gap-1.5 text-xs text-slate-500">
        <router-link :to="`/campanias/${accion.campania.id}`"
          class="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-800 hover:underline font-medium">
          <ChevronLeftIcon class="w-3.5 h-3.5" />
          {{ accion.campania.nombre }}
        </router-link>
        <span class="text-slate-300">/</span>
        <span class="text-slate-400">{{ accion.nombre }}</span>
      </div>

      <!-- WorkflowBar -->
      <WorkflowBar
        :estado-nombre="accion.estado?.nombre || ''"
        :transiciones-disponibles="transicionesDisponibles"
        :cargando="cargandoTransicion"
        :es-final="esFinal"
        @transicion="ejecutarTransicion"
      />

      <AccordionGroup class="space-y-4">

      <!-- Panel 1: Diseño y propuesta -->
      <AccordionPanel title="Diseño y propuesta">
        <template #actions>
          <template v-if="!editandoAccion && faseEditable">
            <button @click="abrirEditAccion"
              class="inline-flex items-center gap-1 h-8 px-3 text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 text-xs font-medium rounded-lg transition-colors">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M16.862 4.487a2.1 2.1 0 1 1 2.978 2.978L7.5 19.805l-4 1 1-4 12.362-12.318z"/>
              </svg>
              Editar
            </button>
            <button @click="showConfirmEliminarAccion = true"
              class="inline-flex items-center gap-1 h-8 px-3 text-slate-600 hover:text-red-600 hover:bg-red-50 text-xs font-medium rounded-lg transition-colors">
              <TrashIcon class="w-3.5 h-3.5" />
              Eliminar
            </button>
          </template>
        </template>

        <!-- Formulario edición -->
        <div v-if="editandoAccion" class="px-5 py-4 space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="sm:col-span-2">
              <label class="block text-xs font-medium text-slate-700 mb-1">Nombre *</label>
              <input v-model="formAccionEdit.nombre" type="text"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Tipo</label>
              <select v-model="formAccionEdit.tipoActividadId"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option v-for="t in tiposActividad" :key="t.id" :value="t.id">{{ t.nombre }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Responsable</label>
              <select v-model="formAccionEdit.responsableId"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option value="">— Sin asignar —</option>
                <option v-for="m in miembros" :key="m.id" :value="m.id">{{ m.nombre }} {{ m.apellido1 }}</option>
              </select>
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-medium text-slate-700 mb-1">Descripción</label>
              <textarea v-model="formAccionEdit.descripcion" rows="3"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"></textarea>
            </div>
            <!-- Fechas en una línea -->
            <div class="sm:col-span-2">
              <label class="block text-xs font-medium text-slate-700 mb-1">Inicio / Fin</label>
              <div class="flex flex-wrap gap-2 items-center">
                <input v-model="formAccionEdit.fechaInicio" type="date"
                  class="h-10 px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                <input v-model="formAccionEdit.horaInicio" type="time"
                  class="h-10 px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                <span class="text-slate-300">–</span>
                <input v-model="formAccionEdit.fechaFin" type="date"
                  class="h-10 px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                <input v-model="formAccionEdit.horaFin" type="time"
                  class="h-10 px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
            </div>
            <!-- Duración estimada -->
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Duración est. (días / horas)</label>
              <div class="flex gap-2 items-center">
                <input v-model.number="formAccionEdit.duracionDias" type="number" min="0" placeholder="d"
                  class="h-10 w-20 px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                <span class="text-slate-400 text-xs">d</span>
                <input v-model.number="formAccionEdit.duracionHoras" type="number" min="0" step="0.5" placeholder="h"
                  class="h-10 w-20 px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                <span class="text-slate-400 text-xs">h</span>
              </div>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Aforo</label>
              <input v-model.number="formAccionEdit.aforo" type="number" min="0"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Lugar (nombre)</label>
              <input v-model="formAccionEdit.lugar" type="text"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-medium text-slate-700 mb-1">Dirección postal</label>
              <input v-model="formAccionEdit.direccion" type="text"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Localidad</label>
              <input v-model="formAccionEdit.localidad" type="text"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Provincia</label>
              <input v-model="formAccionEdit.provincia" type="text"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Presupuesto estimado (€)</label>
              <input v-model.number="formAccionEdit.presupuestoEstimado" type="number" min="0" step="0.01"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div class="flex items-end pb-1">
              <label class="flex items-center gap-2 text-sm">
                <input type="checkbox" v-model="formAccionEdit.esOnline" class="rounded border-slate-300 text-indigo-600" />
                <span>Es online</span>
              </label>
            </div>
            <div v-if="formAccionEdit.esOnline" class="sm:col-span-2">
              <label class="block text-xs font-medium text-slate-700 mb-1">URL online</label>
              <input v-model="formAccionEdit.urlOnline" type="url"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
          </div>
          <div class="flex justify-end gap-2 pt-2 border-t border-slate-100">
            <button type="button" @click="editandoAccion = false"
              class="h-9 px-3 text-sm font-medium text-slate-600 hover:text-slate-900">Cancelar</button>
            <button type="button" @click="guardarEditAccion"
              class="h-9 px-4 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg">Guardar</button>
          </div>
        </div>

        <!-- Vista detalle -->
        <div v-else class="divide-y divide-slate-100">
          <div v-if="accion.descripcion" class="px-5 py-4">
            <p class="text-sm text-slate-600">{{ accion.descripcion }}</p>
          </div>
          <dl class="px-5 py-4 grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-3 text-sm">
            <div v-if="accion.fechaInicio">
              <dt class="text-slate-500 mb-0.5">Fecha inicio</dt>
              <dd class="text-slate-900 font-medium">{{ accion.fechaInicio }}<span v-if="accion.horaInicio" class="ml-1 text-slate-500">{{ accion.horaInicio }}</span></dd>
            </div>
            <div v-if="accion.fechaFin">
              <dt class="text-slate-500 mb-0.5">Fecha fin</dt>
              <dd class="text-slate-900 font-medium">{{ accion.fechaFin }}<span v-if="accion.horaFin" class="ml-1 text-slate-500">{{ accion.horaFin }}</span></dd>
            </div>
            <div v-if="accion.duracionDias || accion.duracionHoras">
              <dt class="text-slate-500 mb-0.5">Duración estimada</dt>
              <dd class="text-slate-900 font-medium">
                <template v-if="accion.duracionDias">{{ accion.duracionDias }}d </template>
                <template v-if="accion.duracionHoras">{{ accion.duracionHoras }}h</template>
              </dd>
            </div>
            <div v-if="accion.lugar">
              <dt class="text-slate-500 mb-0.5">Lugar</dt>
              <dd class="text-slate-900 font-medium">{{ accion.lugar }}</dd>
            </div>
            <div v-if="accion.direccion || accion.localidad || accion.provincia" class="col-span-2">
              <dt class="text-slate-500 mb-0.5">Dirección</dt>
              <dd class="text-slate-900 font-medium">
                {{ [accion.direccion, accion.localidad, accion.provincia].filter(Boolean).join(', ') }}
              </dd>
            </div>
            <div v-if="accion.aforo">
              <dt class="text-slate-500 mb-0.5">Aforo</dt>
              <dd class="text-slate-900 font-medium">{{ accion.aforo }}</dd>
            </div>
            <div v-if="accion.esOnline && accion.urlOnline">
              <dt class="text-slate-500 mb-0.5">URL online</dt>
              <dd><a :href="accion.urlOnline" target="_blank" class="text-indigo-600 hover:underline text-xs">{{ accion.urlOnline }}</a></dd>
            </div>
            <div v-if="accion.responsable">
              <dt class="text-slate-500 mb-0.5">Responsable</dt>
              <dd class="text-slate-900 font-medium">{{ accion.responsable.nombre }} {{ accion.responsable.apellido1 }}</dd>
            </div>
            <div v-if="accion.campania">
              <dt class="text-slate-500 mb-0.5">Campaña</dt>
              <dd class="text-indigo-700 font-medium">{{ accion.campania.nombre }}</dd>
            </div>
            <div v-if="accion.presupuestoEstimado">
              <dt class="text-slate-500 mb-0.5">Presupuesto estimado</dt>
              <dd class="text-slate-900 font-medium">{{ Number(accion.presupuestoEstimado).toFixed(2) }} €</dd>
            </div>
          </dl>
        </div>
      </AccordionPanel>

      <!-- Panel 2: Preparación (tareas) -->
      <AccordionPanel title="Preparación" :count="accion.tareas?.length || 0">
        <template #actions>
          <button v-if="!formTareaNew.visible && faseActual !== 'diseno'"
            @click="formTareaNew.visible = true"
            class="inline-flex items-center gap-1 h-8 px-3 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium rounded-lg transition-colors">
            <PlusIcon class="w-3 h-3" />
            Nueva tarea
          </button>
        </template>

        <div v-if="faseActual === 'diseno'" class="px-5 py-6 text-center text-sm text-slate-400">
          Las tareas se gestionan una vez aprobada la actividad.
        </div>
        <template v-else>
          <!-- Formulario nueva tarea -->
          <div v-if="formTareaNew.visible" class="border-b border-slate-100 bg-slate-50 px-5 py-4 space-y-3">
            <div class="grid grid-cols-12 gap-3">
              <div class="col-span-12">
                <label class="block text-xs font-medium text-slate-700 mb-1">Título *</label>
                <input v-model="formTareaNew.titulo" type="text"
                  class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white" />
              </div>
              <div class="col-span-12">
                <label class="block text-xs font-medium text-slate-700 mb-1">Descripción</label>
                <textarea v-model="formTareaNew.descripcion" rows="2"
                  class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"></textarea>
              </div>
              <div class="col-span-3">
                <label class="block text-xs font-medium text-slate-700 mb-1">Estado</label>
                <select v-model="formTareaNew.estadoId" class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <option value="">—</option>
                  <option v-for="e in estadosTarea" :key="e.id" :value="e.id">{{ e.nombre }}</option>
                </select>
              </div>
              <div class="col-span-3">
                <label class="block text-xs font-medium text-slate-700 mb-1">Prioridad</label>
                <select v-model.number="formTareaNew.prioridad" class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <option :value="1">Alta</option>
                  <option :value="2">Media</option>
                  <option :value="3">Baja</option>
                </select>
              </div>
              <div class="col-span-3">
                <label class="block text-xs font-medium text-slate-700 mb-1">Horas estimadas</label>
                <input v-model.number="formTareaNew.horasEstimadas" type="number" min="0" step="0.5"
                  class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <div class="col-span-3">
                <label class="block text-xs font-medium text-slate-700 mb-1">Fecha límite</label>
                <input v-model="formTareaNew.fechaLimite" type="date"
                  class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <div class="col-span-4">
                <label class="block text-xs font-medium text-slate-700 mb-1">
                  Responsable
                  <span v-if="formTareaNew.habilidadId" class="text-indigo-500 font-normal text-[10px]">(perfil requerido)</span>
                </label>
                <select v-model="formTareaNew.responsableId" class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <option value="">— Sin asignar —</option>
                  <option v-for="m in miembrosParaTarea(formTareaNew.habilidadId, formTareaNew.nivelHabilidadId)" :key="m.id" :value="m.id">{{ m.nombre }} {{ m.apellido1 }}</option>
                </select>
              </div>
              <div class="col-span-4">
                <label class="block text-xs font-medium text-slate-700 mb-1">Habilidad requerida</label>
                <select v-model="formTareaNew.habilidadId" class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <option value="">— Ninguna —</option>
                  <option v-for="h in habilidades" :key="h.id" :value="h.id">{{ h.nombre }}</option>
                </select>
              </div>
              <div class="col-span-4">
                <label class="block text-xs font-medium text-slate-700 mb-1">Nivel requerido</label>
                <select v-model="formTareaNew.nivelHabilidadId" :disabled="!formTareaNew.habilidadId"
                  class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50">
                  <option value="">— Cualquiera —</option>
                  <option v-for="n in nivelesHabilidad" :key="n.id" :value="n.id">{{ n.nombre }}</option>
                </select>
              </div>
            </div>
            <div class="flex justify-end gap-2 pt-2 border-t border-slate-100">
              <button type="button" @click="formTareaNew = { ...emptyTareaForm(), visible: false, guardando: false }"
                class="h-9 px-3 text-sm font-medium text-slate-600 hover:text-slate-900">Cancelar</button>
              <button type="button" @click="crearTarea"
                :disabled="!formTareaNew.titulo || formTareaNew.guardando"
                class="h-9 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg">
                {{ formTareaNew.guardando ? 'Guardando…' : 'Crear tarea' }}
              </button>
            </div>
          </div>
          <div v-if="!accion.tareas?.length && !formTareaNew.visible" class="py-8 text-center text-sm text-slate-400">No hay tareas.</div>
          <div v-else-if="accion.tareas?.length" class="divide-y divide-slate-100">
            <template v-for="tarea in accion.tareas" :key="tarea.id">
              <div v-if="editTareaId !== tarea.id" class="px-5 py-3 flex items-center gap-3">
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-slate-900 truncate">{{ tarea.titulo }}</p>
                  <p v-if="tarea.descripcion" class="text-xs text-slate-500 truncate">{{ tarea.descripcion }}</p>
                  <div class="flex items-center gap-2 mt-0.5">
                    <span v-if="tarea.habilidad" class="text-xs text-violet-600">{{ tarea.habilidad.nombre }}<template v-if="tarea.nivelHabilidad"> · {{ tarea.nivelHabilidad.nombre }}</template></span>
                    <span v-if="tarea.responsable" class="text-xs text-slate-400">{{ tarea.responsable.nombre }} {{ tarea.responsable.apellido1 }}</span>
                  </div>
                </div>
                <span class="text-xs text-slate-500 shrink-0">{{ tarea.estado?.nombre }}</span>
                <span v-if="tarea.horasEstimadas" class="text-xs font-semibold text-amber-600 shrink-0 tabular-nums">{{ tarea.horasEstimadas }}h</span>
                <span v-if="tarea.fechaLimite" class="text-xs text-slate-400 shrink-0">{{ tarea.fechaLimite }}</span>
                <RowActions @edit="abrirEditTarea(tarea)" @delete="eliminarTarea(tarea.id)"
                  confirm-title="¿Eliminar esta tarea?" :confirm-text="`«${tarea.titulo}» será eliminada.`" />
              </div>
              <div v-else class="px-5 py-4 bg-slate-50 space-y-3">
                <div class="grid grid-cols-12 gap-3">
                  <div class="col-span-12">
                    <label class="block text-xs font-medium text-slate-700 mb-1">Título</label>
                    <input v-model="formTareaEdit.titulo" type="text"
                      class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white" />
                  </div>
                  <div class="col-span-12">
                    <label class="block text-xs font-medium text-slate-700 mb-1">Descripción</label>
                    <textarea v-model="formTareaEdit.descripcion" rows="2"
                      class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"></textarea>
                  </div>
                  <div class="col-span-3">
                    <label class="block text-xs font-medium text-slate-700 mb-1">Estado</label>
                    <select v-model="formTareaEdit.estadoId" class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white">
                      <option value="">—</option>
                      <option v-for="e in estadosTarea" :key="e.id" :value="e.id">{{ e.nombre }}</option>
                    </select>
                  </div>
                  <div class="col-span-3">
                    <label class="block text-xs font-medium text-slate-700 mb-1">Prioridad</label>
                    <select v-model.number="formTareaEdit.prioridad" class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white">
                      <option :value="1">Alta</option>
                      <option :value="2">Media</option>
                      <option :value="3">Baja</option>
                    </select>
                  </div>
                  <div class="col-span-3">
                    <label class="block text-xs font-medium text-slate-700 mb-1">Horas estimadas</label>
                    <input v-model.number="formTareaEdit.horasEstimadas" type="number" min="0" step="0.5"
                      class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white" />
                  </div>
                  <div class="col-span-3">
                    <label class="block text-xs font-medium text-slate-700 mb-1">Horas reales</label>
                    <input v-model.number="formTareaEdit.horasReales" type="number" min="0" step="0.5"
                      class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white" />
                  </div>
                  <div class="col-span-4">
                    <label class="block text-xs font-medium text-slate-700 mb-1">
                      Responsable
                      <span v-if="formTareaEdit.habilidadId" class="text-indigo-500 font-normal text-[10px]">(perfil requerido)</span>
                    </label>
                    <select v-model="formTareaEdit.responsableId" class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white">
                      <option value="">— Sin asignar —</option>
                      <option v-for="m in miembrosParaTarea(formTareaEdit.habilidadId, formTareaEdit.nivelHabilidadId)" :key="m.id" :value="m.id">{{ m.nombre }} {{ m.apellido1 }}</option>
                    </select>
                  </div>
                  <div class="col-span-4">
                    <label class="block text-xs font-medium text-slate-700 mb-1">Habilidad requerida</label>
                    <select v-model="formTareaEdit.habilidadId" class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white">
                      <option value="">— Ninguna —</option>
                      <option v-for="h in habilidades" :key="h.id" :value="h.id">{{ h.nombre }}</option>
                    </select>
                  </div>
                  <div class="col-span-4">
                    <label class="block text-xs font-medium text-slate-700 mb-1">Nivel requerido</label>
                    <select v-model="formTareaEdit.nivelHabilidadId" :disabled="!formTareaEdit.habilidadId"
                      class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white disabled:opacity-50">
                      <option value="">— Cualquiera —</option>
                      <option v-for="n in nivelesHabilidad" :key="n.id" :value="n.id">{{ n.nombre }}</option>
                    </select>
                  </div>
                  <div class="col-span-4">
                    <label class="block text-xs font-medium text-slate-700 mb-1">Fecha límite</label>
                    <input v-model="formTareaEdit.fechaLimite" type="date"
                      class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white" />
                  </div>
                </div>
                <div class="flex justify-end gap-2">
                  <button type="button" @click="editTareaId = null"
                    class="h-9 px-3 text-sm font-medium text-slate-600 hover:text-slate-900">Cancelar</button>
                  <button type="button" @click="guardarEditTarea(tarea.id)"
                    class="h-9 px-4 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg">Guardar</button>
                </div>
              </div>
            </template>
          </div>
        </template>
      </AccordionPanel>

      <!-- Panel 3: Seguimiento (participantes + asistencia) -->
      <AccordionPanel title="Seguimiento" :count="accion.participaciones?.length || 0">
        <template #actions>
          <button v-if="!formParticipacion.visible && faseActual === 'seguimiento'"
            @click="formParticipacion.visible = true"
            class="inline-flex items-center gap-1 h-8 px-3 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium rounded-lg transition-colors">
            <PlusIcon class="w-3 h-3" />
            Añadir participante
          </button>
        </template>

        <div v-if="['diseno', 'aprobacion'].includes(faseActual)" class="px-5 py-6 text-center text-sm text-slate-400">
          El seguimiento de participantes se inicia cuando la actividad está en curso.
        </div>
        <template v-else>
          <!-- Formulario añadir participante -->
          <div v-if="formParticipacion.visible" class="border-b border-slate-100 bg-slate-50 px-5 py-4 space-y-4">
            <div class="flex gap-4 text-sm">
              <label class="flex items-center gap-2">
                <input type="radio" v-model="formParticipacion.tipo" value="socio" class="text-indigo-600" />
                <span>Socio / miembro</span>
              </label>
              <label class="flex items-center gap-2">
                <input type="radio" v-model="formParticipacion.tipo" value="externo" class="text-indigo-600" />
                <span>Participante externo</span>
              </label>
            </div>
            <div v-if="formParticipacion.tipo === 'socio'">
              <label class="block text-sm font-medium text-slate-700 mb-1">Miembro *</label>
              <input v-model="formParticipacion.buscar" type="text" placeholder="Buscar por nombre…"
                class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              <div v-if="miembrosFiltrados.length" class="mt-1 border border-slate-200 rounded-lg max-h-48 overflow-auto bg-white">
                <button v-for="m in miembrosFiltrados" :key="m.id" type="button" @click="seleccionarMiembro(m)"
                  class="w-full text-left px-3 py-2 text-sm hover:bg-slate-50 border-b border-slate-100 last:border-b-0"
                  :class="formParticipacion.miembroId === m.id ? 'bg-indigo-50 text-indigo-700' : 'text-slate-700'">
                  {{ m.nombre }} {{ m.apellido1 }}
                  <span class="text-xs text-slate-400 ml-2">{{ m.email }}</span>
                </button>
              </div>
            </div>
            <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Nombre *</label>
                <input v-model="formParticipacion.nombreExterno" type="text"
                  class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Email</label>
                <input v-model="formParticipacion.emailExterno" type="email"
                  class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Rol</label>
                <select v-model="formParticipacion.rol"
                  class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <option value="asistente">Asistente</option>
                  <option value="ponente">Ponente</option>
                  <option value="organizador">Organizador</option>
                  <option value="voluntario">Voluntario</option>
                </select>
              </div>
              <div class="flex items-end pb-1">
                <label class="flex items-center gap-2 text-sm">
                  <input type="checkbox" v-model="formParticipacion.confirmado" class="rounded border-slate-300 text-indigo-600" />
                  <span>Confirmado</span>
                </label>
              </div>
            </div>
            <ErrorAlert v-if="errorParticipacion" :message="errorParticipacion" />
            <div class="flex justify-end gap-2 pt-2 border-t border-slate-100">
              <button type="button" @click="cancelarParticipacion"
                class="h-10 px-4 text-sm font-medium text-slate-600 hover:text-slate-900">Cancelar</button>
              <button type="button" @click="registrarParticipacion"
                :disabled="!puedeGuardarParticipacion || formParticipacion.guardando"
                class="h-10 px-5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg">
                {{ formParticipacion.guardando ? 'Guardando…' : 'Añadir' }}
              </button>
            </div>
          </div>

          <div v-if="!accion.participaciones?.length && !formParticipacion.visible" class="py-8 text-center text-sm text-slate-400">
            No hay participantes registrados.
          </div>
          <div v-else-if="accion.participaciones?.length" class="divide-y divide-slate-100">
            <template v-for="p in accion.participaciones" :key="p.id">
              <div v-if="editParticipacionId !== p.id" class="px-5 py-3 flex items-center gap-3">
                <AvatarImg :src="p.miembro?.fotoUrl" :nombre="p.miembro?.nombre || p.nombreExterno" :apellido="p.miembro?.apellido1" size="sm" />
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-slate-900">{{ p.miembro ? `${p.miembro.nombre} ${p.miembro.apellido1}` : p.nombreExterno || '—' }}</p>
                  <p class="text-xs text-slate-500">{{ p.miembro?.email || p.emailExterno }}</p>
                </div>
                <span class="text-xs text-slate-500 shrink-0">{{ p.rol }}</span>
                <span v-if="p.confirmado" class="text-xs text-green-600 shrink-0">✓ Confirmado</span>
                <span v-if="p.asistio !== null && p.asistio !== undefined" class="text-xs shrink-0"
                  :class="p.asistio ? 'text-green-600' : 'text-red-400'">
                  {{ p.asistio ? 'Asistió' : 'No asistió' }}
                </span>
                <RowActions @edit="abrirEditParticipacion(p)" @delete="eliminarParticipacion(p.id)"
                  confirm-title="¿Eliminar participante?" :confirm-text="`«${nombreParticipacion(p)}» será eliminado.`" />
              </div>
              <div v-else class="px-5 py-3 bg-slate-50 space-y-3">
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label class="block text-xs font-medium text-slate-700 mb-1">Rol</label>
                    <select v-model="formParticipacionEdit.rol" class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white">
                      <option value="asistente">Asistente</option>
                      <option value="ponente">Ponente</option>
                      <option value="organizador">Organizador</option>
                      <option value="voluntario">Voluntario</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-slate-700 mb-1">Horas aportadas</label>
                    <input v-model.number="formParticipacionEdit.horasAportadas" type="number" min="0" step="0.5"
                      class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white" />
                  </div>
                  <label class="flex items-center gap-2 text-sm">
                    <input type="checkbox" v-model="formParticipacionEdit.confirmado" class="rounded border-slate-300 text-indigo-600" />
                    <span>Confirmado</span>
                  </label>
                  <div>
                    <label class="block text-xs font-medium text-slate-700 mb-1">Asistió</label>
                    <select v-model="formParticipacionEdit.asistio" class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white">
                      <option :value="null">— pendiente —</option>
                      <option :value="true">Sí</option>
                      <option :value="false">No</option>
                    </select>
                  </div>
                </div>
                <div class="flex justify-end gap-2">
                  <button type="button" @click="editParticipacionId = null"
                    class="h-9 px-3 text-sm font-medium text-slate-600 hover:text-slate-900">Cancelar</button>
                  <button type="button" @click="guardarEditParticipacion(p.id)"
                    class="h-9 px-4 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg">Guardar</button>
                </div>
              </div>
            </template>
          </div>
        </template>
      </AccordionPanel>

      <!-- Panel 4: Valoración y cierre -->
      <AccordionPanel title="Valoración y cierre">
        <div v-if="!['valoracion'].includes(faseActual)" class="px-5 py-6 text-center text-sm text-slate-400">
          La valoración se registra al cerrar la actividad.
        </div>
        <div v-else class="px-5 py-4 space-y-4">
          <!-- Vista valoración si ya está cerrada -->
          <div v-if="!editandoValoracion" class="space-y-3">
            <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-3 text-sm">
              <div v-if="accion.presupuestoEjecutado">
                <dt class="text-slate-500 mb-0.5">Presupuesto ejecutado</dt>
                <dd class="text-slate-900 font-medium">{{ Number(accion.presupuestoEjecutado).toFixed(2) }} €</dd>
              </div>
              <div v-if="accion.asistenciaReal !== null && accion.asistenciaReal !== undefined">
                <dt class="text-slate-500 mb-0.5">Asistencia real</dt>
                <dd class="text-slate-900 font-medium">{{ accion.asistenciaReal }}</dd>
              </div>
              <div v-if="accion.objetivosCumplidos !== null && accion.objetivosCumplidos !== undefined">
                <dt class="text-slate-500 mb-0.5">Objetivos cumplidos</dt>
                <dd :class="accion.objetivosCumplidos ? 'text-green-600' : 'text-red-500'" class="font-medium">
                  {{ accion.objetivosCumplidos ? 'Sí' : 'No' }}
                </dd>
              </div>
            </dl>
            <div v-if="accion.valoracion" class="bg-slate-50 rounded-lg px-4 py-3">
              <p class="text-xs font-medium text-slate-500 mb-1">Valoración</p>
              <p class="text-sm text-slate-800">{{ accion.valoracion }}</p>
            </div>
            <div v-if="accion.notasAprobacion" class="bg-amber-50 rounded-lg px-4 py-3">
              <p class="text-xs font-medium text-amber-600 mb-1">Notas de aprobación</p>
              <p class="text-sm text-amber-900">{{ accion.notasAprobacion }}</p>
            </div>
            <div class="flex gap-2 pt-2">
              <button @click="abrirEditValoracion"
                class="h-8 px-3 text-xs font-medium text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors">
                Editar valoración
              </button>
            </div>
          </div>
          <!-- Formulario de valoración -->
          <div v-else class="space-y-3">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-700 mb-1">Presupuesto ejecutado (€)</label>
                <input v-model.number="formValoracion.presupuestoEjecutado" type="number" min="0" step="0.01"
                  class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-700 mb-1">Asistencia real</label>
                <input v-model.number="formValoracion.asistenciaReal" type="number" min="0"
                  class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <div class="col-span-2">
                <label class="block text-xs font-medium text-slate-700 mb-1">Objetivos cumplidos</label>
                <div class="flex gap-4 mt-1">
                  <label class="flex items-center gap-2 text-sm">
                    <input type="radio" :value="true" v-model="formValoracion.objetivosCumplidos" class="text-indigo-600" /> Sí
                  </label>
                  <label class="flex items-center gap-2 text-sm">
                    <input type="radio" :value="false" v-model="formValoracion.objetivosCumplidos" class="text-indigo-600" /> No
                  </label>
                </div>
              </div>
              <div class="col-span-2">
                <label class="block text-xs font-medium text-slate-700 mb-1">Valoración</label>
                <textarea v-model="formValoracion.valoracion" rows="4"
                  class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                  placeholder="Resumen de resultados, aprendizajes, incidencias…"></textarea>
              </div>
            </div>
            <div class="flex justify-end gap-2 pt-2 border-t border-slate-100">
              <button type="button" @click="editandoValoracion = false"
                class="h-9 px-3 text-sm font-medium text-slate-600 hover:text-slate-900">Cancelar</button>
              <button type="button" @click="guardarValoracion"
                class="h-9 px-4 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg">Guardar</button>
            </div>
          </div>
        </div>
      </AccordionPanel>

      <!-- Panel 5: Documentos -->
      <AccordionPanel title="Documentos" :count="accion.documentos?.length || 0">
        <div class="px-5 py-4">
          <DocumentosPanel
            :documentos="accion.documentos || []"
            :upload-endpoint="`/upload/actividades/${accion.id}/documentos`"
            :tipo-doc-options="TIPOS_DOC_ACTIVIDAD"
            :delete-fn="eliminarDocumentoActividad"
            @change="recargarAccion"
          />
        </div>
      </AccordionPanel>

      </AccordionGroup>

    </div>
    </div>
  </AppLayout>

  <!-- Modal confirmación eliminar -->
  <ConfirmModal
    v-model="showConfirmEliminarAccion"
    title="¿Eliminar permanentemente?"
    title-soft="¿Mover a la papelera?"
    :message="accion ? `«${accion.nombre}» será eliminada.` : ''"
    @confirm="eliminarAccion"
  />

  <!-- Modal de aprobación / rechazo -->
  <div v-if="modalAprobacion.visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6 space-y-4">
      <h3 class="text-lg font-semibold text-slate-900">{{ modalAprobacion.titulo }}</h3>
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
          class="h-9 px-5 text-sm font-medium rounded-lg text-white transition-colors disabled:opacity-50"
          :class="modalAprobacion.esRechazo ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'">
          {{ cargandoTransicion ? '…' : modalAprobacion.btnLabel }}
        </button>
      </div>
    </div>
  </div>

  <!-- Modal de cierre -->
  <div v-if="modalCierre.visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-lg p-6 space-y-4">
      <h3 class="text-lg font-semibold text-slate-900">Cerrar actividad</h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label class="block text-xs font-medium text-slate-700 mb-1">Presupuesto ejecutado (€)</label>
          <input v-model.number="modalCierre.presupuestoEjecutado" type="number" min="0" step="0.01"
            class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-700 mb-1">Asistencia real</label>
          <input v-model.number="modalCierre.asistenciaReal" type="number" min="0"
            class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>
        <div class="col-span-2">
          <label class="block text-xs font-medium text-slate-700 mb-2">Objetivos cumplidos</label>
          <div class="flex gap-4">
            <label class="flex items-center gap-2 text-sm"><input type="radio" :value="true" v-model="modalCierre.objetivosCumplidos" class="text-indigo-600" /> Sí</label>
            <label class="flex items-center gap-2 text-sm"><input type="radio" :value="false" v-model="modalCierre.objetivosCumplidos" class="text-indigo-600" /> No</label>
          </div>
        </div>
        <div class="col-span-2">
          <label class="block text-xs font-medium text-slate-700 mb-1">Valoración</label>
          <textarea v-model="modalCierre.valoracion" rows="3"
            class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Resumen de resultados…"></textarea>
        </div>
      </div>
      <div class="flex justify-end gap-2 pt-2 border-t border-slate-100">
        <button @click="modalCierre.visible = false"
          class="h-9 px-4 text-sm font-medium text-slate-600 hover:text-slate-900">Cancelar</button>
        <button @click="confirmarCierre" :disabled="cargandoTransicion"
          class="h-9 px-5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg">
          {{ cargandoTransicion ? '…' : 'Cerrar actividad' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { PlusIcon, TrashIcon } from '@heroicons/vue/24/outline'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { useToast } from '@/composables/useToast'
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import AccordionPanel from '@/components/common/AccordionPanel.vue'
import AccordionGroup from '@/components/common/AccordionGroup.vue'
import WorkflowBar from '@/components/common/WorkflowBar.vue'
import RowActions from '@/components/common/RowActions.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import AvatarImg from '@/components/common/AvatarImg.vue'
import LoadSpinner from '@/components/common/LoadSpinner.vue'
import { graphqlClient } from '@/graphql/client'
import {
  GET_ACCION_BY_ID, ACTUALIZAR_ACCION, ELIMINAR_ACCION, SOFT_DELETE_ACCION,
  REGISTRAR_PARTICIPACION, ACTUALIZAR_PARTICIPACION, ELIMINAR_PARTICIPACION,
  CREAR_TAREA, ACTUALIZAR_TAREA, ELIMINAR_TAREA,
  TRANSICIONAR_ACTIVIDAD, APROBAR_ACTIVIDAD, CERRAR_ACTIVIDAD,
  ELIMINAR_DOCUMENTOS_ACTIVIDAD,
} from '../graphql/queries.js'
import DocumentosPanel from '@/components/common/DocumentosPanel.vue'

const TIPOS_DOC_ACTIVIDAD = [
  { value: 'acta',     label: 'Acta' },
  { value: 'informe',  label: 'Informe' },
  { value: 'foto',     label: 'Foto' },
  { value: 'material', label: 'Material' },
  { value: 'otro',     label: 'Otro' },
]

async function eliminarDocumentoActividad(doc) {
  await graphqlClient.request(ELIMINAR_DOCUMENTOS_ACTIVIDAD, {
    filter: { id: { eq: doc.id } },
  })
}

const toast = useToast()

const GET_CATALOGOS = `
  query CatalogosDetalleActividad {
    miembros { id nombre apellido1 email }
    estadosTarea { id nombre }
    tiposActividad { id nombre tieneLugar }
    estadosAccion { id nombre }
    habilidades(filter: { activo: { eq: true } }) { id nombre }
    nivelesHabilidad(filter: { activo: { eq: true } }) { id nombre orden }
    miembrosHabilidades { miembroId habilidadId nivelId }
  }
`

const FASES = [
  { key: 'diseno', label: 'Diseño' },
  { key: 'aprobacion', label: 'Aprobación' },
  { key: 'seguimiento', label: 'Seguimiento' },
  { key: 'valoracion', label: 'Valoración' },
]

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const accion = ref(null)
const showConfirmEliminarAccion = ref(false)
const miembros = ref([])
const estadosTarea = ref([])
const tiposActividad = ref([])
const estadosAccion = ref([])
const habilidades = ref([])
const nivelesHabilidad = ref([])
// miembroId → Set of { habilidadId, nivelHabilidadId }
const miembroHabilidadesMap = ref(new Map())
const errorParticipacion = ref('')
const cargandoTransicion = ref(false)

// Devuelve miembros que tienen la habilidad (y nivel >= requerido si se especifica)
function miembrosParaTarea(habilidadId, nivelHabilidadId) {
  if (!habilidadId) return miembros.value
  const nivelesOrdenados = [...nivelesHabilidad.value].sort((a, b) => a.orden - b.orden)
  const nivelMin = nivelHabilidadId
    ? (nivelesOrdenados.find(n => n.id === nivelHabilidadId)?.orden ?? 0)
    : 0
  return miembros.value.filter(m => {
    const habs = miembroHabilidadesMap.value.get(m.id) || []
    return habs.some(h => {
      if (h.habilidadId !== habilidadId) return false
      if (!nivelHabilidadId) return true
      const ordenHab = nivelesOrdenados.find(n => n.id === h.nivelHabilidadId)?.orden ?? 0
      return ordenHab >= nivelMin
    })
  })
}

// Mapeo estado → fase
function estadoAFase(nombre) {
  const n = (nombre || '').toLowerCase()
  if (n.includes('propuest')) return 'diseno'
  if (n.includes('pendiente') || n.includes('aprobad')) return 'aprobacion'
  if (n.includes('preparac') || n.includes('curso')) return 'seguimiento'
  if (n.includes('finaliz') || n.includes('cancelad')) return 'valoracion'
  return 'diseno'
}

const faseActual = computed(() => estadoAFase(accion.value?.estado?.nombre))
const faseEditable = computed(() => ['diseno', 'aprobacion'].includes(faseActual.value))
const esFinal = computed(() => {
  const n = (accion.value?.estado?.nombre || '').toLowerCase()
  return n.includes('finaliz') || n.includes('cancelad')
})

// Transitions disponibles según estado actual
const transicionesDisponibles = computed(() => {
  if (!accion.value || !estadosAccion.value.length) return []
  const n = (accion.value.estado?.nombre || '').toLowerCase()
  const find = (nombre) => estadosAccion.value.find(e => e.nombre.toLowerCase().includes(nombre))

  if (n.includes('propuest')) {
    const pendiente = find('pendiente')
    return pendiente ? [{ label: 'Enviar para aprobación', estado: pendiente, icono: 'send', tipo: 'transicion' }] : []
  }
  if (n.includes('pendiente')) {
    const aprobada = find('aprobad')
    return [
      aprobada ? { label: 'Aprobar', estado: aprobada, icono: 'check', tipo: 'aprobar', estilo: 'bg-green-50 text-green-700 hover:bg-green-100' } : null,
      { label: 'Devolver', estado: estadosAccion.value.find(e => e.nombre.toLowerCase().includes('propuest')), icono: 'reject', tipo: 'transicion', estilo: 'bg-red-50 text-red-700 hover:bg-red-100' },
    ].filter(Boolean)
  }
  if (n.includes('aprobad')) {
    const prep = find('preparac')
    return prep ? [{ label: 'Iniciar preparación', estado: prep, icono: 'play', tipo: 'transicion' }] : []
  }
  if (n.includes('preparac')) {
    const curso = find('curso')
    return curso ? [{ label: 'Iniciar actividad', estado: curso, icono: 'play', tipo: 'transicion' }] : []
  }
  if (n.includes('curso')) {
    const final = find('finaliz')
    return final ? [{ label: 'Cerrar actividad', estado: final, icono: 'close', tipo: 'cerrar' }] : []
  }
  return []
})

// Modales
const modalAprobacion = ref({ visible: false, titulo: '', notas: '', placeholder: '', btnLabel: '', esRechazo: false, estadoId: null, tipo: '' })
const modalCierre = ref({ visible: false, valoracion: '', objetivosCumplidos: null, presupuestoEjecutado: null, asistenciaReal: null, estadoId: null })

async function ejecutarTransicion(t) {
  if (t.tipo === 'aprobar') {
    modalAprobacion.value = {
      visible: true, titulo: 'Aprobar actividad', notas: '',
      placeholder: 'Observaciones de la aprobación…', btnLabel: 'Aprobar',
      esRechazo: false, estadoId: t.estado.id, tipo: 'aprobar'
    }
  } else if (t.tipo === 'cerrar') {
    modalCierre.value = { visible: true, valoracion: '', objetivosCumplidos: null, presupuestoEjecutado: null, asistenciaReal: null, estadoId: t.estado.id }
  } else if (t.tipo === 'transicion' && t.icono === 'reject') {
    modalAprobacion.value = {
      visible: true, titulo: 'Devolver a diseño', notas: '',
      placeholder: 'Indicar motivo de devolución…', btnLabel: 'Devolver',
      esRechazo: true, estadoId: t.estado.id, tipo: 'transicion'
    }
  } else {
    cargandoTransicion.value = true
    try {
      await graphqlClient.request(TRANSICIONAR_ACTIVIDAD, { id: accion.value.id, estadoId: t.estado.id })
      await recargarAccion()
    } catch (e) {
      toast.error(e?.response?.errors?.[0]?.message || 'Error en la transición')
    } finally {
      cargandoTransicion.value = false
    }
  }
}

async function confirmarAprobacion() {
  cargandoTransicion.value = true
  try {
    const mut = modalAprobacion.value.tipo === 'aprobar' ? APROBAR_ACTIVIDAD : TRANSICIONAR_ACTIVIDAD
    await graphqlClient.request(mut, {
      id: accion.value.id,
      estadoId: modalAprobacion.value.estadoId,
      notas: modalAprobacion.value.notas || null,
    })
    modalAprobacion.value.visible = false
    await recargarAccion()
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error en la operación')
  } finally {
    cargandoTransicion.value = false
  }
}

async function confirmarCierre() {
  cargandoTransicion.value = true
  try {
    await graphqlClient.request(CERRAR_ACTIVIDAD, {
      id: accion.value.id,
      estadoId: modalCierre.value.estadoId,
      valoracion: modalCierre.value.valoracion || null,
      objetivosCumplidos: modalCierre.value.objetivosCumplidos,
      asistenciaReal: modalCierre.value.asistenciaReal || null,
      presupuestoEjecutado: modalCierre.value.presupuestoEjecutado || null,
    })
    modalCierre.value.visible = false
    await recargarAccion()
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error al cerrar')
  } finally {
    cargandoTransicion.value = false
  }
}

// Valoración inline
const editandoValoracion = ref(false)
const formValoracion = ref({ valoracion: '', objetivosCumplidos: null, presupuestoEjecutado: null, asistenciaReal: null })

function abrirEditValoracion() {
  formValoracion.value = {
    valoracion: accion.value.valoracion || '',
    objetivosCumplidos: accion.value.objetivosCumplidos,
    presupuestoEjecutado: accion.value.presupuestoEjecutado || null,
    asistenciaReal: accion.value.asistenciaReal || null,
  }
  editandoValoracion.value = true
}

async function guardarValoracion() {
  try {
    await graphqlClient.request(CERRAR_ACTIVIDAD, {
      id: accion.value.id,
      estadoId: accion.value.estado.id,
      valoracion: formValoracion.value.valoracion || null,
      objetivosCumplidos: formValoracion.value.objetivosCumplidos,
      asistenciaReal: formValoracion.value.asistenciaReal || null,
      presupuestoEjecutado: formValoracion.value.presupuestoEjecutado || null,
    })
    await recargarAccion()
    editandoValoracion.value = false
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error guardando valoración')
  }
}

// edición acción
const editandoAccion = ref(false)
const formAccionEdit = ref({})

function abrirEditAccion() {
  formAccionEdit.value = {
    nombre: accion.value.nombre,
    tipoActividadId: accion.value.tipoActividad?.id || '',
    responsableId: accion.value.responsable?.id || '',
    descripcion: accion.value.descripcion || '',
    fechaInicio: accion.value.fechaInicio || '',
    horaInicio: accion.value.horaInicio || '',
    fechaFin: accion.value.fechaFin || '',
    horaFin: accion.value.horaFin || '',
    duracionHoras: accion.value.duracionHoras ?? null,
    duracionDias: accion.value.duracionDias ?? null,
    lugar: accion.value.lugar || '',
    direccion: accion.value.direccion || '',
    localidad: accion.value.localidad || '',
    provincia: accion.value.provincia || '',
    aforo: accion.value.aforo || null,
    esOnline: accion.value.esOnline || false,
    urlOnline: accion.value.urlOnline || '',
    presupuestoEstimado: accion.value.presupuestoEstimado || null,
  }
  editandoAccion.value = true
}

async function guardarEditAccion() {
  try {
    await graphqlClient.request(ACTUALIZAR_ACCION, { data: { id: accion.value.id, ...formAccionEdit.value } })
    await recargarAccion()
    editandoAccion.value = false
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error guardando actividad')
  }
}

async function eliminarAccion({ hardDelete } = {}) {
  try {
    if (hardDelete) {
      await graphqlClient.request(ELIMINAR_ACCION, { id: accion.value.id })
    } else {
      await graphqlClient.request(SOFT_DELETE_ACCION, { id: accion.value.id })
    }
    router.push('/actividades')
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error eliminando actividad')
  }
}

// Tareas
const editTareaId = ref(null)
const emptyTareaForm = () => ({
  titulo: '', descripcion: '', estadoId: '', prioridad: 2,
  responsableId: '', habilidadId: '', nivelHabilidadId: '',
  horasEstimadas: null, horasReales: null, fechaLimite: '',
})
const formTareaEdit = ref(emptyTareaForm())
const formTareaNew = ref({ ...emptyTareaForm(), visible: false, guardando: false })

function tareaToData(f) {
  return {
    titulo: f.titulo,
    descripcion: f.descripcion || null,
    estadoId: f.estadoId || null,
    prioridad: f.prioridad || 2,
    responsableId: f.responsableId || null,
    habilidadId: f.habilidadId || null,
    nivelHabilidadId: f.nivelHabilidadId || null,
    horasEstimadas: f.horasEstimadas || null,
    horasReales: f.horasReales || null,
    fechaLimite: f.fechaLimite || null,
  }
}

async function crearTarea() {
  if (!formTareaNew.value.titulo) return
  formTareaNew.value.guardando = true
  try {
    await graphqlClient.request(CREAR_TAREA, {
      data: { ...tareaToData(formTareaNew.value), actividadId: accion.value.id },
    })
    await recargarAccion()
    formTareaNew.value = { ...emptyTareaForm(), visible: false, guardando: false }
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error creando tarea')
  } finally {
    formTareaNew.value.guardando = false
  }
}

function abrirEditTarea(t) {
  formTareaEdit.value = {
    titulo: t.titulo,
    descripcion: t.descripcion || '',
    estadoId: t.estado?.id || '',
    prioridad: t.prioridad ?? 2,
    responsableId: t.responsable?.id || '',
    habilidadId: t.habilidad?.id || '',
    nivelHabilidadId: t.nivelHabilidad?.id || '',
    horasEstimadas: t.horasEstimadas ?? null,
    horasReales: t.horasReales ?? null,
    fechaLimite: t.fechaLimite || '',
  }
  editTareaId.value = t.id
}

async function guardarEditTarea(id) {
  try {
    await graphqlClient.request(ACTUALIZAR_TAREA, {
      data: { id, ...tareaToData(formTareaEdit.value) },
    })
    await recargarAccion()
    editTareaId.value = null
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error guardando tarea')
  }
}

async function eliminarTarea(id) {
  try {
    await graphqlClient.request(ELIMINAR_TAREA, { id })
    await recargarAccion()
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error eliminando tarea')
  }
}

// Participaciones
const editParticipacionId = ref(null)
const formParticipacionEdit = ref({ rol: 'asistente', confirmado: false, asistio: null, horasAportadas: 0 })
const formParticipacion = ref({
  visible: false, tipo: 'socio', buscar: '', miembroId: '',
  nombreExterno: '', emailExterno: '', rol: 'asistente', confirmado: false, guardando: false,
})

function nombreParticipacion(p) {
  return p.miembro ? `${p.miembro.nombre} ${p.miembro.apellido1}` : (p.nombreExterno || '—')
}

function abrirEditParticipacion(p) {
  formParticipacionEdit.value = { rol: p.rol, confirmado: p.confirmado, asistio: p.asistio, horasAportadas: Number(p.horasAportadas || 0) }
  editParticipacionId.value = p.id
}

async function guardarEditParticipacion(id) {
  try {
    await graphqlClient.request(ACTUALIZAR_PARTICIPACION, {
      data: { id, rol: formParticipacionEdit.value.rol, confirmado: formParticipacionEdit.value.confirmado, asistio: formParticipacionEdit.value.asistio, horasAportadas: formParticipacionEdit.value.horasAportadas },
    })
    await recargarAccion()
    editParticipacionId.value = null
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error guardando participación')
  }
}

async function eliminarParticipacion(id) {
  try {
    await graphqlClient.request(ELIMINAR_PARTICIPACION, { id })
    await recargarAccion()
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'Error eliminando participación')
  }
}

const miembrosFiltrados = computed(() => {
  const q = formParticipacion.value.buscar.trim().toLowerCase()
  if (!q) return miembros.value.slice(0, 10)
  return miembros.value.filter(m => `${m.nombre} ${m.apellido1} ${m.email || ''}`.toLowerCase().includes(q)).slice(0, 10)
})

const puedeGuardarParticipacion = computed(() => {
  const f = formParticipacion.value
  return f.tipo === 'socio' ? !!f.miembroId : !!f.nombreExterno
})

function seleccionarMiembro(m) {
  formParticipacion.value.miembroId = m.id
  formParticipacion.value.buscar = `${m.nombre} ${m.apellido1}`
}

function cancelarParticipacion() {
  formParticipacion.value = { visible: false, tipo: 'socio', buscar: '', miembroId: '', nombreExterno: '', emailExterno: '', rol: 'asistente', confirmado: false, guardando: false }
  errorParticipacion.value = ''
}

async function registrarParticipacion() {
  const f = formParticipacion.value
  f.guardando = true
  errorParticipacion.value = ''
  try {
    await graphqlClient.request(REGISTRAR_PARTICIPACION, {
      data: {
        actividadId: accion.value.id,
        rol: f.rol,
        confirmado: f.confirmado,
        miembroId: f.tipo === 'socio' ? f.miembroId : null,
        nombreExterno: f.tipo === 'externo' ? f.nombreExterno : null,
        emailExterno: f.tipo === 'externo' ? (f.emailExterno || null) : null,
      },
    })
    await recargarAccion()
    cancelarParticipacion()
  } catch (e) {
    errorParticipacion.value = e?.response?.errors?.[0]?.message || 'Error al añadir participante'
  } finally {
    f.guardando = false
  }
}

async function recargarAccion() {
  const res = await graphqlClient.request(GET_ACCION_BY_ID, { id: route.params.id })
  accion.value = res.actividades?.[0] || null
}

onMounted(async () => {
  try {
    const [resAccion, resCat] = await Promise.all([
      graphqlClient.request(GET_ACCION_BY_ID, { id: route.params.id }),
      graphqlClient.request(GET_CATALOGOS),
    ])
    accion.value = resAccion.actividades?.[0] || null
    miembros.value = resCat.miembros || []
    estadosTarea.value = resCat.estadosTarea || []
    tiposActividad.value = resCat.tiposActividad || []
    estadosAccion.value = resCat.estadosAccion || []
    habilidades.value = resCat.habilidades || []
    nivelesHabilidad.value = (resCat.nivelesHabilidad || []).sort((a, b) => a.orden - b.orden)
    const mhMap = new Map()
    for (const mh of (resCat.miembrosHabilidades || [])) {
      if (!mhMap.has(mh.miembroId)) mhMap.set(mh.miembroId, [])
      mhMap.get(mh.miembroId).push({ habilidadId: mh.habilidadId, nivelHabilidadId: mh.nivelId })
    }
    miembroHabilidadesMap.value = mhMap
  } catch (e) {
    // Sin esto, un error de query dejaba accion=null y la vista mostraba
    // "Actividad no encontrada" ocultando la causa real.
    console.error('Error cargando el detalle de la actividad:', e?.response?.errors || e)
  } finally {
    loading.value = false
  }
})
</script>
