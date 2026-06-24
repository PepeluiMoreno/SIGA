# Refactor CRM (Contacto / Participacion / Vinculacion) — estado

> Continuación del WIP `refactor(crm): modelo Contacto + Participacion + Vinculacion`.
> Este documento registra qué se ha cerrado para que el backend **arranque** y qué
> queda pendiente (reconducción funcional + migración de datos).

## Qué hace el refactor

Rediseño del núcleo de identidad de SIGA siguiendo el patrón Party-Role:

- **Contacto**: persona física o jurídica (single-table, discriminador `tipo`).
  Sustituye a `Miembro` como entidad central de identidad.
- **Vinculacion**: lazo tipado y vigente contacto↔organización (`TipoVinculacion`
  con `codigo`/`ambito`/`area_responsable`); satélites `Socio` y `Voluntario`.
- **Participacion** (base, módulo membresía): actos discretos (firma, donación,
  membresía, convenio, asistencia) con satélites en sus módulos de dominio.
- Entidades demolidas: `Firmante`, `RolParticipante`, `ParticipanteCampania`,
  `ConvenioInstitucional`, el módulo `organizaciones` entero (`Organizacion`,
  `TipoOrganizacion`, `EstadoConvenio`, `Convenio`) y la `Participacion` de
  actividades (renombrada `AsistenciaActividad`).

## Cerrado en esta sesión — el backend ARRANCA

Verificado en el entorno bloqueado (`uv.lock`, Python 3.13): `configure_mappers()`,
construcción del schema Strawchemy (392 tipos en el SDL) e `import main` (29 rutas)
pasan en verde.

- **Modelos**: import de `BaseModel` corregido en los 5 ficheros CRM; colisión de
  tabla `tipos_vinculacion` resuelta (el canónico es el de membresía; eliminado el
  `TipoVinculacion` deprecado de `acceso`); `back_populates` inverso
  `Contacto.firmas_campania` añadido; `Miembro.usuario` (obsoleto) retirado;
  relaciones RGPD en `Contacto` pospuestas (proteccion_datos aún cuelga de
  `miembros`).
- **Registro**: `modules/__init__.py` y `app/models/__init__.py` (Alembic) al día:
  retiradas las clases demolidas, registrado el núcleo CRM.
- **GraphQL**: `types_auto` / `inputs_auto` / `mutations` / `schema_simple`
  depurados de tipos/inputs/mutations de entidades demolidas; `TipoVinculacion`
  repuntado a membresía; `Participacion*` (GraphQL) repuntado a `AsistenciaActividad`
  conservando el nombre de cara al front; view-model `VoluntarioType` → `VoluntarioAmbito`
  (la entidad `Voluntario` ahora ocupa el nombre GraphQL `Voluntario`).
- **Servicios reconducidos**: `actividad_service.crear_participacion`
  (Participacion base + AsistenciaActividad) y `firma_publica_service`
  (Firmante → Contacto PF + Participacion tipo FIRMA + FirmaCampania).

## PENDIENTE — reconducción funcional `Miembro` → `Contacto`

La capa de **modelos** está migrada, pero **~56 ficheros** todavía usan el modelo
`Miembro`. Esto NO rompe el arranque (las referencias viven en cuerpos de método),
pero fallará en tiempo de ejecución contra el esquema nuevo. Reconducir por área:

- `economico/services` (7): `donacion_service` y `modelo_182_service` usan
  `Donacion.miembro_id` (ahora `contacto_id`); `remesa`/recibos referencian
  `miembro_id` (la migración los reapunta a `vinculacion_socio_id`). **Cuidado:
  el modelo 182 es fiscal — requiere validación con datos reales.**
- `secretaria/services/convenio_service` + `graphql/secretaria_resolvers`:
  construyen `Convenio` con `entidad_contraparte`/`nif_contraparte` (texto), que ya
  no existen; la contraparte es ahora `contraparte_id` → Contacto PJ.
- `acceso/services/ambito_territorial`: usa `Usuario.miembro_id` (ahora
  `contacto_id`) y `Participacion.miembro_id` (modelo viejo de actividades).
- `graphql` (6) y `scripts/seeding|importacion|dump` (22): seeds e importadores
  legacy; reconducir cuando se vuelvan a ejecutar.

## Migraciones Alembic — PROBADAS y corregidas en PostgreSQL real

Probadas con un PostgreSQL 16 efímero: esquema base por `create_all` (master),
`stamp f3d4e5f6a7b8`, datos de ejemplo (simpatizante/socio/voluntario, usuario,
cuota) y `alembic upgrade head`. **El núcleo aplica en verde y se verificó el
resultado**: contactos(3, tipo=PERSONA_FISICA), vinculaciones
(SIMPATIZANTE/SOCIO/VOLUNTARIO), socios(2), voluntarios(1),
`usuarios.contacto_id`, `cuotas.vinculacion_socio_id`, `miembros→miembros_legacy`,
`firmas_campania.firmante_id` eliminada.

Bugs corregidos en las migraciones (ver commit): grafo con dos heads (p1 colgaba
de fase2 → rebasado a `f3d4e5f6a7b8`); `tipos_vinculacion` preexistente no recibía
las columnas nuevas; `dialect.has_column` inexistente; `INSERT` sin `id`;
`estados/tipos_miembro` sin `codigo` (se usa `nombre`); drop de FKs por nombre
fijo (frente a `*_fkey` de create_all) → drop dinámico; `contactos_temp` sin las
columnas propias de Contacto (tipo, razon_social, cif…); FK de firmas a contactos.

### Lo que las migraciones AÚN no hacen (acoplado a la reconducción)

- **No crean** `participaciones`, `membresias`, `tipos_entidad_juridica`, ni las
  columnas `participacion_id` de los satélites (firmas/donaciones/convenios/
  asistencias), ni hacen backfill de participaciones para datos existentes.
- En greenfield esas tablas las crea `create_all`; pero `create_all` sobre la BD
  ya migrada **falla** mientras exista el modelo `Miembro` (sus índices
  `ix_miembros_*` chocan con los de `miembros_legacy`). Es decir: **la migración no
  cierra hasta completar la reconducción `Miembro`→`Contacto`** (eliminar/retirar
  el modelo Miembro). Ambas piezas están acopladas.

### Decisión de diseño pendiente (bloqueante)

`EstadoMiembro` y `TipoMiembro` **no tienen columna `codigo`** (solo `nombre`),
pero código y migraciones la asumen (`Miembro.es_simpatizante` usa
`tipo_miembro.codigo == 'SIMPATIZANTE'`; `EstadoMiembro.__repr__` usa
`self.codigo`). Hay que decidir: (a) añadir `codigo` a esos catálogos y semilla
canónica, o (b) identificar por `nombre` en todo el código. La elección condiciona
la reconducción.

⚠️ **`p2` no debe aplicarse en producción hasta cerrar la reconducción**, porque
renombra `miembros`→`miembros_legacy` y deja sin tabla al código que aún usa
`Miembro`.

## RGPD (fuera del bundle)

`proteccion_datos` (Consentimiento, SolicitudDerechoRGPD) sigue colgando de
`miembros.id`. Cuando se reapunte a `contacto_id` se reactivarán en `Contacto` las
relaciones inversas `consentimientos_rgpd` / `solicitudes_derechos` y se persistirá
el consentimiento de comunicaciones del formulario público de firmas (hoy no se
guarda por falta de campo).
