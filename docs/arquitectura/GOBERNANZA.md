# Gobernanza — modelo de responsabilidades, mandatos y órganos

> **Estado: IMPLEMENTADO en su núcleo** (backend, rama `claude/gobernanza`), salvo
> lo marcado **[PENDIENTE]**. Ver §10 para qué está hecho y verificado.
>
> **Nomenclatura (decidida):** el concepto se llama **Responsabilidad** de cara al
> usuario y la UI (abarca puestos protocolarios y encargos funcionales). El modelo
> técnico y la BD siguen usando **`Cargo`/`CargoRol`** por ahora — sin migración de
> nombres en esta fase; solo cambia la etiqueta mostrada. A lo largo del documento,
> «cargo» y «responsabilidad» designan lo mismo.

## La regla que lo vertebra todo

**Un nombramiento no nace de un botón: nace de un ACUERDO de un ÓRGANO, reflejado
en un ACTA.**

```
Órgano (con su composición real)
  └─ se reúne → adopta un Acuerdo (votado, APROBADO)
        └─ consta en un Acta APROBADA
              └─ al ejecutarse produce el MANDATO (HistorialNombramiento)
                    └─ que DERIVA los UsuarioRol vía CargoRol,
                       heredando el territorio del mandato
```

Los roles **no se asignan a una cuenta**: se derivan del cargo que la persona
ejerce por un mandato legítimo. Y quien **aprueba** es un **órgano** (colegiado) o
un **cargo** (unipersonal) — **nunca un rol**: un rol es un haz de permisos, no un
sujeto que decide.

## 0. Por qué existe

El control de acceso se construyó por capas que no encajan:

- El motor (`PermissionMatrixSnapshot.can()`) decide **rol → transacción** y **no mira
  el territorio**. `AmbitoTransaccion` (`GLOBAL`/`TERRITORIAL`/`PROPIO`) se declara y
  se guarda, pero **nadie lo lee** al autorizar.
- El scoping territorial existe aparte (`services/ambito_territorial.py`) y se invoca
  **a mano, resolver por resolver** (30 llamadas verificadas).
- Los roles se otorgan de dos formas: por **cargo** (`HistorialNombramiento.cargo_id`
  → `CargoRol`) y **a mano** (`asignar_rol_usuario`, que no rellena `nombramiento_id`
  y rompe la trazabilidad).
- `Rol.nivel` y `Rol.tipo` no significan lo que aparentan (ver §5).

## 1. Principio rector: qué es fijo y qué configurable

| Capa | Qué es | Configurable |
|---|---|---|
| **Transacción** | Operación que el código sabe ejecutar (`ACCESO_ROL_CREAR`). 176. | No — `catalog.py`. |
| **Funcionalidad** | Agrupación coherente de transacciones («Gestión de contactos»). 45. | No — `catalog.py`. |
| **Rol** | Agrupación de **funcionalidades**. Tiene un `nivel` de autoridad. | **Sí**. |
| **Cargo** | Puesto/encargo genérico, sin territorio («Presidencia»). | **Sí**. |
| **CargoRol** | Qué roles confiere un cargo. | **Sí**. |
| **Composición del órgano** | Qué cargos forman un órgano, con su orden protocolario. | **Sí**. |

- `RolTransaccion` (transacción suelta a un rol) queda como **excepción** puntual, no
  como vía principal. La vía buena es agrupar funcionalidades.
- El **seed es inicialización por defecto, no dogma**. Habilita separación de tareas
  (p. ej. desagregar Tesorería en planificador económico + cobros + contabilidad).

## 2. Las entidades y la cadena de derivación

```
UnidadOrganizativa (territorio, con o sin personalidad jurídica)
   └── Órgano            (junta directiva / asamblea / comisión)
          └── Cargo      (presidencia, tesorería, vocalía…)   ← composición del órgano
                 └── Mandato   (socio + cargo + agrupación + [fecha_inicio, fecha_fin])
                        └── UsuarioRol derivados (vía CargoRol; heredan agrupacion_id)
                               └── funcionalidades → transacciones
```

**Regla de oro: los roles se DERIVAN, no se asignan a mano.**

1. Se **nombra** a una persona para un **cargo**, en un **territorio**, con fecha de
   inicio (y opcional de fin). Eso es un **Mandato**.
2. El cargo ya declara qué roles confiere (`CargoRol`).
3. El sistema **deriva** los `UsuarioRol`, cada uno con `nombramiento_id` (trazabilidad)
   y `agrupacion_id` (territorio → restringe al subárbol).
4. Al **cesar** (poner `fecha_fin`), los `UsuarioRol` derivados se desactivan.

El *nombramiento* y el *cese* no son entidades: son los dos extremos del mandato. El
historial de la persona los emite como **eventos discretos** derivados de esas fechas.

**Definiciones cerradas:**
- **Cargo** = catálogo genérico, sin territorio. Ya existe (`acceso/models/cargo.py`)
  con `max_simultaneos`, `duracion_maxima_meses`, `requiere_aprobacion`,
  `cargo_aprobador_id`, `puede_nominar_igual_nivel`.
- **Mandato** = `HistorialNombramiento`, mal llamado → **renombrar a `mandatos`**.
  Ya tiene `cargo_id`, `agrupacion_id`, `fecha_inicio/fin`, `estado`
  (`PENDIENTE→ACTIVO→FINALIZADO`). Conserva `rol_id` **legacy** que hay que eliminar.
- **Órgano** = entidad de primera clase (`TipoOrgano` catálogo + `Organo` instancia por
  unidad, con periodo). Hoy solo existe como el string `TipoReunion.organo`
  (`JUNTA_DIRECTIVA`/`ASAMBLEA_GENERAL`/`COMISION`) y como `JuntaDirectiva` (caso
  especial sin generalizar).

## 3. Dimensión territorial

**El territorio vive en el mandato, no en el cargo ni en el rol.**

- `Cargo` es genérico («Presidencia», no «Presidencia de Madrid»). **No cuelga de
  ningún órgano ni unidad en el catálogo**: es una plantilla reutilizable (así ya
  es hoy en `acceso/models/cargo.py`).
- **El MANDATO es quien lo instancia**: lo ata a una unidad (`agrupacion_id`) y,
  opcionalmente, a un órgano concreto. La *composición del órgano* (§4) es solo una
  plantilla que declara «qué cargos forman este órgano», no una atadura rígida del
  cargo. Un mismo cargo (Coordinación) puede ejercerse en una unidad sin órgano.
- Los `UsuarioRol` derivados heredan ese `agrupacion_id` = «restringe al subárbol».

Una persona ejerce **cargos distintos en territorios distintos** = varios mandatos:

| persona | cargo | territorio | rol derivado |
|---|---|---|---|
| Ana | Presidencia | Grupo local | PRESIDENTE @ local |
| Ana | Vocalía | Provincial | VOCAL @ provincial |

Ana manda como presidenta solo en su grupo local y su subárbol; en la provincial es
vocal. **Roles globales** (SUPERADMIN, CONFIGURADOR): `UsuarioRol` con
`agrupacion_id = NULL` = todo el árbol.

`UsuarioRol.agrupacion_id` y `.nombramiento_id` **ya existen**. Falta: que el mandato
use `cargo_id` (hoy usa `rol_id`) y que se lea `CargoRol` para derivar los roles al
nombrar.

## 4. El órgano como agente de los flujos

> **Requisito de dominio (DECIDIDO).** No hay una lista fija de cargos ni de
> órganos que sembrar desde los estatutos. **Todo es configurable desde el módulo
> de Configuración**: el usuario define y edita los tipos de órgano, su
> **composición** (qué cargos lo forman) y su **jerarquía/orden protocolario**,
> además del catálogo de cargos y sus `CargoRol`. El seed es solo una semilla por
> defecto, editable, no la fuente de verdad. → La **UI de configuración de órganos
> y cargos** es una pieza de primer nivel de esta implementación, no un accesorio.

> **CONFIGURACIÓN vs POBLAMIENTO (DECIDIDO — distinción capital).**
> En **Configuración** solo hay **modelos y parámetros**, nunca instancias. El modelo
> organizativo se define **por NIVEL territorial**, no por agrupación concreta:
>
> ```
> CONFIGURACIÓN (por nivel)          POBLAMIENTO (por agrupación)
> ─────────────────────────          ───────────────────────────
> Nivel «Delegación»                 Delegación de Madrid
>   ├ Junta Directiva                  ├ su Junta Directiva
>   │   Presidencia (1)                │    Presidencia → Ana
>   │   Secretaría  (2)                │    Secretaría  → Luis
>   │   Tesorería   (3)                │    Tesorería   → (vacante)
>   └ Asamblea (pleno)                 └ su Asamblea
> ```
>
> - **`TipoOrgano`** = catálogo puro (Junta Directiva, Asamblea…) con su modo de
>   composición (CARGOS|PLENO). **No lleva composición**: la misma «Junta Directiva»
>   se compone distinto en una Delegación que en un Grupo Local.
> - **`NivelOrgano`** = qué órganos tiene un nivel. **`NivelOrganoCargo`** = su
>   composición en ese nivel (cargos + orden protocolario). Esto es **configuración**.
> - **`Organo`/`OrganoCargo`** = las **instancias** de cada agrupación, creadas a partir
>   del modelo de su nivel y ajustables. Se consultan y gestionan en la **ficha de la
>   agrupación**, nunca en Configuración.
> - **Estructura distribuida**: `NivelOrganizativo.estructura_distribuida` es **por nivel
>   y recursivo** («cada nivel decide cómo se organiza lo que cuelga de él»), y
>   `unidad_id = NULL` marca la plantilla global de los primeros niveles. Por eso la
>   configuración inicial aplica al **primer nivel**, y los inferiores **no heredan en
>   silencio**: replicar es una acción **explícita** con confirmación.

**Dos tipos de composición de órgano (DECIDIDO):**

- **Por cargos** (Junta Directiva, comisiones): su membresía son los cargos que lo
  forman, con orden protocolario. Tiene `CargoRol`. La «aprobación del órgano» es
  el acto de sus cargos.
- **Por pleno** (Asamblea General): órgano de **composición abierta**; su membresía
  **no son cargos sino el pleno de socios con derecho a voto**. NO tiene `CargoRol`.
  Como agente de flujos, «aprobación de la asamblea» = acuerdo del pleno (quórum +
  votación), conectado con `Reunion`/`Acta`. El `TipoOrgano` debe marcar esta
  distinción (p. ej. `composicion: CARGOS | PLENO`).

Un órgano no solo tiene cargos: **decide**.

- **Aprobador**: `FlujoAprobacion.rol_aprobador_id` → aprobador **polimórfico**
  (rol | cargo | **órgano**). El caso órgano necesita **quórum y votación**, y conecta
  con `Reunion`/`Acta` de secretaría: un acuerdo de la junta *es* el acto de aprobación.
- **Destinatario**: falta `TipoAudiencia.ORGANO` (hoy: ROL, CARGO, PERMISO, USUARIO,
  MIEMBRO).
- **Instructor** de expedientes disciplinarios (incoa y resuelve).

Estado: `flujos_aprobacion` está **vacía**, el rol `JUNTA_DIRECTIVA` que menciona su
docstring **no existe**. Capa 3 del RBAC construida y sin estrenar → diseñar desde cero.

## 5. Los tres campos: usar o quitar

**`nivel` → autoridad** (mayor = más poder). Hoy tiene **dos semánticas mezcladas**:
orden protocolario (PRESIDENTE 1, VICEPRESIDENTE 2…, único consumidor
`DetalleAgrupacion.vue:752`) y autoridad (SUPERADMIN 100, funcionales 15–30).
→ El **orden protocolario se muda a la composición del órgano**, liberando `nivel`.
- Regla: nadie crea/edita/asigna un rol de nivel ≥ al suyo.
- Nivel efectivo = el más alto de sus roles, **evaluado por ámbito territorial**.
- Escala: SUPERADMIN 100 > CONFIGURADOR 90 > PRESIDENCIA 80 > VICEPRESIDENCIA 70 >
  SECRETARÍA 60 = TESORERÍA 60 > VOCALÍA 40 > COORDINACIÓN 30.
- **Aviso de migración**: al invertir la semántica, la composición de la junta saldría
  al revés si no se migra a la vez.

**`tipo` → no protege nada.** Solo se lee para limpiar campos territoriales
(`acceso_resolvers.py:147`). Lo que protege es el flag **`sistema`**, y no coinciden
(INTERVENTOR es `tipo=FUNCIONAL` pero `sistema=true`). La UI muestra `tipo` y esconde
`sistema` → miente. Decisión: reducir `tipo` a etiqueta o eliminarlo; **hacer `sistema`
visible**.

**`ambito` → no lo lee el motor.** `can()` es rol→transacción, sin territorio.
**Agujero**: si Ana es presidenta local, `can()` le concede `MEMBRESIA_MIEMBRO_EDITAR`
sin mirar sobre qué miembro.

**Principio fijado (DECIDIDO):** el ámbito **debe** entrar en la decisión de
autorización. `TERRITORIAL` = solo sobre entidades del subárbol del `agrupacion_id`
del `UsuarioRol` que concede el permiso; `PROPIO` = solo sobre la propia persona;
`GLOBAL` = sin restricción territorial. Los ~30 `assert_*` manuales deben
desaparecer, sustituidos por un mecanismo sistémico.

**El CÓMO se diseña aparte → `MOTOR_TERRITORIAL.md`** (pendiente). Es la decisión
de arquitectura más pesada del módulo (afecta a firma de `can()`, a todos los
puntos de control y quizá a cómo se construyen las queries); no se cierra en este
documento. Opciones a evaluar allí: (a) `can(roles, tx, objetivo)` centralizado;
(b) guard/decorator por resolver; (c) filtrado row-level en las queries.

## 6. CONFIGURADOR y break-glass

**CONFIGURADOR:**
- Rol de **sistema** (`sistema=true`), no eliminable (ni lógica ni físicamente), desde
  el seed. La protección `sistema` actúa **antes** de bifurcar soft/hard (verificado).
- Accede a control de acceso + configuración.
- Puede crear roles **por debajo** de los de sistema (regla de nivel).
- Nota: se creó a mano con `nivel=0` (el formulario exige `nivel` como `Int!` y no lo
  explica → el seed debe fijarlo en 90).

**Break-glass `superadmin` (DECIDIDO):** es la **única excepción** a «todo rol se
otorga vía mandato». Recibe su rol global (`UsuarioRol` con `agrupacion_id = NULL`)
**directamente en el bootstrap, sin mandato**, como acceso de arranque/emergencia.
Justificado porque existe antes de que haya socios ni cargos, y es una cuenta
técnica (no necesariamente un contacto/socio, y los mandatos apuntan a
`contactos.id`). Todo lo demás —incluidos los roles de sistema otorgados a
personas reales— va por mandato. La excepción se documenta y no se generaliza.

## 7. Estado real del código (punto de partida)

**Ya existe (mejor de lo que parecía):**
- `HistorialNombramiento` = el Mandato a medio cablear (`cargo_id`, `agrupacion_id`,
  fechas, estado con aprobación). Conserva `rol_id` legacy.
- `Cargo` + `CargoRol`. `CargoRol` **sí se lee en runtime** (destinatario_resolver,
  económico), vía `NombramientoVigente → CargoRol` — para *saber quién ostenta un rol*,
  no para *derivar* al nombrar.
- `UsuarioRol` con `agrupacion_id` **y** `nombramiento_id`.
- Vista `v_nombramientos_vigentes`.
- `PermissionMatrix` ya recoge `role_functionalities` y `functionality_transactions` en
  el snapshot; `can()` **ya expande funcionalidades**. Falta que expanda **ámbito**.

**Falta o está mal:**
- `asignar_rol_usuario` crea `UsuarioRol` **sin** `nombramiento_id` → jubilar.
- **11 mutaciones de nombramiento**, todas por `rol_id` legacy, ninguna por `cargo_id`.
  Y el frontend llama a `asignarCargo(...)` que **no existe** en el schema. → Unificar en
  `nombrarParaCargo` / `cesarDeCargo` (rechazado `asignar_nombramiento`: pleonasmo y
  recibe rol, no cargo).
- `can()` ignora el ámbito (§5).
- `Organo`/`TipoOrgano` no existen como entidad (§4).
- `Rol.nivel` con doble semántica (§5).
- Roles creados en 3 seeds descoordinados (`bootstrap.py`, `seed_init_accesos.py`,
  `seed_roles_organizacionales.py`) + permisos en **17 `seed_permisos_*.py`** →
  unificar en `seed_gobernanza.py`.

## 8. Historial del socio (consecuencia del modelo)

Nombramiento y cese se emiten como eventos discretos derivados de las fechas del mandato
(«Nombrada tesorera el 3/2/2024», «Cesa el 15/6/2026»), mezclados con cuotas, firmas y
participaciones. Base: `historial_contacto` (cubre FIRMA/ASISTENCIA/DONACION) — falta
unir cuotas y los eventos de mandato.

## 9. Plan de implementación (tras aprobar)

Cada paso verificable:

1. **Nomenclatura (DECIDIDO):** «Responsabilidad» solo como etiqueta de UI; el
   modelo/BD siguen siendo `Cargo`/`CargoRol` (sin migración de nombres ahora).
2. **Unificar el otorgamiento**: `nombrarParaCargo` / `cesarDeCargo` como única puerta;
   derivar `UsuarioRol` con `nombramiento_id` + `agrupacion_id`; deprecar `asignar_rol_usuario`.
   (Fase de menos riesgo.)
3. **`Rol.nivel` = autoridad**: migrar la escala; mover orden protocolario a la
   composición del órgano.
4. **Órgano parametrizable**: `TipoOrgano` (con `composicion: CARGOS | PLENO`) +
   `Organo` + composición configurable; generalizar `JuntaDirectiva`; jubilar
   `org.denominacion_organo_gobierno`. Incluye la **UI de configuración** de órganos
   y cargos (pieza de primer nivel, §4).
5. **Motor territorial**: diseño aparte → `MOTOR_TERRITORIAL.md` (§5) — que la
   decisión de autorización lea el ámbito.
6. **Seed unificado** `seed_gobernanza.py` (semilla por defecto, editable).
7. **UI**: ficha de usuario muestra (solo lectura) cargos y roles derivados; el alta se
   hace nombrando para un cargo.

---

## Decisiones cerradas y trabajo diferido

**Dominio — todo cerrado con el usuario:**
- Nomenclatura: «Responsabilidad» en UI, `Cargo`/`CargoRol` en modelo/BD (sin migración ahora).
- Cargos, composición y jerarquía de órganos → **100% configurables** desde el módulo de
  Configuración. El seed es semilla editable, no fuente de verdad.
- El cargo es **genérico**; el **mandato** lo instancia en unidad (`agrupacion_id`) y,
  opcionalmente, en un órgano.
- **Asamblea General** = órgano de composición **por PLENO** (socios con voto), sin `CargoRol`;
  «Junta/comisión» = composición **por CARGOS**.
- **Break-glass `superadmin`** = única excepción al «todo por mandato»: rol global directo en
  el bootstrap, sin mandato.

**Diferido (no bloquea, pero requiere diseño propio antes de implementar):**
- `MOTOR_TERRITORIAL.md` — cómo `can()`/el sistema aplica el ámbito TERRITORIAL (§5).

---

## 10. Qué está IMPLEMENTADO y verificado

Backend completo en la rama `claude/gobernanza`. Todo verificado end-to-end contra
la API real (no solo build).

**Órganos (entidad de primera clase, antes inexistente):**
- `TipoOrgano` (catálogo configurable, con `composicion: CARGOS | PLENO`),
  `NivelOrgano`/`NivelOrganoCargo` (la gobernanza se configura **por nivel**
  territorial), `Organo`/`OrganoCargo` (la instancia real en una agrupación).
- `OrganoService.instanciar_organos`: materializa en una agrupación los órganos que
  su nivel configura, copiando la composición. Idempotente.
- **Secretaría y gobernanza hablan del mismo órgano**: `TipoReunion.tipo_organo_id`
  (antes un string libre) y `Reunion.organo_id`.

**El acuerdo produce el mandato (el eslabón que da sentido a todo):**
- `sec_tipos_acuerdo` (NOMBRAMIENTO, CESE, APROBACION_CUENTAS…, con
  `produce_efecto`) y `sec_acuerdos_nombramiento` (payload: a quién, qué cargo, qué
  agrupación, fechas). Antes un acuerdo era **solo texto libre**.
- `AcuerdoEjecucionService.ejecutar_nombramiento`: exige acuerdo **APROBADO** y
  **acta APROBADA**; crea el mandato con `cargo_id` (no `rol_id`), con
  `tipo_origen='ACUERDO'` + `origen_id`; y **deriva** los `UsuarioRol` vía `CargoRol`
  heredando el territorio. Idempotente (no se nombra dos veces).

**Aprobador polimórfico** en `FlujoAprobacion`: **órgano** o **cargo** (XOR), nunca
un rol. Esto arregló el bug que mantenía `flujos_aprobacion` **vacía**: el catálogo
declaraba `rol_aprobador="JUNTA_DIRECTIVA"` —un órgano metido donde solo caben
roles—, no existía, y el sync lo descartaba con un `warning` silencioso. Ahora ese
fallo es un **error explícito** (RuntimeError en dev).

**Secretaría, ejecutable por primera vez.** `Acuerdo` cuelga de un `PuntoOrdenDia`
(NOT NULL) y **no existía mutación para crear uno**: `registrarAcuerdo` estaba
muerto y por eso la BD tenía 0 reuniones, 0 actas, 0 acuerdos. Los servicios ya
existían; solo faltaba exponerlos (`agregarPuntoOrdenDia`, `registrarAsistente…`).
Los módulos **Secretaría y Presidencia** se han **encendido** (estaban `activo=False`):
si el nombramiento nace de un acuerdo en acta, la secretaría no es un extra.

**La prueba de que funciona** — la app ya responde a la pregunta de negocio:

> *«¿En qué acta consta que Ana es tesorera?»*
> → En el **Acta nº1/2026 (APROBADA)**, de la reunión de la **Junta Directiva**,
>   donde se adoptó el **Acuerdo nº1** («Se nombra Tesorero/a a Ana García»,
>   APROBADO). El mandato derivó el **rol Tesorero @ Europa Laica**.

Intentar ejecutar el acuerdo **sin acta aprobada se rechaza** (probado).

## 11. Qué falta

- **Frontend**: editor de reunión (orden del día + asistentes + acuerdos), creación
  y ejecución de acuerdos desde `Acuerdos.vue`, vista del órgano («esta es la Junta
  de Madrid y estos son sus miembros»), y **retirar `GestionJunta.vue`** (usa
  mutaciones del modelo `JuntaDirectiva` ya eliminado: **peta en runtime**).
- **Cese**: el tipo de acuerdo `CESE` existe en el catálogo, pero su ejecución
  (cerrar el mandato y desactivar los roles derivados) aún no está escrita.
- **Jubilar las mutaciones legacy** de nombramiento que usan `rol_id` y permiten
  crear mandatos saltándose el acuerdo: `asignarNombramiento` (`auth.py`),
  `revocarNombramiento`, `crearNombramiento` (`vinculaciones_resolvers.py`).
- **Motor territorial** (`MOTOR_TERRITORIAL.md`): que el ámbito entre en la decisión
  de autorización. Hoy `can()` sigue siendo rol→transacción sin territorio.
