
en una aplicación con python, sqlalchemy , strawberry y postgresql. en el backend y vue3  y vite en el frontend, como hago para hacerla totalmente modular  de forma que se puedan poner y quitar exte siones o plugins a la aplicación? y como podemos hacer para que haya un RBAC para esa modularizacion

1:01
Buena pregunta. Te explico la arquitectura completa.

Arquitectura modular con plugin system + RBAC
Concepto central
Cada módulo/plugin es un paquete Python autocontenido que:

Se registra en el sistema al arrancar
Declara sus propios tipos GraphQL (Strawberry)
Declara sus propios modelos SQLAlchemy
Declara los permisos que necesita
Backend (Python + SQLAlchemy + Strawberry)
1. Estructura de directorios
app/
├── core/
│   ├── plugin_registry.py      # Motor de plugins
│   ├── schema_builder.py       # Ensambla el schema GraphQL
│   ├── rbac.py                 # Motor RBAC
│   ├── models.py               # User, Role, Permission (core)
│   └── database.py
├── plugins/
│   ├── __init__.py
│   ├── blog/
│   │   ├── plugin.py           # Manifiesto del plugin
│   │   ├── models.py
│   │   ├── schema.py           # Queries/Mutations propias
│   │   └── permissions.py      # Permisos que declara
│   └── ecommerce/
│       ├── plugin.py
│       ├── models.py
│       ├── schema.py
│       └── permissions.py
├── config.py                   # Lista de plugins activos
└── main.py
2. El Plugin Registry
python
# core/plugin_registry.py
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class PluginManifest:
    name: str
    version: str
    description: str
    permissions: list[str]          # permisos que declara
    get_query_fields: Callable      # fn que devuelve campos Query
    get_mutation_fields: Callable   # fn que devuelve campos Mutation
    models_module: str              # ruta al módulo de modelos

class PluginRegistry:
    _plugins: dict[str, PluginManifest] = {}

    def register(self, manifest: PluginManifest):
        self._plugins[manifest.name] = manifest

    def get_all(self) -> list[PluginManifest]:
        return list(self._plugins.values())

    def get(self, name: str) -> PluginManifest | None:
        return self._plugins.get(name)

registry = PluginRegistry()
3. Manifiesto de un plugin
python
# plugins/blog/plugin.py
from core.plugin_registry import PluginManifest, registry
from plugins.blog.schema import get_query_fields, get_mutation_fields

manifest = PluginManifest(
    name="blog",
    version="1.0.0",
    description="Blog con posts y comentarios",
    permissions=[
        "blog:read",
        "blog:create",
        "blog:edit",
        "blog:delete",
        "blog:moderate",
    ],
    get_query_fields=get_query_fields,
    get_mutation_fields=get_mutation_fields,
    models_module="plugins.blog.models",
)

registry.register(manifest)
4. Schema builder dinámico
python
# core/schema_builder.py
import strawberry
from strawberry.types import Info
from core.plugin_registry import registry

def build_schema():
    query_fields = {}
    mutation_fields = {}

    for plugin in registry.get_all():
        query_fields.update(plugin.get_query_fields())
        mutation_fields.update(plugin.get_mutation_fields())

    # Construye clases dinámicamente
    Query = type("Query", (), query_fields)
    Mutation = type("Mutation", (), mutation_fields)

    Query = strawberry.type(Query)
    Mutation = strawberry.type(Mutation)

    return strawberry.Schema(query=Query, mutation=Mutation)
5. RBAC — Modelos core
python
# core/models.py
from sqlalchemy import Table, Column, ForeignKey, String
from sqlalchemy.orm import relationship, DeclarativeBase

class Base(DeclarativeBase):
    pass

role_permissions = Table(
    "role_permissions", Base.metadata,
    Column("role_id", ForeignKey("roles.id")),
    Column("permission_id", ForeignKey("permissions.id")),
)

user_roles = Table(
    "user_roles", Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("role_id", ForeignKey("roles.id")),
)

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(String, primary_key=True)  # e.g. "blog:create"
    module = Column(String)                 # e.g. "blog"
    description = Column(String)

class Role(Base):
    __tablename__ = "roles"
    id = Column(String, primary_key=True)
    permissions = relationship("Permission", secondary=role_permissions)

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    roles = relationship("Role", secondary=user_roles)
6. Motor RBAC + decorador para resolvers
python
# core/rbac.py
from functools import wraps
from strawberry.types import Info

class RBACEngine:
    def check(self, user, permission: str) -> bool:
        for role in user.roles:
            for perm in role.permissions:
                if perm.id == permission:
                    return True
        return False

rbac = RBACEngine()

def require_permission(permission: str):
    """Decorador para resolvers de Strawberry."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, info: Info, **kwargs):
            user = info.context["user"]   # viene del middleware de auth
            if not user or not rbac.check(user, permission):
                raise PermissionError(f"Requiere permiso: {permission}")
            return fn(*args, info=info, **kwargs)
        return wrapper
    return decorator
Uso en un resolver del plugin:

python
# plugins/blog/schema.py
import strawberry
from core.rbac import require_permission

@strawberry.type
class BlogQuery:
    @strawberry.field
    @require_permission("blog:read")
    def posts(self, info) -> list[PostType]:
        ...

@strawberry.type
class BlogMutation:
    @strawberry.mutation
    @require_permission("blog:create")
    def create_post(self, info, title: str, body: str) -> PostType:
        ...
7. Activar/desactivar plugins en config
python
# config.py
ACTIVE_PLUGINS = [
    "plugins.blog.plugin",
    # "plugins.ecommerce.plugin",   # comentar = desactivado
]
python
# main.py
import importlib
from config import ACTIVE_PLUGINS
from core.schema_builder import build_schema

# Carga solo los plugins activos
for module_path in ACTIVE_PLUGINS:
    importlib.import_module(module_path)

# Al arrancar: sincroniza permisos declarados → BD
def sync_permissions():
    from core.plugin_registry import registry
    from core.models import Permission
    # Inserta en BD los permisos de cada plugin activo
    for plugin in registry.get_all():
        for perm_id in plugin.permissions:
            # upsert
            ...

schema = build_schema()
Frontend (Vue 3 + Vite)
Estructura modular
src/
├── core/
│   ├── plugin-registry.ts
│   ├── router.ts           # router dinámico
│   ├── store/
│   │   └── auth.ts         # user + permissions
│   └── composables/
│       └── usePermission.ts
├── plugins/
│   ├── blog/
│   │   ├── index.ts        # manifiesto del plugin frontend
│   │   ├── routes.ts
│   │   ├── components/
│   │   └── graphql/
│   └── ecommerce/
│       ├── index.ts
│       └── ...
└── main.ts
Plugin frontend manifiesto
typescript
// plugins/blog/index.ts
import type { AppPlugin } from '@/core/plugin-registry'

export const BlogPlugin: AppPlugin = {
  name: 'blog',
  routes: () => import('./routes'),
  navItems: [
    { label: 'Blog', icon: 'file-text', to: '/blog', permission: 'blog:read' }
  ],
}
Registry + router dinámico
typescript
// core/plugin-registry.ts
import type { Router } from 'vue-router'

export interface AppPlugin {
  name: string
  routes: () => Promise<{ default: RouteRecordRaw[] }>
  navItems: NavItem[]
}

const plugins: AppPlugin[] = []

export function registerPlugin(p: AppPlugin) {
  plugins.push(p)
}

export async function mountPlugins(router: Router) {
  for (const plugin of plugins) {
    const mod = await plugin.routes()
    mod.default.forEach(route => router.addRoute(route))
  }
}

export function getNavItems() {
  return plugins.flatMap(p => p.navItems)
}
RBAC en el frontend
typescript
// composables/usePermission.ts
import { useAuthStore } from '@/core/store/auth'

export function usePermission() {
  const auth = useAuthStore()

  const can = (permission: string): boolean =>
    auth.permissions.includes(permission)

  return { can }
}
vue
<!-- Uso en cualquier componente -->
<script setup>
const { can } = usePermission()
</script>

<template>
  <button v-if="can('blog:create')">Nuevo post</button>
</template>
Guard de rutas:

typescript
// core/router.ts
router.beforeEach((to) => {
  const auth = useAuthStore()
  const required = to.meta.permission as string | undefined

  if (required && !auth.permissions.includes(required)) {
    return '/403'
  }
})
Flujo completo resumido
Arranque backend
  └─ importlib carga solo plugins activos
       └─ cada plugin se registra en PluginRegistry
            └─ schema_builder ensambla el schema GraphQL
                 └─ sync_permissions() escribe permisos en BD

Login de usuario
  └─ JWT contiene roles (o se consultan del contexto)
       └─ middleware GraphQL inyecta user en info.context

Resolver llamado
  └─ @require_permission("blog:create") comprueba RBAC
       └─ si falla → PermissionError → error GraphQL

Frontend
  └─ al login, Apollo query trae user.permissions[]
       └─ Pinia lo almacena
            └─ v-if="can('blog:create')" / router guard
Puntos clave para producción
Sync de permisos al arrancar: cuando activas un plugin nuevo, sus permisos aparecen en BD automáticamente. Cuando lo desactivas, los permisos quedan huérfanos (no los borres automáticamente, un admin puede querer conservar la configuración de roles).
Alembic + plugins: cada plugin puede tener su propia carpeta migrations/. Usa múltiples version_locations en alembic.ini.
Feature flags en BD: para activar/desactivar plugins sin redeployar, mueve ACTIVE_PLUGINS a una tabla plugin_config y añade un panel de administración.
¿Quieres que profundice en alguna parte concreta: el schema builder, el sistema de migraciones por plugin, o el panel de admin para gestionar plugins y roles?

aplica este concepto a la aplicación SIGA

1:03
Necesito ver el repositorio de SIGA para entender su estructura actual antes de aplicar el concepto. ¿Puedes darme la URL del repo?

https://github.com/PepeluiMoreno/SIGA

1:04

Se ejecutaron 10 comandos, vio 4 archivos
Se ejecutaron 10 comandos, vio 4 archivos
Ya tengo todo el contexto que necesito. He estudiado SIGA a fondo. Déjame explicarte exactamente dónde está ahora y qué hay que hacer.

Diagnóstico: ¿Dónde está SIGA ahora?
La buena noticia: SIGA ya tiene el 70% de la arquitectura modular hecha sin saberlo:

Componente	Estado actual	Lo que falta
ModuleCatalog + registry.py	✅ Existe y funciona	Formalizar como plugin manifest
catalog.py por módulo	✅ Existe en acceso, membresia, actividades, economico	Añadir enabled flag
PermissionMatrix en memoria	✅ Implementada	Hacerla reaccionar a módulos activos
usePermisos.js	✅ Funciona	Añadir tieneModulo()
Schema GraphQL dinámico	❌ Monolítico en schema_simple.py	Refactorizar a ensamblado por módulo
Plugin on/off en BD	❌ No existe	Tabla modulo_config
Router dinámico frontend	❌ Rutas hardcoded en router/index.js	Cada módulo registra sus rutas
main.py carga de catálogos	⚠️ try/import manual por módulo	Autodescubrimiento
Plan de refactoring concreto para SIGA
PASO 1 — Tabla modulo_config en BD
Añadir al módulo configuracion/models:

python
# backend/app/modules/configuracion/models/modulo_config.py
from sqlalchemy import Boolean, String, JSON
from app.infrastructure.base_model import BaseModel

class ModuloConfig(BaseModel):
    __tablename__ = "modulo_config"

    codigo        = Column(String, unique=True, nullable=False)  # "membresia"
    nombre        = Column(String, nullable=False)
    descripcion   = Column(String)
    version       = Column(String, default="1.0.0")
    activo        = Column(Boolean, default=True, nullable=False)
    es_core       = Column(Boolean, default=False)   # core no se puede desactivar
    orden_menu    = Column(Integer, default=99)
    config_extra  = Column(JSON, default=dict)       # config específica del módulo
Migración Alembic como siempre.

PASO 2 — Formalizar el manifiesto de cada módulo
Ahora mismo cada catalog.py hace el registro de transacciones/funcionalidades. Hay que añadir el manifiesto de plugin al mismo archivo. Ejemplo con membresia:

python
# backend/app/modules/membresia/catalog.py  (añadir al final)
from app.core.plugin_registry import PluginRegistry

PluginRegistry.register(
    codigo      = "membresia",
    nombre      = "Membresía",
    descripcion = "Gestión de miembros, traslados, voluntariado y juntas",
    version     = "1.0.0",
    es_core     = False,
    orden_menu  = 20,
    # Función que devuelve los campos Query de este módulo
    get_schema_fields = lambda: _get_membresia_schema_fields(),
)
PASO 3 — PluginRegistry central (nuevo fichero)
python
# backend/app/core/plugin_registry.py
from dataclasses import dataclass, field
from typing import Callable, Optional

@dataclass
class PluginManifest:
    codigo:            str
    nombre:            str
    descripcion:       str
    version:           str
    es_core:           bool
    orden_menu:        int
    get_schema_fields: Optional[Callable] = None   # devuelve dict con campos Query/Mutation

class _PluginRegistry:
    def __init__(self):
        self._manifests: dict[str, PluginManifest] = {}

    def register(self, **kwargs) -> None:
        m = PluginManifest(**kwargs)
        self._manifests[m.codigo] = m

    def get_active(self, active_codes: set[str]) -> list[PluginManifest]:
        return [m for m in self._manifests.values()
                if m.es_core or m.codigo in active_codes]

    def get_all(self) -> list[PluginManifest]:
        return list(self._manifests.values())

PluginRegistry = _PluginRegistry()
PASO 4 — Schema GraphQL dinámico (refactorizar schema_simple.py)
Aquí está el cambio más importante. El schema_simple.py monolítico se convierte en un ensamblador:

python
# backend/app/graphql/schema_builder.py  (NUEVO)
import strawberry
from app.core.plugin_registry import PluginRegistry

# Campos que SIEMPRE están (core: auth, geo, config)
from app.graphql.auth import AuthQuery
from app.graphql.configuracion_resolvers import ConfiguracionOrganizacionQuery

def build_schema(active_module_codes: set[str]):
    """Ensambla el schema GraphQL incluyendo solo módulos activos."""

    # Base siempre presente
    query_bases = [AuthQuery, ConfiguracionOrganizacionQuery]
    mutation_bases = []

    # Campos dinámicos por módulo activo
    extra_query_fields = {}
    extra_mutation_fields = {}

    for manifest in PluginRegistry.get_active(active_module_codes):
        if manifest.get_schema_fields:
            fields = manifest.get_schema_fields()
            extra_query_fields.update(fields.get("query", {}))
            extra_mutation_fields.update(fields.get("mutation", {}))

    # Construir Query dinámicamente
    Query = type("Query", tuple(query_bases), extra_query_fields)
    Mutation = type("Mutation", tuple(mutation_bases), extra_mutation_fields)

    Query = strawberry.type(Query)
    Mutation = strawberry.type(Mutation)

    return strawberry.Schema(query=Query, mutation=Mutation)
Y en main.py, en el lifespan:

python
# Obtener módulos activos de BD
from app.modules.configuracion.models import ModuloConfig
result = await session.execute(select(ModuloConfig).where(ModuloConfig.activo == True))
active_codes = {row.codigo for row in result.scalars()}

# Importar catálogos solo de módulos activos (autodescubrimiento)
import importlib
for codigo in active_codes:
    try:
        importlib.import_module(f"app.modules.{codigo}.catalog")
    except ImportError:
        pass

# Construir schema con solo los módulos activos
from app.graphql.schema_builder import build_schema
schema = build_schema(active_codes)
PASO 5 — RBAC: conectar módulos con permisos
El CatalogSyncService ya sincroniza transacciones/funcionalidades a BD. Solo hay que añadir que al desactivar un módulo, sus transacciones queden inaccesibles aunque estén en BD:

python
# backend/app/core/authorization_service.py  (añadir al check)
async def check_transaction(self, user, transaction_code: str) -> bool:
    # Extraer módulo del código: "MEMBRESIA_MIEMBRO_CREAR" → "membresia"
    modulo = transaction_code.split("_")[0].lower()

    # Verificar que el módulo está activo
    modulo_activo = await self._is_modulo_active(modulo)
    if not modulo_activo:
        return False   # el módulo está desactivado → permiso denegado

    # Comprobación normal en PermissionMatrix
    return self.matrix.role_allows_transaction(user.rol, transaction_code)
El PermissionMatrixCache ya existente se invalida cuando cambia ModuloConfig.activo — usar el event_bus que ya tienes en events.py.

PASO 6 — Frontend: router dinámico
Cada módulo registra sus propias rutas. En lugar del index.js monolítico:

javascript
// frontend/src/modules/membresia/index.js  (NUEVO en cada módulo)
export default {
  codigo: 'membresia',
  nombre: 'Membresía',
  icono: 'users',
  ordenMenu: 20,

  // Rutas lazy-loaded
  routes: [
    {
      path: '/miembros',
      component: () => import('./views/ListaMiembros.vue'),
      name: 'Miembros',
      meta: { requiresAuth: true, requiredPermission: 'MEMBRESIA_MIEMBRO_LISTAR' }
    },
    {
      path: '/agrupaciones',
      component: () => import('./views/ListaAgrupaciones.vue'),
      name: 'Agrupaciones',
      meta: { requiresAuth: true, requiredPermission: 'MEMBRESIA_MIEMBRO_LISTAR' }
    },
    // ...resto de rutas del módulo
  ],

  // Entradas de navegación (sidebar)
  navItems: [
    {
      label: 'Miembros',
      to: '/miembros',
      icono: 'users',
      permiso: 'MEMBRESIA_MIEMBRO_LISTAR'
    },
  ]
}
javascript
// frontend/src/core/plugin-registry.js  (NUEVO)
const plugins = []

export function registerPlugin(plugin) {
  plugins.push(plugin)
}

export function getNavItems(tienePermiso) {
  return plugins
    .flatMap(p => p.navItems)
    .filter(item => !item.permiso || tienePermiso(item.permiso))
}

export async function mountPlugins(router, modulosActivos) {
  for (const plugin of plugins) {
    if (!modulosActivos.includes(plugin.codigo)) continue
    plugin.routes.forEach(route => router.addRoute(route))
  }
}
javascript
// frontend/src/main.js  (cambio)
import { registerPlugin } from '@/core/plugin-registry.js'
import MembresiaPlugin from '@/modules/membresia/index.js'
import ActividadesPlugin from '@/modules/actividades/index.js'
import EconomicoPlugin from '@/modules/economico/index.js'
// ... etc.

// Registrar todos (el filtrado lo hace mountPlugins según BD)
registerPlugin(MembresiaPlugin)
registerPlugin(ActividadesPlugin)
registerPlugin(EconomicoPlugin)
Y en el auth.js store, tras el login:

javascript
// Consultar qué módulos están activos en BD
const { modulosActivos } = await graphqlClient.request(MODULOS_ACTIVOS_QUERY)
await mountPlugins(router, modulosActivos)
Resumen de qué tocar y en qué orden
Sprint 1 — Base
  1. Crear ModuloConfig (modelo + migración)
  2. Crear plugin_registry.py (core)
  3. Seed inicial: insertar los 6 módulos actuales en modulo_config

Sprint 2 — Backend dinámico
  4. Añadir manifiesto al catalog.py de cada módulo
  5. Crear schema_builder.py
  6. Refactorizar main.py lifespan
  7. Añadir check de módulo activo en authorization_service

Sprint 3 — Frontend dinámico
  8. Crear index.js en cada módulo frontend
  9. Crear core/plugin-registry.js
  10. Refactorizar router/index.js → mountPlugins()
  11. Añadir query MODULOS_ACTIVOS al login

Sprint 4 — Panel de admin
  12. Vista "Módulos" en administración (activar/desactivar)
  13. Mutation GraphQL toggleModulo (solo SUPERADMIN)
  14. Invalidación de PermissionMatrix vía event_bus al cambiar módulo
  
Lo más delicado es el Sprint 2 paso 5, porque el schema de Strawchemy con strawchemy.field() genera los tipos automáticamente — habría que encapsular eso dentro de la función get_schema_fields() de cada módulo. ¿Quieres que empiece por ese punto concreto con código completo listo para integrar?

lo haremos mañana