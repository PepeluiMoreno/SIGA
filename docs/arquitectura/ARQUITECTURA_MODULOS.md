# Arquitectura de módulos en SIGA

## Principio fundamental

Cada módulo de SIGA es una unidad funcional autocontenida que implementa un subdominio de la gestión asociativa. Todos los módulos comparten la misma estructura interna y se comunican hacia el exterior exclusivamente a través de la capa GraphQL.

---

## Estructura de un módulo

```
app/modules/<nombre>/
├── __init__.py
├── models/
│   ├── __init__.py
│   └── <entidad>.py          # Modelos SQLAlchemy
└── services/
    ├── __init__.py            # Exporta los servicios públicos
    └── <nombre>_service.py   # Lógica de negocio
```

La capa GraphQL vive fuera de los módulos, en `app/graphql/`:

```
app/graphql/
├── <nombre>_resolvers.py     # Thin wrappers GraphQL
├── permissions.py            # RBAC — RequireTransaction factory
├── context.py                # Context con check_permission(), get_role_ids()
├── types_auto.py             # Tipos GraphQL generados por strawchemy
└── inputs_auto.py            # Inputs GraphQL generados por strawchemy
```

---

## Las tres capas de un módulo

### 1. Modelos (`models/`)

Clases SQLAlchemy 2.0 async que mapean la base de datos. Definen:

- Tablas y columnas con tipos Python nativos
- Relaciones entre entidades (`relationship()`)
- Propiedades calculadas simples (sin acceso a BD)
- Constraints de integridad referencial

Los modelos **no contienen lógica de negocio**. Son representaciones puras del estado persistido.

```python
class Miembro(Base):
    __tablename__ = "miembros"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str]
    email: Mapped[str | None]
    eliminado: Mapped[bool] = mapped_column(default=False)
    # ...
```

### 2. Servicio (`services/<nombre>_service.py`)

Clase Python que recibe una `AsyncSession` en el constructor y concentra **toda la lógica de negocio** del módulo:

- Validaciones de dominio (reglas que van más allá de un NOT NULL)
- Orquestación de operaciones sobre varios modelos
- Cálculos y transformaciones de datos
- Gestión del ciclo de vida de las entidades
- Operaciones complejas (clonación, exportación, generación de PDFs, envío de emails)

El servicio **no conoce GraphQL, JWT ni HTTP**. Es agnóstico del transporte.

```python
class MembresiaService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def crear(self, *, nombre: str, email: str, ...) -> Miembro:
        # Validaciones de dominio
        # Persistencia
        # Devuelve el modelo

    async def anonimizar(self, miembro_id: uuid.UUID) -> Miembro:
        # Lógica RGPD — borrado de campos PII
        ...
```

**Convenciones internas de los servicios:**

- Métodos `async` que reciben tipos Python nativos (no tipos Strawberry)
- Constantes de módulo para datos reutilizables (`_CAMPOS_PII`, `_MIEMBRO_FIELDS`)
- Helpers privados con prefijo `_` para operaciones internas
- Importaciones locales dentro del método para evitar ciclos de dependencia entre módulos
- El servicio puede instanciar servicios de otros módulos internamente cuando lo necesita (con import local para evitar ciclos)

### 3. Resolver GraphQL (`graphql/<nombre>_resolvers.py`)

Clase Strawberry que actúa como **thin wrapper** entre la API GraphQL y el servicio. Cada método:

1. Extrae parámetros del input GraphQL
2. Instancia el servicio con `info.context.session`
3. Delega la operación al servicio
4. Devuelve el resultado

```python
@strawberry.type
class MembresiaResolverMutation:

    @strawberry.mutation(permission_classes=[RequireTransaction("MBR_CREATE")])
    async def crear_miembro(self, info: strawberry.Info, data: MiembroCreateInput) -> MiembroType:
        return await MembresiaService(info.context.session).crear(
            nombre=data.nombre,
            email=data.email,
            # ...
        )
```

El resolver **nunca contiene** SQL directo, lógica condicional de dominio ni operaciones de BD. Si un método del resolver tiene más de 8-10 líneas de lógica, esa lógica pertenece al servicio.

---

## RBAC — Control de acceso

El sistema de permisos opera en dos niveles, ambos en la capa GraphQL:

**Nivel decorador** — `permission_classes=[RequireTransaction("CODIGO")]`

Se evalúa antes de ejecutar el cuerpo del método. Si el usuario no tiene el permiso, Strawberry lanza `PermissionError` y el método nunca llega a ejecutarse. El servicio no sabe que el permiso falló.

```python
@strawberry.mutation(permission_classes=[RequireTransaction("MBR_EDIT")])
async def actualizar_miembro(self, info, data): ...
```

**Nivel condicional** — `await info.context.check_permission("CODIGO")`

Para permisos que dependen del estado de los datos (no solo del rol). Se evalúa dentro del cuerpo del resolver, antes de llamar al servicio.

```python
async def guardar_parametros(self, info, data):
    if ya_inicializado:
        if not await info.context.check_permission("CFG_EDIT"):
            raise PermissionError(...)
    return await ConfiguracionService(info.context.session).guardar_parametros(
        data, ya_inicializado=ya_inicializado
    )
```

**Los servicios nunca comprueban permisos.** Son agnósticos del contexto de ejecución.

La matriz de permisos (`PermissionMatrixCache`) vive en memoria y se construye al arrancar a partir del catálogo de roles y transacciones en BD. Cada `RequireTransaction("X")` consulta esta matriz con los `role_ids` del JWT del usuario.

---

## Comunicación entre módulos

Cuando un servicio necesita funcionalidad de otro módulo, lo importa localmente dentro del método para evitar ciclos de importación en el arranque:

```python
async def crear_con_acceso(self, ...) -> Miembro:
    # Import local para evitar ciclo membresia ↔ acceso
    from app.modules.acceso.services.acceso_service import AccesoService
    acceso_svc = AccesoService(self.session)
    usuario = await acceso_svc.crear_usuario(...)
    # ...
```

La sesión de BD se comparte — todas las operaciones de un request HTTP ocurren dentro de la misma transacción.

---

## Módulos del sistema

| Módulo | Servicio(s) | Responsabilidad |
|---|---|---|
| `acceso` | `AccesoService`, `PermissionMatrixCache` | Autenticación, roles, matriz de permisos |
| `core` | — | Modelos compartidos (geografía, comunicación) |
| `configuracion` | `ConfiguracionService` | Parámetros de la organización, feature flags |
| `membresia` | `MembresiaService` | Ciclo de vida de socios, RGPD |
| `actividades` | `ActividadService`, `CampaniaService` | Actividades, tareas, participaciones, campañas |
| `economico` | `TesoreriaService`, `ContabilidadService`, `RemesaService`, `ReciboService`, `CuotaService`, `DonacionService`, `JustificanteGastoService` | Toda la operativa financiera |
| `secretaria` | `ReunionService`, `ActaService`, `LibroSociosService`, `ConvenioService` | Órganos de gobierno, actas, convenios |
| `organizaciones` | — | Estructura organizativa |

---

## Regla de oro

> Si un resolver necesita importar `select`, `update` o cualquier construcción de SQLAlchemy, el código está en el lugar equivocado.
