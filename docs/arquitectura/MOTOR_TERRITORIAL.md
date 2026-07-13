# Motor territorial — que el permiso sepa *sobre qué* se ejerce

> **Estado: IMPLEMENTADO y verificado contra la API real** (ver §8).
> Complementa `GOBERNANZA.md` §5 (que fijó el principio; aquí va el *cómo*).
>
> Las secciones 1–7 son el diseño tal como se aprobó. La §8 recoge lo que finalmente se
> construyó, lo que cambió por el camino y lo que queda abierto.

## 1. El agujero

Hoy la autorización responde **«¿puedes editar socios?»**. Nunca **«¿puedes editar
a *este* socio?»**.

```python
# app/modules/acceso/services/matrix.py:39
def can(self, role_ids: FrozenSet[str], transaction_id: str) -> bool
```

Sin entidad objetivo, sin agrupación. Si Ana es presidenta del grupo local de
Sevilla, `can()` le concede `MEMBRESIA_MIEMBRO_EDITAR` **sobre cualquier socio de
la organización**.

### Es peor de lo que parece: los guards existentes son casi todos no-ops

Existe un carril paralelo (`services/ambito_territorial.py`) invocado **a mano** en
18 resolvers. Pero su primitiva tiene una trampa (`ambito_territorial.py:61-85`):

> si **cualquiera** de los roles del usuario tiene `agrupacion_id IS NULL`, devuelve
> `None` = **GLOBAL, sin filtro**.

Y casi todos los `UsuarioRol` se crean precisamente con `agrupacion_id=None`. Es
decir: **hoy casi todo usuario es global y esos 18 guards no filtran nada.**

### Zonas con CERO control territorial

Económico, actividades, campañas, presupuesto, secretaría, acceso, papelera,
comunicación. Ejemplo concreto: cualquiera con `ECO_MOVIMIENTO_REGISTRAR` puede
registrar un apunte **contra la caja de cualquier agrupación**
(`economico_mutations.py:213`, sin un solo guard).

### La señal existe y se está tirando

`AmbitoTransaccion` (`GLOBAL` / `TERRITORIAL` / `PROPIO`) se declara en los
`catalog.py` (~90 declaraciones), se sincroniza a `FuncionalidadTransaccion.ambito`…
y **nadie la lee al autorizar**. El propio builder de la matriz hace el JOIN a esa
tabla y **descarta la columna** (`repositories.py:99`).

**Todo lo necesario está en el modelo. Solo hay que conectarlo.**

## 2. El principio

La decisión de autorización pasa de ser **binaria** a ser **relativa a un objetivo**:

```
can(roles, transacción)            →  can(roles, transacción, objetivo)
   «¿puedes editar socios?»            «¿puedes editar A ESTE socio?»
```

Y se resuelve según el **ámbito declarado** de la transacción:

| Ámbito | Significado | Comprobación |
|---|---|---|
| `GLOBAL` | no mira territorio (configuración, catálogos) | ninguna |
| `TERRITORIAL` | solo sobre entidades del **subárbol** de la agrupación del rol que concede el permiso | `agrupación(objetivo) ∈ subárbol(rol)` |
| `PROPIO` | solo sobre uno mismo (autoservicio) | `objetivo.contacto == usuario.contacto` |

## 3. Arquitectura (decidida: `can()` recibe el objetivo)

Una sola puerta. Los 18 `assert_*` manuales desaparecen: dejan de ser algo que el
programador **puede olvidar**, y pasan a ser algo que el motor **siempre hace**.

### 3.1 El snapshot deja de tirar la señal

`PermissionMatrixSnapshot` gana un dict:

```
transaccion_ambito: Dict[tx_codigo, AmbitoTransaccion]
```

Poblado en `repositories.py:99` proyectando la columna `ambito` que hoy se descarta.
Si una transacción está en varias funcionalidades con ámbitos distintos, **gana el
más restrictivo** (`PROPIO` > `TERRITORIAL` > `GLOBAL`): un permiso no se amplía por
estar declarado dos veces.

Ficheros: `services/matrix.py`, `services/repositories.py`.

### 3.2 El contexto conoce el ámbito del usuario (y lo memoiza)

Hoy `Context.get_role_ids()` (`graphql/context.py:42`) hace
`SELECT rol_id FROM usuarios_roles` y **descarta `agrupacion_id`**. Se añade:

```python
async def get_ambito(self) -> set[UUID] | None   # None = GLOBAL
```

= unión de los subárboles de las agrupaciones de sus `UsuarioRol` activos.
**Memoizado por request**, junto a `_role_ids_cache`. Hoy cada `assert_*` dispara 3
queries (roles + raíces + CTE recursiva) y `actualizar_contacto` hace **dos asserts
seguidos ⇒ 6 queries redundantes**.

**Se corrige la trampa del `None`.** Hoy basta con que *cualquier* rol tenga
`agrupacion_id=NULL` para volverse global — y como casi todos los `UsuarioRol` se crean
así, todo usuario es global y los guards son no-ops.

La regla correcta exige **dos** condiciones a la vez: rol de sistema **y** sin
agrupación.

```
ámbito global  ⇔  ∃ UsuarioRol activo con Rol.sistema = true  Y  agrupacion_id IS NULL
```

Es decir: **el `agrupacion_id` del mandato siempre ancla**. Una Gestora de miembros con
mandato en Sevilla manda en Sevilla, aunque su rol esté marcado `sistema`.

No sirve mirar solo `Rol.sistema`: ese flag **no** significa «manda en todo» sino «rol de
catálogo, no borrable». `seed_init_accesos.py` lo pone a `True` en bloque para todos los
roles sembrados, de modo que *Gestor de miembros*, *Interventor/a* y *Planificador* —que
sus propias definiciones declaran `es_territorial: True`— acaban con `sistema=true` en
BD. Concederles ámbito global por ese flag sería reabrir el agujero justo en los roles
operativos que más necesitan estar acotados.

Tampoco sirve `Rol.es_territorial`: está mal poblado (Presidente, Tesorero y Secretario
—cargos puramente territoriales— salen con `es_territorial=false`).

Con la regla de las dos condiciones, lo único que queda global es el mandato sin
territorio de un rol de sistema: el superadmin. Todo lo demás se ancla donde ejerce.
→ **Los mandatos derivan sus `UsuarioRol` con el `agrupacion_id` del mandato** (ya lo
hacen: `acuerdo_ejecucion_service._derivar_roles`), así que el dato correcto ya se
está escribiendo.

Ficheros: `graphql/context.py`, `services/ambito_territorial.py`.

### 3.3 El guard resuelve el objetivo

`RequireTransaction.has_permission(self, source, info, **kwargs)`
(`graphql/permissions.py:37`) **ya recibe los argumentos del resolver** — y los
ignora. Ese es el hook.

```python
RequireTransaction("MEMBRESIA_MIEMBRO_BAJA", objetivo=Contacto.por_arg("contacto_id"))
```

El guard: mira el ámbito de la transacción; si es `TERRITORIAL`, resuelve la
agrupación del objetivo y la compara con el ámbito del usuario; si es `PROPIO`,
comprueba que el objetivo sea él mismo. Si es `GLOBAL`, no hace nada.

**Resolutores de territorio** (declarativos, uno por entidad; el «hop» de la entidad
a su agrupación):

| Entidad | Cómo se obtiene su agrupación |
|---|---|
| `Contacto` | `Contacto.agrupacion_id` (directo) |
| `UnidadOrganizativa` | ella misma |
| `CuentaBancaria` | `CuentaBancaria.agrupacion_id` (`tesoreria.py:36`) |
| `Cuota` | `Cuota.agrupacion_id` (NOT NULL) |
| `Donacion`, `Recibo`, `Remesa`, `JustificanteGasto` | `.agrupacion_id` |
| `Reunion` | `Reunion.agrupacion_id` |
| `Actividad` | **⚠️ no tiene agrupación — ver §4** |

### 3.4 Fallo cerrado, no abierto

- Una transacción `TERRITORIAL` **sin objetivo declarado** ⇒ **error en el arranque**
  (dev), no un permiso concedido en silencio. El default-deny debe ser real.
- Si el objetivo no existe o su agrupación es `NULL` en una transacción territorial,
  **se deniega** (salvo que la entidad declare explícitamente que un `NULL` significa
  «de la organización central», y entonces solo un ámbito global la alcanza).
- Los guards actuales están además dentro de `if usuario:` (p. ej.
  `vinculaciones_resolvers.py:487`): **si no hay usuario, el guard se salta**. Eso
  desaparece: sin usuario, no hay permiso.

## 4. La deuda que hay que pagar: `Actividad` no tiene territorio

`Actividad` **no tiene `agrupacion_id`**. Su territorio solo es derivable por dos
caminos **ambiguos y ambos nullable**: `campania_id → Campania.agrupacion_id` o
`grupo_id → GrupoTrabajo.agrupacion_id`. Y una actividad interna puede tener **los
dos a NULL** ⇒ sin territorio derivable.

**Propuesta:** `Actividad.agrupacion_id` (nullable = actividad de la organización
central), poblado en la migración desde su campaña o su grupo cuando exista. Sin
esto, el módulo de actividades **no es cableable** y quedaría como un agujero.

**DECIDIDO: se añade el campo.** Migración con relleno desde campaña/grupo. Es la
deuda de modelo que hay que pagar para que actividades no quede como un agujero.

## 5. Las queries: hoy se ve TODO

El control territorial de **lectura** casi no existe:

- Las queries autogeneradas (strawchemy, `campo(...)`) aplican el permiso
  todo-o-nada pero **no filtran filas**: `contactos`, `cuotas`, `apuntesCaja`… devuelven
  **el universo entero**.
- La query `socios` solo **enmascara el IBAN** si el socio está fuera de tu ámbito
  (`socios_resolvers.py:325`). El resto —nombre, NIF, email, dirección— se ve.
- La **única** query con scoping real de filas es `voluntariosEnAmbito`.

Un coordinador local **ve todos los socios de toda la organización**.

**DECIDIDO: entra en esta entrega.** El agujero se cierra por los dos lados —
escritura (las mutaciones validan el objetivo) y lectura (las queries filtran por
subárbol: no ves lo ajeno). No basta con impedir modificar: la fuga de datos también
es un agujero.

## 6. Plan de implementación

Por fases verificables, de menor a mayor riesgo:

1. **Ámbito en el snapshot** — proyectar `FuncionalidadTransaccion.ambito` (hoy se
   descarta). Sin efecto funcional todavía: solo deja de tirarse la señal.
2. **Ámbito del usuario en el contexto** — `get_ambito()` memoizado, con la trampa
   del `None` corregida (global ⇔ rol de **sistema** **y** **sin** agrupación).
3. **El guard con objetivo** — `RequireTransaction(tx, objetivo=…)` + los resolutores
   por entidad. Empezar por **membresía** (donde ya hay guards manuales que sirven de
   red de seguridad y de test) y luego **económico** (que hoy no tiene ninguno).
4. **Retirar los 18 `assert_*` manuales** conforme cada resolver queda cubierto por el
   motor. No antes: nunca dejar un hueco entre lo viejo y lo nuevo.
5. **`Actividad.agrupacion_id`** (§4) y cablear actividades.
6. **Filtrado de lectura** (§5), si entra en el alcance.
7. **Limpieza**: `app/core/context.py`, `core/authorization_service.py` y
   `core/permission_matrix.py` son **código muerto** con una noción de `territory_id`
   que confunde (el JWT real solo lleva `{sub, iat, exp}`). Borrarlos.

## 7. Verificación

La prueba de que el agujero está cerrado, contra la API real:

1. Crear dos agrupaciones hermanas (A y B) con un socio en cada una.
2. Nombrar a Ana presidenta **de A** (por el flujo de acuerdo: reunión → acuerdo →
   acta → ejecutar; así su `UsuarioRol` hereda `agrupacion_id = A`).
3. Con la sesión de Ana:
   - editar el socio de **A** → **permitido**;
   - editar el socio de **B** → **DENEGADO** (hoy: permitido — ese es el agujero);
   - editar un socio de una **sub-agrupación de A** → **permitido** (subárbol).
4. Repetir con una transacción `GLOBAL` (configuración) → permitido en ambos casos.
5. Repetir con una `PROPIO` (mis datos) → solo sobre sí misma.
6. Económico: registrar un apunte contra la caja de **B** → **DENEGADO** (hoy:
   permitido, sin ningún guard).

Entorno: sin puertos publicados ⇒ `docker exec siga_dev_backend python -c '...urllib...'`
y `docker exec siga_dev_db psql`. Login: `superadmin` / `admin_dev_2026`.

---

## Decisiones cerradas

- **`Actividad.agrupacion_id`**: se añade (migración con relleno desde campaña/grupo).
- **Alcance**: escritura **y** lectura en esta entrega. El agujero se cierra por los
  dos lados.

---

## 8. Estado: implementado y verificado

Verificado contra la API real con una presidenta de Madrid (rol NO de sistema, mandato
en Madrid) frente a una socia de Sevilla:

| | superadmin | presidenta de Madrid |
|---|---|---|
| Baja de una socia de Sevilla | permitido | **denegado** |
| Baja de un socio de Madrid | permitido | permitido |
| `socios` (resolver propio) | 17 filas | **2** (solo Madrid) |
| `contactos` (campo strawchemy) | 30 filas | **7** (solo Madrid) |

### Lo que se cableó

- **Escritura**: `RequireTransaction(tx, objetivo=…)` en las mutaciones que tocan a una
  persona (bajas, suspensiones, ediciones, voluntariado, traslados), al dinero
  (movimientos de tesorería, conciliaciones, cuentas) y a las actividades (actividades,
  campañas, participaciones).
- **Lectura**: `FiltrarPorAmbito` (`graphql/ambito_extension.py`), una extensión de campo
  que recorta el resultado de los campos de strawchemy —que generan su propio SQL y no
  pasan por ningún resolver nuestro—. Aplicada a `contactos`, `actividades`, `campanias`,
  `gruposTrabajo` y `cuentasBancarias`. Más los resolvers propios `socios` y
  `contactosDotables`.
- **`Actividad.agrupacion_id`**: migración `act1terr2ag3`, con relleno heredado de la
  campaña o el grupo. Las creaciones nuevas lo heredan igual (`_agrupacion_al_crear`).

### Guards manuales: qué se retiró y qué NO

Se retiraron los redundantes (los que el motor ya cubre en la misma mutación). **Cuatro
sobreviven, y deben sobrevivir**: los de **dos lados**, que un `Objetivo` no puede
expresar porque ancla en un único punto.

- `actualizar_contacto` cuando cambia de agrupación: exige origen **y** destino.
- `aprobar_traslado_origen` / `aprobar_traslado_destino`: cada extremo lo aprueba quien
  manda en *ese* extremo.

De paso se cerró un `if usuario:` que los envolvía: sin usuario autenticado, el guard
simplemente no se ejecutaba.

### Pendiente

- **`unidadesOrganizativas` no se filtra**: el árbol territorial es referencia común (el
  selector de agrupación lo necesita entero, y ocultarlo rompería el propio traslado).
- **Tareas** (`crear_tarea` / `actualizar_tarea`): cuelgan de una actividad **o** de un
  grupo, ambos opcionales, y el update solo trae el id de la tarea. Necesitan un objetivo
  con alternativa. El control efectivo hoy está en la actividad que las contiene.
- **`CFG_TERRITORIO_*` está declarada GLOBAL pero sus resolvers llevan guard manual**.
  Contradicción a resolver **en el dominio**: si el modelo distribuido exige que cada
  nivel defina el territorio inferior, el ámbito correcto es TERRITORIAL, no GLOBAL. Los
  guards se han dejado (protegen de más, no de menos).
