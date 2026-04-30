# Arquitectura del Sistema SIGA

## 📋 Tabla de Contenidos

- [Introducción](#introducción)
- [Estructura de Dominios (DDD)](#estructura-de-dominios-ddd)
- [Infraestructura](#infraestructura)
- [Modelos de Datos](#modelos-de-datos)
- [Servicios](#servicios)
- [Scripts de Inicialización](#scripts-de-inicialización)
- [Patrones y Convenciones](#patrones-y-convenciones)

## Introducción

SIGA utiliza una arquitectura basada en **Domain-Driven Design (DDD)** con SQLAlchemy 2.0+ async, UUID como identificadores primarios, y auditoría completa en todos los modelos.

### Tecnologías Principales

- **FastAPI**: Framework web asíncrono
- **SQLAlchemy 2.0+**: ORM con soporte async/await
- **Strawberry GraphQL**: API GraphQL
- **PostgreSQL**: Base de datos principal
- **Redis**: Cache (opcional, con fallback en memoria)
- **Alembic**: Migraciones de base de datos

## Estructura de Dominios (DDD)

El proyecto está organizado por dominios de negocio:

```
backend/app/
├── infrastructure/          # Capa de infraestructura
│   ├── base_model.py       # BaseModel con auditoría
│   └── services/           # Servicios de infraestructura
├── domains/                # Dominios de negocio
│   ├── core/              # Dominio core (configuración, estados, seguridad)
│   ├── geografico/        # Datos geográficos
│   ├── notificaciones/    # Sistema de notificaciones
│   ├── financiero/        # Cuotas, donaciones, remesas
│   ├── miembros/          # Gestión de miembros
│   ├── campanas/          # Campañas de comunicación
│   ├── grupos/            # Grupos de trabajo
│   ├── voluntariado/      # Gestión de voluntariado
│   └── actividades/       # Actividades y propuestas
├── models/                # Modelos legacy (en migración)
└── scripts/               # Scripts de inicialización
```

## Infraestructura

### BaseModel

Todos los modelos heredan de `BaseModel` que proporciona:

```python
class BaseModel(Base, AuditoriaMixin):
    """
    Campos automáticos:
    - id: UUID (primary key)
    - fecha_creacion: DateTime
    - fecha_modificacion: DateTime (auto-update)
    - fecha_eliminacion: DateTime (soft delete)
    - eliminado: Boolean (soft delete flag)
    - creado_por_id: UUID (FK a usuarios)
    - modificado_por_id: UUID (FK a usuarios)
    """
```

**Características:**
- ✅ Auditoría completa (quién y cuándo)
- ✅ Soft delete (eliminación lógica)
- ✅ UUID como primary key
- ✅ Type hints con `Mapped[]`
- ✅ Async/await en todas las operaciones

### Servicios de Infraestructura

#### 1. EncriptacionService
**Ubicación:** `infrastructure/services/encriptacion_service.py`

Encriptación de datos sensibles usando Fernet (cryptography).

```python
from app.infrastructure.services import get_encriptacion_service

service = get_encriptacion_service()

# Encriptar IBAN
iban_encriptado = service.encriptar_iban("ES12 1234 5678 9012 3456 7890")

# Desencriptar
iban = service.desencriptar_iban(iban_encriptado)

# Encriptar datos genéricos
datos_encriptados = service.encriptar_json({"dni": "12345678A"})
```

**Casos de uso:**
- Encriptar IBAN de miembros
- Encriptar DNI
- Encriptar datos sensibles en JSON

#### 2. CacheService
**Ubicación:** `infrastructure/services/cache_service.py`

Sistema de cache con Redis + fallback en memoria.

```python
from app.infrastructure.services import get_cache_service, generar_cache_key

cache = get_cache_service()

# Guardar en cache (TTL en segundos)
cache.set("clave", valor, ttl=300)

# Obtener del cache
valor = cache.get("clave", default=None)

# Generar claves de cache
key = generar_cache_key("usuarios", usuario_id, "perfil")
```

**Características:**
- Fallback automático a memoria si Redis no está disponible
- TTL configurable
- Funciones helper para generar claves

#### 3. ConfiguracionService
**Ubicación:** `infrastructure/services/configuracion_service.py`

Gestión de configuración dinámica desde base de datos.

```python
from app.infrastructure.services import ConfiguracionService

async def ejemplo(session: AsyncSession):
    config = ConfiguracionService(session)

    # Obtener valores con tipo específico
    cuota_default = await config.get_float('CUOTA_IMPORTE_DEFAULT')
    max_intentos = await config.get_int('MAX_INTENTOS_LOGIN')
    notif_activas = await config.get_bool('NOTIFICACIONES_ACTIVAS')

    # Actualizar configuración
    await config.set('CUOTA_IMPORTE_DEFAULT', '55.0', usuario_id)
```

**Configuraciones disponibles:**
- `CUOTA_IMPORTE_DEFAULT`: Importe por defecto de cuotas
- `MAX_INTENTOS_LOGIN`: Máximo intentos de login
- `TIEMPO_BLOQUEO_MINUTOS`: Tiempo de bloqueo tras intentos fallidos
- `CONTRASENA_LONGITUD_MINIMA`: Longitud mínima de contraseña
- `NOTIFICACIONES_ACTIVAS`: Activar/desactivar notificaciones
- Y más...

#### 4. SeguridadService
**Ubicación:** `infrastructure/services/seguridad_service.py`

Gestión de seguridad: autenticación, brute-force protection, validación de contraseñas.

```python
from app.infrastructure.services import SeguridadService

async def ejemplo(session: AsyncSession):
    seguridad = SeguridadService(session)

    # Registrar intento de login
    await seguridad.registrar_intento_login(
        identificador="user@example.com",
        ip_address="192.168.1.1",
        exitoso=True,
        usuario_id=usuario.id
    )

    # Validar contraseña
    resultado = await seguridad.validar_fortaleza_contrasena("MiPassword123!")
    # resultado = {valida: bool, fortaleza: str, puntuacion: int, errores: list}

    # Verificar si IP está bloqueada
    bloqueada = await seguridad.verificar_ip_bloqueada("192.168.1.1")
```

**Características:**
- Protección contra brute-force
- Validación de fortaleza de contraseñas
- Bloqueo temporal/permanente de IPs
- Tracking de sesiones
- Auditoría de eventos de seguridad

#### 5. AuditoriaService
**Ubicación:** `infrastructure/services/auditoria_service.py`

Helpers para auditoría y soft delete.

```python
from app.infrastructure.services import AuditoriaService

async def ejemplo(session: AsyncSession):
    auditoria = AuditoriaService(session)

    # Soft delete
    await auditoria.soft_delete(entidad, usuario_id)

    # Obtener solo registros activos
    activos = await auditoria.get_active_query(Miembro, agrupacion_id=agrup_id)

    # Restaurar registro eliminado
    await auditoria.restore(entidad, usuario_id)
```

#### 6. EstadoService
**Ubicación:** `infrastructure/services/estado_service.py`

Gestión genérica de estados con historial.

```python
from app.infrastructure.services import EstadoService

async def ejemplo(session: AsyncSession):
    estado_svc = EstadoService(session)

    # Cambiar estado de cuota
    await estado_svc.cambiar_estado(
        entidad=cuota,
        nuevo_estado_codigo='COBRADA',
        usuario_id=usuario.id,
        motivo='Pago recibido vía transferencia'
    )

    # Obtener historial de cambios
    historial = await estado_svc.obtener_historial(
        entidad_tipo='cuotaanual',
        entidad_id=str(cuota.id)
    )
```

**Entidades con estados:**
- CuotaAnual → EstadoCuota (PENDIENTE, COBRADA, IMPAGADA, ANULADA, EXENTA)
- Campania → EstadoCampania (BORRADOR, PROGRAMADA, EN_CURSO, FINALIZADA, CANCELADA)
- Tarea → EstadoTarea (PENDIENTE, EN_PROGRESO, COMPLETADA, CANCELADA)
- OrdenCobro → EstadoOrdenCobro (PENDIENTE, PROCESADA, FALLIDA, ANULADA)
- Remesa → EstadoRemesa (BORRADOR, GENERADA, ENVIADA, PROCESADA, RECHAZADA)
- Donacion → EstadoDonacion (PENDIENTE, RECIBIDA, CERTIFICADA, ANULADA)

#### 7. NotificacionService
**Ubicación:** `infrastructure/services/notificacion_service.py`

Sistema completo de notificaciones multicanal.

```python
from app.infrastructure.services import NotificacionService

async def ejemplo(session: AsyncSession):
    notif = NotificacionService(session)

    # Crear notificación
    await notif.crear_notificacion(
        tipo_codigo='CUOTA_COBRADA',
        usuario_id=usuario.id,
        titulo='Cuota Cobrada',
        mensaje='Tu cuota de 50€ ha sido cobrada correctamente.',
        canal='EMAIL',
        url_accion='/finanzas/cuotas'
    )

    # Obtener notificaciones no leídas
    no_leidas = await notif.obtener_notificaciones_usuario(
        usuario_id=usuario.id,
        solo_no_leidas=True
    )

    # Contar no leídas (con cache)
    count = await notif.contar_no_leidas(usuario.id)

    # Marcar como leída
    await notif.marcar_como_leida(notificacion.id, usuario.id)

    # Envío batch
    await notif.enviar_notificacion_batch(
        tipo_codigo='INVITACION_EVENTO',
        usuarios_ids=[user1.id, user2.id, user3.id],
        titulo='Invitación a Evento',
        mensaje='Estás invitado al evento...'
    )
```

**Canales disponibles:**
- EMAIL: Notificación por email
- SMS: Notificación por SMS
- PUSH: Push notification
- INAPP: Notificación in-app

**Tipos de notificación predefinidos:**
- Sistema: BIENVENIDA, CAMBIO_CONTRASENA, LOGIN_SOSPECHOSO
- Financiero: CUOTA_COBRADA, CUOTA_IMPAGADA, DONACION_RECIBIDA, CERTIFICADO_DONACION
- Campaña: CAMPANA_INICIADA, INVITACION_EVENTO
- Tarea: TAREA_ASIGNADA, TAREA_VENCIMIENTO
- Miembro: NUEVO_MIEMBRO, DATOS_ACTUALIZADOS

## Modelos de Datos

### Dominio Core

#### Configuracion
```python
from app.domains.core.models import Configuracion

config = Configuracion(
    clave='MI_CONFIG',
    valor='valor',
    tipo_dato='string',  # string, int, float, bool, json
    modificable=True,
    grupo='general'
)
```

#### Estados
Cada entidad tiene su tabla de estados:
- `EstadoCuota`
- `EstadoCampania`
- `EstadoTarea`
- `EstadoParticipante`
- `EstadoOrdenCobro`
- `EstadoRemesa`
- `EstadoDonacion`

#### Seguridad
```python
from app.domains.core.models import Sesion, HistorialSeguridad, IPBloqueada

# Sesiones de usuario
sesion = Sesion(usuario_id=..., token=..., ip_address=...)

# Historial de eventos
evento = HistorialSeguridad(
    evento_tipo='LOGIN',
    severidad='INFO',
    usuario_id=...,
    descripcion='Login exitoso'
)
```

### Dominio Geográfico

```python
from app.domains.geografico.models import Pais, Provincia, Municipio, Direccion

# Crear dirección
direccion = Direccion(
    tipo='PRINCIPAL',
    via_tipo='Calle',
    via_nombre='Gran Vía',
    numero='123',
    piso='3',
    puerta='A',
    codigo_postal='28013',
    municipio_id=municipio.id,
    provincia_id=provincia.id,
    pais_id=pais.id
)

# Propiedades útiles
direccion.direccion_completa  # "Calle Gran Vía nº 123, 3º A, 28013 Madrid, Madrid"
direccion.direccion_corta     # "Gran Vía 123 3º"
```

### Dominio Financiero

#### CuotaAnual
```python
from app.domains.financiero.models import CuotaAnual, ModoIngreso

cuota = CuotaAnual(
    miembro_id=miembro.id,
    ejercicio=2024,
    importe=Decimal('50.00'),
    agrupacion_id=agrupacion.id,
    estado_codigo='PENDIENTE'
)

# Registrar pago
cuota.registrar_pago(
    importe_pago=Decimal('50.00'),
    modo_ingreso=ModoIngreso.SEPA,
    referencia='TXN123'
)

# Propiedades
cuota.esta_pagada           # bool
cuota.saldo_pendiente       # Decimal
```

#### Donacion
```python
from app.domains.financiero.models import Donacion

donacion = Donacion(
    miembro_id=miembro.id,
    concepto_id=concepto.id,
    importe=Decimal('100.00'),
    estado_codigo='RECIBIDA'
)

# Emitir certificado fiscal
donacion.emitir_certificado()

# Propiedades
donacion.importe_neto       # Importe después de gastos
donacion.es_deducible       # bool
```

#### Remesa y OrdenCobro
```python
from app.domains.financiero.models import Remesa, OrdenCobro

remesa = Remesa(
    referencia='REM-2024-001',
    fecha_cobro=date(2024, 1, 31),
    estado_codigo='BORRADOR'
)

orden = OrdenCobro(
    remesa_id=remesa.id,
    cuota_id=cuota.id,
    importe=Decimal('50.00'),
    iban='ES...'
)

# Calcular totales
remesa.calcular_totales()

# Verificar si puede enviarse
if remesa.puede_enviarse():
    # Enviar al banco...
```

### Dominio Notificaciones

```python
from app.domains.notificaciones.models import TipoNotificacion, Notificacion

# Crear notificación
notif = Notificacion(
    tipo_id=tipo.id,
    usuario_id=usuario.id,
    titulo='Título',
    mensaje='Mensaje',
    canal='EMAIL',
    estado='PENDIENTE'
)

# Marcar como leída
notif.marcar_como_leida()

# Verificar si expiró
if notif.esta_expirada():
    # ...
```

## Scripts de Inicialización

### Script Maestro

Ejecuta todos los scripts de inicialización en orden:

```bash
python -m app.scripts.inicializar_sistema
```

O programáticamente:

```python
from app.scripts import inicializar_sistema_completo

async with get_session() as session:
    await inicializar_sistema_completo(session)
```

### Scripts Individuales

#### 1. Configuraciones
```bash
python -m app.scripts.inicializar_configuraciones
```

Crea 12 configuraciones por defecto del sistema.

#### 2. Estados
```bash
python -m app.scripts.inicializar_estados
```

Crea 37 estados distribuidos en:
- 5 estados de cuotas
- 6 estados de campañas
- 5 estados de tareas
- 7 estados de participantes
- 4 estados de órdenes de cobro
- 6 estados de remesas
- 4 estados de donaciones

#### 3. Datos Geográficos
```bash
python -m app.scripts.inicializar_geografico
```

Crea:
- 1 país (España)
- 52 provincias
- 20 municipios principales (capitales)

#### 4. Tipos de Notificación
```bash
python -m app.scripts.inicializar_tipos_notificacion
```

Crea 18 tipos de notificación organizados por categorías.

## Patrones y Convenciones

### Nombres de Tablas

Todos los nombres de tablas están en plural:
- ✅ `usuarios`, `miembros`, `cuotas_anuales`
- ❌ `usuario`, `miembro`, `cuota_anio`

### Nombres de Foreign Keys

Format: `entidad_id`
- ✅ `usuario_id`, `miembro_id`, `agrupacion_id`
- ❌ `id_usuario`, `fk_miembro`

### Type Hints

Usar siempre `Mapped[]` con tipos explícitos:

```python
# ✅ Correcto
nombre: Mapped[str] = mapped_column(String(100), nullable=False)
email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
activo: Mapped[bool] = mapped_column(Boolean, default=True)

# ❌ Incorrecto
nombre = Column(String(100))
```

### Relaciones

Siempre especificar `lazy`:

```python
# ✅ Correcto
usuario: Mapped["Usuario"] = relationship(back_populates="miembro", lazy="selectin")

# ❌ Incorrecto
usuario = relationship("Usuario")
```

Opciones de `lazy`:
- `selectin`: Carga en una query separada (recomendado para relaciones 1:1, 1:N pequeños)
- `joined`: JOIN en la misma query
- `select`: Carga bajo demanda

### Async/Await

Todas las operaciones de DB deben ser async:

```python
# ✅ Correcto
async def obtener_usuario(session: AsyncSession, user_id: uuid.UUID):
    result = await session.execute(
        select(Usuario).where(Usuario.id == user_id)
    )
    return result.scalar_one_or_none()

# ❌ Incorrecto (sync)
def obtener_usuario(session: Session, user_id: uuid.UUID):
    return session.query(Usuario).get(user_id)
```

### Soft Delete

Usar siempre soft delete en lugar de eliminar físicamente:

```python
# ✅ Correcto
entidad.soft_delete(usuario_id=current_user.id)
await session.commit()

# ❌ Incorrecto
await session.delete(entidad)
```

### Filtros de Consulta

Siempre excluir registros eliminados:

```python
# ✅ Correcto
stmt = select(Miembro).where(
    Miembro.agrupacion_id == agrup_id,
    Miembro.eliminado == False
)

# O usar el servicio de auditoría
activos = await auditoria.get_active_query(Miembro, agrupacion_id=agrup_id)
```

## Resumen de Archivos Creados

### Infraestructura (8 archivos)
1. `infrastructure/base_model.py` - BaseModel con auditoría
2. `infrastructure/services/encriptacion_service.py`
3. `infrastructure/services/cache_service.py`
4. `infrastructure/services/configuracion_service.py`
5. `infrastructure/services/seguridad_service.py`
6. `infrastructure/services/auditoria_service.py`
7. `infrastructure/services/estado_service.py`
8. `infrastructure/services/notificacion_service.py`

### Dominio Core (4 archivos)
9. `domains/core/models/configuracion.py` - 3 modelos
10. `domains/core/models/estados.py` - 8 modelos
11. `domains/core/models/seguridad.py` - 4 modelos
12. `domains/core/__init__.py`

### Dominio Geográfico (3 archivos)
13. `domains/geografico/models/direccion.py` - 4 modelos
14. `domains/geografico/models/__init__.py`
15. `domains/geografico/__init__.py`

### Dominio Notificaciones (3 archivos)
16. `domains/notificaciones/models/notificacion.py` - 3 modelos
17. `domains/notificaciones/models/__init__.py`
18. `domains/notificaciones/__init__.py`

### Dominio Financiero (5 archivos)
19. `domains/financiero/models/cuotas.py` - 2 modelos
20. `domains/financiero/models/donaciones.py` - 2 modelos
21. `domains/financiero/models/remesas.py` - 2 modelos
22. `domains/financiero/models/__init__.py`
23. `domains/financiero/__init__.py`

### Scripts (5 archivos)
24. `scripts/inicializar_configuraciones.py`
25. `scripts/inicializar_estados.py`
26. `scripts/inicializar_geografico.py`
27. `scripts/inicializar_tipos_notificacion.py`
28. `scripts/inicializar_sistema.py`

### Otros (3 archivos)
29. `models/usuario.py` - Actualizado con BaseModel
30. `domains/__init__.py` - Exports centralizados
31. `scripts/__init__.py`

**Total: 31 archivos creados/actualizados**

## Próximos Pasos

1. **Crear migración de Alembic** con todos los modelos
2. **Ejecutar script de inicialización** para poblar datos base
3. **Actualizar modelos legacy** restantes para usar BaseModel
4. **Crear tests** de servicios e integración
5. **Documentar API GraphQL** con los nuevos modelos

---

**Versión:** 1.0
**Fecha:** Enero 2026
**Autor:** Claude Sonnet 4.5
