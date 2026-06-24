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

## PENDIENTE — migraciones Alembic (NO aplicar todavía)

Dos migraciones escritas y **SIN probar en BD**:

- `s4t5u6v7w8x9` (p1): crea el esquema nuevo (tipos_vinculacion ampliado,
  vinculaciones, socios, voluntarios; firmas_campania.firmante_id → contacto_id).
- `t5u6v7w8x9y0` (p2): migra datos miembros→contactos y **renombra
  `miembros` → `miembros_legacy`** (punto de no retorno).

⚠️ **`p2` no debe aplicarse hasta que la reconducción `Miembro` → `Contacto` esté
completa**, porque al renombrar `miembros` desaparece la tabla sobre la que opera
todo el código que aún usa el modelo `Miembro`. Probar ambas en una BD de staging
desechable antes de tocar nada real.

## RGPD (fuera del bundle)

`proteccion_datos` (Consentimiento, SolicitudDerechoRGPD) sigue colgando de
`miembros.id`. Cuando se reapunte a `contacto_id` se reactivarán en `Contacto` las
relaciones inversas `consentimientos_rgpd` / `solicitudes_derechos` y se persistirá
el consentimiento de comunicaciones del formulario público de firmas (hoy no se
guarda por falta de campo).
