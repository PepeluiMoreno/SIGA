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

### 3.2 Económico — Remesas y cobro
- **Punto:** generación de remesa lista para envío; devoluciones SEPA (pain.002).
- **Tipos:** `REMESA_LISTA_ENVIO` (ALTA→email), `REMESA_DEVOLUCION` (ALTA→email).
- **Audiencia:** `por_permiso("ECO_REMESA_ENVIAR")` global o por agrupación.

### 3.3 Económico — Reducción/exención de cuota
- **Punto:** solicitud creada (al tesorero) y resolución (al solicitante).
- **Tipos:** `CUOTA_REDUCCION_SOLICITADA` (NORMAL), `CUOTA_REDUCCION_RESUELTA` (ALTA→email al socio).
- **Audiencia:** al tesorero regional `por_cargo(tesorero, agrupacion_id)`; al
  solicitante `por_miembro(miembro_id)`.

### 3.4 Secretaría — Reuniones y actas
- **Puntos:** `reunion_service.convocar()` → asistentes; `acta_service.aprobar_acta()`
  → quien firma; acta en borrador → secretaría.
- **Tipos:** `SECRETARIA_CONVOCATORIA` (ALTA→email), `SECRETARIA_ACTA_BORRADOR`
  (NORMAL), `SECRETARIA_ACTA_APROBADA` (ALTA→email a firmantes).
- **Audiencia:** convocatoria → asistentes por `por_usuario`/lista; firma →
  `por_permiso("SECRETARIA_ACTA_FIRMAR")`.
- **Recomendado vía evento** (`ReunionConvocada`, `ActaAprobada`): es transversal.

### 3.5 Membresía — Nombramientos y traslados
- **Puntos:** nombramiento `PENDIENTE`→`EN_REVISION` (al aprobador); solicitud de
  traslado creada/resuelta.
- **Tipos:** `NOMBRAMIENTO_PENDIENTE_APROBACION` (ALTA→email al aprobador),
  `TRASLADO_SOLICITADO` (NORMAL), `TRASLADO_RESUELTO` (ALTA→email al solicitante).
- **Audiencia:** al aprobador → `por_cargo(cargo.cargo_aprobador_id, agrupacion)` o
  `por_permiso` de la transacción de aprobación; al solicitante → `por_miembro`.
- **Sinergia:** el evento `CargoAssigned`/`CargoRevoked` (ya existe y reconstruye
  la matriz de permisos) puede además generar un aviso al interesado.

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

## 6. Orden de implementación sugerido

1. Sembrar estados + tipos (desbloquea todo).
2. Activar presupuestos (enganche listo) → primer caso real end-to-end.
3. Secretaría y membresía vía eventos de dominio (mayor valor, transversal).
4. Resto de económico y actividades.
5. Acceso/seguridad.
