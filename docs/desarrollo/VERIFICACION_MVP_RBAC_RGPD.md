# Verificación en ejecución del MVP GSH→SIGA — cambios de RBAC y RGPD

> Resultado de verificar la rama `claude/gsh-siga-membership-analysis-11otv9` (PR #11)
> contra un backend vivo (stack dev: FastAPI + Strawberry/strawchemy + Postgres 17,
> Python 3.13, versiones exactas de `uv.lock`). Documenta los **cambios que introdujo
> la verificación** sobre el MVP original, con el detalle técnico de cada uno.
>
> El MVP funcional (auto-alta, ciclo de vida, traslados, estadísticas, pago) se probó
> end-to-end y funciona; ver la [checklist de resultados](#resultado-de-la-checklist)
> al final. Este documento se centra en los **fixes** que hubo que aplicar.

---

## 1. RBAC — el módulo económico estaba apagado (bloqueante real)

### Síntoma
El RBAC que la PR añadió a los 18 listados económicos de `schema_simple.py`
(`RequireTransaction("ECO_*_LISTAR")`) **denegaba a TODOS los roles, incluido
SUPERADMIN**. Un tesorero no podía ver cuotas, remesas, recibos ni donaciones.
Verificado en runtime: `matrix_cache.can(<roles_tesorero>, "ECO_CUOTA_LISTAR")` →
`False`; lo mismo para superadmin.

### Causa raíz (cadena completa)
1. `app/modules/acceso/services/modulos.py` declaraba `ModuloDef("economico", …,
   activo=False)` — económico estaba **fuera del MVP** por diseño.
2. En el arranque, `CatalogSyncService` fija la columna `transacciones.activa`
   consultando `transaccion_activa_por_funcionalidades()`. Con el módulo OFF, las
   **55 transacciones económicas** quedan `activa = false`.
3. `AsyncPermissionMatrixBuilder._transacciones_inactivas()` resta esas transacciones
   del snapshot de permisos **para todos los roles** (es un fail-closed deliberado:
   ni el superadmin ejecuta transacciones de un módulo apagado).
4. `RequireTransaction` consulta esa matriz → deniega.

Re-sembrar los permisos **no** lo arreglaba: `activa` no se siembra, la recalcula
`modulos.py` en cada arranque.

### Fix
`modulos.py`:
- `economico` pasa a `activo=True` (entra al MVP, decisión del responsable del repo).
- Se retiran dos overrides que solo existían para forzar OFF lo económico dentro de
  módulos encendidos, y que con económico ON sobran:
  - `DATOS_ECONOMICOS_MIEMBRO` (membresía) — IBAN/cuota del socio.
  - `FLUJO_PRESUPUESTO_CAMPANA` (actividades) — presupuesto de campaña.

Efecto: las 55 transacciones económicas + 2 de membresía pasan a `activa=true`; la
`PermissionMatrix` las vuelve a conceder a los roles que ya las tenían enlazadas.

### Permisos del tesorero que faltaban en los seeds
Con el módulo ON, la matriz reveló que **TESORERO no tenía concedidas** cinco
transacciones que esta PR volvió obligatorias (antes las mutations estaban abiertas
sin permiso, así que "funcionaban" para cualquiera):

| Transacción | Qué desbloquea |
|---|---|
| `ECO_CUENTA_LISTAR` | Listado de cuentas bancarias (`cuentasBancarias`) |
| `ECO_MOVIMIENTO_REGISTRAR` | Registrar/anular apuntes de caja |
| `ECO_CUOTA_REGISTRAR_PAGO` | `registrar_pago_cuota_manual` (cobro manual) |
| `ECO_ASIENTO_APROBAR` | Confirmar/anular asientos contables |
| `ECO_PRESUPUESTO_CONSULTAR` | Ver presupuestos y planificaciones (solo lectura) |

Se añadieron a `seed_permisos_tesorero.py` (idempotente), junto a
`ECO_RECIBO_MARCAR_COBRADO` que ya se concedía por otra vía. El seed se ejecuta con:

```
docker exec siga_dev_backend python -m app.scripts.seeding.seed_permisos_tesorero
```

> **Operativa**: tras sembrar permisos hay que **reconstruir la `PermissionMatrix`**
> (reiniciar el backend, o disparar `invalidate_and_rebuild`). El snapshot se
> construye en el lifespan y no se entera de un `INSERT` en `roles_transacciones`
> hecho por fuera. Se detectó en la verificación: el tesorero seguía denegado hasta
> el reinicio.
>
> **Propagación a un entorno nuevo**: `seed_permisos_tesorero` no lo ejecuta el
> bootstrap; lo orquesta `seed_demo_staging` junto al resto de `seed_permisos_*`
> (la asignación de transacciones a roles organizativos es parte del poblado, no del
> bootstrap base). Mi cambio se aplica por ese mismo camino, como los demás
> `seed_permisos_*` ya existentes; no introduce un paso de despliegue nuevo.

### Verificación (por HTTP, tokens reales)
- TESORERO ve los 18 listados económicos y puede ejecutar las mutations blindadas.
- SOCIO y usuario anónimo → denegados en todos ellos.
- Catálogos de membresía (`formasPago`, `importesCuotaAnio`) → siguen accesibles a
  cualquier autenticado (ver §2).

---

## 2. RBAC — fuga: 104 de 122 listados eran públicos sin autenticar (preexistente)

### Síntoma (agujero grave, ya en `master` — no lo introdujo la PR)
De los 122 campos `strawchemy.field` del `Query`, solo los 18 que blindó esta PR
tenían control de acceso. Los otros **104 eran consultables SIN AUTENTICAR**:
`usuarios`, `logsAuditoria`, `transacciones`, toda la estructura RBAC, catálogos…

Y el más grave: `UsuarioType` exponía `reset_token` (+ sus fechas). Un anónimo podía:
- Leer el token de reset de cualquier usuario con recuperación pendiente →
  **toma de cuenta**.
- Aunque se ocultara el campo de salida, **filtrar** por él
  (`usuarios(filter:{resetToken:{like:"a%"}})`) como oráculo para extraerlo carácter
  a carácter.

### Fix (dos capas)

**a) Default-deny en los listados** — `app/graphql/permissions.py`:

```python
def campo(*args, permission_classes=None, **kwargs):
    from . import strawchemy
    if not permission_classes:
        permission_classes = [RequireAuthenticated]
    return strawchemy.field(*args, permission_classes=permission_classes, **kwargs)
```

En `schema_simple.py` los 122 `strawchemy.field(` pasan a `campo(`. Los 18 con
`RequireTransaction` conservan su permiso fino; los 104 restantes pasan a exigir
**autenticación**. Un listado nuevo queda cerrado por defecto aunque se olvide
anotarlo.

> No rompe flujos públicos: las únicas rutas públicas son `/login` (mutation propia,
> no strawchemy) y `/pagar-cuota` (REST puro, sin GraphQL). Verificado.

**b) Secretos del modelo, no del tipo** — `app/modules/acceso/models/usuario.py`:

```python
from strawchemy.dto.utils import PRIVATE
...
password_hash: Mapped[str] = mapped_column(String(255), nullable=False, info=PRIVATE)
reset_token:  Mapped[Optional[str]] = mapped_column(..., info=PRIVATE)
reset_token_expira_en:     ... info=PRIVATE
reset_token_solicitado_en: ... info=PRIVATE
```

`PRIVATE` = `strawchemy.dto.field(set())`: sin `Purpose.READ` ni `WRITE`, strawchemy
excluye la columna de **todos** los DTOs — el tipo directo, los tipos **embebidos**
por relación (`UsuarioRolType.usuario`, `SesionType.usuario`…), los **filtros**
(`UsuarioBoolExp`) y los `order_by`. Marcarlo en el modelo, no en `UsuarioType`, es lo
que cierra el oráculo del filtro y el leak por embebido —un `exclude=` en el tipo solo
tapaba la salida directa—.

> **Importante**: `info=PRIVATE` solo afecta a GraphQL. El ORM sigue leyendo
> `password_hash` con normalidad, así que el login funciona igual (verificado).

### Verificación (SDL completo + HTTP)
- `resetToken`, `passwordHash`, `resetTokenExpiraEn` **ausentes del SDL entero**
  (ningún tipo, ningún input).
- Anónimo → denegado en los 122 listados.
- `usuarios(filter:{resetToken:…})` → error "Unknown argument 'filter'".
- Login (tesorero, superadmin) → sigue OK.

### Deuda conocida (no cerrada en esta verificación)
Con default-deny, los catálogos y listados **no económicos** quedan accesibles a
**cualquier autenticado**, incluido un socio raso (p. ej. `usuarios`, `logsAuditoria`).
Es mejor que "cualquier anónimo", pero sigue siendo laxo. Endurecer cada listado a su
`RequireTransaction` concreto queda pendiente: requiere mapear ~100 campos a su
transacción y validar contra la UI interna, lo que excede una verificación sin la UI
delante.

---

## 3. RGPD — modelos desalineados con la BD (`miembro_id` vs `contacto_id`)

### Síntoma
La auto-alta con `acepta_comunicaciones=True` abortaba con
`UndefinedColumnError: rgpd_consentimientos.miembro_id does not exist`.

### Causa
La migración `t5u6v7w8x9y0` (refactor miembros→contactos) **renombró** la columna
`miembro_id → contacto_id` en `rgpd_consentimientos` y `rgpd_solicitudes_derechos`
(comentario explícito en la migración: *"Estos modelos sí renombraron la columna a
contacto_id"*). Pero los modelos ORM `Consentimiento` y `SolicitudDerecho` seguían
declarando el atributo `miembro_id`. Bug latente que solo disparaba el código nuevo
(único que inserta consentimientos por esa vía).

### Fix
- Modelos: atributo `miembro_id` → `contacto_id` (refleja la columna real).
- Usos: `solicitud_socio_publica_service.py`, `firma_publica_service.py`.
- Resolver `registrar_solicitud_derecho_rgpd`: conserva el parámetro de API
  `miembro_id` (no rompe el contrato GraphQL) pero construye con `contacto_id`.
- Front: `Consentimientos.vue` lee `contactoId`.

### Verificación
Auto-alta con `acepta_comunicaciones=True` registra el consentimiento y completa el
doble opt-in (pendiente_verificacion → activa → aprobada como SOCIO con IBAN intacto).

---

## Resultado de la checklist (PR #11)

| # | Punto | Resultado |
|---|---|---|
| 1 | Stack dev, backend healthy, esquema construye | ✅ |
| 2 | RBAC económico: tesorero ve lo suyo, sin rol no | ✅ (tras §1 y §2) |
| 3 | Auto-alta doble opt-in + IBAN inválido 422 | ✅ (tras §3) |
| 4 | Ciclo de vida + traslado con HistorialAgrupacion | ✅ |
| 5 | `estadisticas_altas_bajas` | ✅ |
| 6 | Pago PayPal | ⚠️ degradación limpia verificada sin credenciales; **captura real pendiente de sandbox** |
| 7 | Tests + linter | ⚠️ 3 tests preexistentes no cubren la PR; imports OK, sin regresión; no hay linter configurado |

### Detalle punto 4 (traslados)
- Ciclo: `suspender→inactiva/suspendido`, `reactivar→activa/activo`,
  `baja→cerrada + fecha_fin + motivo`, `reactivar` limpia motivo. Todo OK.
- `simpatizante→socio`: crea vinculación SOCIO con IBAN/numeroSocio, cierra la de
  simpatizante. OK.
- Traslado: máquina `PENDIENTE→APROBADO_ORIGEN→APROBADO→EJECUTADO`; mueve
  `agrupacion_id` de contacto y vinculación SOCIO; `HistorialAgrupacion` cierra el
  tramo abierto y abre uno nuevo en destino. OK.
- **Observación menor**: `ejecutar_traslado` cierra un único tramo de historial
  (`scalar()`, el más reciente sin `fecha_fin`). Si por datos corruptos hubiera varios
  tramos abiertos a la vez, solo cerraría uno. En operación normal solo hay uno; no es
  bug de la PR.

### Notas de entorno
- `SMTP_*` y `PAYPAL_*` **no llegan al contenedor** en dev (docker-compose.dev.yml no
  los pasa; SMTP vive además en otro host, `panel.europalaica.org`). El envío de email
  está en try/except, así que el alta no se cae; el pago degrada a "no disponible".
- El `JWT_SECRET` de dev tiene 31 bytes (`InsecureKeyLengthWarning`); irrelevante para
  producción, que usa uno más largo.
