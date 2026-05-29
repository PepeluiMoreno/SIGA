# Módulo Membresía — estado y cambios pendientes

> **Workflow**: NO aplicar `alembic upgrade head` ni reiniciar backend por cada cambio.
> Acumular SQL y cambios de modelo aquí; ejecutar de una vez al cerrar el lote.

---

## Estado actual del modelo (2026-05-15)

### Tablas del módulo

| Tabla | Clase Python | Archivo |
|---|---|---|
| `miembros` | `Miembro` | `miembro.py` |
| `tipos_miembro` | `TipoMiembro` | `miembro.py` |
| `estados_miembro` | `EstadoMiembro` | `estado_miembro.py` |
| `habilidades` | `Habilidad` | `habilidad.py` |
| `categorias_habilidad` | `CategoriaHabilidad` | `categoria_habilidad.py` |
| `niveles_habilidad` | `NivelHabilidad` | `nivel_habilidad.py` |
| `disponibilidad` | `Disponibilidad` | `disponibilidad.py` |
| `niveles_estudios` | `NivelEstudios` | `nivel_estudios.py` |
| `historial_agrupacion` | `HistorialAgrupacion` | `historial_agrupacion.py` |
| `historial_nombramiento` | `HistorialNombramiento` | `historial_nombramiento.py` |
| `juntas` | `Junta` | `junta.py` |
| `motivos_baja` | `MotivoBaja` | `motivo_baja.py` |
| `coordinacion_territorial` | `CoordinacionTerritorial` | `coordinacion_territorial.py` |
| `voluntariado` | `Voluntariado` | `voluntariado.py` |

> **Nota**: `skill.py` existe en el directorio pero está marcado para eliminar (palabra prohibida en el proyecto).
> Ver memory `feedback_no_skill_word.md`.

---

## Pendientes de diseño

### 1. Avisos de perfil incompleto (pendiente módulo comunicación interna)

Avisar al miembro y al coordinador cuando falten campos obligatorios: tipo, estado, email o teléfono.
Ver memory: `project_avisos_perfil_incompleto.md`

### 2. MisDatos — detalle completo del socio logueado (pendiente)

La ruta `/mis-datos` debe reproducir `MiembroDetail.vue` filtrado al usuario logueado.
Ver memory: `project_mis_datos_detalle_socio.md`

### 3. Eliminar `skill.py` y tabla `miembro_skills` (pendiente)

Palabra prohibida en el proyecto. Tabla y archivo a eliminar en la próxima migración de limpieza.
El concepto se cubre con `Habilidad`, `CategoriaHabilidad` y `NivelHabilidad`.

**SQL pendiente** (acumular con el siguiente lote):
```sql
DROP TABLE IF EXISTS miembro_skills;
```
Y borrar el archivo `backend/app/modules/membresia/models/skill.py`.

---

## Cambios pendientes de migrar

*(Ver punto 3 arriba)*

---

## Voluntariado por delegación — control de acceso (regla de negocio, 2026-05-29)

### Regla (para el manual)
La sección **Voluntariado** sirve para **incorporar a un socio como voluntario** registrando sus
**disponibilidades y habilidades**. Puede hacerlo:
- El **propio socio**, sobre sus datos personales.
- **Por delegación**, los perfiles **Presidente**, **Coordinador** y **Coordinador de campaña**:
  - Presidente y cargos **generales**: sin límite territorial.
  - Cargos **territoriales**: solo dentro de **su ámbito territorial** (su agrupación y descendientes).
  - Coordinador de campaña: dentro del ámbito de su campaña.
- (Sin despliegue territorial → todo es "general": ver regla transversal en modulo_actividades.md §9).

### Decisiones (2026-05-29)
1. **Crear rol orgánico `COORDINADOR_CAMPANA`** (ámbito = su campaña). No existía.
2. **Implementación por fases**:
   - **Fase 1**: restringir el acceso por **rol** (PRESIDENTE, COORDINADOR + variantes, COORDINADOR_CAMPANA).
   - **Fase 2**: **filtro territorial** — la lista/edición de voluntarios se limita a los socios de la
     agrupación del `UsuarioRol` del usuario (`UsuarioRol.agrupacion_id`, ya existe en el modelo).

### Estado técnico encontrado
- Acceso por código de transacción (`usePermisos()` → `misTransacciones`).
- La ruta `/voluntarios` y el sidebar gatean con **`HAB_LIST`**, pero el diccionario define
  `VOL_LIST`/`VOL_VIEW`/`HAB_MANAGE` (no `HAB_LIST`). **Incoherencia a resolver** en Fase 1.
- Roles organizativos en `seed_roles_organizacionales.py` (`ORGANIZACION_ROLES`); permisos por rol
  en ficheros `seed_permisos_*.py` (patrón `REPARTO = {rol: [transacciones]}`).

### Fase 1 — ✅ HECHA (2026-05-29)
Códigos de transacción **reales** del catálogo (el diccionario tenía `HAB_MANAGE`, que no existe):
- `VOL_LIST` (listar), `VOL_VIEW` (ver perfil), `MEMBRESIA_VOLUNTARIO_GESTIONAR` (gestionar
  disponibilidad por delegación), `HAB_ASSIGN` (asignar habilidad a miembro), `HAB_LIST` (catálogo).
- `HAB_ASSIGN_OWN` ("declarar habilidades propias") es la del **propio socio**, no se reparte.

Hecho:
1. `seed_roles_organizacionales.py` → rol **`COORDINADOR_CAMPANA`** (es_territorial=False, nivel 9). ✅
2. `seed_permisos_voluntariado.py` (nuevo) → reparte los 5 códigos a PRESIDENTE, VICEPRESIDENTE,
   COORDINADOR, COORD_PROV, COORD_LOCAL, COORDINADOR_CAMPANA. ✅ (verificado en BD)
3. Guard de ruta `/voluntarios` y sidebar: `HAB_LIST` → **`VOL_LIST`**. ✅
4. **NO** se engancha en `bootstrap.py`: la convención es ejecutar estos seeds **a mano**
   (`docker compose ... exec backend python -m app.scripts.seeding.seed_roles_organizacionales`
   y `...seed_permisos_voluntariado`). Idempotentes. **No requiere restart** (misTransacciones lee
   de BD en vivo; los usuarios afectados solo deben re-loguear para refrescar sus códigos).
   ⚠️ **Deploy staging**: ejecutar allí los dos seeds una vez.

### Fase 2 — scoping territorial (parcial, 2026-05-29)
Helper en `backend/app/modules/acceso/services/ambito_territorial.py`
(`agrupaciones_en_ambito(session, usuario_id) -> set[UUID] | None`; None = global; trata NULL/raíz
como global; **excluye `COORDINADOR_CAMPANA`** que va por campaña). CTE recursivo para descendientes.

**✅ Hecho — listado scoped:**
- Resolver `voluntariosEnAmbito` (`MembresiaQuery` en `membresia_resolvers.py`, tipo `VoluntarioType`),
  gated `RequireTransaction("VOL_LIST")`; filtra `Miembro.agrupacion_id IN (ámbito)` salvo global.
- Merge en `schema_simple.py` (`Query(..., MembresiaQuery)`).
- Frontend: `GET_VOLUNTARIOS` usa `voluntariosEnAmbito`; `ListaVoluntarios.vue` lee `data.voluntariosEnAmbito`.
- Verificado: admin (global) ve todos; ámbito territorial filtra al subárbol.

**✅ Hecho — gestión por delegación con guard:**
- Mutación **`gestionarPerfilVoluntario`** (`MembresiaResolverMutation`, gated
  `MEMBRESIA_VOLUNTARIO_GESTIONAR`): edita SOLO campos de voluntariado (disponibilidad, profesión,
  intereses, puede_conducir, etc.), sin tocar el resto del socio ni requerir `MEMBRESIA_MIEMBRO_EDITAR`.
- Guard `assert_miembro_en_ambito(session, usuario_id, miembro_id)` (en `ambito_territorial.py`):
  lanza `PermissionError` si el socio está fuera del ámbito; global ⇒ no restringe. **No se salta por API.**

**❌ Pendiente (resto Fase 2):**
- **Scoping por campaña** de `COORDINADOR_CAMPANA` (depende del flujo de nombrar coordinador de
  campaña, aún sin construir). De momento un COORDINADOR_CAMPANA "solo" tiene ámbito vacío por la vía
  territorial ⇒ no ve/edita nada (deniega, seguro).
- **UI de edición por delegación**: formulario en la vista de voluntarios que llame a
  `gestionarPerfilVoluntario` (la lista es hoy de solo lectura). La asignación de habilidades por
  delegación (`HAB_ASSIGN`) usa hoy el CRUD strawchemy genérico (sin guard de ámbito) — pendiente.

## Pasos para aplicar el lote

```bash
docker compose -f docker-compose.dev.yml --env-file .env.dev exec backend alembic upgrade head
docker compose -f docker-compose.dev.yml --env-file .env.dev restart backend
```
