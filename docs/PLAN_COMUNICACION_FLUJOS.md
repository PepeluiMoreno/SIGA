# Plan de integración del módulo de Comunicación en los flujos de trabajo

> Rama: `feature/comunicacion-flujos`
> Este documento define **dónde** y **cómo** cada módulo dispara avisos a través
> del subsistema de comunicación, de forma uniforme y sin acoplar los módulos
> entre sí.

## 1. Arquitectura de integración (cómo se usa)

El subsistema expone **dos formas de uso**, de menor a mayor desacoplamiento:

### 1.1 Llamada directa al servicio (síncrona, dentro de la transacción)

Para avisos que son consecuencia inmediata y local de una acción del usuario.
El flujo construye una `EspecificacionAudiencia` y llama a `NotificacionService.emitir(...)`:

```python
from app.infrastructure.services.notificacion_service import NotificacionService
from app.modules.core.comunicacion.services import EspecificacionAudiencia

await NotificacionService(session).emitir(
    tipo_codigo="PRESUPUESTO_DESVIACION",
    audiencia=EspecificacionAudiencia.por_permiso("ECO_PRESUPUESTO_APROBAR"),
    titulo="Desviación presupuestaria",
    mensaje="La partida «Material» está sobreejecutada…",
    entidad_tipo="partida_presupuestaria",
    entidad_id=str(partida.id),
)
```

`emitir()` resuelve la audiencia (deduplicada), crea la notificación in-app para
todos y, **según la prioridad del tipo** (ALTA/URGENTE), envía además email a
quien proceda. Un fallo de aviso nunca debe abortar la operación de negocio: el
llamante envuelve la llamada en `try/except` o la difiere tras el commit.

### 1.2 Evento de dominio + handler (desacoplado, recomendado para lo transversal)

Para avisos que cruzan módulos o que conviene mantener fuera del servicio de
negocio. El flujo publica un evento en el `event_bus` (ya existe en
`app/core/events.py`) y un handler suscrito traduce evento → audiencia → `emitir`.
Ventaja: el módulo emisor no conoce el de comunicación; se prueban por separado;
evolucionable a cola externa sin tocar a los emisores.

```python
# en el módulo de negocio:
await event_bus.publish(ActaAprobada(acta_id=str(acta.id), reunion_id=...))

# en core/comunicacion/handlers.py (suscrito una vez en el lifespan):
async def _on_acta_aprobada(ev: ActaAprobada) -> None:
    async with async_session() as s:
        await NotificacionService(s).emitir(
            tipo_codigo="SECRETARIA_ACTA_APROBADA",
            audiencia=EspecificacionAudiencia.por_permiso("SECRETARIA_ACTA_FIRMAR"),
            titulo="Acta lista para firma", mensaje=..., entidad_tipo="acta",
            entidad_id=ev.acta_id,
        )
```

**Criterio de elección:** intra-módulo y simple → llamada directa (1.1). Cruza
módulos, o el aviso es secundario a la acción → evento + handler (1.2).

## 2. Especificación de audiencia: las cuatro vías

El `DestinatarioResolver` traduce un criterio a destinatarios únicos:

| Vía | Constructor | Resuelve | Uso típico |
|---|---|---|---|
| Permiso | `por_permiso("COD", agrupacion_id?)` | Todos los que pueden ejecutar la transacción (RBAC por rol directo **y** vía funcionalidad) | «avisa a quien pueda aprobar esto» |
| Cargo | `por_cargo(cargo_id, agrupacion_id?)` | Ocupante vigente del cargo (vista `v_nombramientos_vigentes`) | «avisa al tesorero de esta agrupación» |
| Rol | `por_rol(rol_id, agrupacion_id?)` | Portadores del rol (nombramiento vigente ∪ asignación directa) | «avisa a todo el rol de secretaría» |
| Usuario / Miembro | `por_usuario(id)` / `por_miembro(id)` | Persona concreta | «avisa al solicitante» |

`agrupacion_id` acota territorialmente: ámbito global (NULL) recibe siempre; un
ámbito concreto recibe solo si coincide. **La vía preferente para flujos de
aprobación es `por_permiso`**: es la más estable (no depende de cómo esté
modelado el rol/cargo, solo de quién tiene el permiso de la acción siguiente).

## 3. Mapa de integración por módulo

Prioridad del tipo: `URGENTE`/`ALTA` ⇒ también email; `NORMAL`/`BAJA` ⇒ solo in-app.

### 3.1 Económico — Presupuestos  *(ACTIVO)*
- **Punto:** `presupuesto_service.avisar_desviacion()` tras imputar gasto.
- **Tipo:** `PRESUPUESTO_DESVIACION` · prioridad NORMAL (control blando, in-app).
- **Audiencia:** `por_permiso("ECO_PRESUPUESTO_APROBAR")`.
- **Estado:** conectado a `emitir()`. Se eliminó el flag `_NOTIFICACIONES_ACTIVAS`
  y el método propio `_usuarios_control_presupuestario` (solo miraba el camino
  RBAC directo); `por_permiso` cubre además el permiso concedido vía funcionalidad.

### 3.2 Económico — Remesas y cobro  *(devolución ACTIVA)*
- **Evento:** `RemesaDevolucion` (en `core/events.py`).
- **Emisión conectada:** `remesa_service.importar_fallidos_banco()` publica
  `RemesaDevolucion` tras el commit cuando hay órdenes devueltas.
- **Handler:** `REMESA_DEVOLUCION` (ALTA→email), audiencia `por_permiso("ECO_REMESA_ENVIAR")`.
- **Pendiente:** `REMESA_LISTA_ENVIO` (menor valor: quien genera la remesa ya lo
  sabe; se deja para cuando haya separación de roles generar/enviar).

### 3.3 Económico — Reducción/exención de cuota
- **Punto:** solicitud creada (al tesorero) y resolución (al solicitante).
- **Tipos:** `CUOTA_REDUCCION_SOLICITADA` (NORMAL), `CUOTA_REDUCCION_RESUELTA` (ALTA→email al socio).
- **Audiencia:** al tesorero regional `por_cargo(tesorero, agrupacion_id)`; al
  solicitante `por_miembro(miembro_id)`.

### 3.4 Secretaría — Reuniones y actas  *(COMPLETO)*
- **Eventos:** `ReunionConvocada`, `ActaEnBorrador`, `ActaAprobada` (en `core/events.py`).
- **Handlers:** suscritos en `core/comunicacion/handlers.py` →
  `SECRETARIA_CONVOCATORIA` (audiencia `REUNION_REGISTRAR_ASIST`),
  `SECRETARIA_ACTA_BORRADOR` (`ACTA_APROBAR`), `SECRETARIA_ACTA_APROBADA` (`ACTA_FIRMAR`).
- **Emisión conectada (tras commit, envuelta):**
  `reunion_service.convocar_reunion()` → `ReunionConvocada`;
  `acta_service.crear_acta_borrador()` → `ActaEnBorrador`;
  `acta_service.aprobar_acta()` → `ActaAprobada`.

### 3.5 Membresía — Nombramientos y traslados  *(handlers ACTIVOS; emisión bloqueada por diseño)*
- **Eventos:** `NombramientoPendienteAprobacion`, `TrasladoSolicitado`, `TrasladoResuelto`.
- **Handlers:** suscritos →
  `NOMBRAMIENTO_PENDIENTE_APROBACION` (audiencia `MEMBRESIA_CARGO_ASIGNAR`),
  `TRASLADO_SOLICITADO` (`MEMBRESIA_TRASLADO_APROBAR`),
  `TRASLADO_RESUELTO` (audiencia `por_miembro` del solicitante).
- **Emisión PENDIENTE — requiere refactor previo del módulo:** hoy nombramientos y
  traslados se crean/actualizan mediante mutations CRUD autogeneradas por strawchemy
  (`crear_historial_nombramiento`, `crear_solicitud_traslado`), sin un método de
  servicio con flujo de aprobación donde publicar el evento. Cuando membresía tenga
  mutations custom de aprobación (refactor propio del módulo), basta con publicar el
  evento tras el commit — el subsistema de comunicación ya está listo para recibirlo.

### 3.6 Actividades — Campañas y grupos de trabajo
- **Puntos:** campaña aprobada (ya hay notificación a la membresía por email vía
  plantilla — mantener ese camino); asignación de tarea; convocatoria de reunión
  de grupo.
- **Tipos:** `TAREA_ASIGNADA` (NORMAL), `GRUPO_REUNION_CONVOCADA` (ALTA→email).
- **Audiencia:** `por_usuario(responsable)` / `por_miembro`.
- **Nota:** la notificación de campaña a la membresía es un envío MASIVO con
  plantilla editable; seguirá usando su flujo propio. El módulo de comunicación
  cubre los avisos DIRIGIDOS por flujo, no las campañas de email masivas.

### 3.7 Acceso / Seguridad
- **Puntos:** IP bloqueada, intentos de acceso anómalos, reseteo de contraseña.
- **Tipos:** `SEGURIDAD_IP_BLOQUEADA` (URGENTE→email al admin),
  `SEGURIDAD_RESET_PASSWORD` (ya cubierto por `password_reset_service`; no duplicar).
- **Audiencia:** `por_permiso` del rol administrador / `por_usuario` afectado.

## 4. Catálogo de tipos de notificación a sembrar

Sembrar idempotentemente en bootstrap (junto a los estados PENDIENTE/ENVIADA/
LEIDA/ERROR). Cada tipo fija su `prioridad` (que decide el email), `categoria`,
`permite_email`, `requiere_accion`, icono y color. Lista inicial:

`PRESUPUESTO_DESVIACION`, `REMESA_LISTA_ENVIO`, `REMESA_DEVOLUCION`,
`CUOTA_REDUCCION_SOLICITADA`, `CUOTA_REDUCCION_RESUELTA`,
`SECRETARIA_CONVOCATORIA`, `SECRETARIA_ACTA_BORRADOR`, `SECRETARIA_ACTA_APROBADA`,
`NOMBRAMIENTO_PENDIENTE_APROBACION`, `TRASLADO_SOLICITADO`, `TRASLADO_RESUELTO`,
`TAREA_ASIGNADA`, `GRUPO_REUNION_CONVOCADA`, `SEGURIDAD_IP_BLOQUEADA`.

## 5. Principios transversales

1. **Un aviso nunca rompe la operación de negocio.** Envolver siempre, o diferir
   tras commit. El subsistema ya captura por destinatario; el llamante captura el
   global.
2. **In-app es el registro base; el email es derivado de la prioridad.** No se
   decide el canal por disparo: se decide por el tipo. Cambiar la prioridad del
   tipo cambia el comportamiento sin tocar código.
3. **Preferencia del usuario y `permite_email` del tipo son vetos**, nunca
   activadores.
4. **SMTP no configurado ⇒ email simulado**, nunca error; coherente con campañas.
5. **`por_permiso` es la vía preferente** para flujos de aprobación: estable
   frente a cambios de modelado de roles/cargos.
6. **Idempotencia** en el seed de tipos y estados (crear-o-actualizar por código).

## 6. Estado de implementación

1. ✅ Estados + tipos sembrados (idempotente, en bootstrap).
2. ✅ Migración Alembic (codigo en estados_notificacion, seed, vista v_nombramientos_vigentes).
3. ✅ DestinatarioResolver (4 vías + dedup) y NotificacionService (email por prioridad).
4. ✅ Capa GraphQL (mis notificaciones, no leídas, marcar/archivar).
5. ✅ Presupuestos activo (primer caso real end-to-end).
6. ✅ Eventos de dominio + 6 handlers (secretaría y membresía) suscritos en el lifespan.
7. ✅ Emisión conectada en secretaría: `convocar_reunion`, `crear_acta_borrador`,
   `aprobar_acta` (los 3 eventos publican tras commit).
8. ⏳ Membresía: handlers listos, pero la emisión requiere que el módulo tenga
   mutations custom de aprobación (hoy son CRUD autogeneradas; refactor propio).
9. ⏳ Pendiente (fase aparte): mensajería interna usuario↔usuario (sección 7).
10. ⏳ Pendiente: resto de económico (remesas, cuotas), actividades y seguridad.

## 7. Pendiente: mensajería interna entre usuarios (fase aparte)

Lo construido en esta rama cubre la comunicación **dirigida por los procesos**
(sistema → usuario): avisos que un flujo de trabajo emite a destinatarios
resueltos por rol/cargo/permiso. Es un alcance distinto del de la **mensajería
interna entre personas** (usuario → usuario / usuario → canal), que queda
PENDIENTE como fase propia.

Esa segunda pieza está especificada en la primera mitad de
`docs/modulo_comunicacion_interna.md` (modelo de **canales**): entidades
`channel` (GLOBAL / TERRITORIAL / GROUP / DIRECT), `channel_membership`
(con `last_read_message_id`, `muted`, `archived_at`), `message` (con
`reply_to_id` para hilos ligeros) y `attachment` opcional; estado de no-leído
calculado por comparación con `last_read_message_id` (O(1), sin estado por
mensaje); API GraphQL `myChannels` / `channel` / `messages` (cursor) y mutations
`createChannel` / `sendMessage` / `markAsRead` / `join` / `leave`; opcional
subscription `onMessage` para tiempo real.

Relación con lo ya hecho:
- **Modelo separado.** La mensajería NO reutiliza la tabla `notificaciones`
  (que es 1 fila por destinatario de un aviso del sistema); usa su propio modelo
  de canales/mensajes. Sí puede **reutilizar** el `DestinatarioResolver` para,
  por ejemplo, crear un canal con todos los portadores de un rol/cargo.
- **Puente útil.** Un mensaje dirigido a un usuario puede, además, generar una
  `Notificacion` in-app de tipo `MENSAJE_DIRECTO` (prioridad NORMAL) para que
  aparezca en el badge ya existente, sin duplicar el contenido.
- **No bloquea** la entrega de avisos de procesos: son subsistemas
  independientes que comparten la sección de UI de "Comunicación".
