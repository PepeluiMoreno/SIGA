<template>
  <AppLayout
    :title="tituloVista"
    :subtitle="subtituloVista">

    <!-- El registro de cargos es una acción de edición, no de consulta -->
    <template v-if="!esNuevo && agrupacion && (tienePermiso('CFG_TERRITORIO_EDITAR') || tienePermiso('NOM_CREATE'))" #actions>
      <button type="button" @click="toggleEdicion"
        class="h-8 px-3 text-sm font-medium border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
        :class="editMode ? 'text-slate-600' : 'text-indigo-600'">
        {{ editMode ? 'Hecho' : 'Editar' }}
      </button>
    </template>

    <div class="flex items-center justify-between mb-4">
      <router-link to="/agrupaciones"
        class="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 transition-colors">
        <ChevronLeftIcon class="w-4 h-4" /> Volver al árbol
      </router-link>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>
    <div v-else-if="error" class="rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
      {{ error }}
    </div>

    <!-- ══ ALTA DE NUEVA UNIDAD ══════════════════════════════════════════════ -->
    <section v-else-if="esNuevo" :class="cardCls">
      <div class="px-5 py-4 space-y-5">
        <!-- Tipo + padre -->
        <div class="grid grid-cols-12 gap-x-4 gap-y-3 text-sm">
          <div class="col-span-12 sm:col-span-6">
            <p :class="lbl">Depende de</p>
            <p :class="ro">{{ padreUnidad?.nombre || '(unidad raíz)' }}</p>
          </div>
          <div class="col-span-12 sm:col-span-6">
            <p :class="lbl">Tipo de unidad <span class="text-red-400">*</span></p>
            <select v-model="formTipoId" :class="inp">
              <option value="">— Seleccionar —</option>
              <option v-for="t in tiposDisponibles" :key="t.id" :value="t.id">{{ t.nombre }}</option>
            </select>
          </div>
        </div>

        <!-- Generales -->
        <div class="grid grid-cols-12 gap-x-4 gap-y-3 text-sm">
          <div class="col-span-12 sm:col-span-8">
            <p :class="lbl">Nombre oficial <span class="text-red-400">*</span></p>
            <input v-model="form.nombre" type="text" :class="inp" />
          </div>
          <div class="col-span-12 sm:col-span-4">
            <p :class="lbl">Nombre corto</p>
            <input v-model="form.nombreCorto" type="text" :class="inp" />
          </div>
          <div class="col-span-12">
            <p :class="lbl">Descripción</p>
            <textarea v-model="form.descripcion" rows="2" :class="inpTa"></textarea>
          </div>
        </div>

        <!-- Contacto -->
        <div>
          <p class="text-[11px] font-semibold uppercase tracking-wide text-slate-400 mb-2">Contacto</p>
          <div class="grid grid-cols-12 gap-x-4 gap-y-3 text-sm">
            <div class="col-span-12 sm:col-span-5"><p :class="lbl">Email</p><input v-model="form.email" type="email" :class="inp" /></div>
            <div class="col-span-6 sm:col-span-3"><p :class="lbl">Teléfono</p><input v-model="form.telefono" type="text" :class="inp" /></div>
            <div class="col-span-6 sm:col-span-4"><p :class="lbl">Web</p><input v-model="form.web" type="url" :class="inp" /></div>
          </div>
        </div>

        <!-- Ubicación -->
        <div>
          <p class="text-[11px] font-semibold uppercase tracking-wide text-slate-400 mb-2">Ubicación</p>
          <div class="grid grid-cols-12 gap-x-4 gap-y-3 text-sm">
            <div class="col-span-12 sm:col-span-4">
              <p :class="lbl">País <span class="text-red-400">*</span></p>
              <select v-model="form.paisId" @change="onPaisChange" :class="inp">
                <option value="">— Seleccionar —</option>
                <option v-for="p in paises" :key="p.id" :value="p.id">{{ p.nombre }}</option>
              </select>
            </div>
            <div class="col-span-6 sm:col-span-4">
              <p :class="lbl">Provincia</p>
              <select v-model="form.provinciaId" @change="onProvinciaChange" :disabled="!form.paisId" :class="inp + ' disabled:bg-slate-50 disabled:text-slate-400'">
                <option value="">— Seleccionar —</option>
                <option v-for="p in provinciasDelPais" :key="p.id" :value="p.id">{{ p.nombre }}</option>
              </select>
            </div>
            <div class="col-span-6 sm:col-span-4">
              <p :class="lbl">Municipio</p>
              <select v-model="form.municipioId" :disabled="!form.provinciaId" :class="inp + ' disabled:bg-slate-50 disabled:text-slate-400'">
                <option value="">— Seleccionar —</option>
                <option v-for="m in municipios" :key="m.id" :value="m.id">{{ m.nombre }}</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Datos jurídicos (solo si el nivel elegido es FILIAL / FEDERADA) -->
        <div v-if="tipoSelEsJuridica">
          <p class="text-[11px] font-semibold uppercase tracking-wide text-slate-400 mb-2">Datos jurídicos</p>
          <div class="grid grid-cols-12 gap-x-4 gap-y-3 text-sm">
            <div class="col-span-6 sm:col-span-4"><p :class="lbl">NIF / CIF</p><input v-model="form.nif" type="text" :class="inp" /></div>
            <div class="col-span-6 sm:col-span-4"><p :class="lbl">Fecha de constitución</p><input v-model="form.fechaConstitucion" type="date" :class="inp" /></div>
            <div class="col-span-12 sm:col-span-4"><p :class="lbl">Registro oficial</p><input v-model="form.registroOficial" type="text" :class="inp" /></div>
          </div>
        </div>

        <ErrorAlert v-if="datosError" :message="datosError" />

        <div class="flex justify-end gap-2 pt-3 border-t border-slate-100">
          <router-link to="/agrupaciones"
            class="px-4 py-2 text-sm text-slate-600 border border-slate-300 rounded-lg hover:bg-slate-50">Cancelar</router-link>
          <button type="button" @click="guardarNuevo" :disabled="creando || !form.nombre.trim() || !form.paisId || !formTipoId"
            class="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50">
            <span v-if="creando" class="animate-spin inline-block h-3 w-3 border-2 border-white border-t-transparent rounded-full"></span>
            Crear unidad
          </button>
        </div>
      </div>
    </section>

    <div v-else-if="!agrupacion" class="rounded-xl border border-slate-200 bg-white px-6 py-10 text-center text-sm text-slate-500">
      Agrupación no encontrada.
    </div>

    <div v-else class="space-y-3">

      <!-- ══ 1 · DATOS GENERALES ════════════════════════════════════════════ -->
      <section :class="cardCls">
        <button type="button" @click="togglePanel('info')" :class="accordionBtn(open.info)">
          <span class="flex items-center gap-3">
            <span class="shrink-0 w-1.5 h-5 rounded-full bg-indigo-500"></span>
            <h2 :class="titleCls">Datos generales</h2>
          </span>
          <ChevronDownIcon :class="chevronCls(open.info)" />
        </button>
        <div v-show="open.info" class="px-5 py-4 space-y-5">

          <!-- Generales -->
          <div class="grid grid-cols-12 gap-x-4 gap-y-3 text-sm">
            <div class="col-span-12 sm:col-span-5">
              <p :class="lbl">Nombre oficial</p>
              <input v-if="editMode" v-model="form.nombre" type="text" :class="inp" />
              <p v-else :class="ro + ' font-medium text-slate-800'">{{ agrupacion.nombre }}</p>
            </div>
            <div class="col-span-6 sm:col-span-3">
              <p :class="lbl">Nombre corto</p>
              <input v-if="editMode" v-model="form.nombreCorto" type="text" :class="inp" />
              <p v-else :class="ro">{{ agrupacion.nombreCorto || '—' }}</p>
            </div>
            <div class="col-span-6 sm:col-span-2">
              <p :class="lbl">Tipo de unidad</p>
              <p :class="ro">{{ agrupacion.tipoUnidad?.nombre || '—' }}</p>
            </div>
            <div class="col-span-12 sm:col-span-2">
              <p :class="lbl">Depende de</p>
              <p :class="ro">{{ agrupacion.agrupacionPadreId ? '—' : '(raíz)' }}</p>
            </div>
            <div class="col-span-12">
              <p :class="lbl">Descripción</p>
              <textarea v-if="editMode" v-model="form.descripcion" rows="2" :class="inpTa"></textarea>
              <p v-else :class="ro">{{ agrupacion.descripcion || '—' }}</p>
            </div>
          </div>

          <!-- Contacto -->
          <div>
            <p class="text-[11px] font-semibold uppercase tracking-wide text-slate-400 mb-2">Contacto</p>
            <div class="grid grid-cols-12 gap-x-4 gap-y-3 text-sm">
              <div class="col-span-12 sm:col-span-5">
                <p :class="lbl">Email</p>
                <input v-if="editMode" v-model="form.email" type="email" :class="inp" />
                <a v-else-if="agrupacion.email" :href="`mailto:${agrupacion.email}`" :class="ro + ' block text-indigo-600 hover:underline'">{{ agrupacion.email }}</a>
                <p v-else :class="ro">—</p>
              </div>
              <div class="col-span-6 sm:col-span-3">
                <p :class="lbl">Teléfono</p>
                <input v-if="editMode" v-model="form.telefono" type="text" :class="inp" />
                <p v-else :class="ro">{{ agrupacion.telefono || '—' }}</p>
              </div>
              <div class="col-span-6 sm:col-span-4">
                <p :class="lbl">Web</p>
                <input v-if="editMode" v-model="form.web" type="url" :class="inp" />
                <a v-else-if="agrupacion.web" :href="agrupacion.web" target="_blank" rel="noopener" :class="ro + ' block text-indigo-600 hover:underline truncate'">{{ agrupacion.web }}</a>
                <p v-else :class="ro">—</p>
              </div>
            </div>
          </div>

          <!-- Ubicación -->
          <div>
            <p class="text-[11px] font-semibold uppercase tracking-wide text-slate-400 mb-2">Ubicación</p>
            <div class="grid grid-cols-12 gap-x-4 gap-y-3 text-sm">
              <div class="col-span-12 sm:col-span-4">
                <p :class="lbl">País</p>
                <select v-if="editMode" v-model="form.paisId" @change="onPaisChange" :class="inp">
                  <option value="">— Seleccionar —</option>
                  <option v-for="p in paises" :key="p.id" :value="p.id">{{ p.nombre }}</option>
                </select>
                <p v-else :class="ro">{{ paisNombre }}</p>
              </div>
              <div class="col-span-6 sm:col-span-4">
                <p :class="lbl">Provincia</p>
                <select v-if="editMode" v-model="form.provinciaId" @change="onProvinciaChange" :disabled="!form.paisId" :class="inp + ' disabled:bg-slate-50 disabled:text-slate-400'">
                  <option value="">— Seleccionar —</option>
                  <option v-for="p in provinciasDelPais" :key="p.id" :value="p.id">{{ p.nombre }}</option>
                </select>
                <p v-else :class="ro">{{ provinciaNombre }}</p>
              </div>
              <div class="col-span-6 sm:col-span-4">
                <p :class="lbl">Municipio</p>
                <select v-if="editMode" v-model="form.municipioId" :disabled="!form.provinciaId" :class="inp + ' disabled:bg-slate-50 disabled:text-slate-400'">
                  <option value="">— Seleccionar —</option>
                  <option v-for="m in municipios" :key="m.id" :value="m.id">{{ m.nombre }}</option>
                </select>
                <p v-else :class="ro">{{ municipioNombre }}</p>
              </div>
            </div>
          </div>

          <ErrorAlert v-if="datosError" :message="datosError" />

          <!-- Guardar (solo en edición) -->
          <div v-if="editMode" class="flex justify-end pt-3 border-t border-slate-100">
            <button type="button" @click="guardarDatos" :disabled="guardandoDatos || !form.nombre.trim()"
              class="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50">
              <span v-if="guardandoDatos" class="animate-spin inline-block h-3 w-3 border-2 border-white border-t-transparent rounded-full"></span>
              Guardar cambios
            </button>
          </div>
        </div>
      </section>

      <!-- ══ CONFIGURACIÓN ═════════════════════════════════════════════════ -->
      <section :class="cardCls">
        <button type="button" @click="togglePanel('config')" :class="accordionBtn(open.config)">
          <span class="flex items-center gap-3">
            <span class="shrink-0 w-1.5 h-5 rounded-full bg-sky-500"></span>
            <h2 :class="titleCls">Configuración</h2>
          </span>
          <ChevronDownIcon :class="chevronCls(open.config)" />
        </button>
        <div v-show="open.config" class="px-5 py-4 space-y-5">

          <!-- Datos jurídicos (solo entidades FILIAL / FEDERADA con personalidad propia) -->
          <div v-if="esEntidadJuridica">
            <p class="text-[11px] font-semibold uppercase tracking-wide text-slate-400 mb-2">Datos jurídicos</p>
            <div class="grid grid-cols-12 gap-x-4 gap-y-3 text-sm">
              <div class="col-span-6 sm:col-span-4">
                <p :class="lbl">NIF / CIF</p>
                <input v-if="editMode" v-model="form.nif" type="text" :class="inp" />
                <p v-else :class="ro">{{ agrupacion.nif || '—' }}</p>
              </div>
              <div class="col-span-6 sm:col-span-4">
                <p :class="lbl">Fecha de constitución</p>
                <input v-if="editMode" v-model="form.fechaConstitucion" type="date" :class="inp" />
                <p v-else :class="ro">{{ fmtFecha(agrupacion.fechaConstitucion) }}</p>
              </div>
              <div class="col-span-12 sm:col-span-4">
                <p :class="lbl">Registro oficial</p>
                <input v-if="editMode" v-model="form.registroOficial" type="text" :class="inp" />
                <p v-else :class="ro">{{ agrupacion.registroOficial || '—' }}</p>
              </div>
            </div>
            <div v-if="editMode" class="flex justify-end pt-3 mt-3 border-t border-slate-100">
              <button type="button" @click="guardarDatos" :disabled="guardandoDatos || !form.nombre.trim()"
                class="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50">
                <span v-if="guardandoDatos" class="animate-spin inline-block h-3 w-3 border-2 border-white border-t-transparent rounded-full"></span>
                Guardar cambios
              </button>
            </div>
          </div>

          <!-- Estructura interna -->
          <div>
            <p class="text-[11px] font-semibold uppercase tracking-wide text-slate-400 mb-2">Estructura interna</p>
            <div v-if="esDistribuida">
              <p class="text-xs text-slate-500 mb-3">
                El nivel «{{ agrupacion.tipoUnidad?.nombre }}» es de estructura <strong>distribuida</strong>:
                esta unidad define su propia subestructura territorial.
              </p>
              <EstructuraOrganizativaEditor
                :nivel-raiz-id="agrupacion.tipoId"
                :unidad-id="agrupacionId"
                :mostrar-radiogroup="false" />
            </div>
            <p v-else class="text-xs text-slate-400 italic">
              Estructura <strong>centralizada</strong>: los niveles se definen en Parámetros Generales (iguales para todas las unidades).
            </p>
          </div>
        </div>
      </section>

      <!-- ══ JUNTA DIRECTIVA ═══════════════════════════════════════════════ -->
      <section :class="cardCls">
        <button type="button" @click="togglePanel('junta')" :class="accordionBtn(open.junta)">
          <span class="flex items-center gap-3">
            <span class="shrink-0 w-1.5 h-5 rounded-full bg-amber-500"></span>
            <h2 :class="titleCls">{{ orgConfig.OrganoGobierno }}</h2>
            <span v-if="composicionJunta.length"
              class="px-2 py-0.5 bg-amber-50 text-amber-700 border border-amber-200 text-xs font-semibold rounded-full tabular-nums">
              {{ composicionJunta.length }}
            </span>
          </span>
          <ChevronDownIcon :class="chevronCls(open.junta)" />
        </button>
        <div v-show="open.junta" class="px-5 pb-4 pt-2">
          <div v-if="editMode && tienePermiso('NOM_CREATE')" class="flex justify-end mb-3">
            <button type="button" @click="abrirRegistro(null)"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200 transition-colors">
              <PlusIcon class="w-3.5 h-3.5" /> Registrar cargo
            </button>
          </div>
          <div v-if="!composicionJunta.length" class="py-8 text-center text-xs text-slate-400 italic">
            Sin cargos electos en esta unidad.<template v-if="!editMode"> Entra en modo edición para registrarlos.</template>
          </div>
          <div v-else class="overflow-x-auto -mx-1"><table class="w-full">
            <thead>
              <tr class="border-b border-slate-100">
                <th class="pb-2 text-left text-xs font-semibold text-slate-400">Cargo</th>
                <th class="pb-2 text-left text-xs font-semibold text-slate-400">Titular</th>
                <th class="pb-2 text-left text-xs font-semibold text-slate-400 hidden sm:table-cell">Desde</th>
                <th class="w-10"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in composicionJunta" :key="c.id"
                class="group border-b border-slate-50 last:border-0 hover:bg-amber-50/40 transition-colors">
                <td class="py-2.5 pr-3">
                  <span class="inline-block px-2 py-0.5 bg-amber-100 text-amber-800 text-xs font-semibold rounded-full">{{ c.rol?.nombre || '—' }}</span>
                </td>
                <td class="py-2.5 pr-3 text-sm font-medium text-slate-800">
                  {{ c.miembro?.apellido1 }}{{ c.miembro?.apellido2 ? ' ' + c.miembro.apellido2 : '' }}, {{ c.miembro?.nombre }}
                </td>
                <td class="py-2.5 pr-3 text-sm text-slate-500 hidden sm:table-cell">{{ fmtFecha(c.fechaInicio) }}</td>
                <td class="py-2.5 text-right">
                  <button v-if="c.miembro?.id" type="button" @click="verFicha(c.miembro.id)"
                    class="p-1 rounded text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors opacity-0 group-hover:opacity-100"
                    :title="`Ver ficha del ${orgConfig.miembro}`">
                    <EyeIcon class="w-4 h-4" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table></div>
        </div>
      </section>

      <!-- ══ 2 · SOCIOS DE LA UNIDAD ═══════════════════════════════════════ -->
      <section :class="cardCls">
        <button type="button" @click="togglePanel('cargos')" :class="accordionBtn(open.cargos)">
          <span class="flex items-center gap-3">
            <span class="shrink-0 w-1.5 h-5 rounded-full bg-violet-500"></span>
            <h2 :class="titleCls">{{ orgConfig.Miembros }} de la unidad</h2>
            <span v-if="miembros.length"
              class="px-2 py-0.5 bg-violet-50 text-violet-700 border border-violet-200 text-xs font-semibold rounded-full tabular-nums">
              {{ miembros.length }}
            </span>
          </span>
          <ChevronDownIcon :class="chevronCls(open.cargos)" />
        </button>
        <div v-show="open.cargos" class="px-5 pb-4 pt-2">

          <!-- Barra de acción (solo en modo edición y con permiso de cargos) -->
          <div v-if="editMode && tienePermiso('NOM_CREATE')" class="flex justify-end mb-3">
            <button type="button" @click="abrirRegistro(null)"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-violet-50 text-violet-700 hover:bg-violet-100 border border-violet-200 transition-colors">
              <PlusIcon class="w-3.5 h-3.5" /> Registrar cargo
            </button>
          </div>

          <div v-if="!miembros.length"
            class="py-8 text-center text-xs text-slate-400 italic">
            Sin socios en esta unidad.
          </div>
          <div v-else class="overflow-x-auto -mx-1"><table class="w-full">
            <thead>
              <tr class="border-b border-slate-100">
                <th class="pb-2 text-left text-xs font-semibold text-slate-400">{{ orgConfig.Miembro }}</th>
                <th class="pb-2 text-left text-xs font-semibold text-slate-400">Cargo</th>
                <th class="pb-2 text-left text-xs font-semibold text-slate-400 hidden md:table-cell">Email</th>
                <th class="w-12"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in miembros" :key="s.id"
                class="group border-b border-slate-50 last:border-0 hover:bg-indigo-50/40 cursor-pointer transition-colors"
                @click="verFicha(s.id)">
                <td class="py-2.5 pr-3">
                  <span class="text-sm font-medium text-slate-800">{{ s.apellido1 }}{{ s.apellido2 ? ' ' + s.apellido2 : '' }}, {{ s.nombre }}</span>
                </td>
                <td class="py-2.5 pr-3">
                  <span v-for="c in cargosDe(s.id)" :key="c"
                    class="inline-block mr-1 px-2 py-0.5 bg-violet-100 text-violet-800 text-xs font-semibold rounded-full">
                    {{ c }}
                  </span>
                  <span v-if="!cargosDe(s.id).length" class="text-xs text-slate-300">—</span>
                </td>
                <td class="py-2.5 pr-3 text-sm text-slate-500 hidden md:table-cell">{{ s.email || '—' }}</td>
                <td class="py-2.5 text-right">
                  <div class="inline-flex items-center gap-0.5 opacity-0 group-hover:opacity-100">
                    <button v-if="editMode" type="button" @click.stop="abrirTraslado(s)"
                      class="p-1 rounded text-slate-400 hover:text-amber-600 hover:bg-amber-50 transition-colors"
                      :title="`Trasladar ${orgConfig.miembro} a otra unidad`">
                      <ArrowsRightLeftIcon class="w-4 h-4" />
                    </button>
                    <button type="button" @click.stop="verFicha(s.id)"
                      class="p-1 rounded text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                      :title="`Ver ficha del ${orgConfig.miembro}`">
                      <EyeIcon class="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table></div>
        </div>
      </section>

    </div>

    <!-- ══ Modal registro de cargo ════════════════════════════════════════ -->
    <div v-if="modal.visible" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md">
        <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <h3 class="font-semibold text-slate-800">
            {{ modal.editandoId ? 'Editar registro de cargo' : 'Registrar cargo' }}
          </h3>
          <button @click="modal.visible = false" class="text-slate-400 hover:text-slate-600 text-xl leading-none">&times;</button>
        </div>
        <div class="px-6 py-5 space-y-4">
          <!-- Cargo (solo lectura si editando, selector si nuevo) -->
          <div v-if="!modal.editandoId">
            <label :class="lbl">Cargo <span class="text-red-400">*</span></label>
            <select v-model="modal.rolId" :class="inp">
              <option value="">— Seleccionar cargo —</option>
              <option v-for="r in rolesTerritoriales" :key="r.id" :value="r.id">{{ r.nombre }}</option>
            </select>
          </div>
          <div v-else>
            <label :class="lbl">Cargo</label>
            <p class="text-sm text-slate-700 font-medium">{{ modal.rolNombre }}</p>
          </div>

          <!-- Titular: socios de esta unidad y de las que cuelgan de ella (recursivo) -->
          <div>
            <label :class="lbl">Titular <span class="text-red-400">*</span></label>
            <select v-model="modal.miembroId" :class="inp">
              <option :value="null">— Seleccionar {{ orgConfig.miembro }} activo —</option>
              <option v-for="m in candidatosJunta" :key="m.id" :value="m.id">
                {{ [m.apellido1, m.apellido2].filter(Boolean).join(' ') }}, {{ m.nombre }}<template v-if="m.agrupacionId && m.agrupacionId !== agrupacionId"> · {{ nombreUnidad(m.agrupacionId) }}</template>
              </option>
            </select>
            <p v-if="!candidatosJunta.length" class="mt-1 text-xs text-slate-400">No hay {{ orgConfig.miembros }} activos en esta unidad ni en las que dependen de ella.</p>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label :class="lbl">Fecha inicio <span class="text-red-400">*</span></label>
              <input v-model="modal.fechaInicio" type="date" :class="inp" />
            </div>
            <div>
              <label :class="lbl">Fecha fin</label>
              <input v-model="modal.fechaFin" type="date" :class="inp" />
            </div>
          </div>
          <div>
            <label :class="lbl">Observaciones</label>
            <textarea v-model="modal.observaciones" rows="2" :class="inpTa"
              placeholder="Notas sobre el cargo…"></textarea>
          </div>
          <ErrorAlert v-if="modal.error" :message="modal.error" />
        </div>
        <div class="px-6 py-4 border-t border-slate-100 flex justify-end gap-3">
          <button @click="modal.visible = false"
            class="px-4 py-2 text-sm text-slate-600 border border-slate-300 rounded-lg hover:bg-slate-50">
            Cancelar
          </button>
          <button @click="guardarRegistro"
            :disabled="!modal.miembroId || !modal.fechaInicio || (!modal.editandoId && !modal.rolId) || modal.guardando"
            class="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 font-medium">
            <span v-if="modal.guardando" class="animate-spin inline-block h-3 w-3 border-2 border-white border-t-transparent rounded-full mr-1"></span>
            {{ modal.editandoId ? 'Guardar' : 'Registrar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ══ Modal traslado de socio a otra unidad ══════════════════════════ -->
    <div v-if="trasladoModal.visible" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md">
        <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <h3 class="font-semibold text-slate-800">Trasladar {{ orgConfig.miembro }} de unidad</h3>
          <button @click="trasladoModal.visible = false" class="text-slate-400 hover:text-slate-600 text-xl leading-none">&times;</button>
        </div>
        <div class="px-6 py-5 space-y-4">
          <p class="text-sm text-slate-600">
            Trasladar a <strong>{{ trasladoModal.socio?.nombre }} {{ trasladoModal.socio?.apellido1 }}</strong>
            desde <strong>{{ agrupacion?.nombre }}</strong> a otra unidad.
          </p>
          <div>
            <label :class="lbl">Unidad de destino <span class="text-red-400">*</span></label>
            <select v-model="trasladoModal.destinoId" :class="inp">
              <option value="">— Seleccionar unidad —</option>
              <option v-for="u in unidadesDestinoFiltradas" :key="u.id" :value="u.id">{{ etiquetaUnidad(u) }}</option>
            </select>
          </div>
          <ErrorAlert v-if="trasladoModal.error" :message="trasladoModal.error" />
        </div>
        <div class="px-6 py-4 border-t border-slate-100 flex justify-end gap-3">
          <button @click="trasladoModal.visible = false"
            class="px-4 py-2 text-sm text-slate-600 border border-slate-300 rounded-lg hover:bg-slate-50">Cancelar</button>
          <button @click="confirmarTraslado" :disabled="!trasladoModal.destinoId || trasladoModal.guardando"
            class="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 font-medium">
            <span v-if="trasladoModal.guardando" class="animate-spin inline-block h-3 w-3 border-2 border-white border-t-transparent rounded-full mr-1"></span>
            Trasladar
          </button>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { useConfirm } from '@/composables/useConfirm'
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ChevronDownIcon, ChevronLeftIcon,
  PencilIcon, PlusIcon, XMarkIcon, EyeIcon, ArrowsRightLeftIcon,
} from '@heroicons/vue/24/outline'
import AppLayout from '@/components/common/AppLayout.vue'
import EstructuraOrganizativaEditor from '@/components/configuracion/EstructuraOrganizativaEditor.vue'
import { usePermisos } from '@/composables/usePermisos.js'
import { useOrgConfigStore } from '@/stores/orgConfig.js'
import { executeQuery, executeMutation } from '@/graphql/client.js'
const confirmDialog = useConfirm()
const { tienePermiso } = usePermisos()
const orgConfig = useOrgConfigStore()

const route = useRoute()
const router = useRouter()
const agrupacionId = computed(() => route.params.id)
// Modo edición: el registro de cargos vive en edición, no en consulta.
const editMode = ref(false)

// ── Modo alta (crear nueva unidad) ──────────────────────────────────────────
const esNuevo       = computed(() => route.name === 'NuevaAgrupacion')
const padreIdParam  = computed(() => route.query.padre || null)
const niveles       = ref([])   // plantillas de nivel (NivelOrganizativo)
const todasUnidades = ref([])   // unidades activas (árbol: id + agrupacionPadreId)
const candidatos    = ref([])   // todos los socios activos (pool de candidatos a cargos)
const formTipoId    = ref('')
const creando       = ref(false)

// Subárbol de esta unidad (ella + descendientes). Recursivo: la raíz abarca todo.
const idsSubarbol = computed(() => {
  const ids = new Set()
  if (!agrupacionId.value) return ids
  ids.add(agrupacionId.value)
  const hijosDe = {}
  todasUnidades.value.forEach(u => {
    if (u.agrupacionPadreId) (hijosDe[u.agrupacionPadreId] ||= []).push(u.id)
  })
  const pila = [agrupacionId.value]
  while (pila.length) {
    for (const h of (hijosDe[pila.pop()] || [])) {
      if (!ids.has(h)) { ids.add(h); pila.push(h) }
    }
  }
  return ids
})

// Candidatos a cargos de esta unidad: socios de la unidad y de sus descendientes.
const candidatosJunta = computed(() =>
  candidatos.value
    .filter(s => idsSubarbol.value.has(s.agrupacionId))
    .sort((a, b) => `${a.apellido1} ${a.nombre}`.localeCompare(`${b.apellido1} ${b.nombre}`, 'es'))
)
const nombreUnidad = (id) => todasUnidades.value.find(u => u.id === id)?.nombre || ''

const tituloVista = computed(() =>
  esNuevo.value ? 'Nueva unidad organizativa' : (agrupacion.value?.nombre || 'Agrupación'))
const subtituloVista = computed(() =>
  esNuevo.value ? (padreUnidad.value ? `Dependiente de ${padreUnidad.value.nombre}` : 'Unidad raíz')
                : (agrupacion.value?.tipoUnidad?.nombre || ''))

const padreUnidad = computed(() => todasUnidades.value.find(u => u.id === padreIdParam.value) || null)
const tiposDisponibles = computed(() => {
  const terr = niveles.value.filter(t => t.naturaleza === 'TERRITORIAL')
  if (!padreIdParam.value) return terr.filter(t => !t.padreTipoId)
  const padreTipoId = padreUnidad.value?.tipoId
  if (!padreTipoId) return terr
  return terr.filter(t => t.padreTipoId === padreTipoId)
})
watch(tiposDisponibles, (lista) => {
  if (lista.length === 1) formTipoId.value = lista[0].id
  else if (!lista.find(t => t.id === formTipoId.value)) formTipoId.value = ''
})
// En el alta, mostrar jurídicos solo si el nivel elegido es FILIAL / FEDERADA
const tipoSelEsJuridica = computed(() =>
  ['FILIAL', 'FEDERADA'].includes(niveles.value.find(t => t.id === formTipoId.value)?.vinculo))

async function iniciarAlta() {
  loading.value = true
  error.value = null
  try {
    const [rNiv, rUni, rPaises, rProvs] = await Promise.allSettled([
      executeQuery(Q_NIVELES),
      executeQuery(Q_TODAS_UNIDADES),
      executeQuery(Q_PAISES),
      executeQuery(Q_PROVINCIAS),
    ])
    if (rNiv.status === 'fulfilled')   niveles.value = rNiv.value.nivelesOrganizativos ?? []
    if (rUni.status === 'fulfilled')   todasUnidades.value = rUni.value.unidadesOrganizativas ?? []
    if (rPaises.status === 'fulfilled') paises.value = (rPaises.value.paises ?? []).sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
    if (rProvs.status === 'fulfilled') provincias.value = (rProvs.value.provincias ?? []).sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error preparando el alta'
  } finally {
    loading.value = false
  }
}

async function guardarNuevo() {
  if (!form.nombre.trim() || !form.paisId || !formTipoId.value) return
  creando.value = true
  datosError.value = null
  try {
    const r = await executeMutation(
      `mutation CrearUnidad($data: UnidadOrganizativaCreateInput!) {
         crearUnidadOrganizativa(data: $data) { id }
       }`,
      { data: {
        nombre: form.nombre.trim(),
        nombreCorto: form.nombreCorto.trim() || null,
        descripcion: form.descripcion.trim() || null,
        tipoId: formTipoId.value || null,
        agrupacionPadreId: padreIdParam.value || null,
        paisId: form.paisId || null,
        provinciaId: form.provinciaId || null,
        municipioId: form.municipioId || null,
        email: form.email.trim() || null,
        telefono: form.telefono.trim() || null,
        web: form.web.trim() || null,
        nif: form.nif.trim() || null,
        fechaConstitucion: form.fechaConstitucion || null,
        registroOficial: form.registroOficial.trim() || null,
      } }
    )
    const nuevoId = r.crearUnidadOrganizativa?.id
    if (nuevoId) router.push(`/agrupaciones/${nuevoId}`)
  } catch (e) {
    datosError.value = e?.response?.errors?.[0]?.message || 'No se pudo crear la unidad.'
  } finally {
    creando.value = false
  }
}

// Navega a la ficha del socio (vista). Patrón "ojo" reutilizable en datagrids.
function verFicha(socioId) { router.push(`/miembros/${socioId}`) }

// Cargos electos (activos) que ostenta un socio en esta unidad → badges.
function cargosDe(socioId) {
  return nombramientos.value
    .filter(n => n.miembro?.id === socioId && n.estado === 'ACTIVO')
    .map(n => n.rol?.nombre)
    .filter(Boolean)
}

// ── Traslado de socio a otra unidad (acción de edición) ─────────────────────
// Autorización por ámbito (coordinador/presidente de la unidad) → Fase 2 en backend
// (ambito_territorial.py). De momento gateado por permiso + selector de destino.
const unidadesDestinoFiltradas = computed(() =>
  unidadesDestino.value.filter(u => u.id !== agrupacionId.value)
)
function etiquetaUnidad(u) {
  const niv = u.tipoUnidad?.denominacionSingular || u.tipoUnidad?.nombre
  return niv ? `${u.nombre} · ${niv}` : u.nombre
}
async function abrirTraslado(socio) {
  Object.assign(trasladoModal, { visible: true, socio, destinoId: '', error: null, guardando: false })
  if (!unidadesDestino.value.length) {
    try {
      const r = await executeQuery(Q_TODAS_UNIDADES)
      unidadesDestino.value = (r.unidadesOrganizativas || []).sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
    } catch { /* el selector quedará vacío */ }
  }
}
async function confirmarTraslado() {
  if (!trasladoModal.destinoId) return
  trasladoModal.guardando = true
  trasladoModal.error = null
  try {
    await executeMutation(
      `mutation TrasladarSocio($data: ContactoUpdateInput!) { actualizarContacto(data: $data) { id } }`,
      { data: { id: trasladoModal.socio.id, agrupacionId: trasladoModal.destinoId } }
    )
    trasladoModal.visible = false
    await cargar()
  } catch (e) {
    trasladoModal.error = e?.response?.errors?.[0]?.message || 'No se pudo trasladar.'
  } finally {
    trasladoModal.guardando = false
  }
}

// ── Estilos ─────────────────────────────────────────────────────────────────
const cardCls = 'rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden'
const titleCls = 'text-sm font-semibold text-slate-800'
const lbl = 'block text-sm font-medium text-slate-700 mb-1.5'
const inp = 'h-10 w-full px-3 py-2 text-sm border border-slate-300 rounded-lg transition-all ' +
            'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ' +
            'bg-white placeholder:text-slate-300'
const inpTa = 'w-full px-3 py-2 text-sm border border-slate-300 rounded-lg transition-all ' +
              'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ' +
              'bg-white placeholder:text-slate-300'
// Campo en solo lectura con aspecto de campo (detalle = edición en readonly)
const ro = 'min-h-[2.5rem] px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg text-slate-700 break-words'

const accordionBtn = (isOpen) =>
  'w-full flex items-center justify-between px-5 py-3.5 hover:bg-slate-50/60 transition-colors ' +
  (isOpen ? 'border-b border-slate-200' : '')
const chevronCls = (isOpen) =>
  'w-4 h-4 text-slate-400 transition-transform duration-200 ' + (isOpen ? 'rotate-180' : '')

// ── Acordeones ───────────────────────────────────────────────────────────────
const open = reactive({ info: true, config: false, junta: false, cargos: true })

function togglePanel(key) {
  const wasOpen = open[key]
  Object.keys(open).forEach(k => { open[k] = false })
  if (!wasOpen) open[key] = true
}

// ── Estado ───────────────────────────────────────────────────────────────────
const loading             = ref(false)
const error               = ref(null)
const agrupacion          = ref(null)
const nombramientos       = ref([])   // registros directos de esta unidad
const nombramientosHijos  = ref([])   // registros de unidades hijas
const rolesTerritoriales  = ref([])   // roles organizacionales territoriales
const miembros            = ref([])   // miembros para el buscador
const unidadesDestino     = ref([])   // todas las unidades activas (selector de traslado)
const trasladoModal       = reactive({ visible: false, socio: null, destinoId: '', guardando: false, error: null })

// ── Edición de datos generales / contacto / ubicación ───────────────────────
const paises         = ref([])
const provincias     = ref([])
const municipios     = ref([])
const guardandoDatos = ref(false)
const datosError     = ref(null)
const form = reactive({
  nombre: '', nombreCorto: '', descripcion: '',
  email: '', telefono: '', web: '',
  paisId: '', provinciaId: '', municipioId: '',
  nif: '', fechaConstitucion: '', registroOficial: '',
})

const provinciasDelPais = computed(() =>
  !form.paisId ? [] : provincias.value.filter(p => p.paisId === form.paisId)
)
// Nombres para la vista en solo lectura (resueltos desde los catálogos cargados)
const paisNombre      = computed(() => paises.value.find(p => p.id === agrupacion.value?.paisId)?.nombre || '—')
const provinciaNombre = computed(() => provincias.value.find(p => p.id === agrupacion.value?.provinciaId)?.nombre || '—')
const municipioNombre = computed(() => municipios.value.find(m => m.id === agrupacion.value?.municipioId)?.nombre || '—')
// ¿El nivel de esta unidad delega la subestructura en cada unidad? (distribuida)
const esDistribuida = computed(() => !!agrupacion.value?.tipoUnidad?.estructuraDistribuida)
// Datos jurídicos solo para entidades con personalidad propia (FILIAL / FEDERADA)
const esEntidadJuridica = computed(() => ['FILIAL', 'FEDERADA'].includes(agrupacion.value?.tipoUnidad?.vinculo))
// Composición del órgano de gobierno: cargos electos activos de esta unidad
const composicionJunta = computed(() =>
  [...nombramientos.value].sort((a, b) =>
    (a.rol?.nivel ?? 99) - (b.rol?.nivel ?? 99) ||
    (a.rol?.nombre || '').localeCompare(b.rol?.nombre || '', 'es'))
)

function sincronizarForm() {
  const a = agrupacion.value
  if (!a) return
  Object.assign(form, {
    nombre: a.nombre ?? '', nombreCorto: a.nombreCorto ?? '', descripcion: a.descripcion ?? '',
    email: a.email ?? '', telefono: a.telefono ?? '', web: a.web ?? '',
    paisId: a.paisId ?? '', provinciaId: a.provinciaId ?? '', municipioId: a.municipioId ?? '',
    nif: a.nif ?? '', fechaConstitucion: a.fechaConstitucion ?? '', registroOficial: a.registroOficial ?? '',
  })
  if (form.provinciaId) cargarMunicipios(form.provinciaId)
}

async function cargarMunicipios(provinciaId) {
  if (!provinciaId) { municipios.value = []; return }
  try {
    const r = await executeQuery(Q_MUNICIPIOS, { provinciaId })
    municipios.value = (r.municipios ?? []).sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
  } catch { municipios.value = [] }
}
function onPaisChange()      { form.provinciaId = ''; form.municipioId = ''; municipios.value = [] }
function onProvinciaChange() { form.municipioId = ''; cargarMunicipios(form.provinciaId) }

function toggleEdicion() {
  editMode.value = !editMode.value
  datosError.value = null
  if (editMode.value) sincronizarForm()
}

async function guardarDatos() {
  if (!form.nombre.trim()) return
  guardandoDatos.value = true
  datosError.value = null
  try {
    await executeMutation(
      `mutation ActualizarUnidad($data: UnidadOrganizativaUpdateInput!) {
         actualizarUnidadOrganizativa(data: $data) { id }
       }`,
      { data: {
        id: agrupacionId.value,
        nombre: form.nombre.trim(),
        nombreCorto: form.nombreCorto.trim() || null,
        descripcion: form.descripcion.trim() || null,
        email: form.email.trim() || null,
        telefono: form.telefono.trim() || null,
        web: form.web.trim() || null,
        paisId: form.paisId || null,
        provinciaId: form.provinciaId || null,
        municipioId: form.municipioId || null,
        nif: form.nif.trim() || null,
        fechaConstitucion: form.fechaConstitucion || null,
        registroOficial: form.registroOficial.trim() || null,
      } }
    )
    await cargar()
  } catch (e) {
    datosError.value = e?.response?.errors?.[0]?.message || 'No se pudieron guardar los datos.'
  } finally {
    guardandoDatos.value = false
  }
}

// ── Computed ─────────────────────────────────────────────────────────────────
// Todos los registros activos: directos primero, luego hijos (marcados)
const todosRegistros = computed(() => [
  ...nombramientos.value,
  ...nombramientosHijos.value.map(r => ({ ...r, _esHijo: true })),
])

// Rol más probable para el selector: el que corresponde al nivel en la jerarquía
const rolSugerido = computed(() => {
  const nivel = agrupacion.value?.tipoUnidad?.nivel
  if (nivel === 1) return rolesTerritoriales.value.find(r => r.codigo === 'COORDINADOR')
  if (nivel === 2) return rolesTerritoriales.value.find(r => r.codigo === 'COORD_PROV')
  if (nivel === 3) return rolesTerritoriales.value.find(r => r.codigo === 'COORD_LOCAL')
  return rolesTerritoriales.value[0] ?? null
})

// ── Helpers ──────────────────────────────────────────────────────────────────
const fmtFecha = (d) => d ? new Date(d + 'T00:00:00').toLocaleDateString('es-ES') : '—'
const estadoBadge = (e) => ({
  ACTIVO:      'bg-green-100 text-green-800',
  PENDIENTE:   'bg-yellow-100 text-yellow-800',
  EN_REVISION: 'bg-blue-100 text-blue-800',
  FINALIZADO:  'bg-slate-100 text-slate-600',
  RECHAZADO:   'bg-red-100 text-red-700',
}[e] ?? 'bg-slate-100 text-slate-600')

// ── Queries ───────────────────────────────────────────────────────────────────
const Q_AGRUPACION = `
  query Agrupacion($id: UUID!) {
    unidadesOrganizativas(filter: { id: { eq: $id } }) {
      id nombre nombreCorto descripcion email telefono web activo
      tipoId agrupacionPadreId
      paisId provinciaId municipioId
      nif fechaConstitucion registroOficial
      tipoUnidad { id nombre naturaleza nivel vinculo estructuraDistribuida }
    }
  }
`
const Q_PAISES     = `query { paises(filter: { activo: { eq: true } }) { id nombre } }`
const Q_PROVINCIAS = `query { provincias(filter: { activo: { eq: true } }) { id nombre paisId activo } }`
const Q_MUNICIPIOS = `query Municipios($provinciaId: UUID!) { municipios(filter: { provinciaId: { eq: $provinciaId } }) { id nombre } }`
const Q_ROLES_TERRITORIALES = `
  query RolesTerritoriales {
    roles(filter: { tipo: { eq: "ORGANIZACION" }, eliminado: { eq: false } }) {
      id codigo nombre nivel esTerritorial nivelTerritorial
    }
  }
`
const Q_NOMBRAMIENTOS = `
  query Nombramientos($agrupacionId: UUID!) {
    historialNombramientos(filter: { agrupacionId: { eq: $agrupacionId }, estado: { eq: "ACTIVO" } }) {
      id rolId estado fechaInicio fechaFin observaciones
      miembro { id nombre apellido1 apellido2 }
      rol { id codigo nombre nivel }
      agrupacion { id nombre }
    }
  }
`
const Q_HIJOS = `
  query AgrupacionesHijas($padreId: UUID!) {
    unidadesOrganizativas(filter: { agrupacionPadreId: { eq: $padreId }, activo: { eq: true } }) {
      id nombre
    }
  }
`
const Q_MIEMBROS = `
  query MiembrosAgrupacion($agrupacionId: UUID!) {
    miembros: socios(agrupacionId: $agrupacionId, activo: true) {
      id nombre apellido1 apellido2 email
    }
  }
`
const Q_TODAS_UNIDADES = `
  query TodasUnidades {
    unidadesOrganizativas(filter: { activo: { eq: true } }) {
      id nombre tipoId agrupacionPadreId
      tipoUnidad { id nombre nivel denominacionSingular }
    }
  }
`
// Todos los socios activos (para el pool recursivo de candidatos a cargos)
const Q_TODOS_SOCIOS = `
  query TodosSocios {
    socios(activo: true) {
      id nombre apellido1 apellido2 email agrupacionId
    }
  }
`
const Q_NIVELES = `
  query Niveles {
    nivelesOrganizativos(filter: { activo: { eq: true } }) {
      id nombre naturaleza padreTipoId vinculo
    }
  }
`

// ── Carga ────────────────────────────────────────────────────────────────────
onMounted(() => {
  if (esNuevo.value) iniciarAlta()
  else {
    cargar()
    if (route.query.edit) editMode.value = true   // llegada desde "Editar" del árbol
  }
})

async function cargar() {
  loading.value = true
  error.value = null
  try {
    const [rAgr, rRoles, rNombr, rHijos, rMbs, rPaises, rProvs, rUni, rCand] = await Promise.allSettled([
      executeQuery(Q_AGRUPACION, { id: agrupacionId.value }),
      executeQuery(Q_ROLES_TERRITORIALES),
      executeQuery(Q_NOMBRAMIENTOS, { agrupacionId: agrupacionId.value }),
      executeQuery(Q_HIJOS, { padreId: agrupacionId.value }),
      executeQuery(Q_MIEMBROS, { agrupacionId: agrupacionId.value }),
      paises.value.length ? Promise.resolve(null) : executeQuery(Q_PAISES),
      provincias.value.length ? Promise.resolve(null) : executeQuery(Q_PROVINCIAS),
      executeQuery(Q_TODAS_UNIDADES),
      executeQuery(Q_TODOS_SOCIOS),
    ])
    if (rUni.status === 'fulfilled')
      todasUnidades.value = rUni.value.unidadesOrganizativas ?? []
    if (rCand.status === 'fulfilled')
      candidatos.value = rCand.value.socios ?? []
    if (rPaises.status === 'fulfilled' && rPaises.value)
      paises.value = (rPaises.value.paises ?? []).sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
    if (rProvs.status === 'fulfilled' && rProvs.value)
      provincias.value = (rProvs.value.provincias ?? []).sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
    if (rAgr.status === 'fulfilled') {
      agrupacion.value = rAgr.value.unidadesOrganizativas?.[0] ?? null
      sincronizarForm()
    }
    if (rRoles.status === 'fulfilled')
      rolesTerritoriales.value = (rRoles.value.roles ?? [])
        .filter(r => r.esTerritorial)
        .sort((a, b) => (a.nivel ?? 99) - (b.nivel ?? 99))
    if (rNombr.status === 'fulfilled')
      nombramientos.value = rNombr.value.historialNombramientos ?? []
    if (rMbs.status === 'fulfilled')
      miembros.value = (rMbs.value.miembros ?? [])
        .sort((a, b) => `${a.nombre} ${a.apellido1}`.localeCompare(`${b.nombre} ${b.apellido1}`, 'es'))

    // Cargar registros de unidades hijas
    if (rHijos.status === 'fulfilled') {
      const hijos = rHijos.value.unidadesOrganizativas ?? []
      if (hijos.length) {
        await cargarNombramientosHijos(hijos.map(h => h.id))
      }
    }
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message || 'Error cargando la agrupación'
  } finally {
    loading.value = false
  }
}

async function cargarNombramientosHijos(ids) {
  // Carga secuencial por cada hijo (strawchemy puede no soportar filtro `in` para UUID)
  const resultados = await Promise.allSettled(
    ids.map(id => executeQuery(Q_NOMBRAMIENTOS, { agrupacionId: id }))
  )
  nombramientosHijos.value = resultados
    .filter(r => r.status === 'fulfilled')
    .flatMap(r => r.value.historialNombramientos ?? [])
}

async function recargarNombramientos() {
  const [rNombr, rHijos] = await Promise.allSettled([
    executeQuery(Q_NOMBRAMIENTOS, { agrupacionId: agrupacionId.value }),
    executeQuery(Q_HIJOS, { padreId: agrupacionId.value }),
  ])
  if (rNombr.status === 'fulfilled')
    nombramientos.value = rNombr.value.historialNombramientos ?? []
  if (rHijos.status === 'fulfilled') {
    const hijos = rHijos.value.unidadesOrganizativas ?? []
    if (hijos.length) await cargarNombramientosHijos(hijos.map(h => h.id))
    else nombramientosHijos.value = []
  }
}

// ── Modal registro ────────────────────────────────────────────────────────────
const modal = reactive({
  visible: false, editandoId: null, guardando: false, error: null,
  rolId: '', rolNombre: '',
  miembroId: null, miembroSearch: '', showList: false,
  fechaInicio: '', fechaFin: '', observaciones: '',
})

const miembrosFiltrados = computed(() => {
  const q = modal.miembroSearch.trim().toLowerCase()
  if (q.length < 2) return []
  return miembros.value
    .filter(m => `${m.nombre} ${m.apellido1}`.toLowerCase().includes(q))
    .slice(0, 10)
})

function abrirRegistro(registro = null) {
  const hoy = new Date().toISOString().split('T')[0]
  Object.assign(modal, {
    visible: true, error: null, guardando: false, showList: false,
    rolId: registro?.rolId ?? (rolSugerido.value?.id ?? ''),
    rolNombre: registro?.rol?.nombre ?? '',
    editandoId: registro?.id ?? null,
    miembroId: registro?.miembro?.id ?? null,
    miembroSearch: registro?.miembro
      ? `${registro.miembro.nombre} ${registro.miembro.apellido1}`
      : '',
    fechaInicio: registro?.fechaInicio ?? hoy,
    fechaFin: registro?.fechaFin ?? '',
    observaciones: registro?.observaciones ?? '',
  })
}

function ocultarLista() {
  setTimeout(() => { modal.showList = false }, 150)
}

function seleccionarMiembro(m) {
  modal.miembroId = m.id
  modal.miembroSearch = `${m.nombre} ${m.apellido1}`
  modal.showList = false
}

async function guardarRegistro() {
  modal.guardando = true
  modal.error = null
  try {
    if (modal.editandoId) {
      // El update input de strawchemy excluye las FK: en edición solo cambian escalares.
      await executeMutation(
        `mutation ActualizarRegistro($data: HistorialNombramientoUpdateInput!) {
           actualizarHistorialNombramiento(data: $data) { id }
         }`,
        { data: {
            id: modal.editandoId,
            fechaInicio: modal.fechaInicio,
            fechaFin: modal.fechaFin || null,
            observaciones: modal.observaciones || null,
        } }
      )
    } else {
      // Alta: mutación custom con FKs planas (el create input autogenerado no las acepta).
      await executeMutation(
        `mutation CrearNombramiento($miembroId: UUID!, $rolId: UUID!, $agrupacionId: UUID!, $fechaInicio: Date!, $fechaFin: Date, $observaciones: String) {
           crearNombramiento(miembroId: $miembroId, rolId: $rolId, agrupacionId: $agrupacionId, fechaInicio: $fechaInicio, fechaFin: $fechaFin, observaciones: $observaciones) { id }
         }`,
        {
          miembroId: modal.miembroId,
          rolId: modal.rolId,
          agrupacionId: agrupacionId.value,
          fechaInicio: modal.fechaInicio,
          fechaFin: modal.fechaFin || null,
          observaciones: modal.observaciones || null,
        }
      )
    }
    modal.visible = false
    await recargarNombramientos()
  } catch (e) {
    modal.error = e?.response?.errors?.[0]?.message || 'Error al guardar el registro'
  } finally {
    modal.guardando = false
  }
}

async function cesarRegistro(reg) {
  if (!(await confirmDialog({ titulo: '¿Confirmar acción?', mensaje: `¿Dar de baja a ${reg.miembro?.nombre} ${reg.miembro?.apellido1} en el cargo?`, variante: 'aviso' }))) return
  await executeMutation(
    `mutation CesarRegistro($data: HistorialNombramientoUpdateInput!) {
       actualizarHistorialNombramiento(data: $data) { id }
     }`,
    { data: { id: reg.id, estado: 'FINALIZADO', fechaFin: new Date().toISOString().split('T')[0] } }
  )
  await recargarNombramientos()
}
</script>
