# Anexo: Uso de Strawchemy en SIGA

## Introducción

Strawchemy es una librería que integra SQLAlchemy con Strawberry GraphQL, generando automáticamente tipos, queries, mutations y filtros a partir de modelos SQLAlchemy.

**Versión utilizada:** 0.21.0

## Configuración Base

### 1. Inicialización de Strawchemy

```python
# backend/app/graphql/__init__.py

from strawchemy import Strawchemy, StrawchemyAsyncRepository, StrawchemyConfig

# Configuración para PostgreSQL con repositorio asíncrono
config = StrawchemyConfig(
    dialect="postgresql",
    repository_type=StrawchemyAsyncRepository,
)

strawchemy = Strawchemy(config)
```

### 2. Contexto GraphQL con Sesión Async

```python
# backend/app/graphql/context.py

from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext
from ..core.database import async_session

@dataclass
class Context(BaseContext):
    session: AsyncSession

async def get_context() -> Context:
    session = async_session()
    return Context(session=session)
```

### 3. Integración con FastAPI

```python
# backend/app/main.py

from strawberry.fastapi import GraphQLRouter
from .graphql.schema_simple import schema
from .graphql.context import get_context

graphql_router = GraphQLRouter(
    schema=schema,
    context_getter=get_context,
)

app.include_router(graphql_router, prefix="/graphql")
```

## Generación de Tipos GraphQL

### Types (Output)

```python
# backend/app/graphql/types_auto.py

from . import strawchemy
from ..domains.miembros.models import Miembro

# Genera MiembroType con todos los campos del modelo
@strawchemy.type(Miembro, include="all", override=True)
class MiembroType:
    pass
```

**Parámetros importantes:**
- `include="all"`: Incluye todos los campos del modelo
- `override=True`: Permite sobreescribir tipos ya registrados
- `exclude=[...]`: Lista de campos a excluir

### Inputs (Create/Update)

```python
# backend/app/graphql/inputs_auto.py

# Campos de auditoría que se excluyen de inputs
AUDIT_FIELDS = [
    "fecha_creacion",
    "fecha_modificacion",
    "fecha_eliminacion",
    "eliminado",
    "creado_por_id",
    "modificado_por_id",
]

# Input para crear (todos los campos excepto auditoría)
@strawchemy.input(Miembro, mode="create_input", include="all", exclude=AUDIT_FIELDS)
class MiembroCreateInput:
    pass

# Input para actualizar por PK (incluye id obligatorio)
@strawchemy.input(Miembro, mode="update_by_pk_input", include="all", exclude=AUDIT_FIELDS)
class MiembroUpdateInput:
    pass
```

**Modos de input:**
- `create_input`: Para mutations de creación (PK opcional si tiene default)
- `update_by_pk_input`: Para actualización, requiere PK obligatorio
- `update_by_filter_input`: Para actualización masiva por filtro

### Filters

```python
# Para filtrar en queries y deletes
@strawchemy.filter(Miembro)
class MiembroFilter:
    pass
```

## Generación de Queries

### Query Fields

```python
# backend/app/graphql/schema_simple.py

import strawberry
from . import strawchemy
from .types_auto import MiembroType

@strawberry.type
class Query:
    # CORRECTO: Sin argumentos lambda
    miembros: list[MiembroType] = strawchemy.field()

    # INCORRECTO: No usar lambdas
    # miembros: list[MiembroType] = strawchemy.field(lambda: Miembro)  # ERROR!
```

**Importante:** `strawchemy.field()` debe usarse SIN argumentos lambda. Strawchemy infiere el modelo automáticamente desde la anotación de tipo.

## Generación de Mutations

### Mutations CRUD

```python
# backend/app/graphql/mutations.py

import strawberry
from . import strawchemy
from .types_auto import MiembroType
from .inputs_auto import MiembroCreateInput, MiembroUpdateInput, MiembroFilter

@strawberry.type
class Mutation:
    # Crear un registro
    crear_miembro: MiembroType = strawchemy.create(MiembroCreateInput)

    # Crear múltiples registros (batch)
    crear_miembros: list[MiembroType] = strawchemy.create(MiembroCreateInput)

    # Actualizar por ID
    actualizar_miembro: MiembroType = strawchemy.update_by_ids(MiembroUpdateInput)

    # Eliminar por filtro
    eliminar_miembros: list[MiembroType] = strawchemy.delete(MiembroFilter)
```

### Métodos de Mutation Disponibles

| Método | Descripción | Input Type |
|--------|-------------|------------|
| `strawchemy.create(input_type)` | Crear uno o varios | CreateInput |
| `strawchemy.update_by_ids(input_type)` | Actualizar por PK | UpdateByPKInput |
| `strawchemy.update(input_type, filter_type)` | Actualizar por filtro | UpdateByFilterInput + Filter |
| `strawchemy.delete(filter_type)` | Eliminar por filtro | Filter |
| `strawchemy.upsert(input, update_fields, conflict_fields)` | Insert o Update | CreateInput + Enums |

## Soporte para Relaciones Anidadas

Strawchemy soporta automáticamente mutations con relaciones anidadas:

```graphql
mutation {
  crearMiembro(data: {
    nombre: "Juan"
    apellido1: "García"
    # Relación anidada - crear dirección
    direccion: {
      create: {
        calle: "Gran Vía"
        numero: "123"
      }
    }
    # Relación anidada - asociar a agrupación existente
    agrupacion: {
      set: { id: "uuid-existente" }
    }
  }) {
    id
    nombre
    direccion {
      calle
    }
  }
}
```

### Operaciones en Relaciones

| Operación | Descripción |
|-----------|-------------|
| `create` | Crear nuevo registro relacionado |
| `set` | Asignar registro existente por ID |
| `add` | Añadir a relación many-to-many |
| `remove` | Quitar de relación many-to-many |
| `upsert` | Insert o Update en relación |

## Filtros Avanzados

Los filtros generados automáticamente soportan:

```graphql
query {
  miembros(filter: {
    _and: [
      { nombre: { _contains: "Juan" } }
      { activo: { _eq: true } }
    ]
    _or: [
      { email: { _like: "%@gmail.com" } }
      { email: { _like: "%@hotmail.com" } }
    ]
  }) {
    id
    nombre
  }
}
```

### Operadores de Filtro

| Operador              | Descripción              |
|-----------------------|--------------------------|
| `_eq`                 | Igual                    |
| `_neq`                | No igual                 |
| `_gt`, `_gte`         | Mayor que, Mayor o igual |
| `_lt`, `_lte`         | Menor que, Menor o igual |
| `_in`, `_nin`         | En lista, No en lista    |
| `_contains`           | Contiene substring       |
| `_like`, `_ilike`     | Pattern matching         |
| `_is_null`            | Es nulo                  |
| `_and`, `_or`, `_not` | Operadores lógicos       |

## Paginación y Ordenamiento

```graphql
query {
  miembros(
    limit: 10
    offset: 0
    orderBy: [{ nombre: ASC }, { fechaCreacion: DESC }]
  ) {
    id
    nombre
  }
}
```

## Errores Comunes y Soluciones

### Error: "Expected Iterable, but did not find one"

**Causa:** Usar lambda en `strawchemy.field()`

```python
# INCORRECTO
miembros: list[MiembroType] = strawchemy.field(lambda: Miembro)

# CORRECTO
miembros: list[MiembroType] = strawchemy.field()
```

### Error: "Input Object type must define one or more fields"

**Causa:** No especificar `include="all"` en los inputs

```python
# INCORRECTO
@strawchemy.input(Model, mode="create_input")
class ModelCreateInput:
    pass

# CORRECTO
@strawchemy.input(Model, mode="create_input", include="all")
class ModelCreateInput:
    pass
```

### Error: "missing required keyword-only argument: 'mode'"

**Causa:** No especificar el modo en `@strawchemy.input()`

```python
# INCORRECTO
@strawchemy.input(Model)
class ModelInput:
    pass

# CORRECTO
@strawchemy.input(Model, mode="create_input")
class ModelCreateInput:
    pass
```

## Campos de Auditoría

Los campos de auditoría deben **excluirse** de los inputs porque:

1. **`fecha_creacion`**: Tiene `server_default=func.now()`, se establece automáticamente
2. **`fecha_modificacion`**: Tiene `onupdate=func.now()`, se actualiza automáticamente
3. **`fecha_eliminacion`**: Se gestiona por el método `soft_delete()`
4. **`eliminado`**: Se gestiona por el método `soft_delete()`
5. **`creado_por_id`** / **`modificado_por_id`**: Deben establecerse desde el contexto de autenticación

```python
AUDIT_FIELDS = [
    "fecha_creacion",
    "fecha_modificacion",
    "fecha_eliminacion",
    "eliminado",
    "creado_por_id",
    "modificado_por_id",
]

@strawchemy.input(Model, mode="create_input", include="all", exclude=AUDIT_FIELDS)
class ModelCreateInput:
    pass
```

## Configuración de Dialecto PostgreSQL

Para funcionalidades específicas de PostgreSQL como `DISTINCT ON`:

```python
config = StrawchemyConfig(
    dialect="postgresql",  # Habilita features específicas
    repository_type=StrawchemyAsyncRepository,
)
```

## Referencias

- [Strawchemy GitHub](https://github.com/strawberry-graphql/strawchemy)
- [Strawberry GraphQL Docs](https://strawberry.rocks/)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/en/20/)
