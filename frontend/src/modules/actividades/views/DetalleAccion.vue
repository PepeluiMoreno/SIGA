<template>
  <AppLayout :title="accion?.nombre || 'Acción'" :subtitle="accion?.tipoAccion?.nombre || ''">
    <div class="max-w-5xl">

    <div v-if="accion" class="space-y-4">
      <!-- Panel: Información -->
      <AccordionPanel title="Información">
        <template #actions>
          <template v-if="!editandoAccion">
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
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
              Eliminar
            </button>
          </template>
        </template>

        <!-- Formulario edición -->
        <div v-if="editandoAccion" class="px-5 py-4 space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="sm:col-span-2">
              <label class="block text-xs font-medium text-slate-700 mb-1">Nombre *</label>
              <input v-model="formAccionEdit.nombre" type="text"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Tipo</label>
              <select v-model="formAccionEdit.tipoAccionId"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option v-for="t in tiposAccion" :key="t.id" :value="t.id">{{ t.nombre }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Estado</label>
              <select v-model="formAccionEdit.estadoId"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option v-for="e in estadosAccion" :key="e.id" :value="e.id">{{ e.nombre }}</option>
              </select>
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-medium text-slate-700 mb-1">Descripción</label>
              <textarea v-model="formAccionEdit.descripcion" rows="3"
                class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"></textarea>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Fecha inicio</label>
              <input v-model="formAccionEdit.fechaInicio" type="date"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Hora inicio</label>
              <input v-model="formAccionEdit.horaInicio" type="time"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Fecha fin</label>
              <input v-model="formAccionEdit.fechaFin" type="date"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Hora fin</label>
              <input v-model="formAccionEdit.horaFin" type="time"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Lugar</label>
              <input v-model="formAccionEdit.lugar" type="text"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Aforo</label>
              <input v-model.number="formAccionEdit.aforo" type="number" min="0"
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
          <dl class="px-5 py-4 grid grid-cols-2 gap-x-8 gap-y-3 text-sm">
            <div v-if="accion.fechaInicio">
              <dt class="text-slate-500 mb-0.5">Fecha inicio</dt>
              <dd class="text-slate-900 font-medium">{{ accion.fechaInicio }}<span v-if="accion.horaInicio" class="ml-1 text-slate-500">{{ accion.horaInicio }}</span></dd>
            </div>
            <div v-if="accion.fechaFin">
              <dt class="text-slate-500 mb-0.5">Fecha fin</dt>
              <dd class="text-slate-900 font-medium">{{ accion.fechaFin }}<span v-if="accion.horaFin" class="ml-1 text-slate-500">{{ accion.horaFin }}</span></dd>
            </div>
            <div v-if="accion.lugar">
              <dt class="text-slate-500 mb-0.5">Lugar</dt>
              <dd class="text-slate-900 font-medium">{{ accion.lugar }}</dd>
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
            <div v-if="accion.iniciativa">
              <dt class="text-slate-500 mb-0.5">Campaña</dt>
              <dd class="text-slate-900 font-medium">{{ accion.iniciativa.nombre }}</dd>
            </div>
            <div v-if="accion.presupuestoEstimado">
              <dt class="text-slate-500 mb-0.5">Presupuesto estimado</dt>
              <dd class="text-slate-900 font-medium">{{ accion.presupuestoEstimado }} €</dd>
            </div>
          </dl>
        </div>
      </AccordionPanel>

      <!-- Panel: Tareas -->
      <AccordionPanel title="Tareas" :count="accion.tareas?.length || 0">
        <template #actions>
          <button
            v-if="!formTareaNew.visible"
            @click="formTareaNew.visible = true"
            class="inline-flex items-center gap-1 h-8 px-3 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium rounded-lg transition-colors"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            Nueva
          </button>
        </template>

        <!-- Formulario nueva tarea -->
        <div v-if="formTareaNew.visible" class="border-b border-slate-100 bg-slate-50 px-5 py-4 space-y-3">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="sm:col-span-2">
              <label class="block text-xs font-medium text-slate-700 mb-1">Título *</label>
              <input v-model="formTareaNew.titulo" type="text"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Estado</label>
              <select v-model="formTareaNew.estadoId"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option v-for="e in estadosTarea" :key="e.id" :value="e.id">{{ e.nombre }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Fecha límite</label>
              <input v-model="formTareaNew.fechaLimite" type="date"
                class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
          </div>
          <div class="flex justify-end gap-2 pt-2 border-t border-slate-100">
            <button type="button" @click="formTareaNew = { visible: false, titulo: '', estadoId: '', fechaLimite: '' }"
              class="h-9 px-3 text-sm font-medium text-slate-600 hover:text-slate-900">Cancelar</button>
            <button type="button" @click="crearTarea"
              :disabled="!formTareaNew.titulo || formTareaNew.guardando"
              class="h-9 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg">
              {{ formTareaNew.guardando ? 'Guardando…' : 'Crear tarea' }}
            </button>
          </div>
        </div>

        <div v-if="!accion.tareas?.length && !formTareaNew.visible" class="py-8 text-center text-sm text-slate-400">
          No hay tareas registradas.
        </div>
        <div v-else-if="accion.tareas?.length" class="divide-y divide-slate-100">
          <template v-for="tarea in accion.tareas" :key="tarea.id">
            <!-- Vista normal -->
            <div v-if="editTareaId !== tarea.id" class="px-5 py-3 flex items-center gap-4">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-slate-900 truncate">{{ tarea.titulo }}</p>
                <p v-if="tarea.descripcion" class="text-xs text-slate-500 truncate">{{ tarea.descripcion }}</p>
              </div>
              <span class="text-xs text-slate-500 shrink-0">{{ tarea.estado?.nombre }}</span>
              <span v-if="tarea.fechaLimite" class="text-xs text-slate-400 shrink-0">{{ tarea.fechaLimite }}</span>
              <RowActions
                @edit="abrirEditTarea(tarea)"
                @delete="eliminarTarea(tarea.id)"
                confirm-title="¿Eliminar esta tarea?"
                :confirm-text="`«${tarea.titulo}» será eliminada permanentemente.`"
              />
            </div>
            <!-- Edit inline -->
            <div v-else class="px-5 py-3 bg-slate-50 space-y-3">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div class="sm:col-span-2">
                  <label class="block text-xs font-medium text-slate-700 mb-1">Título</label>
                  <input v-model="formTareaEdit.titulo" type="text"
                    class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-700 mb-1">Estado</label>
                  <select v-model="formTareaEdit.estadoId" class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white">
                    <option v-for="e in estadosTarea" :key="e.id" :value="e.id">{{ e.nombre }}</option>
                  </select>
                </div>
                <div>
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
      </AccordionPanel>

      <!-- Panel: Participantes -->
      <AccordionPanel title="Participantes" :count="accion.participaciones?.length || 0">
        <template #actions>
          <button
            v-if="!formParticipacion.visible"
            @click="formParticipacion.visible = true"
            class="inline-flex items-center gap-1 h-8 px-3 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium rounded-lg transition-colors"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            Añadir
          </button>
        </template>

        <!-- Formulario añadir -->
        <div v-if="formParticipacion.visible" class="border-b border-slate-100 bg-slate-50 px-5 py-4 space-y-4">
          <!-- Tipo: socio o externo -->
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

          <!-- Socio: selector -->
          <div v-if="formParticipacion.tipo === 'socio'">
            <label class="block text-sm font-medium text-slate-700 mb-1">Miembro *</label>
            <input
              v-model="formParticipacion.buscar"
              type="text"
              placeholder="Buscar por nombre…"
              class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <div v-if="miembrosFiltrados.length" class="mt-1 border border-slate-200 rounded-lg max-h-48 overflow-auto bg-white">
              <button
                v-for="m in miembrosFiltrados"
                :key="m.id"
                type="button"
                @click="seleccionarMiembro(m)"
                class="w-full text-left px-3 py-2 text-sm hover:bg-slate-50 border-b border-slate-100 last:border-b-0"
                :class="formParticipacion.miembroId === m.id ? 'bg-indigo-50 text-indigo-700' : 'text-slate-700'"
              >
                {{ m.nombre }} {{ m.apellido1 }}
                <span class="text-xs text-slate-400 ml-2">{{ m.email }}</span>
              </button>
            </div>
          </div>

          <!-- Externo: nombre + email -->
          <div v-else class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Nombre *</label>
              <input
                v-model="formParticipacion.nombreExterno"
                type="text"
                class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Email</label>
              <input
                v-model="formParticipacion.emailExterno"
                type="email"
                class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <!-- Rol y confirmado -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Rol</label>
              <select
                v-model="formParticipacion.rol"
                class="w-full h-10 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
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

          <div v-if="errorParticipacion" class="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{{ errorParticipacion }}</div>

          <div class="flex justify-end gap-2 pt-2 border-t border-slate-100">
            <button
              type="button"
              @click="cancelarParticipacion"
              class="h-10 px-4 text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="button"
              @click="registrarParticipacion"
              :disabled="!puedeGuardarParticipacion || formParticipacion.guardando"
              class="h-10 px-5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
            >
              {{ formParticipacion.guardando ? 'Guardando…' : 'Añadir' }}
            </button>
          </div>
        </div>

        <!-- Lista -->
        <div v-if="!accion.participaciones?.length && !formParticipacion.visible" class="py-8 text-center text-sm text-slate-400">
          No hay participantes registrados.
        </div>
        <div v-else-if="accion.participaciones?.length" class="divide-y divide-slate-100">
          <template v-for="p in accion.participaciones" :key="p.id">
            <!-- Vista normal -->
            <div v-if="editParticipacionId !== p.id" class="px-5 py-3 flex items-center gap-3">
              <AvatarImg
                :src="p.miembro?.fotoUrl"
                :nombre="p.miembro?.nombre || p.nombreExterno"
                :apellido="p.miembro?.apellido1"
                size="sm"
              />
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-slate-900">
                  {{ p.miembro ? `${p.miembro.nombre} ${p.miembro.apellido1}` : p.nombreExterno || '—' }}
                </p>
                <p class="text-xs text-slate-500">{{ p.miembro?.email || p.emailExterno }}</p>
              </div>
              <span class="text-xs text-slate-500 shrink-0">{{ p.rol }}</span>
              <span v-if="p.confirmado" class="text-xs text-green-600 shrink-0">✓ Confirmado</span>
              <span v-if="p.asistio !== null" class="text-xs shrink-0" :class="p.asistio ? 'text-green-600' : 'text-red-400'">
                {{ p.asistio ? 'Asistió' : 'No asistió' }}
              </span>
              <RowActions
                @edit="abrirEditParticipacion(p)"
                @delete="eliminarParticipacion(p.id)"
                confirm-title="¿Eliminar participante?"
                :confirm-text="`«${nombreParticipacion(p)}» será eliminado de la acción.`"
              />
            </div>
            <!-- Edit inline -->
            <div v-else class="px-5 py-3 bg-slate-50 space-y-3">
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-xs font-medium text-slate-700 mb-1">Rol</label>
                  <select v-model="formParticipacionEdit.rol"
                    class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white">
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
                  <select v-model="formParticipacionEdit.asistio"
                    class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg bg-white">
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
      </AccordionPanel>
    </div>
    </div>
  </AppLayout>

  <ConfirmModal
    v-model="showConfirmEliminarAccion"
    title="¿Eliminar permanentemente?"
    title-soft="¿Mover a la papelera?"
    :message="accion ? `«${accion.nombre}» será eliminada permanentemente.` : ''"
    @confirm="eliminarAccion"
  />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import AccordionPanel from '@/components/common/AccordionPanel.vue'
import RowActions from '@/components/common/RowActions.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import AvatarImg from '@/components/common/AvatarImg.vue'
import { graphqlClient } from '@/graphql/client'
import {
  GET_ACCION_BY_ID, ACTUALIZAR_ACCION, ELIMINAR_ACCION, SOFT_DELETE_ACCION,
  REGISTRAR_PARTICIPACION, ACTUALIZAR_PARTICIPACION, ELIMINAR_PARTICIPACION,
  CREAR_TAREA, ACTUALIZAR_TAREA, ELIMINAR_TAREA,
} from '../graphql/queries.js'

const GET_CATALOGOS = `
  query CatalogosDetalleAccion {
    miembros { id nombre apellido1 email }
    estadosTarea { id nombre }
    tiposAccion { id nombre tieneLugar }
    estadosAccion { id nombre }
  }
`

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const accion = ref(null)
const showConfirmEliminarAccion = ref(false)
const miembros = ref([])
const estadosTarea = ref([])
const tiposAccion = ref([])
const estadosAccion = ref([])
const errorParticipacion = ref('')

// edición acción
const editandoAccion = ref(false)
const formAccionEdit = ref({})

function abrirEditAccion() {
  formAccionEdit.value = {
    nombre: accion.value.nombre,
    tipoAccionId: accion.value.tipoAccion?.id || '',
    estadoId: accion.value.estado?.id || '',
    descripcion: accion.value.descripcion || '',
    fechaInicio: accion.value.fechaInicio || '',
    horaInicio: accion.value.horaInicio || '',
    fechaFin: accion.value.fechaFin || '',
    horaFin: accion.value.horaFin || '',
    lugar: accion.value.lugar || '',
    aforo: accion.value.aforo || null,
    esOnline: accion.value.esOnline || false,
    urlOnline: accion.value.urlOnline || '',
    presupuestoEstimado: accion.value.presupuestoEstimado || null,
  }
  editandoAccion.value = true
}

async function guardarEditAccion() {
  try {
    await graphqlClient.request(ACTUALIZAR_ACCION, {
      data: { id: accion.value.id, ...formAccionEdit.value },
    })
    await recargarAccion()
    editandoAccion.value = false
  } catch (e) {
    alert(e?.response?.errors?.[0]?.message || 'Error guardando acción')
  }
}

async function eliminarAccion({ hardDelete } = {}) {
  try {
    if (hardDelete) {
      await graphqlClient.request(ELIMINAR_ACCION, { id: accion.value.id })
    } else {
      await graphqlClient.request(SOFT_DELETE_ACCION, { id: accion.value.id })
    }
    router.push('/acciones')
  } catch (e) {
    alert(e?.response?.errors?.[0]?.message || 'Error eliminando acción')
  }
}

// edición inline tareas
const editTareaId = ref(null)
const formTareaEdit = ref({ titulo: '', estadoId: '', fechaLimite: '' })
const formTareaNew = ref({ visible: false, titulo: '', estadoId: '', fechaLimite: '', guardando: false })

async function crearTarea() {
  if (!formTareaNew.value.titulo) return
  formTareaNew.value.guardando = true
  try {
    await graphqlClient.request(CREAR_TAREA, {
      data: {
        titulo: formTareaNew.value.titulo,
        estadoId: formTareaNew.value.estadoId || null,
        fechaLimite: formTareaNew.value.fechaLimite || null,
        accionId: accion.value.id,
      },
    })
    await recargarAccion()
    formTareaNew.value = { visible: false, titulo: '', estadoId: '', fechaLimite: '', guardando: false }
  } catch (e) {
    alert(e?.response?.errors?.[0]?.message || 'Error creando tarea')
  } finally {
    formTareaNew.value.guardando = false
  }
}

// edición inline participaciones
const editParticipacionId = ref(null)
const formParticipacionEdit = ref({ rol: 'asistente', confirmado: false, asistio: null, horasAportadas: 0 })

function nombreParticipacion(p) {
  return p.miembro ? `${p.miembro.nombre} ${p.miembro.apellido1}` : (p.nombreExterno || '—')
}

function abrirEditTarea(t) {
  formTareaEdit.value = {
    titulo: t.titulo,
    estadoId: t.estado?.id || '',
    fechaLimite: t.fechaLimite || '',
  }
  editTareaId.value = t.id
}

async function guardarEditTarea(id) {
  try {
    await graphqlClient.request(ACTUALIZAR_TAREA, {
      data: {
        id,
        titulo: formTareaEdit.value.titulo,
        estadoId: formTareaEdit.value.estadoId,
        fechaLimite: formTareaEdit.value.fechaLimite || null,
      },
    })
    await recargarAccion()
    editTareaId.value = null
  } catch (e) {
    alert(e?.response?.errors?.[0]?.message || 'Error guardando tarea')
  }
}

async function eliminarTarea(id) {
  try {
    await graphqlClient.request(ELIMINAR_TAREA, { id })
    await recargarAccion()
  } catch (e) {
    alert(e?.response?.errors?.[0]?.message || 'Error eliminando tarea')
  }
}

function abrirEditParticipacion(p) {
  formParticipacionEdit.value = {
    rol: p.rol,
    confirmado: p.confirmado,
    asistio: p.asistio,
    horasAportadas: Number(p.horasAportadas || 0),
  }
  editParticipacionId.value = p.id
}

async function guardarEditParticipacion(id) {
  try {
    await graphqlClient.request(ACTUALIZAR_PARTICIPACION, {
      data: {
        id,
        rol: formParticipacionEdit.value.rol,
        confirmado: formParticipacionEdit.value.confirmado,
        asistio: formParticipacionEdit.value.asistio,
        horasAportadas: formParticipacionEdit.value.horasAportadas,
      },
    })
    await recargarAccion()
    editParticipacionId.value = null
  } catch (e) {
    alert(e?.response?.errors?.[0]?.message || 'Error guardando participación')
  }
}

async function eliminarParticipacion(id) {
  try {
    await graphqlClient.request(ELIMINAR_PARTICIPACION, { id })
    await recargarAccion()
  } catch (e) {
    alert(e?.response?.errors?.[0]?.message || 'Error eliminando participación')
  }
}

async function recargarAccion() {
  const res = await graphqlClient.request(GET_ACCION_BY_ID, { id: route.params.id })
  accion.value = res.acciones?.[0] || null
}

const formParticipacion = ref({
  visible: false,
  tipo: 'socio',
  buscar: '',
  miembroId: '',
  nombreExterno: '',
  emailExterno: '',
  rol: 'asistente',
  confirmado: false,
  guardando: false,
})

const miembrosFiltrados = computed(() => {
  const q = formParticipacion.value.buscar.trim().toLowerCase()
  if (!q) return miembros.value.slice(0, 10)
  return miembros.value
    .filter(m => `${m.nombre} ${m.apellido1} ${m.email || ''}`.toLowerCase().includes(q))
    .slice(0, 10)
})

const puedeGuardarParticipacion = computed(() => {
  const f = formParticipacion.value
  if (f.tipo === 'socio') return !!f.miembroId
  return !!f.nombreExterno
})

function seleccionarMiembro(m) {
  formParticipacion.value.miembroId = m.id
  formParticipacion.value.buscar = `${m.nombre} ${m.apellido1}`
}

function cancelarParticipacion() {
  formParticipacion.value = {
    visible: false, tipo: 'socio', buscar: '', miembroId: '',
    nombreExterno: '', emailExterno: '', rol: 'asistente', confirmado: false, guardando: false,
  }
  errorParticipacion.value = ''
}

async function registrarParticipacion() {
  const f = formParticipacion.value
  f.guardando = true
  errorParticipacion.value = ''
  try {
    const data = {
      accionId: accion.value.id,
      rol: f.rol,
      confirmado: f.confirmado,
      miembroId: f.tipo === 'socio' ? f.miembroId : null,
      nombreExterno: f.tipo === 'externo' ? f.nombreExterno : null,
      emailExterno: f.tipo === 'externo' ? (f.emailExterno || null) : null,
    }
    await graphqlClient.request(REGISTRAR_PARTICIPACION, { data })
    await recargarAccion()
    cancelarParticipacion()
  } catch (e) {
    errorParticipacion.value = e?.response?.errors?.[0]?.message || 'Error al añadir participante'
  } finally {
    f.guardando = false
  }
}

onMounted(async () => {
  try {
    const [resAccion, resCat] = await Promise.all([
      graphqlClient.request(GET_ACCION_BY_ID, { id: route.params.id }),
      graphqlClient.request(GET_CATALOGOS),
    ])
    accion.value = resAccion.acciones?.[0] || null
    miembros.value = resCat.miembros || []
    estadosTarea.value = resCat.estadosTarea || []
    tiposAccion.value = resCat.tiposAccion || []
    estadosAccion.value = resCat.estadosAccion || []
  } finally {
    loading.value = false
  }
})
</script>
