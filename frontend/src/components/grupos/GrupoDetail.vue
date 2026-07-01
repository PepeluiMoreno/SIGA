<template>
  <div>
    <!-- Header -->
    <div class="bg-white rounded-xl border border-slate-200 mb-4">
      <div class="px-6 pt-5 pb-0">
        <DetailHeader fallback="/grupos" />
        <div v-if="grupo" class="flex flex-wrap items-center gap-3 pb-1">
          <h1 class="text-xl font-bold text-slate-900">{{ grupo.nombre }}</h1>
          <span :class="tipoClass(grupo.tipoGrupo?.nombre)" class="text-xs font-medium px-2.5 py-0.5 rounded-full">
            {{ grupo.tipoGrupo?.nombre || 'Sin tipo' }}
          </span>
          <span v-if="!grupo.activo" class="text-xs font-medium px-2.5 py-0.5 rounded-full bg-red-100 text-red-700">Inactivo</span>
        </div>
        <!-- Tabs -->
        <nav class="flex gap-1 mt-3 -mb-px">
          <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
            :class="['px-4 py-2.5 text-sm font-medium border-b-2 transition-colors whitespace-nowrap',
              activeTab === tab.id
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300']">
            {{ tab.name }}
            <span v-if="tab.count != null"
              class="ml-1.5 text-xs bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded-full">
              {{ tab.count }}
            </span>
          </button>
        </nav>
      </div>
    </div>

    <!-- Loading / Error -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">{{ error }}</div>

    <div v-else-if="grupo">

      <!-- ── INFO GENERAL ── -->
      <div v-show="activeTab === 'info'" class="grid grid-cols-1 lg:grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div class="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-5 space-y-4">
          <h2 class="text-xs font-semibold uppercase tracking-widest text-indigo-600">Datos del grupo</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            <div>
              <p class="text-xs text-slate-500 mb-0.5">Coordinador</p>
              <p class="font-medium text-slate-900">
                {{ grupo.coordinador ? `${grupo.coordinador.nombre} ${grupo.coordinador.apellido1}` : '—' }}
              </p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-0.5">Agrupación</p>
              <p class="font-medium text-slate-900">{{ grupo.agrupacion?.nombre || '—' }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-0.5">Fecha inicio</p>
              <p class="font-medium text-slate-900">{{ formatDate(grupo.fechaInicio) || '—' }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-0.5">Fecha fin</p>
              <p class="font-medium text-slate-900">{{ formatDate(grupo.fechaFin) || 'Permanente' }}</p>
            </div>
          </div>
          <div v-if="grupo.objetivo">
            <p class="text-xs text-slate-500 mb-1">Objetivo</p>
            <p class="text-sm text-slate-700 bg-slate-50 rounded-lg px-3 py-2">{{ grupo.objetivo }}</p>
          </div>
          <div v-if="grupo.descripcion">
            <p class="text-xs text-slate-500 mb-1">Descripción</p>
            <p class="text-sm text-slate-700">{{ grupo.descripcion }}</p>
          </div>
        </div>

        <!-- Presupuesto -->
        <div class="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
          <h2 class="text-xs font-semibold uppercase tracking-widest text-indigo-600">Presupuesto</h2>
          <div class="space-y-3 text-sm">
            <div class="flex justify-between">
              <span class="text-slate-500">Asignado</span>
              <span class="font-semibold text-slate-900">{{ formatEur(grupo.presupuestoAsignado) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Ejecutado</span>
              <span class="font-semibold" :class="pctEjecutado > 90 ? 'text-red-600' : 'text-indigo-600'">
                {{ formatEur(grupo.presupuestoEjecutado) }}
              </span>
            </div>
            <div>
              <div class="w-full bg-slate-100 rounded-full h-2 mt-1">
                <div class="h-2 rounded-full transition-all"
                  :class="pctEjecutado > 90 ? 'bg-red-500' : 'bg-indigo-500'"
                  :style="{ width: Math.min(pctEjecutado, 100) + '%' }" />
              </div>
              <p class="text-xs text-slate-400 mt-1 text-right">{{ pctEjecutado }}% ejecutado</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ── MIEMBROS ── -->
      <div v-show="activeTab === 'miembros'" class="space-y-4">
        <div class="bg-white rounded-xl border border-slate-200">
          <div class="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <h2 class="text-sm font-semibold text-slate-800">Miembros del grupo ({{ miembrosActivos.length }})</h2>
            <button @click="panelVoluntarios = !panelVoluntarios"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 transition-colors">
              <span>{{ panelVoluntarios ? '✕ Cerrar buscador' : '+ Añadir voluntario' }}</span>
            </button>
          </div>

          <!-- Panel buscador de candidatos (voluntarios / contratados / coordinadores) -->
          <div v-if="panelVoluntarios" class="border-b border-slate-100 bg-indigo-50 px-5 py-4 space-y-3">
            <p class="text-xs font-semibold text-indigo-800 uppercase tracking-wide">Añadir miembros al grupo</p>
            <div class="flex flex-wrap gap-2">
              <input v-model="busqVoluntario" type="text" placeholder="Nombre…"
                class="h-9 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white w-full sm:w-48" />
              <select v-model="filtroColectivo" class="h-9 px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white">
                <option value="">Todos los colectivos</option>
                <option value="VOLUNTARIO">Voluntarios</option>
                <option value="CONTRATADO">Contratados</option>
                <option value="COORDINADOR">Coordinadores de campaña</option>
              </select>
              <button @click="buscarVoluntarios" :disabled="cargandoVol"
                class="h-9 px-4 text-sm font-medium rounded-lg bg-white border border-indigo-300 text-indigo-700 hover:bg-indigo-50 transition-colors disabled:opacity-50">
                {{ cargandoVol ? 'Buscando…' : 'Buscar' }}
              </button>
            </div>

            <div v-if="voluntariosResultado.length" class="space-y-1 max-h-56 overflow-y-auto rounded-lg border border-slate-200 bg-white divide-y divide-slate-100">
              <div v-for="vol in voluntariosResultado" :key="`${vol.id}-${vol.colectivo}`"
                class="flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-slate-50">
                <div class="h-8 w-8 rounded-full bg-indigo-100 text-indigo-700 text-xs font-bold flex items-center justify-center flex-shrink-0">
                  {{ iniciales(vol.nombre, vol.apellido1) }}
                </div>
                <div class="flex-1 min-w-0">
                  <p class="font-medium text-slate-900">{{ vol.nombre }} {{ vol.apellido1 }}</p>
                  <span class="inline-block mt-0.5 px-1.5 py-0.5 rounded text-[10px] font-medium" :class="colectivoBadge(vol.colectivo)">
                    {{ colectivoLabel(vol.colectivo) }}
                  </span>
                </div>
                <div class="flex items-center gap-2 flex-shrink-0">
                  <select v-model="rolSeleccionado[vol.id]" class="h-8 text-xs px-2 border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500">
                    <option value="">Rol…</option>
                    <option v-for="r in rolesGrupo" :key="r.id" :value="r.id">{{ r.nombre }}</option>
                  </select>
                  <button @click="añadirMiembro(vol)"
                    :disabled="!rolSeleccionado[vol.id] || yaEsMiembro(vol.id)"
                    class="px-2 py-1 text-xs font-medium rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-40 transition-colors">
                    {{ yaEsMiembro(vol.id) ? 'Ya está' : 'Añadir' }}
                  </button>
                </div>
              </div>
            </div>
            <p v-else-if="busqRealizada" class="text-xs text-slate-400 text-center py-2">No se encontraron candidatos con esos criterios.</p>
            <ErrorAlert v-if="errorAnadir" :message="errorAnadir" />
          </div>

          <!-- Lista de miembros actuales -->
          <div v-if="miembrosActivos.length" class="divide-y divide-slate-100">
            <div v-for="mg in miembrosActivos" :key="mg.id"
              class="flex items-center gap-3 px-5 py-3">
              <div class="h-9 w-9 rounded-full bg-indigo-100 text-indigo-700 text-sm font-bold flex items-center justify-center flex-shrink-0">
                {{ iniciales(mg.miembro?.nombre, mg.miembro?.apellido1) }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-slate-900">
                  {{ mg.miembro ? `${mg.miembro.nombre} ${mg.miembro.apellido1}` : mg.miembroId }}
                </p>
                <p class="text-xs text-slate-400">
                  {{ mg.rolGrupo?.nombre }} · desde {{ formatDate(mg.fechaIncorporacion) }}
                </p>
              </div>
              <span v-if="mg.rolGrupo?.esCoordinador"
                class="text-xs font-medium px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">Coordinador</span>
              <button @click="pendingQuitarMgId = mg.id; showConfirmQuitarMiembro = true" title="Quitar del grupo"
                class="p-1 text-slate-300 hover:text-red-500 transition-colors rounded">
                <XMarkIcon class="w-4 h-4" />
              </button>
            </div>
          </div>
          <div v-else class="px-5 py-8 text-center text-sm text-slate-400">
            El grupo aún no tiene miembros. Usa el buscador de voluntarios para añadir.
          </div>
        </div>
      </div>

      <!-- ── TAREAS ── -->
      <div v-show="activeTab === 'tareas'" class="space-y-4">
        <div class="bg-white rounded-xl border border-slate-200">
          <div class="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <h2 class="text-sm font-semibold text-slate-800">Tareas ({{ grupo.tareas?.length || 0 }})</h2>
            <button @click="formTarea.visible = !formTarea.visible"
              class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 transition-colors">
              {{ formTarea.visible ? '✕ Cancelar' : '+ Nueva tarea' }}
            </button>
          </div>

          <!-- Formulario nueva tarea -->
          <div v-if="formTarea.visible" class="border-b border-slate-100 bg-slate-50 px-5 py-4 space-y-3">
            <div class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="sm:col-span-2">
                <label class="block text-xs font-medium text-slate-700 mb-1">Título</label>
                <input v-model="formTarea.titulo" type="text"
                  class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white" />
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-700 mb-1">Estado</label>
                <select v-model="formTarea.estadoId" class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white">
                  <option value="">Seleccionar…</option>
                  <option v-for="e in estadosTarea" :key="e.id" :value="e.id">{{ e.nombre }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-700 mb-1">Prioridad</label>
                <select v-model="formTarea.prioridad" class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white">
                  <option :value="1">Alta</option>
                  <option :value="2">Media</option>
                  <option :value="3">Baja</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-700 mb-1">Fecha límite</label>
                <input v-model="formTarea.fechaLimite" type="date"
                  class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white" />
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-700 mb-1">Horas estimadas</label>
                <input v-model.number="formTarea.horasEstimadas" type="number" min="0" step="0.5"
                  class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white" />
              </div>
              <div class="sm:col-span-2">
                <label class="block text-xs font-medium text-slate-700 mb-1">Descripción</label>
                <textarea v-model="formTarea.descripcion" rows="2"
                  class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white resize-none" />
              </div>
            </div>
            <ErrorAlert v-if="errorTarea" :message="errorTarea" />
            <div class="flex gap-2 pt-1">
              <button @click="crearTarea" :disabled="!formTarea.titulo || !formTarea.estadoId || formTarea.guardando"
                class="px-4 py-2 text-sm font-medium rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                {{ formTarea.guardando ? 'Guardando…' : 'Crear tarea' }}
              </button>
            </div>
          </div>

          <!-- Lista de tareas -->
          <div v-if="grupo.tareas?.length" class="divide-y divide-slate-100">
            <div v-for="tarea in tareasOrdenadas" :key="tarea.id"
              class="flex items-start gap-3 px-5 py-3.5">
              <span :class="['mt-0.5 flex-shrink-0 w-2 h-2 rounded-full mt-1.5',
                tarea.prioridad === 1 ? 'bg-red-500' : tarea.prioridad === 2 ? 'bg-amber-400' : 'bg-emerald-400']" />
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-slate-900">{{ tarea.titulo }}</p>
                <p v-if="tarea.descripcion" class="text-xs text-slate-500 mt-0.5">{{ tarea.descripcion }}</p>
                <div class="flex flex-wrap gap-3 mt-1.5 text-xs text-slate-400">
                  <span v-if="tarea.fechaLimite">📅 {{ formatDate(tarea.fechaLimite) }}</span>
                  <span v-if="tarea.horasEstimadas">⏱ {{ tarea.horasEstimadas }}h est.</span>
                  <span v-if="tarea.horasReales">✓ {{ tarea.horasReales }}h reales</span>
                </div>
              </div>
              <span :class="estadoTareaClass(tarea.estado?.nombre)"
                class="text-xs font-medium px-2 py-0.5 rounded-full flex-shrink-0">
                {{ tarea.estado?.nombre || '—' }}
              </span>
            </div>
          </div>
          <div v-else class="px-5 py-8 text-center text-sm text-slate-400">No hay tareas registradas.</div>
        </div>

        <!-- Resumen horas -->
        <div v-if="grupo.tareas?.length" class="bg-white rounded-xl border border-slate-200 px-5 py-4">
          <h3 class="text-xs font-semibold uppercase tracking-widest text-indigo-600 mb-3">Estimación de horas</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-center">
            <div>
              <p class="text-2xl font-bold text-slate-900">{{ totalHorasEstimadas }}</p>
              <p class="text-xs text-slate-400 mt-0.5">Estimadas</p>
            </div>
            <div>
              <p class="text-2xl font-bold text-indigo-600">{{ totalHorasReales }}</p>
              <p class="text-xs text-slate-400 mt-0.5">Reales</p>
            </div>
            <div>
              <p class="text-2xl font-bold" :class="desvioHoras > 0 ? 'text-red-600' : 'text-emerald-600'">
                {{ desvioHoras > 0 ? '+' : '' }}{{ desvioHoras }}
              </p>
              <p class="text-xs text-slate-400 mt-0.5">Desvío</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ── RECURSOS ── -->
      <div v-show="activeTab === 'recursos'" class="space-y-4">
        <div class="bg-white rounded-xl border border-slate-200">
          <div class="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <h2 class="text-sm font-semibold text-slate-800">Bolsas de horas necesarias ({{ requisitos.length }})</h2>
            <button @click="formRequisito.visible = !formRequisito.visible"
              class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 transition-colors">
              {{ formRequisito.visible ? '✕ Cancelar' : '+ Nueva bolsa' }}
            </button>
          </div>

          <!-- Formulario nueva bolsa de horas -->
          <div v-if="formRequisito.visible" class="border-b border-slate-100 bg-slate-50 px-5 py-4 space-y-3">
            <div class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-700 mb-1">Especialidad / Habilidad</label>
                <select v-model="formRequisito.especialidadId" class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white">
                  <option value="">Seleccionar…</option>
                  <option v-for="h in habilidades" :key="h.id" :value="h.id">{{ h.nombre }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-700 mb-1">Nivel</label>
                <select v-model="formRequisito.nivelId" class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white">
                  <option value="">Sin especificar</option>
                  <option v-for="n in nivelesHabilidad" :key="n.id" :value="n.id">{{ n.nombre }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-700 mb-1">Horas necesarias</label>
                <input v-model.number="formRequisito.horasNecesarias" type="number" min="0.5" step="0.5"
                  class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white" />
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-700 mb-1">Descripción</label>
                <input v-model="formRequisito.descripcion" type="text" placeholder="Ej: Diseño de carteles…"
                  class="h-10 w-full px-3 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white" />
              </div>
            </div>
            <ErrorAlert v-if="errorRequisito" :message="errorRequisito" />
            <button @click="crearRequisito" :disabled="!formRequisito.especialidadId || !formRequisito.horasNecesarias || formRequisito.guardando"
              class="px-4 py-2 text-sm font-medium rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors">
              {{ formRequisito.guardando ? 'Guardando…' : 'Crear bolsa de horas' }}
            </button>
          </div>

          <!-- Lista de bolsas de horas -->
          <div v-if="requisitos.length" class="divide-y divide-slate-100">
            <div v-for="req in requisitos" :key="req.id" class="px-5 py-4">
              <!-- Cabecera del requisito -->
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-3">
                  <div>
                    <span class="text-sm font-medium text-slate-900">{{ nombreHabilidad(req.especialidadId) }}</span>
                    <span v-if="req.nivelId && req.nivelId !== req.especialidadId" class="ml-2 text-xs text-slate-500">· {{ nombreNivel(req.nivelId) }}</span>
                    <span v-if="req.descripcion" class="ml-2 text-xs text-slate-400 italic">{{ req.descripcion }}</span>
                  </div>
                </div>
                <div class="flex items-center gap-3">
                  <span class="text-xs font-semibold" :class="pctCoverage(req) >= 100 ? 'text-emerald-600' : 'text-amber-600'">
                    {{ horasCubiertas(req).toFixed(1) }} / {{ req.horasNecesarias }}h
                  </span>
                  <button @click="eliminarRequisito(req.id)" title="Eliminar bolsa"
                    class="p-1 text-slate-300 hover:text-red-500 transition-colors rounded">
                    <XMarkIcon class="w-4 h-4" />
                  </button>
                </div>
              </div>

              <!-- Barra de cobertura -->
              <div class="w-full bg-slate-100 rounded-full h-1.5 mb-3">
                <div class="h-1.5 rounded-full transition-all" :class="pctCoverage(req) >= 100 ? 'bg-emerald-500' : 'bg-indigo-500'"
                  :style="{ width: pctCoverage(req) + '%' }" />
              </div>

              <!-- Aportaciones -->
              <div v-if="req.aportaciones?.length" class="space-y-1 mb-2">
                <div v-for="ap in req.aportaciones" :key="ap.id"
                  class="flex items-center gap-3 text-xs text-slate-600 bg-slate-50 rounded-lg px-3 py-1.5">
                  <button @click="toggleConfirmarAportacion(ap)" title="Confirmar/desconfirmar"
                    class="flex-shrink-0" :class="ap.confirmado ? 'text-emerald-600' : 'text-slate-300 hover:text-emerald-500'">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                    </svg>
                  </button>
                  <span class="flex-1 font-medium">{{ ap.miembro ? `${ap.miembro.nombre} ${ap.miembro.apellido1}` : '—' }}</span>
                  <span>{{ ap.horasComprometidas }}h comprometidas</span>
                  <span v-if="ap.horasReales > 0" class="text-emerald-600">{{ ap.horasReales }}h reales</span>
                  <span v-if="ap.fechaCompromiso" class="text-slate-400">{{ ap.fechaCompromiso }}</span>
                  <button @click="eliminarAportacion(req.id, ap.id)" title="Eliminar aportación"
                    class="text-slate-300 hover:text-red-500 transition-colors">✕</button>
                </div>
              </div>

              <!-- Añadir aportación inline -->
              <div v-if="formAportacion.requisitoId === req.id" class="flex flex-wrap gap-2 items-end bg-indigo-50 rounded-lg px-3 py-2.5 mb-1">
                <div>
                  <label class="block text-xs font-medium text-slate-700 mb-1">Miembro</label>
                  <select v-model="formAportacion.miembroId" class="h-9 px-2 text-xs border border-slate-300 rounded-lg bg-white focus:ring-1 focus:ring-indigo-500">
                    <option value="">Seleccionar…</option>
                    <option v-for="mg in miembrosActivos" :key="mg.miembro?.id" :value="mg.miembro?.id">
                      {{ mg.miembro?.nombre }} {{ mg.miembro?.apellido1 }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-700 mb-1">Horas</label>
                  <input v-model.number="formAportacion.horasComprometidas" type="number" min="0.5" step="0.5"
                    class="h-9 w-20 px-2 text-xs border border-slate-300 rounded-lg bg-white focus:ring-1 focus:ring-indigo-500" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-700 mb-1">Fecha</label>
                  <input v-model="formAportacion.fechaCompromiso" type="date"
                    class="h-9 px-2 text-xs border border-slate-300 rounded-lg bg-white focus:ring-1 focus:ring-indigo-500" />
                </div>
                <button @click="crearAportacion(req.id)" :disabled="!formAportacion.miembroId || formAportacion.guardando"
                  class="h-9 px-3 text-xs font-medium rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 self-end">
                  {{ formAportacion.guardando ? '…' : 'Registrar' }}
                </button>
                <button @click="formAportacion.requisitoId = null" class="h-9 px-2 text-xs text-slate-500 hover:text-slate-700 self-end">✕</button>
                <ErrorAlert v-if="errorAportacion" :message="errorAportacion" />
              </div>
              <button v-else @click="formAportacion.requisitoId = req.id; formAportacion.miembroId = ''"
                class="text-xs text-indigo-600 hover:text-indigo-800 font-medium">
                + Añadir aportación
              </button>
            </div>
          </div>
          <div v-else class="px-5 py-8 text-center text-sm text-slate-400">
            No hay bolsas de horas definidas. Crea una para gestionar los recursos necesarios del grupo.
          </div>
        </div>
      </div>

      <!-- ── REUNIONES ── -->
      <div v-show="activeTab === 'reuniones'" class="space-y-3">
        <div class="bg-white rounded-xl border border-slate-200">
          <div class="px-5 py-4 border-b border-slate-100">
            <h2 class="text-sm font-semibold text-slate-800">Reuniones ({{ grupo.reuniones?.length || 0 }})</h2>
          </div>
          <div v-if="reunionesOrdenadas.length" class="divide-y divide-slate-100">
            <div v-for="r in reunionesOrdenadas" :key="r.id" class="px-5 py-4 flex gap-4">
              <div class="flex-shrink-0 text-center w-12">
                <p class="text-lg font-bold text-slate-900 leading-none">{{ new Date(r.fecha).getDate() }}</p>
                <p class="text-xs text-slate-400 uppercase">{{ new Date(r.fecha).toLocaleDateString('es-ES', {month:'short'}) }}</p>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-slate-900">{{ r.titulo }}</p>
                <p v-if="r.horaInicio" class="text-xs text-slate-500 mt-0.5">
                  {{ r.horaInicio }}{{ r.horaFin ? ` – ${r.horaFin}` : '' }}
                  <span v-if="r.lugar"> · {{ r.lugar }}</span>
                  <a v-if="r.urlOnline" :href="r.urlOnline" target="_blank"
                    class="ml-2 text-indigo-600 hover:underline">🔗 enlace</a>
                </p>
                <p v-if="r.descripcion" class="text-xs text-slate-500 mt-1">{{ r.descripcion }}</p>
              </div>
              <span :class="r.realizada ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'"
                class="text-xs font-medium px-2 py-0.5 rounded-full flex-shrink-0 self-start">
                {{ r.realizada ? 'Realizada' : 'Planificada' }}
              </span>
            </div>
          </div>
          <div v-else class="px-5 py-8 text-center text-sm text-slate-400">No hay reuniones registradas.</div>
        </div>
      </div>

    </div>
  </div>

  <ConfirmModal
    v-model="showConfirmQuitarMiembro"
    title-soft="¿Quitar este miembro del grupo?"
    title="¿Quitar este miembro del grupo?"
    confirm-label="Quitar"
    @confirm="ejecutarQuitarMiembro"
  />
</template>

<script setup>
import { XMarkIcon } from '@heroicons/vue/24/outline'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import DetailHeader from '@/components/common/DetailHeader.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import { graphqlClient } from '@/graphql/client.js'

const route = useRoute()
const grupoId = computed(() => route.params.id)

const loading = ref(true)
const error = ref('')
const grupo = ref(null)
const habilidades = ref([])
const nivelesHabilidad = ref([])
const rolesGrupo = ref([])
const estadosTarea = ref([])
const requisitos = ref([])

// ── Tabs ─────────────────────────────────────────────────────────────────────
const activeTab = ref('info')
const tabs = computed(() => [
  { id: 'info',      name: 'Información',  count: null },
  { id: 'miembros',  name: 'Miembros',     count: miembrosActivos.value.length },
  { id: 'tareas',    name: 'Tareas',       count: grupo.value?.tareas?.length ?? 0 },
  { id: 'recursos',  name: 'Recursos',     count: requisitos.value.length },
  { id: 'reuniones', name: 'Reuniones',    count: grupo.value?.reuniones?.length ?? 0 },
])

const miembrosActivos = computed(() => (grupo.value?.miembros || []).filter(m => m.activo))

// ── GraphQL ───────────────────────────────────────────────────────────────────
const GQL_GRUPO = `
  query GrupoDetalle($id: UUID!) {
    gruposTrabajo(filter: { id: { eq: $id } }) {
      id nombre descripcion objetivo activo
      fechaInicio fechaFin presupuestoAsignado presupuestoEjecutado
      tipoGrupo { id nombre esPermanente }
      coordinador { id nombre apellido1 email }
      agrupacion { id nombre }
      miembros {
        id miembroId activo fechaIncorporacion responsabilidades
        miembro { id nombre apellido1 email }
        rolGrupo { id nombre esCoordinador }
      }
      tareas {
        id titulo descripcion prioridad fechaLimite horasEstimadas horasReales
        estado { id nombre }
      }
      reuniones {
        id titulo descripcion fecha horaInicio horaFin lugar urlOnline realizada
      }
    }
  }
`

const GQL_CATALOGOS = `
  query CatalogosGrupo {
    habilidades { id nombre categoriaId }
    nivelesHabilidad { id nombre }
    rolesGrupo { id nombre esCoordinador activo }
    estadosTarea { id nombre }
  }
`

const GQL_REQUISITOS = `
  query RequisitosGrupo($grupoId: UUID!) {
    requisitosRecurso(filter: { grupoId: { eq: $grupoId } }) {
      id grupoId especialidadId nivelId horasNecesarias descripcion
      aportaciones {
        id miembroId horasComprometidas horasReales confirmado fechaCompromiso observaciones
        miembro { id nombre apellido1 }
      }
    }
  }
`

const MUTATION_CREAR_REQUISITO = `
  mutation CrearRequisitoRecurso($data: RequisitoRecursoCreateInput!) {
    crearRequisitoRecurso(data: $data) {
      id grupoId especialidadId nivelId horasNecesarias descripcion
      aportaciones { id miembroId horasComprometidas horasReales confirmado miembro { id nombre apellido1 } }
    }
  }
`

const MUTATION_ELIMINAR_REQUISITO = `
  mutation EliminarRequisitoRecurso($id: UUID!) {
    eliminarRequisitosRecurso(filter: { id: { eq: $id } }) { id }
  }
`

const MUTATION_CREAR_APORTACION = `
  mutation CrearAportacionHoras($data: AportacionHorasCreateInput!) {
    crearAportacionHoras(data: $data) {
      id requisito { id } miembro { id nombre apellido1 }
      horasComprometidas horasReales confirmado fechaCompromiso observaciones
    }
  }
`

const MUTATION_ACTUALIZAR_APORTACION = `
  mutation ActualizarAportacionHoras($data: AportacionHorasUpdateInput!) {
    actualizarAportacionHoras(data: $data) {
      id horasComprometidas horasReales confirmado
    }
  }
`

const MUTATION_ELIMINAR_APORTACION = `
  mutation EliminarAportacionHoras($id: UUID!) {
    eliminarAportacionesHoras(filter: { id: { eq: $id } }) { id }
  }
`

const GQL_VOLUNTARIOS = `
  query CandidatosParaGrupo($colectivo: String) {
    candidatos: candidatosGrupo(colectivo: $colectivo) {
      id nombre apellido1 apellido2 email colectivo
    }
  }
`

const MUTATION_CREAR_MIEMBRO_GRUPO = `
  mutation CrearMiembroGrupo($grupoId: UUID!, $miembroId: UUID!, $rolGrupoId: UUID!) {
    crearMiembroGrupo(data: { grupoId: $grupoId, miembroId: $miembroId, rolGrupoId: $rolGrupoId }) {
      id miembroId activo fechaIncorporacion
      miembro { id nombre apellido1 }
      rolGrupo { id nombre esCoordinador }
    }
  }
`

const MUTATION_ELIMINAR_MIEMBRO_GRUPO = `
  mutation EliminarMiembroGrupo($id: UUID!) {
    eliminarMiembrosGrupo(filter: { id: { eq: $id } }) { id }
  }
`

const MUTATION_CREAR_TAREA = `
  mutation CrearTarea($data: TareaCreateData!) {
    crearTarea(data: $data) {
      id titulo descripcion prioridad fechaLimite horasEstimadas horasReales
      estado { id nombre }
    }
  }
`

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const [dataGrupo, dataCat] = await Promise.all([
      graphqlClient.request(GQL_GRUPO, { id: grupoId.value }),
      graphqlClient.request(GQL_CATALOGOS),
    ])
    grupo.value = dataGrupo.gruposTrabajo?.[0] || null
    habilidades.value = dataCat.habilidades || []
    nivelesHabilidad.value = dataCat.nivelesHabilidad || []
    rolesGrupo.value = (dataCat.rolesGrupo || []).filter(r => r.activo)
    estadosTarea.value = dataCat.estadosTarea || []
    if (!grupo.value) error.value = 'Grupo no encontrado'
    if (grupo.value) {
      const dataReq = await graphqlClient.request(GQL_REQUISITOS, { grupoId: grupoId.value })
      requisitos.value = dataReq.requisitosRecurso || []
    }
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando el grupo'
  } finally {
    loading.value = false
  }
}

// ── Buscador voluntarios ──────────────────────────────────────────────────────
const panelVoluntarios = ref(false)
const busqVoluntario = ref('')
const filtroColectivo = ref('')
const voluntariosResultado = ref([])
const cargandoVol = ref(false)
const busqRealizada = ref(false)
const rolSeleccionado = ref({})
const errorAnadir = ref('')

async function buscarVoluntarios() {
  cargandoVol.value = true
  busqRealizada.value = false
  try {
    const data = await graphqlClient.request(GQL_VOLUNTARIOS, {
      colectivo: filtroColectivo.value || null,
    })
    let cands = data.candidatos || []
    const q = busqVoluntario.value.toLowerCase()
    if (q) cands = cands.filter(v =>
      `${v.nombre} ${v.apellido1 || ''}`.toLowerCase().includes(q)
    )
    voluntariosResultado.value = cands
    busqRealizada.value = true
  } catch (e) {
    errorAnadir.value = e?.response?.errors?.[0]?.message || 'Error buscando candidatos'
  } finally {
    cargandoVol.value = false
  }
}

const COLECTIVO_LABELS = { VOLUNTARIO: 'Voluntario', CONTRATADO: 'Contratado', COORDINADOR: 'Coordinador' }
const COLECTIVO_BADGES = {
  VOLUNTARIO: 'bg-purple-100 text-purple-700',
  CONTRATADO: 'bg-orange-100 text-orange-700',
  COORDINADOR: 'bg-sky-100 text-sky-700',
}
function colectivoLabel(c) { return COLECTIVO_LABELS[c] || c }
function colectivoBadge(c) { return COLECTIVO_BADGES[c] || 'bg-slate-100 text-slate-600' }

function yaEsMiembro(miembroId) {
  return miembrosActivos.value.some(m => m.miembroId === miembroId || m.miembro?.id === miembroId)
}

async function añadirMiembro(vol) {
  const rolId = rolSeleccionado.value[vol.id]
  if (!rolId) return
  errorAnadir.value = ''
  try {
    const data = await graphqlClient.request(MUTATION_CREAR_MIEMBRO_GRUPO, {
      grupoId: grupoId.value,
      miembroId: vol.id,
      rolGrupoId: rolId,
    })
    grupo.value.miembros = [...(grupo.value.miembros || []), data.crearMiembroGrupo]
  } catch (e) {
    errorAnadir.value = e?.response?.errors?.[0]?.message || 'Error añadiendo miembro'
  }
}

const showConfirmQuitarMiembro = ref(false)
const pendingQuitarMgId = ref(null)

async function ejecutarQuitarMiembro() {
  const mgId = pendingQuitarMgId.value
  if (!mgId) return
  pendingQuitarMgId.value = null
  try {
    await graphqlClient.request(MUTATION_ELIMINAR_MIEMBRO_GRUPO, { id: mgId })
    grupo.value.miembros = grupo.value.miembros.filter(m => m.id !== mgId)
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error al quitar miembro'
  }
}

// ── Tareas ────────────────────────────────────────────────────────────────────
const formTarea = ref({ visible: false, titulo: '', estadoId: '', prioridad: 2, descripcion: '', fechaLimite: '', horasEstimadas: null, guardando: false })
const errorTarea = ref('')

const tareasOrdenadas = computed(() =>
  [...(grupo.value?.tareas || [])].sort((a, b) => a.prioridad - b.prioridad)
)

const totalHorasEstimadas = computed(() =>
  (grupo.value?.tareas || []).reduce((s, t) => s + Number(t.horasEstimadas || 0), 0).toFixed(1)
)
const totalHorasReales = computed(() =>
  (grupo.value?.tareas || []).reduce((s, t) => s + Number(t.horasReales || 0), 0).toFixed(1)
)
const desvioHoras = computed(() =>
  (Number(totalHorasReales.value) - Number(totalHorasEstimadas.value)).toFixed(1)
)

async function crearTarea() {
  if (!formTarea.value.titulo || !formTarea.value.estadoId) return
  formTarea.value.guardando = true
  errorTarea.value = ''
  try {
    const data = await graphqlClient.request(MUTATION_CREAR_TAREA, {
      data: {
        grupoId: grupoId.value,
        titulo: formTarea.value.titulo,
        estadoId: formTarea.value.estadoId,
        prioridad: formTarea.value.prioridad,
        descripcion: formTarea.value.descripcion || null,
        fechaLimite: formTarea.value.fechaLimite || null,
        horasEstimadas: formTarea.value.horasEstimadas || null,
      }
    })
    grupo.value.tareas = [...(grupo.value.tareas || []), data.crearTarea]
    formTarea.value = { visible: false, titulo: '', estadoId: '', prioridad: 2, descripcion: '', fechaLimite: '', horasEstimadas: null, guardando: false }
  } catch (e) {
    errorTarea.value = e?.response?.errors?.[0]?.message || 'Error creando tarea'
  } finally {
    formTarea.value.guardando = false
  }
}

// ── Recursos (RequisitoRecurso / AportacionHoras) ────────────────────────────
const formRequisito = ref({ visible: false, especialidadId: '', nivelId: '', horasNecesarias: 8, descripcion: '', guardando: false })
const errorRequisito = ref('')
const formAportacion = ref({ requisitoId: null, miembroId: '', horasComprometidas: 4, fechaCompromiso: '', observaciones: '', guardando: false })
const errorAportacion = ref('')

function nombreHabilidad(id) {
  return habilidades.value.find(h => h.id === id)?.nombre || id?.slice(0, 8) || '—'
}
function nombreNivel(id) {
  return nivelesHabilidad.value.find(n => n.id === id)?.nombre || id?.slice(0, 8) || '—'
}
function horasCubiertas(req) {
  return (req.aportaciones || []).filter(a => a.confirmado).reduce((s, a) => s + Number(a.horasComprometidas || 0), 0)
}
function pctCoverage(req) {
  const total = Number(req.horasNecesarias || 0)
  return total > 0 ? Math.min(Math.round((horasCubiertas(req) / total) * 100), 100) : 0
}

async function crearRequisito() {
  if (!formRequisito.value.especialidadId || !formRequisito.value.horasNecesarias) return
  formRequisito.value.guardando = true
  errorRequisito.value = ''
  try {
    const data = await graphqlClient.request(MUTATION_CREAR_REQUISITO, {
      data: {
        grupoId: grupoId.value,
        especialidadId: formRequisito.value.especialidadId,
        nivelId: formRequisito.value.nivelId || formRequisito.value.especialidadId,
        horasNecesarias: formRequisito.value.horasNecesarias,
        descripcion: formRequisito.value.descripcion || null,
      }
    })
    requisitos.value = [...requisitos.value, data.crearRequisitoRecurso]
    formRequisito.value = { visible: false, especialidadId: '', nivelId: '', horasNecesarias: 8, descripcion: '', guardando: false }
  } catch (e) {
    errorRequisito.value = e?.response?.errors?.[0]?.message || 'Error creando requisito'
  } finally {
    formRequisito.value.guardando = false
  }
}

async function eliminarRequisito(reqId) {
  try {
    await graphqlClient.request(MUTATION_ELIMINAR_REQUISITO, { id: reqId })
    requisitos.value = requisitos.value.filter(r => r.id !== reqId)
  } catch (e) {
    errorRequisito.value = e?.response?.errors?.[0]?.message || 'Error eliminando requisito'
  }
}

async function crearAportacion(reqId) {
  if (!formAportacion.value.miembroId || !formAportacion.value.horasComprometidas) return
  formAportacion.value.guardando = true
  errorAportacion.value = ''
  try {
    const data = await graphqlClient.request(MUTATION_CREAR_APORTACION, {
      data: {
        requisitoId: reqId,
        miembroId: formAportacion.value.miembroId,
        horasComprometidas: formAportacion.value.horasComprometidas,
        horasReales: 0,
        confirmado: false,
        fechaCompromiso: formAportacion.value.fechaCompromiso || null,
        observaciones: formAportacion.value.observaciones || null,
      }
    })
    const req = requisitos.value.find(r => r.id === reqId)
    if (req) req.aportaciones = [...(req.aportaciones || []), data.crearAportacionHoras]
    formAportacion.value = { requisitoId: null, miembroId: '', horasComprometidas: 4, fechaCompromiso: '', observaciones: '', guardando: false }
  } catch (e) {
    errorAportacion.value = e?.response?.errors?.[0]?.message || 'Error registrando aportación'
  } finally {
    formAportacion.value.guardando = false
  }
}

async function toggleConfirmarAportacion(ap) {
  try {
    await graphqlClient.request(MUTATION_ACTUALIZAR_APORTACION, {
      data: { id: ap.id, confirmado: !ap.confirmado }
    })
    ap.confirmado = !ap.confirmado
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error actualizando aportación'
  }
}

async function eliminarAportacion(reqId, apId) {
  try {
    await graphqlClient.request(MUTATION_ELIMINAR_APORTACION, { id: apId })
    const req = requisitos.value.find(r => r.id === reqId)
    if (req) req.aportaciones = req.aportaciones.filter(a => a.id !== apId)
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error eliminando aportación'
  }
}

// ── Reuniones ─────────────────────────────────────────────────────────────────
const reunionesOrdenadas = computed(() =>
  [...(grupo.value?.reuniones || [])].sort((a, b) => new Date(b.fecha) - new Date(a.fecha))
)

// ── Helpers ───────────────────────────────────────────────────────────────────
const pctEjecutado = computed(() => {
  const asig = Number(grupo.value?.presupuestoAsignado || 0)
  const ejec = Number(grupo.value?.presupuestoEjecutado || 0)
  return asig ? Math.round((ejec / asig) * 100) : 0
})

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })
}

function formatEur(v) {
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(Number(v) || 0)
}

function iniciales(nombre, apellido) {
  return `${(nombre || '')[0] || ''}${(apellido || '')[0] || ''}`.toUpperCase()
}

function tipoClass(nombre) {
  if (!nombre) return 'bg-slate-100 text-slate-600'
  const n = nombre.toUpperCase()
  if (n.includes('PERMANENTE')) return 'bg-purple-100 text-purple-700'
  if (n.includes('TEMPORAL')) return 'bg-amber-100 text-amber-700'
  return 'bg-slate-100 text-slate-600'
}

function estadoTareaClass(nombre) {
  if (!nombre) return 'bg-slate-100 text-slate-600'
  const n = nombre.toUpperCase()
  if (n.includes('COMPLET') || n.includes('HECHA')) return 'bg-emerald-100 text-emerald-700'
  if (n.includes('PROGRES') || n.includes('CURSO')) return 'bg-blue-100 text-blue-700'
  if (n.includes('BLOQUEA') || n.includes('ESPERA')) return 'bg-red-100 text-red-700'
  return 'bg-slate-100 text-slate-600'
}

onMounted(cargar)
</script>
