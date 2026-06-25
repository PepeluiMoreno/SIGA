<template>
  <!-- Modal: sugerencia de agrupación -->
  <div v-if="mostrarModalAgrupacion"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
    @click.self="mostrarModalAgrupacion = false">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-md">
      <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-base font-semibold text-gray-900">Agrupación territorial</h3>
        <button @click="mostrarModalAgrupacion = false" class="text-gray-400 hover:text-gray-600 text-xl leading-none">&times;</button>
      </div>
      <div class="px-6 py-4 space-y-3">
        <p class="text-sm text-gray-600">
          Hemos detectado la provincia de residencia. ¿Deseas asignar este {{ orgConfig.miembro }} a una agrupación territorial de su zona?
        </p>
        <select v-model="miembro.agrupacionId"
          class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500">
          <option value="">Sin asignar</option>
          <option v-for="a in agrupacionesSugeridas" :key="a.id" :value="a.id">{{ a.nombre }}</option>
        </select>
      </div>
      <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
        <button @click="mostrarModalAgrupacion = false"
          class="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50">
          Decidir más tarde
        </button>
        <button @click="mostrarModalAgrupacion = false"
          class="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700">
          Aceptar
        </button>
      </div>
    </div>
  </div>

  <!-- Layout wrapper: AppLayout para vista independiente, div para modoPropio -->
  <component :is="layoutComponent" v-bind="layoutBindings">

    <!-- Botón Editar en cabecera de página (AppLayout #actions) -->
    <template v-if="!modoPropio" #actions>
      <button v-if="!isCreateMode && miembro.id" @click="toggleEditMode"
        :class="editMode ? 'text-slate-500 hover:text-slate-700' : 'text-indigo-600 hover:text-indigo-800'"
        class="h-8 px-3 text-sm font-medium border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors">
        {{ editMode ? 'Cancelar edición' : 'Editar' }}
      </button>
    </template>

    <!-- Barra de guardado en footer de AppLayout -->
    <template v-if="!modoPropio && (editMode || isCreateMode)" #footer>
      <button @click="handleCancel"
        class="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50">
        {{ isCreateMode ? 'Cancelar' : 'Cancelar cambios' }}
      </button>
      <button @click="handleSave" :disabled="loading || !formValido"
        class="px-5 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50">
        {{ isCreateMode ? 'Crear miembro' : 'Guardar cambios' }}
      </button>
    </template>

    <!-- Cargando -->
    <div v-if="loading" class="py-20 text-center">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-600 border-t-transparent mb-3"></div>
      <p class="text-slate-500 text-sm">{{ isCreateMode ? 'Preparando formulario...' : `Cargando datos del ${orgConfig.miembro}...` }}</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="py-8 text-center">
      <p class="text-red-600 font-medium">{{ error }}</p>
    </div>

    <!-- Contenido -->
    <div v-else>

      <!-- Banner de guardado correcto -->
      <div v-if="saveMessage"
        class="mb-4 rounded-lg bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-800 flex items-center gap-2">
        <CheckIcon class="w-4 h-4 shrink-0" />
        {{ saveMessage }}
      </div>

      <!-- Barra de edición en modoPropio (/mis-datos): AppLayout no aporta slots aquí -->
      <div v-if="modoPropio && !isCreateMode" class="mb-4 flex justify-end gap-2">
        <button @click="handleCancel"
          class="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50">
          Descartar cambios
        </button>
        <button @click="handleSave" :disabled="loading || !formValido"
          class="px-5 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50">
          Guardar cambios
        </button>
      </div>

      <AccordionGroup class="space-y-3">

        <!-- ── 1. DATOS PERSONALES ── -->
        <AccordionPanel :defaultOpen="true">
          <template #title>
            <span class="w-2 h-2 rounded-full bg-indigo-500 shrink-0"></span>
            <h2 class="text-sm font-semibold text-slate-800">Datos personales</h2>
          </template>
          <div class="p-5">
            <AccordionGroup class="space-y-3">

            <AccordionPanel :defaultOpen="true">
              <template #title>
                <span class="w-2 h-2 rounded-full bg-purple-500 shrink-0"></span>
                <h3 class="text-sm font-semibold text-slate-800">Identificación</h3>
              </template>
              <div class="p-5 space-y-4">

                <div class="flex items-center gap-4 mb-2">
                  <AvatarImg
                    :src="miembro.fotoUrl"
                    :nombre="miembro.nombre"
                    :apellido="miembro.apellido1"
                    size="2xl"
                    shape="carnet"
                  />
                  <div v-if="puedeEditarFoto" class="flex flex-col gap-1">
                    <label class="inline-flex items-center gap-1.5 h-8 px-3 text-xs font-medium text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-lg cursor-pointer hover:bg-indigo-100 transition-colors">
                      <ArrowUpTrayIcon class="w-3.5 h-3.5" />
                      Cambiar foto
                      <input type="file" accept="image/*" class="hidden" @change="subirFoto" />
                    </label>
                    <p class="text-xs text-slate-400">JPG, PNG, WebP · máx. 5 MB</p>
                  </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  <FieldText v-model="miembro.nombre" label="Nombre *" :edit-mode="editMode || isCreateMode" />
                  <FieldText v-model="miembro.apellido1" label="Primer apellido *" :edit-mode="editMode || isCreateMode" />
                  <FieldText v-model="miembro.apellido2" label="Segundo apellido" :edit-mode="editMode || isCreateMode" />
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  <FieldSelect v-model="miembro.sexo" label="Sexo" :edit-mode="editMode || isCreateMode" :options="sexoOptions" />
                  <FieldText v-model="miembro.fechaNacimiento" label="Fecha de nacimiento" type="date" :edit-mode="editMode || isCreateMode" />
                  <FieldSelect v-model="miembro.paisNacimientoId" label="País de nacimiento" :edit-mode="editMode || isCreateMode"
                    :options="catalogos.paises" option-label="nombre" option-value="id" empty-label="Sin especificar" />
                </div>
                <div class="grid grid-cols-12 gap-4">
                  <div class="col-span-3">
                    <FieldSelect v-model="miembro.tipoDocumento" label="Tipo doc." :edit-mode="editMode || isCreateMode" :options="tipoDocumentoOptions" />
                  </div>
                  <div class="col-span-4">
                    <FieldText v-model="miembro.numeroDocumento" label="Número" :edit-mode="editMode || isCreateMode" />
                  </div>
                  <div class="col-span-5">
                    <FieldSelect v-model="miembro.paisDocumentoId" label="País expedición" :edit-mode="editMode || isCreateMode"
                      :options="catalogos.paises" option-label="nombre" option-value="id" empty-label="Sin especificar" />
                  </div>
                </div>
              </div>
            </AccordionPanel>

            <AccordionPanel :defaultOpen="true">
              <template #title>
                <span class="w-2 h-2 rounded-full bg-sky-500 shrink-0"></span>
                <h3 class="text-sm font-semibold text-slate-800">Contacto</h3>
              </template>
              <div class="p-5 space-y-4">
                <div class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  <FieldText v-model="miembro.email" label="Email" type="email" :edit-mode="editMode || isCreateMode" />
                  <FieldText v-model="miembro.telefono" label="Teléfono" :edit-mode="editMode || isCreateMode" />
                  <FieldText v-model="miembro.telefono2" label="Tel. alternativo" :edit-mode="editMode || isCreateMode" />
                </div>
                <FieldText v-model="miembro.direccion" label="Dirección" :edit-mode="editMode || isCreateMode" />
                <div class="grid grid-cols-12 gap-4">
                  <div class="col-span-2">
                    <FieldSelect v-model="miembro.paisDomicilioId" label="País" :edit-mode="editMode || isCreateMode"
                      :options="catalogos.paises" option-label="nombre" option-value="id" empty-label="—" />
                  </div>
                  <div class="col-span-4">
                    <FieldSelect v-model="miembro.provinciaId" label="Provincia" :edit-mode="editMode || isCreateMode"
                      :options="catalogos.provincias" option-label="nombre" option-value="id" empty-label="Sin especificar" />
                  </div>
                  <div class="col-span-4">
                    <FieldText v-model="miembro.localidad" label="Localidad" :edit-mode="editMode || isCreateMode" />
                  </div>
                  <div class="col-span-2">
                    <FieldText v-model="miembro.codigoPostal" label="CP" :edit-mode="editMode || isCreateMode" />
                  </div>
                </div>
              </div>
            </AccordionPanel>

            <AccordionPanel :defaultOpen="false">
              <template #title>
                <span class="w-2 h-2 rounded-full bg-slate-400 shrink-0"></span>
                <h3 class="text-sm font-semibold text-slate-800">Observaciones</h3>
              </template>
              <div class="p-5">
                <FieldTextarea v-model="miembro.observaciones" label="Observaciones" :edit-mode="editMode || isCreateMode" rows="4" />
              </div>
            </AccordionPanel>

            <AccordionPanel :defaultOpen="false">
              <template #title>
                <span class="w-2 h-2 rounded-full bg-rose-500 shrink-0"></span>
                <h3 class="text-sm font-semibold text-slate-800">RGPD y privacidad</h3>
              </template>
              <div class="p-5 space-y-4">

                <!-- Solicitud de supresión: la ejerce el propio socio (derecho RGPD).
                     El flujo formal de tramitación queda para el módulo transversal. -->
                <div class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 gap-4">
                  <FieldCheckbox v-model="miembro.solicitaSupresionDatos" label="Solicita supresión de datos" :edit-mode="editMode || isCreateMode" />
                  <FieldText v-model="miembro.fechaSolicitudSupresion" label="Fecha de la solicitud" type="date"
                    :edit-mode="(editMode || isCreateMode) && miembro.solicitaSupresionDatos" />
                </div>

                <!-- Límite de conservación: calculado a partir de la baja, solo lectura -->
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Límite de conservación de datos</label>
                  <p class="text-sm text-gray-800">
                    <template v-if="fechaLimiteRetencion">
                      {{ formatDate(fechaLimiteRetencion) }}
                      <span class="text-gray-400 text-xs">· {{ ANIOS_RETENCION }} años desde la baja</span>
                    </template>
                    <span v-else class="text-gray-400 italic">Mientras conste como {{ orgConfig.miembro }}</span>
                  </p>
                </div>

                <!-- Anonimización: acción real e irreversible, no un campo editable -->
                <div class="border-t border-gray-100 pt-3">
                  <label class="block text-xs font-medium text-gray-600 mb-1">Anonimización</label>
                  <div v-if="miembro.datosAnonimizados" class="flex items-center gap-2">
                    <span class="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded-full font-medium">Datos anonimizados</span>
                    <span class="text-gray-400 text-xs">{{ fechaCorta(miembro.fechaAnonimizacion) }}</span>
                  </div>
                  <template v-else>
                    <button v-if="puedeAnonimizar" type="button" @click="modalAnonimizar = true"
                      class="inline-flex items-center gap-1.5 h-8 px-3 text-xs font-medium text-red-700 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-colors">
                      Anonimizar datos
                    </button>
                    <p v-else class="text-xs text-gray-400 italic">
                      La anonimización estará disponible cuando el {{ orgConfig.miembro }} cause baja.
                    </p>
                  </template>
                </div>
              </div>
            </AccordionPanel>

            </AccordionGroup>
          </div>
        </AccordionPanel>

        <!-- ── 2. DATOS ECONÓMICOS ── (cuotas si el tipo paga; justificantes siempre) -->
        <AccordionPanel v-if="modoPropio || tienePermiso('CUOT_LIST') || tienePermiso('JUST_LIST')" :defaultOpen="false">
          <template #title>
            <span class="w-2 h-2 rounded-full bg-emerald-500 shrink-0"></span>
            <h2 class="text-sm font-semibold text-slate-800">Datos económicos</h2>
          </template>
          <div class="p-5">
            <AccordionGroup class="space-y-3">

            <!-- Sub-acordeón: Procedimiento de pago -->
            <AccordionPanel v-if="requiereCuota" :defaultOpen="true">
              <template #title>
                <span class="w-2 h-2 rounded-full bg-purple-500 shrink-0"></span>
                <h3 class="text-sm font-semibold text-slate-800">Procedimiento de pago de cuotas</h3>
              </template>
              <div class="p-5">

            <div class="flex gap-5 items-start">
              <!-- Selector de forma de pago -->
              <section class="space-y-3 rounded-xl border border-gray-200 p-5 flex-shrink-0 w-80">
                <div v-if="editMode || isCreateMode" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-1.5">
                  <button
                    v-for="fp in catalogos.formasPago"
                    :key="fp.id"
                    type="button"
                    @click="miembro.formaPagoId = miembro.formaPagoId === fp.id ? null : fp.id"
                    :class="[
                      'relative flex flex-col items-center gap-1 rounded-lg border-2 px-1 py-2 text-center text-[11px] leading-tight font-medium transition-all duration-150',
                      miembro.formaPagoId === fp.id
                        ? 'border-purple-500 bg-purple-50 text-purple-700 shadow-sm'
                        : 'border-gray-100 bg-gray-50 text-gray-500 hover:border-purple-200 hover:bg-purple-50 hover:text-purple-600'
                    ]"
                  >
                    <span class="leading-none" v-html="formaPagoIcono(fp.nombre)"></span>
                    <span class="leading-tight">{{ fp.nombre }}</span>
                    <span v-if="miembro.formaPagoId === fp.id"
                      class="absolute -top-1.5 -right-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-purple-500 text-white text-[9px]">✓</span>
                  </button>
                </div>
                <div v-else-if="miembro.formaPagoId" class="flex items-center gap-2 text-sm text-gray-900">
                  <span class="text-lg" v-html="formaPagoIcono(formaPagoSeleccionada?.nombre)"></span>
                  {{ formaPagoSeleccionada?.nombre }}
                </div>
                <div v-else class="text-sm text-gray-400 italic">Sin especificar</div>
              </section>

              <!-- Panel contextual según forma de pago -->
              <Transition
                enter-active-class="transition-all duration-200 ease-out"
                enter-from-class="opacity-0 translate-x-2"
                enter-to-class="opacity-100 translate-x-0"
                leave-active-class="transition-all duration-150 ease-in"
                leave-from-class="opacity-100 translate-x-0"
                leave-to-class="opacity-0 translate-x-2"
                mode="out-in"
              >
                <section v-if="esTransferencia && !esInternacional" key="transf" class="flex-1 space-y-4 rounded-xl border border-purple-100 bg-purple-50/40 p-5">
                  <h3 class="text-xs font-semibold uppercase tracking-widest text-purple-600">Datos bancarios</h3>
                  <div class="space-y-1">
                    <label class="block text-xs font-medium text-gray-600">IBAN</label>
                    <template v-if="editMode || isCreateMode">
                      <input
                        :value="ibanDisplay"
                        @input="onIbanInput"
                        @blur="ibanTouched = true"
                        type="text" maxlength="40"
                        placeholder="ES91 2100 0418 4502 0005 1332"
                        autocomplete="off"
                        :class="[
                          'w-full max-w-md border rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2',
                          ibanTouched && miembro.iban && ibanValidar(miembro.iban) === false
                            ? 'border-red-400 focus:ring-red-300 bg-white'
                            : ibanTouched && miembro.iban && ibanValidar(miembro.iban) === true
                              ? 'border-green-400 focus:ring-green-300 bg-white'
                              : 'border-gray-300 focus:ring-purple-300 bg-white'
                        ]"
                      />
                      <p v-if="ibanTouched && miembro.iban && ibanValidar(miembro.iban) === false" class="text-xs text-red-600 mt-1">IBAN no válido — comprueba el número</p>
                      <p v-else-if="ibanTouched && miembro.iban && ibanValidar(miembro.iban) === true" class="text-xs text-green-600 mt-1">✓ IBAN correcto</p>
                    </template>
                    <p v-else class="text-sm font-mono text-gray-900">{{ ibanFormatear(miembro.iban) || '—' }}</p>
                  </div>
                </section>

                <section v-else-if="esInternacional" key="transf-int" class="flex-1 space-y-4 rounded-xl border border-purple-100 bg-purple-50/40 p-5">
                  <h3 class="text-xs font-semibold uppercase tracking-widest text-purple-600">Datos bancarios internacionales</h3>
                  <div class="space-y-1">
                    <label class="block text-xs font-medium text-gray-600">IBAN</label>
                    <template v-if="editMode || isCreateMode">
                      <input
                        :value="ibanDisplay"
                        @input="onIbanInput"
                        @blur="ibanTouched = true"
                        type="text" maxlength="40"
                        placeholder="ES91 2100 0418 4502 0005 1332"
                        autocomplete="off"
                        :class="[
                          'w-full max-w-md border rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2',
                          ibanTouched && miembro.iban && ibanValidar(miembro.iban) === false
                            ? 'border-red-400 focus:ring-red-300 bg-white'
                            : ibanTouched && miembro.iban && ibanValidar(miembro.iban) === true
                              ? 'border-green-400 focus:ring-green-300 bg-white'
                              : 'border-gray-300 focus:ring-purple-300 bg-white'
                        ]"
                      />
                      <p v-if="ibanTouched && miembro.iban && ibanValidar(miembro.iban) === false" class="text-xs text-red-600 mt-1">IBAN no válido — comprueba el número</p>
                      <p v-else-if="ibanTouched && miembro.iban && ibanValidar(miembro.iban) === true" class="text-xs text-green-600 mt-1">✓ IBAN correcto</p>
                    </template>
                    <p v-else class="text-sm font-mono text-gray-900">{{ ibanFormatear(miembro.iban) || '—' }}</p>
                  </div>
                  <FieldText v-model="miembro.swiftBic" label="SWIFT / BIC" :edit-mode="editMode || isCreateMode" />
                </section>

                <section v-else-if="esDomiciliacion" key="sepa" class="flex-1 space-y-4 rounded-xl border border-purple-100 bg-purple-50/40 p-5">
                  <h3 class="text-xs font-semibold uppercase tracking-widest text-purple-600">Domiciliación bancaria</h3>
                  <div class="space-y-1">
                    <label class="block text-xs font-medium text-gray-600">IBAN de la cuenta a cargar</label>
                    <template v-if="editMode || isCreateMode">
                      <input
                        :value="ibanDisplay"
                        @input="onIbanInput"
                        @blur="ibanTouched = true"
                        type="text" maxlength="40"
                        placeholder="ES91 2100 0418 4502 0005 1332"
                        autocomplete="off"
                        :class="[
                          'w-full max-w-md border rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2',
                          ibanTouched && miembro.iban && ibanValidar(miembro.iban) === false
                            ? 'border-red-400 focus:ring-red-300 bg-white'
                            : ibanTouched && miembro.iban && ibanValidar(miembro.iban) === true
                              ? 'border-green-400 focus:ring-green-300 bg-white'
                              : 'border-gray-300 focus:ring-purple-300 bg-white'
                        ]"
                      />
                      <p v-if="ibanTouched && miembro.iban && ibanValidar(miembro.iban) === false" class="text-xs text-red-600 mt-1">IBAN no válido — comprueba el número</p>
                      <p v-else-if="ibanTouched && miembro.iban && ibanValidar(miembro.iban) === true" class="text-xs text-green-600 mt-1">✓ IBAN correcto</p>
                    </template>
                    <p v-else class="text-sm font-mono text-gray-900">{{ ibanFormatear(miembro.iban) || '—' }}</p>
                  </div>
                  <p class="text-xs text-gray-400">El cargo se realizará mediante mandato SEPA en la fecha de vencimiento de cada cuota.</p>
                </section>

                <section v-else-if="esPaypal" key="paypal" class="flex-1 space-y-4 rounded-xl border border-blue-100 bg-blue-50/40 p-5">
                  <h3 class="text-xs font-semibold uppercase tracking-widest text-blue-600">Cuenta PayPal</h3>
                  <FieldText v-model="miembro.referenciaPago" label="Email / cuenta PayPal" :edit-mode="editMode || isCreateMode" />
                  <p class="text-xs text-gray-400">Se enviará el cobro de la cuota a esta dirección PayPal.</p>
                </section>

                <section v-else-if="esTarjeta" key="tarjeta" class="flex-1 space-y-4 rounded-xl border border-gray-100 bg-gray-50/60 p-5">
                  <h3 class="text-xs font-semibold uppercase tracking-widest text-gray-600">Tarjeta de pago</h3>
                  <FieldText v-model="miembro.referenciaPago" label="Referencia / últimos 4 dígitos" :edit-mode="editMode || isCreateMode" />
                  <p class="text-xs text-gray-400">Solo para referencia interna. No almacenamos datos completos de tarjeta.</p>
                </section>

                <section v-else-if="esBizum" key="bizum" class="flex-1 space-y-4 rounded-xl border border-teal-100 bg-teal-50/40 p-5">
                  <h3 class="text-xs font-semibold uppercase tracking-widest text-teal-600">Cuenta Bizum</h3>
                  <FieldText v-model="miembro.referenciaPago" label="Teléfono Bizum" :edit-mode="editMode || isCreateMode" />
                  <p class="text-xs text-gray-400">Se enviará la solicitud de cobro de la cuota por Bizum a este número.</p>
                </section>

                <section v-else key="empty" class="flex-1 flex items-center justify-center rounded-xl border border-dashed border-gray-200 p-8 text-center">
                  <div class="text-gray-400">
                    <p class="text-2xl mb-2" v-html="miembro.formaPagoId ? formaPagoIcono(formaPagoSeleccionada?.nombre) : '👆'"></p>
                    <p class="text-sm">{{ miembro.formaPagoId ? 'No se requieren datos adicionales' : 'Selecciona un procedimiento de cobro' }}</p>
                  </div>
                </section>
              </Transition>
            </div>

              </div>
            </AccordionPanel>

            <!-- Sub-acordeón: Cuota aplicada -->
            <AccordionPanel v-if="requiereCuota" :defaultOpen="false">
              <template #title>
                <span class="w-2 h-2 rounded-full bg-indigo-500 shrink-0"></span>
                <h3 class="text-sm font-semibold text-slate-800">Cuota aplicada</h3>
              </template>
              <template #actions>
                <button v-if="puedeModificarCuota" type="button" @click="abrirModalIncremento"
                  class="inline-flex items-center gap-1.5 h-8 px-3 text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg hover:bg-emerald-100 transition-colors">
                  Incremento voluntario
                </button>
                <button v-if="puedeSolicitarReduccion" type="button" @click="abrirModalReduccion"
                  class="inline-flex items-center gap-1.5 h-8 px-3 text-xs font-medium text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-lg hover:bg-indigo-100 transition-colors">
                  Solicitar reducción
                </button>
              </template>
              <div class="p-5 space-y-3">

              <div class="grid grid-cols-1 md:grid-cols-1 sm:grid-cols-2 gap-4">
                <!-- Tipo de cuota -->
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Tipo de cuota</label>
                  <p class="text-sm text-gray-800">{{ tipoCuotaNombre || '—' }}</p>
                  <p class="text-xs text-gray-500 mt-1">
                    Se hereda del tipo de {{ orgConfig.miembro }} seleccionado más arriba.
                  </p>
                </div>

                <!-- Importe de la cuota -->
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Importe</label>
                  <p class="text-sm text-gray-800">
                    <template v-if="cuotaVigente">
                      <span class="font-semibold">{{ formatEuros(cuotaVigente.importe) }}</span>
                      <span class="text-gray-500"> · ejercicio {{ cuotaVigente.ejercicio }}</span>
                    </template>
                    <span v-else class="text-gray-400 italic">Sin cuota generada todavía</span>
                  </p>
                  <p v-if="motivoReduccionResumen" class="text-xs text-emerald-700 mt-1">
                    Reducción aplicada: {{ motivoReduccionResumen }}
                  </p>
                  <p v-if="incrementoCuotaActual > 0" class="text-xs text-amber-700 mt-1">
                    Incremento voluntario: +{{ formatEuros(incrementoCuotaActual) }}
                    <span v-if="miembro.incrementoCuotaObs" class="text-gray-500"> · {{ miembro.incrementoCuotaObs }}</span>
                  </p>
                </div>
              </div>

              <!-- Historial de solicitudes de reducción del socio -->
              <div v-if="solicitudesReduccion.length" class="space-y-1.5 pt-1">
                <p class="text-xs font-medium text-gray-500">Solicitudes de reducción tramitadas</p>
                <div v-for="s in solicitudesReduccion" :key="s.id"
                  class="rounded-lg border px-3 py-2 text-xs flex items-start justify-between gap-3"
                  :class="claseEstadoSolicitud(s.estado)">
                  <div>
                    <span>
                      <strong>{{ etiquetaEstadoSolicitud(s.estado) }}</strong>
                      <template v-if="s.motivoReduccion"> · {{ s.motivoReduccion.nombre }}</template>
                      <span class="opacity-70"> · ejercicio {{ s.ejercicio }}</span>
                    </span>
                    <p v-if="s.estado === 'RECHAZADA' && s.motivoRechazo" class="mt-0.5">
                      Motivo del rechazo: {{ s.motivoRechazo }}
                    </p>
                  </div>
                  <div class="flex items-center gap-2 shrink-0">
                    <span class="opacity-60">{{ fechaCorta(s.fechaResolucion || s.fechaPresentacion) }}</span>
                    <button v-if="s.estado === 'PRESENTADA' && modoPropio"
                      type="button" @click="anularReduccion(s)"
                      class="text-red-600 hover:text-red-800 font-medium">Anular</button>
                  </div>
                </div>
              </div>

              </div>
            </AccordionPanel>

            <!-- Sub-acordeón: Historial de cuotas -->
            <AccordionPanel v-if="!isCreateMode && requiereCuota" :defaultOpen="false">
              <template #title>
                <span class="w-2 h-2 rounded-full bg-sky-500 shrink-0"></span>
                <h3 class="text-sm font-semibold text-slate-800">Historial de cuotas</h3>
              </template>
              <div v-if="loadingCuotas" class="px-5 py-6 text-center text-gray-400 text-sm">Cargando…</div>
              <div v-else-if="!cuotas.length" class="px-5 py-6 text-center text-gray-400 text-sm italic">Sin cuotas registradas</div>
              <div v-else class="overflow-x-auto -mx-1"><table class="min-w-full divide-y divide-gray-100 text-sm">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-5 py-2 text-left text-xs font-medium text-gray-500 uppercase">Ejercicio</th>
                    <th class="px-5 py-2 text-right text-xs font-medium text-gray-500 uppercase">Importe</th>
                    <th class="px-5 py-2 text-right text-xs font-medium text-gray-500 uppercase">Pagado</th>
                    <th class="px-5 py-2 text-left text-xs font-medium text-gray-500 uppercase">Fecha pago</th>
                    <th class="px-5 py-2 text-left text-xs font-medium text-gray-500 uppercase">Modo</th>
                    <th class="px-5 py-2 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-50">
                  <tr v-for="c in cuotasOrdenadas" :key="c.id" class="hover:bg-gray-50">
                    <td class="px-5 py-2.5 font-semibold text-gray-900">{{ c.ejercicio }}</td>
                    <td class="px-5 py-2.5 text-right text-gray-700">{{ formatEuros(c.importe) }}</td>
                    <td class="px-5 py-2.5 text-right"
                      :class="Number(c.importePagado) >= Number(c.importe) ? 'text-green-700 font-medium' : 'text-amber-600'">
                      {{ formatEuros(c.importePagado) }}
                    </td>
                    <td class="px-5 py-2.5 text-gray-500">{{ c.fechaPago ?? '—' }}</td>
                    <td class="px-5 py-2.5 text-gray-500 text-xs">{{ c.modoIngreso ?? '—' }}</td>
                    <td class="px-5 py-2.5">
                      <span class="px-2 py-0.5 text-xs font-medium rounded-full" :style="badgeColorStyle(c.estado)">
                        {{ c.estado?.nombre ?? '—' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table></div>
            </AccordionPanel>

            <!-- Sub-acordeón: Justificantes de gasto -->
            <AccordionPanel v-if="!isCreateMode" :defaultOpen="false">
              <template #title>
                <span class="w-2 h-2 rounded-full bg-amber-500 shrink-0"></span>
                <h3 class="text-sm font-semibold text-slate-800">Justificantes de gasto</h3>
              </template>
              <div class="p-5">
                <JustificantesGastoPanel modo="PROPIO" :miembro-id="miembro.id" />
              </div>
            </AccordionPanel>

            </AccordionGroup>
          </div>
        </AccordionPanel>

        <!-- ── 3. MEMBRESÍA Y PARTICIPACIÓN ── -->
        <AccordionPanel :defaultOpen="false">
          <template #title>
            <span class="w-2 h-2 rounded-full bg-violet-500 shrink-0"></span>
            <h2 class="text-sm font-semibold text-slate-800">Membresía y participación</h2>
          </template>
          <div class="p-5 space-y-5">

            <!-- Situación de membresía -->
            <section class="space-y-4 rounded-xl border border-gray-200 p-5">
              <h3 class="text-xs font-semibold uppercase tracking-widest text-purple-600">Situación</h3>
              <div class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 lg:grid-cols-4 gap-4">
                <FieldSelect v-model="miembro.tipoMiembroId" :label="`Tipo de ${orgConfig.miembro} *`" :edit-mode="editAdmin"
                  :options="catalogos.tiposMiembro" option-label="nombre" option-value="id" />
                <FieldSelect v-model="miembro.estadoId" label="Estado *" :edit-mode="editAdmin"
                  :options="catalogos.estadosMiembro" option-label="nombre" option-value="id" />
                <FieldText v-model="miembro.fechaAlta" label="Fecha de alta *" type="date" :edit-mode="editAdmin" />
                <FieldSelect v-model="miembro.agrupacionId" label="Agrupación territorial" :edit-mode="editAdmin"
                  :options="catalogos.agrupaciones" option-label="nombre" option-value="id" empty-label="Sin asignar" />
              </div>

              <!-- Crear cuenta (sólo en alta) -->
              <div v-if="isCreateMode" class="pt-3 border-t border-indigo-100">
                <label class="flex items-start gap-3 cursor-pointer group">
                  <input type="checkbox" v-model="crearCuenta"
                    class="mt-0.5 h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                  <div>
                    <span class="text-sm font-medium text-gray-900 group-hover:text-indigo-700">
                      Crear cuenta de acceso a la aplicación
                    </span>
                    <p class="text-xs text-gray-500 mt-0.5">
                      La cuenta se creará inactiva. El socio recibirá un email con un enlace para establecer su contraseña (requiere SMTP configurado en Parámetros Generales).
                    </p>
                  </div>
                </label>
                <p v-if="crearCuenta && !miembro.email" class="mt-2 text-xs text-amber-600">
                  Se requiere email para crear la cuenta de acceso.
                </p>
              </div>

              <!-- Sección de baja -->
              <template v-if="estadoEsBaja">
                <div class="pt-3 border-t border-red-100 space-y-4">
                  <div class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 gap-4">
                    <FieldText v-model="miembro.fechaBaja" label="Fecha de baja" type="date" :edit-mode="editMode || isCreateMode" />
                    <FieldSelect v-model="miembro.motivoBajaId" label="Motivo de baja" :edit-mode="editMode || isCreateMode"
                      :options="catalogos.motivosBaja" option-label="nombre" option-value="id" empty-label="Sin especificar" />
                  </div>
                  <FieldText v-model="miembro.motivoBajaTexto" label="Observaciones de baja" :edit-mode="editMode || isCreateMode" />
                </div>
              </template>
            </section>

            <!-- Disposición a participar -->
            <section class="rounded-xl border border-gray-200 p-5">
              <FieldCheckbox v-model="miembro.esVoluntario"
                label="Dispuesto/a a participar en actividades de la asociación"
                :edit-mode="editForm" />
              <p class="text-xs text-slate-500 mt-1.5">
                Marca esta casilla para indicar tus habilidades, intereses y disponibilidad horaria.
              </p>
            </section>

            <template v-if="miembro.esVoluntario">
              <div class="grid grid-cols-1 lg:grid-cols-1 sm:grid-cols-2 gap-5">

                <!-- Perfil voluntario -->
                <section class="space-y-4 rounded-xl border border-gray-200 p-5">
                  <h3 class="text-xs font-semibold uppercase tracking-widest text-purple-600">Perfil voluntario</h3>
                  <div class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 gap-4">
                    <FieldText v-model="miembro.profesion" label="Profesión" :edit-mode="editForm" />
                    <FieldSelect v-model="miembro.nivelEstudiosId" label="Nivel de estudios"
                      :options="catalogos.nivelesEstudios" option-label="nombre" option-value="id"
                      empty-label="Sin especificar" :edit-mode="editForm" />
                  </div>
                  <FieldTextarea v-model="miembro.intereses" label="Intereses" :edit-mode="editForm" rows="3" />
                  <FieldTextarea v-model="miembro.experienciaVoluntariado" label="Experiencia en voluntariado" :edit-mode="editForm" rows="3" />
                  <FieldTextarea v-model="miembro.observacionesVoluntariado" label="Observaciones de voluntariado" :edit-mode="editForm" rows="3" />
                  <div class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 pt-1">
                    <FieldCheckbox v-model="miembro.puedeConducir" label="Puede conducir" :edit-mode="editForm" />
                    <FieldCheckbox v-model="miembro.vehiculoPropio" label="Vehículo propio" :edit-mode="editForm" />
                    <FieldCheckbox v-model="miembro.disponibilidadViajar" label="Disponibilidad para viajar" :edit-mode="editForm" />
                  </div>
                </section>

                <!-- Habilidades -->
                <section class="space-y-3 rounded-xl border border-gray-200 p-5">
                  <div class="flex items-center justify-between">
                    <h3 class="text-xs font-semibold uppercase tracking-widest text-indigo-600">Habilidades</h3>
                    <button @click="mostrarFormHabilidad = !mostrarFormHabilidad"
                      class="px-3 py-1.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700">
                      + Añadir
                    </button>
                  </div>

                  <div v-if="mostrarFormHabilidad" class="bg-indigo-50 border border-indigo-200 rounded-xl p-4 space-y-3">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Habilidad del catálogo</label>
                      <select v-model="nuevaHabilidad.habilidadId"
                        class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500">
                        <option value="">Seleccionar...</option>
                        <template v-for="grupo in habilidadesAgrupadas" :key="grupo.categoriaId">
                          <optgroup :label="grupo.categoriaNombre">
                            <option v-for="h in grupo.habilidades" :key="h.id" :value="h.id">{{ h.nombre }}</option>
                          </optgroup>
                        </template>
                      </select>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Nivel</label>
                      <select v-model="nuevaHabilidad.nivelId"
                        class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500">
                        <option value="">Sin especificar</option>
                        <option v-for="n in catalogos.nivelesHabilidad" :key="n.id" :value="n.id">{{ n.nombre }}</option>
                      </select>
                    </div>
                    <div class="flex gap-2 justify-end">
                      <button @click="mostrarFormHabilidad = false; nuevaHabilidad = { habilidadId: '', nivelId: '' }"
                        class="px-3 py-1.5 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50">Cancelar</button>
                      <button @click="guardarHabilidad" :disabled="!nuevaHabilidad.habilidadId"
                        class="px-3 py-1.5 text-sm text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50">Guardar</button>
                    </div>
                  </div>

                  <p v-if="isCreateMode" class="text-xs text-gray-400 italic py-2">
                    Las habilidades podrán registrarse una vez creada la ficha.
                  </p>
                  <template v-else>
                    <div v-if="loadingHabilidades" class="text-center py-6 text-gray-400 text-sm">Cargando...</div>
                    <div v-else-if="miembroHabilidades.length === 0" class="text-center py-10 text-gray-400 text-sm">
                      Sin habilidades registradas.
                    </div>
                    <div v-else class="space-y-2">
                      <div v-for="mh in miembroHabilidades" :key="mh.id"
                        class="flex items-center justify-between bg-gray-50 border border-gray-200 rounded-xl px-4 py-3">
                        <div>
                          <p class="text-sm font-medium text-gray-900">{{ mh.habilidad?.nombre }}</p>
                          <div class="flex items-center gap-2 mt-0.5">
                            <span v-if="mh.habilidad?.categoria?.nombre" class="text-xs text-indigo-500">{{ mh.habilidad.categoria.nombre }}</span>
                            <span v-if="mh.nivelHabilidad?.nombre" class="text-xs text-gray-500">{{ mh.nivelHabilidad.nombre }}</span>
                            <span v-if="mh.validado" class="text-xs text-green-600 font-medium">Validado</span>
                          </div>
                        </div>
                        <button @click="eliminarHabilidad(mh.id)" class="text-xs text-red-400 hover:text-red-600 ml-3">Eliminar</button>
                      </div>
                    </div>
                  </template>
                </section>

              </div>

              <!-- Disponibilidad -->
              <section class="space-y-4 rounded-xl border border-gray-200 p-5">
                <h3 class="text-xs font-semibold uppercase tracking-widest text-sky-600">Disponibilidad</h3>
                <div class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 gap-4">
                  <FieldText v-model="miembro.disponibilidad" label="Disponibilidad" :edit-mode="editForm" />
                  <FieldText v-model="miembro.horasDisponiblesSemana" label="Horas/semana" type="number" :edit-mode="editForm" />
                </div>

                <p v-if="isCreateMode" class="text-xs text-gray-400 italic">
                  Las franjas horarias podrán configurarse una vez creada la ficha.
                </p>
                <template v-else>
                  <div v-if="loadingFranjas" class="text-center py-6 text-gray-400 text-sm">Cargando...</div>
                  <div v-else class="grid grid-cols-1 sm:grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 lg:grid-cols-7 gap-2">
                    <div v-for="(dia, i) in diasSemana" :key="i"
                      class="rounded-xl border flex flex-col min-h-[140px] overflow-hidden"
                      :class="franjasPorDia[i]?.length ? 'border-purple-200' : 'border-gray-200'">
                      <div class="px-3 py-2 flex items-center justify-between"
                        :class="franjasPorDia[i]?.length ? 'bg-purple-100' : 'bg-gray-100'">
                        <span class="text-xs font-semibold"
                          :class="franjasPorDia[i]?.length ? 'text-purple-800' : 'text-gray-500'">{{ dia }}</span>
                        <button @click="abrirFormFranja(i)"
                          class="w-5 h-5 flex items-center justify-center rounded-full text-sm font-bold leading-none"
                          :class="franjasPorDia[i]?.length ? 'text-purple-500 hover:bg-purple-200' : 'text-gray-400 hover:bg-gray-200'">
                          +
                        </button>
                      </div>
                      <div class="flex-1 px-2 py-2 flex flex-col gap-1">
                        <template v-if="franjasPorDia[i]?.length">
                          <div v-for="f in franjasPorDia[i]" :key="f.id"
                            class="flex items-center justify-between bg-white rounded-lg px-2 py-1 border border-purple-100 text-xs">
                            <span class="text-purple-700 font-medium">{{ f.horaInicio.slice(0,5) }}–{{ f.horaFin.slice(0,5) }}</span>
                            <button @click="eliminarFranja(f.id)" class="text-gray-300 hover:text-red-400 font-bold ml-1 leading-none">×</button>
                          </div>
                        </template>
                        <div v-else class="flex-1 flex items-center justify-center">
                          <span class="text-xs text-gray-400 italic">No disponible</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div v-if="!mostrarFormFranja" class="flex justify-end">
                    <button @click="abrirFormFranja(0)"
                      class="px-3 py-1.5 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700">
                      + Añadir franja
                    </button>
                  </div>

                  <!-- Drawer de nueva franja: el día ya viene fijado por la columna -->
                  <AppDrawer
                    v-model="mostrarFormFranja"
                    :title="`Disponibilidad — ${diasSemanaLargo[nuevaFranja.diaSemana]}`"
                    subtitle="Indica el tramo horario en que puedes colaborar"
                    size="sm"
                  >
                    <div class="space-y-4">
                      <!-- Día (cambiable, por si se abrió desde el botón general) -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Día de la semana</label>
                        <div class="grid grid-cols-7 gap-1">
                          <button
                            v-for="(dia, i) in diasSemana" :key="i"
                            type="button"
                            @click="nuevaFranja.diaSemana = i"
                            class="h-9 rounded-lg text-xs font-medium transition-colors"
                            :class="nuevaFranja.diaSemana === i
                              ? 'bg-purple-600 text-white'
                              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
                          >{{ dia }}</button>
                        </div>
                      </div>

                      <div class="grid grid-cols-2 gap-3">
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">Desde</label>
                          <input v-model="nuevaFranja.horaInicio" type="time"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
                        </div>
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">Hasta</label>
                          <input v-model="nuevaFranja.horaFin" type="time"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
                        </div>
                      </div>
                    </div>

                    <template #footer>
                      <button @click="mostrarFormFranja = false"
                        class="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50">
                        Cancelar
                      </button>
                      <button @click="guardarFranja" :disabled="!nuevaFranja.horaInicio || !nuevaFranja.horaFin"
                        class="px-4 py-2 text-sm text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50">
                        Guardar franja
                      </button>
                    </template>
                  </AppDrawer>
                </template>
              </section>
            </template>
          </div>
        </AccordionPanel>

        <!-- ── 6. CARGOS ── -->
        <AccordionPanel v-if="!isCreateMode" :defaultOpen="false">
          <template #title>
            <span class="w-2 h-2 rounded-full bg-slate-400 shrink-0"></span>
            <h2 class="text-sm font-semibold text-slate-800">Cargos y nombramientos</h2>
          </template>
          <div class="p-5">
            <div v-if="loadingNombramientos" class="text-center py-6 text-gray-400 text-sm">Cargando…</div>
            <div v-else-if="!nombramientos.length"
              class="rounded-xl border border-dashed border-gray-200 p-8 text-center text-sm text-gray-400">
              Sin nombramientos registrados.
            </div>
            <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <div class="overflow-x-auto -mx-1"><table class="min-w-full divide-y divide-gray-100 text-sm">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Cargo / Rol</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Ámbito</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Desde</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Hasta</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-50">
                  <tr v-for="n in nombramientos" :key="n.id" class="hover:bg-gray-50">
                    <td class="px-4 py-2.5 font-medium text-gray-900">{{ n.rol?.nombre || '—' }}</td>
                    <td class="px-4 py-2.5 text-gray-600">{{ n.agrupacion?.nombre || 'Toda la organización' }}</td>
                    <td class="px-4 py-2.5 text-gray-600">{{ n.fechaInicio ? formatDate(n.fechaInicio) : '—' }}</td>
                    <td class="px-4 py-2.5 text-gray-600">{{ n.fechaFin ? formatDate(n.fechaFin) : '—' }}</td>
                    <td class="px-4 py-2.5">
                      <span :class="['inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium',
                        !n.fechaFin ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-500']">
                        {{ !n.fechaFin ? 'Vigente' : 'Finalizado' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table></div>
            </div>
          </div>
        </AccordionPanel>

        <!-- ── 7. ACCESO Y ROLES ── -->
        <AccordionPanel v-if="!isCreateMode" :defaultOpen="false">
          <template #title>
            <span class="w-2 h-2 rounded-full bg-rose-500 shrink-0"></span>
            <h2 class="text-sm font-semibold text-slate-800">Acceso y roles</h2>
          </template>
          <div class="p-5 space-y-5">

            <!-- Sin cuenta de usuario -->
            <div v-if="!miembro.usuario">
              <div v-if="!modalCuenta.abierto" class="rounded-xl border border-dashed border-gray-200 p-8 text-center text-sm text-gray-400">
                <p class="text-3xl mb-3">🔒</p>
                <p class="font-medium text-gray-500">Este miembro no tiene cuenta de acceso a la aplicación.</p>
                <button v-if="!modoPropio" type="button" @click="abrirModalCuenta"
                  class="mt-4 inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-indigo-600 text-white text-xs font-medium hover:bg-indigo-700 transition-colors">
                  Crear cuenta de acceso
                </button>
              </div>

              <div v-else class="rounded-xl border border-indigo-200 bg-indigo-50 p-6 space-y-4">
                <div class="flex items-center justify-between">
                  <h3 class="text-sm font-semibold text-indigo-800">Crear cuenta de acceso</h3>
                  <button type="button" @click="modalCuenta.abierto = false" class="text-gray-400 hover:text-gray-600 text-lg leading-none">&times;</button>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label class="block text-xs font-medium text-gray-700 mb-1">Email de acceso</label>
                    <input v-model="modalCuenta.email" type="email"
                      class="h-10 w-full px-3 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white" />
                  </div>
                  <div class="flex flex-col justify-end">
                    <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                      <input v-model="modalCuenta.enviarEmail" type="checkbox" class="rounded text-indigo-600" />
                      Enviar email de bienvenida con enlace de activación
                    </label>
                  </div>
                </div>
                <p v-if="!modalCuenta.enviarEmail" class="text-xs text-amber-700 bg-amber-50 rounded-lg px-3 py-2">
                  Sin email de bienvenida, el miembro no podrá acceder hasta que se le asigne una contraseña manualmente.
                </p>
                <ErrorAlert v-if="modalCuenta.error" :message="modalCuenta.error" />
                <div class="flex gap-2 pt-1">
                  <button type="button" @click="crearCuentaDesdeTab"
                    :disabled="!modalCuenta.email || modalCuenta.cargando"
                    class="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                    {{ modalCuenta.cargando ? 'Creando...' : 'Crear cuenta' }}
                  </button>
                  <button type="button" @click="modalCuenta.abierto = false"
                    class="px-4 py-2 rounded-lg border border-gray-300 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
                    Cancelar
                  </button>
                </div>
              </div>
            </div>

            <template v-else>
              <!-- Datos de la cuenta -->
              <section class="rounded-xl border border-gray-200 p-5 space-y-3">
                <h3 class="text-xs font-semibold uppercase tracking-widest text-purple-600">Cuenta de acceso</h3>
                <div class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
                  <div>
                    <p class="text-xs text-gray-500 mb-0.5">Email de acceso</p>
                    <p class="font-medium text-gray-900">{{ miembro.usuario.email }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500 mb-0.5">Estado</p>
                    <span :class="['inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium',
                      miembro.usuario.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-600']">
                      {{ miembro.usuario.activo ? 'Activa' : 'Bloqueada' }}
                    </span>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500 mb-0.5">Último acceso</p>
                    <p class="text-gray-700">{{ miembro.usuario.ultimoAcceso ? formatDate(miembro.usuario.ultimoAcceso) : 'Nunca' }}</p>
                  </div>
                </div>

                <!-- Cambiar contraseña (solo en modo propio) -->
                <div v-if="modoPropio" class="pt-3 border-t border-gray-100">
                  <div class="rounded-lg border border-dashed border-gray-300">
                    <button type="button" @click="cambioPass.activo = !cambioPass.activo"
                      class="w-full flex items-center justify-between px-4 py-3 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
                      <span>Cambiar contraseña</span>
                      <span class="text-xs px-2 py-0.5 rounded-full"
                        :class="cambioPass.activo ? 'bg-gray-600 text-white' : 'bg-gray-200 text-gray-500'">
                        {{ cambioPass.activo ? 'Cancelar' : 'Cambiar' }}
                      </span>
                    </button>
                    <div v-if="cambioPass.activo" class="px-4 pb-4 border-t border-gray-100 pt-3 space-y-3">
                      <div class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                        <div>
                          <label class="block text-xs font-medium text-gray-700 mb-1">Contraseña actual</label>
                          <input v-model="cambioPass.actual" type="password"
                            class="h-9 w-full px-3 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white" />
                        </div>
                        <div>
                          <label class="block text-xs font-medium text-gray-700 mb-1">Nueva contraseña</label>
                          <input v-model="cambioPass.nueva" type="password"
                            class="h-9 w-full px-3 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white" />
                        </div>
                        <div>
                          <label class="block text-xs font-medium text-gray-700 mb-1">Repetir nueva</label>
                          <input v-model="cambioPass.repetir" type="password"
                            class="h-9 w-full px-3 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white" />
                        </div>
                      </div>
                      <ErrorAlert v-if="cambioPass.error" :message="cambioPass.error" />
                      <p v-if="cambioPass.ok" class="text-xs text-green-600">{{ cambioPass.ok }}</p>
                      <div class="flex justify-end gap-2">
                        <button type="button" @click="cambioPass.activo = false; cambioPass.error = ''; cambioPass.ok = ''"
                          class="px-4 py-1.5 text-sm border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50">
                          Cancelar
                        </button>
                        <button type="button" @click="guardarPassword" :disabled="guardandoPass"
                          class="px-4 py-1.5 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50">
                          {{ guardandoPass ? 'Guardando…' : 'Actualizar contraseña' }}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Roles -->
              <section class="rounded-xl border border-gray-200 p-5 space-y-3">
                <h3 class="text-xs font-semibold uppercase tracking-widest text-purple-600">Roles asignados</h3>

                <div v-if="!rolesAsignados.length" class="text-sm text-gray-400 italic py-2">
                  Sin roles asignados.
                </div>
                <div v-else class="divide-y divide-gray-100">
                  <div v-for="ur in rolesAsignados" :key="ur.id"
                    :class="['flex items-center justify-between py-2.5', !ur.activo && 'opacity-40']">
                    <div class="flex items-center gap-3">
                      <span :class="['w-1.5 h-1.5 rounded-full shrink-0', ur.activo ? 'bg-green-500' : 'bg-gray-300']" />
                      <div>
                        <p class="text-sm font-medium text-gray-900">{{ ur.rol.nombre }}</p>
                        <p v-if="agrupacionNombre(ur.agrupacionId)" class="text-xs text-gray-500">
                          Ámbito: {{ agrupacionNombre(ur.agrupacionId) }}
                        </p>
                        <p v-else class="text-xs text-gray-500">Ámbito: toda la organización</p>
                      </div>
                    </div>
                    <div class="flex items-center gap-2">
                      <span :class="['text-xs px-2 py-0.5 rounded-full font-medium', tipoRolClass(ur.rol.tipo)]">
                        {{ ur.rol.tipo }}
                      </span>
                      <button v-if="!modoPropio" @click="revocarRol(ur.rol.id)"
                        class="text-xs text-red-500 hover:text-red-700 px-1.5 py-0.5 rounded hover:bg-red-50"
                        title="Revocar rol">
                        Revocar
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Asignar nuevo rol (solo admin) -->
                <div v-if="!modoPropio" class="pt-2 border-t border-gray-100 space-y-2">
                  <p class="text-xs font-medium text-gray-600">Asignar rol</p>
                  <div class="flex flex-wrap gap-2">
                    <select v-model="nuevoRolId"
                      class="flex-1 min-w-full sm:w-40 rounded-lg border border-gray-300 px-3 py-1.5 text-sm focus:border-purple-500 focus:ring-1 focus:ring-purple-500">
                      <option value="">Seleccionar rol…</option>
                      <optgroup v-for="tipo in ['FUNCIONAL','ORGANIZACION','SISTEMA','PERSONALIZADO']" :key="tipo" :label="tipo">
                        <option v-for="r in rolesDisponibles.filter(r => r.tipo === tipo)"
                          :key="r.id" :value="r.id">{{ r.nombre }}</option>
                      </optgroup>
                    </select>
                    <select v-model="nuevoRolAgrupacionId"
                      class="flex-1 min-w-full sm:w-40 rounded-lg border border-gray-300 px-3 py-1.5 text-sm focus:border-purple-500 focus:ring-1 focus:ring-purple-500">
                      <option value="">Toda la organización</option>
                      <option v-for="a in catalogos.agrupaciones" :key="a.id" :value="a.id">{{ a.nombre }}</option>
                    </select>
                    <button @click="asignarRol" :disabled="!nuevoRolId || guardandoRol"
                      class="px-3 py-1.5 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700 disabled:opacity-50">
                      Asignar
                    </button>
                  </div>
                  <ErrorAlert v-if="errorRol" :message="errorRol" />
                </div>
              </section>
            </template>

          </div>
        </AccordionPanel>

      </AccordionGroup>
    </div>

    <!-- Modal: solicitar reducción de cuota -->
    <div v-if="modalReduccion.visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg">
        <div class="px-6 py-4 border-b border-slate-200">
          <h3 class="text-base font-semibold text-slate-900">Solicitar reducción</h3>
          <p class="text-xs text-slate-500 mt-0.5">
            Elige el motivo y adjunta un documento que acredite tu situación (tarjeta de
            desempleo, carné de estudiante, resolución de jubilación…). El tesorero la revisará.
          </p>
        </div>
        <div class="px-6 py-5 space-y-4">
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Motivo de reducción *</label>
            <select v-model="modalReduccion.motivoId"
              class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 bg-white">
              <option :value="null">— Selecciona motivo —</option>
              <option v-for="m in catalogos.motivosReduccion" :key="m.id" :value="m.id">
                {{ m.nombre }} ({{ Number(m.porcentajeReduccion) }}%)
              </option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Explicación <span class="text-slate-400">(opcional)</span></label>
            <textarea v-model="modalReduccion.texto" rows="3"
              class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              placeholder="Describe brevemente tu situación…"></textarea>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Documento acreditativo</label>
            <input type="file" multiple accept="image/*,application/pdf"
              @change="modalReduccion.archivos = Array.from($event.target.files || [])"
              class="block w-full text-sm text-slate-600 file:mr-3 file:h-8 file:px-3 file:rounded-lg file:border file:border-indigo-200 file:bg-indigo-50 file:text-indigo-700 file:text-xs file:font-medium hover:file:bg-indigo-100" />
            <p v-if="modalReduccion.archivos.length" class="text-xs text-slate-500 mt-1">
              {{ modalReduccion.archivos.length }} archivo(s) seleccionado(s)
            </p>
            <p class="text-xs text-slate-400 mt-1">JPG, PNG o PDF · máx. 30 MB por archivo</p>
          </div>
          <p v-if="modalReduccion.error" class="text-red-600 text-sm bg-red-50 border border-red-200 px-3 py-2 rounded-lg">
            {{ modalReduccion.error }}
          </p>
        </div>
        <div class="flex justify-end gap-3 px-6 py-4 border-t border-slate-200">
          <button @click="modalReduccion.visible = false"
            class="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50">
            Cancelar
          </button>
          <button @click="presentarReduccion" :disabled="!modalReduccion.motivoId || modalReduccion.guardando"
            class="px-5 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50">
            {{ modalReduccion.guardando ? 'Enviando…' : 'Enviar solicitud' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: modificación (incremento voluntario) de cuota -->
    <div v-if="modalIncremento.visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg">
        <div class="px-6 py-4 border-b border-slate-200">
          <h3 class="text-base font-semibold text-slate-900">Incremento voluntario</h3>
          <p class="text-xs text-slate-500 mt-0.5">
            Si quieres aportar más de la cuota establecida, indica el incremento voluntario.
            Se sumará a tu cuota base. No requiere aprobación: se aplica directamente.
          </p>
        </div>
        <div class="px-6 py-5 space-y-4">
          <div>
            <div class="flex items-center gap-3">
              <label class="text-xs font-medium text-slate-700 shrink-0">Incremento sobre la cuota base *</label>
              <div class="relative w-full sm:w-28 shrink-0">
                <input type="number" min="0" step="1" v-model.number="modalIncremento.incremento"
                  class="w-full border border-slate-300 rounded-lg pl-3 pr-7 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400" />
                <span class="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-slate-400 pointer-events-none">€</span>
              </div>
            </div>
            <p class="text-xs text-slate-400 mt-1">Introduce 0 para retirar un incremento anterior.</p>
          </div>
          <div v-if="Number(modalIncremento.incremento) > 0 && cuotaTotalConIncremento != null"
               class="text-xs text-amber-700 bg-amber-50 rounded-lg px-3 py-2">
            Tus futuras cuotas se verán incrementadas en {{ formatEuros(Number(modalIncremento.incremento)) }}.
            En el {{ anioEnCurso }} se te girará un recibo por {{ formatEuros(cuotaTotalConIncremento) }}.
            Muchas gracias.
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Observaciones <span class="text-slate-400">(opcional)</span></label>
            <textarea v-model="modalIncremento.observaciones" rows="3"
              class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
              placeholder="Motivo de la aportación adicional…"></textarea>
          </div>
          <p v-if="modalIncremento.error" class="text-red-600 text-sm bg-red-50 border border-red-200 px-3 py-2 rounded-lg">
            {{ modalIncremento.error }}
          </p>
        </div>
        <div class="flex justify-end gap-3 px-6 py-4 border-t border-slate-200">
          <button @click="modalIncremento.visible = false"
            class="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50">
            Cancelar
          </button>
          <button @click="guardarIncremento" :disabled="modalIncremento.guardando"
            class="px-5 py-2 text-sm font-medium text-white bg-emerald-600 rounded-lg hover:bg-emerald-700 disabled:opacity-50">
            {{ modalIncremento.guardando ? 'Guardando…' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: confirmar anonimización RGPD (irreversible) -->
    <div v-if="modalAnonimizar" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md">
        <div class="px-6 py-4 border-b border-slate-200">
          <h3 class="text-base font-semibold text-slate-900">Anonimizar datos personales</h3>
        </div>
        <div class="px-6 py-5 space-y-3 text-sm text-slate-600">
          <p>
            Esta acción elimina <strong>de forma irreversible</strong> el nombre, documento,
            contacto, dirección, IBAN y demás datos personales de este {{ orgConfig.miembro }}.
          </p>
          <p>
            El registro se conserva sin datos identificativos (para estadística e
            histórico). <strong>No se puede deshacer.</strong>
          </p>
          <p v-if="anonimizarError" class="text-red-600 bg-red-50 border border-red-200 px-3 py-2 rounded-lg">
            {{ anonimizarError }}
          </p>
        </div>
        <div class="flex justify-end gap-3 px-6 py-4 border-t border-slate-200">
          <button @click="modalAnonimizar = false"
            class="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50">
            Cancelar
          </button>
          <button @click="confirmarAnonimizar" :disabled="anonimizando"
            class="px-5 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50">
            {{ anonimizando ? 'Anonimizando…' : 'Anonimizar definitivamente' }}
          </button>
        </div>
      </div>
    </div>

  </component>
</template>

<script setup>
import { ArrowUpTrayIcon } from '@heroicons/vue/24/outline'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { useToast } from '@/composables/useToast'
import { computed, defineComponent, h, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import AccordionGroup from '@/components/common/AccordionGroup.vue'
import AccordionPanel from '@/components/common/AccordionPanel.vue'
import AppDrawer from '@/components/common/AppDrawer.vue'
import AvatarImg from '@/components/common/AvatarImg.vue'
import JustificantesGastoPanel from '@/components/common/JustificantesGastoPanel.vue'
import { gql } from 'graphql-request'
import { graphqlClient } from '@/graphql/client.js'
import { useMiembro } from '@/composables/useMiembro'
import { badgeStyle, bandStyle } from '@/utils/badge'
import { useOrgConfigStore } from '@/stores/orgConfig'
import { useAuthStore } from '@/stores/auth.js'
import { usePermisos } from '@/composables/usePermisos.js'
const toast = useToast()

const props = defineProps({
  miembroIdProp: { type: String, default: null },
  modoPropio: { type: Boolean, default: false },
})

const route = useRoute()
const router = useRouter()
const orgConfig = useOrgConfigStore()
const { tienePermiso } = usePermisos()
const editMode = ref(false)
const saveMessage = ref('')
const crearCuenta = ref(false)

const {
  miembro,
  catalogos,
  loading,
  error,
  isCreateMode,
  nombreCompleto,
  loadCatalogos,
  fetchMiembro,
  saveMiembro,
  resetMiembro,
} = useMiembro()

const detectCreateMode = route.name === 'NuevoMiembro'

if (detectCreateMode) {
  resetMiembro()
  isCreateMode.value = true
  editMode.value = true
}

// En /mis-datos (modoPropio) la ficha es editable de entrada: no hay paso previo
// de "Editar". editMode permanece siempre activo; solo se Guarda o se Descarta.
if (props.modoPropio) {
  editMode.value = true
}

// ── Layout dinámico ───────────────────────────────────────────────────────────

const tituloPage = computed(() => {
  if (isCreateMode.value) return `Nuevo ${orgConfig.miembro || 'miembro'}`
  return nombreCompleto.value || orgConfig.Miembro || 'Miembro'
})

const subtituloPage = computed(() => {
  if (loading.value || !miembro.value.id) return ''
  const tipoNombre = catalogos.value.tiposMiembro?.find(t => t.id === miembro.value.tipoMiembroId)?.nombre
  const estadoNombre = catalogos.value.estadosMiembro?.find(e => e.id === miembro.value.estadoId)?.nombre
  return [tipoNombre, estadoNombre].filter(Boolean).join(' · ')
})

const layoutComponent = computed(() => props.modoPropio ? 'div' : AppLayout)
const layoutBindings = computed(() => props.modoPropio ? {} : {
  title: tituloPage.value,
  subtitle: subtituloPage.value,
})

// ── Modos de edición ──────────────────────────────────────────────────────────
// editForm  → datos que el propio socio puede modificar (personales, contacto,
//             económicos, participación). Disponible en modoPropio y para gestores.
// editAdmin → datos administrativos (tipo de miembro, estado, agrupación, alta,
//             RGPD, baja). NUNCA editables por el propio socio en /mis-datos.
const editForm  = computed(() => editMode.value || isCreateMode.value)
const editAdmin = computed(() => (editMode.value && !props.modoPropio) || isCreateMode.value)

// ── Forma de pago ─────────────────────────────────────────────────────────────

function formaPagoIcono(nombre) {
  const n = (nombre || '').toLowerCase()
  if (n.includes('paypal')) return `<svg viewBox="0 0 24 24" class="w-6 h-6 inline-block" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M7.144 19.532l1.049-5.751c.11-.605.691-1.002 1.304-.948 2.155.195 6.243.265 7.908-3.402 2.88-6.388-3.344-8.05-8.36-7.737C7.51 1.745 6.617 1.9 6.617 1.9L4 19.532h3.144z" fill="#009CDE"/><path d="M17.124 7.952c1.394 3.073-.51 6.252-3.971 7.257-1.307.378-2.856.507-4.293.507L8 19.532H4l2.617-17.47s4.91-.688 7.815.147c1.578.452 2.873 1.574 2.692 5.743z" fill="#003087"/><path d="M17.124 7.952c-.18 4.169-1.114 5.291-2.692 5.743-3.461 1.005-5.005-1.005-4.295.507-.71-1.512-.507-4.293-.507-4.293s3.073-.13 4.38-.508c2.165-.625 2.674-2.78 3.114-1.449z" fill="#012169"/></svg>`
  if (n.includes('bizum')) return `<svg viewBox="0 0 48 24" class="w-11 h-5 inline-block" xmlns="http://www.w3.org/2000/svg"><rect width="48" height="24" rx="5" fill="#00C3B2"/><text x="24" y="16.5" font-size="11" font-weight="800" fill="#fff" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" letter-spacing="-0.5">bizum</text></svg>`
  if (n.includes('tarjeta')) return `<svg viewBox="0 0 48 32" class="w-8 h-6 inline-block" xmlns="http://www.w3.org/2000/svg"><rect width="48" height="32" rx="4" fill="#252525"/><circle cx="19" cy="16" r="9" fill="#EB001B"/><circle cx="29" cy="16" r="9" fill="#F79E1B"/><path d="M24 8.536a9 9 0 0 1 0 14.928A9 9 0 0 1 24 8.536z" fill="#FF5F00"/></svg>`
  if (n.includes('transferencia') && n.includes('internacional')) return '<span class="text-xl">🌍</span>'
  if (n.includes('transferencia')) return '<span class="text-xl">🏦</span>'
  if (n.includes('domiciliación') || n.includes('sepa')) return '<span class="text-xl">📋</span>'
  if (n.includes('efectivo') || n.includes('metálico')) return '<span class="text-xl">💵</span>'
  return '<span class="text-xl">💰</span>'
}

// ── IBAN / SWIFT ─────────────────────────────────────────────────────────────

const ibanTouched = ref(false)

function ibanLimpiar(raw) {
  return (raw || '').replace(/\s/g, '').toUpperCase()
}

function ibanValidar(raw) {
  const iban = ibanLimpiar(raw)
  if (!iban) return null
  if (!/^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$/.test(iban)) return false
  const rearranged = iban.slice(4) + iban.slice(0, 4)
  const numeric = rearranged.split('').map(c => {
    const code = c.charCodeAt(0)
    return code >= 65 ? String(code - 55) : c
  }).join('')
  let remainder = 0
  for (const digit of numeric) {
    remainder = (remainder * 10 + parseInt(digit)) % 97
  }
  return remainder === 1
}

function ibanFormatear(raw) {
  return ibanLimpiar(raw).replace(/(.{4})(?=.)/g, '$1 ')
}

const ibanDisplay = computed(() => ibanFormatear(miembro.value.iban))

function onIbanInput(event) {
  const raw = event.target.value.replace(/\s/g, '').toUpperCase()
  miembro.value.iban = raw
  ibanTouched.value = true
  const formatted = ibanFormatear(raw)
  if (event.target.value !== formatted) {
    const pos = event.target.selectionStart
    event.target.value = formatted
    const spaces = (formatted.slice(0, pos).match(/ /g) || []).length
    const rawPos = pos - spaces
    let newPos = 0
    let counted = 0
    for (let i = 0; i < formatted.length; i++) {
      if (formatted[i] !== ' ') counted++
      if (counted === rawPos) { newPos = i + 1; break }
    }
    event.target.setSelectionRange(newPos, newPos)
  }
}

const formaPagoSeleccionada = computed(() =>
  catalogos.value.formasPago.find(fp => fp.id === miembro.value.formaPagoId)
)

// TipoMiembro seleccionado y si su tipo de cuota implica pago.
const tipoMiembroActual = computed(() =>
  catalogos.value.tiposMiembro?.find(t => t.id === miembro.value.tipoMiembroId) || null
)
const requiereCuota = computed(() => !!tipoMiembroActual.value?.requiereCuota)
const tipoCuotaNombre = computed(() => tipoMiembroActual.value?.nombre || '')

// Resumen del motivo de reducción individual (override).
const motivoReduccionResumen = computed(() => {
  const id = miembro.value.motivoReduccionId
  if (!id) return ''
  const m = catalogos.value.motivosReduccion?.find(x => x.id === id)
  if (!m) return ''
  const pct = Number(m.porcentajeReduccion)
  return `${m.nombre} (${pct}%${m.excluyeCuota ? ' · excluye cuota' : ''})`
})

const esTransferencia = computed(() => {
  const fp = formaPagoSeleccionada.value
  return !fp || fp.nombre.toLowerCase().includes('transferencia')
})

const esInternacional = computed(() => {
  const fp = formaPagoSeleccionada.value
  return fp?.nombre.toLowerCase().includes('internacional') ?? false
})

const esDomiciliacion = computed(() => {
  const n = formaPagoSeleccionada.value?.nombre.toLowerCase() ?? ''
  return n.includes('domiciliación') || n.includes('domiciliacion') || n.includes('sepa')
})

const esPaypal = computed(() =>
  formaPagoSeleccionada.value?.nombre.toLowerCase().includes('paypal') ?? false
)

const esTarjeta = computed(() =>
  formaPagoSeleccionada.value?.nombre.toLowerCase().includes('tarjeta') ?? false
)

const esBizum = computed(() =>
  formaPagoSeleccionada.value?.nombre.toLowerCase().includes('bizum') ?? false
)

// ─────────────────────────────────────────────────────────────────────────────

const formValido = computed(() => {
  const m = miembro.value
  const necesitaIban = esTransferencia.value || esDomiciliacion.value
  const ibanOk = !necesitaIban || !m.iban || ibanValidar(m.iban) !== false
  if (!isCreateMode.value) return ibanOk
  return !!(
    m.nombre?.trim() &&
    m.apellido1?.trim() &&
    m.tipoMiembroId &&
    m.estadoId &&
    m.fechaAlta &&
    ibanOk
  )
})

const estadoEsBaja = computed(() => {
  const estado = catalogos.value.estadosMiembro.find(e => e.id === miembro.value.estadoId)
  if (!estado) return false
  const norm = estado.nombre.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
  return norm.includes('baja')
})

const estadoColor      = computed(() => miembro.value.estado?.color)
const estadoBadgeStyle = computed(() => badgeStyle(estadoColor.value))
const estadoBandaStyle = computed(() => bandStyle(estadoColor.value))

const puedeEditarFoto = computed(() =>
  !isCreateMode.value && (editMode.value || props.modoPropio)
)

async function subirFoto(event) {
  const file = event.target.files?.[0]
  if (!file || !miembro.value.id) return
  const authStore = useAuthStore()
  const fd = new FormData()
  fd.append('file', file)
  try {
    const resp = await fetch(`/api/upload/foto-miembro/${miembro.value.id}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${authStore.token}` },
      body: fd,
    })
    if (resp.ok) {
      const data = await resp.json()
      // Cache-bust: el backend reescribe el mismo filename ({miembroId}.ext),
      // así que la URL no cambia y el navegador serviría la imagen cacheada.
      miembro.value.fotoUrl = `${data.fotoUrl}?t=${Date.now()}`
      // Si es la foto del usuario en sesión, refrescar el avatar del sidebar.
      if (miembro.value.id === authStore.user?.miembroId) {
        authStore.setUserFoto(data.fotoUrl)
      }
    }
  } catch (e) {
    console.error('Error subiendo foto:', e)
  }
  event.target.value = ''
}

const sexoOptions = [
  { value: 'H', label: 'Hombre' },
  { value: 'M', label: 'Mujer' },
  { value: 'X', label: 'Otro / no especificado' },
]

const tipoDocumentoOptions = [
  { value: 'DNI',       label: 'DNI' },
  { value: 'NIE',       label: 'NIE' },
  { value: 'NIF',       label: 'NIF' },
  { value: 'TIE',       label: 'TIE (Tarjeta Identidad Extranjero)' },
  { value: 'PASAPORTE', label: 'Pasaporte' },
  { value: 'OTRO',      label: 'Otro documento' },
]

// ── Cambiar contraseña ────────────────────────────────────────────────────────
const cambioPass = ref({ activo: false, actual: '', nueva: '', repetir: '', error: '', ok: '' })
const guardandoPass = ref(false)

const CAMBIAR_MI_PASSWORD = gql`
  mutation CambiarMiPassword($passwordActual: String!, $nuevaPassword: String!) {
    cambiarMiPassword(passwordActual: $passwordActual, nuevaPassword: $nuevaPassword)
  }
`

async function guardarPassword() {
  cambioPass.value.error = ''
  cambioPass.value.ok = ''
  const { actual, nueva, repetir } = cambioPass.value
  if (!actual || !nueva || !repetir) { cambioPass.value.error = 'Completa todos los campos'; return }
  if (nueva !== repetir) { cambioPass.value.error = 'Las contraseñas nuevas no coinciden'; return }
  if (nueva.length < 8) { cambioPass.value.error = 'La nueva contraseña debe tener al menos 8 caracteres'; return }
  guardandoPass.value = true
  try {
    await graphqlClient.request(CAMBIAR_MI_PASSWORD, { passwordActual: actual, nuevaPassword: nueva })
    cambioPass.value.ok = 'Contraseña actualizada correctamente'
    cambioPass.value.actual = ''
    cambioPass.value.nueva = ''
    cambioPass.value.repetir = ''
    setTimeout(() => { cambioPass.value.activo = false; cambioPass.value.ok = '' }, 2000)
  } catch (e) {
    cambioPass.value.error = e?.response?.errors?.[0]?.message || 'Error al cambiar la contraseña'
  } finally {
    guardandoPass.value = false
  }
}

// ── Cuotas ────────────────────────────────────────────────────────────────────
const cuotas = ref([])
const loadingCuotas = ref(false)

const QUERY_CUOTAS_MIEMBRO = gql`
  query CuotasMiembro($miembroId: UUID!) {
    cuotasPorMiembro(miembroId: $miembroId) {
      id ejercicio importe importePagado fechaPago modoIngreso referenciaPago
      estado { id nombre color }
    }
  }
`

const cuotasOrdenadas = computed(() =>
  [...cuotas.value].sort((a, b) => b.ejercicio - a.ejercicio)
)

// Cuota más reciente del socio: el importe que se le aplica actualmente.
const cuotaVigente = computed(() => cuotasOrdenadas.value[0] || null)

function formatEuros(val) {
  if (val == null) return '—'
  return Number(val).toLocaleString('es-ES', { style: 'currency', currency: 'EUR' })
}

function badgeColorStyle(estado) {
  if (!estado?.color) return { background: '#f1f5f9', color: '#475569' }
  const hex = estado.color.replace('#', '')
  const r = parseInt(hex.slice(0,2),16), g = parseInt(hex.slice(2,4),16), b = parseInt(hex.slice(4,6),16)
  return { background: `rgba(${r},${g},${b},0.15)`, color: estado.color, border: `1px solid rgba(${r},${g},${b},0.3)` }
}

async function cargarCuotas(id = null) {
  const miembroId = id || miembro.value.id
  if (!miembroId) return
  loadingCuotas.value = true
  try {
    const r = await graphqlClient.request(QUERY_CUOTAS_MIEMBRO, { miembroId })
    cuotas.value = r.cuotasPorMiembro || []
  } finally {
    loadingCuotas.value = false
  }
}

// ── Solicitud de reducción de cuota ───────────────────────────────────────────
const solicitudesReduccion = ref([])  // historial completo de solicitudes del miembro
const modalReduccion = ref({ visible: false, motivoId: null, texto: '', archivos: [], guardando: false, error: '' })

const QUERY_SOLICITUDES_REDUCCION = gql`
  query SolicitudesReduccion($miembroId: UUID!) {
    solicitudesReduccionCuota(filter: { miembroId: { eq: $miembroId }, eliminado: { eq: false } }) {
      id estado ejercicio fechaPresentacion fechaResolucion motivoRechazo
      motivoReduccion { id nombre porcentajeReduccion }
    }
  }
`
const MUTATION_PRESENTAR_REDUCCION = gql`
  mutation PresentarReduccion($miembroId: UUID!, $motivoReduccionId: UUID!, $texto: String) {
    presentarSolicitudReduccionCuota(miembroId: $miembroId, motivoReduccionId: $motivoReduccionId, textoSolicitud: $texto)
  }
`
const MUTATION_ANULAR_REDUCCION = gql`
  mutation AnularReduccion($id: UUID!) {
    anularSolicitudReduccionCuota(solicitudId: $id)
  }
`

// El socio puede solicitar reducción desde /mis-datos si no tiene ya una pendiente.
const solicitudPendiente = computed(() =>
  solicitudesReduccion.value.find(s => s.estado === 'PRESENTADA') || null
)
const puedeSolicitarReduccion = computed(() =>
  props.modoPropio && !isCreateMode.value && !solicitudPendiente.value
)
// Etiqueta que deja claro quién tramitó la solicitud y en qué quedó.
const ETIQUETA_ESTADO_SOLICITUD = {
  PRESENTADA: 'Pendiente de revisión por tesorería',
  APROBADA:   'Aprobada por tesorería',
  RECHAZADA:  'Rechazada por tesorería',
  ANULADA:    'Anulada por el socio',
}
const etiquetaEstadoSolicitud = (estado) => ETIQUETA_ESTADO_SOLICITUD[estado] || estado
const claseEstadoSolicitud = (estado) => ({
  APROBADA:   'border-green-200 bg-green-50 text-green-800',
  RECHAZADA:  'border-red-200 bg-red-50 text-red-800',
  PRESENTADA: 'border-amber-200 bg-amber-50 text-amber-800',
  ANULADA:    'border-slate-200 bg-slate-50 text-slate-500',
}[estado] || 'border-slate-200 bg-slate-50 text-slate-600')

const fechaCorta = (d) =>
  d ? new Intl.DateTimeFormat('es-ES').format(new Date(d + 'T12:00:00')) : ''

async function cargarSolicitudReduccion(id = null) {
  const miembroId = id || miembro.value.id
  if (!miembroId) return
  try {
    const r = await graphqlClient.request(QUERY_SOLICITUDES_REDUCCION, { miembroId })
    solicitudesReduccion.value = (r.solicitudesReduccionCuota || [])
      .slice().sort((a, b) => (b.fechaPresentacion || '').localeCompare(a.fechaPresentacion || ''))
  } catch (e) {
    console.error('Error cargando solicitudes de reducción:', e?.message || e)
  }
}

function abrirModalReduccion() {
  modalReduccion.value = { visible: true, motivoId: null, texto: '', archivos: [], guardando: false, error: '' }
}

async function presentarReduccion() {
  const m = modalReduccion.value
  m.error = ''
  if (!m.motivoId) { m.error = 'Selecciona un motivo de reducción.'; return }
  if (!miembro.value.id) { m.error = 'No se ha podido determinar el miembro.'; return }
  m.guardando = true
  try {
    const data = await graphqlClient.request(MUTATION_PRESENTAR_REDUCCION, {
      miembroId: miembro.value.id,
      motivoReduccionId: m.motivoId,
      texto: m.texto || null,
    })
    const solicitudId = data.presentarSolicitudReduccionCuota
    if (solicitudId && m.archivos.length) {
      const authStore = useAuthStore()
      for (const file of m.archivos) {
        const fd = new FormData()
        fd.append('file', file)
        await fetch(`/api/upload/solicitudes-reduccion/${solicitudId}/documentos`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${authStore.token}` },
          body: fd,
        })
      }
    }
    modalReduccion.value.visible = false
    await cargarSolicitudReduccion()
  } catch (e) {
    m.error = e?.response?.errors?.[0]?.message || 'No se pudo enviar la solicitud.'
  } finally {
    m.guardando = false
  }
}

async function anularReduccion(solicitud) {
  if (!solicitud?.id) return
  try {
    await graphqlClient.request(MUTATION_ANULAR_REDUCCION, { id: solicitud.id })
    await cargarSolicitudReduccion()
  } catch (e) {
    toast.error(e?.response?.errors?.[0]?.message || 'No se pudo anular la solicitud.')
  }
}

// ── Modificación (incremento voluntario) de cuota ─────────────────────────────
const modalIncremento = ref({ visible: false, incremento: 0, observaciones: '', guardando: false, error: '' })

const incrementoCuotaActual = computed(() => Number(miembro.value?.incrementoCuota) || 0)
const anioEnCurso = new Date().getFullYear()

// Cuota base efectiva = importe vigente menos el incremento ya aplicado.
const cuotaBaseEfectiva = computed(() => {
  if (!cuotaVigente.value) return null
  return Math.max(0, Number(cuotaVigente.value.importe) - incrementoCuotaActual.value)
})
// Total resultante con el incremento que se está editando en el modal.
const cuotaTotalConIncremento = computed(() => {
  if (cuotaBaseEfectiva.value == null) return null
  return cuotaBaseEfectiva.value + (Number(modalIncremento.value.incremento) || 0)
})

// El socio puede aumentar su cuota desde /mis-datos; un gestor de cuotas también.
const puedeModificarCuota = computed(() =>
  (props.modoPropio || tienePermiso('CUOT_LIST')) && !isCreateMode.value
)

const MUTATION_MODIFICAR_INCREMENTO = gql`
  mutation ModificarIncremento($miembroId: UUID!, $incremento: Decimal!, $observaciones: String) {
    modificarIncrementoCuota(miembroId: $miembroId, incremento: $incremento, observaciones: $observaciones)
  }
`

function abrirModalIncremento() {
  modalIncremento.value = {
    visible: true,
    incremento: incrementoCuotaActual.value,
    observaciones: miembro.value?.incrementoCuotaObs || '',
    guardando: false,
    error: '',
  }
}

async function guardarIncremento() {
  const m = modalIncremento.value
  m.error = ''
  if (!miembro.value.id) { m.error = 'No se ha podido determinar el miembro.'; return }
  const inc = Math.round(Number(m.incremento))
  if (!(inc >= 0)) { m.error = 'Indica un incremento válido (0 o mayor).'; return }
  m.guardando = true
  try {
    await graphqlClient.request(MUTATION_MODIFICAR_INCREMENTO, {
      miembroId: miembro.value.id,
      incremento: String(inc),
      observaciones: m.observaciones || null,
    })
    miembro.value.incrementoCuota = inc
    miembro.value.incrementoCuotaObs = m.observaciones || null
    modalIncremento.value.visible = false
    await cargarCuotas()
  } catch (e) {
    m.error = e?.response?.errors?.[0]?.message || 'No se pudo guardar la modificación.'
  } finally {
    m.guardando = false
  }
}

// ── RGPD / privacidad ─────────────────────────────────────────────────────────
// Periodo legal de conservación de datos tras la baja (años). A futuro será
// configurable desde el módulo transversal de RGPD.
const ANIOS_RETENCION = 6

// Límite de conservación = fecha de baja + ANIOS_RETENCION. Solo lectura.
const fechaLimiteRetencion = computed(() => {
  const fb = miembro.value?.fechaBaja
  if (!fb) return null
  const d = new Date(fb + 'T12:00:00')
  d.setFullYear(d.getFullYear() + ANIOS_RETENCION)
  return d.toISOString().slice(0, 10)
})

// Al marcar la solicitud de supresión, se fecha automáticamente con la de hoy.
watch(() => miembro.value?.solicitaSupresionDatos, (val) => {
  if (val && miembro.value && !miembro.value.fechaSolicitudSupresion) {
    miembro.value.fechaSolicitudSupresion = new Date().toISOString().slice(0, 10)
  }
})

// La anonimización solo es posible sobre un miembro de baja y no anonimizado,
// y nunca desde /mis-datos (no es una acción del propio socio).
const puedeAnonimizar = computed(() =>
  !isCreateMode.value && !props.modoPropio
  && !!miembro.value?.fechaBaja && !miembro.value?.datosAnonimizados
)

const modalAnonimizar = ref(false)
const anonimizando = ref(false)
const anonimizarError = ref('')

const MUTATION_ANONIMIZAR = gql`
  mutation AnonimizarMiembro($miembroId: UUID!) {
    anonimizarMiembro(miembroId: $miembroId) { id }
  }
`

async function confirmarAnonimizar() {
  anonimizarError.value = ''
  anonimizando.value = true
  try {
    await graphqlClient.request(MUTATION_ANONIMIZAR, { miembroId: miembro.value.id })
    modalAnonimizar.value = false
    await fetchMiembro(miembro.value.id)
  } catch (e) {
    anonimizarError.value = e?.response?.errors?.[0]?.message || 'No se pudo anonimizar.'
  } finally {
    anonimizando.value = false
  }
}

// ── Habilidades ───────────────────────────────────────────────────────────────
const miembroHabilidades = ref([])
const habilidadesCatalogo = ref([])
const loadingHabilidades = ref(false)
const mostrarFormHabilidad = ref(false)
const nuevaHabilidad = ref({ habilidadId: '', nivelId: '' })

const habilidadesAgrupadas = computed(() => {
  const grupos = new Map()
  for (const h of habilidadesCatalogo.value) {
    const key = h.categoriaId ?? '__sin_categoria__'
    const label = h.categoria?.nombre ?? 'Sin categoría'
    if (!grupos.has(key)) grupos.set(key, { categoriaId: key, categoriaNombre: label, habilidades: [] })
    grupos.get(key).habilidades.push(h)
  }
  return [...grupos.values()].sort((a, b) => a.categoriaNombre.localeCompare(b.categoriaNombre))
})

const QUERY_HABILIDADES_MIEMBRO = gql`
  query MiembroHabilidades($miembroId: UUID!) {
    miembrosHabilidades(filter: { miembroId: { eq: $miembroId } }) {
      id miembroId nivelId validado
      habilidad { id nombre categoria { id nombre } }
      nivelHabilidad { id nombre }
    }
  }
`
const QUERY_HABILIDADES_CATALOGO = gql`
  query Habilidades { habilidades(filter: { activo: { eq: true } }) { id nombre categoriaId categoria { id nombre } } }
`
const MUTATION_CREATE_HABILIDAD = gql`
  mutation CrearMiembroHabilidad($data: MiembroHabilidadCreateInput!) {
    crearMiembroHabilidad(data: $data) { id }
  }
`
const MUTATION_DELETE_HABILIDAD = gql`
  mutation EliminarMiembroHabilidades($filter: MiembroHabilidadFilter!) {
    eliminarMiembrosHabilidad(filter: $filter) { id }
  }
`

async function cargarHabilidades(id = null) {
  const miembroId = id || miembro.value.id
  if (!miembroId) return
  loadingHabilidades.value = true
  try {
    const [r1, r2] = await Promise.all([
      graphqlClient.request(QUERY_HABILIDADES_MIEMBRO, { miembroId }),
      graphqlClient.request(QUERY_HABILIDADES_CATALOGO),
    ])
    miembroHabilidades.value = r1.miembrosHabilidades || []
    habilidadesCatalogo.value = r2.habilidades || []
  } finally {
    loadingHabilidades.value = false
  }
}

async function guardarHabilidad() {
  if (!nuevaHabilidad.value.habilidadId || !miembro.value.id) return
  await graphqlClient.request(MUTATION_CREATE_HABILIDAD, {
    data: {
      miembroId: miembro.value.id,
      habilidadId: nuevaHabilidad.value.habilidadId,
      nivelId: nuevaHabilidad.value.nivelId || null,
      validado: false,
    },
  })
  mostrarFormHabilidad.value = false
  nuevaHabilidad.value = { habilidadId: '', nivelId: '' }
  await cargarHabilidades()
}

async function eliminarHabilidad(id) {
  await graphqlClient.request(MUTATION_DELETE_HABILIDAD, { filter: { id: { eq: id } } })
  await cargarHabilidades()
}

// ── Franjas de disponibilidad ─────────────────────────────────────────────────
const franjas = ref([])
const loadingFranjas = ref(false)
const mostrarFormFranja = ref(false)
const nuevaFranja = ref({ diaSemana: 0, horaInicio: '', horaFin: '' })
const diasSemana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
const diasSemanaLargo = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

const franjasPorDia = computed(() => {
  const grupos = {}
  for (const f of franjas.value) {
    if (!grupos[f.diaSemana]) grupos[f.diaSemana] = []
    grupos[f.diaSemana].push(f)
  }
  return grupos
})

const QUERY_FRANJAS = gql`
  query Franjas($miembroId: UUID!) {
    franjasDisponibilidad(filter: { miembroId: { eq: $miembroId }, activa: { eq: true } }) {
      id diaSemana horaInicio horaFin notas activa
    }
  }
`
const MUTATION_CREATE_FRANJA = gql`
  mutation CrearFranja($data: FranjaDisponibilidadCreateInput!) {
    crearFranjaDisponibilidad(data: $data) { id }
  }
`
const MUTATION_DELETE_FRANJA = gql`
  mutation EliminarFranjas($filter: FranjaDisponibilidadFilter!) {
    eliminarFranjasDisponibilidad(filter: $filter) { id }
  }
`

async function cargarFranjas(id = null) {
  const miembroId = id || miembro.value.id
  if (!miembroId) return
  loadingFranjas.value = true
  try {
    const r = await graphqlClient.request(QUERY_FRANJAS, { miembroId })
    franjas.value = (r.franjasDisponibilidad || []).sort(
      (a, b) => a.diaSemana - b.diaSemana || a.horaInicio.localeCompare(b.horaInicio)
    )
  } finally {
    loadingFranjas.value = false
  }
}

function abrirFormFranja(dia) {
  nuevaFranja.value = { diaSemana: dia, horaInicio: '', horaFin: '' }
  mostrarFormFranja.value = true
}

async function guardarFranja() {
  if (!nuevaFranja.value.horaInicio || !nuevaFranja.value.horaFin || !miembro.value.id) return
  await graphqlClient.request(MUTATION_CREATE_FRANJA, {
    data: {
      miembroId: miembro.value.id,
      diaSemana: nuevaFranja.value.diaSemana,
      horaInicio: nuevaFranja.value.horaInicio,
      horaFin: nuevaFranja.value.horaFin,
      activa: true,
    },
  })
  mostrarFormFranja.value = false
  nuevaFranja.value = { diaSemana: 0, horaInicio: '', horaFin: '' }
  await cargarFranjas()
}

async function eliminarFranja(id) {
  await graphqlClient.request(MUTATION_DELETE_FRANJA, { filter: { id: { eq: id } } })
  await cargarFranjas()
}

// ── Acceso y roles ────────────────────────────────────────────────────────────
const rolesDisponibles = ref([])
const loadingRoles = ref(false)
const nuevoRolId = ref('')
const nuevoRolAgrupacionId = ref('')
const guardandoRol = ref(false)
const errorRol = ref('')

const QUERY_ROLES = gql`
  query RolesParaAsignar {
    roles(filter: { activo: { eq: true } }) {
      id codigo nombre tipo
    }
  }
`
const MUTATION_ASIGNAR_ROL = gql`
  mutation AsignarRolUsuario($usuarioId: UUID!, $rolId: UUID!, $agrupacionId: UUID) {
    asignarRolUsuario(usuarioId: $usuarioId, rolId: $rolId, agrupacionId: $agrupacionId)
  }
`
const MUTATION_REVOCAR_ROL = gql`
  mutation RevocarRolUsuario($usuarioId: UUID!, $rolId: UUID!) {
    revocarRolUsuario(usuarioId: $usuarioId, rolId: $rolId)
  }
`

async function cargarRolesDisponibles() {
  if (rolesDisponibles.value.length) return
  loadingRoles.value = true
  try {
    const r = await graphqlClient.request(QUERY_ROLES)
    rolesDisponibles.value = (r.roles || []).sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
  } finally {
    loadingRoles.value = false
  }
}

async function asignarRol() {
  if (!nuevoRolId.value || !miembro.value.usuario?.id) return
  guardandoRol.value = true
  errorRol.value = ''
  try {
    await graphqlClient.request(MUTATION_ASIGNAR_ROL, {
      usuarioId: miembro.value.usuario.id,
      rolId: nuevoRolId.value,
      agrupacionId: nuevoRolAgrupacionId.value || null,
    })
    nuevoRolId.value = ''
    nuevoRolAgrupacionId.value = ''
    await fetchMiembro(miembro.value.id)
  } catch (e) {
    errorRol.value = e?.response?.errors?.[0]?.message || 'Error al asignar rol'
  } finally {
    guardandoRol.value = false
  }
}

async function revocarRol(rolId) {
  if (!miembro.value.usuario?.id) return
  try {
    await graphqlClient.request(MUTATION_REVOCAR_ROL, {
      usuarioId: miembro.value.usuario.id,
      rolId,
    })
    await fetchMiembro(miembro.value.id)
  } catch (e) {
    errorRol.value = e?.response?.errors?.[0]?.message || 'Error al revocar rol'
  }
}

const rolesAsignados = computed(() => miembro.value.usuario?.roles || [])

// ── Modal crear cuenta desde acceso ──────────────────────────────────────────
const modalCuenta = ref({ abierto: false, email: '', enviarEmail: true, cargando: false, error: '' })

function abrirModalCuenta() {
  modalCuenta.value = {
    abierto: true,
    email: miembro.value.email || '',
    enviarEmail: true,
    cargando: false,
    error: '',
  }
}

async function crearCuentaDesdeTab() {
  if (!modalCuenta.value.email) return
  modalCuenta.value.cargando = true
  modalCuenta.value.error = ''
  try {
    await graphqlClient.request(CREAR_USUARIO_GQL, {
      email: modalCuenta.value.email,
      miembroId: miembro.value.id,
      enviarEmailBienvenida: modalCuenta.value.enviarEmail,
    })
    modalCuenta.value.abierto = false
    await fetchMiembro(miembro.value.id)
  } catch (e) {
    modalCuenta.value.error = e?.response?.errors?.[0]?.message || 'Error al crear la cuenta'
  } finally {
    modalCuenta.value.cargando = false
  }
}

// ── Historial de nombramientos ────────────────────────────────────────────────
const nombramientos = ref([])
const loadingNombramientos = ref(false)

const QUERY_NOMBRAMIENTOS = gql`
  query NombramientosMiembro($miembroId: UUID!) {
    historialNombramientos(filter: { miembroId: { eq: $miembroId } }) {
      id fechaInicio fechaFin estado tipoOrigen motivo observaciones
      rol { id nombre tipo }
      agrupacion { id nombre }
    }
  }
`

async function cargarNombramientos(id = null) {
  const miembroId = id || miembro.value.id
  if (!miembroId) return
  loadingNombramientos.value = true
  try {
    const r = await graphqlClient.request(QUERY_NOMBRAMIENTOS, { miembroId })
    nombramientos.value = (r.historialNombramientos || []).sort(
      (a, b) => (b.fechaInicio || '').localeCompare(a.fechaInicio || '')
    )
  } finally {
    loadingNombramientos.value = false
  }
}

// ── Sugerencia de agrupación por provincia ────────────────────────────────────
const mostrarModalAgrupacion = ref(false)

const agrupacionesSugeridas = computed(() => {
  if (!miembro.value.provinciaId) return catalogos.value.agrupaciones
  const provincia = catalogos.value.provincias.find(p => p.id === miembro.value.provinciaId)
  if (!provincia) return catalogos.value.agrupaciones
  const termino = provincia.nombre.toLowerCase()
  const coinciden = catalogos.value.agrupaciones.filter(a =>
    a.nombre.toLowerCase().includes(termino) ||
    (a.nombreCorto && a.nombreCorto.toLowerCase().includes(termino))
  )
  return coinciden.length > 0 ? coinciden : catalogos.value.agrupaciones
})

watch(() => miembro.value.provinciaId, (newVal) => {
  if (newVal && !miembro.value.agrupacionId && (editMode.value || isCreateMode.value)) {
    nextTick(() => { mostrarModalAgrupacion.value = true })
  }
})

watch(esPaypal, (isPaypal) => {
  if (isPaypal && !miembro.value.referenciaPago && miembro.value.email) {
    miembro.value.referenciaPago = miembro.value.email
  }
})

const handleCancel = () => {
  if (isCreateMode.value) {
    if (window.history.state?.back) router.back()
    else router.push('/miembros')
    return
  }
  if (originalSnapshot.value) {
    miembro.value = structuredClone(originalSnapshot.value)
  }
  // En modoPropio la ficha sigue siendo editable; solo se descartan los cambios.
  if (!props.modoPropio) editMode.value = false
}

const CREAR_USUARIO_GQL = `
  mutation CrearUsuario($email: String!, $miembroId: UUID, $enviarEmailBienvenida: Boolean) {
    crearUsuario(
      email: $email
      activo: false
      miembroId: $miembroId
      enviarEmailBienvenida: $enviarEmailBienvenida
    ) { id }
  }
`

const handleSave = async () => {
  try {
    if (isCreateMode.value) {
      const created = await saveMiembro()
      if (created?.id) {
        if (crearCuenta.value && miembro.value.email) {
          try {
            await graphqlClient.request(CREAR_USUARIO_GQL, {
              email: miembro.value.email,
              miembroId: created.id,
              enviarEmailBienvenida: true,
            })
          } catch (e) {
            console.warn('No se pudo crear la cuenta de acceso:', e?.message)
          }
        }
        router.push(`/miembros/${created.id}`)
      }
    } else {
      await saveMiembro()
      saveMessage.value = 'Ficha de militancia actualizada correctamente.'
      // En modoPropio la ficha permanece editable tras guardar.
      if (!props.modoPropio) editMode.value = false
      originalSnapshot.value = JSON.parse(JSON.stringify(miembro.value))
      window.setTimeout(() => { saveMessage.value = '' }, 3000)
    }
  } catch {
    saveMessage.value = ''
  }
}

const originalSnapshot = ref(null)

const toggleEditMode = () => {
  if (!editMode.value) {
    originalSnapshot.value = JSON.parse(JSON.stringify(miembro.value))
    editMode.value = true
    saveMessage.value = ''
    return
  }
  if (originalSnapshot.value) {
    miembro.value = JSON.parse(JSON.stringify(originalSnapshot.value))
  }
  editMode.value = false
}

onMounted(async () => {
  await loadCatalogos()
  if (isCreateMode.value && !props.miembroIdProp) {
    const espana = catalogos.value.paises.find(p => p.codigo === 'ES')
    if (espana) miembro.value.paisDomicilioId = espana.id
    const estadoAlta = catalogos.value.estadosMiembro.find(e => e.nombre.toLowerCase() === 'alta')
    if (estadoAlta) miembro.value.estadoId = estadoAlta.id
    return
  }
  const resolvedId = props.miembroIdProp || route.params.id
  if (resolvedId) {
    await Promise.all([fetchMiembro(resolvedId), cargarHabilidades(resolvedId), cargarFranjas(resolvedId), cargarNombramientos(resolvedId), cargarCuotas(resolvedId), cargarSolicitudReduccion(resolvedId)])
    if (!props.modoPropio) await cargarRolesDisponibles()
    if (route.query.modo === 'editar') editMode.value = true
    // modoPropio entra ya en edición: guardamos el snapshot para poder descartar.
    if (props.modoPropio) originalSnapshot.value = JSON.parse(JSON.stringify(miembro.value))
  }
})

// ── Componentes de campo inline ───────────────────────────────────────────────

const FieldText = defineComponent({
  props: {
    modelValue: { type: [String, Number], default: '' },
    label: { type: String, required: true },
    type: { type: String, default: 'text' },
    editMode: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    return () => h('div', [
      h('label', { class: 'block text-xs font-medium text-gray-600 mb-1' }, props.label),
      props.editMode
        ? h('input', {
            class: 'mt-0.5 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/30',
            type: props.type,
            value: props.modelValue ?? '',
            onInput: (e) => emit('update:modelValue', e.target.value),
          })
        : h('div', { class: 'mt-0.5 px-0 py-1.5 text-sm text-gray-900 min-h-[34px]' }, formatDisplay(props.modelValue)),
    ])
  },
})

const FieldTextarea = defineComponent({
  props: {
    modelValue: { type: String, default: '' },
    label: { type: String, required: true },
    rows: { type: [Number, String], default: 4 },
    editMode: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    return () => h('div', [
      h('label', { class: 'block text-xs font-medium text-gray-600 mb-1' }, props.label),
      props.editMode
        ? h('textarea', {
            class: 'mt-0.5 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/30',
            rows: props.rows,
            value: props.modelValue ?? '',
            onInput: (e) => emit('update:modelValue', e.target.value),
          })
        : h('div', { class: 'mt-0.5 py-1.5 text-sm text-gray-900 min-h-[60px] whitespace-pre-wrap' }, formatDisplay(props.modelValue)),
    ])
  },
})

const FieldSelect = defineComponent({
  props: {
    modelValue: { default: null },
    label: { type: String, default: '' },
    options: { type: Array, default: () => [] },
    optionLabel: { type: String, default: 'label' },
    optionValue: { type: String, default: 'value' },
    emptyLabel: { type: String, default: 'Sin especificar' },
    editMode: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const displayValue = computed(() => {
      const current = props.options.find((item) => item?.[props.optionValue] === props.modelValue)
      return current?.[props.optionLabel] || props.emptyLabel
    })
    return () => h('div', [
      props.label ? h('label', { class: 'block text-xs font-medium text-gray-600 mb-1' }, props.label) : null,
      props.editMode
        ? h('select', {
            class: 'mt-0.5 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/30',
            value: props.modelValue ?? '',
            onChange: (e) => emit('update:modelValue', e.target.value || null),
          }, [
            h('option', { value: '' }, props.emptyLabel),
            ...props.options.map((item) =>
              h('option', { value: item?.[props.optionValue] }, item?.[props.optionLabel] || ''),
            ),
          ])
        : h('div', { class: 'mt-0.5 py-1.5 text-sm text-gray-900 min-h-[34px]' }, displayValue.value),
    ])
  },
})

const FieldCheckbox = defineComponent({
  props: {
    modelValue: { type: Boolean, default: false },
    label: { type: String, required: true },
    editMode: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    return () => h('label', {
      class: [
        'flex items-center gap-2 rounded-lg px-3 py-2.5 min-h-[42px] text-sm',
        props.modelValue ? 'bg-purple-50 border border-purple-200 text-purple-800' : 'bg-gray-50 border border-gray-200 text-gray-700'
      ]
    }, [
      h('input', {
        type: 'checkbox',
        class: 'rounded border-gray-300 text-purple-600 focus:ring-purple-500',
        checked: props.modelValue,
        disabled: !props.editMode,
        onChange: (e) => emit('update:modelValue', e.target.checked),
      }),
      h('span', {}, props.label),
    ])
  },
})

function formatDisplay(value) {
  return value === null || value === undefined || value === '' ? '—' : String(value)
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })
}

function agrupacionNombre(agrupacionId) {
  if (!agrupacionId) return null
  return catalogos.value.agrupaciones.find(a => a.id === agrupacionId)?.nombre || agrupacionId
}

const _tipoRolColors = {
  SISTEMA:       'bg-gray-100 text-gray-600',
  ORGANIZACION:  'bg-blue-100 text-blue-700',
  TERRITORIAL:   'bg-teal-100 text-teal-700',
  FUNCIONAL:     'bg-purple-100 text-purple-700',
  PERSONALIZADO: 'bg-amber-100 text-amber-700',
}
function tipoRolClass(tipo) {
  return _tipoRolColors[tipo] || 'bg-gray-100 text-gray-600'
}
</script>
