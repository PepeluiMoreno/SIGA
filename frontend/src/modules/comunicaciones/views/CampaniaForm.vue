<template>
  <AppLayout
    :title="campania.nombre || (isEdit ? 'Editar campaña' : 'Nueva campaña')"
    :subtitle="isEdit ? 'Editando campaña' : 'Rellena los datos para registrar la nueva campaña'">
    <template #actions>
      <FormActions :submit-text="isEdit ? 'Actualizar campaña' : 'Crear campaña'"
        :loading="submitting" :error="error"
        @cancel="$router.push('/campanias')" @submit="handleSubmit" />
    </template>

    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>

    <form v-else novalidate @submit.prevent="handleSubmit" class="space-y-3">

      <!-- ══ PANEL ORIGEN (solo nueva campaña) ════════════════════════════════ -->
      <section v-if="!isEdit" class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div class="flex items-center gap-3 px-5 py-3.5 border-b border-slate-200">
          <span class="shrink-0 w-1.5 h-5 rounded-full bg-slate-400"></span>
          <h2 class="text-sm font-semibold text-slate-800">Punto de partida</h2>
        </div>
        <div class="px-5 py-4 space-y-4">

          <!-- Fila 1: 3 botones de origen -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <button type="button" @click="origenTipo = 'blanco'"
              class="flex flex-col items-center gap-2 p-4 border-2 rounded-xl transition-colors text-center"
              :class="origenTipo === 'blanco' ? 'border-indigo-500 bg-indigo-50' : 'border-slate-200 bg-white hover:border-slate-300'">
              <DocumentPlusIcon class="w-6 h-6" :class="origenTipo === 'blanco' ? 'text-indigo-600' : 'text-slate-400'" />
              <div>
                <p class="text-sm font-semibold text-slate-800">En blanco</p>
                <p class="text-xs text-slate-400">Empieza desde cero</p>
              </div>
            </button>
            <button type="button" @click="origenTipo = 'plantilla'"
              class="flex flex-col items-center gap-2 p-4 border-2 rounded-xl transition-colors text-center"
              :class="origenTipo === 'plantilla' ? 'border-indigo-500 bg-indigo-50' : 'border-slate-200 bg-white hover:border-slate-300'">
              <DocumentTextIcon class="w-6 h-6" :class="origenTipo === 'plantilla' ? 'text-indigo-600' : 'text-slate-400'" />
              <div>
                <p class="text-sm font-semibold text-slate-800">Plantilla</p>
                <p class="text-xs text-slate-400">Tipo preconfigurado</p>
              </div>
            </button>
            <button type="button"
              :disabled="!campaniasCandidatas.length"
              @click="campaniasCandidatas.length && (origenTipo = 'clonar')"
              class="flex flex-col items-center gap-2 p-4 border-2 rounded-xl transition-colors text-center"
              :class="[
                origenTipo === 'clonar' ? 'border-indigo-500 bg-indigo-50' : 'border-slate-200 bg-white hover:border-slate-300',
                !campaniasCandidatas.length ? 'opacity-40 cursor-not-allowed' : '',
              ]">
              <DocumentDuplicateIcon class="w-6 h-6" :class="origenTipo === 'clonar' ? 'text-indigo-600' : 'text-slate-400'" />
              <div>
                <p class="text-sm font-semibold text-slate-800">Clonar campaña</p>
                <p class="text-xs text-slate-400">{{ campaniasCandidatas.length ? 'Basarse en otra existente' : 'Sin campañas todavía' }}</p>
              </div>
            </button>
          </div>

          <!-- Fila 2: Tipo + desplegable contextual en la misma línea -->
          <div class="border-t border-slate-100 pt-4 flex flex-wrap items-end gap-3">
            <!-- Tipo de campaña -->
            <div class="w-56">
              <label :class="lbl">Tipo de campaña <span class="text-red-400">*</span></label>
              <select v-model="campania.tipo_campania_id" :class="fieldInp('tipo_campania_id')" @change="onTipoCampaniaChange">
                <option value="">— Seleccionar —</option>
                <option v-for="t in tiposCampania" :key="t.id" :value="t.id">{{ t.nombre }}</option>
              </select>
              <ErrorAlert v-if="errors.tipo_campania_id" :message="errors.tipo_campania_id" />
            </div>

            <!-- Plantilla (si origen = plantilla) -->
            <div v-if="origenTipo === 'plantilla'" class="w-72">
              <label :class="lbl">Plantilla</label>
              <select v-model="plantillaSeleccionadaId" :class="inp"
                :disabled="plantillaCargando || !campania.tipo_campania_id">
                <option value="">{{ !campania.tipo_campania_id ? 'Elige primero el tipo' : plantillaCargando ? 'Cargando…' : plantillasDisponibles.length ? '— Seleccionar —' : 'Sin plantillas para este tipo' }}</option>
                <option v-for="p in plantillasDisponibles" :key="p.id" :value="p.id">{{ p.nombre }}</option>
              </select>
            </div>

            <!-- Campaña de origen (si origen = clonar) -->
            <div v-if="origenTipo === 'clonar'" class="w-80">
              <label :class="lbl">Campaña de origen</label>
              <select v-model="clonarDeCampaniaId" :class="inp" :disabled="!campania.tipo_campania_id">
                <option value="">{{ !campania.tipo_campania_id ? 'Elige primero el tipo' : clonarCandidatasDelTipo.length ? '— Seleccionar campaña —' : 'Sin campañas de este tipo' }}</option>
                <option v-for="c in clonarCandidatasDelTipo" :key="c.id" :value="c.id">{{ c.nombre }}</option>
              </select>
            </div>
          </div>

          <!-- Chips resumen plantilla seleccionada -->
          <div v-if="origenTipo === 'plantilla' && plantillaSeleccionadaInfo" class="flex flex-wrap gap-2">
            <span class="inline-flex px-2.5 py-1 text-xs font-medium rounded-lg bg-violet-50 text-violet-700 border border-violet-200">
              {{ plantillaSeleccionadaInfo.metas?.length || 0 }} metas
            </span>
            <span class="inline-flex px-2.5 py-1 text-xs font-medium rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200">
              {{ plantillaSeleccionadaInfo.partidas?.length || 0 }} partidas
            </span>
            <span class="inline-flex px-2.5 py-1 text-xs font-medium rounded-lg bg-sky-50 text-sky-700 border border-sky-200">
              {{ plantillaSeleccionadaInfo.actividades?.length || 0 }} actividades /
              {{ (plantillaSeleccionadaInfo.actividades || []).reduce((n, a) => n + (a.tareas?.length || 0), 0) }} tareas
            </span>
          </div>

          <!-- Confirmación clonar -->
          <p v-if="origenTipo === 'clonar' && clonarDeCampaniaId" class="text-xs text-indigo-600 font-medium">
            ✓ Se han copiado metas, canales y partidas. Puedes editarlos antes de guardar.
          </p>

        </div>
      </section>

      <AccordionGroup class="space-y-3">

        <!-- ── 1 · DATOS GENERALES ──────────────────────────────────────────── -->
        <AccordionPanel :default-open="true">
          <template #title>
            <span class="shrink-0 w-1.5 h-5 rounded-full bg-violet-500"></span>
            <h2 :class="titleCls">Datos generales</h2>
          </template>
          <div class="px-5 py-4 grid grid-cols-12 gap-x-3 gap-y-4">

            <!-- Nombre | Estado -->
            <div class="col-span-10">
              <label :class="lbl">Nombre <span class="text-red-400">*</span></label>
              <input v-model="campania.nombre" type="text" :class="fieldInp('nombre')"
                placeholder="Nombre de la campaña" maxlength="200" autofocus
                @blur="validateField('nombre', campania.nombre, campania)" />
              <ErrorAlert v-if="errors.nombre" :message="errors.nombre" />
            </div>
            <div class="col-span-2">
              <label :class="lbl">Estado<span v-if="isEdit" class="text-red-400"> *</span></label>
              <!-- Creación: estado inicial automático -->
              <div v-if="!isEdit" class="h-10 flex items-center gap-2">
                <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-500">
                  {{ estadoInicialNombre }}
                </span>
                <span class="text-xs text-slate-400 italic">Automático</span>
              </div>
              <!-- Edición: select normal -->
              <select v-else v-model="campania.estado_campania_id" :class="fieldInp('estado_campania_id')"
                @change="validateField('estado_campania_id', campania.estado_campania_id, campania)">
                <option value="">—</option>
                <option v-for="e in estadosCampania" :key="e.id" :value="e.id">{{ e.nombre }}</option>
              </select>
              <ErrorAlert v-if="errors.estado_campania_id" :message="errors.estado_campania_id" />
            </div>

            <!-- Tipo (solo en modo edición; en creación está en "Punto de partida") -->
            <div v-if="isEdit" class="col-span-4">
              <label :class="lbl">Tipo de campaña <span class="text-red-400">*</span></label>
              <select v-model="campania.tipo_campania_id" :class="fieldInp('tipo_campania_id')"
                @change="onTipoCampaniaChange">
                <option value="">— Seleccionar —</option>
                <option v-for="t in tiposCampania" :key="t.id" :value="t.id">{{ t.nombre }}</option>
              </select>
              <ErrorAlert v-if="errors.tipo_campania_id" :message="errors.tipo_campania_id" />
            </div>
            <div class="col-span-4">
              <label :class="lbl">Ámbito</label>
              <select v-model="campania.agrupacion_id" :class="inp">
                <option value="">— General (todas las agrupaciones) —</option>
                <template v-for="grupo in agrupacionesPorNivel" :key="grupo.nombre">
                  <optgroup :label="grupo.nombre">
                    <option v-for="a in grupo.items" :key="a.id" :value="a.id">{{ a.nombre }}</option>
                  </optgroup>
                </template>
              </select>
            </div>
            <div class="col-span-4">
              <label :class="lbl">
                Responsable
                <span v-if="campania.agrupacion_id && sinCoordinadores"
                  class="ml-1 text-xs font-normal text-amber-600 inline-flex items-center gap-1">
                  <ExclamationTriangleIcon class="w-3 h-3 shrink-0" />
                  Sin coordinadores en este ámbito
                </span>
              </label>
              <select v-model="campania.responsable_id" :class="inp">
                <option value="">— Sin asignar —</option>
                <option v-for="m in responsablesCandidatos" :key="m.id" :value="m.id">
                  {{ m.nombre }} {{ m.apellido1 }}
                </option>
              </select>
            </div>

            <!-- Lema | URL -->
            <div class="col-span-6">
              <label :class="lbl">Lema</label>
              <input v-model="campania.lema" type="text" :class="inp"
                placeholder="Frase breve de la campaña" maxlength="200" />
            </div>
            <div class="col-span-6">
              <label :class="lbl">URL externa</label>
              <div :class="inputGroupCls">
                <span :class="prefixCls"><LinkIcon class="w-3.5 h-3.5" /></span>
                <input v-model="campania.url_externa" type="url" :class="inputGroupInp"
                  placeholder="https://laicismo.org/…" />
              </div>
            </div>

            <!-- Descripciones -->
            <div class="col-span-12">
              <label :class="lbl">Descripción corta</label>
              <input v-model="campania.descripcion_corta" type="text" :class="inp"
                placeholder="Resumen para listados (máx. 300 car.)" maxlength="300" />
            </div>
            <div class="col-span-7">
              <label :class="lbl">Descripción completa</label>
              <textarea v-model="campania.descripcion_larga" rows="4" :class="inp"
                placeholder="Contexto, motivación y alcance de la campaña…"
                @input="autoResize" />
            </div>
            <div class="col-span-5">
              <label :class="lbl">Objetivo principal</label>
              <textarea v-model="campania.objetivo_principal" rows="4" :class="inp"
                placeholder="¿Qué resultado concreto se persigue?"
                @input="autoResize" />
            </div>

          </div>
        </AccordionPanel>

        <!-- ── 2 · PRESUPUESTO ────────────────────────────────────────────────── -->
        <AccordionPanel :default-open="false">
          <template #title>
            <span class="shrink-0 w-1.5 h-5 rounded-full bg-emerald-500"></span>
            <h2 :class="titleCls">
              Presupuesto
              <span v-if="partidas.length" class="ml-2 text-xs font-normal text-emerald-600 normal-case">
                {{ fmtEur(totalPresupuesto) }} est.
              </span>
            </h2>
          </template>
          <div class="px-5 py-4">
            <div class="flex items-center justify-end mb-3">
              <button type="button" @click="addPartida"
                class="inline-flex items-center gap-1.5 text-xs text-emerald-600 hover:text-emerald-800 font-medium transition-colors">
                <PlusIcon class="w-3.5 h-3.5" /> Añadir partida
              </button>
            </div>
            <div class="overflow-x-auto -mx-1"><table class="w-full">
              <thead>
                <tr class="border-b border-slate-100">
                  <th class="pb-2 text-left text-xs font-semibold text-slate-400">Concepto</th>
                  <th class="pb-2 w-24 text-left text-xs font-semibold text-slate-400">Tipo</th>
                  <th class="pb-2 w-full sm:w-32 text-right text-xs font-semibold text-slate-400 pr-1">Importe estimado</th>
                  <th class="w-7"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!partidas.length">
                  <td colspan="4" class="py-4 text-center text-xs text-slate-400 italic">
                    Sin partidas — pulsa «Añadir» o selecciona una plantilla
                  </td>
                </tr>
                <tr v-for="(p, i) in partidas" :key="p._id" class="border-b border-slate-50">
                  <td class="py-1.5 pr-2">
                    <input v-model="p.concepto" type="text" :class="inpSm" placeholder="Concepto" />
                  </td>
                  <td class="py-1.5 pr-2">
                    <select v-model="p.tipo_partida" :class="inpSm">
                      <option value="gasto">Gasto</option>
                      <option value="ingreso">Ingreso</option>
                    </select>
                  </td>
                  <td class="py-1.5 pr-1">
                    <div :class="inputGroupSmCls">
                      <span :class="prefixSmCls">€</span>
                      <input v-model.number="p.importe_estimado" type="number" min="0" step="0.01"
                        :class="inputGroupInpSm + ' w-24 text-right tabular-nums'" placeholder="0,00" />
                    </div>
                  </td>
                  <td class="py-1.5 pl-1">
                    <button type="button" @click="partidas.splice(i, 1)"
                      class="p-1 text-slate-300 hover:text-red-400 transition-colors">
                      <XMarkIcon class="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
                <tr v-if="partidas.length" class="border-t-2 border-slate-200">
                  <td colspan="2" class="pt-2 text-xs font-semibold text-slate-500 uppercase tracking-wide">Total gastos est.</td>
                  <td class="pt-2 pr-1 text-right font-bold tabular-nums text-sm text-emerald-700">{{ fmtEur(totalPresupuesto) }}</td>
                  <td></td>
                </tr>
              </tbody>
            </table></div>
          </div>
        </AccordionPanel>

        <!-- ── 3 · CALENDARIO Y ACTIVIDADES ───────────────────────────────────── -->
        <AccordionPanel :default-open="true">
          <template #title>
            <span class="shrink-0 w-1.5 h-5 rounded-full bg-indigo-500"></span>
            <h2 :class="titleCls">Calendario y actividades</h2>
          </template>
          <div class="px-5 py-4 space-y-4">

            <!-- Fechas de campaña -->
            <div class="flex flex-wrap gap-4 items-end">
              <div class="w-52">
                <label :class="lbl">Periodicidad</label>
                <select v-model="campania.periodicidad" :class="inp">
                  <option v-for="p in PERIODICIDADES" :key="p.value" :value="p.value">{{ p.label }}</option>
                </select>
              </div>
              <div class="w-full sm:w-36">
                <label :class="lbl">{{ periInfo.labelInicio }}</label>
                <input v-model="campania.fecha_inicio" type="date" :class="inp" />
              </div>
              <div v-if="!periInfo.sinFin" class="w-full sm:w-36">
                <label :class="lbl">{{ periInfo.labelFin }}</label>
                <input v-model="campania.fecha_fin" type="date" :class="inp" />
              </div>
            </div>
            <p v-if="periInfo.hint" class="text-xs text-sky-600 font-medium">{{ periInfo.hint }}</p>
            <p v-else class="text-xs text-slate-400">{{ PERIODICIDADES.find(p => p.value === campania.periodicidad)?.desc }}</p>

            <!-- Actividades: calendario editable (plantilla en creación) -->
            <div v-if="!isEdit && origenTipo === 'plantilla' && actividadesPreview.length"
              class="border-t border-slate-100 pt-4">
              <div class="flex items-center justify-between mb-3">
                <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Calendario de actividades ({{ actividadesPreview.length }})
                </p>
                <span class="text-xs text-slate-400 italic">Fija las fechas antes de crear la campaña</span>
              </div>
              <div class="space-y-2">
                <TarjetaActividadPlantilla
                  v-for="(act, idx) in actividadesPreview"
                  :key="act._id"
                  :actividad="act"
                  :indice="idx"
                  :voluntarios="voluntariosAmbito"
                  :habilidades="habilidades"
                  :niveles-habilidad="nivelesHabilidad"
                />
              </div>
            </div>

            <!-- Actividades: lista enlazada (modo edición) -->
            <div v-if="isEdit" class="border-t border-slate-100 pt-4">
              <div class="flex items-center justify-between mb-3">
                <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Actividades ({{ actividadesCampania.length }})
                </p>
                <router-link :to="`/actividades/nueva?campaniaId=${route.params.id}&campaniaNombre=${encodeURIComponent(campania.nombre)}`"
                  class="inline-flex items-center gap-1.5 h-7 px-3 text-xs font-medium text-indigo-600 hover:bg-indigo-50 border border-indigo-200 rounded-lg transition-colors">
                  <PlusIcon class="w-3.5 h-3.5" /> Nueva actividad
                </router-link>
              </div>
              <div v-if="!actividadesCampania.length"
                class="text-sm text-slate-400 italic py-4 text-center border border-dashed border-slate-200 rounded-xl">
                Sin actividades todavía.
              </div>
              <div v-else class="divide-y divide-slate-50 rounded-xl border border-slate-100 overflow-hidden">
                <div v-for="act in actividadesCampania" :key="act.id"
                  class="flex items-center gap-3 px-4 py-2.5 hover:bg-slate-50 group transition-colors">
                  <div class="flex-1 flex items-center gap-2 min-w-0">
                    <span class="shrink-0 w-20 text-xs text-slate-400 tabular-nums">
                      {{ act.fechaInicio ? fmtFechaCorta(act.fechaInicio) : '—' }}
                    </span>
                    <span class="text-sm font-medium text-slate-800 truncate">{{ act.nombre }}</span>
                    <span v-if="act.estado"
                      class="shrink-0 inline-flex px-1.5 py-0.5 rounded-full text-[10px] font-semibold"
                      :style="{ background: act.estado.color + '20', color: act.estado.color }">
                      {{ act.estado.nombre }}
                    </span>
                  </div>
                  <router-link :to="`/actividades/${act.id}`"
                    class="shrink-0 opacity-0 group-hover:opacity-100 text-xs font-medium text-indigo-600 hover:underline transition-opacity">
                    Editar →
                  </router-link>
                </div>
              </div>
            </div>

          </div>
        </AccordionPanel>

        <!-- ── 4 · COMUNICACIÓN Y METAS ─────────────────────────────────────── -->
        <AccordionPanel :default-open="false">
          <template #title>
            <span class="shrink-0 w-1.5 h-5 rounded-full bg-sky-500"></span>
            <h2 :class="titleCls">Comunicación y metas</h2>
          </template>
          <div class="px-5 py-4 space-y-5">

            <!-- Canales de difusión -->
            <div>
              <label :class="lbl">Canales de difusión</label>
              <div class="flex flex-wrap gap-2">
                <label v-for="canal in tiposCanal" :key="canal.id"
                  class="flex items-center gap-2 px-3 py-1.5 rounded-lg border cursor-pointer transition-colors text-sm select-none"
                  :class="canalesSeleccionados.includes(canal.id)
                    ? 'border-sky-400 bg-sky-50 text-sky-800'
                    : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'">
                  <input type="checkbox" class="sr-only"
                    :value="canal.id"
                    :checked="canalesSeleccionados.includes(canal.id)"
                    @change="toggleCanal(canal.id)" />
                  <span class="w-3.5 h-3.5 rounded border flex items-center justify-center shrink-0"
                    :class="canalesSeleccionados.includes(canal.id)
                      ? 'border-sky-500 bg-sky-500'
                      : 'border-slate-300 bg-white'">
                    <CheckIcon v-if="canalesSeleccionados.includes(canal.id)" class="w-2.5 h-2.5 text-white" />
                  </span>
                  {{ canal.nombre }}
                </label>
                <p v-if="!tiposCanal.length" class="text-xs text-slate-400 italic">
                  Sin canales configurados — añádelos en Parametrización
                </p>
              </div>
            </div>

            <!-- Metas -->
            <div class="border-t border-slate-100 pt-4">
              <div class="flex items-center justify-between mb-2">
                <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Metas de la campaña</p>
                <button type="button" @click="addMeta"
                  class="inline-flex items-center gap-1.5 text-xs text-sky-600 hover:text-sky-800 font-medium transition-colors">
                  <PlusIcon class="w-3.5 h-3.5" /> Añadir meta
                </button>
              </div>
              <div class="overflow-x-auto -mx-1"><table class="w-full">
                <thead>
                  <tr class="border-b border-slate-100">
                    <th class="pb-2 text-left text-xs font-semibold text-slate-400">Tipo de meta</th>
                    <th class="pb-2 w-full sm:w-32 text-right text-xs font-semibold text-slate-400 pr-1">Valor planificado</th>
                    <th class="pb-2 text-left text-xs font-semibold text-slate-400 pl-2">Notas</th>
                    <th class="w-7"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="!metas.length">
                    <td colspan="4" class="py-4 text-center text-xs text-slate-400 italic">
                      Sin metas — pulsa «Añadir» o selecciona una plantilla
                    </td>
                  </tr>
                  <tr v-for="(m, i) in metas" :key="m._id" class="border-b border-slate-50">
                    <td class="py-1.5 pr-2">
                      <select v-model="m.tipo_meta_id" :class="inpSm">
                        <option value="">— Tipo —</option>
                        <option v-for="t in tiposMeta" :key="t.id" :value="t.id">
                          {{ t.nombre }}<template v-if="t.unidad"> ({{ t.unidad }})</template>
                        </option>
                      </select>
                    </td>
                    <td class="py-1.5 pr-1">
                      <input v-model.number="m.valor_planificado" type="number" min="0"
                        :class="inpSm + ' text-right tabular-nums'" placeholder="0" />
                    </td>
                    <td class="py-1.5 pl-2 pr-2">
                      <input v-model="m.notas" type="text" :class="inpSm" placeholder="Notas opcionales" />
                    </td>
                    <td class="py-1.5 pl-1">
                      <button type="button" @click="metas.splice(i, 1)"
                        class="p-1 text-slate-300 hover:text-red-400 transition-colors">
                        <XMarkIcon class="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table></div>
            </div>

          </div>
        </AccordionPanel>

        <!-- ── 4 · VALORACIÓN Y CIERRE ──────────────────────────────────────── -->
        <AccordionPanel :default-open="false">
          <template #title>
            <span class="shrink-0 w-1.5 h-5 rounded-full bg-emerald-500"></span>
            <h2 :class="titleCls">Valoración y cierre</h2>
          </template>
          <div class="px-5 py-4 space-y-4">
            <div v-if="!isEdit" class="rounded-lg bg-slate-50 border border-slate-100 px-4 py-3">
              <p class="text-xs text-slate-500">Los datos de valoración y cierre se registran cuando la campaña finalice.</p>
            </div>
            <template v-else>
              <div class="grid grid-cols-12 gap-x-3 gap-y-4">
                <div class="col-span-4">
                  <label :class="lbl">Presupuesto ejecutado</label>
                  <div :class="inputGroupCls">
                    <span :class="prefixCls">€</span>
                    <input v-model.number="campania.presupuesto_ejecutado" type="number" min="0" step="0.01"
                      :class="inputGroupInp + ' tabular-nums'" placeholder="0,00" />
                  </div>
                </div>
                <div class="col-span-4 flex items-end pb-1">
                  <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                    <input type="checkbox" v-model="campania.objetivos_cumplidos" class="accent-indigo-600 w-4 h-4 rounded" />
                    Objetivos cumplidos
                  </label>
                </div>
                <div class="col-span-12">
                  <label :class="lbl">Valoración final</label>
                  <textarea v-model="campania.valoracion" rows="3" :class="inp"
                    placeholder="Balance de resultados, lecciones aprendidas…"
                    @input="autoResize" />
                </div>
              </div>
            </template>
          </div>
        </AccordionPanel>

      </AccordionGroup>

    </form>

  </AppLayout>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  CheckIcon,
  ExclamationTriangleIcon, PlusIcon, XMarkIcon, LinkIcon,
  DocumentPlusIcon, DocumentTextIcon, DocumentDuplicateIcon,
} from '@heroicons/vue/24/outline'
import AppLayout from '@/components/common/AppLayout.vue'
import FormActions from '@/components/common/FormActions.vue'
import AccordionGroup from '@/components/common/AccordionGroup.vue'
import AccordionPanel from '@/components/common/AccordionPanel.vue'
import TarjetaActividadPlantilla from '@/components/campanias/TarjetaActividadPlantilla.vue'
import { executeQuery, executeMutation } from '@/graphql/client.js'
import {
  GET_CAMPANIA, GET_TIPOS_CAMPANIA, GET_ESTADOS_CAMPANIA,
  CREAR_CAMPANIA, ACTUALIZAR_CAMPANIA,
  GET_TIPOS_META, GET_TIPOS_CANAL, GET_PLANTILLA_POR_TIPO,
  GUARDAR_METAS_CAMPANIA, GUARDAR_CANALES_CAMPANIA, GUARDAR_PARTIDAS_CAMPANIA,
  APLICAR_PLANTILLA,
} from '@/modules/comunicaciones/graphql/queries.js'
import { GET_AGRUPACIONES } from '@/graphql/queries/miembros.js'
import { GET_CAMPANIAS } from '@/graphql/queries/campanias.js'
import { ACTUALIZAR_ACCION, ACTUALIZAR_TAREA } from '@/modules/actividades/graphql/queries.js'
import { useFormValidation, required } from '@/composables/useFormValidation.js'

const GET_MIEMBROS_SIMPLE = `
  query MiembrosSimple {
    miembros: socios { id nombre apellido1 agrupacion { id }
      usuario { id activo roles { id activo eliminado agrupacionId rol { codigo } } }
    }
  }
`

const GET_HABILIDADES_NIVELES = `
  query HabilidadesNiveles {
    habilidades(filter: { activo: { eq: true } }) { id nombre }
    nivelesHabilidad(filter: { activo: { eq: true } }) { id nombre orden }
  }
`

// ── Constantes ───────────────────────────────────────────────────────────────
const PERIODICIDADES = [
  { value: 'anual',      label: 'Anual',      desc: 'Se repite cada año',         recurrente: true  },
  { value: 'permanente', label: 'Permanente', desc: 'En curso, sin fecha de fin',  recurrente: false },
  { value: 'puntual',    label: 'Puntual',    desc: 'Acción única',               recurrente: false },
  { value: 'semestral',  label: 'Semestral',  desc: 'Se repite cada 6 meses',     recurrente: true  },
]

// ── Validación ───────────────────────────────────────────────────────────────
const { errors, validate, validateField } = useFormValidation({
  nombre:             [required('El nombre de la campaña es obligatorio')],
  tipo_campania_id:   [required('Selecciona un tipo de campaña')],
  estado_campania_id: [required('Selecciona un estado')],
})

const estadoInicialNombre = computed(() => {
  const id = campania.value.estado_campania_id
  if (!id) return 'Borrador'
  return estadosCampania.value.find(e => e.id === id)?.nombre ?? 'Borrador'
})

// ── Estilos ──────────────────────────────────────────────────────────────────
const titleCls     = 'text-sm font-semibold text-slate-800'
const lbl          = 'block text-sm font-medium text-slate-700 mb-1.5'
const inp          = 'h-10 w-full px-3 py-2 text-sm border border-slate-300 rounded-lg transition-all ' +
                     'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ' +
                     'bg-white placeholder:text-slate-300 disabled:bg-slate-50 disabled:text-slate-400'
const _inpBase     = 'h-10 w-full px-3 py-2 text-sm border rounded-lg transition-all focus:outline-none focus:ring-2 ' +
                     'bg-white placeholder:text-slate-300 disabled:bg-slate-50 disabled:text-slate-400'
const fieldInp = (field) => errors[field]
  ? _inpBase + ' border-red-400 focus:ring-red-400 focus:border-red-400'
  : _inpBase + ' border-slate-300 focus:ring-indigo-500 focus:border-indigo-500'
const inpSm        = 'w-full px-2.5 py-1.5 text-sm border border-slate-300 rounded-lg transition-all ' +
                     'focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 ' +
                     'bg-white placeholder:text-slate-300'
const inputGroupCls   = 'flex h-10 rounded-lg border border-slate-300 overflow-hidden transition-all focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-indigo-500'
const prefixCls       = 'px-2.5 flex items-center bg-slate-50 border-r border-slate-200 text-slate-400 text-sm shrink-0'
const inputGroupInp   = 'flex-1 px-3 text-sm bg-white focus:outline-none placeholder:text-slate-300'
const inputGroupSmCls = 'flex rounded-lg border border-slate-300 overflow-hidden transition-all focus-within:ring-1 focus-within:ring-indigo-500 focus-within:border-indigo-500'
const prefixSmCls     = 'px-2 flex items-center bg-slate-50 border-r border-slate-200 text-slate-400 text-sm shrink-0'
const inputGroupInpSm = 'flex-1 px-2 py-1.5 text-sm bg-white focus:outline-none placeholder:text-slate-300'

// ── Router ───────────────────────────────────────────────────────────────────
const route      = useRoute()
const router     = useRouter()
const isEdit     = computed(() => !!route.params.id && !route.path.includes('/nueva'))
const loading    = ref(false)
const submitting = ref(false)
const error      = ref(null)

// ── Modelo campaña ───────────────────────────────────────────────────────────
const campania = ref({
  nombre: '', lema: '', descripcion_corta: '', descripcion_larga: '',
  url_externa: '', tipo_campania_id: '', estado_campania_id: '',
  periodicidad: 'puntual', fecha_inicio: '', fecha_fin: '',
  objetivo_principal: '', responsable_id: '', agrupacion_id: '',
  presupuesto_ejecutado: null, objetivos_cumplidos: false, valoracion: '',
})

// ── Metas ─────────────────────────────────────────────────────────────────────
const metas = ref([])
let _mid = 0
const addMeta = () => metas.value.push({ _id: ++_mid, tipo_meta_id: '', valor_planificado: null, notas: '' })

// ── Canales ──────────────────────────────────────────────────────────────────
const canalesSeleccionados = ref([])
const toggleCanal = (id) => {
  const idx = canalesSeleccionados.value.indexOf(id)
  if (idx === -1) canalesSeleccionados.value.push(id)
  else canalesSeleccionados.value.splice(idx, 1)
}

// ── Presupuesto ───────────────────────────────────────────────────────────────
const partidas = ref([])
let _pid = 0
const addPartida = () => partidas.value.push({ _id: ++_pid, concepto: '', tipo_partida: 'gasto', importe_estimado: null })
const totalPresupuesto = computed(() =>
  partidas.value.filter(p => p.tipo_partida === 'gasto').reduce((s, p) => s + (parseFloat(p.importe_estimado) || 0), 0)
)
const fmtEur = (n) => Number(n || 0).toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const fmtFechaCorta = (d) => d ? new Date(d + 'T12:00:00').toLocaleDateString('es-ES', { day: 'numeric', month: 'short' }) : ''

// ── Actividades (solo edición) ────────────────────────────────────────────────
const actividadesCampania = ref([])

// ── Actividades preview (creación con plantilla, editable en memoria) ─────────
let _aid = 0
const actividadesPreview = ref([])  // [{ _id, _open, nombre, tareas, fechaInicio, horaInicio, fechaFin, horaFin }]

// ── Origen (solo nueva campaña) ──────────────────────────────────────────────
const origenTipo          = ref('blanco')   // 'blanco' | 'plantilla' | 'clonar'
const campaniasCandidatas = ref([])
const clonarDeCampaniaId  = ref('')
const clonarSearch        = ref('')
const showClonarList      = ref(false)
const clonarCargando      = ref(false)

// Campañas del tipo seleccionado (para clonar)
const clonarCandidatasDelTipo = computed(() => {
  const tid = campania.value.tipo_campania_id
  if (!tid) return campaniasCandidatas.value
  return campaniasCandidatas.value.filter(c => c.tipoCampania?.id === tid)
})

const clonarFiltradas = computed(() => {
  const base = clonarCandidatasDelTipo.value
  const q = clonarSearch.value.trim().toLowerCase()
  if (!q) return base.slice(0, 20)
  return base.filter(c => c.nombre?.toLowerCase().includes(q)).slice(0, 20)
})

async function seleccionarOrigen(c) {
  if (!c) return
  clonarCargando.value = true
  try {
    const data = await executeQuery(GET_CAMPANIA, { id: c.id })
    const src = data.campanias?.[0]
    if (!src) return
    campania.value.agrupacion_id = src.agrupacion?.id || campania.value.agrupacion_id
    campania.value.periodicidad  = src.periodicidad || 'puntual'
    metas.value = (src.metas || []).map(m => ({
      _id: ++_mid, tipo_meta_id: m.tipoMeta?.id || '', valor_planificado: m.valorPlanificado ?? null, notas: m.notas || '',
    }))
    canalesSeleccionados.value = (src.canales || []).map(x => x.canal?.id).filter(Boolean)
    partidas.value = (src.partidasPresupuesto || []).map(p => ({
      _id: ++_pid, concepto: p.concepto, tipo_partida: p.tipoPartida || 'gasto', importe_estimado: p.importeEstimado ?? null,
    }))
  } catch { /* silently ignore */ } finally {
    clonarCargando.value = false
  }
}

// Reaccionar al cambio del select de clonar
watch(clonarDeCampaniaId, (id) => {
  if (!id) return
  const c = clonarCandidatasDelTipo.value.find(x => x.id === id)
  if (c) seleccionarOrigen(c)
})

// Al cambiar el origen se resetea la selección pero NO el tipo
watch(origenTipo, () => {
  plantillaSeleccionadaId.value = ''
  clonarDeCampaniaId.value = ''
  clonarSearch.value = ''
  metas.value = []
  partidas.value = []
  canalesSeleccionados.value = []
  actividadesPreview.value = []
})

// Al cambiar el tipo, si hay origen elegido se resetea la selección secundaria
watch(() => campania.value.tipo_campania_id, (newTipo, oldTipo) => {
  if (newTipo !== oldTipo) {
    plantillaSeleccionadaId.value = ''
    clonarDeCampaniaId.value = ''
    clonarSearch.value = ''
    // Si el origen actual ya no aplica, volver a blanco
    if (origenTipo.value !== 'blanco' && !newTipo) origenTipo.value = 'blanco'
  }
})

// ── Plantilla ─────────────────────────────────────────────────────────────────
const plantillaSeleccionadaId = ref('')
const plantillasDisponibles   = ref([])
const plantillaCargando       = ref(false)

const plantillaSeleccionadaInfo = computed(() =>
  plantillasDisponibles.value.find(p => p.id === plantillaSeleccionadaId.value) ?? null
)

async function loadPlantillasTipo(tipoCampaniaId) {
  plantillasDisponibles.value = []
  if (!tipoCampaniaId) return
  plantillaCargando.value = true
  try {
    const data = await executeQuery(GET_PLANTILLA_POR_TIPO, { tipoCampaniaId })
    plantillasDisponibles.value = data.plantillasCampania ?? []
    if (plantillasDisponibles.value.length && !isEdit.value && origenTipo.value === 'plantilla') {
      plantillaSeleccionadaId.value = plantillasDisponibles.value[0].id
    }
  } catch {
    plantillasDisponibles.value = []
  } finally {
    plantillaCargando.value = false
  }
}

watch(plantillaSeleccionadaId, (newId) => {
  const plantilla = plantillasDisponibles.value.find(p => p.id === newId)
  if (!plantilla) {
    metas.value = []
    partidas.value = []
    actividadesPreview.value = []
    return
  }
  metas.value = (plantilla.metas || []).map(m => ({
    _id: ++_mid, tipo_meta_id: m.tipoMeta?.id || '', valor_planificado: m.valorSugerido ?? null, notas: m.notas || '',
  }))
  partidas.value = (plantilla.partidas || []).map(p => ({
    _id: ++_pid, concepto: p.concepto || '', tipo_partida: p.tipoPartida || 'gasto', importe_estimado: p.importeEstimado ?? null,
  }))
  actividadesPreview.value = (plantilla.actividades || []).map(a => ({
    _id: ++_aid,
    _open: false,
    templateId: a.id,
    nombre: a.nombre,
    duracionHoras: a.duracionHoras ?? null,
    duracionDias: a.duracionDias ?? null,
    // Tareas con campos sobreescribibles por el usuario antes de crear
    tareas: (a.tareas || []).map(t => ({
      templateId: t.id,
      titulo: t.titulo,
      horasEstimadas: t.horasEstimadas ?? null,
      habilidadId: t.habilidad?.id || '',
      nivelHabilidadId: t.nivelHabilidad?.id || '',
    })),
    fechaInicio: '',
    horaInicio: '',
    fechaFin: '',
    horaFin: '',
    responsableId: '',
    lugar: '',
    direccion: '',
    localidad: '',
    provincia: '',
  }))
})

function onTipoCampaniaChange() {
  validateField('tipo_campania_id', campania.value.tipo_campania_id, campania)
  plantillaSeleccionadaId.value = ''
  loadPlantillasTipo(campania.value.tipo_campania_id)
}

// ── Periodicidad ──────────────────────────────────────────────────────────────
const periInfo = computed(() => {
  const p = campania.value.periodicidad
  if (p === 'permanente') return { labelInicio: 'Fecha de inicio', labelFin: '',              sinFin: true,  hint: null }
  if (p === 'puntual')    return { labelInicio: 'Fecha de inicio', labelFin: 'Fecha de fin',  sinFin: false, hint: null }
  if (p === 'anual')      return { labelInicio: 'Fecha de inicio', labelFin: 'Fin de campaña', sinFin: false, hint: '↻ Se repite anualmente' }
  if (p === 'semestral')  return { labelInicio: 'Fecha de inicio', labelFin: 'Fin de campaña', sinFin: false, hint: '↻ Se repite cada 6 meses' }
  return { labelInicio: 'Fecha de inicio', labelFin: 'Fecha de fin', sinFin: false, hint: null }
})
watch(() => campania.value.periodicidad, (nuevo) => {
  if (nuevo === 'permanente') campania.value.fecha_fin = ''
})


function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

// ── Catálogos ─────────────────────────────────────────────────────────────────
const tiposCampania   = ref([])
const estadosCampania = ref([])
const miembros        = ref([])
const agrupaciones    = ref([])
const tiposMeta       = ref([])
const tiposCanal      = ref([])
const habilidades     = ref([])
const nivelesHabilidad = ref([])

// ── Derivados de catálogos ────────────────────────────────────────────────────
const agrupacionesPorNivel = computed(() => {
  const map = {}
  agrupaciones.value.forEach(a => {
    const nombre = a.tipoUnidad?.nombre || 'Sin clasificar'
    const nivel  = a.tipoUnidad?.nivel  ?? 99
    const key    = `${String(nivel).padStart(3, '0')}__${nombre}`
    if (!map[key]) map[key] = { nivel, nombre, items: [] }
    map[key].items.push(a)
  })
  return Object.values(map)
    .sort((a, b) => a.nivel - b.nivel)
    .map(g => ({ ...g, items: g.items.sort((a, b) => a.nombre.localeCompare(b.nombre, 'es')) }))
})

const CAMP_COORD_ROLES = ['PLANIFICADOR', 'SUPERADMIN']

const sinCoordinadores = computed(() =>
  !!campania.value.agrupacion_id && responsablesCandidatos.value.length === 0
)

// Miembros activos en el ámbito de la campaña (para responsable de actividad)
const voluntariosAmbito = computed(() => {
  const agrupId = campania.value.agrupacion_id
  if (!agrupId) return miembros.value.filter(m => m.usuario?.activo)
  // Incluir miembros cuya agrupacion coincide con agrupId o cualquier descendiente
  const descendientes = new Set([agrupId])
  agrupaciones.value.forEach(a => {
    if (a.agrupacionPadreId && descendientes.has(a.agrupacionPadreId)) descendientes.add(a.id)
  })
  // Segunda pasada para indirect descendants
  agrupaciones.value.forEach(a => {
    if (a.agrupacionPadreId && descendientes.has(a.agrupacionPadreId)) descendientes.add(a.id)
  })
  return miembros.value.filter(m =>
    m.usuario?.activo && (!m.agrupacion_id || descendientes.has(m.agrupacion_id))
  )
})

function getAncestorIds(agrupId) {
  const ids = new Set([agrupId])
  let cur = agrupaciones.value.find(a => a.id === agrupId)
  while (cur?.agrupacionPadreId) {
    ids.add(cur.agrupacionPadreId)
    cur = agrupaciones.value.find(a => a.id === cur.agrupacionPadreId)
  }
  return ids
}

const responsablesCandidatos = computed(() => {
  const agrupId = campania.value.agrupacion_id
  const ancestros = agrupId ? getAncestorIds(agrupId) : new Set()
  return miembros.value.filter(m => {
    if (!m.usuario?.activo) return false
    const roles = m.usuario.roles || []
    if (!roles.length) return false
    return roles.some(r =>
      r.activo && !r.eliminado &&
      CAMP_COORD_ROLES.includes(r.rol?.codigo) &&
      (!agrupId || !r.agrupacionId || ancestros.has(r.agrupacionId))
    )
  })
})

// ── Carga ─────────────────────────────────────────────────────────────────────
onMounted(async () => {
  await loadCatalogos()
  if (isEdit.value) await loadCampania()
})

async function loadCatalogos() {
  const [rTipos, rEstados, rMbs, rAgrs, rMetas, rCanales, rCamp, rHab] = await Promise.allSettled([
    executeQuery(GET_TIPOS_CAMPANIA),
    executeQuery(GET_ESTADOS_CAMPANIA),
    executeQuery(GET_MIEMBROS_SIMPLE),
    executeQuery(GET_AGRUPACIONES),
    executeQuery(GET_TIPOS_META),
    executeQuery(GET_TIPOS_CANAL),
    executeQuery(GET_CAMPANIAS),
    executeQuery(GET_HABILIDADES_NIVELES),
  ])

  if (rTipos.status === 'fulfilled')
    tiposCampania.value = (rTipos.value.tiposCampania || []).filter(t => t.activo)
      .sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
  if (rEstados.status === 'fulfilled') {
    estadosCampania.value = (rEstados.value.estadosCampania || []).filter(e => e.activo)
      .sort((a, b) => (a.orden ?? 99) - (b.orden ?? 99))
    if (!isEdit.value && !campania.value.estado_campania_id) {
      const inicial = estadosCampania.value.find(e => e.nombre === 'Borrador') ?? estadosCampania.value[0]
      if (inicial) campania.value.estado_campania_id = inicial.id
    }
  }
  if (rMbs.status === 'fulfilled')
    miembros.value = (rMbs.value.miembros || []).map(m => ({
      id: m.id, nombre: m.nombre, apellido1: m.apellido1,
      agrupacion_id: m.agrupacion?.id || null,
      usuario: m.usuario || null,
    }))
  if (rAgrs.status === 'fulfilled') {
    agrupaciones.value = rAgrs.value.unidadesOrganizativas || []
    if (!isEdit.value && !campania.value.agrupacion_id) {
      const raiz = agrupaciones.value.find(a => !a.agrupacionPadreId)
      if (raiz) campania.value.agrupacion_id = raiz.id
    }
  }
  if (rMetas.status === 'fulfilled')
    tiposMeta.value = rMetas.value.tiposMetaCampania || []
  if (rCanales.status === 'fulfilled')
    tiposCanal.value = rCanales.value.tiposCanalDifusion || []
  if (rCamp.status === 'fulfilled')
    campaniasCandidatas.value = (rCamp.value.campanias || []).sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
  if (rHab.status === 'fulfilled') {
    habilidades.value = rHab.value.habilidades || []
    nivelesHabilidad.value = (rHab.value.nivelesHabilidad || []).sort((a, b) => a.orden - b.orden)
  }
}

async function loadCampania() {
  loading.value = true
  try {
    const data = await executeQuery(GET_CAMPANIA, { id: route.params.id })
    const c = data.campanias?.[0]
    if (c) {
      campania.value = {
        nombre:               c.nombre || '',
        lema:                 c.lema || '',
        descripcion_corta:    c.descripcionCorta || '',
        descripcion_larga:    c.descripcionLarga || '',
        url_externa:          c.urlExterna || '',
        tipo_campania_id:     c.tipoCampania?.id || '',
        estado_campania_id:   c.estado?.id || '',
        periodicidad:         c.periodicidad || 'puntual',
        fecha_inicio:         c.fechaInicioPlan || '',
        fecha_fin:            c.fechaFinPlan || '',
        objetivo_principal:   c.objetivoPrincipal || '',
        responsable_id:       c.responsable?.id || '',
        agrupacion_id:        c.agrupacion?.id || '',
        presupuesto_ejecutado: c.presupuestoEjecutado ?? null,
        objetivos_cumplidos:  c.objetivosCumplidos ?? false,
        valoracion:           c.valoracion || '',
      }
      metas.value = (c.metas || []).sort((a, b) => (a.orden ?? 0) - (b.orden ?? 0)).map(m => ({
        _id: ++_mid,
        tipo_meta_id:      m.tipoMeta?.id || '',
        valor_planificado: m.valorPlanificado ?? null,
        notas:             m.notas || '',
      }))
      canalesSeleccionados.value = (c.canales || []).map(c => c.canal?.id).filter(Boolean)
      partidas.value = (c.partidasPresupuesto || []).sort((a, b) => (a.orden ?? 0) - (b.orden ?? 0)).map(p => ({
        _id:              ++_pid,
        concepto:         p.concepto,
        tipo_partida:     p.tipoPartida || 'gasto',
        importe_estimado: p.importeEstimado ?? null,
      }))
      actividadesCampania.value = [...(c.actividades || [])].sort((a, b) => {
        const da = a.fechaInicio ?? '9999-99-99'
        const db = b.fechaInicio ?? '9999-99-99'
        return da !== db ? da.localeCompare(db) : (a.horaInicio ?? '').localeCompare(b.horaInicio ?? '')
      })
      if (c.tipoCampania?.id) loadPlantillasTipo(c.tipoCampania.id)
    }
  } catch {
    error.value = 'Error al cargar la campaña'
  } finally {
    loading.value = false
  }
}

// ── Submit ────────────────────────────────────────────────────────────────────
async function handleSubmit() {
  error.value = null
  if (!validate(campania.value)) return

  submitting.value = true
  try {
    const periActual = PERIODICIDADES.find(p => p.value === campania.value.periodicidad)
    const base = {
      nombre:            campania.value.nombre.trim(),
      tipoCampaniaId:    campania.value.tipo_campania_id,
      estadoId:          campania.value.estado_campania_id,
      lema:              campania.value.lema || null,
      descripcionCorta:  campania.value.descripcion_corta || null,
      descripcionLarga:  campania.value.descripcion_larga || null,
      urlExterna:        campania.value.url_externa || null,
      objetivoPrincipal: campania.value.objetivo_principal || null,
      fechaInicioPlan:   campania.value.fecha_inicio || null,
      fechaFinPlan:      campania.value.periodicidad === 'permanente' ? null : (campania.value.fecha_fin || null),
      responsableId:     campania.value.responsable_id || null,
      agrupacionId:      campania.value.agrupacion_id || null,
      periodicidad:          campania.value.periodicidad,
      esRecurrente:          periActual?.recurrente ?? false,
      presupuestoEjecutado:  campania.value.presupuesto_ejecutado ?? null,
      objetivosCumplidos:    campania.value.objetivos_cumplidos ?? false,
      valoracion:            campania.value.valoracion || null,
    }

    let campaniaId
    if (isEdit.value) {
      await executeMutation(ACTUALIZAR_CAMPANIA, { data: { campaniaId: route.params.id, ...base } })
      campaniaId = route.params.id
    } else {
      const res = await executeMutation(CREAR_CAMPANIA, { data: base })
      campaniaId = res.crearCampania.id
    }

    if (!isEdit.value && origenTipo.value === 'plantilla' && plantillaSeleccionadaId.value) {
      const rPlantilla = await executeMutation(APLICAR_PLANTILLA, { campaniaId, plantillaId: plantillaSeleccionadaId.value })
      // Parchear fechas de actividades creadas usando el orden de creación (coincide con actividadesPreview)
      const actsCreadadas = rPlantilla.aplicarPlantilla?.actividades ?? []
      const patches = []
      actividadesPreview.value.forEach((prev, i) => {
        const act = actsCreadadas[i]
        if (!act) return
        // Patch actividad si tiene algún dato sobreescrito
        const hasActData = prev.fechaInicio || prev.horaInicio || prev.fechaFin || prev.horaFin
          || prev.responsableId || prev.lugar || prev.direccion || prev.localidad || prev.provincia
          || prev.duracionHoras || prev.duracionDias
        if (hasActData) {
          patches.push(executeMutation(ACTUALIZAR_ACCION, { data: {
            id: act.id,
            fechaInicio: prev.fechaInicio || null,
            horaInicio: prev.horaInicio || null,
            fechaFin: prev.fechaFin || null,
            horaFin: prev.horaFin || null,
            responsableId: prev.responsableId || null,
            lugar: prev.lugar || null,
            direccion: prev.direccion || null,
            localidad: prev.localidad || null,
            provincia: prev.provincia || null,
            duracionHoras: prev.duracionHoras || null,
            duracionDias: prev.duracionDias || null,
          }}))
        }
        // Patch tareas con overrides (horas/habilidad distintos del template)
        const actTareas = act.tareas || []
        prev.tareas.forEach((pt, j) => {
          const realTarea = actTareas[j]
          if (!realTarea) return
          const hasTareaData = pt.horasEstimadas || pt.habilidadId || pt.nivelHabilidadId
          if (!hasTareaData) return
          patches.push(executeMutation(ACTUALIZAR_TAREA, { data: {
            id: realTarea.id,
            horasEstimadas: pt.horasEstimadas || null,
            habilidadId: pt.habilidadId || null,
            nivelHabilidadId: pt.nivelHabilidadId || null,
          }}))
        })
      })
      if (patches.length) await Promise.all(patches)
    }

    await Promise.all([
      executeMutation(GUARDAR_METAS_CAMPANIA, {
        campaniaId,
        metas: metas.value
          .filter(m => m.tipo_meta_id)
          .map((m, i) => ({
            tipo_meta_id:      m.tipo_meta_id,
            valor_planificado: m.valor_planificado ?? null,
            notas:             m.notas || null,
            orden:             i,
          })),
      }),
      executeMutation(GUARDAR_CANALES_CAMPANIA, {
        campaniaId,
        canal_ids: canalesSeleccionados.value,
      }),
      executeMutation(GUARDAR_PARTIDAS_CAMPANIA, {
        campaniaId,
        partidas: partidas.value
          .filter(p => p.concepto?.trim())
          .map((p, i) => ({
            concepto:         p.concepto.trim(),
            importe_estimado: parseFloat(p.importe_estimado) ?? null,
            tipo_partida:     p.tipo_partida || 'gasto',
            orden:            i,
          })),
      }),
    ])

    router.push(`/campanias/${campaniaId}`)
  } catch (e) {
    console.error('Error guardando campaña:', e)
    error.value = e?.response?.errors?.[0]?.message || 'Error al guardar. Por favor, inténtalo de nuevo.'
  } finally {
    submitting.value = false
  }
}
</script>
