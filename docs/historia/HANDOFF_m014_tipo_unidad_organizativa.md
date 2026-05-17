# Handoff — TipoUnidadOrganizativa (migración m014)

**Fecha:** 2026-05-06  
**Rama:** master  
**Autor:** PepeluiMoreno + Claude

---

## Contexto

El modelo `AgrupacionTerritorial` tenía el tipo codificado como String libre
(`LOCAL / PROVINCIAL / AUTONOMICO / NACIONAL`) y un campo `nivel` entero
hardcodeado para la jerarquía española. Esto impedía representar cualquier
estructura organizativa de una ONG o fundación internacional.

Se reemplazó por un catálogo `TipoUnidadOrganizativa` con dos dimensiones:

- **naturaleza**: `TERRITORIAL | FUNCIONAL | PROGRAMATICA | ADMINISTRATIVA`
- **vínculo jurídico**: `INTERNA | FILIAL | FEDERADA`
- **nivel**: `1 | 2 | 3 | null` — jerárquico solo para tipos TERRITORIAL;
  null para tipos transversales.

---

## Estado

Backend y frontend **completados y en producción** (backend arrancado sin errores).  
La BD tiene alembic en `m014` y 7 tipos por defecto insertados.

---

## Ficheros modificados o creados

### Backend

| Fichero | Tipo | Descripción |
|---|---|---|
| `backend/app/modules/core/geografico/tipo_unidad_organizativa.py` | **NUEVO** | Modelo `TipoUnidadOrganizativa` con enums `NaturalezaUnidad` y `VinculoUnidad` |
| `backend/app/modules/core/geografico/direccion.py` | modificado | `AgrupacionTerritorial`: elimina `tipo`/`nivel`, añade `tipo_id` FK, `nif`, `fecha_constitucion`, `registro_oficial`, relación `tipo_unidad`, propiedad calculada `nivel` |
| `backend/app/modules/core/geografico/__init__.py` | modificado | Exporta `TipoUnidadOrganizativa`, `NaturalezaUnidad`, `VinculoUnidad` |
| `backend/app/models/__init__.py` | modificado | Idem |
| `backend/alembic/versions/m014_add_tipo_unidad_organizativa.py` | **NUEVO** | Migración DDL (ya aplicada directo a BD) |
| `backend/app/graphql/types_auto.py` | modificado | Añade `TipoUnidadOrganizativaType` |
| `backend/app/graphql/inputs_auto.py` | modificado | Añade `TipoUnidadOrganizativaCreateInput`, `UpdateInput`, `Filter` |
| `backend/app/graphql/schema_simple.py` | modificado | Query `tiposUnidadesOrganizativas` |
| `backend/app/graphql/mutations.py` | modificado | Mutations `crear/actualizar/eliminar_tipo_unidad_organizativa` |

### Frontend

| Fichero | Tipo | Descripción |
|---|---|---|
| `frontend/src/composables/useUnidadesOrganizativas.js` | **NUEVO** | Composable CRUD para tipos y unidades organizativas |
| `frontend/src/graphql/queries/catalogos.js` | modificado | Queries `GET/CREATE/UPDATE/DELETE_TIPO_UNIDAD_ORGANIZATIVA`; `GET_AGRUPACIONES_TERRITORIALES` actualizado (sin `tipo`/`nivel`, con `tipoUnidad { }`) |
| `frontend/src/views/parametrizacion/EstructuraOrganizativa.vue` | **NUEVO** | Pantalla de configuración: edición inline de 3 niveles territoriales + lista de tipos transversales |
| `frontend/src/modules/membresia/views/ArbolUnidades.vue` | **NUEVO** | Vista árbol operativa con formulario modal de alta/edición; reemplaza `ListaAgrupaciones` en el router |
| `frontend/src/modules/membresia/views/NodoArbol.vue` | **NUEVO** | Sub-componente recursivo para renderizar cada nodo del árbol |
| `frontend/src/router/index.js` | modificado | `/agrupaciones` → `ArbolUnidades`; nueva ruta `/configuracion/estructura` → `EstructuraOrganizativa` |

---

## BD — Datos migrados

```
tipos_unidades_organizativas (7 filas):
  nivel 1 → Sede / Federación nacional   (TERRITORIAL, INTERNA)
  nivel 2 → Delegación regional          (TERRITORIAL, INTERNA)
  nivel 3 → Grupo local                  (TERRITORIAL, INTERNA)
  null    → Sección funcional            (FUNCIONAL, INTERNA)
  null    → Área programática            (PROGRAMATICA, INTERNA)
  null    → Entidad filial               (TERRITORIAL, FILIAL)
  null    → Entidad federada             (TERRITORIAL, FEDERADA)

agrupaciones_territoriales:
  - 1 registro migrado a nivel 1 (tipo original NACIONAL/similar)
  - 62 registros migrados a nivel 2 (tipo original AUTONOMICO/similar)
  - 0 registros migraron a nivel 3 (ninguno con tipo LOCAL/similar)
  - Columnas eliminadas: tipo, nivel
  - Columnas añadidas: tipo_id, nif, fecha_constitucion, registro_oficial
```

---

## Verificación pendiente (manual)

```graphql
# Debe devolver 7 registros
{ tiposUnidadesOrganizativas { id nombre naturaleza vinculo nivel activo } }

# Debe devolver unidades con tipoUnidad poblado
{ agrupacionesTerritoriales { id nombre tipoId tipoUnidad { nombre naturaleza } } }
```

1. `/configuracion/estructura` → carga tipos sin error de consola
2. `/agrupaciones` → árbol anidado visible
3. Crear unidad con tipo FILIAL/FEDERADA → aparece sección "Datos jurídicos"
4. Crear unidad con tipo INTERNA → sección "Datos jurídicos" NO aparece

---

## Correcciones posteriores

### EstructuraOrganizativaEditor.vue — botones sin `type="button"`
`frontend/src/components/configuracion/EstructuraOrganizativaEditor.vue` está embebido dentro del `<form>` de `ParametrosGenerales.vue`. Todos sus `<button>` carecían de `type="button"`, así que cualquier clic disparaba el submit del formulario padre en lugar de ejecutar el handler. Se añadió `type="button"` a todos los botones del componente.  
Adicionalmente se renombró el radio "Asociación jerárquica" → **"Asociación con organización extendida"**.

---

## Notas importantes

- **`ListaAgrupaciones.vue` sigue existiendo** — el router ya no la usa
  en `/agrupaciones` pero puede estar referenciada en otros componentes
  (p.ej. `JuntasDirectivas.vue`). No borrar sin revisar.

- **Cualquier componente que leyera `agrupacion.tipo` o `agrupacion.nivel`**
  directamente dejará de funcionar — esos campos ya no existen en la BD.
  Buscar con: `grep -r "\.tipo\b\|\.nivel\b" frontend/src/modules/membresia/`

- **`nivel_territorial` en el modelo `Rol`** (String con valores "AUTONOMICO"
  etc.) no fue tocado — es un campo distinto, fuera del alcance.

- **`agrupacion_territorial_view.py`** y `vista_agrupaciones_territoriales`
  (vista materializada que lee de `organizaciones`) no fueron tocados — son
  código legacy independiente.

- Imports siempre absolutos: `from app.modules.core.geografico import ...`
