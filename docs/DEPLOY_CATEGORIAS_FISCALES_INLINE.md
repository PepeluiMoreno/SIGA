# Instrucciones de despliegue — Categorías fiscales: edición inline

**Rama:** `feature/categorias-fiscales-inline`
**Merge destino:** `master`
**Última actualización:** 2026-05-22

---

## 1. Qué incluye

Refactor de UX puro: migra el panel de categorías fiscales (contabilidad simplificada)
de edición por modal a **edición inline** sobre la fila. Paga la primera deuda técnica
del criterio de edición ágil registrado en `DISENO_PRESUPUESTOS.md`.

- Nombre, color y casilla del modelo editables sobre la fila.
- Interruptores Modelo 182 / 347 y Activa/Inactiva clicables en la fila.
- Alta inline (fila expandible al pie de cada columna).
- Se elimina el modal de crear/editar; se conserva solo el de confirmar borrado.
- Fix menor: borrar la casilla del modelo envía cadena vacía en vez de null
  (el resolver filtraba los null y no permitía borrarla).

---

## 2. Alcance del cambio

**Solo frontend.** Dos archivos:

```
frontend/src/components/common/CategoriasFiscalesPanel.vue   (reescrito)
frontend/src/views/Ayuda.vue                                 (flujo actualizado)
```

**No toca:** backend, base de datos, GraphQL, permisos ni configuración.

---

## 3. Merge y despliegue

```bash
git checkout master && git pull origin master
git merge --no-ff feature/categorias-fiscales-inline
git push origin master
```

**No requiere migraciones, seeds ni reinicio de backend.** Solo rebuild del frontend
en el despliegue habitual:

```bash
cd frontend && npm run build
```

> El backend ya soportaba la actualización parcial de categorías
> (`ACTUALIZAR_CATEGORIA_FISCAL` con input opcional por campo); no hubo que cambiarlo.

---

## 4. Verificación post-deploy

1. Organización en modo contabilidad simplificada → *Económico → Contabilidad → Categorías fiscales*.
2. Editar el nombre de una categoría sobre la fila → se guarda al salir del campo.
3. Activar/desactivar el interruptor Modelo 182 → cambio inmediato.
4. Cambiar el color → se refleja al instante.
5. Escribir y luego borrar la casilla del modelo → ambos cambios persisten.
6. Añadir una categoría con la fila inline (+ Nueva categoría de ingreso/gasto).
7. Sin permiso `ECO_ESTRUCTURA_CONTABLE_GESTIONAR` → todo se ve en solo lectura, sin campos editables.
