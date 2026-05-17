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

## Pasos para aplicar el lote

```bash
docker compose -f docker-compose.dev.yml --env-file .env.dev exec backend alembic upgrade head
docker compose -f docker-compose.dev.yml --env-file .env.dev restart backend
```
