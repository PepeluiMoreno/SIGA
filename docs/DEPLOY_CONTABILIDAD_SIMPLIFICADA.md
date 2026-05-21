# Instrucciones de despliegue — Contabilidad simplificada

**Rama:** `feature/contabilidad-simplificada`
**Merge destino:** `master`
**Última actualización:** 2026-05-21

---

## 1. Qué incluye esta entrega

Habilita un segundo modo de contabilidad, **simplificada**, como alternativa a la
contabilidad completa por partida doble (PCESFL). El modo se elige por organización
con el parámetro `org.contabilidad_compleja` (ya existente).

| | Contabilidad simplificada | Contabilidad completa |
|---|---|---|
| Estructura de clasificación | Categorías fiscales | Plan de cuentas PCESFL |
| Mecánica | Libro de ingresos y gastos | Asientos por partida doble |
| Mapeo fiscal | Modelos 182 / 347 por categoría | Reglas contables → cuentas |
| Obligatorio para | — | Fundaciones (RD 1491/2011) |
| Modo por defecto | Sí | — |

Las categorías fiscales son a la contabilidad simplificada lo que el plan de cuentas
es a la compleja: la misma función (clasificar todo ingreso y gasto), el mismo lugar
en la UI, el mismo permiso RBAC.

---

## 2. Merge a master

```bash
git checkout master
git pull origin master
git merge --no-ff feature/contabilidad-simplificada
```

> **Migraciones — posible merge de cabezas.** Las migraciones de esta rama encadenan
> sobre `d36a6ce11db3`, que ya está en master. Si en el momento del merge master tiene
> otra cabeza de migración en paralelo, Alembic detectará múltiples heads. En ese caso,
> antes de `alembic upgrade head`:
> ```bash
> cd backend
> alembic merge heads -m "merge contabilidad simplificada"
> ```
> Si no hay cabezas paralelas, este paso no es necesario.

```bash
git push origin master
```

---

## 3. Migraciones de base de datos

Dos migraciones encadenadas. Un solo comando las aplica:

```bash
cd backend
alembic upgrade head
```

### Migración 1 — `n9o0p1q2r3s4` — Categorías fiscales
**Encadena sobre:** `d36a6ce11db3`

| Cambio | Detalle |
|---|---|
| Tabla `categorias_fiscales` | codigo, nombre, tipo (INGRESO/GASTO), computa_modelo_182, computa_modelo_347, casilla_modelo, orden, color, activa |
| Columna `apuntes_caja.categoria_fiscal_id` | FK nullable a `categorias_fiscales` |
| Enum `tipocategoriafiscal` | INGRESO, GASTO |

### Migración 2 — `o0p1q2r3s4t5` — Reglas de categorización
**Encadena sobre:** `n9o0p1q2r3s4`

| Cambio | Detalle |
|---|---|
| Tabla `reglas_categorizacion` | patron, tipo_coincidencia, tipo_apunte, categoria_fiscal_id, orden, descripcion, activa |
| Enum `tipocoincidencia` | CONTIENE, EMPIEZA_POR, EXACTO, REGEX |

### Rollback
```bash
alembic downgrade n9o0p1q2r3s4   # deshace solo las reglas
alembic downgrade d36a6ce11db3   # deshace ambas
```

---

## 4. Seeds

### 4.1 Categorías fiscales por defecto — automático
`seed_categorias_fiscales` está registrado en `inicializar_sistema.py` y se ejecuta en
el arranque. Idempotente por código. Inserta 14 categorías: 6 de ingreso (Cuotas,
Donativos, Subvenciones, Actividades, Financieros, Otros) y 8 de gasto (Personal,
Suministros, Alquileres, Servicios externos, Actividades, Desplazamientos, Bancarios,
Otros). Donativos marcado para Modelo 182; Suministros, Alquileres, Servicios y
Actividades para Modelo 347.

Para sembrar sin reiniciar:
```bash
cd backend
python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.scripts.seeding.seed_categorias_fiscales import seed_categorias_fiscales
async def run():
    async with AsyncSessionLocal() as s:
        await seed_categorias_fiscales(s)
asyncio.run(run())
"
```

### 4.2 Permisos RBAC
`seed_permisos_plan_cuentas.py` se actualizó para asignar al rol **TESORERO** las
transacciones de estructura contable compartidas:
```bash
cd backend
python -m app.scripts.seeding.seed_permisos_plan_cuentas
```

### 4.3 Reglas de categorización — sin seed (deliberado)
No se siembran reglas por defecto: las define cada organización según sus proveedores
("Endesa" → Suministros). La clasificación por origen funciona sin reglas.

---

## 5. RBAC — permiso compartido

Las categorías fiscales y el plan de cuentas comparten permiso, por ser la misma función.

| Transacción | Tipo | Cubre |
|---|---|---|
| `ECO_ESTRUCTURA_CONTABLE_LISTAR` | Consulta | Plan de cuentas y categorías fiscales |
| `ECO_ESTRUCTURA_CONTABLE_GESTIONAR` | Mutación | Crear/editar/eliminar en ambos modos + reglas + clasificación |

Funcionalidad `ESTRUCTURA_CLASIFICACION_CONTABLE`. Asignadas al rol TESORERO.

**Saneamiento:** `ECO_CUENTA_*` queda exclusivamente para cuentas bancarias (antes estaba
sobrecargado entre bancarias y plan de cuentas). Los resolvers de cuenta contable
migraron a `ECO_ESTRUCTURA_CONTABLE_GESTIONAR`.

---

## 6. Comportamiento por modo

### Configuración
*Parámetros generales → Funcionalidades → Estructura de clasificación contable*: dos
radios (Categorías fiscales / Plan General Contable). Si el tipo de entidad es Fundación,
se fuerza PCESFL y se bloquea (triple cobertura: carga, watch y UI).

### Pantalla de Contabilidad
- **Simplificado**: pestañas *Categorías fiscales* (sub-secciones Categorías y Reglas) y
  *Bitácora*. Sin asientos ni balances.
- **Completo**: pestañas *Plan de cuentas*, *Bitácora*, *Asientos*, *Sumas y saldos*.

### Clasificación de apuntes (modo simplificado)
Tres mecanismos combinados: (1) derivación automática por origen, (2) reglas por concepto,
(3) clasificación masiva en la bitácora (filtro sin clasificar, selección múltiple,
botón clasificar pendientes). Edición individual como respaldo.

---

## 7. Decisión de diseño registrada

**ReglaCategorizacion NO se unificó con ReglaContable** (la regla del modo complejo).
Aunque la derivación por origen del modo simplificado (`_ORIGEN_A_CATEGORIA`, ~7 líneas)
se solapa conceptualmente con `ReglaContable` (origen → cuentas), no se acopló código
estable en producción para eliminar una duplicación pequeña. Entrada/salida difieren
(origen→categoría vs origen→cuentas debe/haber) y pueden divergir. **Reevaluable** si en
el futuro la lógica origen→destino se vuelve compleja en ambos modos.

---

## 8. Inventario de archivos

### Backend — nuevos
```
alembic/versions/n9o0p1q2r3s4_contabilidad_simplificada.py
alembic/versions/o0p1q2r3s4t5_reglas_categorizacion.py
app/modules/economico/models/contabilidad/categoria_fiscal.py
app/modules/economico/models/contabilidad/regla_categorizacion.py
app/modules/economico/services/categoria_fiscal_service.py
app/modules/economico/services/categorizacion_service.py
app/modules/economico/services/regla_categorizacion_service.py
app/graphql/categoria_fiscal_resolvers.py
app/graphql/categorizacion_resolvers.py
app/scripts/seeding/seed_categorias_fiscales.py
```

### Backend — modificados
```
app/modules/economico/models/contabilidad/__init__.py    registro de los nuevos modelos
app/modules/economico/models/__init__.py                 idem
app/modules/economico/models/tesoreria/apunte.py         + categoria_fiscal_id
app/modules/economico/services/tesoreria_service.py      metadatos + categoría fiscal
app/modules/economico/catalog.py                         transacciones estructura contable
app/graphql/economico_resolvers.py                       permiso compartido en cuenta contable
app/graphql/economico_mutations.py                       categoria_fiscal_id en metadatos
app/graphql/schema_simple.py                             + CategoriaFiscalQuery, CategorizacionQuery
app/graphql/mutations.py                                 + CategoriaFiscalMutation, CategorizacionMutation
app/scripts/inicializar_sistema.py                       + seed_categorias_fiscales
app/scripts/seeding/seed_permisos_plan_cuentas.py        transacciones compartidas
```

### Frontend — nuevos
```
src/components/common/CategoriasFiscalesPanel.vue
src/components/common/ReglasCategorizacionPanel.vue
src/graphql/queries/categorias_fiscales.js
```

### Frontend — modificados
```
src/modules/economico/views/Contabilidad.vue            tabs condicionales, clasificación masiva
src/modules/configuracion/views/ParametrosGenerales.vue radios de estructura contable
src/graphql/queries/tesoreria.js                        + categoriaFiscalId en bitácora
src/views/Ayuda.vue                                     dos modos + flujos de contabilidad
```

---

## 9. Verificación post-deploy

1. Organización tipo Asociación → Contabilidad muestra 2 pestañas (Categorías + Bitácora).
2. Crear una categoría y una regla; registrar un gasto manual cuyo concepto case con la regla → se autoclasifica.
3. En bitácora, filtrar "sin clasificar", seleccionar varios, asignar categoría en lote.
4. Cambiar el tipo de entidad a Fundación → el modo se fuerza a PCESFL y el radio queda bloqueado.
5. Confirmar que una organización en modo completo conserva las 4 pestañas sin cambios.
