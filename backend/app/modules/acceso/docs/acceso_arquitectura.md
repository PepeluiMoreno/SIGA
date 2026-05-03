# Módulo Acceso — Arquitectura y especificaciones

## 1. Responsabilidad del módulo

El módulo `acceso` centraliza todo lo relacionado con identidad, autenticación,
autorización y auditoría. Es el núcleo de seguridad de la aplicación; ningún
otro módulo contiene lógica de permisos.

---

## 2. Modelo de dominio

### 2.1 Entidades principales

```
Usuario
├── credenciales (JWT / sesión)
├── Roles directos (UsuarioRol)
└── Roles por cargo (vía Miembro → Cargo → Rol)

Rol
├── Transacciones directas (RolTransaccion)
└── Funcionalidades (RolFuncionalidad → Funcionalidad → FuncionalidadTransaccion)

Funcionalidad
└── Transacciones con ámbito (FuncionalidadTransaccion.ambito)

FlujoAprobacion
├── transaccion_inicio  (quien propone)
├── transaccion_aprobacion (quien aprueba)
├── transaccion_rechazo (opcional)
└── rol_aprobador
```

### 2.2 Tablas del módulo

| Tabla                       | Propósito                                        |
|-----------------------------|--------------------------------------------------|
| `usuarios`                  | Identidad del sistema                            |
| `roles`                     | Catálogo de roles (RBAC)                         |
| `transacciones`             | Catálogo de operaciones autorizables             |
| `roles_transacciones`       | Permisos directos rol → transacción              |
| `funcionalidades`           | Agrupaciones lógicas de transacciones            |
| `roles_funcionalidades`     | Capa 1: rol accede a funcionalidad completa      |
| `funcionalidades_transacciones` | Capa 2: transacción dentro de funcionalidad + ámbito |
| `flujos_aprobacion`         | Capa 3: cadenas de aprobación entre roles        |
| `sesiones`                  | Sesiones activas                                 |
| `log_auditoria`             | Registro de cada acción autorizada               |

---

## 3. Sistema de autorización en tres capas

### Capa 1 — Rol → Transacción directa (`RolTransaccion`)

Permisos granulares y explícitos. Un rol tiene permiso sobre una transacción
concreta. Válido para operaciones administrativas del propio módulo de acceso.

### Capa 2 — Rol → Funcionalidad → Transacción (`RolFuncionalidad` + `FuncionalidadTransaccion`)

Un rol recibe acceso a una *funcionalidad* (conjunto coherente de operaciones).
Cada transacción de la funcionalidad lleva un `ambito`:

| Ámbito       | Significado                                                      |
|--------------|------------------------------------------------------------------|
| GLOBAL       | El usuario puede actuar sobre cualquier entidad del sistema      |
| TERRITORIAL  | Solo sobre entidades de su agrupación territorial                |
| PROPIO       | Solo sobre entidades con vínculo directo al usuario              |

**Ejemplo:** El rol `DISENADOR_CAMPANA` tiene la funcionalidad `DISENO_CAMPANA`.
Esa funcionalidad incluye `CAMPANA_CREAR` (TERRITORIAL) y `CAMPANA_PUBLICAR` (GLOBAL).

### Capa 3 — Flujo de aprobación (`FlujoAprobacion`)

Modela operaciones que requieren intervención de otro rol para completarse.

```
ROL_DISENADOR       ejecuta  CAMPANA_PROPONER_PRESUPUESTO
        ↓  (estado: PENDIENTE_APROBACION)
ROL_JUNTA_DIRECTIVA ejecuta  CAMPANA_APROBAR_PRESUPUESTO | CAMPANA_RECHAZAR_PRESUPUESTO
```

El `FlujoAprobacion` no gestiona la lógica de estado (eso es responsabilidad del
servicio del módulo afectado); solo define qué transacciones activan y resuelven
el flujo y qué rol tiene la potestad de aprobación.

---

## 4. PermissionMatrix — cache en memoria

### Propósito

Evitar consultas DB en cada request de autorización. La matriz se construye una
vez al arrancar y se invalida y reconstruye cuando cambia la configuración de
roles o permisos.

### Componentes

```
AsyncPermissionMatrixBuilder  →  PermissionMatrixSnapshot
PermissionMatrixCache (global) ← invalidate_and_rebuild()
Context.check_permission()     ← usa la cache sin DB
```

### Ciclo de vida

1. **Arranque** (`lifespan` de FastAPI): `matrix_cache.rebuild(session)`
2. **Request normal**: `ctx.check_permission("CAMPANA_CREAR")` — O(1), sin DB
3. **Mutación de permisos**: el servicio publica un `DomainEvent` → event bus →
   `invalidate_and_rebuild()` en background

---

## 5. Catálogo de funcionalidades (registro dinámico)

Cada módulo tiene un archivo `catalog.py` que declara sus funcionalidades y
transacciones llamando a `ModuleCatalog.register_*`. Al arrancar la aplicación,
`CatalogSyncService.sync()` hace upsert de esas definiciones en DB.

Resultado: la UI del `EditorRol` siempre muestra las funcionalidades actuales
del código sin intervención manual.

### Ejemplo — catalog.py de un módulo

```python
from app.modules.acceso.services.registry import (
    ModuleCatalog, FuncionalidadDef, FuncionalidadTransaccionDef,
    TransaccionDef, AmbitoTransaccion,
)

ModuleCatalog.register_transaccion("campana", TransaccionDef(
    codigo="CAMPANA_CREAR",
    nombre="Crear campaña",
    tipo="MUTACION",
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="DISENO_CAMPANA",
    nombre="Diseño de campaña",
    modulo="actividades",
    transacciones=[
        FuncionalidadTransaccionDef("CAMPANA_CREAR", AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("CAMPANA_PUBLICAR", AmbitoTransaccion.GLOBAL),
    ],
))
```

---

## 6. Integración con Strawberry (GraphQL)

Los resolvers usan `permission_classes` de Strawberry:

```python
from app.graphql.permissions import RequireTransaction

@strawberry.mutation(permission_classes=[RequireTransaction("CAMPANA_CREAR")])
async def crear_campana(self, info: Info, input: CampanaInput) -> Campana:
    ...
```

`RequireTransaction` delega en `ctx.check_permission()`, que consulta la matrix
en memoria. Sin DB, sin lógica de permisos en el resolver.

---

## 7. Flujo de autorización completo (por request)

```
HTTP Request
    ↓ JWT decode → user_id, territory_id, role_ids (claims)
Context.__init__
    ↓
resolver llama permission_classes
    ↓
RequireTransaction.has_permission()
    ↓
Context.check_permission("CAMPANA_CREAR")
    ↓
matrix_cache.can(role_ids, "CAMPANA_CREAR")  ← sin DB
    ↓
ALLOW / DENY
```

---

## 8. Auditoría

Todo acceso autorizado debe registrar en `log_auditoria`:

| Campo             | Contenido                                 |
|-------------------|-------------------------------------------|
| `usuario_id`      | ID del usuario                            |
| `transaccion`     | Código de la transacción ejecutada        |
| `entidad`         | Aggregate afectado (nombre + ID)          |
| `agrupacion_id`   | Territorio en contexto                    |
| `resultado`       | ALLOW / DENY                              |
| `timestamp`       | `func.now()`                              |

---

## 9. Feature flag MULTITERRITORIAL_MODE

Si `False`: `UsuarioRol.agrupacion_id` siempre es `NULL` y las consultas de
roles por posición no filtran por territorio.

Si `True`: los roles se evalúan también por agrupación, habilitando juntas
territoriales independientes con permisos diferenciados.

El flag vive en `configuracion/models/configuracion.py → Configuracion`.

---

## 10. Casos de uso del módulo

- Registro y activación de usuarios
- Asignación y revocación de roles (directos y por cargo)
- Definición de funcionalidades y su asignación a roles (EditorRol)
- Definición de flujos de aprobación
- Consulta de auditoría de acceso
- Gestión de sesiones y bloqueos de IP
