# Instrucciones de despliegue — Presupuestos Fase 2

**Rama:** `feature/presupuestos-fase2`
**Merge destino:** `master`
**Última actualización:** 2026-05-22

---

## 1. Qué incluye

Modificaciones presupuestarias, presupuesto inicial vs vigente, alertas y control
de disponibilidad (blando). Construye sobre la Fase 1 (ya en master).

- **Inicial vs vigente:** al aprobar, el presupuesto se congela (importe_inicial). Los
  cambios posteriores son modificaciones que ajustan el vigente sin tocar el inicial.
- **Modificaciones:** transferencia (entre partidas), ampliación, suplemento. Trazables.
- **Alertas:** partidas sobreejecutadas o agotadas, visibles en panel propio.
- **Control de disponibilidad (blando):** opcional. Cuando una partida se desvía, avisa
  a los responsables de control presupuestario. NUNCA bloquea el gasto real.

> **Nota — notificaciones.** El aviso de desviación está **preparado pero desactivado**
> (flag `_NOTIFICACIONES_ACTIVAS = False` en `presupuesto_service.py`), porque el sistema
> de notificaciones del frontend aún no existe (pendiente, rama `feature/notificaciones`).
> El gasto y las alertas en pantalla funcionan sin él. Cuando se construya: poner el flag
> a True y crear el tipo de notificación `PRESUPUESTO_DESVIACION` en su seed. No hay que
> tocar la lógica de detección ni el punto de llamada.

---

## 2. Merge

```bash
git checkout master && git pull origin master
git merge --no-ff feature/presupuestos-fase2
```

> Migración encadena sobre `p1q2r3s4t5u6` (Fase 1). Si Fase 1 no está en master,
> mergéala primero. Si hay heads paralelos: `alembic merge heads`.

```bash
git push origin master
```

---

## 3. Migración

```bash
cd backend && alembic upgrade head
```

### `q2r3s4t5u6v7` — Fase 2
**Encadena sobre:** `p1q2r3s4t5u6`

| Cambio | Detalle |
|---|---|
| `partidas_presupuestarias.importe_inicial` | Numeric(12,2). Se inicializa con el vigente actual de cada partida |
| `planificaciones_anuales.control_disponibilidad` | Boolean, default false |
| tabla `modificaciones_presupuestarias` | tipo, partida origen/destino, importe, fecha, motivo, registrada_por |
| enum `tipomodificacionpresupuestaria` | TRANSFERENCIA, AMPLIACION, SUPLEMENTO |

### Rollback
```bash
alembic downgrade p1q2r3s4t5u6
```

---

## 4. Seeds y permisos

Ninguno nuevo. Reutiliza los permisos de Fase 1:
- Consultar (modificaciones, alertas): `ECO_PRESUPUESTO_CONSULTAR`
- Registrar modificación y toggle de control: `ECO_PRESUPUESTO_APROBAR`

El permiso `ECO_PRESUPUESTO_APROBAR` identifica además al **responsable de control
presupuestario** (destinatario del futuro aviso de desviación).

---

## 5. Comportamiento

- Las modificaciones solo se permiten sobre presupuestos **APROBADO** o **EN_EJECUCION**
  (el borrador se edita directamente). En esos estados aparecen los paneles de
  Modificaciones y Alertas, y el toggle de control de disponibilidad en la cabecera.
- Transferencia: valida que el origen tenga disponible suficiente.
- La imputación de gasto (Fase 1) ahora, además, dispara el chequeo de desviación;
  con notificaciones activas, avisaría. Sin ellas, la desviación se ve en el panel Alertas.

---

## 6. Inventario de archivos

### Backend — nuevos
```
alembic/versions/q2r3s4t5u6v7_presupuestos_fase2.py
```
### Backend — modificados
```
app/modules/economico/models/presupuesto.py            + importe_inicial, control_disponibilidad,
                                                         ModificacionPresupuestaria, propiedades de alerta
app/modules/economico/models/__init__.py               registro del nuevo modelo
app/modules/economico/services/presupuesto_service.py  modificaciones, alertas, control, congelar inicial
                                                         al aprobar, aviso de desviación (preparado/off)
app/graphql/presupuesto_resolvers.py                   tipos y campos Fase 2, queries y mutations
```
### Frontend — nuevos
```
src/modules/economico/components/ModificacionesPresupuestarias.vue
```
### Frontend — modificados
```
src/modules/economico/views/Presupuesto.vue            paneles Alertas y Modificaciones, toggle control
src/modules/economico/components/PartidasPorCategoria.vue  inicial vs vigente, marca sobreejecución
src/graphql/queries/presupuestos.js                    queries/mutations Fase 2, campos nuevos
src/views/Ayuda.vue                                    paso 5 (modificaciones y control)
```

---

## 7. Verificación post-deploy

1. Crear/usar un presupuesto, añadir partidas, aprobarlo → al aprobar, el inicial queda fijado.
2. En estado Aprobado/En ejecución aparecen los paneles Modificaciones y (si las hay) Alertas.
3. Registrar una transferencia entre dos partidas → el vigente de origen baja y el de destino sube; el inicial no cambia (se ve debajo del vigente).
4. Intentar transferir más del disponible del origen → se rechaza con mensaje.
5. Registrar una ampliación → sube el vigente del destino y el total.
6. Imputar gasto que supere una partida → aparece en Alertas como sobreejecutada (en rojo).
7. Activar el toggle de control de disponibilidad → queda guardado (el aviso por notificación se activará con el módulo de notificaciones).
