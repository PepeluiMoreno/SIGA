# Instrucciones de despliegue — Módulo de Presupuestos (Fase 1)

**Rama:** `feature/presupuestos`
**Merge destino:** `master`
**Última actualización:** 2026-05-21

---

## 1. Qué incluye esta entrega (Fase 1)

Gestión presupuestaria anual con ciclo de vida, partidas por categoría, vinculación a la
actividad real e integración con tesorería. El presupuesto es una **funcionalidad
activable** (no un modo): opcional para asociaciones, obligatoria para fundaciones.

Funcionalidad:
- Planificación anual (una por ejercicio) con ciclo de vida:
  BORRADOR → PROPUESTO → APROBADO → EN_EJECUCION → CERRADO
- Partidas de ingreso y gasto agrupadas por categoría, con edición inline
- Vinculación de partida a actividad o campaña (presupuesto por programas)
- Imputación automática de la ejecución desde los apuntes de caja
- Informe de desviaciones (previsto vs ejecutado) en tabla
- Feature flag `org.usa_presupuesto` (forzado para fundaciones)

Fuera de alcance (fases posteriores): modificaciones presupuestarias formales,
control de disponibilidad, clonado de ejercicio, prórroga, dashboard con gráficas.

---

## 2. Merge a master

```bash
git checkout master && git pull origin master
git merge --no-ff feature/presupuestos
```

> **Migraciones — posible merge de cabezas.** La migración encadena sobre `o0p1q2r3s4t5`
> (rama de contabilidad simplificada). Si esa rama no está aún en master, mergéala primero.
> Si Alembic detecta múltiples heads: `cd backend && alembic merge heads -m "merge presupuestos"`.

```bash
git push origin master
```

---

## 3. Migración

```bash
cd backend && alembic upgrade head
```

### `p1q2r3s4t5u6` — vinculación de partida a actividad/campaña
**Encadena sobre:** `o0p1q2r3s4t5`

| Cambio | Detalle |
|---|---|
| `partidas_presupuestarias.actividad_id` | FK nullable a `actividades` |
| `partidas_presupuestarias.campania_id` | FK nullable a `campanias` |

> El resto del modelo (`planificaciones_anuales`, `partidas_presupuestarias`,
> `categorias_partida`, `estados_planificacion`, `compromisos_presupuestarios`) ya existía
> en master de migraciones anteriores.

### Rollback
```bash
alembic downgrade o0p1q2r3s4t5
```

---

## 4. Seeds

### Estados de planificación — automático
`seed_estados_planificacion` está registrado en `inicializar_sistema.py`. Idempotente.
Inserta los 5 estados del ciclo (BORRADOR, PROPUESTO, APROBADO, EN_EJECUCION, CERRADO).

Para sembrar sin reiniciar:
```bash
cd backend
python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.scripts.seeding.seed_estados_planificacion import seed_estados_planificacion
async def run():
    async with AsyncSessionLocal() as s:
        await seed_estados_planificacion(s)
asyncio.run(run())
"
```

### Permisos RBAC — ya existían
Las transacciones `ECO_PRESUPUESTO_CONSULTAR`, `ECO_PRESUPUESTO_CREAR` y
`ECO_PRESUPUESTO_APROBAR` ya estaban en el catálogo (funcionalidad
`PLANIFICACION_PRESUPUESTARIA`). No requiere seed nuevo; asignar al rol que corresponda
desde Administración → Roles.

---

## 5. Feature flag

`org.usa_presupuesto`. Configuración → Parámetros generales → Funcionalidades →
Presupuesto anual.

- **Asociaciones:** opcional (obligación estatutaria, no legal).
- **Fundaciones:** forzado a activado y bloqueado (plan de actuación, Ley 50/2002),
  mismo patrón que el PCESFL obligatorio.
- Desactivado: el ítem "Presupuesto" no aparece en el menú y la ruta
  `/economico/presupuesto` queda inaccesible (guard `requiereFeature`).

---

## 6. Permisos por operación

| Operación | Permiso |
|---|---|
| Consultar presupuesto, partidas, desviaciones | `ECO_PRESUPUESTO_CONSULTAR` |
| Crear/editar/eliminar partidas, crear planificación, proponer, devolver a borrador | `ECO_PRESUPUESTO_CREAR` |
| Aprobar, iniciar ejecución, cerrar | `ECO_PRESUPUESTO_APROBAR` |

Las partidas solo se editan en estado BORRADOR o PROPUESTO.

---

## 7. Integración con tesorería (reajuste de ejecución)

La ejecución de cada partida se alimenta de los apuntes imputados a su actividad/campaña:

| Acción sobre el apunte | Efecto |
|---|---|
| Crear apunte imputado | Suma a ejecución |
| Reasignar imputación | Resta de la antigua, suma a la nueva |
| Quitar imputación | Resta de la partida |
| Anular apunte | Revierte la ejecución |

Defensivo: un fallo de imputación nunca impide registrar/editar/anular el movimiento real.

---

## 8. Inventario de archivos

### Backend — nuevos
```
alembic/versions/p1q2r3s4t5u6_presupuesto_partida_actividad.py
app/graphql/presupuesto_resolvers.py
app/modules/economico/services/presupuesto_service.py
app/scripts/seeding/seed_estados_planificacion.py
```

### Backend — modificados
```
app/modules/economico/models/presupuesto.py        + actividad_id/campania_id, transiciones funcionales
app/modules/economico/services/tesoreria_service.py  imputación/reversión en crear, editar, anular
app/graphql/configuracion_resolvers.py             + org.usa_presupuesto (salida y guardado)
app/graphql/schema_simple.py                       + PresupuestoQuery
app/graphql/mutations.py                           + PresupuestoMutation
app/scripts/inicializar_sistema.py                 + seed_estados_planificacion
```

### Frontend — nuevos
```
src/modules/economico/views/Presupuesto.vue           (sustituye el stub)
src/modules/economico/components/PartidasPorCategoria.vue
src/graphql/queries/presupuestos.js
```

### Frontend — modificados
```
src/modules/configuracion/views/ParametrosGenerales.vue  toggle usa_presupuesto + forzado fundación
src/stores/orgConfig.js                                  expone usaPresupuesto
src/components/common/AppLayout.vue                      oculta menú si flag apagado
src/router/index.js                                      ruta protegida requiereFeature
src/views/Ayuda.vue                                      flujo de presupuesto
```

---

## 9. Verificación post-deploy

1. Organización tipo Asociación con flag apagado → no aparece "Presupuesto" en el menú.
2. Activar el flag → aparece. Crear presupuesto del ejercicio → nace en Borrador.
3. Añadir partidas de ingreso y gasto inline; comprobar totales y aviso de superávit/déficit.
4. Proponer → Aprobar (con permiso) → las partidas quedan bloqueadas para edición.
5. Iniciar ejecución. Registrar en tesorería un gasto imputado a una actividad con partida
   → su importe aparece en "Seguimiento de ejecución".
6. Reasignar ese apunte a otra actividad → la ejecución se mueve de partida. Anularlo → se revierte.
7. Cambiar tipo de entidad a Fundación → el flag se fuerza a activado y se bloquea.
