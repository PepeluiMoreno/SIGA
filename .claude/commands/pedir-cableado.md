---
description: Formaliza una petición de cableado al integrador (tocar una zona caliente)
---

Necesitas que el **integrador** toque una zona caliente que tú no puedes editar (router raíz,
schema/mutations GraphQL, main.py, registry de permisos, migración, componente común, etc.
— lista completa en `.claude/PROTOCOLO_MULTIAGENTE.md` §3).

NO edites la zona caliente. En su lugar:

1. Lee `.claude/AGENTE.local.md` para tu `MODULO`, y `git rev-parse --abbrev-ref HEAD` para tu rama.
2. Asegúrate de que el trabajo de TU lado ya está hecho y commiteado en tu rama (la vista, el
   resolver, el modelo, la migración que generaste sin aplicar…). El integrador parte de tu rama.
3. Añade (append) un bloque a `.claude/inbox/integrador.md` con este formato exacto:

   ```markdown
   ## [PENDIENTE] <fecha ISO> · de:<MODULO> · rama:feature/<MODULO>
   **Necesito en zona caliente:**
   - <fichero>: <qué cambio concreto> (estado en mi rama: …)
   - …
   **Contexto:** <por qué, qué desbloquea>
   **Tras mergear mi rama**, aplica estos cableados.
   ---
   ```

   Sé MUY concreto en cada línea: fichero exacto, ruta/símbolo a añadir, y dónde está ya hecho
   lo tuyo (nombre de la vista/resolver y que está commiteado). El integrador no debe adivinar.
4. Reemplaza `<fecha ISO>` por la fecha/hora real (pídela con `date -Iseconds` si la necesitas).
5. Avisa al usuario de que la petición quedó encolada para el integrador.

$ARGUMENTS
