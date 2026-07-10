# Gobernanza — diseño del modelo de responsabilidades, mandatos y órganos

> **Estado: diseño consolidado, pendiente de aprobación final.** Documento único de
> gobernanza (reconcilia los dos borradores previos). Recoge el modelo cerrado con
> el usuario y el mapa del código verificado contra el stack. Las decisiones aún
> abiertas van marcadas **[PENDIENTE]**.
>
> **Nomenclatura (decidida):** el concepto se llama **Responsabilidad** de cara al
> usuario y la UI (abarca puestos protocolarios y encargos funcionales). El modelo
> técnico y la BD siguen usando **`Cargo`/`CargoRol`** por ahora — sin migración de
> nombres en esta fase; solo cambia la etiqueta mostrada. A lo largo del documento,
> «cargo» y «responsabilidad» designan lo mismo.
>
> **No se toca el motor de permisos ni el modelo de datos hasta aprobar el diseño.**

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

- `Cargo` es genérico («Presidencia», no «Presidencia de Madrid»).
- `Mandato.agrupacion_id` lo instancia en un territorio.
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
sin mirar sobre qué miembro. → Implementar en el motor: `can()` responde «¿puede *sobre
esto*?». `TERRITORIAL` comprueba `agrupacion_id` contra el subárbol; `PROPIO`, el vínculo
directo. Los 30 `assert_*` sueltos desaparecen.

## 6. CONFIGURADOR

- Rol de **sistema** (`sistema=true`), no eliminable (ni lógica ni físicamente), desde
  el seed. La protección `sistema` actúa **antes** de bifurcar soft/hard (verificado).
- Accede a control de acceso + configuración.
- Puede crear roles **por debajo** de los de sistema (regla de nivel).
- Nota: se creó a mano con `nivel=0` (el formulario exige `nivel` como `Int!` y no lo
  explica → el seed debe fijarlo en 90).

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
4. **Órgano parametrizable**: `TipoOrgano` + `Organo` + composición; generalizar
   `JuntaDirectiva`; jubilar `org.denominacion_organo_gobierno`.
5. **Motor territorial**: diseño aparte (§5) — que `can()` lea el ámbito.
6. **Seed unificado** `seed_gobernanza.py`.
7. **UI**: ficha de usuario muestra (solo lectura) cargos y roles derivados; el alta se
   hace nombrando para un cargo.

---

## [PENDIENTE] — preguntas abiertas para el usuario

1. **Lista de cargos de Europa Laica** (según estatutos): presidencia, vicepresidencia,
   secretaría, tesorería, vocalía(s), coordinación territorial, ¿interventoría? ¿vocalías
   temáticas? — bloquea el seed.
2. ¿`Cargo` cuelga del **tipo de órgano** o de la **unidad**? (la coordinación territorial
   parece cargo de unidad, sin órgano).
3. ¿La **Asamblea General** se modela con composición de cargos o es el pleno de socios?
4. **Break-glass `superadmin`**: ¿excepción técnica (rol global sin mandato) o mandato de
   sistema?
5. Estrategia de cableado del territorio en el motor (§5) — requiere su propio diseño.

_(Resueltas: nomenclatura Responsabilidad→UI / Cargo interno; reconciliación de los
dos borradores en este documento.)_
