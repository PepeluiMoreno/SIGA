# Módulo Acceso (RBAC) — estado y cambios pendientes

> **Workflow**: NO aplicar `alembic upgrade head` ni reiniciar backend por cada cambio.
> Acumular SQL y cambios de modelo aquí; ejecutar de una vez al cerrar el lote.

---

## Estado actual del modelo (2026-05-15)

### Tablas principales

| Tabla | Clase Python | Descripción |
|---|---|---|
| `usuarios` | `Usuario` | Cuenta de acceso a la aplicación |
| `roles` | `Rol` | Roles del sistema (ADMIN, SOCIO, TESORERO, etc.) |
| `tipos_rol` | `TipoRol` (enum) | Clasificación de roles |
| `transacciones` | `Transaccion` | Operaciones funcionales del sistema |
| `rol_transaccion` | `RolTransaccion` | Tabla pivote rol↔transaccion |
| `cargos` | `Cargo` | Puestos dentro de la organización |
| `funcionalidades` | `Funcionalidad` | Módulos/secciones funcionales |
| `auditoria` | `Auditoria` | Log de auditoría de acciones |
| `seguridad` | — | Configuración de seguridad |

### Lógica RBAC
- Permiso = `Transaccion` (unidad atómica de permiso: `CREAR_MIEMBRO`, `VER_CONTABILIDAD`, etc.)
- `Rol` agrupa `Transaccion`s via `RolTransaccion`
- El usuario tiene uno o más `Rol`es; sus permisos son la unión de todas sus transacciones
- El frontend usa `usePermisos()` → `tienePermiso(codigo_transaccion)` para controlar la UI

---

## Documentación de referencia

Documentos detallados en `backend/app/modules/acceso/docs/`:

- [acceso_arquitectura.md](../backend/app/modules/acceso/docs/acceso_arquitectura.md) — Arquitectura RBAC completa
- [acceso_usuarios_roles.md](../backend/app/modules/acceso/docs/acceso_usuarios_roles.md) — Diseño de usuarios y roles
- [funcionalidad_eventos_permission_matrix.md](../backend/app/modules/acceso/docs/funcionalidad_eventos_permission_matrix.md) — Matriz de permisos por funcionalidad

---

## Pendientes de diseño

### 1. Control de acceso en UI según rol (pendiente)

El composable `usePermisos()` está implementado pero el uso de `v-if="tienePermiso(...)"` en
vistas individuales está incompleto. Completar tras el módulo membresía.
Ver memory: `project_acceso_ui_permisos.md`

### 2. Modal crear cuenta desde ficha de miembro (pendiente)

En la pestaña "Acceso y roles" de `MiembroDetail.vue`, si el miembro no tiene cuenta,
ofrecer un modal para crearla en el momento con envío de correo de bienvenida.
Ver memory: `project_modal_crear_cuenta_desde_miembro.md`

---

## Cambios pendientes de migrar

*(Vacío — acumular aquí cuando se acuerde el próximo lote)*
