<template>
  <AppLayout title="Parámetros Generales" subtitle="Configuración de la organización">
    <template #footer>
      <button type="button" :disabled="guardando" @click="guardar"
        class="h-10 px-5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors">
        {{ guardando ? 'Guardando…' : 'Guardar cambios' }}
      </button>
            <span v-if="error" class="text-sm text-red-600">{{ error }}</span>
    </template>

    <form @submit.prevent="guardar" class="flex flex-col"  id="parametros-form">

      <!-- Error de carga -->
      <div v-if="errorCarga"
        class="mb-4 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700 flex items-center gap-2 flex-shrink-0">
        <span>⚠️</span> {{ errorCarga }}
      </div>

      <!-- Acordeones -->
      <AccordionGroup class="flex-1 space-y-3 pb-4">

        <!-- 1. Identidad y Sede Social -->
        <AccordionPanel title="Identidad y Sede Social" :default-open="true">
          <div class="px-5 py-4 space-y-4">
            <!-- Nombre + NIF + Nº registro -->
            <div class="flex flex-wrap items-end gap-3">
              <div class="flex-1 min-w-0">
                <label class="label">Nombre de la organización <span class="text-red-500">*</span></label>
                <input v-model="form.nombre" type="text" class="input" placeholder="Nombre completo" />
              </div>
              <div class="w-full sm:w-28 flex-shrink-0">
                <label class="label">NIF <span class="text-red-500">*</span></label>
                <input v-model="form.nif" type="text" class="input" placeholder="G00000000" maxlength="12" />
              </div>
              <div class="w-full sm:w-32 flex-shrink-0">
                <label class="label">Nº registro</label>
                <input v-model="form.numero_registro" type="text" class="input" placeholder="12345/A" maxlength="40" />
              </div>
            </div>
            <!-- Sede social -->
            <div>
              <label class="label">Dirección</label>
              <input v-model="form.sede_social" type="text" class="input" placeholder="Calle, número, piso..." />
            </div>
            <div class="flex flex-wrap items-end gap-3">
              <div class="flex-1 min-w-0">
                <label class="label">Localidad</label>
                <input v-model="form.localidad" type="text" class="input" />
              </div>
              <div class="w-20 flex-shrink-0">
                <label class="label">CP</label>
                <input v-model="form.cp" type="text" class="input" placeholder="28001" maxlength="10" />
              </div>
              <div class="flex-1 min-w-0">
                <label class="label">Provincia</label>
                <input v-model="form.provincia" type="text" class="input" />
              </div>
              <div class="w-full sm:w-28 flex-shrink-0">
                <label class="label">País</label>
                <input v-model="form.pais" type="text" class="input" />
              </div>
            </div>
            <div class="flex flex-wrap items-end gap-3">
              <div class="w-full sm:w-40 flex-shrink-0">
                <label class="label">Teléfono <span class="text-red-500">*</span></label>
                <input v-model="form.telefono" type="tel" class="input" placeholder="+34 900 000 000" />
              </div>
              <div class="flex-1 min-w-0">
                <label class="label">Email de contacto <span class="text-red-500">*</span></label>
                <input v-model="form.email" type="email" class="input" placeholder="info@organización.org" />
              </div>
              <div class="flex-1 min-w-0">
                <label class="label">Sitio web</label>
                <input v-model="form.web" type="url" class="input" placeholder="https://www.organización.org" />
              </div>
            </div>
          </div>
        </AccordionPanel>

        <!-- 2. Estructura organizativa -->
        <AccordionPanel title="Estructura organizativa" :default-open="true">
          <div class="px-5 pt-4 space-y-5">
            <!-- General: tipo de entidad + modelo de estructura territorial -->
            <div class="flex flex-col lg:flex-row gap-4 lg:items-start">
              <div class="w-full lg:w-44 flex-shrink-0">
                <label class="label">Tipo entidad</label>
                <select v-model="form.tipo_entidad" class="input">
                  <option value="ASOCIACION">Asociación</option>
                  <option value="FUNDACION">Fundación</option>
                </select>
              </div>
              <div class="flex-1 min-w-0">
                <label class="label">Modelo de estructura territorial</label>
                <div class="flex flex-col sm:flex-row gap-2.5">
                  <label class="flex-1 flex items-start gap-2.5 rounded-lg border p-2.5 cursor-pointer transition-colors"
                    :class="!estructuraDistribuida ? 'border-indigo-400 bg-indigo-50/60 ring-1 ring-indigo-200' : 'border-slate-200 hover:bg-slate-50'">
                    <input type="radio" class="mt-0.5 accent-indigo-600" :checked="!estructuraDistribuida" @change="editorRef?.setDistribuida(false)" />
                    <span class="min-w-0">
                      <span class="block text-sm font-medium text-slate-800">Centralizada</span>
                      <span class="block text-xs text-slate-500 leading-snug mt-0.5">La estructura interna se define aquí, igual para todas las unidades.</span>
                    </span>
                  </label>
                  <label class="flex-1 flex items-start gap-2.5 rounded-lg border p-2.5 cursor-pointer transition-colors"
                    :class="estructuraDistribuida ? 'border-indigo-400 bg-indigo-50/60 ring-1 ring-indigo-200' : 'border-slate-200 hover:bg-slate-50'">
                    <input type="radio" class="mt-0.5 accent-indigo-600" :checked="estructuraDistribuida" @change="editorRef?.setDistribuida(true)" />
                    <span class="min-w-0">
                      <span class="block text-sm font-medium text-slate-800">Distribuida</span>
                      <span class="block text-xs text-slate-500 leading-snug mt-0.5">Cada unidad define su propia subestructura.</span>
                    </span>
                  </label>
                </div>
              </div>
            </div>

            <!-- Nomenclatura -->
            <fieldset class="rounded-xl border border-slate-200 px-4 pt-2 pb-4">
              <legend class="px-1.5 text-[11px] font-semibold uppercase tracking-wide text-slate-400">Nomenclatura</legend>
              <div class="grid grid-cols-1 lg:grid-cols-2 gap-x-5 gap-y-3 mt-1">
                <div>
                  <label class="label">Denominación de la membresía (singular / plural)</label>
                  <div class="flex items-center gap-2">
                    <input v-model="form.denominacion_miembro" type="text" class="input w-0 flex-1" placeholder="socio" maxlength="30" />
                    <span class="text-slate-400 text-sm flex-shrink-0">/</span>
                    <input v-model="form.denominacion_miembro_plural" type="text" class="input w-0 flex-1" placeholder="socios" maxlength="30" />
                  </div>
                  <p class="mt-1 text-[11px] text-slate-400">p.ej. socio/socios · afiliado/afiliados · miembro/miembros</p>
                </div>
                <div>
                  <label class="label">Denominación del Órgano de Gobierno (singular / plural)</label>
                  <div class="flex items-center gap-2">
                    <input v-model="form.denominacion_organo_gobierno" type="text" class="input w-0 flex-1" placeholder="junta directiva" maxlength="40" />
                    <span class="text-slate-400 text-sm flex-shrink-0">/</span>
                    <input v-model="form.denominacion_organo_gobierno_plural" type="text" class="input w-0 flex-1" placeholder="juntas directivas" maxlength="40" />
                  </div>
                  <p class="mt-1 text-[11px] text-slate-400">p.ej. junta directiva · patronato · comité ejecutivo</p>
                </div>
              </div>
            </fieldset>

            <!-- Aviso protección -->
            <div v-if="editorRef?.estructuraProtegida" class="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
              🔒 Protegida — hay datos asociados. Solo se puede renombrar.
            </div>
          </div>
          <div class="px-5 pb-4">
            <EstructuraOrganizativaEditor ref="editorRef" :mostrar-radiogroup="false" />
          </div>
        </AccordionPanel>

        <!-- 3. Identidad visual -->
        <AccordionPanel title="Identidad visual" :default-open="true">
          <div class="px-5 py-4 flex gap-6">
            <!-- Logotipo -->
            <div class="flex flex-col items-center gap-2 flex-shrink-0">
              <div class="w-full sm:w-28 h-28 rounded-xl border-2 border-dashed border-slate-200 bg-slate-50 flex items-center justify-center overflow-hidden">
                <img v-if="form.logo" :src="form.logo" alt="Logo" class="w-full h-full object-contain p-2" />
                <span v-else class="text-4xl text-slate-200">🏛</span>
              </div>
              <div class="flex items-center gap-1.5">
                <label class="cursor-pointer px-2.5 py-1.5 text-xs font-medium bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors text-slate-700">
                  {{ form.logo ? 'Cambiar' : 'Seleccionar' }}
                  <input ref="fileInput" type="file" accept="image/png,image/jpeg,image/svg+xml,image/webp" class="hidden" @change="handleLogoChange" />
                </label>
                <button v-if="form.logo" type="button" @click="eliminarLogo"
                  class="px-2.5 py-1.5 text-xs font-medium text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors">
                  Eliminar
                </button>
              </div>
              <p class="text-xs text-slate-400 text-center leading-tight">PNG · JPG · SVG · máx. 300 KB</p>
              <ErrorAlert v-if="logoError" :message="logoError" />
            </div>
            <!-- Tema + Fuente -->
            <div class="flex-1 min-w-0 space-y-4">
              <div>
                <label class="label">Tema de color</label>
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 sm:grid-cols-5 gap-2 mt-1.5">
                  <button v-for="t in temas" :key="t.slug" type="button"
                    @click="form.tema = t.slug; orgConfigStore.applyTheme(t, form.fuente_principal)"
                    class="rounded-lg border-2 p-1.5 text-center transition-all hover:border-slate-400"
                    :class="form.tema === t.slug ? 'border-slate-700 shadow-sm' : 'border-slate-200'">
                    <div class="flex gap-0.5 mb-0.5 justify-center">
                      <div v-for="c in temaPaleta(t)" :key="c" class="h-3 w-3 rounded-sm" :style="{ backgroundColor: c }" />
                    </div>
                    <span class="text-xs font-medium text-slate-700">{{ t.nombre }}</span>
                  </button>
                </div>
              </div>
              <div>
                <label class="label">Tipografía</label>
                <select v-model="form.fuente_principal" class="input w-full sm:w-44 mt-1.5">
                  <option v-for="f in fuentesDisponibles" :key="f.valor" :value="f.valor">{{ f.nombre }}</option>
                </select>
              </div>
            </div>
          </div>
        </AccordionPanel>

        <!-- 4. Funcionalidades -->
        <AccordionPanel title="Funcionalidades" :default-open="false">
          <div class="px-5 py-4">

            <!-- Estructura de clasificación contable -->
            <div class="mb-6 pb-6 border-b border-slate-100">
              <h3 class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                Estructura de clasificación contable
              </h3>
              <p class="text-xs text-slate-400 mb-3">
                Determina cómo se clasifican los ingresos y gastos de la organización.
              </p>
              <div class="space-y-3">
                <label class="flex items-start gap-3 cursor-pointer">
                  <input
                    type="radio"
                    :value="false"
                    v-model="form.contabilidad_compleja"
                    :disabled="esObligatorioContabilidad"
                    class="h-4 w-4 mt-0.5 border-slate-300 text-indigo-600 focus:ring-indigo-500 disabled:opacity-60 disabled:cursor-not-allowed"
                  />
                  <span class="text-sm text-slate-700">
                    Categorías fiscales
                    <span class="text-slate-400 text-xs block mt-0.5">
                      Contabilidad simplificada: libro de ingresos y gastos clasificados por
                      categorías que cuadran con los modelos fiscales (130/131, 182, 347).
                      Recomendado para asociaciones pequeñas.
                    </span>
                  </span>
                </label>
                <label class="flex items-start gap-3 cursor-pointer">
                  <input
                    type="radio"
                    :value="true"
                    v-model="form.contabilidad_compleja"
                    :disabled="esObligatorioContabilidad"
                    class="h-4 w-4 mt-0.5 border-slate-300 text-indigo-600 focus:ring-indigo-500 disabled:opacity-60 disabled:cursor-not-allowed"
                  />
                  <span class="text-sm text-slate-700">
                    Plan General Contable (PCESFL)
                    <span class="text-slate-400 text-xs block mt-0.5">
                      Contabilidad por partida doble según RD 1491/2011 — obligatorio para
                      fundaciones.
                    </span>
                  </span>
                </label>
              </div>
              <p v-if="esObligatorioContabilidad" class="text-xs text-amber-600 mt-2">
                El Plan General Contable es obligatorio para fundaciones y no puede desactivarse.
              </p>
            </div>

            <!-- Presupuesto anual -->
            <div class="mb-6 pb-6 border-b border-slate-100">
              <h3 class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                Presupuesto anual
              </h3>
              <p class="text-xs text-slate-400 mb-3">
                Habilita la elaboración y el seguimiento del presupuesto anual por partidas.
              </p>
              <label class="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  v-model="form.usa_presupuesto"
                  :disabled="esObligatorioPresupuesto"
                  class="h-4 w-4 mt-0.5 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 disabled:opacity-60 disabled:cursor-not-allowed"
                />
                <span class="text-sm text-slate-700">
                  Usar gestión presupuestaria
                  <span class="text-slate-400 text-xs block mt-0.5">
                    Planificación anual de ingresos y gastos por partidas, ciclo de aprobación y
                    seguimiento de ejecución. Para asociaciones es opcional (según estatutos).
                  </span>
                </span>
              </label>
              <p v-if="esObligatorioPresupuesto" class="text-xs text-amber-600 mt-2">
                El plan de actuación (presupuesto) es obligatorio para fundaciones (Ley 50/2002)
                y no puede desactivarse.
              </p>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-4">
              <div v-for="feat in catalogoFuncionalidades" :key="feat.clave" class="space-y-3">
                <label class="flex items-start gap-3 cursor-pointer"
                  :class="feat.deshabilitado?.() ? 'cursor-not-allowed' : ''">
                  <input
                    v-model="form[feat.campo]"
                    type="checkbox"
                    :disabled="feat.deshabilitado?.()"
                    class="h-4 w-4 mt-0.5 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 disabled:opacity-60 disabled:cursor-not-allowed"
                  />
                  <span class="text-sm text-slate-700">
                    {{ feat.nombre }}
                    <span class="text-slate-400 text-xs block mt-0.5">{{ feat.descripcion }}</span>
                  </span>
                </label>
                <div v-if="form[feat.campo] && feat.campos?.length"
                  class="ml-7 space-y-3 border-l-2 border-indigo-100 pl-4">
                  <div v-for="campo in feat.campos" :key="campo.key">
                    <label class="label">{{ campo.label }}</label>
                    <input
                      v-model="form[campo.key]"
                      :type="campo.tipo"
                      :placeholder="campo.placeholder"
                      class="input"
                      :autocomplete="campo.tipo === 'password' ? 'off' : undefined"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </AccordionPanel>

        <!-- 6. Autenticación y Email -->
        <AccordionPanel title="Autenticación y Email" :default-open="false">
          <div class="px-5 py-4 space-y-5">

            <!-- Mecanismo de autenticación -->
            <div class="space-y-3">
              <h3 class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Autenticación</h3>
              <!-- Mecanismo + Inactividad + Sesión en una fila -->
              <div class="flex flex-wrap items-start gap-3">
                <div class="flex-1 min-w-0">
                  <label class="label">Mecanismo</label>
                  <select v-model="form.auth_modo" class="input">
                    <option value="LOCAL">Local (SIGA)</option>
                    <option value="AUTHELIA">Authelia (forward-auth)</option>
                    <option value="OIDC">OIDC / OAuth2</option>
                  </select>
                </div>
                <div class="w-full sm:w-40 flex-shrink-0">
                  <label class="label">Inactividad (min)</label>
                  <input v-model.number="form.session_inactividad_minutos" type="number" min="0" class="input" />
                  <p class="text-xs text-slate-400 mt-1">0 = sin timeout</p>
                </div>
                <div class="w-full sm:w-40 flex-shrink-0">
                  <label class="label">Sesión máxima (min)</label>
                  <input v-model.number="form.session_maximo_minutos" type="number" min="0" class="input" />
                  <p class="text-xs text-slate-400 mt-1">0 = ilimitada</p>
                </div>
              </div>
              <div v-if="form.auth_modo === 'AUTHELIA'">
                <label class="label">URL de Authelia</label>
                <input v-model="form.auth_authelia_url" type="url" class="input" placeholder="https://auth.midominio.org" />
              </div>
              <div v-if="form.auth_modo === 'OIDC'">
                <label class="label">OIDC Issuer URL</label>
                <input v-model="form.auth_oidc_issuer" type="url" class="input" placeholder="https://accounts.google.com" />
              </div>
            </div>

            <!-- Servidor de correo (SMTP) -->
            <div class="space-y-3 pt-3 border-t border-slate-100">
              <div class="flex items-baseline justify-between">
                <h3 class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Servidor de correo (SMTP)</h3>
                <p class="text-xs text-slate-400">Usado para enviar emails de bienvenida, reset de contraseña, etc.</p>
              </div>
              <div class="flex flex-wrap items-end gap-3">
                <div class="flex-1 min-w-0">
                  <label class="label">Servidor</label>
                  <input v-model="form.smtp_host" type="text" class="input" placeholder="smtp.midominio.org" />
                </div>
                <div class="w-full sm:w-24 flex-shrink-0">
                  <label class="label">Puerto</label>
                  <input v-model="form.smtp_port" type="text" class="input" placeholder="587" />
                </div>
                <div class="w-full sm:w-auto flex-shrink-0 flex items-end gap-4 pb-2">
                  <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                    <input v-model="form.smtp_tls" type="checkbox" class="rounded text-indigo-600" />
                    STARTTLS
                  </label>
                  <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                    <input v-model="form.smtp_ssl" type="checkbox" class="rounded text-indigo-600" />
                    SSL directo
                  </label>
                </div>
              </div>
              <div class="flex flex-wrap items-end gap-3">
                <div class="flex-1 min-w-0">
                  <label class="label">Usuario</label>
                  <input v-model="form.smtp_usuario" type="text" class="input" placeholder="noreply@midominio.org" autocomplete="off" />
                </div>
                <div class="flex-1 min-w-0">
                  <label class="label">Contraseña</label>
                  <input v-model="form.smtp_password" type="password" class="input" placeholder="••••••••" autocomplete="new-password" />
                </div>
                <div class="flex-1 min-w-0">
                  <label class="label">Remitente (From)</label>
                  <input v-model="form.smtp_from" type="email" class="input" placeholder="SIGA <noreply@midominio.org>" />
                </div>
              </div>
              <p class="text-xs text-slate-400">
                Si dejas la contraseña en blanco, se conservará la actual. Si hay variables de entorno SMTP definidas en el servidor, tienen prioridad sobre esta configuración.
              </p>
            </div>

          </div>
        </AccordionPanel>

        <!-- 7. SEPA — Acreedor para remesas (Flujo 3 — D3.5) -->
        <AccordionPanel title="SEPA — Acreedor para remesas" :default-open="false">
          <div class="px-5 py-4 space-y-3">
            <p class="text-xs text-slate-500">
              Datos que se incluirán como acreedor en los XML SEPA Pain.008 generados.
              Sin completar, las remesas no podrán generar XML. La cuenta operativa puede ser cualquiera, pero
              el <b>Identificador de acreedor SEPA</b> debe estar registrado en tu banco.
            </p>
            <div class="grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="label">Nombre del acreedor *</label>
                <input v-model="form.sepa_creditor_name" type="text" maxlength="70" class="input"
                       placeholder="Razón social que aparecerá en el cargo bancario al socio" />
              </div>
              <div>
                <label class="label">Identificador SEPA (AT-02) *</label>
                <input v-model="form.sepa_creditor_id" type="text" class="input"
                       placeholder="ES77ZZZ12345678" />
                <p class="text-xs text-slate-400 mt-1">Formato España: ES + 2 dígitos control + ZZZ + 9 dígitos del NIF.</p>
              </div>
              <div>
                <label class="label">IBAN del acreedor *</label>
                <input v-model="form.sepa_creditor_iban" type="text" class="input font-mono"
                       placeholder="ES00 0000 0000 0000 0000 0000" />
              </div>
              <div>
                <label class="label">BIC / SWIFT *</label>
                <input v-model="form.sepa_creditor_bic" type="text" class="input font-mono"
                       placeholder="BBVAESMM" />
              </div>
            </div>
          </div>
        </AccordionPanel>

        <!-- 7b. Protección de datos (RGPD) -->
        <AccordionPanel title="Protección de datos (RGPD)" :default-open="false">
          <div class="px-5 py-4 space-y-4">
            <p class="text-xs text-slate-500">
              Datos del Delegado de Protección de Datos (DPD/DPO) y plazos de retención.
              Obligatorio según art. 37 RGPD para algunas entidades.
            </p>
            <div class="space-y-3">
              <h3 class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Delegado de Protección de Datos</h3>
              <div class="flex flex-wrap items-end gap-3">
                <div class="flex-1 min-w-[200px]">
                  <label class="label">Nombre del DPD</label>
                  <input v-model="form.rgpd_dpd_nombre" type="text" class="input"
                    placeholder="María García López / Consultora ABC, S.L." />
                </div>
                <div class="flex-1 min-w-[200px]">
                  <label class="label">Email del DPD</label>
                  <input v-model="form.rgpd_dpd_email" type="email" class="input"
                    placeholder="dpd@organizacion.org" />
                </div>
                <div class="w-full sm:w-44 flex-shrink-0">
                  <label class="label">Teléfono</label>
                  <input v-model="form.rgpd_dpd_telefono" type="tel" class="input"
                    placeholder="+34 900 000 000" />
                </div>
                <div class="w-full sm:w-auto flex-shrink-0 pb-2">
                  <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                    <input v-model="form.rgpd_dpd_externo" type="checkbox" class="rounded text-indigo-600" />
                    DPD externo (proveedor)
                  </label>
                </div>
              </div>
            </div>
            <div class="space-y-3 pt-3 border-t border-slate-100">
              <h3 class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Plazos de retención</h3>
              <div class="flex flex-wrap items-end gap-3">
                <div class="w-full sm:w-64 flex-shrink-0">
                  <label class="label">Años de retención tras baja</label>
                  <input v-model.number="form.rgpd_anios_retencion_baja" type="number" min="0" max="20" class="input" />
                  <p class="text-xs text-slate-400 mt-1">
                    Tras la baja, se calcula <code>fecha_baja + N años</code> como límite tras el cual los datos
                    pueden purgarse. 6 años cubre el Código de Comercio (art. 30).
                  </p>
                </div>
              </div>
            </div>
          </div>
        </AccordionPanel>

        <!-- 8. Redes sociales -->
        <AccordionPanel title="Redes sociales" :default-open="false">
          <div class="px-5 py-4 grid grid-cols-1 sm:grid-cols-1 sm:grid-cols-2 gap-3">
            <div v-for="red in redesSociales" :key="red.key" class="flex items-center gap-2 min-w-0">
              <div class="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
                   :style="{ backgroundColor: red.bg, color: red.color }" :title="red.label">
                <svg viewBox="0 0 24 24" fill="currentColor" class="w-3.5 h-3.5">
                  <path :d="red.path" />
                </svg>
              </div>
              <label class="label mb-0 w-20 flex-shrink-0">{{ red.label }}</label>
              <div class="flex-1 min-w-0 flex items-center border border-slate-300 rounded-lg overflow-hidden h-10
                          focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500 transition-colors">
                <span v-if="red.handle"
                  class="px-2 text-sm text-slate-400 bg-slate-50 border-r border-slate-200 flex-shrink-0 select-none h-full flex items-center">
                  {{ red.handle }}
                </span>
                <input v-model="form[red.key]" type="text" :placeholder="red.placeholder"
                  class="flex-1 min-w-0 px-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none bg-transparent" />
              </div>
            </div>
          </div>
        </AccordionPanel>

      </AccordionGroup>

    </form>
  </AppLayout>
</template>

<script setup>
import { useToast } from '@/composables/useToast'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { ref, reactive, computed, watch, watchEffect, onMounted } from 'vue'
import { useRouter, onBeforeRouteLeave } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'
import AccordionPanel from '@/components/common/AccordionPanel.vue'
import AccordionGroup from '@/components/common/AccordionGroup.vue'
import EstructuraOrganizativaEditor from '@/components/configuracion/EstructuraOrganizativaEditor.vue'
import { graphqlClient } from '@/graphql/client.js'
import { useOrgConfigStore } from '@/stores/orgConfig.js'
import { CheckCircleIcon } from '@heroicons/vue/24/outline'
const toast = useToast()

const router = useRouter()
const orgConfigStore = useOrgConfigStore()

const editorRef = ref(null)
// Espejo reactivo del modelo centralizada/distribuida que expone el editor,
// para que el radiogroup (que vive aquí, junto a Tipo entidad) se actualice.
const estructuraDistribuida = ref(false)
watchEffect(() => { estructuraDistribuida.value = !!editorRef.value?.distribuida })

const guardando = ref(false)
const guardadoOk = ref(false)
const error = ref('')
const errorCarga = ref('')
const logoError = ref('')
const fileInput = ref(null)

const form = reactive({
  nombre: '',
  nif: '',
  tipo_entidad: 'ASOCIACION',
  contabilidad_compleja: false,
  usa_presupuesto: false,
  sede_social: '',
  localidad: '',
  cp: '',
  provincia: '',
  pais: 'España',
  telefono: '',
  email: '',
  web: '',
  rrss_twitter: '',
  rrss_facebook: '',
  rrss_instagram: '',
  rrss_linkedin: '',
  rrss_youtube: '',
  rrss_telegram: '',
  logo: '',
  numero_registro: '',
  denominacion_miembro: 'miembro',
  denominacion_miembro_plural: 'miembros',
  denominacion_organo_gobierno: 'junta directiva',
  denominacion_organo_gobierno_plural: 'juntas directivas',
  auth_modo: 'LOCAL',
  auth_authelia_url: '',
  auth_oidc_issuer: '',
  session_inactividad_minutos: 30,
  session_maximo_minutos: 480,
  smtp_host: '',
  smtp_port: '587',
  smtp_usuario: '',
  smtp_password: '',
  smtp_from: '',
  smtp_tls: true,
  smtp_ssl: false,
  tema: 'violeta',
  fuente_principal: 'Inter',
  indico_activo: false,
  indico_url: '',
  indico_api_token: '',
  // SEPA — Acreedor para remesas (D3.5)
  sepa_creditor_name: '',
  sepa_creditor_iban: '',
  sepa_creditor_bic: '',
  sepa_creditor_id: '',
  // Open Banking — conciliación bancaria automática (flujo 8)
  openbanking_activo: false,
  // RGPD — Protección de datos
  rgpd_dpd_nombre: '',
  rgpd_dpd_email: '',
  rgpd_dpd_telefono: '',
  rgpd_dpd_externo: false,
  rgpd_anios_retencion_baja: 6,
})

const temaOriginal = ref(orgConfigStore.temaActivo)
const fuenteOriginal = ref(orgConfigStore.fuentePrincipal)
let guardadoExitoso = false

onBeforeRouteLeave(() => {
  if (!guardadoExitoso && temaOriginal.value) {
    orgConfigStore.applyTheme(temaOriginal.value, fuenteOriginal.value)
  }
})

const temas = computed(() => orgConfigStore.temas)
const temaPaleta = (t) => [t.t50, t.t300, t.t600, t.t800, t.t900].filter(Boolean)

const fuentesDisponibles = [
  { nombre: 'Inter',          valor: 'Inter' },
  { nombre: 'Poppins',        valor: 'Poppins' },
  { nombre: 'Nunito',         valor: 'Nunito' },
  { nombre: 'Roboto',         valor: 'Roboto' },
  { nombre: 'Open Sans',      valor: 'Open Sans' },
  { nombre: 'Plus Jakarta',   valor: 'Plus Jakarta Sans' },
]

const catalogoFuncionalidades = [
  {
    clave: 'indico',
    campo: 'indico_activo',
    nombre: 'Integración con Indico (gestión de eventos)',
    descripcion: 'Sincroniza acciones/eventos con una instalación de Indico vía API REST',
    campos: [
      { key: 'indico_url',       label: 'URL de la instancia Indico', tipo: 'url',      placeholder: 'https://indico.tuorganizacion.org' },
      { key: 'indico_api_token', label: 'API Token',                  tipo: 'password', placeholder: '••••••••' },
    ],
  },
  {
    clave: 'openbanking',
    campo: 'openbanking_activo',
    nombre: 'Conciliación bancaria automática (Open Banking)',
    descripcion: 'Si está activo, los movimientos se descargan automáticamente del banco vía API PSD2 (Enable Banking u otro proveedor). Si no, se usa la importación manual de CSV o Norma 43. El emparejamiento entre apuntes y extracto sigue siendo manual en ambos casos.',
    campos: [],
  },
]

const esObligatorioContabilidad = computed(() => {
  const tipo = (form.tipo_entidad ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
  return tipo.includes('fundacion')
})
watch(esObligatorioContabilidad, (val) => { if (val) form.contabilidad_compleja = true })

// El presupuesto (plan de actuación) es obligatorio para fundaciones (Ley 50/2002)
const esObligatorioPresupuesto = computed(() => esObligatorioContabilidad.value)
watch(esObligatorioPresupuesto, (val) => { if (val) form.usa_presupuesto = true })

watch(() => form.fuente_principal, (font) => {
  const t = orgConfigStore.temas.find(t => t.slug === form.tema) ?? form.tema
  orgConfigStore.applyTheme(t, font)
})

const redesSociales = [
  {
    key: 'rrss_twitter', label: 'Twitter / X', handle: '@', placeholder: 'usuario',
    color: '#000', bg: '#f1f5f9',
    path: 'M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z',
  },
  {
    key: 'rrss_facebook', label: 'Facebook', handle: '', placeholder: 'pagina-o-perfil',
    color: '#1877F2', bg: '#eff6ff',
    path: 'M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z',
  },
  {
    key: 'rrss_instagram', label: 'Instagram', handle: '@', placeholder: 'usuario',
    color: '#C13584', bg: '#fdf2f8',
    path: 'M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z',
  },
  {
    key: 'rrss_linkedin', label: 'LinkedIn', handle: '', placeholder: 'empresa-o-perfil',
    color: '#0A66C2', bg: '#eff6ff',
    path: 'M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z',
  },
  {
    key: 'rrss_youtube', label: 'YouTube', handle: '@', placeholder: 'canal',
    color: '#FF0000', bg: '#fff1f2',
    path: 'M23.495 6.205a3.007 3.007 0 00-2.088-2.088c-1.87-.501-9.396-.501-9.396-.501s-7.507-.01-9.396.501A3.007 3.007 0 00.527 6.205a31.247 31.247 0 00-.522 5.805 31.247 31.247 0 00.522 5.783 3.007 3.007 0 002.088 2.088c1.868.502 9.396.502 9.396.502s7.506 0 9.396-.502a3.007 3.007 0 002.088-2.088 31.247 31.247 0 00.5-5.783 31.247 31.247 0 00-.5-5.805zM9.609 15.601V8.408l6.264 3.602z',
  },
  {
    key: 'rrss_telegram', label: 'Telegram', handle: '@', placeholder: 'canal',
    color: '#0088cc', bg: '#e8f4fd',
    path: 'M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z',
  },
]

const QUERY_PARAMETROS = `
  query {
    parametrosOrganizacion {
      nombre nif numeroRegistro tipoEntidad contabilidadCompleja usaPresupuesto
      sedeSocial localidad cp provincia pais
      telefono email web
      rrssTwitter rrssFacebook rrssInstagram rrssLinkedin rrssYoutube rrssTelegram
      logo denominacionMiembro denominacionMiembroPlural
      denominacionOrganoGobierno denominacionOrganoGobiernoPlural
      authModo authAutheliaUrl authOidcIssuer
      sessionInactividadMinutos sessionMaximoMinutos
      smtpHost smtpPort smtpUsuario smtpPassword smtpFrom smtpTls smtpSsl
      indicoActivo indicoUrl indicoApiToken
      tema fuentePrincipal
      sepaCreditorName sepaCreditorIban sepaCreditorBic sepaCreditorId
      openbankingActivo
      rgpdDpdNombre rgpdDpdEmail rgpdDpdTelefono rgpdDpdExterno rgpdAniosRetencionBaja
    }
  }
`

const MUTATION_GUARDAR = `
  mutation GuardarParametros($datos: ParametrosOrganizacionInput!) {
    guardarParametrosOrganizacion(datos: $datos) {
      nombre logo
    }
  }
`

function handleLogoChange(event) {
  const file = event.target.files[0]
  if (!file) return
  if (file.size > 300 * 1024) {
    logoError.value = 'La imagen supera el límite de 300 KB'
    if (fileInput.value) fileInput.value.value = ''
    return
  }
  logoError.value = ''
  const reader = new FileReader()
  reader.onload = (e) => { form.logo = e.target.result }
  reader.readAsDataURL(file)
}

function eliminarLogo() {
  form.logo = ''
  logoError.value = ''
  if (fileInput.value) fileInput.value.value = ''
}

onMounted(async () => {
  if (orgConfigStore.nombre) form.nombre = orgConfigStore.nombre
  if (orgConfigStore.logo)   form.logo   = orgConfigStore.logo

  try {
    const data = await graphqlClient.request(QUERY_PARAMETROS)
    const p = data.parametrosOrganizacion
    form.nombre                          = p.nombre                           ?? ''
    form.nif                             = p.nif                              ?? ''
    form.numero_registro                 = p.numeroRegistro                   ?? ''
    form.tipo_entidad                    = p.tipoEntidad                      ?? 'ASOCIACION'
    form.contabilidad_compleja           = p.contabilidadCompleja             ?? false
    form.usa_presupuesto                 = p.usaPresupuesto                   ?? false
    // Defensivo: si la entidad es fundación, contabilidad PCESFL y presupuesto son
    // obligatorios aunque en BD vinieran desactivados (datos inconsistentes).
    if (esObligatorioContabilidad.value) form.contabilidad_compleja = true
    if (esObligatorioPresupuesto.value)  form.usa_presupuesto = true
    form.sede_social                     = p.sedeSocial                       ?? ''
    form.localidad                       = p.localidad                        ?? ''
    form.cp                              = p.cp                               ?? ''
    form.provincia                       = p.provincia                        ?? ''
    form.pais                            = p.pais                             ?? 'España'
    form.telefono                        = p.telefono                         ?? ''
    form.email                           = p.email                            ?? ''
    form.web                             = p.web                              ?? ''
    form.rrss_twitter                    = p.rrssTwitter                      ?? ''
    form.rrss_facebook                   = p.rrssFacebook                     ?? ''
    form.rrss_instagram                  = p.rrssInstagram                    ?? ''
    form.rrss_linkedin                   = p.rrssLinkedin                     ?? ''
    form.rrss_youtube                    = p.rrssYoutube                      ?? ''
    form.rrss_telegram                   = p.rrssTelegram                     ?? ''
    form.logo                            = p.logo                             ?? ''
    form.denominacion_miembro            = p.denominacionMiembro              ?? 'miembro'
    form.denominacion_miembro_plural     = p.denominacionMiembroPlural        ?? 'miembros'
    form.denominacion_organo_gobierno    = p.denominacionOrganoGobierno       ?? 'junta directiva'
    form.denominacion_organo_gobierno_plural = p.denominacionOrganoGobiernoPlural ?? 'juntas directivas'
    orgConfigStore.miembro               = form.denominacion_miembro
    orgConfigStore.miembros              = form.denominacion_miembro_plural
    form.auth_modo                       = p.authModo                         ?? 'LOCAL'
    form.auth_authelia_url               = p.authAutheliaUrl                  ?? ''
    form.auth_oidc_issuer                = p.authOidcIssuer                   ?? ''
    form.session_inactividad_minutos     = p.sessionInactividadMinutos        ?? 30
    form.session_maximo_minutos          = p.sessionMaximoMinutos             ?? 480
    form.smtp_host                       = p.smtpHost                         ?? ''
    form.smtp_port                       = p.smtpPort                         ?? '587'
    form.smtp_usuario                    = p.smtpUsuario                      ?? ''
    form.smtp_password                   = p.smtpPassword                     ?? ''
    form.smtp_from                       = p.smtpFrom                         ?? ''
    form.smtp_tls                        = p.smtpTls                          ?? true
    form.smtp_ssl                        = p.smtpSsl                          ?? false
    form.indico_activo                   = p.indicoActivo                     ?? false
    form.indico_url                      = p.indicoUrl                        ?? ''
    form.indico_api_token                = p.indicoApiToken                   ?? ''
    form.tema                            = p.tema                             ?? 'violeta'
    form.fuente_principal                = p.fuentePrincipal                  ?? 'Inter'
    form.sepa_creditor_name              = p.sepaCreditorName                 ?? ''
    form.sepa_creditor_iban              = p.sepaCreditorIban                 ?? ''
    form.sepa_creditor_bic               = p.sepaCreditorBic                  ?? ''
    form.sepa_creditor_id                = p.sepaCreditorId                   ?? ''
    form.openbanking_activo              = p.openbankingActivo                ?? false
    form.rgpd_dpd_nombre                 = p.rgpdDpdNombre                    ?? ''
    form.rgpd_dpd_email                  = p.rgpdDpdEmail                     ?? ''
    form.rgpd_dpd_telefono               = p.rgpdDpdTelefono                  ?? ''
    form.rgpd_dpd_externo                = p.rgpdDpdExterno                   ?? false
    form.rgpd_anios_retencion_baja       = p.rgpdAniosRetencionBaja           ?? 6
    temaOriginal.value   = orgConfigStore.temas.find(t => t.slug === form.tema) ?? null
    fuenteOriginal.value = form.fuente_principal
  } catch (e) {
    errorCarga.value = e?.response?.errors?.[0]?.message
      ?? 'No se pudieron cargar los parámetros. Comprueba la conexión con el servidor.'
  }
})

async function guardar() {
  error.value = ''
  if (!form.nombre.trim())   { error.value = 'El nombre de la organización es obligatorio'; return }
  if (!form.nif.trim())      { error.value = 'El NIF es obligatorio'; return }
  if (!form.telefono.trim()) { error.value = 'El teléfono es obligatorio'; return }
  if (!form.email.trim())    { error.value = 'El email es obligatorio'; return }
  if (!form.logo)            { error.value = 'El logotipo es obligatorio'; return }

  guardando.value = true
  guardadoOk.value = false
  try {
    await graphqlClient.request(MUTATION_GUARDAR, {
      datos: {
        nombre:                          form.nombre,
        nif:                             form.nif,
        numeroRegistro:                  form.numero_registro,
        tipoEntidad:                     form.tipo_entidad,
        contabilidadCompleja:            form.contabilidad_compleja,
        usaPresupuesto:                  form.usa_presupuesto,
        sedeSocial:                      form.sede_social,
        localidad:                       form.localidad,
        cp:                              form.cp,
        provincia:                       form.provincia,
        pais:                            form.pais,
        telefono:                        form.telefono,
        email:                           form.email,
        web:                             form.web,
        rrssTwitter:                     form.rrss_twitter,
        rrssFacebook:                    form.rrss_facebook,
        rrssInstagram:                   form.rrss_instagram,
        rrssLinkedin:                    form.rrss_linkedin,
        rrssYoutube:                     form.rrss_youtube,
        rrssTelegram:                    form.rrss_telegram,
        logo:                            form.logo,
        denominacionMiembro:             form.denominacion_miembro,
        denominacionMiembroPlural:       form.denominacion_miembro_plural,
        denominacionOrganoGobierno:      form.denominacion_organo_gobierno,
        denominacionOrganoGobiernoPlural: form.denominacion_organo_gobierno_plural,
        authModo:                        form.auth_modo,
        authAutheliaUrl:                 form.auth_authelia_url,
        authOidcIssuer:                  form.auth_oidc_issuer,
        sessionInactividadMinutos:       form.session_inactividad_minutos,
        sessionMaximoMinutos:            form.session_maximo_minutos,
        smtpHost:                        form.smtp_host,
        smtpPort:                        form.smtp_port,
        smtpUsuario:                     form.smtp_usuario,
        smtpPassword:                    form.smtp_password,
        smtpFrom:                        form.smtp_from,
        smtpTls:                         form.smtp_tls,
        smtpSsl:                         form.smtp_ssl,
        indicoActivo:                    form.indico_activo,
        indicoUrl:                       form.indico_url,
        indicoApiToken:                  form.indico_api_token,
        tema:                            form.tema,
        fuentePrincipal:                 form.fuente_principal,
        sepaCreditorName:                form.sepa_creditor_name,
        sepaCreditorIban:                form.sepa_creditor_iban,
        sepaCreditorBic:                 form.sepa_creditor_bic,
        sepaCreditorId:                  form.sepa_creditor_id,
        openbankingActivo:               form.openbanking_activo,
        rgpdDpdNombre:                   form.rgpd_dpd_nombre,
        rgpdDpdEmail:                    form.rgpd_dpd_email,
        rgpdDpdTelefono:                 form.rgpd_dpd_telefono,
        rgpdDpdExterno:                  form.rgpd_dpd_externo,
        rgpdAniosRetencionBaja:          form.rgpd_anios_retencion_baja,
      }
    })
    await orgConfigStore.refreshConfig()
    const temaObj = orgConfigStore.temas.find(t => t.slug === form.tema) ?? form.tema
    temaOriginal.value   = typeof temaObj === 'object' ? temaObj : null
    fuenteOriginal.value = form.fuente_principal
    guardadoExitoso = true
    toast.success('Cambios guardados correctamente')
  } catch (e) {
    error.value = e?.response?.errors?.[0]?.message ?? 'Error al guardar'
  } finally {
    guardando.value = false
  }
}
</script>

<style scoped>
.label {
  @apply block text-sm font-medium text-slate-700 mb-1;
}
.input {
  @apply w-full h-10 rounded-lg border border-slate-300 px-3 text-sm text-slate-900
         placeholder:text-slate-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500
         focus:outline-none transition-colors bg-white;
}
</style>
