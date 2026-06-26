---
description: Lee tu bandeja de módulo y empieza a trabajar las tareas abiertas
---

Eres un agente de **módulo**. Atiende tu bandeja:

1. Lee `.claude/AGENTE.local.md` para saber tu `MODULO`. Si no existe o tu ROL no es `modulo`,
   dilo y para (este comando es solo para agentes de módulo).
2. Confirma que estás en tu worktree y rama correctos: `git status` debe mostrar `feature/<MODULO>`.
3. Lee `.claude/inbox/<MODULO>.md`. Lista las entradas `[ABIERTO]` y `[EN CURSO]` con su asunto
   y prioridad. Si está vacía, dilo y pregunta al usuario qué quiere que hagas.
4. Si hay tareas, propón en qué orden atacarlas (prioridad alta primero) y empieza por la primera:
   - cámbiala a `[EN CURSO]` en el fichero,
   - resuélvela **solo en ficheros de tu módulo** (ver ownership en `.claude/PROTOCOLO_MULTIAGENTE.md` §2),
   - si necesitas tocar una zona caliente (§3), NO la edites: usa `/pedir-cableado`,
   - al terminar, commitea con `tipo(<MODULO>): …`, marca la entrada `[HECHO]` y añade
     `**Resuelto:** <hash> · <qué hiciste>`.
5. Recuerda las reglas duras: no mergeas a master, no corres `alembic upgrade head`, no arrancas
   tu propio stack dev. Eso es del integrador.

$ARGUMENTS
