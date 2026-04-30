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