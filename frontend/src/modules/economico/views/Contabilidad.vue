<template>
  <AppLayout title="Contabilidad" :subtitle="contabilidadCompleja
    ? 'Plan de cuentas PCESFL 2013, asientos y balances'
    : 'Contabilidad simplificada: categorías fiscales y libro de ingresos y gastos'">

    <!-- Tabs -->
    <div class="border-b border-gray-200 mb-6 flex items-center justify-between">
      <nav class="-mb-px flex space-x-6">
        <button v-for="tab in tabs" :key="tab.id"
          @click="activeTab = tab.id"
          :class="[activeTab === tab.id ? 'border-purple-500 text-purple-600' : 'border-transparent text-gray-500 hover:text-gray-700', 'py-3 px-1 border-b-2 font-medium text-sm']"
        >{{ tab.icon }} {{ tab.name }}</button>
      </nav>
      <router-link to="/economico/cierre-ejercicio"
        class="px-3 py-1.5 bg-purple-600 text-white text-xs font-medium rounded-lg hover:bg-purple-700">
        Cierre del ejercicio →
      </router-link>
    </div>

    <!-- Tab Plan de Cuentas / Categorías Fiscales según el modo -->
    <div v-if="activeTab === 'plan'">
      <!-- Modo simplificado: categorías fiscales y reglas de clasificación -->
      <div v-if="!contabilidadCompleja">
        <div class="flex gap-2 mb-4">
          <button @click="subTabSimplificado = 'categorias'"
            :class="subTabSimplificado === 'categorias' ? 'bg-purple-100 text-purple-700' : 'text-gray-500 hover:bg-gray-100'"
            class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors">
            🏷️ Categorías
          </button>
          <button @click="subTabSimplificado = 'reglas'"
            :class="subTabSimplificado === 'reglas' ? 'bg-purple-100 text-purple-700' : 'text-gray-500 hover:bg-gray-100'"
            class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors">
            ⚙️ Reglas de clasificación
          </button>
        </div>
        <CategoriasFiscalesPanel v-if="subTabSimplificado === 'categorias'" />
        <ReglasCategorizacionPanel v-else />
      </div>

      <!-- Modo completo: plan de cuentas PCESFL -->
      <template v-else>
      <FilterBar
        v-model="filtrosPlan"
        v-model:search="busquedaPlan"
        search-placeholder="Buscar por código o nombre…"
        create-label="+ Nueva cuenta"
        :fields="camposFiltroPlan"
        :description="descripcionFiltro"
        @create="abrirNuevaCuenta()"
      />

      <!-- Controles de vista del árbol -->
      <div class="flex items-center justify-between mt-3 mb-2 px-1">
        <button
          @click="toggleTodos"
          class="inline-flex items-center gap-1 text-xs text-purple-600 hover:text-purple-800"
          :title="todoExpandido ? 'Colapsar todo' : 'Expandir todo'"
        >
          <span class="inline-block w-3 text-center">{{ todoExpandido ? '▼' : '▶' }}</span>
          {{ todoExpandido ? 'Colapsar todo' : 'Expandir todo' }}
        </button>
        <div class="text-xs text-gray-500">
          {{ totalCuentasVisibles }} de {{ cuentasContables.length }} cuentas
          <span v-if="busquedaPlan || hayFiltroPlanActivo" class="ml-1 text-purple-600">(filtrado)</span>
        </div>
      </div>

      <!-- Árbol jerárquico -->
      <div v-if="arbolCuentasFiltrado.length" class="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100">
        <CuentaNode
          v-for="raiz in arbolCuentasFiltrado"
          :key="raiz.id"
          :cuenta="raiz"
          :saldos="saldosCuentas"
          :busqueda="busquedaPlan"
          @add-sub="abrirNuevaSubcuenta"
          @editar="abrirEditarCuenta"
        />
      </div>
      <p v-else-if="!cuentasContables.length" class="text-center text-gray-400 py-8 border border-dashed border-gray-200 rounded-lg">
        No hay cuentas contables. Inicializa el plan de cuentas PCESFL 2013.
      </p>
      <p v-else class="text-center text-gray-400 py-8 border border-dashed border-gray-200 rounded-lg">
        Ningún resultado para los filtros aplicados.
      </p>
      </template>
    </div>

    <!-- Tab Asientos -->
    <!-- Tab Bitácora: vista orientada al evento de negocio (ApunteCaja con su asiento) -->
    <div v-if="activeTab === 'bitacora'">
      <div class="flex flex-wrap items-end justify-between gap-3 mb-4">
        <div class="flex flex-wrap items-end gap-3">
          <div>
            <label class="label">Ejercicio</label>
            <select v-model.number="bitacoraEjercicio" class="input-sm">
              <option v-for="y in ejerciciosDisponibles" :key="y" :value="y">{{ y }}</option>
            </select>
          </div>
          <div>
            <label class="label">Tipo</label>
            <select v-model="bitacoraTipo" class="input-sm">
              <option value="">Todos</option>
              <option value="INGRESO">Ingresos</option>
              <option value="GASTO">Gastos</option>
              <option value="TRANSFERENCIA">Transferencias</option>
            </select>
          </div>
          <div>
            <label class="label">Origen</label>
            <select v-model="bitacoraOrigen" class="input-sm">
              <option value="">Todos</option>
              <option value="CUOTA">Cuotas</option>
              <option value="DONACION">Donaciones</option>
              <option value="REMESA">Remesas</option>
              <option value="JUSTIFICANTE_GASTO">Justificantes</option>
              <option value="ACTIVIDAD">Actividades</option>
              <option value="MANUAL">Manuales</option>
              <option value="PAYPAL">PayPal</option>
            </select>
          </div>
          <div>
            <label class="label">Buscar</label>
            <input v-model="bitacoraBusqueda" type="text" placeholder="Concepto, ref…"
                   class="input-sm w-56" />
          </div>
          <div v-if="!contabilidadCompleja" class="flex flex-wrap items-end gap-3">
            <label class="flex items-center gap-2 cursor-pointer select-none pb-1.5">
              <input type="checkbox" v-model="bitacoraSoloSinClasificar"
                class="w-4 h-4 text-purple-600 rounded focus:ring-purple-500" />
              <span class="text-sm text-gray-600">Solo sin clasificar</span>
            </label>
            <button @click="clasificarPendientes" :disabled="clasificandoPendientes"
              class="px-3 py-1.5 text-sm font-medium text-purple-700 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 disabled:opacity-50">
              {{ clasificandoPendientes ? 'Clasificando…' : '⚡ Clasificar pendientes' }}
            </button>
          </div>
        </div>
        <div class="text-xs text-gray-500">
          {{ movimientosFiltrados.length }} de {{ movimientos.length }} movimientos
        </div>
      </div>

      <p v-if="mensajeClasificacion"
        class="mb-3 text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg px-3 py-2">
        {{ mensajeClasificacion }}
      </p>

      <!-- Barra de acción masiva (modo simplificado, con selección) -->
      <div v-if="!contabilidadCompleja && seleccionApuntes.size > 0"
        class="mb-3 flex items-center gap-3 bg-purple-50 border border-purple-200 rounded-lg px-4 py-2.5">
        <span class="text-sm font-medium text-purple-800">{{ seleccionApuntes.size }} seleccionados</span>
        <select v-model="categoriaMasiva" class="input-sm flex-1 max-w-xs">
          <option :value="null">Asignar categoría…</option>
          <optgroup label="Ingresos">
            <option v-for="c in categoriasFiscales.filter(x => x.tipo === 'INGRESO')" :key="c.id" :value="c.id">{{ c.nombre }}</option>
          </optgroup>
          <optgroup label="Gastos">
            <option v-for="c in categoriasFiscales.filter(x => x.tipo === 'GASTO')" :key="c.id" :value="c.id">{{ c.nombre }}</option>
          </optgroup>
        </select>
        <button @click="aplicarCategoriaMasiva" :disabled="!categoriaMasiva || aplicandoMasiva"
          class="px-3 py-1.5 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50">
          {{ aplicandoMasiva ? 'Aplicando…' : 'Aplicar' }}
        </button>
        <button @click="limpiarSeleccion" class="text-sm text-gray-500 hover:text-gray-700">Cancelar</button>
      </div>

      <div v-if="cargandoBitacora" class="py-12 text-center text-slate-400 text-sm">Cargando bitácora…</div>
      <div v-else-if="movimientosFiltrados.length" class="overflow-x-auto bg-white border border-gray-200 rounded-lg">
        <table class="min-w-full text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th v-if="!contabilidadCompleja" class="px-3 py-2 text-center w-8">
                <input type="checkbox" :checked="todosVisiblesSeleccionados" @change="toggleSeleccionTodos"
                  class="w-4 h-4 text-purple-600 rounded focus:ring-purple-500" />
              </th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Fecha</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Origen</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Concepto</th>
              <th v-if="!contabilidadCompleja" class="px-3 py-2 text-left text-xs font-medium text-gray-500">Categoría</th>
              <th class="px-3 py-2 text-right text-xs font-medium text-gray-500">Importe</th>
              <th class="px-3 py-2 text-center text-xs font-medium text-gray-500">Tipo</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Cuenta</th>
              <th class="px-3 py-2 text-center text-xs font-medium text-gray-500">Conc.</th>
              <th class="px-3 py-2 text-center text-xs font-medium text-gray-500">Asiento</th>
              <th class="px-3 py-2 text-center text-xs font-medium text-gray-500">Estado</th>
              <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 w-24">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="m in movimientosFiltrados" :key="m.id" class="hover:bg-gray-50"
                :class="!contabilidadCompleja && estaSeleccionado(m.id) ? 'bg-purple-50/50' : ''">
              <td v-if="!contabilidadCompleja" class="px-3 py-1.5 text-center">
                <input type="checkbox" :checked="estaSeleccionado(m.id)" @change="toggleSeleccion(m.id)"
                  class="w-4 h-4 text-purple-600 rounded focus:ring-purple-500" />
              </td>
              <td class="px-3 py-1.5 text-xs text-gray-600 whitespace-nowrap">{{ fechaFmt(m.fecha) }}</td>
              <td class="px-3 py-1.5">
                <span :class="badgeOrigen(m.origen)" class="text-[10px] uppercase rounded px-1.5 py-0.5">
                  {{ origenLabel(m.origen) }}
                </span>
              </td>
              <td class="px-3 py-1.5 text-gray-800 max-w-md truncate" :title="m.concepto">{{ m.concepto }}</td>
              <td v-if="!contabilidadCompleja" class="px-3 py-1.5">
                <span v-if="m.categoriaFiscalId" class="inline-flex items-center gap-1.5 text-xs">
                  <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: colorCategoriaFiscal(m.categoriaFiscalId) }"></span>
                  {{ nombreCategoriaFiscal(m.categoriaFiscalId) }}
                </span>
                <span v-else class="text-xs text-amber-500 italic">sin clasificar</span>
              </td>
              <td class="px-3 py-1.5 text-right font-mono"
                  :class="m.tipo === 'INGRESO' ? 'text-green-700' : (m.tipo === 'GASTO' ? 'text-red-600' : 'text-gray-700')">
                {{ m.tipo === 'GASTO' ? '−' : (m.tipo === 'INGRESO' ? '+' : '') }}{{ fmt(m.importe) }}
              </td>
              <td class="px-3 py-1.5 text-center">
                <span :class="badgeTipoMov(m.tipo)" class="text-[10px] uppercase rounded px-1.5 py-0.5">
                  {{ m.tipo }}
                </span>
              </td>
              <td class="px-3 py-1.5 text-xs text-gray-500">{{ m.cuentaBancaria?.nombre || '—' }}</td>
              <td class="px-3 py-1.5 text-center">
                <button @click="toggleConciliado(m)" :title="m.conciliado ? 'Conciliado — clic para desconciliar' : 'Sin conciliar — clic para marcar'"
                        :class="m.conciliado ? 'text-green-600' : 'text-gray-300 hover:text-amber-500'">
                  {{ m.conciliado ? '●' : '○' }}
                </button>
              </td>
              <td class="px-3 py-1.5 text-center">
                <button v-if="asientoDe(m.asientoId)" @click="abrirAsientoDetalle(asientoDe(m.asientoId))"
                        class="text-xs font-mono text-indigo-600 hover:underline">
                  #{{ String(asientoDe(m.asientoId).numeroAsiento).padStart(4, '0') }}
                </button>
                <span v-else class="text-xs text-gray-300">—</span>
              </td>
              <td class="px-3 py-1.5 text-center">
                <span v-if="asientoDe(m.asientoId)" :class="badgeEstado(estadoLimpio(asientoDe(m.asientoId).estado))"
                      class="text-[10px] uppercase rounded px-1.5 py-0.5">
                  {{ estadoLabel(asientoDe(m.asientoId).estado) }}
                </span>
                <span v-else class="text-[10px] text-gray-400">sin asiento</span>
              </td>
              <td class="px-3 py-1.5 text-center">
                <button @click="abrirEdicionApunte(m)" title="Editar metadatos"
                        class="p-1 text-gray-400 hover:text-blue-600">
                  ✏️
                </button>
                <button @click="abrirAnulacionApunte(m)" title="Anular (genera contraapunte)"
                        class="p-1 text-gray-400 hover:text-red-600">
                  🗑
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="text-center text-gray-400 py-8 border border-dashed border-gray-200 rounded-lg">
        No hay movimientos para los filtros aplicados.
      </p>
    </div>

    <div v-if="activeTab === 'asientos'">
      <div class="flex justify-between items-center mb-4">
        <div class="flex items-center gap-3">
          <h3 class="font-semibold text-gray-800">Asientos contables</h3>
          <select v-model="filtroEjercicio" class="input-sm" @change="recargarAsientos">
            <option v-for="y in ejerciciosDisponibles" :key="y" :value="y">{{ y }}</option>
          </select>
          <select v-model="filtroEstado" class="input-sm" @change="recargarAsientos">
            <option value="">Todos</option>
            <option value="BORRADOR">Borrador</option>
            <option value="CONFIRMADO">Confirmado</option>
            <option value="ANULADO">Anulado</option>
          </select>
        </div>
        <button @click="abrirNuevoAsiento" class="btn-primary">+ Nuevo asiento</button>
      </div>

      <div v-if="asientosContables.length" class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Nº</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Fecha</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Glosa</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Tipo</th>
              <th class="px-3 py-2 text-center text-xs font-medium text-gray-500">Estado</th>
              <th class="px-3 py-2 text-center text-xs font-medium text-gray-500">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="a in asientosContables" :key="a.id" class="hover:bg-gray-50">
              <td class="px-3 py-2 font-mono text-gray-500">{{ String(a.numeroAsiento).padStart(4, '0') }}</td>
              <td class="px-3 py-2 text-gray-600 whitespace-nowrap">{{ fechaFmt(a.fecha) }}</td>
              <td class="px-3 py-2 text-gray-900">{{ a.glosa }}</td>
              <td class="px-3 py-2 text-xs text-gray-500">{{ tipoAsientoLabel(a.tipoAsiento) }}</td>
              <td class="px-3 py-2 text-center">
                <span class="text-xs rounded px-2 py-0.5" :class="badgeEstado(estadoLimpio(a.estado))">{{ estadoLabel(a.estado) }}</span>
              </td>
              <td class="px-3 py-2 text-center">
                <button v-if="a.estado === 'BORRADOR'" @click="confirmarAsiento(a.id)"
                  class="text-xs text-green-600 hover:underline mr-2">Confirmar</button>
                <button v-if="a.estado !== 'ANULADO'" @click="anularAsiento(a.id)"
                  class="text-xs text-red-500 hover:underline">Anular</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="text-center text-gray-400 py-8">No hay asientos para el ejercicio {{ filtroEjercicio }}.</p>
    </div>

    <!-- Tab Sumas y saldos (calculadora al vuelo, NO se persiste) -->
    <div v-if="activeTab === 'balances'">
      <div class="flex flex-wrap items-end gap-3 mb-4">
        <div>
          <label class="label">Ejercicio</label>
          <select v-model.number="balanceEjercicio" class="input-sm">
            <option v-for="y in ejerciciosDisponibles" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
        <div>
          <label class="label">Fecha de corte</label>
          <input type="date" v-model="balanceFechaCorte" class="input-sm" />
        </div>
        <label class="flex items-center gap-2 text-sm text-gray-700">
          <input type="checkbox" v-model="balanceSoloConSaldo" />
          Solo cuentas con movimiento
        </label>
        <button @click="calcularBalance" :disabled="calculandoBalance" class="btn-primary ml-auto">
          {{ calculandoBalance ? 'Calculando…' : 'Calcular' }}
        </button>
      </div>
      <p class="text-xs text-gray-500 mb-4">
        Incluye solo asientos confirmados con fecha ≤ fecha de corte. Es una foto del libro mayor; no se archiva.
      </p>

      <div v-if="lineasBalanceSumasSaldos.length">
        <div class="overflow-x-auto bg-white border border-gray-200 rounded-lg">
          <table class="min-w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Código</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Cuenta</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Tipo</th>
                <th class="px-3 py-2 text-right text-xs font-medium text-gray-500">Debe</th>
                <th class="px-3 py-2 text-right text-xs font-medium text-gray-500">Haber</th>
                <th class="px-3 py-2 text-right text-xs font-medium text-gray-500">Saldo</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="l in lineasBalanceSumasSaldos" :key="l.codigo" class="hover:bg-gray-50">
                <td class="px-3 py-1.5 font-mono text-xs text-gray-600">{{ l.codigo }}</td>
                <td class="px-3 py-1.5 text-gray-900">{{ l.nombre }}</td>
                <td class="px-3 py-1.5">
                  <span class="text-[10px] uppercase rounded px-1.5 py-0.5" :class="badgeTipo(stripEnum(l.tipo))">{{ stripEnum(l.tipo) }}</span>
                </td>
                <td class="px-3 py-1.5 text-right font-mono text-gray-700">{{ l.totalDebe ? fmt(l.totalDebe) : '—' }}</td>
                <td class="px-3 py-1.5 text-right font-mono text-gray-700">{{ l.totalHaber ? fmt(l.totalHaber) : '—' }}</td>
                <td class="px-3 py-1.5 text-right font-mono" :class="l.saldo >= 0 ? 'text-gray-900' : 'text-red-600'">{{ fmt(l.saldo) }}</td>
              </tr>
            </tbody>
            <tfoot class="bg-gray-50 font-semibold">
              <tr>
                <td colspan="3" class="px-3 py-2 text-right text-gray-700">Totales</td>
                <td class="px-3 py-2 text-right font-mono text-gray-900">{{ fmt(totalDebeBalance) }}</td>
                <td class="px-3 py-2 text-right font-mono text-gray-900">{{ fmt(totalHaberBalance) }}</td>
                <td class="px-3 py-2 text-right font-mono" :class="diferenciaBalance === 0 ? 'text-green-600' : 'text-red-600'">
                  {{ diferenciaBalance === 0 ? '✓ cuadra' : fmt(diferenciaBalance) }}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
      <p v-else class="text-center text-gray-400 py-8 border border-dashed border-gray-200 rounded-lg">
        Selecciona ejercicio y fecha de corte y pulsa <b>Calcular</b>.
      </p>
    </div>

    <LoadSpinner v-if="loading" />

    <!-- MODAL: Nueva cuenta contable -->
    <div v-if="modalCuenta" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="modalCuenta = false">
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
        <h3 class="text-lg font-semibold mb-4">
          <template v-if="modoEdicion">Editar cuenta <span class="font-mono text-purple-700">{{ formCuenta.codigo }}</span></template>
          <template v-else>{{ formCuenta.padreId ? 'Nueva subcuenta' : 'Nueva cuenta contable' }}</template>
        </h3>
        <div class="space-y-3">
          <div v-if="formCuenta.padreId && !modoEdicion" class="bg-purple-50 border border-purple-200 rounded-lg px-3 py-2 text-xs text-purple-700">
            Bajo: <span class="font-mono">{{ formCuenta.padreLabel }}</span>
          </div>
          <div v-if="modoEdicion && cuentaBloqueada" class="bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 text-xs text-amber-800">
            ⚠ Esta cuenta tiene apuntes en asientos confirmados.
            Solo se permite renombrar, editar la descripción y activar/desactivar.
            Los campos estructurales (código, tipo, nivel) no se pueden modificar para preservar la integridad contable.
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="label">Código *</label>
              <input v-model="formCuenta.codigo" :disabled="modoEdicion && cuentaBloqueada"
                class="input font-mono disabled:bg-gray-100 disabled:text-gray-500"
                placeholder="Ej: 572" />
            </div>
            <div>
              <label class="label">Nivel *</label>
              <select v-model.number="formCuenta.nivel" :disabled="modoEdicion && cuentaBloqueada"
                class="input disabled:bg-gray-100 disabled:text-gray-500">
                <option :value="1">1 — Grupo</option>
                <option :value="2">2 — Subgrupo</option>
                <option :value="3">3 — Cuenta</option>
              </select>
            </div>
          </div>
          <div>
            <label class="label">Nombre *</label>
            <input v-model="formCuenta.nombre" class="input" placeholder="Ej: Bancos e instituciones de crédito" />
          </div>
          <div>
            <label class="label">Tipo *</label>
            <select v-model="formCuenta.tipo" :disabled="modoEdicion && cuentaBloqueada"
              class="input disabled:bg-gray-100 disabled:text-gray-500">
              <option value="ACTIVO">Activo</option>
              <option value="PASIVO">Pasivo</option>
              <option value="PATRIMONIO">Patrimonio</option>
              <option value="INGRESO">Ingreso</option>
              <option value="GASTO">Gasto</option>
            </select>
            <p v-if="!modoEdicion && formCuenta.padreId" class="text-xs text-gray-400 mt-0.5">
              Por defecto hereda del padre, pero puedes cambiarlo (en PCESFL los grupos 1, 4 y 5 mezclan Activo/Pasivo).
            </p>
          </div>
          <div class="flex items-center gap-4">
            <label class="flex items-center gap-2 text-sm text-gray-700">
              <input type="checkbox" v-model="formCuenta.esDotacion" />
              Elemento de dotación fundacional
            </label>
            <label v-if="modoEdicion" class="flex items-center gap-2 text-sm text-gray-700">
              <input type="checkbox" v-model="formCuenta.activa" />
              Cuenta activa
            </label>
            <label v-if="modoEdicion && !cuentaBloqueada" class="flex items-center gap-2 text-sm text-gray-700">
              <input type="checkbox" v-model="formCuenta.permiteAsiento" />
              Permite apuntes
            </label>
          </div>
          <div>
            <label class="label">Descripción</label>
            <textarea v-model="formCuenta.descripcion" class="input h-16" />
          </div>
        </div>
        <ErrorAlert v-if="errorModal" :message="errorModal" />
        <div class="flex justify-end gap-3 mt-5">
          <button @click="modalCuenta = false" class="btn-secondary">Cancelar</button>
          <button @click="guardarCuenta" :disabled="guardando" class="btn-primary">
            {{ guardando ? 'Guardando…' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- MODAL: Nuevo asiento -->
    <div v-if="modalAsiento" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="modalAsiento = false">
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-lg mx-4">
        <h3 class="text-lg font-semibold mb-4">Nuevo asiento contable</h3>
        <div class="space-y-3">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="label">Ejercicio *</label>
              <input type="number" v-model="formAsiento.ejercicio" class="input" />
            </div>
            <div>
              <label class="label">Fecha *</label>
              <input type="date" v-model="formAsiento.fecha" class="input" />
            </div>
          </div>
          <div>
            <label class="label">Glosa (descripción) *</label>
            <input v-model="formAsiento.glosa" class="input" placeholder="Descripción del asiento" />
          </div>
          <div>
            <label class="label">Tipo</label>
            <select v-model="formAsiento.tipoAsiento" class="input">
              <option value="GESTION">Gestión</option>
              <option value="APERTURA">Apertura</option>
              <option value="REGULARIZACION">Regularización</option>
              <option value="CIERRE">Cierre</option>
            </select>
          </div>
          <div>
            <label class="label">Observaciones</label>
            <textarea v-model="formAsiento.observaciones" class="input h-16" />
          </div>
          <p class="text-xs text-gray-500">El asiento se crea en estado BORRADOR. Añade los apuntes debe/haber y luego confírmalo.</p>
        </div>
        <ErrorAlert v-if="errorModal" :message="errorModal" />
        <div class="flex justify-end gap-3 mt-5">
          <button @click="modalAsiento = false" class="btn-secondary">Cancelar</button>
          <button @click="guardarAsiento" :disabled="guardando" class="btn-primary">
            {{ guardando ? 'Creando…' : 'Crear asiento' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: editar metadatos de apunte -->
    <div v-if="modalEditApunte" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4"
         @click.self="modalEditApunte = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-xl">
        <div class="px-6 py-4 border-b border-slate-200">
          <h3 class="font-semibold text-slate-800">Editar metadatos del apunte</h3>
          <p class="text-xs text-slate-500 mt-0.5">
            Importe, fecha y tipo no son editables. Para corregir esos, anula el apunte y crea uno nuevo.
          </p>
        </div>
        <div class="px-6 py-5 space-y-3">
          <div class="text-xs text-slate-500 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 bg-slate-50 p-3 rounded">
            <div><span class="text-slate-400">Fecha:</span> {{ fechaFmt(formApunte.fecha) }}</div>
            <div><span class="text-slate-400">Importe:</span> <span class="font-mono">{{ fmt(formApunte.importe) }}</span></div>
            <div><span class="text-slate-400">Tipo:</span> {{ formApunte.tipo }}</div>
          </div>
          <div>
            <label class="label">Concepto *</label>
            <input v-model="formApunte.concepto" class="input" />
          </div>
          <div>
            <label class="label">Observaciones</label>
            <textarea v-model="formApunte.observaciones" rows="2" class="input" />
          </div>
          <ImputacionActividadPicker
            v-model="imputacionApunte"
            :campanias="campaniasBitacora"
            :actividades="actividadesBitacora"
            :allow-sin-imputar="true"
            :required="false"
          />
          <ErrorAlert v-if="formApunte.error" :message="formApunte.error" />
        </div>
        <div class="flex justify-end gap-3 px-6 py-4 border-t border-slate-200">
          <button @click="modalEditApunte = false" class="btn-secondary">Cancelar</button>
          <button @click="guardarEdicionApunte" :disabled="ocupadoApunte" class="btn-primary">
            {{ ocupadoApunte ? 'Guardando…' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: anular apunte -->
    <div v-if="modalAnularApunte" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4"
         @click.self="modalAnularApunte = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md">
        <div class="px-6 py-4 border-b border-slate-200">
          <h3 class="font-semibold text-slate-800">Anular apunte de caja</h3>
          <p class="text-xs text-slate-500 mt-0.5">
            Se generará un contraapunte con importe inverso. El apunte original se mantiene
            por inmutabilidad contable; el asiento contable asociado se anula también.
          </p>
        </div>
        <div class="px-6 py-5 space-y-3">
          <div class="text-xs text-slate-500 bg-slate-50 p-3 rounded">
            <div><strong>{{ fechaFmt(formAnular.fecha) }}</strong> · {{ formAnular.tipo }} · <span class="font-mono">{{ fmt(formAnular.importe) }}</span></div>
            <div class="mt-1">{{ formAnular.concepto }}</div>
          </div>
          <div>
            <label class="label">Motivo de la anulación *</label>
            <textarea v-model="formAnular.motivo" rows="3" class="input"
                      placeholder="Ej.: importe equivocado, duplicado, error de fecha…" />
          </div>
          <ErrorAlert v-if="formAnular.error" :message="formAnular.error" />
        </div>
        <div class="flex justify-end gap-3 px-6 py-4 border-t border-slate-200">
          <button @click="modalAnularApunte = false" class="btn-secondary">Cancelar</button>
          <button @click="confirmarAnulacionApunte" :disabled="ocupadoApunte"
                  class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium disabled:opacity-50">
            {{ ocupadoApunte ? 'Anulando…' : 'Anular apunte' }}
          </button>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { ref, reactive, computed, onMounted, provide, watch } from 'vue'
import AppLayout from '@/components/common/AppLayout.vue'
import LoadSpinner from '@/components/common/LoadSpinner.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import ImputacionActividadPicker from '@/components/common/ImputacionActividadPicker.vue'
import CuentaNode from './CuentaNode.vue'
import CategoriasFiscalesPanel from '@/components/common/CategoriasFiscalesPanel.vue'
import ReglasCategorizacionPanel from '@/components/common/ReglasCategorizacionPanel.vue'
import { useContabilidad } from '@/composables/useContabilidad'
import { useGraphQL } from '@/composables/useGraphQL'
import {
  GET_BITACORA_MOVIMIENTOS,
  MARCAR_APUNTE_CONCILIADO,
  DESMARCAR_APUNTE_CONCILIADO,
  ACTUALIZAR_METADATOS_APUNTE,
  ANULAR_APUNTE_CAJA,
} from '@/graphql/queries/tesoreria'
import { GET_ACTIVIDADES_PARA_GASTO } from '@/graphql/queries/economico'
import { GET_CAMPANIAS } from '@/graphql/queries/campanias'
import {
  ASIGNAR_CATEGORIA_MASIVA,
  CLASIFICAR_APUNTES_PENDIENTES,
} from '@/graphql/queries/categorias_fiscales.js'

const toast = useToast()
const confirmDialog = useConfirm()

const {
  cuentasContables,
  asientosContables,
  lineasBalanceSumasSaldos,
  saldosCuentas,
  loading,
  obtenerPlanCuentas,
  obtenerSaldosCuentas,
  obtenerAsientos,
  calcularBalanceSumasYSaldos,
  crearCuentaContable,
  actualizarCuentaContable,
  cuentaTieneApuntesConfirmados,
  crearAsiento,
  confirmarAsientoContable,
  anularAsientoContable,
} = useContabilidad()

const activeTab = ref('plan')
const contabilidadCompleja = ref(true)  // se carga en onMounted; true por defecto (no degrada la vista completa)
const subTabSimplificado = ref('categorias')  // categorias | reglas (solo modo simplificado)
const filtroEjercicio = ref(new Date().getFullYear())
const filtroEstado = ref('')

// Calculadora del balance de sumas y saldos (no se persiste)
const balanceEjercicio = ref(new Date().getFullYear())
const balanceFechaCorte = ref(new Date().toISOString().split('T')[0])
const balanceSoloConSaldo = ref(true)
const calculandoBalance = ref(false)

const modalCuenta = ref(false)
const modalAsiento = ref(false)
const guardando = ref(false)
const errorModal = ref('')
const modoEdicion = ref(false)        // false=crear, true=editar
const cuentaBloqueada = ref(false)    // true si la cuenta tiene apuntes confirmados

const formCuenta = ref({ codigo: '', nombre: '', tipo: 'ACTIVO', nivel: 3, padreId: null, esDotacion: false, descripcion: '', activa: true, permiteAsiento: true })
const formAsiento = ref({ ejercicio: new Date().getFullYear(), fecha: new Date().toISOString().split('T')[0], glosa: '', tipoAsiento: 'GESTION', observaciones: '' })

// ─── Estado del Plan de Cuentas: filtros, búsqueda y nodos expandidos ───
const busquedaPlan = ref('')
const filtrosPlan = ref({
  tipos: [],          // multiselect: ACTIVO/PASIVO/PATRIMONIO/INGRESO/GASTO
  soloHojas: false,   // solo cuentas que permiten asientos (nivel 3 típicamente)
  conSaldo: false,    // solo con saldo distinto de 0
  inactivas: false,   // incluir cuentas inactivas
})
// Objeto reactivo plano {id: true}. reactive() intercepta add/delete de propiedades
const expandedMap = reactive({})

const camposFiltroPlan = [
  {
    key: 'tipos',
    label: 'Tipo',
    type: 'multiselect',
    options: [
      { value: 'ACTIVO',     label: 'Activo' },
      { value: 'PASIVO',     label: 'Pasivo' },
      { value: 'PATRIMONIO', label: 'Patrimonio' },
      { value: 'INGRESO',    label: 'Ingreso' },
      { value: 'GASTO',      label: 'Gasto' },
    ],
    allLabel: 'Todos los tipos',
  },
  { key: 'soloHojas',  label: 'Solo hojas', type: 'toggle' },
  { key: 'conSaldo',   label: 'Con saldo',  type: 'toggle' },
  { key: 'inactivas',  label: 'Incluir inactivas', type: 'toggle' },
]

const descripcionFiltro = computed(() => {
  const parts = []
  if (filtrosPlan.value.tipos?.length) parts.push(`${filtrosPlan.value.tipos.length} tipo(s)`)
  if (filtrosPlan.value.soloHojas) parts.push('solo hojas')
  if (filtrosPlan.value.conSaldo) parts.push('con saldo')
  if (filtrosPlan.value.inactivas) parts.push('incluye inactivas')
  if (busquedaPlan.value) parts.push(`búsqueda "${busquedaPlan.value}"`)
  return parts.join(' · ')
})

const hayFiltroPlanActivo = computed(() =>
  (filtrosPlan.value.tipos?.length > 0) ||
  filtrosPlan.value.soloHojas ||
  filtrosPlan.value.conSaldo ||
  filtrosPlan.value.inactivas
)

// ─── Construcción del árbol jerárquico ──────────────────────────────────
const arbolCuentas = computed(() => {
  const map = new Map()
  const raices = []
  // 1ª pasada: crear nodos
  for (const c of cuentasContables.value) {
    map.set(c.id, { ...c, hijos: [] })
  }
  // 2ª pasada: enlazar padre/hijo
  for (const node of map.values()) {
    if (node.padreId && map.has(node.padreId)) {
      map.get(node.padreId).hijos.push(node)
    } else {
      raices.push(node)
    }
  }
  // Ordenar todos los niveles por código
  const ordenar = (nodes) => {
    nodes.sort((a, b) => String(a.codigo).localeCompare(String(b.codigo)))
    for (const n of nodes) ordenar(n.hijos)
  }
  ordenar(raices)
  return raices
})

// Filtra el árbol — un nodo se mantiene si él coincide O algún descendiente coincide
const cuentaCoincide = (c) => {
  if (!filtrosPlan.value.inactivas && c.activa === false) return false
  if (filtrosPlan.value.tipos?.length && !filtrosPlan.value.tipos.includes(c.tipo)) return false
  if (filtrosPlan.value.soloHojas && !c.permiteAsiento) return false
  if (filtrosPlan.value.conSaldo) {
    const s = saldosCuentas.value[c.codigo]
    if (!s || Math.abs(s) < 0.005) return false
  }
  if (busquedaPlan.value) {
    const q = busquedaPlan.value.toLowerCase()
    if (!(String(c.codigo).toLowerCase().includes(q) || (c.nombre || '').toLowerCase().includes(q))) return false
  }
  return true
}

const filtrarArbol = (nodes) => {
  const res = []
  for (const n of nodes) {
    const hijosFiltrados = filtrarArbol(n.hijos)
    if (cuentaCoincide(n) || hijosFiltrados.length) {
      res.push({ ...n, hijos: hijosFiltrados })
    }
  }
  return res
}

const arbolCuentasFiltrado = computed(() => filtrarArbol(arbolCuentas.value))

const totalCuentasVisibles = computed(() => {
  let n = 0
  const contar = (nodes) => {
    for (const x of nodes) { n++; contar(x.hijos) }
  }
  contar(arbolCuentasFiltrado.value)
  return n
})

// ─── Expandir / colapsar ────────────────────────────────────────────────
const toggleNodo = (id) => {
  if (expandedMap[id]) delete expandedMap[id]
  else expandedMap[id] = true
}

const todosIds = (nodes) => {
  const ids = []
  const walk = (xs) => { for (const n of xs) { ids.push(n.id); walk(n.hijos) } }
  walk(nodes)
  return ids
}

const totalNodosExpandibles = computed(() => {
  let n = 0
  const walk = (xs) => { for (const x of xs) { if (x.hijos.length) { n++; walk(x.hijos) } } }
  walk(arbolCuentasFiltrado.value)
  return n
})

const nodosExpandidos = computed(() => Object.keys(expandedMap).length)

const todoExpandido = computed(() =>
  totalNodosExpandibles.value > 0 && nodosExpandidos.value >= totalNodosExpandibles.value
)

const toggleTodos = () => {
  if (todoExpandido.value) {
    for (const k of Object.keys(expandedMap)) delete expandedMap[k]
  } else {
    for (const id of todosIds(arbolCuentas.value)) expandedMap[id] = true
  }
}

// Provee a CuentaNode el objeto reactivo y la función de toggle
provide('expandedMap', expandedMap)
provide('toggleNodo', toggleNodo)

const tabs = computed(() => {
  if (!contabilidadCompleja.value) {
    // Modo simplificado: la estructura es de categorías fiscales; sin asientos ni balances de partida doble
    return [
      { id: 'plan', name: 'Categorías fiscales', icon: '🏷️' },
      { id: 'bitacora', name: 'Bitácora', icon: '📒' },
    ]
  }
  return [
    { id: 'plan', name: 'Plan de cuentas', icon: '📋' },
    { id: 'bitacora', name: 'Bitácora', icon: '📒' },
    { id: 'asientos', name: 'Asientos (técnico)', icon: '📝' },
    { id: 'balances', name: 'Sumas y saldos', icon: '⚖️' },
  ]
})

const ejercicioActual = computed(() => new Date().getFullYear())
const ejerciciosDisponibles = computed(() => {
  const year = new Date().getFullYear()
  return [year, year - 1, year - 2]
})

const asientosConfirmados = computed(() => asientosContables.value.filter(a => a.estado === 'CONFIRMADO'))
const asientosBorrador = computed(() => asientosContables.value.filter(a => a.estado === 'BORRADOR'))

// ── Bitácora de movimientos (pestaña nueva) ─────────────────────────────────
const { query: gqlQuery } = useGraphQL()
const movimientos = ref([])
const cargandoBitacora = ref(false)
const bitacoraEjercicio = ref(new Date().getFullYear())
const bitacoraTipo = ref('')
const bitacoraOrigen = ref('')
const bitacoraBusqueda = ref('')

// ── Clasificación masiva (solo modo simplificado) ──────────────────────────
const bitacoraSoloSinClasificar = ref(false)
const seleccionApuntes = ref(new Set())
const categoriasFiscales = ref([])
const categoriaMasiva = ref(null)
const aplicandoMasiva = ref(false)
const clasificandoPendientes = ref(false)
const mensajeClasificacion = ref('')

const cargarCategoriasFiscales = async () => {
  if (categoriasFiscales.value.length) return
  try {
    const data = await gqlQuery(`query { categoriasFiscales(activasSolo: true) { id codigo nombre tipo color } }`)
    categoriasFiscales.value = data?.categoriasFiscales ?? []
  } catch (e) {
    console.warn('No se pudieron cargar categorías fiscales:', e?.message)
  }
}

const nombreCategoriaFiscal = (id) => categoriasFiscales.value.find(c => c.id === id)?.nombre ?? null
const colorCategoriaFiscal = (id) => categoriasFiscales.value.find(c => c.id === id)?.color ?? '#9ca3af'

const cargarBitacora = async () => {
  cargandoBitacora.value = true
  try {
    const data = await gqlQuery(GET_BITACORA_MOVIMIENTOS)
    movimientos.value = (data.apuntesCaja || []).slice().sort(
      (a, b) => (b.fecha || '').localeCompare(a.fecha || '')
    )
  } catch (e) {
    console.error('Error cargando bitácora:', e?.message || e)
    movimientos.value = []
  } finally {
    cargandoBitacora.value = false
  }
}

const movimientosFiltrados = computed(() => {
  const q = bitacoraBusqueda.value.trim().toLowerCase()
  return movimientos.value.filter(m => {
    if (bitacoraEjercicio.value && !(m.fecha || '').startsWith(String(bitacoraEjercicio.value))) return false
    if (bitacoraTipo.value && m.tipo !== bitacoraTipo.value) return false
    if (bitacoraOrigen.value && m.origen !== bitacoraOrigen.value) return false
    if (bitacoraSoloSinClasificar.value && m.categoriaFiscalId) return false
    if (q) {
      const cs = (m.concepto || '').toLowerCase()
      const rf = (m.referenciaExterna || '').toLowerCase()
      if (!cs.includes(q) && !rf.includes(q)) return false
    }
    return true
  })
})

// ── Selección múltiple para clasificación masiva ───────────────────────────
const toggleSeleccion = (id) => {
  const s = new Set(seleccionApuntes.value)
  s.has(id) ? s.delete(id) : s.add(id)
  seleccionApuntes.value = s
}
const estaSeleccionado = (id) => seleccionApuntes.value.has(id)
const todosVisiblesSeleccionados = computed(() =>
  movimientosFiltrados.value.length > 0 &&
  movimientosFiltrados.value.every(m => seleccionApuntes.value.has(m.id))
)
const toggleSeleccionTodos = () => {
  seleccionApuntes.value = todosVisiblesSeleccionados.value
    ? new Set()
    : new Set(movimientosFiltrados.value.map(m => m.id))
}
const limpiarSeleccion = () => { seleccionApuntes.value = new Set() }

const origenLabel = (o) => ({
  CUOTA: 'Cuota',
  DONACION: 'Donación',
  REMESA: 'Remesa',
  JUSTIFICANTE_GASTO: 'Justificante',
  ACTIVIDAD: 'Actividad',
  MANUAL: 'Manual',
  PAYPAL: 'PayPal',
}[o] || (o || '—'))

const badgeOrigen = (o) => ({
  CUOTA:               'bg-blue-100 text-blue-700',
  DONACION:            'bg-emerald-100 text-emerald-700',
  REMESA:              'bg-indigo-100 text-indigo-700',
  JUSTIFICANTE_GASTO:  'bg-amber-100 text-amber-700',
  ACTIVIDAD:           'bg-sky-100 text-sky-700',
  MANUAL:              'bg-slate-100 text-slate-700',
  PAYPAL:              'bg-cyan-100 text-cyan-700',
}[o] || 'bg-slate-100 text-slate-600')

const badgeTipoMov = (t) => ({
  INGRESO:       'bg-green-100 text-green-700',
  GASTO:         'bg-red-100 text-red-700',
  TRANSFERENCIA: 'bg-slate-100 text-slate-700',
}[t] || 'bg-slate-100 text-slate-600')

// Resuelve el detalle del asiento de un apunte usando el cache ya cargado
// (asientosContables proviene de useContabilidad y se llena con recargarAsientos).
const asientoDe = (asientoId) => {
  if (!asientoId) return null
  return asientosContables.value.find(a => a.id === asientoId) || null
}

const abrirAsientoDetalle = (asiento) => {
  filtroEjercicio.value = asiento.ejercicio || filtroEjercicio.value
  activeTab.value = 'asientos'
}

// ── CRUD de apuntes: conciliar / editar / anular ───────────────────────────
const { mutation: gqlMutation } = useGraphQL()
const ocupadoApunte = ref(false)

// ── Acciones masivas de clasificación (modo simplificado) ──────────────────
const aplicarCategoriaMasiva = async () => {
  if (!categoriaMasiva.value || seleccionApuntes.value.size === 0) return
  aplicandoMasiva.value = true
  try {
    await gqlMutation(ASIGNAR_CATEGORIA_MASIVA, {
      apunteIds: Array.from(seleccionApuntes.value),
      categoriaFiscalId: categoriaMasiva.value,
    })
    limpiarSeleccion()
    categoriaMasiva.value = null
    await cargarBitacora()
  } catch (e) {
    console.error('Error en asignación masiva:', e?.message || e)
  } finally {
    aplicandoMasiva.value = false
  }
}

const clasificarPendientes = async () => {
  clasificandoPendientes.value = true
  try {
    const data = await gqlMutation(CLASIFICAR_APUNTES_PENDIENTES, {
      ejercicio: bitacoraEjercicio.value || null,
      forzar: false,
    })
    const r = data?.clasificarApuntesPendientes
    if (r) {
      mensajeClasificacion.value =
        `Se clasificaron ${r.clasificados} de ${r.procesados} apuntes pendientes.`
      setTimeout(() => { mensajeClasificacion.value = '' }, 5000)
    }
    await cargarBitacora()
  } catch (e) {
    console.error('Error al clasificar pendientes:', e?.message || e)
  } finally {
    clasificandoPendientes.value = false
  }
}

// Catálogo de campañas y actividades para el modal de edición.
const campaniasBitacora = ref([])
const actividadesBitacora = ref([])

const cargarCatalogosBitacora = async () => {
  try {
    const [ca, ac] = await Promise.all([
      gqlQuery(GET_CAMPANIAS),
      gqlQuery(GET_ACTIVIDADES_PARA_GASTO),
    ])
    campaniasBitacora.value = ca.campanias || []
    actividadesBitacora.value = ac.actividades || []
  } catch (e) {
    console.error('Error cargando catálogos de imputación:', e?.message || e)
  }
}

// Puente bidireccional con el componente ImputacionActividadPicker
const imputacionApunte = computed({
  get: () => ({
    modo:        formApunte.value.modoImputacion,
    campaniaId:  formApunte.value.campaniaId,
    actividadId: formApunte.value.actividadId,
    tipoFuera:   formApunte.value.tipoFuera,
  }),
  set: (v) => {
    formApunte.value.modoImputacion = v.modo
    formApunte.value.campaniaId     = v.campaniaId
    formApunte.value.actividadId    = v.actividadId
    formApunte.value.tipoFuera      = v.tipoFuera
  },
})

// Toggle conciliado/desconciliado desde la tabla
const toggleConciliado = async (m) => {
  try {
    if (m.conciliado) {
      await gqlMutation(DESMARCAR_APUNTE_CONCILIADO, { apunteId: m.id })
    } else {
      await gqlMutation(MARCAR_APUNTE_CONCILIADO, { apunteId: m.id, fechaConciliacion: null })
    }
    await cargarBitacora()
  } catch (e) {
    toast.error(errMsgApunte(e, 'Error al cambiar el estado de conciliación'))
  }
}

// Modal de edición de metadatos
const modalEditApunte = ref(false)
const formApunte = ref(_emptyApunteForm())
function _emptyApunteForm() {
  return {
    id: null, fecha: null, importe: 0, tipo: '', concepto: '', observaciones: '',
    modoImputacion: 'NINGUNA',  // CAMPANIA | FUERA | NINGUNA
    campaniaId: null, actividadId: null,
    tipoFuera: 'PERMANENTE',
    error: '',
  }
}

const abrirEdicionApunte = async (m) => {
  if (!campaniasBitacora.value.length) await cargarCatalogosBitacora()
  // Resolver modo de imputación inicial a partir del apunte
  let modo = 'NINGUNA'
  let tipoFuera = 'PERMANENTE'
  if (m.actividadId) {
    const act = actividadesBitacora.value.find(a => a.id === m.actividadId)
    if (act?.campaniaId) modo = 'CAMPANIA'
    else { modo = 'FUERA'; tipoFuera = act?.caracter || 'PERMANENTE' }
  }
  formApunte.value = {
    id: m.id,
    fecha: m.fecha, importe: m.importe, tipo: m.tipo,
    concepto: m.concepto || '',
    observaciones: m.observaciones || '',
    modoImputacion: modo,
    campaniaId: m.campaniaId || null,
    actividadId: m.actividadId || null,
    tipoFuera,
    error: '',
  }
  modalEditApunte.value = true
}

const guardarEdicionApunte = async () => {
  const f = formApunte.value
  f.error = ''
  if (!f.concepto?.trim()) { f.error = 'El concepto no puede quedar vacío'; return }
  if (f.modoImputacion !== 'NINGUNA' && !f.actividadId) {
    f.error = 'Selecciona la actividad o elige «Sin imputar»'; return
  }
  ocupadoApunte.value = true
  try {
    await gqlMutation(ACTUALIZAR_METADATOS_APUNTE, {
      apunteId: f.id,
      concepto: f.concepto.trim(),
      observaciones: f.observaciones || null,
      actividadId: f.modoImputacion === 'NINGUNA' ? null : f.actividadId,
      campaniaId: null,  // se deriva en backend
      limpiarActividad: f.modoImputacion === 'NINGUNA',
    })
    modalEditApunte.value = false
    await cargarBitacora()
  } catch (e) {
    f.error = errMsgApunte(e, 'Error al guardar la edición')
  } finally { ocupadoApunte.value = false }
}

// Modal de anulación
const modalAnularApunte = ref(false)
const formAnular = ref({ id: null, fecha: null, tipo: '', importe: 0, concepto: '', motivo: '', error: '' })

const abrirAnulacionApunte = (m) => {
  formAnular.value = { id: m.id, fecha: m.fecha, tipo: m.tipo, importe: m.importe, concepto: m.concepto, motivo: '', error: '' }
  modalAnularApunte.value = true
}

const confirmarAnulacionApunte = async () => {
  const f = formAnular.value
  f.error = ''
  if (!f.motivo?.trim()) { f.error = 'Indica el motivo de la anulación'; return }
  ocupadoApunte.value = true
  try {
    await gqlMutation(ANULAR_APUNTE_CAJA, { apunteId: f.id, motivo: f.motivo.trim() })
    modalAnularApunte.value = false
    await cargarBitacora()
  } catch (e) {
    f.error = errMsgApunte(e, 'Error al anular el apunte')
  } finally { ocupadoApunte.value = false }
}

const errMsgApunte = (e, fallback = 'Error') => {
  if (e?.response?.errors?.[0]?.message) return e.response.errors[0].message
  if (typeof e?.message === 'string') {
    const i = e.message.indexOf(': {')
    return i > 0 ? e.message.slice(0, i) : e.message
  }
  return fallback
}

const fmt = (val) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(val ?? 0)
const fechaFmt = (d) => d ? new Intl.DateTimeFormat('es-ES').format(new Date(d)) : ''

const badgeTipo = (tipo) => ({
  'ACTIVO': 'bg-blue-100 text-blue-700',
  'PASIVO': 'bg-red-100 text-red-700',
  'PATRIMONIO': 'bg-purple-100 text-purple-700',
  'INGRESO': 'bg-green-100 text-green-700',
  'GASTO': 'bg-orange-100 text-orange-700',
}[tipo] || 'bg-gray-100 text-gray-600')

const badgeEstado = (estado) => ({
  'BORRADOR': 'bg-yellow-100 text-yellow-700',
  'CONFIRMADO': 'bg-green-100 text-green-700',
  'ANULADO': 'bg-red-100 text-red-600',
}[estado] || 'bg-gray-100 text-gray-600')

// Quita el prefijo "TipoAsientoContable." / "EstadoAsientoContable." que viene del enum del backend
const stripEnum = (s) => (s || '').toString().split('.').pop()
const estadoLimpio = (s) => stripEnum(s)

const tipoAsientoLabel = (s) => ({
  GESTION:        'Gestión',
  APERTURA:       'Apertura',
  REGULARIZACION: 'Regularización',
  CIERRE:         'Cierre',
  AJUSTE:         'Ajuste',
}[stripEnum(s)] || stripEnum(s))

const estadoLabel = (s) => ({
  BORRADOR:   'Borrador',
  CONFIRMADO: 'Confirmado',
  ANULADO:    'Anulado',
}[stripEnum(s)] || stripEnum(s))

const recargarAsientos = async () => {
  await obtenerAsientos()
}

const abrirNuevaCuenta = () => {
  formCuenta.value = { codigo: '', nombre: '', tipo: 'ACTIVO', nivel: 1, padreId: null, esDotacion: false, descripcion: '', activa: true, permiteAsiento: true }
  modoEdicion.value = false
  cuentaBloqueada.value = false
  errorModal.value = ''
  modalCuenta.value = true
}

const abrirNuevaSubcuenta = (cuentaPadre) => {
  formCuenta.value = {
    codigo: (cuentaPadre.codigo || '') + '',
    nombre: '',
    tipo: cuentaPadre.tipo,
    nivel: Math.min((cuentaPadre.nivel || 0) + 1, 3),
    padreId: cuentaPadre.id,
    padreLabel: `${cuentaPadre.codigo} — ${cuentaPadre.nombre}`,
    esDotacion: cuentaPadre.esDotacion || false,
    descripcion: '',
    activa: true,
    permiteAsiento: true,
  }
  modoEdicion.value = false
  cuentaBloqueada.value = false
  errorModal.value = ''
  modalCuenta.value = true
}

const abrirEditarCuenta = async (cuenta) => {
  formCuenta.value = {
    id: cuenta.id,
    codigo: cuenta.codigo,
    nombre: cuenta.nombre,
    tipo: cuenta.tipo,
    nivel: cuenta.nivel,
    padreId: cuenta.padreId,
    esDotacion: !!cuenta.esDotacion,
    descripcion: cuenta.descripcion || '',
    activa: cuenta.activa !== false,
    permiteAsiento: !!cuenta.permiteAsiento,
  }
  modoEdicion.value = true
  cuentaBloqueada.value = false
  errorModal.value = ''
  modalCuenta.value = true
  // Comprobar en paralelo si tiene apuntes confirmados (bloquea campos estructurales)
  try {
    cuentaBloqueada.value = await cuentaTieneApuntesConfirmados(cuenta.id)
  } catch (e) {
    console.warn('No se pudo verificar apuntes confirmados:', e?.message)
  }
}

const abrirNuevoAsiento = () => {
  formAsiento.value = { ejercicio: filtroEjercicio.value, fecha: new Date().toISOString().split('T')[0], glosa: '', tipoAsiento: 'GESTION', observaciones: '' }
  errorModal.value = ''
  modalAsiento.value = true
}

const guardarCuenta = async () => {
  errorModal.value = ''
  if (!formCuenta.value.codigo || !formCuenta.value.nombre) {
    errorModal.value = 'Código y nombre son obligatorios'
    return
  }
  guardando.value = true
  try {
    const payload = { ...formCuenta.value }
    delete payload.padreLabel
    if (modoEdicion.value) {
      // En edición con cuenta bloqueada solo se permite renombrar/desc/activa/dotación
      if (cuentaBloqueada.value) {
        const original = cuentasContables.value.find(c => c.id === payload.id)
        if (original) {
          payload.codigo = original.codigo
          payload.tipo = original.tipo
          payload.nivel = original.nivel
          payload.padreId = original.padreId
          payload.permiteAsiento = original.permiteAsiento
        }
      }
      await actualizarCuentaContable(payload)
    } else {
      delete payload.id
      delete payload.activa
      await crearCuentaContable(payload)
      // Mantener expandido el padre tras añadir
      if (formCuenta.value.padreId) expandedMap[formCuenta.value.padreId] = true
    }
    modalCuenta.value = false
    await obtenerPlanCuentas()
  } catch (e) {
    errorModal.value = e.message || 'Error al guardar la cuenta'
  } finally {
    guardando.value = false
  }
}

const guardarAsiento = async () => {
  errorModal.value = ''
  if (!formAsiento.value.glosa || !formAsiento.value.fecha) {
    errorModal.value = 'Glosa y fecha son obligatorias'
    return
  }
  guardando.value = true
  try {
    await crearAsiento(formAsiento.value)
    modalAsiento.value = false
    await recargarAsientos()
  } catch (e) {
    errorModal.value = e.message || 'Error al crear el asiento'
  } finally {
    guardando.value = false
  }
}

const confirmarAsiento = async (asientoId) => {
  if (!(await confirmDialog({ titulo: '¿Confirmar acción?', mensaje: '¿Confirmar este asiento? Verifica que debe = haber.', variante: 'aviso' }))) return
  try {
    await confirmarAsientoContable(asientoId)
    await recargarAsientos()
  } catch (e) {
    toast.error(e.message || 'Error: el asiento no cuadra o ya está confirmado')
  }
}

const anularAsiento = async (asientoId) => {
  if (!(await confirmDialog({ titulo: '¿Confirmar acción?', mensaje: '¿Anular este asiento? Esta acción no se puede deshacer.', variante: 'critica' }))) return
  try {
    await anularAsientoContable(asientoId)
    await recargarAsientos()
  } catch (e) {
    toast.error(e.message || 'Error al anular el asiento')
  }
}

const calcularBalance = async () => {
  calculandoBalance.value = true
  try {
    await calcularBalanceSumasYSaldos(
      balanceEjercicio.value,
      balanceFechaCorte.value || null,
      balanceSoloConSaldo.value,
    )
  } catch (e) {
    toast.error(e.message || 'Error al calcular el balance')
  } finally {
    calculandoBalance.value = false
  }
}

const totalDebeBalance = computed(() =>
  lineasBalanceSumasSaldos.value.reduce((s, l) => s + (l.totalDebe || 0), 0)
)
const totalHaberBalance = computed(() =>
  lineasBalanceSumasSaldos.value.reduce((s, l) => s + (l.totalHaber || 0), 0)
)
const diferenciaBalance = computed(() => totalDebeBalance.value - totalHaberBalance.value)

onMounted(async () => {
  // Leer el modo de contabilidad para decidir qué estructura mostrar
  try {
    const cfg = await gqlQuery(`query { parametrosOrganizacion { contabilidadCompleja } }`)
    contabilidadCompleja.value = cfg?.parametrosOrganizacion?.contabilidadCompleja ?? true
  } catch (e) {
    console.warn('No se pudo leer el modo de contabilidad, se asume completo:', e?.message)
    contabilidadCompleja.value = true
  }

  // En modo simplificado no hay plan de cuentas que cargar; el panel de categorías se autogestiona
  if (contabilidadCompleja.value) {
    await obtenerPlanCuentas()
    await recargarAsientos()
    try {
      await obtenerSaldosCuentas(ejercicioActual.value)
    } catch (e) {
      console.warn('No se pudieron cargar saldos:', e?.message)
    }
  }
})

// Cargar la bitácora la primera vez que se abre la pestaña
watch(activeTab, (tab) => {
  if (tab === 'bitacora') {
    if (!movimientos.value.length && !cargandoBitacora.value) cargarBitacora()
    if (!campaniasBitacora.value.length) cargarCatalogosBitacora()
    if (!contabilidadCompleja.value) cargarCategoriasFiscales()
  }
})

// Si el modo cambia y la pestaña activa ya no existe, volver a 'plan'
watch(tabs, (nuevos) => {
  if (!nuevos.some(t => t.id === activeTab.value)) {
    activeTab.value = 'plan'
  }
})
</script>

<style scoped>
.btn-primary { @apply px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed; }
.btn-secondary { @apply px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm font-medium; }
.label { @apply block text-sm font-medium text-gray-700 mb-1; }
.input { @apply w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent; }
.input-sm { @apply px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-400; }
</style>
