# Flujo 6 — Donaciones

## 1. Propósito

Registrar las donaciones que la entidad recibe (dinerarias o en especie), generar los certificados fiscales para que el donante pueda deducirlas en su IRPF/IS (Ley 49/2002), y producir los inputs del Modelo 182 (flujo 11) y la Memoria económica (flujo 10).

Base funcional en [chat_donaciones.md](../chat_donaciones.md): el módulo es la fuente de verdad de los donativos, no de las cuotas (separación legal y fiscal). Las donaciones se acogen al régimen de la Ley 49/2002 si la entidad está adherida.

---

## 2. Entidades implicadas

### 2.1 `Donacion` (existente, ampliar)

Campos existentes:
- `id`, `miembro_id?`, `concepto_id?`, `campania_id?`
- Datos del donante externo: `donante_nombre`, `donante_email`, `donante_telefono`, `donante_dni`
- `importe`, `gastos`, `fecha`, `modo_ingreso`, `referencia_pago`
- `estado_id` (FK a `estados_donacion`), `certificado_emitido`, `fecha_certificado`, `anonima`, `observaciones`

**Campos NUEVOS (D6.5)**:
- `tipo: str` ∈ {DINERARIA, ESPECIE} — por defecto DINERARIA.
- `caracter: str` ∈ {PUNTUAL, RECURRENTE} — por defecto PUNTUAL.
- `descripcion_especie: text?` — descripción del bien si tipo=ESPECIE.
- `valoracion: numeric?` — importe de tasación para especie (en dineraria coincide con `importe`).
- `documento_valoracion: varchar(500)?` — URL/path al PDF de tasación si especie.
- `cuenta_bancaria_id: UUID?` FK a `cuentas_bancarias` — dónde entra el dinero (solo dineraria).
- `apunte_caja_id: UUID?` FK a `apuntes_caja` — referencia al apunte generado.
- `asiento_id: UUID?` FK a `asientos_contables` — referencia al asiento generado.
- `agrupacion_id: UUID?` FK a `unidades_organizativas` — tesorería delegada.
- `numero_certificado: varchar(30)?` — `CERT-{YYYY}-{NNNNN}` cuando se emite.

### 2.2 `DonacionConcepto` (existente)

Catálogo libre de conceptos: "Campaña Navidad", "Donación legado", etc.

### 2.3 `EstadoDonacion`

Catálogo. Estados (D6.1): REGISTRADA, COBRADA, ANULADA.

### 2.4 `ApunteCaja` y `AsientoContable`

Generados automáticamente al pasar a COBRADA (D6.2).

---

## 3. Estados y transiciones

```
   (nueva)
        │ A1 registrar()
        ▼
   ┌────────────┐
   │ REGISTRADA │  ← compromiso registrado, sin dinero aún
   └─────┬──────┘
         │ A2 marcar_cobrada(cuenta_bancaria_id, fecha_cobro)
         ▼
   ┌────────────┐
   │  COBRADA   │  ← ApunteCaja + asiento contable generados
   └─────┬──────┘
         │ A3 emitir_certificado(s) (anual por donante + tipo)
         │
         │ A4 anular(motivo)
         ▼
   ┌────────────┐
   │  ANULADA   │  ← reversión del asiento si lo había
   └────────────┘
```

Atajo: A2 se puede combinar con A1 si el dinero ya está cobrado (caso 80%). El form acepta "Registrar y marcar cobrada en un acto".

---

## 4. Acciones

| # | Acción | Quién | Pre | Post |
|---|---|---|---|---|
| A1 | **Registrar donación** | Tesorero | datos donante (NIF si quiere deducción) | Donacion REGISTRADA |
| A2 | **Marcar cobrada** | Tesorero | REGISTRADA + cuenta bancaria si dineraria | COBRADA + ApunteCaja + asiento |
| A3 | **Emitir certificado anual** | Tesorero | hay donaciones COBRADAS del ejercicio para un donante | PDF agrupado (D6.3, D6.6) |
| A4 | **Anular donación** | Tesorero | REGISTRADA o COBRADA (revierte asiento si procede) | ANULADA |
| A5 | **Adjuntar documento valoración** (especie) | Tesorero | tipo=ESPECIE | URL guardada en `documento_valoracion` |
| A6 | **Listar pendientes de certificar** | Tesorero/Auditor | — | filtro |

---

## 5. Pantallas UI

### 5.1 `Donaciones.vue` rediseñada — ruta `/economico/donaciones`

```
FilterBar:  Ejercicio · Tipo · Estado · Carácter · Donante · Búsqueda
  + Nueva donación

Listado:
  Fecha │ Donante (NIF)        │ Tipo │ Importe   │ Cuenta │ Estado    │ Cert.
  15/02 │ García López 11111111H│ A    │  100,00 € │ Bancos │ COBRADA   │  ✓
  20/03 │ Empresa SL G87654321 │ B    │ 2 500,00 €│ Bancos │ COBRADA   │  —
  …
Resúmenes: total recibido año / pendientes certificar / nº donantes únicos.
```

Acciones por fila: ver detalle, marcar cobrada (si REGISTRADA), anular, descargar certificado.

### 5.2 Modal "Nueva donación"

Campos:
- Tipo: ◉ Dineraria · ○ Especie
- Donante: ◉ Miembro [selector] · ○ Externo (NIF + nombre + email)
- Importe (o valoración si especie) · Fecha · Modo de pago · Carácter
- Concepto / Campaña (selectores)
- Cuenta bancaria de destino (si dineraria, obligatorio para marcar cobrada)
- Si especie: descripción del bien + URL del documento de valoración
- ¿Marcar como cobrada al guardar? (toggle)

### 5.3 Modal "Emitir certificados anuales"

Selector de ejercicio. El sistema lista los donantes con donaciones COBRADAS y, para cada uno, los certificados a emitir (A si dinerarias, B si especie, ambos si ambas). Botón "Emitir todos" o casillas para selección parcial.

---

## 6. Permisos / roles

| Código | Acción | Asignación |
|---|---|---|
| `DON_LIST` | Listado y detalle | TESORERO + AUDITOR |
| `DON_CREATE` | Registrar y modificar donaciones (A1, A2, A4, A5) | TESORERO |
| `DON_CERT` | Emitir certificados (A3) | TESORERO |

(Las 3 transacciones ya existen en `transacciones.json` desde antes.)

---

## 7. Norma legal aplicable

- **Ley 49/2002 art. 17, 18, 24** (Régimen fiscal mecenazgo): tipos de donativos deducibles, requisitos del certificado, modelo informativo.
- **Real Decreto 1270/2003** — reglamento de la Ley 49/2002.
- **Ley 27/2014 IS art. 20**: deducción de personas jurídicas.
- **Orden HAC/146/2024** — formato Modelo 182.
- **Código de Comercio art. 25**: todo cobro queda en el Libro Diario.

---

## 8. Estado de implementación actual

| Pieza | Estado |
|---|---|
| Modelo `Donacion` y `DonacionConcepto` | ✓ |
| Estados (catálogo `estados_donacion`) — REGISTRADA / COBRADA / ANULADA | ✓ |
| Permisos `DON_LIST`, `DON_CREATE`, `DON_CERT` | ✓ (en `transacciones.json`) |
| Campos nuevos D6.5: `tipo`, `caracter`, `descripcion_especie`, `valoracion`, `documento_valoracion`, `cuenta_bancaria_id`, `apunte_caja_id`, `asiento_id`, `agrupacion_id`, `numero_certificado` | ✓ |
| `DonacionService` con `registrar`, `marcar_cobrada`, `anular`, `emitir_certificado_anual`, `listar_certificables_por_ejercicio` | ✓ |
| Mutations específicas (`registrar_donacion`, `marcar_donacion_cobrada`, `anular_donacion`, `emitir_certificado_donacion_anual`, `listar_donaciones_certificables`) | ✓ |
| PDF certificado con reportlab (Ley 49/2002 art. 24) | ✓ |
| Vista funcional `Donaciones.vue` (FilterBar + listado + modales de alta/detalle/cobro/certificados) | ✓ |
| Sección de ayuda (acordeón "Flujo · Donaciones" en `Ayuda.vue`) | ✓ |
| Asignación de permisos a TESORERO (`seed_permisos_donaciones.py`) | ✓ |

---

## 9. Plan de implementación

**Lote A — Schema**
1. ALTER TABLE `donaciones` con los campos nuevos.
2. Sembrar estados `estados_donacion` si faltan: REGISTRADA, COBRADA, ANULADA.

**Lote B — Modelo + servicio**
3. Actualizar `Donacion` (Python) con los campos nuevos + properties helper.
4. `DonacionService`:
   - `registrar(...)` con validación de NIF si se quiere certificable.
   - `marcar_cobrada(donacion_id, cuenta_bancaria_id?, fecha_cobro?)`: en dineraria crea ApunteCaja + asiento; en especie solo asiento.
   - `anular(donacion_id, motivo)`: revierte asiento si existe.
   - `emitir_certificado_anual(ejercicio, miembro_id_o_nif, tipo_clave)`: agrega y produce PDF.
   - `listar_pendientes_certificar(ejercicio)`.

**Lote C — Permisos**
5. Verificar asignación a TESORERO; añadir si falta. Seed reproducible.

**Lote D — GraphQL**
6. Mutations: `registrar_donacion`, `marcar_donacion_cobrada`, `anular_donacion`, `emitir_certificado_donacion_anual`.
7. Queries: listado con filtros, agregado por donante, pendientes de certificar.

**Lote E — Frontend**
8. Vista `Donaciones.vue` con FilterBar + listado + modales de alta/detalle/cobro/certificado.

**Lote F — Ayuda**
9. Acordeón "Flujo · Donaciones" en `Ayuda.vue`.

---

## 10. Decisiones tomadas

- **D6.1** — Workflow REGISTRADA → COBRADA → ANULADA.
- **D6.2** — Asiento contable automático al pasar a COBRADA (Debe 572 / Haber 730).
- **D6.3** — Certificado anual agrupado por donante con número correlativo `CERT-{YYYY}-{NNNNN}`.
- **D6.4** — Permisos: TESORERO (matriz y agrupación).
- **D6.5** — v1 con tipo/carácter; recurrentes SEPA aplazado a v2.
- **D6.6** — Certificados separados por tipo (A dineraria, B especie) cuando un donante tiene ambos.

---

## 11. Implicaciones para otros flujos

- **Flujo 11 (Modelo 182)**: usa el agregado anual por donante con la clave A/B. Pendiente de actualizar (en backlog).
- **Flujo 10 (Cuentas Anuales) apartado 11** ("Subvenciones, donaciones y legados"): se nutre del agregado anual.
- **Flujo 3 (Remesas SEPA)**: futuro v2 — donaciones recurrentes vía SEPA.
- **Módulo Comunicación Interna**: plantilla email para enviar el certificado al donante.
