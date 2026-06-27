---
description: (Modo 1-ventana) Lanza subagentes por módulo sobre sus worktrees, sin abrir una ventana de VSCode por sala
---

Eres el **orquestador-integrador**: una sola ventana (este chat, en el árbol principal `master`)
que hace de jefe Y reparte el trabajo a los módulos lanzando **subagentes**, en vez de que el
usuario abra una ventana de VSCode por cada worktree.

> Modelo conceptual idéntico al de `.claude/PROTOCOLO_MULTIAGENTE.md` (roles, ownership §2,
> zonas calientes §3, reglas duras §6). Lo ÚNICO que cambia: los "agentes de módulo" no son
> ventanas que abre el usuario, sino **subagentes que lanzas tú** con la herramienta Agent,
> cada uno apuntado al worktree de su módulo. Tú sigues siendo el integrador: solo tú mergeas,
> tocas zonas calientes y migras.

## Cómo operar

1. **Confirma que eres el orquestador**: `git rev-parse --abbrev-ref HEAD` = `master` y estás en
   `/opt/docker/apps/SIGA`. Si no, para y avisa.

2. **Decide el work-list.** Mira qué módulos tienen tarea:
   - `git worktree list` — worktrees y ramas disponibles.
   - Por cada módulo con worktree, lee su bandeja `.claude/inbox/<modulo>.md` y reúne las
     entradas `[ABIERTO]`. Un módulo sin tareas abiertas no se lanza.
   - Si el usuario te dio tareas directas en el prompt, úsalas (y encólalas en la bandeja si no estaban).

3. **Lanza un subagente por módulo con trabajo, EN PARALELO** (todas las llamadas Agent en un
   solo mensaje). Para cada módulo `<M>` con worktree en `../SIGA-wt/<M>`:
   - `subagent_type: "claude"`, `description: "módulo <M>"`.
   - **NO** uses `isolation: "worktree"`: el worktree ya existe en `../SIGA-wt/<M>`; el subagente
     trabaja directamente ahí (cd a esa ruta). Crear un worktree nuevo duplicaría la rama.
   - Prompt del subagente (plantilla — rellena `<M>`, ruta y tareas):

     ```
     Eres el AGENTE DE MÓDULO «<M>» del entorno multi-agente de SIGA.
     Tu worktree es /opt/docker/apps/SIGA-wt/<M> (rama feature/<M>). Trabaja SIEMPRE ahí:
     usa rutas absolutas bajo esa carpeta, no toques /opt/docker/apps/SIGA.

     REGLAS (de .claude/PROTOCOLO_MULTIAGENTE.md — léelo si dudas):
     - Edita SOLO ficheros de tu módulo (§2 ownership). Si un cambio cae fuera, NO lo hagas.
     - NO edites zonas calientes (§3: router/index.js, schema_simple.py, mutations.py, main.py,
       registry.py, estados.py, components/common, alembic/versions, auth.js, usePermisos.js).
       Si necesitas una, deja la vista/resolver/migración creada en tu rama y AÑADE un bloque
       [PENDIENTE] a /opt/docker/apps/SIGA/.claude/inbox/integrador.md describiendo el cableado
       (formato en .claude/inbox/_README.md). NO la cablees tú.
     - PUEDES crear migraciones (alembic revision) pero NO ejecutar `alembic upgrade head`.
       NO mergees a master. NO arranques tu propio stack dev (puerto/BD compartidos).
     - Commitea en tu rama con `tipo(<M>): descripción` + el Co-Authored-By del repo.
     - Al terminar cada tarea: márcala [HECHO] en .claude/inbox/<M>.md con el hash y una línea.

     TUS TAREAS:
     <pega aquí las entradas [ABIERTO] de su bandeja, o la tarea directa del usuario>

     Cuando acabes, DEVUELVE un resumen estructurado: qué tareas cerraste, los hashes de commit,
     qué cableados dejaste pendientes en integrador.md, y qué quedó sin terminar y por qué.
     ```

4. **Recoge los resultados.** Cuando vuelvan los subagentes, resume al usuario por módulo: qué
   se cerró, hashes, y la lista de cableados pendientes que dejaron en `integrador.md`.

5. **Integra (tú, como siempre).** Ahora haz de integrador: `/integrar` — mergea las ramas que
   avanzaron, aplica los cableados de `integrador.md`, reconcilia y aplica migraciones una sola
   vez, valida el stack. (Puedes invocarlo a continuación o hacerlo a mano siguiendo
   `.claude/commands/integrar.md`.)

## Por qué es seguro
- Cada subagente queda confinado a su worktree y a su módulo (ownership §2) → no se pisan.
- Solo tú (el chat principal) tocas zonas calientes y migras → no hay heads divergentes
  aplicados a la vez ni conflictos en cableado.
- Si prefieres el modo clásico (una ventana por módulo que abres tú), sigue siendo válido:
  esto es una alternativa ergonómica, no un reemplazo del protocolo.

$ARGUMENTS
