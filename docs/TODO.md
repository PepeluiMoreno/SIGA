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
