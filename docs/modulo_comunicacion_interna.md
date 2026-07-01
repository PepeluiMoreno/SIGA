Módulo de comunicación interna — Requisitos y especificación técnica

1. Objetivo

Dotar a la aplicación de un sistema de comunicación interno unificado que permita:

Mensajería entre usuarios
Difusión en ámbitos organizativos (general, territorial, grupos)
Sustituir correo externo y herramientas dispersas
Escalar sin rediseños

El sistema se basa en el concepto único de canal.

2. Alcance funcional
2.1 Tipos de canal

El sistema soporta los siguientes tipos:

GLOBAL → comunicación general a todos los usuarios
TERRITORIAL → comunicación por ámbito geográfico
GROUP → grupos de trabajo
DIRECT → comunicación privada (1:1 o grupo reducido)
2.2 Funcionalidades principales
Envío de mensajes dentro de un canal
Lectura de mensajes con orden cronológico
Gestión de membresía por canal
Indicador de mensajes no leídos
Respuestas a mensajes (hilos ligeros)
Silenciar canales
Archivado/eliminación por usuario

Posibilidad de convertir el mensaje en un mensaje de correo

2.3 Exclusiones iniciales
No hay emails externos
No hay federación con sistemas externos
No hay edición de mensajes (fase inicial)
No hay permisos avanzados por mensaje
3. Modelo de datos

Implementado con SQLAlchemy sobre PostgreSQL.

3.1 Entidad channel

Representa un canal de comunicación.

Campos:

id (PK)
type (enum)
name
description
parent_id (FK self, nullable)
created_at
created_by (FK user)

Restricciones:

type obligatorio
parent_id permite jerarquía organizativa (no funcional)

Índices:

(type)
(parent_id)
3.2 Entidad channel_membership

Relación usuario-canal.

Campos:

channel_id (FK)
user_id (FK)
role (admin, member)
joined_at
last_read_message_id (FK message, nullable)
muted (bool)
archived_at (nullable)
deleted_at (nullable)

Claves:

PK compuesta (channel_id, user_id)

Índices:

(user_id)
(channel_id, user_id)
3.3 Entidad message

Campos:

id (PK)
channel_id (FK)
sender_id (FK user)
body (text)
created_at
reply_to_id (FK message, nullable)

Índices:

(channel_id, created_at DESC)
(sender_id)
3.4 Entidad attachment (opcional)
id
message_id
file_url
metadata
4. Reglas de negocio
4.1 Acceso
Un usuario puede acceder a un canal si existe registro en channel_membership
Canal GLOBAL → membresía obligatoria para todos los usuarios
4.2 Escritura
Permitida si:
existe membership
role != readonly (si se introduce en el futuro)
4.3 Eliminación
Eliminación lógica por usuario:
deleted_at en channel_membership
No se eliminan mensajes físicamente
4.4 Lectura y estado “no leído”

Regla:

Un mensaje está leído si message.id <= last_read_message_id

Ventajas:

No se almacenan estados por mensaje
Escalable
4.5 Creación de canales
GLOBAL: único
DIRECT: se crea dinámicamente al iniciar conversación
GROUP y TERRITORIAL: creados por usuarios con permisos
5. API GraphQL

Implementación con Strawberry GraphQL.

5.1 Queries
myChannels
channel(id)
messages(channelId, cursor, limit)

Requisitos:

Paginación obligatoria (cursor-based)
5.2 Mutations
createChannel(input)
joinChannel(channelId)
leaveChannel(channelId)
sendMessage(channelId, body, replyToId)
markAsRead(channelId, messageId)
5.3 Subscriptions (opcional)
onMessage(channelId)

Uso:

Actualización en tiempo real
6. Frontend

Implementado con Vue.js.

6.1 Estructura UI
Sidebar:
agrupación por tipo de canal
Panel principal:
lista de mensajes
Indicadores:
contador de no leídos por canal
6.2 Estado
Cache por canal
Cursor de paginación
Estado de lectura sincronizado
7. Rendimiento
7.1 Requisitos
Lectura de mensajes O(log n)
Escritura O(1)
Cálculo de no leídos O(1)
7.2 Estrategias
Índices en channel_id + created_at
Uso de last_read_message_id
Paginación obligatoria
8. Escalabilidad

Preparado para:

Añadir reacciones
Añadir menciones
Notificaciones push
Moderación por canal
Permisos avanzados (ACL)

Sin romper el modelo base.

9. Restricciones técnicas
Base de datos: PostgreSQL
ORM: SQLAlchemy
API: GraphQL
Sin dependencias externas de mensajería
Sin duplicación de datos por usuario
10. Criterios de aceptación
Un usuario puede:
ver sus canales
enviar mensajes
recibir mensajes
ver no leídos correctamente
El sistema:
no degrada con volumen de mensajes
mantiene consistencia de permisos
no duplica información
11. Riesgos y decisiones
No implementar estados por mensaje → obligatorio
No separar “foro” y “mensajería” → obligatorio
No usar librerías externas completas → obligatorio

---

## 12. Plantillas de comunicación (correo)

> Las plantillas de correo son un **componente transversal** del módulo de comunicación.
> Las usan otros módulos (campañas, tesorería, asambleas…) para enviar mensajes
> personalizados a los miembros sin duplicar lógica de renderizado o envío.

### 12.1 Modelo `PlantillaEmail`

Tabla: `plantillas_email` en `backend/app/modules/core/comunicacion/plantilla_email.py`.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID | PK |
| `codigo` | String(50) unique | Identificador único (`CAMP_APROBACION`, `TESO_RECORDATORIO_CUOTA`…) |
| `nombre` | String(200) | Nombre legible para el selector de UI |
| `descripcion` | Text nullable | Cuándo usar la plantilla |
| `modulo` | String(50) indexed | Filtro funcional: `campanias`, `tesoreria`, `asambleas`… |
| `asunto` | String(300) | Plantilla del asunto (acepta variables) |
| `cuerpo_html` | Text | Plantilla del cuerpo HTML (acepta variables y bloques `{% if %}`) |
| `variables_disponibles` | JSON nullable | Lista documentada de variables aceptadas, p.e.:<br>`[{"clave": "nombre_miembro", "descripcion": "Nombre del destinatario"}]` |
| `activo` | Boolean | Si está disponible para selección |

Campos de auditoría heredados de `BaseModel`: `fecha_creacion`, `fecha_modificacion`, `eliminado`, `creado_por_id`, `modificado_por_id`.

### 12.2 Campos pendientes — clasificación por rol emisor

Para que cada rol de la organización pueda mantener su catálogo de plantillas, añadir:

```python
rol_emisor: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
contexto:   Mapped[Optional[str]] = mapped_column(Text, nullable=True)
```

**SQL pendiente** (acumular en próxima migración del módulo):
```sql
ALTER TABLE plantillas_email ADD COLUMN rol_emisor VARCHAR(50);
ALTER TABLE plantillas_email ADD COLUMN contexto TEXT;
CREATE INDEX ix_plantillas_email_rol_emisor ON plantillas_email (rol_emisor);
```

Valores previstos de `rol_emisor`: `TESORERO`, `COORDINADOR_CAMPANIA`, `PRESIDENTE`, `null` (general/sin emisor específico).

### 12.3 Sistema de renderizado

Función `_renderizar_plantilla()` en `campania_resolvers.py` (se debe extraer a `core/comunicacion/render.py` cuando lo use más de un módulo).

- Sustitución simple: `{{ variable }}` → valor de `variables[clave]`
- Bloques condicionales: `{% if variable %}…{% endif %}` — se elimina todo el bloque si `variable` es falsy o no existe
- Sin loops, sin filtros, sin includes — “Jinja2-lite”

Variables comunes ya inyectadas en notificaciones de campaña:
`nombre_miembro`, `nombre_campania`, `lema`, `objetivo_principal`, `presupuesto_estimado`,
`requisitos_recursos` (lista), `url_campanias`, `nombre_organizacion`.

### 12.4 Catálogo de plantillas

| Código | Módulo | Rol emisor | Estado | Descripción |
|---|---|---|---|---|
| `CAMP_APROBACION` | `campanias` | — | ✅ Sembrada | Convocatoria pública de campaña aprobada |
| `TESO_RECORDATORIO_CUOTA` | `tesoreria` | `TESORERO` | ⬜ Pendiente | Recordatorio de cuota pendiente |
| `COORD_CAMP_BIENVENIDA` | `campanias` | `COORDINADOR_CAMPANIA` | ⬜ Pendiente | Bienvenida al equipo de campaña |
| `PRES_CONVOCATORIA_ASAMBLEA` | `asambleas` | `PRESIDENTE` | ⬜ Pendiente | Convocatoria de asamblea |

Las plantillas se siembran de forma idempotente desde `backend/app/scripts/bootstrap.py`
en la lista `_PLANTILLAS_EMAIL`. La función `ensure_plantillas_email()` las crea o
actualiza por `codigo` en cada arranque.

### 12.5 API GraphQL

**Queries**
- `plantillasEmail(filter, orderBy, ...)` — listado con filtros (strawchemy auto-generado)

**Mutations CRUD** (strawchemy auto-generado, requieren transacción `COMUNICACION_*`):
- `crearPlantillaEmail(data)`
- `actualizarPlantillaEmail(data)`
- `eliminarPlantillaEmail(id)` (soft delete)

**Mutations específicas de notificación** (en `campania_resolvers.py`, requieren `CAMP_EDIT`):

```graphql
mutation Previsualizar($campaniaId: UUID!, $plantillaCodigo: String) {
  previsualizarNotificacionCampania(campaniaId: $campaniaId, plantillaCodigo: $plantillaCodigo) {
    asunto cuerpoHtml totalDestinatarios
  }
}

mutation Enviar($campaniaId: UUID!, $asunto: String!, $cuerpoHtml: String!) {
  enviarNotificacionCampania(campaniaId: $campaniaId, asunto: $asunto, cuerpoHtml: $cuerpoHtml) {
    enviados fallidos sinEmail total simulado mensaje
  }
}
```

Cuando el patrón se generalice, extraer mutations genéricas a `core/comunicacion/`:
`previsualizarNotificacion(entidadTipo, entidadId, plantillaCodigo)` y
`enviarNotificacion(entidadTipo, entidadId, asunto, cuerpoHtml)`.

### 12.6 Comportamiento del envío

`enviar_notificacion_campania` (extensible al resto de entidades):

1. Si la entidad consumidora tiene flag `notificacion_enviada = true` → rechaza con `ValueError`
2. Si SMTP **no está configurado** (`_load_smtp_config(session).configured == False`):
   - Cuenta destinatarios potenciales y sin-email
   - Marca `notificacion_enviada = true`
   - Devuelve `ResultadoEnvioNotificacion { simulado: true, mensaje: "Envío simulado: SMTP no configurado…" }`
3. Si SMTP está configurado:
   - Itera miembros, intenta enviar uno por uno con `EmailService.enviar(...)`
   - Personaliza `[nombre destinatario]` y `{{ nombre_miembro }}` por destinatario
   - Cuenta `enviados`, `fallidos`, `sinEmail`
   - Marca `notificacion_enviada = true` aunque haya fallos parciales

**Regla one-shot**: cada entidad consumidora (campaña, asamblea, llamamiento de cuota…)
mantiene su propio flag `notificacion_enviada` que **no se puede revertir**. Una vez
notificada, el botón queda deshabilitado (verde "Notificación enviada"). Esto evita
duplicar comunicaciones por error.

### 12.7 Integración en UI — selector de plantilla

Patrón implementado en `frontend/src/modules/comunicaciones/views/DetalleCampania.vue`
(pestaña Aprobación → botón "Notificar a la membresía"):

1. Cargar plantillas filtradas por `modulo` (y futuramente por `rol_emisor` según el rol del usuario)
2. Seleccionar la primera por defecto → previsualizar con datos reales
3. Modal con:
   - `<select>` de plantillas (cambio dispara nueva previsualización)
   - Badge "X destinatarios"
   - `<input>` editable de asunto
   - `<textarea>` editable de cuerpo HTML (font-mono, bg-slate-50, `rows=14`)
   - Aviso de variables sustituidas en runtime: `{{ nombre_miembro }}` y `[nombre destinatario]`
   - Botón "Enviar a N miembros"
4. Pantalla de resultado con estadísticas (Total / Enviados / Fallidos / Sin email)
   y badge "Envío simulado" si el backend devuelve `simulado: true`

Replicar el mismo componente modal para tesorería (recordatorio de cuota) y junta
(convocatoria asamblea) cuando se implementen.

### 12.8 Pendiente: UI de gestión de plantillas

Sección nueva en el módulo de Comunicación (ruta sugerida: `/comunicacion/plantillas`).

Funcionalidad:
- Tabla con columnas: `codigo`, `nombre`, `modulo`, `rol_emisor`, `activo`
- Filtros por `modulo` y `rol_emisor`
- Botón "Editar" → modal con editor HTML inline (textarea por ahora; valorar `vue-quill` o similar más adelante)
- Botón "Nueva plantilla" → mismo modal en modo creación
- Vista previa con variables de ejemplo antes de guardar

Permisos requeridos: nueva transacción `COMUNICACION_PLANTILLA_EDIT` (asignar al rol
`ADMIN` y a coordinadores con responsabilidad de comunicación).

### 12.9 Variables disponibles por módulo (catálogo)

Documentar en `variables_disponibles` (JSON del modelo) qué claves acepta cada plantilla.
Convención:

```json
[
  {"clave": "nombre_miembro",       "descripcion": "Nombre del destinatario"},
  {"clave": "nombre_campania",      "descripcion": "Título de la campaña"},
  {"clave": "url_campanias",        "descripcion": "URL pública del listado de campañas"},
  {"clave": "nombre_organizacion",  "descripcion": "Nombre legal de la organización"}
]
```

Esta lista la consumirá la futura UI de edición para ofrecer un picker de variables
("Insertar {{ nombre_miembro }}").

---

## 13. Histórico de mensajes enviados (MVP, 2026-07-01)

MVP del módulo de Comunicación: cada correo enviado desde la app (mutación
`enviarMensajeContactos`, botón "Enviar mensaje" del grid de contactos) se **registra**
para trazabilidad y consulta. NO es un cliente de correo (no lee IMAP): solo el histórico
de lo enviado por SMTP. La visión de cliente incrustado completo queda post-MVP.

### 13.1 Modelo `MensajeEnviado` (tabla `mensajes_enviados`)

`backend/app/modules/core/comunicacion/mensajeria/mensaje_enviado.py`. Campos: `remitente_id`
(FK usuarios, SET NULL), `enviado_en`, `asunto`, `cuerpo_html`, `para`/`cc`/`cco` (emails
serializados por coma), `enviados`/`total`, `errores` (\n-serializados). Registrado en
`app/models/__init__.py` y en el `__init__` del módulo para que Alembic/el mapper lo vean.

**Regla para el manual:** todo correo que la aplicación envía a socios o contactos queda
archivado en "Mensajes enviados", con su fecha, remitente, destinatarios y el resultado de la
entrega. Permite comprobar qué se comunicó, a quién y cuándo.

### 13.2 API GraphQL

- Mutación `enviarMensajeContactos` (en `membresia_resolvers.py`): tras enviar, si `enviados > 0`,
  crea un `MensajeEnviado` y hace commit.
- Query `mensajesEnviados(limite, offset)` (en `comunicacion_resolvers.py`, tipo `MensajeEnviadoType`):
  histórico ordenado por fecha desc; resuelve `remitenteNombre` desde el contacto del usuario
  (o username/email si es un usuario técnico sin contacto). Permiso: `RequireAuthenticated`.

### 13.3 UI

- Vista `frontend/src/modules/comunicaciones/views/MensajesEnviados.vue`: tabla (fecha, asunto,
  destinatarios, remitente, envíos ok/total) + modal de detalle con el cuerpo HTML tal cual se
  envió. Ruta `/mensajes-enviados`; entrada de menú "Mensajes enviados" (icono sobre) en la zona
  personal del sidebar, gateada por `CONTACTO_LISTAR`/`MEMBRESIA_MIEMBRO_LISTAR`.

### 13.4 SQL pendiente para staging/prod (acumular con el lote)

En dev la tabla se creó vía `MensajeEnviado.__table__.create(checkfirst=True)`. Para staging/prod,
generar la migración Alembic de la tabla `mensajes_enviados` (columnas arriba) al cerrar el lote.
