# Arquitectura de Mixins Reutilizables

## Motivación

En el sistema existen múltiples entidades que comparten datos de contacto:
- **Organizaciones** (agrupaciones territoriales, asociaciones)
- **Miembros** (afiliados, simpatizantes)
- **Voluntarios**
- **Proveedores** (posible futuro)
- **Ponentes/Conferenciantes** (posible futuro)

Duplicar estos campos en cada modelo genera:
- Código repetido (violación del principio DRY)
- Dificultad para mantener consistencia
- Más trabajo al añadir nuevos campos de contacto

## Solución: `ContactoMixin`

Creamos un mixin reutilizable que proporciona todos los campos de contacto estándar.

### Ubicación

```
backend/app/infrastructure/mixins/
├── __init__.py
└── contacto_mixin.py
```

## Mixins Disponibles

### 1. `ContactoMixin`

**Propósito**: Campos básicos de contacto y ubicación geográfica.

**Campos incluidos**:
```python
# Ubicación geográfica
pais_id: uuid.UUID (FK → paises.id)
provincia_id: Optional[uuid.UUID] (FK → provincias.id)
municipio_id: Optional[uuid.UUID] (FK → municipios.id)
direccion_id: Optional[uuid.UUID] (FK → direcciones.id)

# Datos de contacto
email: Optional[str]
telefono_fijo: Optional[str]
telefono_movil: Optional[str]
web: Optional[str]
```

**Propiedades útiles**:
- `telefono_principal` → Devuelve móvil preferente, sino fijo
- `tiene_telefono` → Verifica si tiene al menos un teléfono
- `email_valido` → Validación básica de formato email

**Uso**:
```python
from app.infrastructure.mixins import ContactoMixin
from app.infrastructure.base_model import BaseModel

class Miembro(BaseModel, ContactoMixin):
    __tablename__ = 'miembros'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))

    # Los campos de ContactoMixin están disponibles automáticamente
    # No necesitas declararlos aquí

    # Relaciones (deben definirse explícitamente)
    pais = relationship('Pais', lazy='selectin')
    provincia = relationship('Provincia', lazy='selectin')
    municipio = relationship('Municipio', lazy='selectin')
    direccion = relationship('Direccion', lazy='selectin')
```

### 2. `ContactoCompletoMixin`

**Propósito**: Extiende `ContactoMixin` añadiendo datos de persona de contacto.

**Campos adicionales**:
```python
# Hereda todos los campos de ContactoMixin, más:
persona_contacto_nombre: Optional[str]
persona_contacto_cargo: Optional[str]
persona_contacto_email: Optional[str]
persona_contacto_telefono: Optional[str]
```

**Propiedades útiles**:
- `tiene_persona_contacto` → Verifica si hay datos de contacto

**Uso**:
```python
from app.infrastructure.mixins import ContactoCompletoMixin
from app.infrastructure.base_model import BaseModel

class Organizacion(BaseModel, ContactoCompletoMixin):
    __tablename__ = 'organizaciones'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200))

    # Tiene todos los campos de ContactoMixin + persona_contacto_*

    # Relaciones
    pais = relationship('Pais', lazy='selectin')
    provincia = relationship('Provincia', lazy='selectin')
    municipio = relationship('Municipio', lazy='selectin')
    direccion = relationship('Direccion', lazy='selectin')
```

## Modelos que Usan los Mixins

### Organizacion (usa `ContactoCompletoMixin`)

```python
class Organizacion(BaseModel, ContactoCompletoMixin):
    """
    Unifica agrupaciones territoriales y asociaciones externas.
    """
    __tablename__ = 'organizaciones'

    # Campos propios
    tipo_id: Mapped[uuid.UUID]  # FK → tipos_organizacion
    codigo: Mapped[Optional[str]]
    nombre: Mapped[str]
    cif_nif: Mapped[Optional[str]]

    # Jerarquía (agrupaciones)
    organizacion_padre_id: Mapped[Optional[uuid.UUID]]
    nivel: Mapped[int]
    ambito: Mapped[str]  # LOCAL, PROVINCIAL, AUTONOMICA, ESTATAL

    # Campos de ContactoCompletoMixin (heredados):
    # - pais_id, provincia_id, municipio_id, direccion_id
    # - email, telefono_fijo, telefono_movil, web
    # - persona_contacto_nombre, persona_contacto_cargo
    # - persona_contacto_email, persona_contacto_telefono

    # Información adicional
    descripcion: Mapped[Optional[str]]
    numero_socios: Mapped[Optional[int]]
    activo: Mapped[bool]
```

### Miembro (debería usar `ContactoMixin`)

```python
from app.infrastructure.mixins import ContactoMixin

class Miembro(BaseModel, ContactoMixin):
    """Miembros de la organización (afiliados, simpatizantes)."""
    __tablename__ = 'miembros'

    # Campos propios
    numero_miembro: Mapped[str]
    nombre: Mapped[str]
    apellidos: Mapped[str]
    dni: Mapped[Optional[str]]  # Encriptado
    fecha_nacimiento: Mapped[Optional[date]]

    # Campos de ContactoMixin (heredados):
    # - pais_id, provincia_id, municipio_id, direccion_id
    # - email, telefono_fijo, telefono_movil, web

    # Estado
    tipo_miembro_id: Mapped[uuid.UUID]
    estado_miembro_id: Mapped[uuid.UUID]
    fecha_alta: Mapped[date]
    activo: Mapped[bool]
```

### Voluntario (debería usar `ContactoMixin`)

```python
from app.infrastructure.mixins import ContactoMixin

class Voluntario(BaseModel, ContactoMixin):
    """Voluntarios de la organización."""
    __tablename__ = 'voluntarios'

    # Campos propios
    nombre: Mapped[str]
    apellidos: Mapped[str]
    dni: Mapped[Optional[str]]

    # Campos de ContactoMixin (heredados):
    # - pais_id, provincia_id, municipio_id, direccion_id
    # - email, telefono_fijo, telefono_movil, web

    # Disponibilidad
    disponibilidad: Mapped[str]
    habilidades: Mapped[Optional[str]]
    activo: Mapped[bool]
```

## Ventajas del Uso de Mixins

### 1. DRY (Don't Repeat Yourself)
```python
# Antes (código duplicado en cada modelo):
class Miembro(BaseModel):
    email: Mapped[Optional[str]] = mapped_column(String(255))
    telefono_fijo: Mapped[Optional[str]] = mapped_column(String(20))
    telefono_movil: Mapped[Optional[str]] = mapped_column(String(20))
    # ... repetido en Organizacion, Voluntario, etc.

# Después (código centralizado):
class Miembro(BaseModel, ContactoMixin):
    pass  # Los campos se heredan automáticamente
```

### 2. Mantenimiento Centralizado
Si necesitas añadir un nuevo campo de contacto (ej: `telefono_secundario`), solo lo añades una vez en el mixin y todos los modelos lo heredan.

### 3. Consistencia Garantizada
Todos los modelos tendrán exactamente los mismos campos de contacto con los mismos tipos y validaciones.

### 4. Propiedades Reutilizables
```python
# Disponible en todos los modelos que usan ContactoMixin
miembro.telefono_principal  # Devuelve móvil o fijo
organizacion.tiene_telefono  # True/False
voluntario.email_valido  # Validación básica
```

### 5. Queries Uniformes
```python
# Buscar por email funciona igual en todos los modelos
miembros = await session.execute(
    select(Miembro).where(Miembro.email == 'ejemplo@email.com')
)

organizaciones = await session.execute(
    select(Organizacion).where(Organizacion.email == 'ejemplo@email.com')
)
```

## Relaciones en Modelos con Mixins

**Importante**: Las relaciones deben definirse explícitamente en cada modelo, aunque los campos FK vengan del mixin.

```python
class Miembro(BaseModel, ContactoMixin):
    __tablename__ = 'miembros'

    # ... campos propios

    # IMPORTANTE: Definir relaciones explícitamente
    pais = relationship('Pais', lazy='selectin')
    provincia = relationship('Provincia', lazy='selectin')
    municipio = relationship('Municipio', lazy='selectin')
    direccion = relationship('Direccion', lazy='selectin')
```

**¿Por qué?**: SQLAlchemy necesita saber el nombre de la tabla origen para configurar correctamente el JOIN. Los mixins proporcionan los campos FK pero no pueden inferir el nombre de la tabla automáticamente.

## Migración de Modelos Existentes

### Paso 1: Importar el mixin
```python
from app.infrastructure.mixins import ContactoMixin  # o ContactoCompletoMixin
```

### Paso 2: Añadir a herencia
```python
# Antes:
class Miembro(BaseModel):
    __tablename__ = 'miembros'

# Después:
class Miembro(BaseModel, ContactoMixin):
    __tablename__ = 'miembros'
```

### Paso 3: Eliminar campos duplicados
Borrar las declaraciones de campos que ya vienen del mixin:
- `email`
- `telefono_fijo` / `telefono`
- `telefono_movil`
- `web`
- `pais_id`, `provincia_id`, `municipio_id`, `direccion_id`

### Paso 4: Mantener relaciones
Conservar las definiciones de `relationship()`:
```python
pais = relationship('Pais', lazy='selectin')
provincia = relationship('Provincia', lazy='selectin')
# etc.
```

### Paso 5: Actualizar referencias
Si el modelo usaba `telefono` en lugar de `telefono_fijo`:
```python
# Código antiguo:
miembro.telefono

# Código nuevo (usar propiedad):
miembro.telefono_principal  # Devuelve móvil o fijo
```

## Ejemplo Completo: Antes y Después

### Antes (sin mixin)

```python
class Miembro(BaseModel):
    __tablename__ = 'miembros'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))

    # Contacto (duplicado en cada modelo)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    telefono: Mapped[Optional[str]] = mapped_column(String(20))
    web: Mapped[Optional[str]] = mapped_column(String(255))

    # Ubicación (duplicado en cada modelo)
    pais_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('paises.id'))
    provincia_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('provincias.id'))

    pais = relationship('Pais')
    provincia = relationship('Provincia')

class Organizacion(BaseModel):
    __tablename__ = 'organizaciones'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200))

    # DUPLICADO del modelo Miembro
    email: Mapped[Optional[str]] = mapped_column(String(255))
    telefono: Mapped[Optional[str]] = mapped_column(String(20))
    web: Mapped[Optional[str]] = mapped_column(String(255))
    pais_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('paises.id'))
    provincia_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('provincias.id'))

    pais = relationship('Pais')
    provincia = relationship('Provincia')
```

### Después (con mixin)

```python
from app.infrastructure.mixins import ContactoMixin, ContactoCompletoMixin

class Miembro(BaseModel, ContactoMixin):
    __tablename__ = 'miembros'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))

    # Campos de contacto heredados de ContactoMixin:
    # - email, telefono_fijo, telefono_movil, web
    # - pais_id, provincia_id, municipio_id, direccion_id

    # Relaciones (deben mantenerse)
    pais = relationship('Pais', lazy='selectin')
    provincia = relationship('Provincia', lazy='selectin')
    municipio = relationship('Municipio', lazy='selectin')
    direccion = relationship('Direccion', lazy='selectin')

class Organizacion(BaseModel, ContactoCompletoMixin):
    __tablename__ = 'organizaciones'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200))

    # Campos de contacto heredados de ContactoCompletoMixin:
    # - email, telefono_fijo, telefono_movil, web
    # - pais_id, provincia_id, municipio_id, direccion_id
    # - persona_contacto_nombre, persona_contacto_cargo, etc.

    # Relaciones (deben mantenerse)
    pais = relationship('Pais', lazy='selectin')
    provincia = relationship('Provincia', lazy='selectin')
    municipio = relationship('Municipio', lazy='selectin')
    direccion = relationship('Direccion', lazy='selectin')
```

**Resultado**: 40+ líneas de código eliminadas, sin pérdida de funcionalidad.

## Próximos Pasos

1. ✅ Crear `ContactoMixin` y `ContactoCompletoMixin`
2. ✅ Aplicar a modelo `Organizacion`
3. ⏳ Aplicar a modelo `Miembro`
4. ⏳ Aplicar a modelo `Voluntario`
5. ⏳ Actualizar referencias a `telefono` → `telefono_principal`
6. ⏳ Crear tests unitarios para propiedades del mixin
