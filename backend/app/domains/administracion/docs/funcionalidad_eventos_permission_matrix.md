Sistema de eventos para reconstrucción automática de la Permission Matrix

Objetivo: mantener la PermissionMatrix en memoria coherente con cambios en roles, cargos, juntas y funcionalidades, sin recalcular permisos en cada request.

1. Principio general

Separar tres capas:

Command side (mutaciones): modifica estado organizativo
Event layer: notifica cambios relevantes
Projection layer: reconstruye la PermissionMatrix
2. Tipos de eventos del dominio
2.1 Eventos de roles
RoleCreated
RoleUpdated
RoleDeleted
RoleAssignedToUser
RoleRevokedFromUser
2.2 Eventos de cargos y juntas
CargoAssigned
CargoChanged
CargoRevoked
JuntaUpdated
JuntaReconfigured
2.3 Eventos de estructura territorial
TerritoryCreated
TerritoryUpdated
MemberMovedTerritory
MemberJoinedTerritory
2.4 Eventos de permisos
PermissionAddedToRole
PermissionRemovedFromRole
FunctionalityUpdated
TransactionUpdated
3. Bus de eventos (Event Bus)
Responsabilidad

Distribuir eventos de dominio a sus consumidores.

Interfaz conceptual
publish(event)
subscribe(event_type, handler)
Implementación recomendada
In-process (monolito modular)
Evolucionable a:
Redis Pub/Sub
RabbitMQ
Kafka
4. Proyección: PermissionMatrixUpdater

Este es el núcleo del sistema.

Responsabilidad
Escuchar eventos
Invalidar cache o snapshot
Reconstruir matriz parcial o total
Estrategia
Opción A (simple y robusta)
invalidación completa
rebuild total de matriz
Opción B (optimizada)
rebuild parcial por:
role
funcionalidad
territorio
5. Flujo completo
[Mutation / Service]
        ↓
  Domain changes state
        ↓
     Domain Event
        ↓
     Event Bus
        ↓
PermissionMatrixUpdater
        ↓
Invalidate / Rebuild
        ↓
Updated PermissionMatrix (cache)
6. Implementación conceptual
6.1 Event base
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DomainEvent:
    event_id: str
    timestamp: datetime
6.2 Event bus
from collections import defaultdict
from typing import Callable, Dict, List, Type


class EventBus:

    def __init__(self):
        self._handlers: Dict[Type, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: Type, handler: Callable):
        self._handlers[event_type].append(handler)

    def publish(self, event):
        for handler in self._handlers[type(event)]:
            handler(event)
6.3 Evento crítico: cambio de permisos
@dataclass(frozen=True)
class PermissionChanged:
    role_id: str
6.4 PermissionMatrixUpdater
class PermissionMatrixUpdater:

    def __init__(self, matrix_cache, builder):
        self.matrix_cache = matrix_cache
        self.builder = builder

    def handle_permission_change(self, event):
        self.matrix_cache.invalidate()

        snapshot = self.builder.build()
        self.matrix_cache.set(snapshot)
6.5 Suscripción
event_bus.subscribe(
    PermissionChanged,
    matrix_updater.handle_permission_change
)
7. Estrategia de reconstrucción
7.1 Estrategia básica (recomendada inicialmente)
cualquier cambio relevante → rebuild total
simplicidad
consistencia fuerte

✔ ideal para sistemas medianos

7.2 Estrategia avanzada (escala grande)

Separar snapshots:

por rol
por funcionalidad
por territorio

Ejemplo:

Matrix[territory_id]
Matrix[role_id]

✔ reduce coste de recomputación

8. Integración con SQLAlchemy
Patrón correcto
Mutaciones SQLAlchemy → generan Domain Events
Commit → flush events
Event Bus los procesa post-commit
Evitar (crítico)
no reconstruir matriz dentro de transaction DB
no bloquear writes con recomputación pesada
9. Integración con Strawberry
Flujo correcto
Resolver → Application Service
Service → DB + Domain Events
Event Bus → actualiza matriz async o post-commit

Strawberry no participa en permisos ni eventos.

10. Consistencia del sistema
Modelo resultante
consistencia eventual para permisos
consistencia fuerte para datos
permisos reconstruidos automáticamente
11. Resumen de arquitectura
SQLAlchemy Mutation
        ↓
Application Service
        ↓
Domain Event(s)
        ↓
Event Bus
        ↓
PermissionMatrixUpdater
        ↓
In-memory PermissionMatrix Cache
12. Resultado final

Este diseño consigue:

actualización automática de permisos
desacoplamiento total de seguridad y UI
escalabilidad horizontal (event bus externo si se necesita)
coherencia organizativa en sistemas complejos (juntas + territorios + roles)