# HANDOFF — estado de la sesión (control de acceso / gobernanza / traslados)

> Rama `claude/traslados-mejora`. Stack dev en z4dev (Docker + hot reload).
> Lee esto entero antes de tocar nada.

## Entorno (z4dev)

- Repo en `/opt/docker/apps/SIGA`. Stack: `docker compose -f docker-compose.yml -f docker-compose.dev.yml`.
  Contenedores `siga_dev_backend` (uvicorn --reload + `alembic upgrade head`), `siga_dev_frontend`
  (Vite HMR), `siga_dev_db` (postgres).
- **Ningún puerto está publicado al host.** `curl localhost:8000` cuelga. Para hablar con la API:
  `docker exec siga_dev_backend python -c '...urllib...'` (no hay `curl` dentro del contenedor).
- Login break-glass: usuario **`superadmin`**, pass **`admin_dev_2026`**.
- Login GraphQL: `mutation { login(email: "superadmin", password: "...") { token } }` — el campo se
  llama `email` pero acepta el username.
- **Gotcha de git**: `origin` tiene refspec estrecho → `git fetch origin` **solo trae master**.
  Para otras ramas: `git fetch origin <rama>`. Arreglo de raíz:
  `git config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*' && git fetch origin`.
- Verificar frontend: `docker exec siga_dev_frontend npx vite build --mode development`.
  Ojo: el build reescribe `frontend/dist/`, que está versionado.

## Convenciones del proyecto (respétalas)

- **RBAC en 3 capas por el MISMO permiso** (menú `v-if` = ruta `meta.requiredPermission`
  = resolver `RequireTransaction`). Ver `docs/modulo_acceso.md`. Router es default-deny.
- El catálogo RBAC se declara en `app/modules/<mod>/catalog.py` y lo materializa
  `CatalogSyncService.sync()` en el `lifespan` de `main.py` (que además enlaza SUPERADMIN a todo).
- **Patrón de vista-lista** (referencia: `modules/membresia/views/ListaMiembros.vue`):
  `AppLayout` con **`fluid`** → `<div class="flex flex-col lg:flex-row gap-4 items-start">` →
  `FilterRail storage-key="..."` conteniendo `FilterBar vertical` → columna de resultados en
  `flex-1 min-w-0 w-full` con `ResponsiveTable`. Acción principal en el slot `#actions` del topbar.
  **Sin `fluid`, `AppLayout` centra el contenido en `lg:w-3/4 lg:mx-auto`** y deja un hueco enorme.
- **Vistas en `<keep-alive>`** (ver `App.vue`): usan `onActivated(cargar)`, **no** `onMounted`.
  Con `onMounted` la vista muestra datos obsoletos al volver de un formulario.
- **DRY**: reutilizar AppLayout, ResponsiveTable, FilterBar, FilterRail, EstadoBadge, AppButton,
  SelectorMiembro/Agrupacion, useGraphQL, useConfirm/usePrompt, usePermisos.
- **master es rama de despliegue**: nada de commits directos ni force-push. Trabajo en rama + PR.

## Regla de oro con el usuario

Trabaja **paso a paso**: pregunta lo que no sepas del dominio (estatutos, roles reales),
**no sobre-ingenierices** (lección de traslados), y **confirma el modelo antes de codificar**.

---

## HECHO EN ESTA SESIÓN (sin commitear, 7 ficheros)

### Backend
- `modules/actividades/catalog.py`: las 3 transacciones huérfanas (`GRUPO_EDITAR`,
  `GRUPO_CONVOCAR_REUNION`, `CAMPANA_APROBAR`) ya pertenecen a una funcionalidad. Quitado un
  `CAMPANA_LISTAR` duplicado.
- `modules/acceso/services/catalog_sync.py`: nuevo `_validar_sin_huerfanas()`. Toda transacción
  debe estar en ≥1 funcionalidad (si no, es inasignable: los roles se componen de funcionalidades).
  En `SIGA_ENV=dev` **aborta el arranque**; en producción `logger.error`. Verificado en ambos sentidos.
- `graphql/acceso_resolvers.py`: `eliminar_rol(id, hard=False)`. **El borrado lógico precede
  siempre al físico**: `hard=True` exige que el rol ya esté en la papelera. Verificado contra la BD
  (hard sobre rol vivo → denegado; soft → papelera; hard tras papelera → purgado).

### Frontend
- `components/common/ResponsiveTable.vue`: **ordenación por columna**, aditiva. Solo actúa en
  columnas con `ordenable: true`; sin columna activa devuelve `filas` intacto, así que las otras
  11 vistas que lo usan no cambian. Soporta `valorOrden` (columnas calculadas), nulos al final,
  `aria-sort`, y `ordenInicial`.
- `modules/acceso/views/ListaTransacciones.vue`: patrón estándar completo. Columna **Roles**
  (sin tocar backend: `Transaccion.roles` ya estaba expuesta), chip ámbar «sin asignar»,
  filtro **«Solo sin asignar»**, filtro por módulo, tipo codificado por color con leyenda en el raíl.
  Fuera contadores globales, `EstadoPendiente`, modo `lazy`.
- `modules/acceso/views/ListaRoles.vue`: `ResponsiveTable` con columnas ordenables, patrón
  estándar (`fluid` + `FilterRail`), sin tarjetas de contadores, `onActivated`.
- `graphql/queries/administracion.js`: `GET_ROLES` filtra `eliminado: {eq: false}`
  (el resolver strawchemy no lo hace, y se colaban roles borrados).

---

## PENDIENTE — prioridad

### 1. GOBERNANZA (autorizado por el usuario; empezar por el DISEÑO, no por el código)

**El diseño ya está escrito en `docs/arquitectura/GOBERNANZA.md`** (BORRADOR para revisión).
Recoge las 5 entidades, la cadena de derivación, el territorio en el motor, el órgano como agente,
`nivel`/`tipo`/`ambito`, el estado real del código y el plan por fases. **No tocar el motor de
permisos ni el modelo de datos hasta aprobarlo.** Antes de implementar, resolver con el usuario los
5 `[PENDIENTE]` del final del documento (renombrar `Cargo`→`Responsabilidad`; lista de cargos/órganos
de Europa Laica según estatutos; Asamblea General ¿composición o pleno?; break-glass ¿excepción o
mandato?; estrategia de cableado del territorio). El resto de este punto es contexto de apoyo.

**Modelo cerrado con el usuario:**
- **Cargo** = catálogo genérico («Presidencia»), sin territorio. Configurable por el usuario.
- **Mandato** = socio + cargo + agrupación + `[fecha_inicio, fecha_fin]`. La tabla
  `historial_nombramientos` **ya es esto**, mal llamado → renombrar a `mandatos`.
  El *nombramiento* y el *cese* son sus dos extremos, no entidades aparte; el historial del socio
  los emite como **eventos discretos** derivados de esas fechas.
- **La dimensión territorial vive en el mandato** (`agrupacion_id`), no en el cargo ni en el rol.
  Los `UsuarioRol` derivados heredan ese `agrupacion_id` (= «restringe al subárbol»).
  Así una persona ejerce cargos distintos en territorios distintos.
- **El mandato apunta a un CARGO**, y los roles se derivan vía `CargoRol`. Hoy guarda `rol_id`
  y nadie lee `CargoRol` → hay que cablearlo y eliminar `rol_id`.
- **Órgano** = entidad de primera clase (`TipoOrgano` catálogo + `Organo` instancia por unidad,
  con su periodo). Hoy solo existe como el string `TipoReunion.organo` (valores en BD:
  `JUNTA_DIRECTIVA`, `ASAMBLEA_GENERAL`, `COMISION`) y como `JuntaDirectiva`, que es un caso
  especial sin generalizar.
- **Composición del órgano** = qué cargos lo forman, con su **orden protocolario**. Configurable.
- **El órgano es AGENTE** de los flujos: aprobador en `FlujoAprobacion`, `TipoAudiencia.ORGANO`
  en comunicaciones, e instructor de expedientes disciplinarios.
- **Jerarquía**: `nivel` = autoridad (mayor = más poder). Regla: nadie crea/edita/asigna un rol de
  nivel ≥ al suyo. Nivel efectivo = el más alto de sus roles, **evaluado por ámbito territorial**.
  Escala acordada: SUPERADMIN 100 > CONFIGURADOR 90 > PRESIDENCIA 80 > VICEPRESIDENCIA 70 >
  SECRETARIA 60 = TESORERIA 60 > VOCALIA 40 > COORDINACION 30.
- **CONFIGURADOR**: rol de sistema (`sistema=true`, no eliminable ni lógica ni físicamente) desde el
  seed. Accede a control de acceso + configuración. Puede crear roles por debajo de los de sistema.
- **Roles globales** (SUPERADMIN, CONFIGURADOR): `UsuarioRol` con `agrupacion_id = NULL`.
- **Qué es fijo y qué configurable**: transacciones y funcionalidades vienen del código
  (`catalog.py`). Roles = agrupación de funcionalidades → **configurable**. Cargos, `CargoRol` y
  composición del órgano → **configurables**. El seed es una *inicialización por defecto*, no un dogma.
  (Esto permite separación de tareas: p.ej. tesorería podría desagregarse en planificador
  económico + cobros + contabilidad.)

**Bugs de fondo que el diseño debe resolver:**
- `AmbitoTransaccion` (`GLOBAL`/`TERRITORIAL`/`PROPIO`) **no lo lee el motor de permisos**.
  `PermissionMatrix.can()` es rol→transacción, sin territorio. El control territorial existe aparte
  en `modules/acceso/services/ambito_territorial.py` (`assert_miembro_en_ambito()`, etc.) y se invoca
  **a mano, resolver por resolver**. → Hoy, si Ana es presidenta del grupo local, `can()` le concede
  `MEMBRESIA_MIEMBRO_EDITAR` **sin mirar sobre qué miembro**. Es un agujero, no un detalle.
- `Rol.nivel` tiene **dos semánticas incompatibles**: el seed de roles organizacionales lo usó como
  **orden protocolario** (PRESIDENTE 1, VICEPRESIDENTE 2…) y su único consumidor real es
  `DetalleAgrupacion.vue:752` (`composicionJunta` ordena por él). Pero `bootstrap.py` metió
  SUPERADMIN con 100 y `seed_init_accesos.py` los funcionales con 15–30, usándolo como autoridad.
  → El orden protocolario debe irse al **cargo** dentro de la composición del órgano, liberando
  `Rol.nivel` para autoridad. **Ojo: al invertir la semántica, la composición de la junta saldría
  al revés si no se migra a la vez.**
- `Rol.tipo` (`SISTEMA|ORGANIZACION|TERRITORIAL|FUNCIONAL|PERSONALIZADO`) **no protege nada**; solo
  se lee para limpiar campos territoriales (`acceso_resolvers.py:147`). Lo que protege es el flag
  **`sistema`**, y no coinciden: `INTERVENTOR`/`PLANIFICADOR`/`GESTOR_MIEMBROS` son `tipo=FUNCIONAL`
  pero `sistema=true`. La UI muestra `tipo` y esconde `sistema` → miente al usuario.
- **Los roles se crean en 3 sitios** sin coordinación: `bootstrap.py` (SUPERADMIN),
  `seed_init_accesos.py` (PLANIFICADOR/GESTOR_MIEMBROS/INTERVENTOR), `seed_roles_organizacionales.py`
  (los 9 de gobierno). Y los permisos en **17 ficheros `seed_permisos_*.py`** (de 66 en
  `app/scripts/seeding/`). → Unificar en un `seed_gobernanza.py`.
- **El schema expone 11 mutaciones solapadas** para nombrar: `asignarNombramiento`,
  `crearNombramiento`, `crearHistorialNombramiento`, `actualizarHistorialNombramiento`,
  `eliminarHistorialNombramientos`, `revocarNombramiento`, + CRUD de `cargos`/`cargos_roles`.
  Las tres primeras reciben `rolId`, ninguna `cargoId`. Y el frontend llama a
  `asignarCargo(juntaId, miembroId, tipoCargaId…)` — **que no existe en el schema** (y con errata).
  → Dejar una sola puerta: `nombrarParaCargo` / `cesarDeCargo` (el usuario rechazó
  `asignar_nombramiento`: es un pleonasmo y además recibe un rol, no un cargo).
- `flujos_aprobacion` está **vacía**; el rol `JUNTA_DIRECTIVA` que menciona su docstring **no existe**.
  La capa 3 del RBAC está construida y sin estrenar → diseñar bien desde cero, con órgano como agente.
- **Reparto pendiente**: 55 transacciones activas sin ningún rol (salvo SUPERADMIN), agrupadas en
  **17 funcionalidades**: 11 que ningún rol tiene (`GESTION_ROLES` 9, `APROBACION_CAMPANAS` 6,
  `GESTION_ACTIVIDADES` 6, `GESTION_USUARIOS` 5, `GESTION_EVENTOS` 5, `GESTION_TRASLADOS` 3,
  `GESTION_JUNTAS` 3, + 4 sueltas) y **6 a medias** (`DISENO_CAMPANA` 5/11, `GESTION_MIEMBROS` 4/8,
  `TESORERIA_BASICA` 2/4, `CONTABILIDAD`, `CONCILIACION_BANCARIA`, `GESTION_CUOTAS`) — prueba de que
  se cablearon transacciones sueltas ignorando la agrupación. Las parciales se arreglan solas al
  asignar la funcionalidad entera. **El aviso de "control de acceso incompletamente configurado"
  tiene sentido DESPUÉS del seed, no antes** (hoy diría 55 y nadie le haría caso).
  Excluir de la cuenta las de módulos apagados (16 de `proteccion_datos`).

### 2. Rework de TRASLADOS — ¡REEMPLAZAR lo que hay en la rama!
La rama trae una versión **SOBRE-INGENIERIZADA** (doble aprobación origen/destino + "ejecutar" +
catálogo `motivos_traslado`). **El usuario la rechazó.** El modelo REAL:
- Un traslado es una **NOTIFICACIÓN**. Lo registra el **propio socio** o el **secretario de su
  agrupación**. El **secretario de DESTINO se da por enterado**, y **ese acto aplica el cambio**
  de agrupación (mueve `agrupacion_id` + rellena `HistorialAgrupacion`).
- **Fuera el catálogo `motivos_traslado`** y su página en Config. Solo **nota libre opcional**
  (`SolicitudTraslado.motivo` como texto).
- Estados reducidos a **Notificado → Enterado (+ Anulado)**. El catálogo `estados_traslado`
  (con color) puede quedarse, **re-sembrado** con los 3 nuevos.
- Migración de limpieza: quitar `motivo_traslado_id` + tabla `motivos_traslado`, re-sembrar estados.
- **Ubicación (pendiente de confirmar)**: autoservicio del socio + bandeja del secretario filtrada
  a su agrupación. Preguntar.

Ficheros: `app/modules/membresia/models/traslados/modelos.py`, `app/graphql/vinculaciones_resolvers.py`
(mutations solicitar/aprobar*/rechazar/cancelar/ejecutar → `notificar_traslado` +
`darse_por_enterado_traslado` + `anular`), `frontend/.../BandejaTraslados.vue`,
`frontend/src/graphql/queries/socioGestion.js`, y quitar `catalogos/MotivosTraslado.vue` + ruta +
tarjeta en `CatalogosIndex.vue`.

**Nota**: el `TypeError: Cannot return null for non-nullable field SolicitudTrasladoType.motivoTraslado`
que llena los logs desaparece solo con este rework (el campo se elimina).

### 3. Estandarización del frontend (a medias)
El usuario insiste: **coherencia**. El patrón existe pero no se aplica en todas partes.
- `ListaUsuarios.vue` y `LogAuditoria.vue`: sin `fluid`, sin `FilterRail`, sin `ResponsiveTable`,
  con `onMounted`. Alinear con `ListaMiembros.vue`.
- **Nueve vistas en `<keep-alive>` con `onMounted`** (datos obsoletos al volver): `ListaMiembros`,
  `ListaUsuarios`, `ListaEventos`, `ListaGrupos`, `ListaCampanias`, `Tesoreria`, `Contabilidad`,
  `Remesas`, `Donaciones`. → `onActivated`.
- **`ResponsiveTable` no tiene paginación** y **no existe ningún componente de paginación**:
  `ListaMiembros` la implementa a mano (`pageSize`/`total`/`totalPages`/`from`/`to`, líneas 316-359).
  Decidir: ¿paginación de cliente en el componente (sirve para roles/transacciones), de servidor
  (necesaria para miles de socios), o ambas? **No meter las dos a lo bruto en el mismo componente.**
- **Aviso de cambios sin guardar**: unas vistas de edición lo tienen y otras no
  (`FormularioRol`, `PermisosRol`, `GestionJunta` no avisan). Buscar si hay composable común o si
  cada vista lo reimplementa; extraerlo antes de propagarlo.
- **`EditorRol.vue` es CÓDIGO MUERTO**: no está en ninguna ruta. `/roles/:id/editar` carga
  `FormularioRol.vue`. Su pestaña «transacciones» solo enlaza a `/roles/:id/permisos`. Borrar o cablear.
- **Tres pantallas para editar un rol** (`FormularioRol`, `EditorRol` huérfano, `PermisosRol`) y el
  acceso a permisos es un icono de llave sin etiqueta. El usuario se queja de que ni él, siendo el
  desarrollador, sabe qué es cada cosa. Unificar.
- El menú dice **«Catálogo RBAC»**. El usuario acepta lenguaje técnico (rol, transacción, permiso)
  pero exige **coherencia**.

### 4. Parámetros generales: inmutables vs. mutables
Hay dos clases: los que se fijan en la **inicialización** de la aplicación y pasan a **solo lectura**
(NIF, tipo de entidad…), y los alterables (denominaciones, flags). Darles tratamiento diferenciado.
Relacionado: **«Denominación del Órgano de Gobierno»** (`org.denominacion_organo_gobierno`) es un
vestigio — con `TipoOrgano` como entidad, cada tipo trae su nombre singular/plural y ese parámetro sobra.

### 5. Vestigio: personalidad jurídica de las unidades
`niveles_organizativos` tiene `naturaleza` (`TERRITORIAL|FUNCIONAL|PROGRAMATICA|ADMINISTRATIVA`) y
`vinculo` (`INTERNA|FILIAL|FEDERADA`), y `unidades_organizativas` tiene `nif`, `fecha_constitucion`,
`registro_oficial`. **Nada de eso se usa**: las 5 filas de niveles son `TERRITORIAL`+`INTERNA`, las 65
unidades tienen 0 NIF / 0 fechas / 0 registros, y `EstructuraOrganizativaEditor.vue` fuerza
`naturaleza: 'TERRITORIAL'` y `vinculo: 'INTERNA'` en sus 5 ramas de creación.
La personalidad jurídica es de la **unidad**, no del órgano. Y `FUNCIONAL`/`PROGRAMATICA` no son
territorio: son **órganos** mal colocados en el árbol de unidades.

### 6. Otros
- **Bug preexistente en master**: `TypeError: Cannot return null for non-nullable field
  GrupoTrabajoType.agrupacion`. Igual que se arregló `SolicitudTrasladoType.motivoTraslado`:
  declarar `Optional` en el tipo strawchemy en `types_auto.py`.
- **Redundancia de diseño**: la expansión funcionalidad→transacciones se materializa en
  `roles_transacciones` al guardar el rol *y* se recalcula en `PermissionMatrix.can()`. Si se añade
  una transacción a una funcionalidad en `catalog.py`, los roles que ya la tenían **no la heredan**
  hasta que alguien reedite el rol.
- **Vocabulario de `tipo` de transacción**: los 8 `catalog.py` declaran `CONSULTA|MUTACION|APROBACION`,
  pero la BD tiene además `escritura|critica|configuracion` (afinados a mano que el sync no pisa,
  porque `_sync_transacciones` actualiza nombre/descripción/módulo/activa/sistema pero **no `tipo`**).
  `ListaTransacciones.vue` lo tapa con un `normalizarTipo()` provisional (`MUTACION`→«Escritura»).
  Acordado: unificar al vocabulario de negocio, hacer que el sync escriba `tipo`, migrar las 125 filas
  en mayúsculas, y reclasificar: **crítica** = `ACCESO_ROL_ELIMINAR`, `CFG_TERRITORIO_ELIMINAR`,
  `ACCESO_USUARIO_ELIMINAR`, `CAMPANA_ELIMINAR`, `CONTACTO_ELIMINAR`; **configuración** =
  `MEMBRESIA_JUNTA_CONFIGURAR`, `CFG_CONFIGURACION_EDITAR`, `CFG_ESTADO_GESTIONAR`,
  `CFG_FLAG_MULTITERRITORIAL`, `ECO_CUOTA_CONFIGURAR`, `ACTIVIDAD_CATALOGO_GESTIONAR`.
  `RGPD_ANONIMIZAR_MIEMBRO` se queda en **aprobacion** (anonimizar no destruye: disocia).
  Al terminar, `normalizarTipo()` se borra.
- `_sync_funcionalidades` actualiza nombre/descripción/sistema pero **nunca `activa`**: apagar un
  módulo no apaga sus funcionalidades. Hoy inocuo (las 45 están activas).
- **El módulo de control de acceso NO estaba roto** (punto 1 del handoff anterior): era falsa alarma.
  BD sana: 176 transacciones, 45 funcionalidades, 15 roles, SUPERADMIN enlazado a las 176.
  A superadmin le "faltan" 42 permisos porque `misTransacciones` filtra por `Transaccion.activa` y
  tres módulos (`secretaria`, `proteccion_datos`, `presidencia`) están **apagados a propósito**.

### 7. Catálogo de flujos de membresía (documentar)
Producir `docs/flujos_membresia/` (patrón de `docs/flujos_economico/`). Agentes: socio (PROPIO),
secretario de agrupación (territorial), coordinador territorial, tesorero, presidente/vicepresidente,
junta directiva (colegiado), coordinador de campaña. Flujos: alta/auto-alta ✅, admisión ✅, baja ✅,
traslado (rework), reducción de cuota ✅, **sanciones disciplinarias ✗ (falta entero)**,
**histórico integral del socio ◑**.

- **Sanciones disciplinarias**: no existe modelo (solo `EXPULSION` como MotivoBaja). Flujo
  **estatutario** (incoación → instrucción → alegaciones → resolución Junta/Asamblea →
  apercibimiento / suspensión / expulsión). **Diseñar con el usuario según los estatutos de
  Europa Laica; NO inventar.** Necesita `Organo` como agente (quien incoa y quien resuelve).
- **Histórico integral del socio**: piezas existen (cuotas, donaciones, participaciones) pero sin
  ensamblar. Base: `historial_contacto` (cubre FIRMA/ASISTENCIA/DONACION) — falta unir cuotas y
  los eventos de mandato (nombramiento/cese).
