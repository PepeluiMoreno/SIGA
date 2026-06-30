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

## Principio de diseño: datos en su tabla de extensión

El modelo es Party-Role: la identidad común vive en `Contacto`; cada **condición**
(socio, voluntario) es una `Vinculacion` tipada con su **tabla de extensión 1:1**
(`Socio`, `Voluntario`, satélites de `Vinculacion`).

Regla: **los binarios (ficheros/documentos) y los campos calculados (`@property`) que
aplican a la condición de SOCIO o VOLUNTARIO viven en su tabla de extensión**, no en
`Contacto` ni sueltos en los resolvers.

- Datos económicos del socio (iban, cuota, forma de pago, motivos…) → `Socio`.
- Situación efectiva del socio y su color → `Socio.estado_efectivo` / `Socio.estado_color`.
- Documentos, competencias, formación, habilidades y disponibilidad del voluntario →
  cuelgan de `Voluntario` (`voluntario_id` → `voluntarios.id`, ondelete CASCADE).
- `Contacto` solo guarda lo de la persona (identidad, foto, RGPD) y las @property de
  identidad (`tiene_acceso`, `es_voluntario`, `nombre_completo`).

## Cambios pendientes de migrar

- **⏳ Migración `vol1ext2anc3` (ancla datos de voluntario a la extensión Voluntario):**
  ya APLICADA EN DEV. Cambia `miembro_id` → `voluntario_id` (FK a `voluntarios`) en
  `documentos_miembro`, `miembros_competencia`, `formaciones_miembro`,
  `miembros_habilidades`, `franjas_disponibilidad`. La migración hace backfill
  (contacto → su Voluntario) y borra filas sin vinculación de voluntario. **NO aplicada
  en staging/prod**: antes de aplicar allí, verificar conteos de esas tablas (en dev
  estaban vacías → backfill no-op; en staging/prod podría haber datos importados).
- *(Ver también punto 3 arriba: eliminar skill.py.)*

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

**✅ Hecho — habilidades por delegación con guard:**
- Mutaciones `asignarHabilidadVoluntario(miembroId, habilidadId, nivelId?)` y
  `quitarHabilidadVoluntario(miembroId, habilidadId)` (gated `HAB_ASSIGN`) con
  `assert_miembro_en_ambito` (upsert/borra `MiembroHabilidad`).

**✅ Hecho — UI de edición por delegación:**
- En `ListaVoluntarios.vue`, botón "editar" por tarjeta (gated `tienePermiso('MEMBRESIA_VOLUNTARIO_GESTIONAR')`)
  → modal que edita disponibilidad/profesión/intereses/conducción/vehículo/viajar (vía
  `gestionarPerfilVoluntario`) y gestiona habilidades (añadir/quitar con nivel). Queries:
  `GET_CATALOGO_HABILIDADES`, `GET_HABILIDADES_MIEMBRO`.

**✅ Hecho — scoping por campaña (cierre de Fase 2):**
- Al fijar el `responsable_id` de una campaña (crear/actualizar), su usuario recibe el rol
  `COORDINADOR_CAMPANA` (`ensure_rol_coordinador_campania`, idempotente; no se revoca porque el
  ámbito es dinámico: si deja de coordinar, su ámbito de campaña queda vacío).
- Ámbito de un coordinador de campaña = socios que **participan en actividades de las campañas que
  coordina** (`miembros_de_campanias_coordinadas`: `Campania.responsable_id` → `Actividad.campania_id`
  → `Participacion.miembro_id`).
- Integrado: `voluntariosEnAmbito` filtra **territorial ∪ campañas**; `assert_miembro_en_ambito`
  admite ambas vías. (No verificable end-to-end en dev por falta de datos de campaña; misma forma
  SQL que la vía territorial, ya verificada.)

**Fase 2 completa.**

## Pasos para aplicar el lote

```bash
docker compose -f docker-compose.dev.yml --env-file .env.dev exec backend alembic upgrade head
docker compose -f docker-compose.dev.yml --env-file .env.dev restart backend
```
