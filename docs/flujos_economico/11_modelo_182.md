# Flujo 11 — Modelo 182 (declaración fiscal de donaciones)

## 1. Propósito

Cumplir la obligación informativa anual de la **AEAT — Modelo 182** (declaración de donativos, donaciones y aportaciones recibidas por entidades acogidas a la Ley 49/2002 de mecenazgo).

El fichero se presenta en enero del año siguiente al del ejercicio declarado, telemáticamente en la sede electrónica de la AEAT. Sin él, los donantes pierden la deducción en IRPF/IS y la entidad incumple.

---

## 2. Entidades implicadas

| Entidad | Rol |
|---|---|
| `Donacion` | Una por donativo recibido. Origen del agregado anual. |
| `Miembro` | Si el donante es socio, se toma su NIF. |
| `Presentacion182` (NUEVA) | Registro de cada presentación enviada (ejercicio, fecha, código AEAT, acuse). |
| `Configuracion` | NIF de la entidad declarante (sección "SEPA" tiene `sepa.creditor_id`, pero el NIF de la entidad es otro dato — se lee de `org.nif`). |

---

## 3. Estados y transiciones

```
   (no existe)
        │ A1 generar_modelo_182(ejercicio)
        ▼  (filtra donaciones con NIF, agrega por donante)
   Agregado en memoria — no se persiste hasta presentar
        │ A2 descargar_fichero_aeat / descargar_pdf_resumen
        ▼
   Tesorero sube el TXT a la sede AEAT
        │ A3 registrar_presentacion(ejercicio, codigo_aeat, fecha, acuse)
        ▼
   ┌──────────────────────────┐
   │ Presentacion182 PRESENTADA│  ← trazabilidad inmutable
   └──────────────────────────┘
```

---

## 4. Acciones

| # | Acción | Quién | Pre | Post |
|---|---|---|---|---|
| A1 | **Generar agregado del ejercicio** | Tesorero | hay donaciones del ejercicio | dict en memoria: donantes con (NIF, nombre, importe, tipo PF/PJ); excluidos con motivo |
| A2 | **Descargar TXT AEAT** | Tesorero | A1 hecho | Fichero binario ISO-8859-1 listo para subir a la AEAT |
| A3 | **Descargar PDF resumen** | Tesorero | A1 hecho | PDF con listado y totales |
| A4 | **Registrar presentación** | Tesorero | TXT subido a la AEAT y acuse recibido | `Presentacion182` creada con fecha, código, acuse |
| A5 | **Listar presentaciones** | Tesorero / Auditor | — | Histórico por ejercicios |

---

## 5. Pantallas UI

### 5.1 `Modelo182.vue` (NUEVA) — ruta `/economico/modelo-182`

```
Ejercicio:  [ 2025 ▼ ]   [ Generar Modelo 182 ]

Resumen del agregado:
  142 donaciones del ejercicio
  - 128 incluibles (con NIF, no anónimas)
  -  14 excluidas: 8 sin NIF, 6 anónimas
  Total incluido: 24 350,00 €

[ ↓ Fichero AEAT (TXT) ]    [ ↓ PDF resumen ]    [ Registrar presentación ]

────────────────────────────────────────────────────────────────────────
Historial de presentaciones:
  Ejercicio │ Fecha envío │ Código AEAT │ Total       │ Acuse
  2024      │ 15/01/2025  │ AEAT-XXXXX  │ 18 200,00 € │ [ver PDF]
  2023      │ 18/01/2024  │ AEAT-YYYYY  │ 12 850,00 € │ [ver PDF]
```

### 5.2 Sección de excluidos

Al generar, mostrar lista de excluidos con motivo para que el tesorero pueda completar datos antes de presentar.

---

## 6. Permisos / roles

| Código | Acción | Asignación |
|---|---|---|
| `M182_GENERAR` | A1, A2, A3 | TESORERO |
| `M182_REGISTRAR` | A4 — registrar presentación | TESORERO |
| `M182_LIST` | A5 | TESORERO + AUDITOR |

---

## 7. Norma legal aplicable

- **Ley 49/2002 art. 24**: deducciones por donativos. Requiere NIF del donante y certificado emitido por la entidad.
- **Ley 27/2014 IS art. 20**: deducción para personas jurídicas.
- **Orden HAC/146/2024**: aprueba el modelo y el formato técnico (registro posicional de 250 caracteres).
- **Plazo**: enero del año siguiente.
- **Sanción por no presentar**: art. 198 LGT — entre 200 y 20.000 € según volumen.

---

## 8. Estado de implementación actual

| Pieza | Estado |
|---|---|
| Modelo `Donacion` con NIF, fecha, importe, anónima | ✓ |
| Tabla `presentaciones_modelo_182` | ✗ FALTA |
| Modelo `Presentacion182` | ✗ FALTA |
| `Modelo182Service.generar_agregado`, `generar_fichero_aeat`, `generar_pdf_resumen`, `registrar_presentacion`, `listar_presentaciones` | ✗ FALTA |
| Mutations + Queries GraphQL | ✗ FALTA |
| Vista `Modelo182.vue` | ✗ FALTA |
| 3 permisos `M182_*` + asignación | ✗ FALTA |
| Sección de ayuda | ✗ FALTA |

---

## 9. Plan de implementación

**Lote A — Schema + modelo**

1. `CREATE TABLE presentaciones_modelo_182` (ejercicio único, fecha_envio, codigo_aeat, n_donantes, importe_total, archivo_acuse, observaciones, auditoría).
2. Modelo `Presentacion182` en `economico/models/modelo_182.py`.

**Lote B — Servicio**

3. `Modelo182Service` con:
   - `_inferir_tipo_donante(nif) -> int` (1=PF, 2=PJ).
   - `generar_agregado(ejercicio) -> dict` (incluidos + excluidos + totales).
   - `generar_fichero_aeat(ejercicio) -> bytes` (TXT 250 chars, ISO-8859-1).
   - `generar_pdf_resumen(ejercicio, organizacion_nombre) -> bytes` (PDF con reportlab).
   - `registrar_presentacion(ejercicio, codigo_aeat, fecha, archivo_acuse, importe_total, n_donantes) -> Presentacion182`.
   - `listar_presentaciones() -> list[Presentacion182]`.
   - `obtener_presentacion(ejercicio) -> Optional[Presentacion182]`.

**Lote C — Permisos**

4. 3 transacciones + bootstrap + seed.

**Lote D — GraphQL**

5. Type `Presentacion182Type`, `AgregadoModelo182Type` + queries y mutations con guards.

**Lote E — Frontend**

6. Vista `Modelo182.vue` con generación, descarga TXT/PDF, registro de presentación e histórico.

**Lote F — Ayuda**

7. Acordeón "Flujo · Modelo 182" en `Ayuda.vue`.

---

## 10. Decisiones tomadas (referencia rápida)

- **D11.1** — Solo donaciones con NIF identificable.
- **D11.2** — Tipo de donante (PF/PJ) inferido del NIF.
- **D11.3** — Salida: TXT AEAT + PDF resumen.
- **D11.4** — Tabla `presentaciones_modelo_182` para trazabilidad.

---

## 11. Implicaciones para otros flujos

- **Flujo 6 (Donaciones)**: precondición. Las donaciones deben estar registradas correctamente con NIF.
- **Memoria Anual (flujo 10) apartado 11**: los datos agregados del 182 alimentan el apartado de Subvenciones, donaciones y legados.
