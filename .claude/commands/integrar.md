---
description: (Integrador) Mergea ramas de módulo listas, aplica cableados y migra contra la BD compartida
---

Eres el **integrador**. Vives en el árbol principal sobre `master` y eres el ÚNICO que toca
zonas calientes, mergea y migra. Trabaja con cuidado y de forma supervisada.

1. Confirma rol y ubicación: `.claude/AGENTE.local.md` debe decir `ROL=integrador`, y
   `git rev-parse --abbrev-ref HEAD` debe ser `master`. Si no, para y avisa.
2. **Estado del terreno:**
   - `git worktree list` — qué worktrees/ramas hay.
   - `git branch --list 'feature/*'` y, por cada una, `git log master..feature/<x> --oneline`
     para ver qué traería cada merge.
   - Lee `.claude/inbox/integrador.md` — peticiones de cableado `[PENDIENTE]`.
3. **Por cada rama lista para integrar** (confírmalo con el usuario si hay dudas):
   - `git merge --no-ff feature/<modulo>` (o rebase si el repo lo prefiere). Resuelve conflictos
     con criterio: en zonas calientes manda master + lo que pida el bloque de cableado.
   - Aplica los **cableados** que esa rama dejó en `integrador.md`: edita router/index.js,
     schema_simple.py, mutations.py, main.py, registry.py, componentes comunes, etc., según el bloque.
   - Marca cada bloque `[PENDIENTE]` → `[CABLEADO]` con el hash del commit de cableado.
4. **Migraciones (solo aquí):** si alguna rama trajo migraciones en `alembic/versions/`:
   - revisa que la cadena tenga un solo head: `cd backend && uv run alembic heads`.
   - si hay heads divergentes, reconcílialos: `uv run alembic merge -m "merge <a>+<b>"`.
   - aplica una sola vez contra la BD compartida: `uv run alembic upgrade head`.
   - reinicia/valida el backend del stack dev compartido.
5. **Valida que arranca:** levanta o recarga el stack (`docker compose -f docker-compose.dev.yml up`),
   comprueba que el backend importa todos los catalogs sin `ValueError` de duplicados y que el
   frontend buildea. Si el CI está configurado, mira que pase en las ramas.
6. Commitea el cableado con `chore(integracion): …` o `feat(<modulo>): cableado de …` según corresponda.
7. Resume al usuario: qué ramas mergeaste, qué cableé, qué migraciones apliqué, y si algo quedó pendiente.

$ARGUMENTS
