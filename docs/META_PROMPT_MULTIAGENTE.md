# Meta-prompt: montar un entorno multi-agente en paralelo (portable)

Este documento es un **meta-prompt**: cópialo y pégalo (la sección "PROMPT" de abajo) en un chat
de Claude Code abierto en la raíz de **cualquier** repo que quieras preparar para trabajo
multi-agente en paralelo. Ese Claude actuará de *bootstrapper*: explora el repo, detecta sus
módulos y zonas calientes, y genera toda la infraestructura de coordinación (protocolo, bandejas,
comandos, script de worktrees). No escribe features; monta el andamiaje.

Está basado en el tinglado real de SIGA, pero **no asume SIGA**: descubre la estructura del repo
que tenga delante. Donde veas `<...>` es un placeholder que el bootstrapper rellena.

---

## Qué monta (resumen del diseño)

- **Aislamiento por git worktrees**: un worktree + rama `feature/<modulo>` por agente de módulo.
  Aísla en disco sin duplicar el `.git`. Comparten un único stack dev (no se arranca uno por worktree).
- **Agente integrador dedicado**: el único que toca "zonas calientes" (ficheros que todos los
  módulos necesitan: router/schema/registro/migraciones/componentes comunes), mergea ramas a la
  rama principal y corre migraciones. Serializa el conflicto en un punto.
- **Buzón con cola en ficheros**: un chat recibe las notas desordenadas del usuario, las clasifica
  por módulo y las encola en `.claude/inbox/<modulo>.md`. Reverse proxy humano→agente.
- **Identidad por worktree**: cada worktree tiene `.claude/AGENTE.local.md` (gitignored) con su rol.

### Cuatro roles
- **Agente de módulo** (N): trabaja solo en su módulo, en su worktree/rama. Pide cableado al integrador.
- **Integrador** (1): zonas calientes, merges, migraciones, stack dev. Vive en la rama principal.
- **Buzón** (1): clasifica y encola; no toca código.
- **Tú**: abres los chats (uno por rol/módulo) y diriges. **Los agentes no se autoinstancian**:
  cada agente = un chat que tú abres apuntando a su carpeta.

---

## PROMPT (cópialo a partir de aquí)

> Eres el **agente de arranque (bootstrapper)** de un entorno de trabajo multi-agente en paralelo
> para ESTE repositorio. Tu trabajo NO es escribir features: es montar la infraestructura de
> coordinación para que varios chats de Claude Code (uno por módulo, más un integrador y un buzón)
> trabajen a la vez sin pisarse. Sigue estas cinco fases. Pregunta cuando una decisión sea del
> usuario; usa los valores recomendados como defaults.
>
> ### Fase 1 — Descubrimiento (solo lectura)
> Explora el repo y determina:
> 1. **Modularización backend**: ¿hay un directorio de módulos (`modules/`, `domains/`, `apps/`,
>    `packages/`)? Lista los módulos. ¿Cada uno es autocontenido (models/services/etc.) o hay
>    muchos imports cruzados?
> 2. **Modularización frontend** (si lo hay): ¿organización por módulo/feature o plana? ¿Hay una
>    carpeta de componentes compartidos (`components/common`, `shared/`, `ui/`)?
> 3. **Zonas calientes** = ficheros que CUALQUIER módulo necesita tocar. Búscalos por patrón:
>    - punto de entrada / arranque (`main.*`, `app.*`, `index.*`, `server.*`)
>    - router/rutas agregadas (`router`, `routes`, `urls.py`)
>    - schema/API raíz que agrega todos los módulos (`schema`, `graphql`, `api`)
>    - registro de módulos/permisos/plugins (`registry`, `catalog`, `__init__` agregadores)
>    - migraciones de BD (¿cadena lineal compartida? `alembic/`, `migrations/`, `prisma/`)
>    - estado/estilos/componentes compartidos del frontend
>    - modelos base / mixins compartidos
> 4. **Stack dev**: cómo se arranca (docker-compose, Makefile, scripts, `npm run dev`). Puertos.
>    **¿La base de datos es única y compartida?** (crítico: si N worktrees migran contra la misma
>    BD se pisan → el integrador será el único que migre).
> 5. **Migraciones**: ¿cuántos heads hay? ¿la cadena está sana? (no la arregles, solo diagnostica).
> 6. **Convención de commits**: mira `git log --oneline -30`. ¿Hay formato `tipo(scope): …`?
>    Se reutilizará: scope = módulo, como mecanismo de atribución de quién tocó qué.
>
> Resume todo en una tabla de "módulos y lo que posee cada uno" + una lista de "zonas calientes".
>
> ### Fase 2 — Decisiones (con defaults recomendados)
> Confirma con el usuario (con `AskUserQuestion` si tu entorno lo permite), proponiendo el default:
> - **Aislamiento** → *git worktrees* (recomendado). Alternativas: ramas en el mismo árbol (solo
>   sirve por turnos), o clones separados (duplican espacio).
> - **Zonas calientes** → *agente integrador dedicado* (recomendado). Alternativa: locks por
>   convención, o refactor a registro dinámico (más trabajo previo).
> - **Buzón** → *cola en ficheros* en `.claude/inbox/` (recomendado). Alternativa: GitHub Issues.
> - **Cuántos módulos arrancar ya** → 2-3 para rodar el flujo antes de escalar.
>
> ### Fase 3 — Generación
> Crea estos ficheros (plantillas literales más abajo, sustituyendo los `<...>` con lo descubierto):
> - `.claude/PROTOCOLO_MULTIAGENTE.md` — reglas, roles, mapa de ownership, zonas calientes.
> - `.claude/inbox/_README.md` + una bandeja `<modulo>.md` por módulo + `integrador.md` + `_triage_log.md`.
> - `.claude/commands/{inbox,pedir-cableado,triaje,integrar,montar-agentes}.md` — comandos slash.
> - `scripts/montar-agentes.sh` — crea worktrees + escribe `AGENTE.local.md` de cada uno.
> - Edita `.gitignore`: añade el directorio de worktrees (`<repo>-wt/`) y `.claude/AGENTE.local.md`.
> - Si hay CI y apunta a rutas inexistentes, corrígelo (que valide los módulos de verdad).
>
> ### Fase 4 — Arranque
> Ejecuta `bash scripts/montar-agentes.sh <modulo1> <modulo2> <modulo3>` para los módulos elegidos.
> Muestra al usuario la lista "abre un chat en cada carpeta". Recuérdale que **él** abre los chats
> (los agentes no se autoinstancian) apuntando cada uno a su worktree, y que el integrador es el
> chat en la raíz del repo.
>
> ### Fase 5 — Verificación
> Comprueba y reporta:
> - `git worktree list` muestra la raíz + un worktree por módulo en su rama `feature/<modulo>`.
> - Editar un fichero en un worktree no aparece en otro (aislamiento físico).
> - Dry-run del buzón: clasifica una nota de prueba y aparece un `[ABIERTO]` en la bandeja correcta
>   y una fila en `_triage_log.md`.
> - Los comandos slash son invocables y el `AGENTE.local.md` de cada worktree tiene su rol.

---

## Plantillas literales (las usa el bootstrapper en la Fase 3)

> Estas son las plantillas mínimas. El bootstrapper las adapta a la estructura real del repo
> descubierta en la Fase 1. Los `<...>` son placeholders.

### `.claude/PROTOCOLO_MULTIAGENTE.md`

```markdown
# Protocolo de trabajo multi-agente en paralelo — <NOMBRE_REPO>

> Léeme al empezar cada sesión. Fuente de verdad de cómo colaboran varios agentes sin pisarse.

## 0. Al arrancar
1. Lee `.claude/AGENTE.local.md` para saber tu ROL (modulo|integrador|buzon) y MODULO.
2. modulo → `/inbox`; integrador → `/integrar`; buzon → espera notas y usa `/triaje`.

## 1. Roles
- Agente de módulo (N): worktree `<repo>-wt/<modulo>`, rama `feature/<modulo>`. Solo toca su módulo.
  Pide cableado al integrador para zonas calientes. No mergea, no migra, no arranca su stack.
- Integrador (1): rama principal. Único que toca zonas calientes, mergea y migra.
- Buzón (1): clasifica y encola notas del usuario. No toca código.

## 2. Mapa de propiedad (ownership)
| Módulo | Posee (edita libre) | Resolver/API (posee el fichero, no su registro) |
|---|---|---|
| <modulo> | <rutas backend+frontend de ese módulo> | <fichero(s) de resolver/api> |
| ... | ... | ... |

## 3. Zonas calientes (NINGÚN agente de módulo las edita — se piden con /pedir-cableado)
<lista de ficheros: entrypoint, router raíz, schema/api raíz, registro de módulos/permisos,
 migraciones, modelos/estados compartidos, componentes/estado/estilos comunes>

## 4. Flujo de un agente de módulo
status → /inbox → desarrolla solo lo suyo → ¿zona caliente? /pedir-cableado → commit `tipo(<modulo>): …`
→ marca [HECHO] con el hash. Nunca mergea, nunca `<comando de migración> upgrade`, nunca arranca su stack.

## 5. Commits
`tipo(scope): descripción`. scope = tu módulo SIEMPRE (es la atribución). Tipos: feat/fix/refactor/chore/docs.

## 6. Reglas duras
- BD única compartida → SOLO el integrador aplica migraciones. Los módulos pueden CREAR migraciones,
  no aplicarlas. Heads divergentes los reconcilia el integrador.
- Un solo stack dev (puertos <PUERTO_BACK>/<PUERTO_FRONT>), gestionado por el integrador.

## 7. Buzón
Usuario → buzón (/triaje) → `.claude/inbox/<modulo>.md`. Cableados → `.claude/inbox/integrador.md`.
```

### `.claude/inbox/_README.md`, bandejas, y comandos

Usa exactamente la misma estructura que este repo de referencia (SIGA):
- `_README.md` define el formato de bloque `[ABIERTO]→[EN CURSO]→[HECHO]` y el de cableado
  `[PENDIENTE]→[CABLEADO]`, más la regla append-only.
- una bandeja `<modulo>.md` por módulo, una `integrador.md`, y `_triage_log.md` (tabla de auditoría).
- comandos `inbox`, `pedir-cableado`, `triaje`, `integrar`, `montar-agentes` con el frontmatter
  `--- description: … ---` y el cuerpo de instrucciones para ese rol.

> El contenido íntegro de referencia de cada uno está en el repo SIGA bajo `.claude/`. El
> bootstrapper puede leerlos de ahí si tiene acceso, o regenerarlos siguiendo las descripciones de
> este meta-prompt (son cortos y autodescriptivos).

### `scripts/montar-agentes.sh`

Script bash idempotente que:
1. detecta la raíz del repo y define `WT_BASE="<dir-padre>/<nombre-repo>-wt"`.
2. acepta módulos por argumento (o un default de 2-3, o `--todos`).
3. marca la raíz como integrador (escribe su `.claude/AGENTE.local.md` con `ROL=integrador`).
4. por cada módulo: `git worktree add "$WT_BASE/<m>" -b feature/<m> <rama-principal>` (reutiliza si
   ya existe) y escribe `<wt>/.claude/AGENTE.local.md` con `ROL=modulo` y `MODULO=<m>`.
5. imprime la lista "abre un chat en cada carpeta".

(Plantilla completa en el repo SIGA: `scripts/montar-agentes.sh`.)

---

## Notas de portabilidad

- **No-monorepo / sin "módulos" claros**: si el repo no está modularizado, el bootstrapper debe
  decirlo y proponer dividir por *carpetas de alto nivel* o por *features*, o avisar de que el
  trabajo multi-agente paralelo aporta poco hasta modularizar.
- **Sin GraphQL / sin Alembic / sin Docker**: las "zonas calientes" y el "comando de migración" se
  sustituyen por los equivalentes del stack (REST router, Django/Prisma migrations, etc.). El
  principio no cambia: lo que agrega o enruta TODOS los módulos es zona caliente del integrador.
- **CI**: si existe, que valide los módulos reales; si no, el tinglado funciona igual pero el
  integrador pierde la red de seguridad automática antes de mergear.
- **Los agentes no se autoinstancian**: este andamiaje es pasivo. Cada agente es un chat que el
  usuario abre apuntando a la carpeta correcta; el protocolo solo lo coordina.
```
