# Módulo de Control de Acceso (RBAC)

El control de acceso de SIGA es **basado en transacciones**: cada acción del sistema está
representada por una **transacción** (un permiso atómico), los **roles** agrupan
transacciones, y a cada **usuario** se le asignan roles. Un usuario puede realizar una
acción si alguno de sus roles tiene la transacción correspondiente.

## Conceptos

- **Transacción**: la unidad mínima de permiso. Tiene un código único con **prefijo de
  módulo** (`ECO_`, `SEC_`, `MEMBRESIA_`, `PRESIDENCIA_`, `RGPD_`, `ACCESO_`, `CFG_`,
  `CONTACTO_`, `CAMPANA_`, `ACTIVIDAD_`, `GRUPO_`). El prefijo identifica el **módulo
  dueño** de la acción, **nunca el rol** que la usa: una misma transacción puede asignarse
  a varios roles (los roles no son conjuntos disjuntos de permisos).
- **Funcionalidad**: agrupación de transacciones de un módulo, con su ámbito.
- **Rol**: conjunto de transacciones. Hay roles de SISTEMA (SUPERADMIN), FUNCIONALES
  (PLANIFICADOR, GESTOR_MIEMBROS, INTERVENTOR) y de ORGANIZACIÓN/gobierno (PRESIDENTE,
  VICEPRESIDENTE, SECRETARIO, TESORERO, VOCAL, COORDINADOR…).
- **Ámbito** (`AmbitoTransaccion`): `GLOBAL` (sobre cualquier entidad) o `TERRITORIAL`
  (solo sobre entidades de la agrupación del usuario).

### Tablas

| Tabla | Clase | Descripción |
|---|---|---|
| `usuarios` | `Usuario` | Cuenta de acceso (login por email o username) |
| `roles` | `Rol` | Roles (tipo SISTEMA / FUNCIONAL / ORGANIZACION) |
| `transacciones` | `Transaccion` | Permisos atómicos, con prefijo de módulo |
| `roles_transacciones` | `RolTransaccion` | Pivote rol↔transacción |
| `usuarios_roles` | `UsuarioRol` | Roles del usuario, con ámbito territorial opcional |
| `funcionalidades` | `Funcionalidad` | Agrupación de transacciones por módulo |

## El catálogo por módulo (fuente única de permisos)

Cada módulo declara sus transacciones y funcionalidades en su propio
`app/modules/<modulo>/catalog.py`, mediante `ModuleCatalog.register_transaccion()` y
`register_funcionalidad()`. Ese catálogo es la **única fuente de verdad** de los permisos.

Al arrancar, `main.py` importa el `catalog.py` de cada módulo (por su efecto secundario de
registro) y `CatalogSyncService.sync()` materializa en la base de datos las transacciones
declaradas y las enlaza a SUPERADMIN. Añadir un permiso = declararlo en el catálogo; el
resto es automático.

## El patrón único de gateo: un destino, un permiso, tres capas

Toda pantalla se protege en **tres capas que gatean por el MISMO permiso** `X`:

```
MENÚ     (frontend)  el item se MUESTRA      ⇔  v-if="tienePermiso(X)"
RUTA     (frontend)  la página se ENTRA      ⇔  meta.requiredPermission === X
BACKEND              la operación se EJECUTA ⇔  RequireTransaction(X)
```

El backend es la red de seguridad real (aunque un botón no se oculte, la mutación se
rechaza); el menú y la ruta son comodidad de UX que debe coincidir con él.

### Ruta (router) — seguro por defecto (default-DENY)

El guard de navegación es **default-deny**: toda ruta autenticada debe declarar
`meta.requiredPermission`. Si no lo declara y no está en la allowlist de rutas universales
(`/`, `/mis-datos`, `/chat`, `/ayuda`, `/papelera`), el acceso se **deniega**. Un olvido
bloquea, no abre un agujero.

`requiredPermission` admite un **string** (se exige esa transacción) o un **array** (se
exige tener **alguna**, OR) para pantallas que abren con cualquiera de varios permisos
operativos.

### Menú (AppLayout) — invariante

- Cada **item** se muestra con `v-if="tienePermiso(X)"`, siendo `X` el `requiredPermission`
  de su ruta.
- El **contenedor de sección** se muestra con `tieneAlguno(...)` de la **unión** de los
  permisos de sus items.

Así una sección nunca aparece vacía ni un item queda inalcanzable.

### Vista (composable) — una sola API

La comprobación en componentes usa siempre el composable único
`@/composables/usePermisos.js`:

```js
const { tienePermiso, tieneAlguno, tieneTodos } = usePermisos()
```

- `tienePermiso('X')` — tiene X.
- `tieneAlguno('A','B')` — tiene alguna (OR).
- `tieneTodos('A','B')` — tiene todas (AND).

No se definen helpers de permisos locales ni se encadena `tienePermiso() || tienePermiso()`
a mano: para un OR se usa `tieneAlguno(...)`.

## Asignación de permisos a roles

Los enlaces rol↔transacción se siembran con `seed_permisos_*.py` (idempotentes). El juego
de datos de prueba `python -m app.fixtures` deja los roles de gobierno con sus permisos
consistentes (vacía y re-cablea).

## Cómo añadir una pantalla nueva (checklist)

1. Declarar su transacción en el `catalog.py` del módulo dueño (prefijo de módulo).
2. Proteger su mutación/consulta en el backend con `RequireTransaction('X')`.
3. Declarar la ruta con `meta: { requiresAuth: true, requiredPermission: 'X' }` (o array OR).
4. Añadir el item al menú con `v-if="tienePermiso('X')"` e incluir `X` en el `tieneAlguno`
   del contenedor de su sección.
5. Asignar la transacción a los roles que deban tenerla en el seed de permisos.

## Regla de negocio: dotación de cuenta a un contacto

Una cuenta de usuario no se crea «en el vacío»: siempre se otorga **a un contacto** que ya
tiene un vínculo con la organización. Al dar de alta un usuario no se declara la
vinculación, sino que se **elige a qué contacto se le dota de cuenta de acceso**.

No cualquier contacto puede recibir cuenta. Cada **tipo de vinculación** declara, con el
atributo `permite_cuenta`, si los contactos con ese vínculo pueden ser dotados de cuenta.
Por defecto la habilitan los vínculos que implican operar el sistema —**socio, voluntario
y contratado/a**—, mientras que los meramente relacionales —**firmante, simpatizante,
donante**— no. Es editable en el catálogo de tipos de vinculación.

La vista «Nuevo usuario» presenta un buscador de contactos (filtrable por tipo de vínculo y
por nombre); solo aparecen los contactos cuyo vínculo permite cuenta, e indica si ya tienen
una. Al elegir un contacto, la cuenta queda asociada a él y su correo se propone como email
de acceso.
