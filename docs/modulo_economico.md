# Módulo Económico — estado y cambios pendientes

> **Workflow**: NO aplicar `alembic upgrade head` ni reiniciar backend por cada cambio.
> Acumular SQL y cambios de modelo aquí; ejecutar de una vez al cerrar el lote.

---

## Estado actual del modelo (2026-05-15)

### Tablas principales

| Tabla | Clase Python | Archivo |
|---|---|---|
| `cuentas_bancarias` | `CuentaBancaria` | `tesoreria.py` |
| `movimientos_tesoreria` | `MovimientoTesoreria` | `tesoreria.py` |
| `conciliaciones_bancarias` | `ConciliacionBancaria` | `tesoreria.py` |
| `cuotas` | `Cuota` | `cuotas.py` |
| `cobros` | `Cobro` | `cobro/` |
| `donaciones` | `Donacion` | `donaciones.py` |
| `remesas` | `Remesa` | `remesas.py` |
| `reclamaciones` | `Reclamacion` | `reclamaciones/` |
| `categorias_partida` | `CategoriaPartida` | `presupuesto.py` |
| `partidas_presupuestarias` | `PartidaPresupuestaria` | `presupuesto.py` |
| `compromisos_presupuestarios` | `CompromisoPresupuestario` | `presupuesto.py` |
| `planificaciones_anuales` | `PlanificacionAnual` | `presupuesto.py` |
| `asientos_contables` | `AsientoContable` | `contabilidad.py` |

### Normativa aplicada
- PCESFL 2013 (Plan de Contabilidad para Entidades Sin Fines Lucrativos)
- Guía AEF 2022

---

## Documentación de referencia

Los documentos de diseño del módulo están en `backend/app/modules/economico/docs/`:

- [financiero.md](../backend/app/modules/economico/docs/financiero.md) — Tesorería y contabilidad (spec completa)
- [cobro.md](../backend/app/modules/economico/docs/cobro.md) — Adaptador de cobros
- [paypal.md](../backend/app/modules/economico/docs/paypal.md) — Integración PayPal

---

## Pendientes de diseño

### 1. `tipos_ingreso` como catálogo de tabla (pendiente)

El frontend usa un enum hardcoded `getTipoClass()` para colorear el tipo de ingreso.
Reemplazar por tabla `tipos_ingreso` con campo `color` para que sea configurable desde UI.
Ver memory: `project_tipo_ingreso_catalogo.md`

### 2. `campania_id` en pagos y donaciones (pendiente)

Para campañas de recogida de fondos (fundraising), añadir FK opcional `campania_id` a
`Cobro` / `Donacion`. Ver memory: `project_pagos_campanas_fondos.md`

### 3. Plan Anual de Actividades / Memoria Anual (pendiente)

Ejercicio presupuestario anual: las campañas se vinculan por fechas al plan, no por FK directa.
Ver memory: `project_plan_anual_actividades.md`

### 4. Migración m012 — verificar estado

La migración `m012` del módulo económico puede estar incompleta o no aplicada.
Verificar con `alembic history` y `alembic current` antes del siguiente lote.

---

## Cambios pendientes de migrar

### Lote: rediseño módulo campañas (2026-05-16)

#### Nuevas tablas

```sql
-- Desglose de presupuesto a nivel de actividad
CREATE TABLE partidas_presupuesto_actividad (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actividad_id UUID NOT NULL REFERENCES actividades(id) ON DELETE CASCADE,
  concepto VARCHAR(200) NOT NULL,
  importe_estimado NUMERIC(12,2) NOT NULL DEFAULT 0,
  importe_real NUMERIC(12,2),
  tipo_partida VARCHAR(10) NOT NULL DEFAULT 'gasto',  -- 'gasto' | 'ingreso'
  orden INTEGER NOT NULL DEFAULT 0,
  creado_en TIMESTAMPTZ DEFAULT now(),
  modificado_en TIMESTAMPTZ DEFAULT now()
);

-- Partes de trabajo (horas por actividad y miembro)
CREATE TABLE registros_trabajo_actividad (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actividad_id UUID NOT NULL REFERENCES actividades(id) ON DELETE CASCADE,
  miembro_id UUID NOT NULL REFERENCES miembros(id),
  fecha DATE NOT NULL,
  horas NUMERIC(5,2) NOT NULL,
  descripcion TEXT,
  tipo VARCHAR(20) NOT NULL DEFAULT 'presencia',  -- presencia|teletrabajo|coordinacion|otro
  creado_en TIMESTAMPTZ DEFAULT now()
);

-- Documentos adjuntos a actividades (actas, informes, fotos, material)
CREATE TABLE documentos_actividad (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actividad_id UUID NOT NULL REFERENCES actividades(id) ON DELETE CASCADE,
  nombre VARCHAR(200) NOT NULL,
  nombre_archivo VARCHAR(300) NOT NULL,
  ruta VARCHAR(500) NOT NULL,
  tipo_mime VARCHAR(100),
  tamanyo BIGINT,
  tipo_doc VARCHAR(20) NOT NULL DEFAULT 'otro',  -- acta|informe|foto|material|otro
  subido_por_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  creado_en TIMESTAMPTZ DEFAULT now()
);

-- Justificantes contables adjuntos a partidas de presupuesto
CREATE TABLE documentos_partida (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  partida_actividad_id UUID REFERENCES partidas_presupuesto_actividad(id) ON DELETE CASCADE,
  partida_campania_id UUID REFERENCES partidas_presupuesto_campania(id) ON DELETE CASCADE,
  nombre VARCHAR(200) NOT NULL,
  nombre_archivo VARCHAR(300) NOT NULL,
  ruta VARCHAR(500) NOT NULL,
  tipo_mime VARCHAR(100),
  tamanyo BIGINT,
  tipo_doc VARCHAR(20) NOT NULL DEFAULT 'otro',  -- factura|ticket|presupuesto|otro
  subido_por_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  creado_en TIMESTAMPTZ DEFAULT now(),
  CONSTRAINT chk_partida_xor CHECK (
    (partida_actividad_id IS NOT NULL)::int + (partida_campania_id IS NOT NULL)::int = 1
  )
);
```

#### Modelos Python añadidos
- `PartidaPresupuestoActividad` — en `actividad.py`
- `RegistroTrabajoActividad` — en `actividad.py`
- `DocumentoActividad` — en `actividad.py`
- `DocumentoPartida` — en `actividad.py`

#### Infraestructura de uploads
- Nuevo router REST: `backend/app/routers/uploads.py`
- Volumen Docker: `/app/uploads/` → persistencia de ficheros subidos
- Pendiente: añadir volumen en `docker-compose.dev.yml`

---

## Pasos para aplicar el lote

```bash
docker compose -f docker-compose.dev.yml --env-file .env.dev exec backend alembic upgrade head
docker compose -f docker-compose.dev.yml --env-file .env.dev restart backend
```

---

## Lote actual (2026-05-18): Ciclo de cobro completo + Cierre contable PCESFL

### Contexto

El módulo económico tiene fundamentos sólidos (partida doble, tesorería, remesas SEPA) pero le faltan:
1. El ciclo de cobro completo: tabla `Recibo` numerada, tipos de remesa, gestión de fallidos SEPA
2. El cierre de ejercicio legal: balance estructurado PCESFL, Cuenta de Resultados (Excedente), Libro Diario, asientos de cierre/apertura
3. UI para funcionalidades de backend ya implementadas: conciliación bancaria, extractos, reglas contables

**Base legislativa**: Ley 50/2002 art. 34, PCESFL 2013 (resolución ICAC), Ley Orgánica 8/2007 (partidos políticos), norma SEPA EPC131-08.

### Aclaración importante sobre presupuesto

El presupuesto es una **estimación previa** de ingresos y gastos. No se conoce de antemano lo que se recaudará. Es la **ejecución presupuestaria** la que va registrando la realidad. Los fallidos SEPA no afectan al presupuesto en sí, sino a la ejecución de ingresos y a la imagen fiel del balance (PCESFL norma 1ª).

### Nuevo: Justificante de Gastos

Documento que un miembro presenta para solicitar reembolso o registrar un gasto realizado en nombre de la organización. **Imputación obligatoria a una actividad** (de campaña, permanente o puntual).

#### Flujo de estados

```
PRESENTADO  → APROBADO  → PAGADO
            ↘ RECHAZADO (con motivo)
            ↘ ANULADO
```

#### Autorización jerárquica

El justificante lo aprueba:
- El **tesorero de la agrupación** del miembro (caso normal)
- O un **tesorero de ámbito superior** (escalado: nacional puede aprobar local, no al revés)

Control basado en permisos por agrupación: si el tesorero tiene rol en la agrupación del miembro o en una agrupación padre, puede aprobar.

#### Modelo `justificantes_gasto` (nuevo)

```sql
CREATE TABLE justificantes_gasto (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  numero_justificante VARCHAR(30) NOT NULL UNIQUE,      -- JUS-2025-00001
  ejercicio INTEGER NOT NULL,
  miembro_id UUID NOT NULL REFERENCES miembros(id),     -- quien presenta
  actividad_id UUID NOT NULL REFERENCES actividades(id),-- imputación obligatoria
  partida_actividad_id UUID REFERENCES partidas_presupuesto_actividad(id),
  agrupacion_id UUID REFERENCES unidades_organizativas(id),
  concepto VARCHAR(300) NOT NULL,
  importe NUMERIC(10,2) NOT NULL,
  fecha_gasto DATE NOT NULL,
  fecha_presentacion DATE NOT NULL,
  estado VARCHAR(20) NOT NULL DEFAULT 'PRESENTADO',     -- PRESENTADO|APROBADO|RECHAZADO|PAGADO|ANULADO
  aprobado_por_id UUID REFERENCES miembros(id),         -- tesorero que aprobó
  fecha_aprobacion DATE,
  motivo_rechazo TEXT,
  apunte_caja_id UUID REFERENCES apuntes_caja(id),      -- vinculo al pago
  cuenta_bancaria_id UUID REFERENCES cuentas_bancarias(id),
  modo_pago VARCHAR(20),                                -- TRANSFERENCIA|EFECTIVO|TARJETA
  fecha_pago DATE,
  observaciones TEXT,
  creado_en TIMESTAMPTZ DEFAULT now(),
  modificado_en TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX ix_justificantes_gasto_ejercicio ON justificantes_gasto(ejercicio);
CREATE INDEX ix_justificantes_gasto_miembro_id ON justificantes_gasto(miembro_id);
CREATE INDEX ix_justificantes_gasto_actividad_id ON justificantes_gasto(actividad_id);
CREATE INDEX ix_justificantes_gasto_estado ON justificantes_gasto(estado);
```

#### Documentos adjuntos

Reutiliza `documentos_partida` con FK opcional `justificante_gasto_id`, o se añade un nuevo enlace si conviene. Las facturas, tickets y presupuestos del miembro se suben al justificante con el router de uploads existente.

#### Servicio `JustificanteGastoService`

```python
class JustificanteGastoService:
    async def siguiente_numero(ejercicio: int) → str  # JUS-YYYY-NNNNN
    async def presentar(miembro_id, actividad_id, concepto, importe, fecha_gasto,
                        partida_actividad_id?, observaciones?) → JustificanteGasto
    async def aprobar(justificante_id, aprobador_id) → JustificanteGasto
        # Valida que aprobador tiene rol tesorero en la agrupación del miembro o superior
    async def rechazar(justificante_id, aprobador_id, motivo) → JustificanteGasto
    async def pagar(justificante_id, cuenta_bancaria_id, modo_pago,
                    fecha_pago?, referencia?) → ApunteCaja
        # Genera ApunteCaja (GASTO) + asiento contable (origen=JUSTIFICANTE_GASTO)
    async def anular(justificante_id, motivo) → JustificanteGasto
    async def listar(ejercicio?, miembro_id?, actividad_id?, estado?) → List[JustificanteGasto]
```

#### Nuevo origen de apunte: `JUSTIFICANTE_GASTO`

Añadir al enum `OrigenApunte` para que `RegistroContable` genere el asiento automático cuando el tesorero marca el justificante como PAGADO:

Regla contable por defecto:
- Origen `JUSTIFICANTE_GASTO` + Tipo `GASTO` → Debe 629 (Otros servicios) / Haber 572 (Banco)
- Configurable desde la UI de reglas contables — el tesorero puede afinar el cargo a 621/622/623/625/628/629 según concepto

#### Justificación legal

| Funcionalidad | Norma | Razón |
|---------------|-------|-------|
| Documentar todo gasto | LGT art. 106; RD 1619/2012 | Obligación de conservar facturas y justificantes; control fiscal |
| Imputación a actividad | LO 8/2007 (PP); Ley 50/2002 (fundaciones) | Trazabilidad de gastos por proyecto/actividad — exigida en cuentas anuales y rendición |
| Autorización por tesorero | Control interno (PCESFL norma 1ª) | Segregación de funciones: quien gasta no debe ser quien autoriza |
| Estado APROBADO antes de PAGADO | Buena gobernanza | Imposibilidad de pago sin aprobación previa formal |

### Editabilidad del Plan de Cuentas con ejercicio iniciado

| Acción | ¿Permitida? | Razón |
|--------|-------------|-------|
| Añadir subcuenta (4300001, 4300002…) | ✅ Siempre | Refinar desglose es legítimo |
| Renombrar / cambiar descripción | ✅ Siempre | Nombre es etiqueta, no afecta a la contabilidad |
| Desactivar (no eliminar) | ✅ Siempre | Soft-state; la cuenta y apuntes se conservan |
| Eliminar | ❌ Si tiene apuntes confirmados | Rompe integridad de los asientos |
| Cambiar código | ❌ Si tiene apuntes | Rompe trazabilidad y mapeo PCESFL |
| Cambiar tipo (ACTIVO↔PASIVO…) | ❌ Si tiene apuntes | Cambia naturaleza; rompe Balance |
| Cambiar padre / jerarquía | ❌ Si tiene apuntes | Rompe jerarquía de saldos |
| Reglas contables (origen→cuentas) | ✅ Siempre | Solo afecta a apuntes futuros |

**Implementación**:
- Añadir método `tiene_apuntes_confirmados(cuenta_id) → bool` en `ContabilidadService`
- En el frontend del Plan de Cuentas: si la cuenta tiene apuntes, **bloquear** los campos código/tipo/padre y mostrar etiqueta "no editable: en uso"
- Cuentas con apuntes: solo editables nombre/descripción/activa; añadir/desactivar siempre permitido
- Mostrar saldo actual de cada cuenta en el árbol → diferencia entre "imagen consultable" (lo presentamos atractivo) y "estructura editable" (solo subcuentas e hijas nuevas)

### Justificación legal por funcionalidad

| Funcionalidad | Norma | Razón |
|---------------|-------|-------|
| Tabla `Recibo` numerada | Código de Comercio art. 25; PCESFL norma 1ª | Justificante numerado del cobro; sin él no hay trazabilidad ni auditoría |
| `tipo_remesa` + `seq_tipo` SEPA | Norma EPC131-08 | El esquema SEPA exige `FRST` en el primer cobro y `RCUR` en sucesivos; otra cosa es causa de rechazo bancario |
| Registro de fallidos | PCESFL norma 1ª (imagen fiel); EPC131-08 | (a) Cta 430 reflejaría saldo no cobrado; balance perdería la imagen fiel. (b) Códigos como MD01 prohíben re-presentar |
| Flujo remesa de reenvío | EPC131-08 | Nueva presentación requiere actualizar `SeqTp`; no se puede simplemente re-enviar la misma orden |
| Asiento de regularización | PCESFL norma 18ª | ESFL presenta **Excedente del ejercicio** (cta 129), no Beneficio/Pérdida — no pueden repartirlo |
| Asiento cierre/apertura | Código de Comercio art. 25.1 | El Libro de Inventario debe contener balance de apertura y cierre de cada ejercicio |
| Balance PCESFL | Ley 50/2002 art. 34; LO 8/2007 | Depósito ante Protectorado/Tribunal de Cuentas en formato PCESFL; balance libre no es admisible |
| Cuenta Resultados PCESFL | Ley 50/2002 art. 34 | Depósito obligatorio en formato normalizado |
| Libro Diario (PDF) | Código de Comercio art. 25.1 | Obligatorio registrar día a día todas las operaciones |
| Conciliación bancaria | PCESFL norma 9ª | Control interno; primer documento solicitado en auditoría |
| Reglas contables uniformes | PCESFL norma 1ª de elaboración | Principio de uniformidad: imputación consistente entre ejercicios |

### Modelos de datos nuevos / ampliados

#### Tabla `recibos` (nueva)

```sql
CREATE TABLE recibos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  numero_recibo VARCHAR(30) NOT NULL UNIQUE,     -- REC-2025-00001
  ejercicio INTEGER NOT NULL,
  tipo VARCHAR(30) NOT NULL DEFAULT 'CUOTA_ORDINARIA',  -- CUOTA_ORDINARIA | EXTRAORDINARIA | REENVIO
  concepto VARCHAR(300) NOT NULL,
  miembro_id UUID NOT NULL REFERENCES miembros(id),
  cuota_id UUID REFERENCES cuotas_anuales(id) ON DELETE SET NULL,
  importe NUMERIC(10,2) NOT NULL,
  importe_pagado NUMERIC(10,2) NOT NULL DEFAULT 0,
  estado VARCHAR(20) NOT NULL DEFAULT 'EMITIDO',  -- EMITIDO | COBRADO | FALLIDO | ANULADO
  modo_cobro VARCHAR(20),                          -- SEPA | TRANSFERENCIA | MANUAL | EFECTIVO
  orden_cobro_id UUID REFERENCES ordenes_cobro(id) ON DELETE SET NULL,
  fecha_emision DATE NOT NULL,
  fecha_vencimiento DATE,
  fecha_cobro DATE,
  observaciones TEXT,
  creado_en TIMESTAMPTZ DEFAULT now(),
  modificado_en TIMESTAMPTZ DEFAULT now()
);
```

#### Ampliación `ordenes_cobro`

```sql
ALTER TABLE ordenes_cobro
  ADD COLUMN IF NOT EXISTS codigo_rechazo_sepa VARCHAR(10),
  ADD COLUMN IF NOT EXISTS motivo_rechazo TEXT,
  ADD COLUMN IF NOT EXISTS fecha_rechazo DATE;
```

#### Ampliación `remesas`

```sql
ALTER TABLE remesas
  ADD COLUMN IF NOT EXISTS tipo_remesa VARCHAR(20) NOT NULL DEFAULT 'ORDINARIA',
  ADD COLUMN IF NOT EXISTS concepto VARCHAR(300),
  ADD COLUMN IF NOT EXISTS seq_tipo VARCHAR(4) NOT NULL DEFAULT 'RCUR';
```

### TODOs del lote

#### Backend (Lote A) — COMPLETADO 2026-05-18
- [x] Crear `backend/app/modules/economico/models/recibos.py` — modelo `Recibo`
- [x] Ampliar `backend/app/modules/economico/models/remesas.py` — campos en `Remesa` y `OrdenCobro` (tipo_remesa, concepto, seq_tipo, remesa_origen_id, fecha_rechazo)
- [x] Crear `backend/app/modules/economico/services/recibo_service.py` — `ReciboService`
- [x] Ampliar `backend/app/modules/economico/services/remesa_service.py` — extraordinaria, reenvío, importar_fallidos; fix SeqTp hardcoded
- [x] Mutations recibos/fallidos en `backend/app/graphql/financiero_mutations.py`
- [x] `ReciboType` + inputs + CRUD strawchemy en types_auto/inputs_auto/schema_simple/mutations
- [x] Crear `backend/app/modules/economico/models/justificantes_gasto.py` — modelo `JustificanteGasto`
- [x] Añadir `OrigenApunte.JUSTIFICANTE_GASTO` al enum + `ALTER TYPE origenapunte ADD VALUE`
- [x] Crear `backend/app/modules/economico/services/justificante_gasto_service.py` — `presentar/aprobar/rechazar/pagar/anular`
- [x] Mutations justificantes en `financiero_mutations.py`
- [x] `JustificanteGastoType` + inputs + CRUD strawchemy
- [x] Crear `backend/app/modules/economico/services/cierre_service.py` — `CierreEjercicioService` con `MAPA_BALANCE`, `MAPA_RESULTADOS`
- [x] Método `tiene_apuntes_confirmados(cuenta_id)` en `ContabilidadService` para bloquear edición estructural
- [x] Crear `backend/app/modules/economico/services/pdf/libro_diario.py` — generación **CSV** (PDF queda pendiente hasta añadir reportlab a requirements)
- [x] Queries GraphQL: `balancePcesfl`, `cuentaResultados`, `estadoCierre`, `libroDiarioCsv` (base64)
- [x] Mutations GraphQL: `generarAsientoRegularizacion`, `generarAsientoCierre`, `generarAsientoApertura`
- [x] Aplicar SQL + restart + verificar (3 nuevas queries funcionando)

**Pendiente para futuro lote**:
- [ ] Añadir `reportlab` (o `weasyprint`) a `requirements.txt` para generar Libro Diario en PDF (además del CSV)
- [ ] Permisos: definir transacciones `ECO_RECIBO_EMITIR`, `ECO_JUSTIFICANTE_APROBAR`, `ECO_JUSTIFICANTE_PAGAR`, `ECO_CIERRE_EJECUTAR` y rol "Tesorero"
- [ ] Validación en `aprobar_justificante`/`pagar_justificante`: aprobador debe tener rol tesorero en agrupación del miembro o superior

#### Frontend (Lote B — posterior)
- [ ] **Rediseñar pestaña Plan de Cuentas en `Contabilidad.vue`**: árbol jerárquico colapsable con saldos por cuenta, búsqueda, alta inline; sustituye la tabla plana actual
- [ ] `Remesas.vue` — selector tipo + sección fallidos
- [ ] `Contabilidad.vue` — pestaña "Reglas contables"
- [ ] `Contabilidad.vue` — pestaña "Cierre de ejercicio"
- [ ] `Tesoreria.vue` — pestaña "Conciliación"
- [ ] `Tesoreria.vue` — pestaña "Cobros manuales"
- [ ] **Vista "Mis justificantes" para socio** y **"Aprobar justificantes" para tesorero** en módulo económico

#### Documentos (Lote C — baja prioridad)
- [ ] Certificado donación PDF (`Donacion.emitir_certificado()`)
- [ ] `PresupuestoService` (aprobar/iniciar_ejecucion/cerrar)

### Servicio CierreEjercicioService — diseño

```python
class CierreEjercicioService:
    async def calcular_saldos_cuentas(ejercicio: int) → dict[str, Decimal]
    async def calcular_balance_pcesfl(ejercicio: int) → dict  # estructura PCESFL
    async def calcular_cuenta_resultados(ejercicio: int) → dict  # excedente del ejercicio
    async def generar_asiento_regularizacion(ejercicio: int) → AsientoContable
        # Salda cuentas grupo 6 (gastos) y 7 (ingresos) contra cta 129
    async def generar_asiento_cierre(ejercicio: int) → AsientoContable
        # Cierra balance completo contra cta 129
    async def generar_asiento_apertura(ejercicio_nuevo: int) → AsientoContable
        # Reabre balance con saldos invertidos del cierre anterior
    async def verificar_estado_cierre(ejercicio: int) → dict
```

`MAPA_BALANCE` y `MAPA_RESULTADOS` son constantes con la clasificación PCESFL 2013 de códigos de cuenta a secciones del balance y cuenta de resultados. Detalle en el plan completo: `~/.claude/plans/vectorized-drifting-meteor.md`.

### GraphQL nuevo (queries + mutations)

Queries (en `Query` raíz, módulo contabilidad):
```graphql
balancePcesfl(ejercicio: Int!): BalancePcesflType!
cuentaResultados(ejercicio: Int!): CuentaResultadosType!
estadoCierre(ejercicio: Int!): EstadoCierreType!
libroDiarioPdf(ejercicio: Int!): String!   # PDF en base64
```

Mutations (en `FinancieroMutation`):
```graphql
generarAsientoRegularizacion(ejercicio: Int!): UUID!  # devuelve asiento_id
generarAsientoCierre(ejercicio: Int!): UUID!
generarAsientoApertura(ejercicio: Int!): UUID!
```

Types nuevos en `types_auto.py`:
- `BalancePcesflType` — estructura activo/pasivo/PN según PCESFL
- `CuentaResultadosType` — estructura excedente PCESFL
- `EstadoCierreType` — `{todosConfirmados, balanceCuadra, regularizacionHecha, cierreHecho, aperturaHecha}`

### Verificación end-to-end (al cerrar el lote)

1. **Ciclo de cobro**: Generar remesa ordinaria → XML SEPA → marcar enviada → importar fallido (código AM04) → generar remesa reenvío (SeqTp=FRST)
2. **Recibos**: Emitir lote `REC-2025-XXXXX` → verificar numeración correlativa → estado COBRADO tras liquidar remesa
3. **Cierre contable**:
   - Confirmar asientos del ejercicio → ejecutar `generar_asiento_regularizacion(2025)` → verificar cta 129 con excedente correcto
   - Ejecutar `generar_asiento_cierre(2025)` → descargar Libro Diario PDF
   - Calcular Balance PCESFL → verificar Activo Total == Pasivo + PN
   - Generar asiento apertura 2026
4. **Conciliación**: Importar extracto CSV → vincular apuntes → confirmar período → diferencia 0
5. **Reglas contables**: Crear regla CUOTA/INGRESO → 572/721 → registrar pago manual → asiento generado automáticamente

---

## TODOs pendientes (mayo 2026)

### Críticos por obligación legal

1. **Modelo 182 — declaración fiscal anual de donaciones**
   - Norma: art. 6 Ley 49/2002 (régimen fiscal mecenazgo); orden HAC/146/2024 (modelo 182).
   - Plazo: enero del año siguiente.
   - Sin él: incumplimiento ante AEAT y los donantes pierden la deducción IRPF.
   - Implementación: exportador de fichero plano AEAT (formato 182) sobre la tabla `Donacion` con DNI/NIF, importe y tipo de deducción.

2. **Cierre de ejercicio operativo**
   - Servicios ya existen (`CierreEjercicioService`) pero falta:
     - Pestaña "Cierre" en `Contabilidad.vue` (queries `estadoCierre`, mutations `generarAsientoRegularizacion`/`generarAsientoCierre`/`generarAsientoApertura`).
     - Verificar que el bloqueo de creación de asientos en ejercicios cerrados (recién añadido a `ContabilidadService.crear_asiento`) se respeta en todos los puntos de entrada.
   - Norma: art. 25 Código de Comercio + PCESFL 2013 norma 18ª; sin asiento de CIERRE confirmado los asientos pasados son modificables, viola la inmutabilidad contable.

3. **Informe de destino de rentas (Memoria Anual)**
   - Norma: art. 34 Ley 50/2002 (apartado 3 de la Memoria económica); LO 8/2007 art. 14 (partidos políticos).
   - Sin él: las cuentas anuales no se pueden depositar ante el Protectorado / Tribunal de Cuentas.
   - Implementación: a partir del `MAPA_RESULTADOS` separar ingresos de la actividad propia vs mercantil; trazar destino del excedente (a reservas / a remanente / a actividad).

### Pendientes funcionales

- **Cuotas del ejercicio en curso**: falta UI para establecer la cuota ordinaria y las cuotas reducidas del ejercicio activo (creación masiva de `CuotaAnual` partiendo del importe configurado en parámetros).
- **Motivos de reducción de cuota**: catalogar en parametrización (`tipos_reduccion_cuota`) con código, descripción y porcentaje de reducción aplicable.
- **Descripciones del plan de cuentas**: completar `descripcion` de todas las cuentas con texto en castellano llano (sin tecnicismos contables) orientado al tesorero no profesional.

- **Dashboard del tesorero**: pantalla de inicio del módulo económico orientada al tesorero no profesional. Debe mostrar de un vistazo:
  - Saldo de las cuentas bancarias y caja (cuentas 570, 572) con evolución mensual.
  - Cuotas pendientes de cobro del ejercicio en curso y comparativa con ejercicio anterior.
  - Recibos fallidos pendientes de re-presentar.
  - Próximos vencimientos (remesas a enviar, declaraciones fiscales, asiento de cierre).
  - Estado del ejercicio: % asientos confirmados, balance cuadra/no cuadra, alertas legales.
  - Acceso directo a: emitir lote de recibos, conciliar extracto, registrar gasto, generar cierre.
  - Sustituye al panel KPI antiguo (4 contadores aislados sin contexto, retirado mayo 2026).

- **Rediseño de la pestaña Asientos → Movimientos** (mayo 2026): el asiento contable es solo la consecuencia formal de un evento de negocio (un recibo cobrado, un justificante pagado, etc.). El tesorero no debe ver una tabla técnica de asientos, sino la **bitácora de movimientos** con su origen:
  | Fecha | Concepto / Origen | Importe | Tipo | Asiento # | Estado |
  |---|---|---|---|---|---|
  | 15/05/25 | Cuota 2025 — cobrada (REC-2025-00042) | +50,00 € | Ingreso | 0042 | ✓ |
  | 18/05/25 | Material oficina — pagado (JUST-2025-00003) | -120,00 € | Gasto | 0043 | ✓ |
  Clic en una fila → desplegable con los apuntes del asiento (debe/haber por cuenta). La vista raw de "asientos" se conserva solo como modo experto.

  Fuente de datos: query `ApunteCaja` con `entidad_origen_tipo` + `entidad_origen_id` resueltos a un texto legible (lookup a `recibos.numero_recibo`, `justificantes_gasto.numero_justificante`, etc.) y join al asiento generado vía `asiento_id`.
