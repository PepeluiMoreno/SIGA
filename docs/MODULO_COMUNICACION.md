# Módulo transversal de Comunicación

> Ubicación principal: `app/modules/core/comunicacion/`
> Estado: operativo. Notificaciones dirigidas por flujos de trabajo.
> No cubre (todavía): mensajería entre usuarios — ver §7.

## 1. Para qué sirve

Es la pieza por la que **los procesos del sistema avisan a las personas
adecuadas**. Cuando ocurre algo en un flujo de trabajo —se aprueba un acta, el
banco devuelve una remesa, una partida se sobreejecuta— el módulo entrega un
aviso a quienes corresponde según su **rol, cargo o permiso**, sin que el módulo
que origina el aviso tenga que saber quiénes son esas personas ni cómo
contactarlas.

Es **transversal**: cualquier módulo (económico, secretaría, membresía…) puede
emitir avisos a través de él, y el módulo de comunicación no depende de ninguno
en concreto. La dirección de la dependencia es siempre hacia comunicación, nunca
al revés.

Cada aviso se materializa en una **notificación in-app** (una fila por
destinatario, que alimenta el badge de no leídas) y, según la prioridad, también
en un **email**.

## 2. Conceptos

- **Notificación**: aviso para UN usuario. Tiene tipo, título, mensaje, estado
  (PENDIENTE → ENVIADA → LEIDA; o ERROR), y referencia genérica a la entidad que
  lo originó (`entidad_tipo` + `entidad_id`) y una `url_accion` opcional.
- **Tipo de notificación**: catálogo (`PRESUPUESTO_DESVIACION`, `REMESA_DEVOLUCION`,
  `SECRETARIA_ACTA_APROBADA`…). Cada tipo fija su **prioridad**
  (BAJA/NORMAL/ALTA/URGENTE), categoría y qué canales admite. Hay 13 tipos sembrados.
- **Audiencia**: el criterio de a quién va dirigido un aviso, sin nombrar
  personas. Cuatro formas: por **rol**, por **cargo**, por **permiso** o por
  **usuario/miembro** directo.
- **Evento de dominio**: lo que publica un flujo de trabajo ("acta aprobada").
  Un **handler** lo traduce a un aviso con su audiencia.

## 3. Cómo decide el canal email

In-app **siempre**. El email se añade solo si se cumplen TODAS:
1. la **prioridad del tipo** es ALTA o URGENTE,
2. el tipo admite email (`permite_email`),
3. la preferencia del usuario no lo veta (`PreferenciaNotificacion.email_habilitado`),
4. hay SMTP configurado (si no, el envío se marca como simulado, no falla).

La prioridad **propone** el email; el tipo y la preferencia pueden **retirarlo**.
Cambiar el comportamiento de un aviso = cambiar la prioridad de su tipo, sin tocar código.

## 4. Cómo está implementado

```
app/modules/core/comunicacion/
  notificacion.py         Modelos: Notificacion, TipoNotificacion, PreferenciaNotificacion
  plantilla_email.py      Modelo PlantillaEmail
  handlers.py             Handlers de eventos de dominio → emiten avisos
  services/
    destinatario_resolver.py   Resuelve audiencia → lista de destinatarios únicos

app/infrastructure/services/notificacion_service.py
                          NotificacionService: crea in-app en lote, envía email
                          por prioridad, gestiona lectura/archivado/preferencias.
                          Método de alto nivel: emitir().

app/graphql/comunicacion_resolvers.py
                          ComunicacionQuery / ComunicacionMutation (notificaciones
                          del propio usuario).

app/scripts/seeding/seed_comunicacion.py
                          Seed idempotente: 4 estados + 13 tipos.

alembic/.../c1a2b3d4e5f6_comunicacion_estados_y_vista.py
                          Migración: codigo en estados_notificacion, seed de
                          estados, y vista v_nombramientos_vigentes.
```

### 4.1 DestinatarioResolver — el corazón

Traduce una `EspecificacionAudiencia` a destinatarios concretos, **deduplicados
por usuario**. Las cuatro vías:

| Vía | Constructor | Resuelve |
|---|---|---|
| Permiso | `por_permiso("COD", agrupacion?)` | quien puede ejecutar la transacción (RBAC por rol directo **y** por funcionalidad) |
| Cargo | `por_cargo(cargo_id, agrupacion?)` | ocupante vigente del cargo (vista `v_nombramientos_vigentes`) |
| Rol | `por_rol(rol_id, agrupacion?)` | portadores del rol (nombramiento vigente ∪ asignación directa) |
| Usuario/Miembro | `por_usuario(id)` / `por_miembro(id)` | persona concreta |

`agrupacion_id` acota territorialmente: ámbito global (NULL) recibe siempre;
acotado, solo si coincide. **`por_permiso` es la vía preferente** para flujos de
aprobación: es estable frente a cómo esté modelado el rol/cargo.

### 4.2 NotificacionService — la orquestación

- `emitir(tipo_codigo, audiencia, titulo, mensaje, …)`: punto de entrada para los
  flujos. Resuelve la audiencia, crea las notificaciones in-app en lote (un
  commit) y dispara los emails que procedan según la prioridad.
- `crear_notificacion(...)`: crea una notificación individual.
- Lectura/gestión: `obtener_notificaciones_usuario`, `contar_no_leidas`,
  `marcar_como_leida`, `marcar_todas_como_leidas`, `archivar_notificacion`.
- Preferencias: `obtener_preferencias_usuario`, `actualizar_preferencia`.
- Estados resueltos por código (PENDIENTE/ENVIADA/LEIDA/ERROR), cacheados por request.

### 4.3 Eventos y handlers — el desacoplamiento

Los flujos publican un evento (`app/core/events.py`) en el `event_bus`
in-process; los handlers (`handlers.py`) lo traducen a `emitir(...)`. El emisor
no conoce al consumidor. Registro: `wire_comunicacion_handlers(async_session)` en
el lifespan de `main.py`, junto a la invalidación de la PermissionMatrix.

7 eventos con handler suscrito: `ReunionConvocada`, `ActaEnBorrador`,
`ActaAprobada`, `NombramientoPendienteAprobacion`, `TrasladoSolicitado`,
`TrasladoResuelto`, `RemesaDevolucion`.

## 5. Cómo emitir un aviso desde un flujo

Dos formas. Para algo intra-módulo y simple, llamada directa al servicio:

```python
from app.infrastructure.services.notificacion_service import NotificacionService
from app.modules.core.comunicacion.services import EspecificacionAudiencia

await NotificacionService(session).emitir(
    tipo_codigo="PRESUPUESTO_DESVIACION",
    audiencia=EspecificacionAudiencia.por_permiso("ECO_PRESUPUESTO_APROBAR"),
    titulo="Desviación presupuestaria",
    mensaje="…",
    entidad_tipo="partida_presupuestaria", entidad_id=str(partida.id),
)
```

Para algo transversal o secundario a la acción, evento de dominio (recomendado),
publicado **desde el servicio, tras el commit**, envuelto en try/except:

```python
await self.session.commit()
try:
    from app.core.events import event_bus, ActaAprobada
    await event_bus.publish(ActaAprobada(acta_id=str(acta.id), …))
except Exception:
    pass
```

Regla de oro: **un fallo de aviso nunca debe revertir la operación de negocio.**

## 6. Flujos conectados hoy

| Módulo | Disparo | Tipo | Audiencia |
|---|---|---|---|
| económico | desviación presupuestaria | `PRESUPUESTO_DESVIACION` | `por_permiso(ECO_PRESUPUESTO_APROBAR)` |
| económico | devolución de remesa | `REMESA_DEVOLUCION` | `por_permiso(ECO_REMESA_ENVIAR)` |
| secretaría | reunión convocada | `SECRETARIA_CONVOCATORIA` | `por_permiso(REUNION_REGISTRAR_ASIST)` |
| secretaría | acta en borrador | `SECRETARIA_ACTA_BORRADOR` | `por_permiso(ACTA_APROBAR)` |
| secretaría | acta aprobada | `SECRETARIA_ACTA_APROBADA` | `por_permiso(ACTA_FIRMAR)` |

Definidos con handler listo pero **sin emisión conectada** (a la espera de que el
módulo tenga capa de servicios): membresía (nombramientos y traslados). Tipos
sembrados sin uso aún: `REMESA_LISTA_ENVIO`, `CUOTA_*`, `TAREA_ASIGNADA`,
`GRUPO_REUNION_CONVOCADA`, `SEGURIDAD_IP_BLOQUEADA`.

Detalle de planificación por módulo: `docs/PLAN_COMUNICACION_FLUJOS.md`.

## 7. Lo que este módulo NO es

No es mensajería entre personas (usuario↔usuario / canales tipo chat). Eso es una
fase aparte con modelo propio (`channel`/`message`), especificada en
`docs/modulo_comunicacion_interna.md`. Podrá reutilizar el `DestinatarioResolver`
(p. ej. crear un canal con todos los de un rol) y puentear con una notificación
in-app, pero no usa la tabla `notificaciones`.
