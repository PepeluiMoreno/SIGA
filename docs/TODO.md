# TODO — refactors pendientes

## Unificar los modales de confirmación (A)
Hoy conviven dos sistemas + casos aparte:
- **Imperativo** `useConfirm()` + `ConfirmHost` + `ConfirmActionModal` (centralizado, prompt, variantes).
- **Por props** `ConfirmModal` (8 usos, incl. `RowActions`) con checkbox papelera/permanente.
- `ConfirmPopover` (inline) y `BaseModal` (shell) — casos aparte.

**Objetivo:** dejar UNO para todos los flujos = `useConfirm()` + `ConfirmActionModal`,
plegando el checkbox papelera/permanente y migrando los 8 usos de `ConfirmModal`
(borrarlo después). `BaseModal` se queda (shell). `ConfirmPopover`: decidir si se
migra o se conserva por su UX inline.

Pendiente de hacer como pase dedicado (es transversal, merece su PR + pruebas).

## Documentar el modelo CRM contacto-céntrico
Cuando se estabilice el frontend contacto-céntrico, documentar (doc de
arquitectura + procedimiento) las decisiones tomadas:

- **Identidad = `Contacto`** (PF/PJ, STI). "Socio/voluntario" no son entidades:
  son **facetas** = `Vinculacion` tipada (+ satélite Socio/Voluntario).
- **Vector de situación**: el conjunto de vinculaciones vigentes de un contacto
  es lo que lo incluye/excluye de cada vista (filtro por faceta vigente).
- **Capa de compatibilidad**: read-models planos (`socios`→`SocioVista`,
  `voluntariosEnAmbito`→`VoluntarioAmbito`) que reconstruyen el viejo "Miembro"
  para que el frontend antiguo siga funcionando.
- **Tres ejes, separados en datos, unidos en pantalla**:
  1. Vinculaciones (pertenencia: socio, voluntario, donante, firmante…).
  2. Cargos orgánicos (`Cargo`+`CargoRol`+`HistorialNombramiento`): aprobación + RBAC.
  3. Participaciones (actos puntuales).
- **Cargos NO se duplican como vinculaciones**: el vector uniforme se sirve por
  **proyección** en lectura (read-model `situacionDeContacto`), no por espejo
  sincronizado (se descartó la doble escritura por riesgo de deriva).
- **Historiales**: cada eje guarda el suyo (tramos `fecha_inicio/fin`);
  `cerrar` conserva el tramo, `eliminar`=papelera. Cambios de campo → `LogAuditoria`.
- **Decisión pendiente**: consolidar `CoordinacionTerritorial` en
  `HistorialNombramiento(cargo=Coordinador)` (un solo dueño del rol).
- **Contrato GraphQL Fase 1** (commit en rama `claude/crm-contacto-centrico`):
  `VinculacionType`/`SocioType`/`VoluntarioType`, `vinculacionesDeContacto`,
  `crearContacto`/`actualizarContacto`, `altaVinculacionSocio/Voluntario`,
  `cerrarVinculacion`.
- **Rotulación UI / propiedad por faceta**: ver `TipoVinculacion.area_responsable`
  (cada faceta declara su área RBAC responsable).
