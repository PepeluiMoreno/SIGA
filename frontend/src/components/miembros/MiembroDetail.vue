<template>
  <!-- ── Cabecera ──────────────────────────────────────────────────── -->
  <DetailHeader v-if="!modoPropio" fallback="/miembros">
    <button v-if="!isCreateMode && miembro.id" @click="toggleEditMode"
      :class="editMode ? 'text-gray-500 hover:text-gray-700' : 'text-purple-600 hover:text-purple-800'"
      class="text-sm font-medium transition-colors">
      {{ editMode ? 'Cancelar edición' : 'Editar' }}
    </button>
  </DetailHeader>

  <!-- ── Modal: sugerencia de agrupación ─────────────────────────── -->
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

  <!-- ── Tarjeta de contenido ─────────────────────────────────────── -->
  <div class="bg-white rounded-xl shadow-sm border border-gray-200">

    <div v-if="loading" class="p-12 text-center">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-purple-600 border-t-transparent mb-3"></div>
      <p class="text-gray-500 text-sm">{{ isCreateMode ? 'Preparando formulario...' : `Cargando datos del ${orgConfig.miembro}...` }}</p>
    </div>

    <div v-else-if="error" class="p-8 text-center">
      <p class="text-red-600 font-medium">{{ error }}</p>
      <DetailHeader fallback="/miembros" />
    </div>

    <div v-else>
      <!-- Banner de guardado -->
      <div v-if="saveMessage"
        class="mx-6 mt-4 rounded-lg bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-800 flex items-center gap-2">
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
        </svg>
        {{ saveMessage }}
      </div>

      <!-- Tabs -->
      <div class="border-b border-gray-200 px-6">
        <nav class="-mb-px flex overflow-x-auto">
          <button
            v-for="tab in availableTabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'whitespace-nowrap pb-3 pt-4 px-4 border-b-2 text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'border-purple-500 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]">
            {{ tab.name }}
          </button>
        </nav>
      </div>

      <!-- Contenido de tabs -->
      <div class="p-6">

        <!-- ── DATOS PERSONALES ── -->
        <div v-show="activeTab === 'personal'" class="space-y-5">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">

            <section class="space-y-4 rounded-xl border border-gray-200 p-5">
              <h3 class="text-xs font-semibold uppercase tracking-widest text-purple-600">Identificación</h3>

              <!-- Foto de perfil -->
              <div class="flex items-center gap-4 mb-2">
                <AvatarImg
                  :src="miembro.fotoUrl"
                  :nombre="miembro.nombre"
                  :apellido="miembro.apellido1"
                  size="xl"
                />
                <div v-if="puedeEditarFoto" class="flex flex-col gap-1">
                  <label class="inline-flex items-center gap-1.5 h-8 px-3 text-xs font-medium text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-lg cursor-pointer hover:bg-indigo-100 transition-colors">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
                    </svg>
                    Cambiar foto
                    <input type="file" accept="image/*" class="hidden" @change="subirFoto" />
                  </label>
                  <p class="text-xs text-slate-400">JPG, PNG, WebP · máx. 5 MB</p>
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <FieldText v-model="miembro.nombre" label="Nombre *" :edit-mode="editMode || isCreateMode" />
                <FieldText v-model="miembro.apellido1" label="Primer apellido *" :edit-mode="editMode || isCreateMode" />
                <FieldText v-model="miembro.apellido2" label="Segundo apellido" :edit-mode="editMode || isCreateMode" />
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
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
            </section>

            <section class="space-y-4 rounded-xl border border-gray-200 p-5">
              <h3 class="text-xs font-semibold uppercase tracking-widest text-purple-600">Contacto</h3>
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
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
            </section>
          </div>

          <section class="rounded-xl border border-gray-200 p-5">
            <FieldTextarea v-model="miembro.observaciones" label="Observaciones" :edit-mode="editMode || isCreateMode" rows="4" />
          </section>
        </div>

        <!-- ── MEMBRESÍA ── -->
        <div v-show="activeTab === 'membresia'" class="space-y-5">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">

            <section class="space-y-4 rounded-xl border border-gray-200 p-5">
              <h3 class="text-xs font-semibold uppercase tracking-widest text-purple-600">Situación</h3>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <FieldSelect v-model="miembro.tipoMiembroId" :label="`Tipo de ${orgConfig.miembro} *`" :edit-mode="editMode || isCreateMode"
                  :options="catalogos.tiposMiembro" option-label="nombre" option-value="id" />
                <FieldSelect v-model="miembro.estadoId" label="Estado *" :edit-mode="editMode || isCreateMode"
                  :options="catalogos.estadosMiembro" option-label="nombre" option-value="id" />
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <FieldText v-model="miembro.fechaAlta" label="Fecha de alta *" type="date" :edit-mode="editMode || isCreateMode" />
                <FieldSelect v-model="miembro.agrupacionId" label="Agrupación territorial" :edit-mode="editMode || isCreateMode"
                  :options="catalogos.agrupaciones" option-label="nombre" option-value="id" empty-label="Sin asignar" />
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 border-t border-gray-100">
                <FieldCheckbox v-model="miembro.esVoluntario" label="Dispuesto/a a participar en actividades de la asociación" :edit-mode="editMode || isCreateMode" />
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

              <!-- Sección de baja: visible solo cuando el estado contiene "baja" -->
              <template v-if="estadoEsBaja">
                <div class="pt-3 border-t border-red-100 space-y-4">
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <FieldText v-model="miembro.fechaBaja" label="Fecha de baja" type="date" :edit-mode="editMode || isCreateMode" />
                    <FieldSelect v-model="miembro.motivoBajaId" label="Motivo de baja" :edit-mode="editMode || isCreateMode"
                      :options="catalogos.motivosBaja" option-label="nombre" option-value="id" empty-label="Sin especificar" />
                  </div>
                  <FieldText v-model="miembro.motivoBajaTexto" label="Observaciones de baja" :edit-mode="editMode || isCreateMode" />
                </div>
              </template>
            </section>

            <section class="space-y-4 rounded-xl border border-gray-200 p-5">
              <h3 class="text-xs font-semibold uppercase tracking-widest text-purple-600">RGPD y privacidad</h3>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <FieldCheckbox v-model="miembro.solicitaSupresionDatos" label="Solicita supresión de datos" :edit-mode="editMode || isCreateMode" />
                <FieldCheckbox v-model="miembro.datosAnonimizados" label="Datos anonimizados" :edit-mode="editMode || isCreateMode" />
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <FieldText v-model="miembro.fechaSolicitudSupresion" label="Solicitud RGPD" type="date" :edit-mode="editMode || isCreateMode" />
                <FieldText v-model="miembro.fechaLimiteRetencion" label="Límite retención" type="date" :edit-mode="editMode || isCreateMode" />
                <FieldText v-model="miembro.fechaAnonimizacion" label="Anonimización" type="date" :edit-mode="editMode || isCreateMode" />
              </div>
            </section>
          </div>
        </div>

        <!-- ── PAGO DE CUOTAS ── -->
        <div v-show="activeTab === 'pagoCuotas'">
          <div class="flex gap-5 items-start">

            <!-- Izquierda: selector de forma de pago -->
            <section class="space-y-3 rounded-xl border border-gray-200 p-5 flex-shrink-0 w-80">
              <h3 class="text-xs font-semibold uppercase tracking-widest text-purple-600">Procedimiento pago cuotas</h3>
              <div v-if="editMode || isCreateMode" class="grid grid-cols-3 gap-2">
                <button
                  v-for="fp in catalogos.formasPago"
                  :key="fp.id"
                  type="button"
                  @click="miembro.formaPagoId = miembro.formaPagoId === fp.id ? null : fp.id"
                  :class="[
                    'relative flex flex-col items-center gap-2 rounded-xl border-2 px-2 py-4 text-center text-xs font-medium transition-all duration-150',
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

            <!-- Derecha: panel contextual según forma de pago -->
            <Transition
              enter-active-class="transition-all duration-200 ease-out"
              enter-from-class="opacity-0 translate-x-2"
              enter-to-class="opacity-100 translate-x-0"
              leave-active-class="transition-all duration-150 ease-in"
              leave-from-class="opacity-100 translate-x-0"
              leave-to-class="opacity-0 translate-x-2"
              mode="out-in"
            >
              <!-- Transferencia nacional -->
              <section v-if="esTransferencia && !esInternacional" key="transf" class="flex-1 space-y-4 rounded-xl border border-purple-100 bg-purple-50/40 p-5">
                <h3 class="text-xs font-semibold uppercase tracking-widest text-purple-600">Datos bancarios</h3>
                <div class="space-y-1">
                  <label class="block text-xs font-medium text-gray-600">IBAN</label>
                  <template v-if="editMode || isCreateMode">
                    <input
                      :value="ibanDisplay"
                      @input="onIbanInput"
                      @blur="ibanTouched = true"
                      type="text"
                      maxlength="40"
                      placeholder="ES91 2100 0418 4502 0005 1332"
                      autocomplete="off"
                      :class="[
                        'w-full border rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2',
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

              <!-- Transferencia internacional -->
              <section v-else-if="esInternacional" key="transf-int" class="flex-1 space-y-4 rounded-xl border border-purple-100 bg-purple-50/40 p-5">
                <h3 class="text-xs font-semibold uppercase tracking-widest text-purple-600">Datos bancarios internacionales</h3>
                <div class="space-y-1">
                  <label class="block text-xs font-medium text-gray-600">IBAN</label>
                  <template v-if="editMode || isCreateMode">
                    <input
                      :value="ibanDisplay"
                      @input="onIbanInput"
                      @blur="ibanTouched = true"
                      type="text"
                      maxlength="40"
                      placeholder="ES91 2100 0418 4502 0005 1332"
                      autocomplete="off"
                      :class="[
                        'w-full border rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2',
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

              <!-- Domiciliación SEPA -->
              <section v-else-if="esDomiciliacion" key="sepa" class="flex-1 space-y-4 rounded-xl border border-purple-100 bg-purple-50/40 p-5">
                <h3 class="text-xs font-semibold uppercase tracking-widest text-purple-600">Domiciliación bancaria</h3>
                <div class="space-y-1">
                  <label class="block text-xs font-medium text-gray-600">IBAN de la cuenta a cargar</label>
                  <template v-if="editMode || isCreateMode">
                    <input
                      :value="ibanDisplay"
                      @input="onIbanInput"
                      @blur="ibanTouched = true"
                      type="text"
                      maxlength="40"
                      placeholder="ES91 2100 0418 4502 0005 1332"
                      autocomplete="off"
                      :class="[
                        'w-full border rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2',
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

              <!-- PayPal -->
              <section v-else-if="esPaypal" key="paypal" class="flex-1 space-y-4 rounded-xl border border-blue-100 bg-blue-50/40 p-5">
                <h3 class="text-xs font-semibold uppercase tracking-widest text-blue-600">Cuenta PayPal</h3>
                <FieldText v-model="miembro.referenciaPago" label="Email / cuenta PayPal" :edit-mode="editMode || isCreateMode" />
                <p class="text-xs text-gray-400">Se enviará el cobro de la cuota a esta dirección PayPal.</p>
              </section>

              <!-- Tarjeta -->
              <section v-else-if="esTarjeta" key="tarjeta" class="flex-1 space-y-4 rounded-xl border border-gray-100 bg-gray-50/60 p-5">
                <h3 class="text-xs font-semibold uppercase tracking-widest text-gray-600">Tarjeta de pago</h3>
                <FieldText v-model="miembro.referenciaPago" label="Referencia / últimos 4 dígitos" :edit-mode="editMode || isCreateMode" />
                <p class="text-xs text-gray-400">Solo para referencia interna. No almacenamos datos completos de tarjeta.</p>
              </section>

              <!-- Sin datos adicionales (Efectivo, Otro, sin selección) -->
              <section v-else key="empty" class="flex-1 flex items-center justify-center rounded-xl border border-dashed border-gray-200 p-8 text-center">
                <div class="text-gray-400">
                  <p class="text-2xl mb-2" v-html="miembro.formaPagoId ? formaPagoIcono(formaPagoSeleccionada?.nombre) : '👆'"></p>
                  <p class="text-sm">{{ miembro.formaPagoId ? 'No se requieren datos adicionales' : 'Selecciona un procedimiento de cobro' }}</p>
                </div>
              </section>
            </Transition>

          </div>
        </div>

        <!-- ── CUOTAS (sección inferior del tab económico) ── -->
        <div v-show="activeTab === 'pagoCuotas'" v-if="!isCreateMode" class="mt-6">
          <div class="rounded-xl border border-gray-200 overflow-hidden">
            <div class="flex items-center gap-3 px-5 py-3 border-b border-gray-100 bg-gray-50">
              <span class="w-1.5 h-5 rounded-full bg-sky-500 shrink-0"></span>
              <h3 class="text-xs font-semibold uppercase tracking-widest text-gray-600">Historial de cuotas</h3>
            </div>
            <div v-if="loadingCuotas" class="px-5 py-6 text-center text-gray-400 text-sm">Cargando…</div>
            <div v-else-if="!cuotas.length" class="px-5 py-6 text-center text-gray-400 text-sm italic">Sin cuotas registradas</div>
            <table v-else class="min-w-full divide-y divide-gray-100 text-sm">
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
                    <span class="px-2 py-0.5 text-xs font-medium rounded-full"
                      :style="badgeColorStyle(c.estado)">
                      {{ c.estado?.nombre ?? '—' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- ── DISPONIBILIDAD Y PERFIL ── -->
        <!-- ── VOLUNTARIADO ── -->
        <div v-show="activeTab === 'voluntariado'" class="flex gap-5" style="height: calc(100vh - 320px)">

          <!-- Panel izquierdo: perfil -->
          <div class="flex-1 min-w-0 overflow-y-auto space-y-4 pr-1">
            <h3 class="text-xs font-semibold uppercase tracking-widest text-purple-600">Perfil voluntario</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <FieldText v-model="miembro.profesion" label="Profesión" :edit-mode="editMode || isCreateMode" />
              <FieldSelect v-model="miembro.nivelEstudiosId" label="Nivel de estudios"
                :options="catalogos.nivelesEstudios" option-label="nombre" option-value="id"
                empty-label="Sin especificar" :edit-mode="editMode || isCreateMode" />
            </div>
            <FieldTextarea v-model="miembro.intereses" label="Intereses" :edit-mode="editMode || isCreateMode" rows="3" />
            <FieldTextarea v-model="miembro.experienciaVoluntariado" label="Experiencia en voluntariado" :edit-mode="editMode || isCreateMode" rows="3" />
            <FieldTextarea v-model="miembro.observacionesVoluntariado" label="Observaciones de voluntariado" :edit-mode="editMode || isCreateMode" rows="3" />
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-1">
              <FieldCheckbox v-model="miembro.puedeConducir" label="Puede conducir" :edit-mode="editMode || isCreateMode" />
              <FieldCheckbox v-model="miembro.vehiculoPropio" label="Vehículo propio" :edit-mode="editMode || isCreateMode" />
              <FieldCheckbox v-model="miembro.disponibilidadViajar" label="Disponibilidad para viajar" :edit-mode="editMode || isCreateMode" />
            </div>
          </div>

          <div class="w-px bg-gray-200 flex-shrink-0"></div>

          <!-- Panel derecho: habilidades -->
          <div class="flex-1 min-w-0 overflow-y-auto space-y-3 pl-1">
            <div class="flex items-center justify-between">
              <h3 class="text-xs font-semibold uppercase tracking-widest text-indigo-600">Habilidades</h3>
              <button @click="mostrarFormHabilidad = !mostrarFormHabilidad"
                class="px-3 py-1.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700">
                + Añadir
              </button>
            </div>

            <div v-if="mostrarFormHabilidad" class="bg-indigo-50 border border-indigo-200 rounded-xl p-4 space-y-3">
              <div class="space-y-3">
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
              </div>
              <div class="flex gap-2 justify-end">
                <button @click="mostrarFormHabilidad = false; nuevaHabilidad = { habilidadId: '', nivelId: '' }"
                  class="px-3 py-1.5 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50">Cancelar</button>
                <button @click="guardarHabilidad" :disabled="!nuevaHabilidad.habilidadId"
                  class="px-3 py-1.5 text-sm text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50">Guardar</button>
              </div>
            </div>

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
          </div>
        </div>

        <!-- ── ACCESO Y ROLES ── -->
        <div v-show="activeTab === 'acceso'" class="space-y-5">

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

            <!-- Modal inline de creación de cuenta -->
            <div v-else class="rounded-xl border border-indigo-200 bg-indigo-50 p-6 space-y-4">
              <div class="flex items-center justify-between">
                <h3 class="text-sm font-semibold text-indigo-800">Crear cuenta de acceso</h3>
                <button type="button" @click="modalCuenta.abierto = false" class="text-gray-400 hover:text-gray-600 text-lg leading-none">&times;</button>
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
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
              <p v-if="modalCuenta.error" class="text-xs text-red-600">{{ modalCuenta.error }}</p>
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
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
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
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
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
                    <p v-if="cambioPass.error" class="text-xs text-red-600">{{ cambioPass.error }}</p>
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
                    <span :class="['text-xs px-2 py-0.5 rounded-full font-medium',
                      tipoRolClass(ur.rol.tipo)]">
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
                    class="flex-1 min-w-40 rounded-lg border border-gray-300 px-3 py-1.5 text-sm focus:border-purple-500 focus:ring-1 focus:ring-purple-500">
                    <option value="">Seleccionar rol…</option>
                    <optgroup v-for="tipo in ['FUNCIONAL','ORGANIZACION','SISTEMA','PERSONALIZADO']" :key="tipo"
                      :label="tipo">
                      <option v-for="r in rolesDisponibles.filter(r => r.tipo === tipo)"
                        :key="r.id" :value="r.id">{{ r.nombre }}</option>
                    </optgroup>
                  </select>
                  <select v-model="nuevoRolAgrupacionId"
                    class="flex-1 min-w-40 rounded-lg border border-gray-300 px-3 py-1.5 text-sm focus:border-purple-500 focus:ring-1 focus:ring-purple-500">
                    <option value="">Toda la organización</option>
                    <option v-for="a in catalogos.agrupaciones" :key="a.id" :value="a.id">{{ a.nombre }}</option>
                  </select>
                  <button @click="asignarRol" :disabled="!nuevoRolId || guardandoRol"
                    class="px-3 py-1.5 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700 disabled:opacity-50">
                    Asignar
                  </button>
                </div>
                <p v-if="errorRol" class="text-xs text-red-600">{{ errorRol }}</p>
              </div>
            </section>
          </template>
        </div>

        <!-- ── CARGOS / HISTORIAL DE NOMBRAMIENTOS ── -->
        <div v-show="activeTab === 'cargos'" class="space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-semibold text-gray-900">Historial de cargos y nombramientos</h3>
          </div>

          <div v-if="loadingNombramientos" class="text-center py-6 text-gray-400 text-sm">Cargando…</div>

          <div v-else-if="!nombramientos.length"
            class="rounded-xl border border-dashed border-gray-200 p-8 text-center text-sm text-gray-400">
            Sin nombramientos registrados.
          </div>

          <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <table class="min-w-full divide-y divide-gray-100 text-sm">
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
            </table>
          </div>
        </div>

        <!-- ── FRANJAS HORARIAS ── -->
        <!-- ── DISPONIBILIDAD ── -->
        <!-- ── DISPONIBILIDAD ── -->
        <div v-show="activeTab === 'franjas'" class="space-y-5">
          <section class="space-y-4 rounded-xl border border-gray-200 p-5">
            <h3 class="text-xs font-semibold uppercase tracking-widest text-purple-600">Resumen de disponibilidad</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <FieldText v-model="miembro.disponibilidad" label="Disponibilidad" :edit-mode="editMode || isCreateMode" />
              <FieldText v-model="miembro.horasDisponiblesSemana" label="Horas/semana" type="number" :edit-mode="editMode || isCreateMode" />
            </div>
          </section>

          <div v-if="loadingFranjas" class="text-center py-6 text-gray-400 text-sm">Cargando...</div>
          <div v-else class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2">
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

          <div v-if="mostrarFormFranja" class="bg-purple-50 border border-purple-200 rounded-xl p-4 space-y-3">
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Día</label>
                <select v-model="nuevaFranja.diaSemana"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500">
                  <option v-for="(dia, i) in diasSemana" :key="i" :value="i">{{ dia }}</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Hora inicio</label>
                <input v-model="nuevaFranja.horaInicio" type="time"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Hora fin</label>
                <input v-model="nuevaFranja.horaFin" type="time"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500" />
              </div>
            </div>
            <div class="flex gap-2 justify-end">
              <button @click="mostrarFormFranja = false; nuevaFranja = { diaSemana: 0, horaInicio: '', horaFin: '' }"
                class="px-3 py-1.5 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50">Cancelar</button>
              <button @click="guardarFranja" :disabled="!nuevaFranja.horaInicio || !nuevaFranja.horaFin"
                class="px-3 py-1.5 text-sm text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50">Guardar</button>
            </div>
          </div>

          <div v-if="!mostrarFormFranja" class="flex justify-end">
            <button @click="abrirFormFranja(0)"
              class="px-3 py-1.5 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700">
              + Añadir franja
            </button>
          </div>
        </div>

      </div>

      <!-- ── Barra de guardado ─────────────────────────────────────── -->
      <div v-if="editMode || isCreateMode"
        class="px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-xl flex justify-end gap-3">
        <button @click="handleCancel"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
          {{ isCreateMode ? 'Cancelar' : 'Cancelar cambios' }}
        </button>
        <button @click="handleSave" :disabled="loading || !formValido"
          class="px-5 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50">
          {{ isCreateMode ? 'Crear miembro' : 'Guardar cambios' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DetailHeader from '@/components/common/DetailHeader.vue'
import AvatarImg from '@/components/common/AvatarImg.vue'
import { gql } from 'graphql-request'
import { graphqlClient } from '@/graphql/client.js'
import { useMiembro } from '@/composables/useMiembro'
import { badgeStyle, bandStyle } from '@/utils/badge'
import { useOrgConfigStore } from '@/stores/orgConfig'
import { useAuthStore } from '@/stores/auth.js'
import { usePermisos } from '@/composables/usePermisos.js'

const props = defineProps({
  miembroIdProp: { type: String, default: null },
  modoPropio: { type: Boolean, default: false },
})

const route = useRoute()
const router = useRouter()
const orgConfig = useOrgConfigStore()
const { tienePermiso } = usePermisos()
const editMode = ref(false)
const activeTab = ref('personal')
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

const tabsAdmin = [
  { id: 'personal',    name: 'Datos personales' },
  { id: 'membresia',   name: 'Membresía' },
  { id: 'pagoCuotas',  name: 'Datos económicos' },
  { id: 'voluntariado', name: 'Voluntariado' },
  { id: 'franjas',     name: 'Disponibilidad' },
  { id: 'cargos',      name: 'Cargos' },
  { id: 'acceso',      name: 'Acceso y roles' },
]

const tabsPropio = [
  { id: 'personal',    name: 'Datos personales' },
  { id: 'acceso',      name: 'Acceso y roles' },
  { id: 'membresia',   name: 'Membresía' },
  { id: 'pagoCuotas',  name: 'Datos económicos' },
  { id: 'voluntariado', name: 'Voluntariado' },
  { id: 'franjas',     name: 'Disponibilidad' },
  { id: 'cargos',      name: 'Cargos' },
]

const availableTabs = computed(() => {
  const tabs = props.modoPropio ? tabsPropio : tabsAdmin
  const excluirSiNuevo = ['franjas', 'cargos', 'acceso']
  const excluirSiNoVoluntario = ['voluntariado', 'franjas']
  return tabs.filter(t => {
    if (isCreateMode.value && excluirSiNuevo.includes(t.id)) return false
    if (!miembro.value.esVoluntario && excluirSiNoVoluntario.includes(t.id)) return false
    if (t.id === 'pagoCuotas' && !props.modoPropio && !tienePermiso('CUOT_LIST')) return false
    return true
  })
})

// ── Forma de pago ─────────────────────────────────────────────────────────────

function formaPagoIcono(nombre) {
  const n = (nombre || '').toLowerCase()
  if (n.includes('paypal')) return `<svg viewBox="0 0 24 24" class="w-7 h-7 inline-block" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M7.144 19.532l1.049-5.751c.11-.605.691-1.002 1.304-.948 2.155.195 6.243.265 7.908-3.402 2.88-6.388-3.344-8.05-8.36-7.737C7.51 1.745 6.617 1.9 6.617 1.9L4 19.532h3.144z" fill="#009CDE"/><path d="M17.124 7.952c1.394 3.073-.51 6.252-3.971 7.257-1.307.378-2.856.507-4.293.507L8 19.532H4l2.617-17.47s4.91-.688 7.815.147c1.578.452 2.873 1.574 2.692 5.743z" fill="#003087"/><path d="M17.124 7.952c-.18 4.169-1.114 5.291-2.692 5.743-3.461 1.005-5.005-1.005-4.295.507-.71-1.512-.507-4.293-.507-4.293s3.073-.13 4.38-.508c2.165-.625 2.674-2.78 3.114-1.449z" fill="#012169"/></svg>`
  if (n.includes('tarjeta')) return `<svg viewBox="0 0 48 32" class="w-10 h-7 inline-block" xmlns="http://www.w3.org/2000/svg"><rect width="48" height="32" rx="4" fill="#252525"/><circle cx="19" cy="16" r="9" fill="#EB001B"/><circle cx="29" cy="16" r="9" fill="#F79E1B"/><path d="M24 8.536a9 9 0 0 1 0 14.928A9 9 0 0 1 24 8.536z" fill="#FF5F00"/></svg>`
  if (n.includes('transferencia') && n.includes('internacional')) return '<span class="text-2xl">🌍</span>'
  if (n.includes('transferencia')) return '<span class="text-2xl">🏦</span>'
  if (n.includes('domiciliación') || n.includes('sepa')) return '<span class="text-2xl">📋</span>'
  if (n.includes('efectivo') || n.includes('metálico')) return '<span class="text-2xl">💵</span>'
  return '<span class="text-2xl">💰</span>'
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
    // Reposicionar cursor ajustando por los espacios insertados
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

// ── Estilos de estado desde catálogo ─────────────────────────────────────
const estadoColor      = computed(() => miembro.value.estado?.color)
const estadoBadgeStyle = computed(() => badgeStyle(estadoColor.value))
const estadoBandaStyle = computed(() => bandStyle(estadoColor.value))

const initials = computed(() => {
  const n = miembro.value.nombre?.[0] || ''
  const a = miembro.value.apellido1?.[0] || ''
  return (n + a).toUpperCase() || '?'
})

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
      miembro.value.fotoUrl = data.fotoUrl
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

// ── Cambiar contraseña (modo propio) ─────────────────────────────────────
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

// ── Cuotas ───────────────────────────────────────────────────────────────
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

// ── Habilidades ───────────────────────────────────────────────────────────
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

// ── Franjas de disponibilidad ──────────────────────────────────────────────
const franjas = ref([])
const loadingFranjas = ref(false)
const mostrarFormFranja = ref(false)
const nuevaFranja = ref({ diaSemana: 0, horaInicio: '', horaFin: '' })
const diasSemana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

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

// ── Acceso y roles ────────────────────────────────────────────────────────
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

// ── Modal crear cuenta desde tab Acceso ──────────────────────────────────
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

// ── Historial de nombramientos ────────────────────────────────────────────
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

// ── Sugerencia de agrupación por provincia ────────────────────────────────
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
  editMode.value = false
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
      editMode.value = false
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
    await Promise.all([fetchMiembro(resolvedId), cargarHabilidades(resolvedId), cargarFranjas(resolvedId), cargarNombramientos(resolvedId), cargarCuotas(resolvedId)])
    if (!props.modoPropio) await cargarRolesDisponibles()
    if (route.query.modo === 'editar') editMode.value = true
  }
})

// ── Componentes de campo inline ───────────────────────────────────────────

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
