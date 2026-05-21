# Instrucciones de despliegue — Presupuestos Fase 3

**Rama:** `feature/presupuestos-fase3`
**Merge destino:** `master`
**Última actualización:** 2026-05-22

---

## 1. Qué incluye

Funciones avanzadas sobre las fases 1 y 2 (ambas deben estar en master antes):

- **Clonar:** crear el presupuesto de un ejercicio copiando las partidas del anterior
  (importes como base, ejecución a cero, nace en borrador).
- **Prórroga:** caso especial de clonado, marca el presupuesto como prórroga del
  anterior (uso: el del nuevo ejercicio no se aprueba a tiempo).
- **Comparativa interanual:** partidas del ejercicio frente al anterior, con variación.
- **Liquidación presupuestaria:** previsto vs ejecutado (global), listo para incorporar
  a la Memoria de las cuentas anuales.

> El **dashboard económico** NO entra aquí: es transversal y va en sesión propia con
> elección de librería de gráficas.

> Decisión de diseño: la liquidación **expone el dato** (previsto/ejecutado/resultado/
> grado de ejecución); no inyecta texto en la memoria narrativa, que la redacta la persona
> en el apartado correspondiente del módulo de cuentas anuales.

---

## 2. Merge

```bash
git checkout master && git pull origin master
git merge --no-ff feature/presupuestos-fase3
```

> Encadena sobre la Fase 2 (`q2r3s4t5u6v7`). Mergear primero Fase 1 y Fase 2 si no
> estuvieran. Si hay heads paralelos: `alembic merge heads`.

```bash
git push origin master
```

---

## 3. Migración

```bash
cd backend && alembic upgrade head
```

### `r3s4t5u6v7w8` — Fase 3
**Encadena sobre:** `q2r3s4t5u6v7`

| Cambio | Detalle |
|---|---|
| `planificaciones_anuales.es_prorroga` | Boolean, default false |
| `planificaciones_anuales.ejercicio_origen_prorroga` | Integer nullable |

### Rollback
```bash
alembic downgrade q2r3s4t5u6v7
```

---

## 4. Seeds y permisos

Ninguno nuevo. Reutiliza los de presupuesto:
- Clonar: `ECO_PRESUPUESTO_CREAR`
- Prorrogar: `ECO_PRESUPUESTO_APROBAR`
- Comparativa y liquidación (consulta): `ECO_PRESUPUESTO_CONSULTAR`

---

## 5. Inventario de archivos

### Backend
```
alembic/versions/r3s4t5u6v7w8_presupuestos_fase3.py            (nuevo)
app/modules/economico/models/presupuesto.py                   + es_prorroga, ejercicio_origen_prorroga
app/modules/economico/services/presupuesto_service.py         clonar, prorrogar, comparativa, liquidación
app/graphql/presupuesto_resolvers.py                          tipos, queries y mutations Fase 3
```
### Frontend
```
src/modules/economico/views/Presupuesto.vue     clonar/prorrogar en estado vacío, distintivo prórroga,
                                                 paneles comparativa y liquidación
src/graphql/queries/presupuestos.js             queries/mutations Fase 3
src/views/Ayuda.vue                             paso 6 (reutilizar, comparar, liquidar)
```

---

## 6. Verificación post-deploy

1. Con un presupuesto del año N existente, ir al ejercicio N+1 (sin presupuesto) → aparece la opción "partir del presupuesto de N".
2. Clonar → se crea N+1 en borrador con las partidas de N copiadas (ejecución a cero).
3. Prorrogar (con permiso de aprobación) → se crea marcado como "Prórroga de N", visible con su distintivo en la cabecera.
4. Abrir el panel Comparativa interanual → muestra las partidas frente a N con variación.
5. Abrir el panel Liquidación → muestra previsto/ejecutado/resultado y grado de ejecución.
6. Intentar clonar a un ejercicio que ya tiene presupuesto → se rechaza.
