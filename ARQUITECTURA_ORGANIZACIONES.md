# Arquitectura Unificada de Organizaciones

## Motivación

Anteriormente teníamos dos modelos muy similares:
- **`AgrupacionTerritorial`** (en `geografico/direccion.py`)
- **`Asociacion`** (en `colaboraciones/asociacion.py`)

Ambos compartían el 80% de sus campos (nombre, email, teléfono, web, dirección, provincia, activo, etc.), lo que generaba duplicación de código y lógica.

## Nueva Arquitectura: Modelo `Organizacion`

Ahora tenemos un **único modelo `Organizacion`** que unifica ambos conceptos mediante el campo `tipo_id` → `TipoOrganizacion`.

### Tabla: `tipos_organizacion`

Define los tipos de organizaciones con los siguientes campos clave:

| Campo | Descripción | Ejemplos |
|-------|-------------|----------|
| `codigo` | Código único | `AGRUP_ESTATAL`, `AGRUP_AUTONOMICA`, `ASOC_ONG`, `ASOC_SINDICAL` |
| `categoria` | INTERNA o EXTERNA | `INTERNA` (Europa Laica), `EXTERNA` (colaboradores) |
| `permite_jerarquia` | Si puede tener organizaciones hijas | `True` para agrupaciones territoriales |
| `permite_convenios` | Si puede tener convenios | `True` para asociaciones externas |

#### Tipos predefinidos:

**Organizaciones INTERNAS (Europa Laica):**
- `AGRUP_ESTATAL` - Agrupación Estatal
- `AGRUP_INTERNACIONAL` - Agrupación Internacional
- `AGRUP_AUTONOMICA` - Agrupación Autonómica
- `AGRUP_PROVINCIAL` - Agrupación Provincial
- `AGRUP_LOCAL` - Agrupación Local

**Organizaciones EXTERNAS (Colaboradoras):**
- `ASOC_ONG` - ONG
- `ASOC_CULTURAL` - Asociación Cultural
- `ASOC_DEPORTIVA` - Asociación Deportiva
- `ASOC_VECINAL` - Asociación Vecinal
- `ASOC_SINDICAL` - Sindicato
- `ASOC_EMPRESARIAL` - Organización Empresarial
- `ASOC_EDUCATIVA` - Asociación Educativa
- `ASOC_OTRO` - Otra asociación

### Tabla: `organizaciones`

Modelo unificado con todos los campos:

#### Campos comunes (para todas):
- `tipo_id` → `TipoOrganizacion`
- `codigo` (opcional)
- `nombre`, `nombre_corto`, `siglas`
- `cif_nif`
- `pais_id`, `provincia_id`, `municipio_id`, `direccion_id`
- `email`, `telefono`, `telefono_movil`, `web`
- `descripcion`, `observaciones`
- `activo`, `fecha_alta`, `fecha_baja`

#### Campos específicos de agrupaciones territoriales (INTERNAS):
- `organizacion_padre_id` - Jerarquía de agrupaciones
- `nivel` - Nivel en la jerarquía (1=Local, 2=Provincial, 3=Autonómica, 4=Estatal)
- `ambito` - LOCAL, PROVINCIAL, AUTONOMICA, ESTATAL, INTERNACIONAL

#### Campos específicos de asociaciones externas (EXTERNAS):
- `persona_contacto_nombre`, `persona_contacto_cargo`
- `persona_contacto_email`, `persona_contacto_telefono`
- `numero_socios`
- `valoracion` (1-5 estrellas)
- `registro_oficial`, `numero_registro`, `fecha_constitucion`
- Relación → `convenios`

## Ventajas de la Unificación

1. **DRY (Don't Repeat Yourself)**: Un solo modelo para mantener
2. **Flexibilidad**: Fácil añadir nuevos tipos de organizaciones
3. **Consultas unificadas**: Buscar "todas las organizaciones de Andalucía" (internas y externas)
4. **Reutilización de código**: Servicios, resolvers, schemas compartidos
5. **Relaciones simplificadas**: Otras entidades pueden referenciar `organizacion_id` sin importar el tipo

## Migración desde Modelos Antiguos

### Paso 1: Crear tabla nueva
```sql
-- Ya existe la migración en alembic/versions/
CREATE TABLE tipos_organizacion (...);
CREATE TABLE organizaciones (...);
```

### Paso 2: Poblar tipos
```python
# Script: scripts/inicializar_tipos_organizacion.py
tipos = [
    TipoOrganizacion(
        codigo='AGRUP_ESTATAL',
        nombre='Agrupación Estatal',
        categoria='INTERNA',
        permite_jerarquia=True,
        permite_convenios=False
    ),
    # ... resto de tipos
]
```

### Paso 3: Migrar datos
```python
# Script: scripts/migrar_a_organizaciones.py

# Migrar agrupaciones_territoriales -> organizaciones
for agrup in agrupaciones_territoriales:
    org = Organizacion(
        tipo_id=tipos['AGRUP_' + agrup.tipo].id,  # AGRUP_PROVINCIAL, etc.
        codigo=agrup.codigo,
        nombre=agrup.nombre,
        # ... copiar campos comunes
        organizacion_padre_id=agrup.agrupacion_padre_id,
        ambito=agrup.tipo
    )

# Migrar asociaciones -> organizaciones
for asoc in asociaciones:
    org = Organizacion(
        tipo_id=tipos[asoc.tipo.codigo].id,  # ASOC_ONG, etc.
        nombre=asoc.nombre,
        # ... copiar campos comunes
        persona_contacto_nombre=asoc.persona_contacto_nombre,
        # ... campos específicos de asociaciones
    )
```

### Paso 4: Actualizar referencias
```sql
-- Actualizar FK en otras tablas
UPDATE miembros SET organizacion_id = (
    SELECT new_id FROM temp_mapping WHERE old_agrupacion_id = miembros.agrupacion_id
);

UPDATE campanias SET organizacion_id = (
    SELECT new_id FROM temp_mapping WHERE old_agrupacion_id = campanias.agrupacion_id
);
```

### Paso 5: Deprecar tablas antiguas
```sql
-- Mantener temporalmente por compatibilidad
-- RENAME TABLE agrupaciones_territoriales TO agrupaciones_territoriales_old;
-- RENAME TABLE asociaciones TO asociaciones_old;
```

## Queries Comunes

### Obtener todas las agrupaciones territoriales de Andalucía
```python
from sqlalchemy import select
from app.domains.organizaciones.models import Organizacion, TipoOrganizacion

result = await session.execute(
    select(Organizacion)
    .join(TipoOrganizacion)
    .where(
        TipoOrganizacion.categoria == 'INTERNA',
        Organizacion.provincia_id == provincia_andalucia_id
    )
)
agrupaciones = result.scalars().all()
```

### Obtener agrupación estatal (Europa Laica)
```python
result = await session.execute(
    select(Organizacion)
    .join(TipoOrganizacion)
    .where(
        TipoOrganizacion.codigo == 'AGRUP_ESTATAL',
        Organizacion.activo == True
    )
)
europa_laica = result.scalar_one()
```

### Obtener todas las ONGs con convenios vigentes
```python
result = await session.execute(
    select(Organizacion)
    .join(TipoOrganizacion)
    .where(
        TipoOrganizacion.codigo == 'ASOC_ONG',
        Organizacion.activo == True
    )
)
ongs = result.scalars().all()
ongs_con_convenio = [ong for ong in ongs if ong.tiene_convenio_vigente]
```

### Obtener jerarquía completa de agrupaciones
```python
# Obtener agrupación provincial y sus hijos
agrupacion = await session.get(Organizacion, id)

# Hijos (agrupaciones locales)
locales = agrupacion.organizaciones_hijas

# Padre (agrupación autonómica)
autonomica = agrupacion.organizacion_padre

# Abuelo (agrupación estatal)
estatal = autonomica.organizacion_padre if autonomica else None
```

## GraphQL Schema

```graphql
type TipoOrganizacion {
  id: UUID!
  codigo: String!
  nombre: String!
  categoria: CategoriaOrganizacion!  # INTERNA, EXTERNA
  permiteJerarquia: Boolean!
  permiteConvenios: Boolean!
}

enum CategoriaOrganizacion {
  INTERNA
  EXTERNA
}

type Organizacion {
  id: UUID!
  tipo: TipoOrganizacion!
  codigo: String
  nombre: String!
  nombreCorto: String
  siglas: String

  # Ubicación
  pais: Pais!
  provincia: Provincia
  municipio: Municipio
  direccion: Direccion

  # Contacto
  email: String
  telefono: String
  web: String

  # Jerarquía (solo agrupaciones territoriales)
  organizacionPadre: Organizacion
  organizacionesHijas: [Organizacion!]!
  nivel: Int!
  ambito: String!

  # Asociaciones externas
  personaContactoNombre: String
  numeroSocios: Int
  convenios: [Convenio!]!
  tieneConvenioVigente: Boolean!

  # Estado
  activo: Boolean!
  fechaAlta: Date!
}

type Query {
  # Obtener todas las organizaciones
  organizaciones(
    categoria: CategoriaOrganizacion
    ambito: String
    provinciaId: UUID
    activo: Boolean
  ): [Organizacion!]!

  # Obtener agrupación estatal
  agrupacionEstatal: Organizacion

  # Obtener jerarquía de agrupaciones
  agrupacionesJerarquia(raizId: UUID): [Organizacion!]!

  # Obtener asociaciones con convenios vigentes
  asociacionesConConveniosVigentes: [Organizacion!]!
}
```

## Migración de Código Existente

### Antes (modelo antiguo):
```python
from app.domains.geografico.models.direccion import AgrupacionTerritorial

agrupacion = await session.get(AgrupacionTerritorial, id)
print(agrupacion.nombre)
```

### Después (modelo unificado):
```python
from app.domains.organizaciones.models import Organizacion

organizacion = await session.get(Organizacion, id)
if organizacion.es_agrupacion_territorial:
    print(f"Agrupación: {organizacion.nombre}")
    print(f"Nivel: {organizacion.nivel}")
```

## Siguiente Pasos

1. ✅ Crear modelos en `domains/organizaciones/`
2. ⏳ Crear migración Alembic para nuevas tablas
3. ⏳ Crear script `inicializar_tipos_organizacion.py`
4. ⏳ Crear script `migrar_a_organizaciones.py` para datos existentes
5. ⏳ Actualizar imports y resolvers GraphQL
6. ⏳ Actualizar schemas Strawberry
7. ⏳ Deprecar modelos antiguos
