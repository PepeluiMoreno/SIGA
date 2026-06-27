# Guía rápida: cómo usar el trabajo en paralelo (sin tecnicismos)

> Si solo quieres trabajar como siempre, **ignora esto**: abre un chat normal y ya está.
> Esta guía es para el día que quieras tener **varios chats currando a la vez**.

## La idea en 3 frases
- Tu proyecto se divide en **salas** (módulos: económico, miembros, actividades…).
- Cada sala trabaja en lo suyo y no pisa a las demás.
- Un **jefe** (el integrador) junta el trabajo de todos. Un **buzón** recoge tus quejas y las reparte.

## Dos formas de hacerlo (elige la que te apetezca)

**Opción A — 1 sola ventana (cómoda, recomendada).** No abres una ventana de VSCode por sala.
Abres **un solo chat** en la carpeta de siempre (`/opt/docker/apps/SIGA`) y escribes:

```
/orquestar
```

Ese chat hace de jefe **y** reparte el trabajo: lanza por dentro un "operario" por cada sala que
tenga tareas pendientes, todos a la vez, cada uno en su carril. Cuando acaban, ese mismo chat lo
junta todo. Tú solo miras una ventana. (Las tareas las coge de las bandejas, igual que siempre;
puedes llenarlas antes con el buzón.)

**Opción B — una ventana por sala (la de toda la vida).** Si prefieres ver cada operario en su
propia ventana, abres un chat por carpeta y le dices `/inbox`. Es lo que se explica en el resto
de esta guía. Las dos opciones usan las mismas reglas y son intercambiables.

---

## Ejemplo completo: "el botón de exportar recibos no filtra por fecha"

Sigue estos pasos. Es un caso real de principio a fin.

### Paso 1 — Sueltas la queja en el buzón
Abre un chat (cualquiera vale) y escribe:

> Eres el buzón. Usa /triaje. Nota: el botón de exportar recibos no filtra por fecha, se baja todo.

El buzón decide que eso es del módulo **económico** y lo apunta en una lista de tareas
(`.claude/inbox/economico.md`). Tú no haces nada más. Ya está encolado.

> 💡 Puedes soltarle al buzón 5 quejas seguidas de cosas distintas; él las reparte cada una a su sala.

### Paso 2 — El operario de económico coge la tarea
Abre **otro chat**, y al abrirlo elige la carpeta:

```
/opt/docker/apps/SIGA-wt/economico
```

(esa carpeta ya existe, la creé yo). Ese chat sabe que es "el de económico". Le dices:

> /inbox

Lee su lista, ve la tarea del botón de recibos, y se pone a arreglarla. **Solo toca cosas de
económico**, así que no puede romperte nada de otra sala.

### Paso 3 — Si necesita tocar algo "común", lo pide (no lo toca)
A veces el arreglo necesita cambiar una pieza compartida (un menú, una ruta, la base de datos).
El operario **no la toca**: deja una nota para el jefe con `/pedir-cableado`. Tú no haces nada;
es automático.

### Paso 4 — El jefe junta el trabajo
Cuando el operario termina, abre un chat en la carpeta de siempre:

```
/opt/docker/apps/SIGA
```

y le dices:

> /integrar

El jefe revisa lo que hicieron los operarios, lo une todo, toca las piezas comunes que le
pidieron, y deja el proyecto actualizado. **Solo el jefe hace esto** (así nada choca).

---

## Chuleta de "quién es quién"

| Quiero… | Abro un chat en… | Y le digo… |
|---|---|---|
| **Que trabajen TODAS las salas sin abrir N ventanas** | `SIGA` (la de siempre) | **"/orquestar"** |
| Soltar una queja/mejora | cualquier carpeta | "eres el buzón, /triaje, [tu queja]" |
| Que trabajen el módulo económico (una ventana) | `SIGA-wt/economico` | "/inbox" |
| Que trabajen miembros (una ventana) | `SIGA-wt/membresia` | "/inbox" |
| Que trabajen actividades (una ventana) | `SIGA-wt/actividades` | "/inbox" |
| Juntar todo el trabajo | `SIGA` (la de siempre) | "/integrar" |

## Tres cosas y ya
1. **No estás obligado.** Si abres un chat normal en la carpeta de siempre, todo funciona como antes.
2. **Cada chat sabe quién es** por dónde lo abriste. No tienes que explicárselo.
3. **¿Quieres más salas?** Dile a cualquier chat: "monta el agente de secretaría" (`/montar-agentes secretaria`).

## Local vs. GitHub (importante)
Todo este baile de ramas ocurre **en tu ordenador**. En GitHub solo hay `master`.
- Las ramas `feature/economico`, etc. **viven solo en local**, no se suben.
- **GitHub no recibe nada hasta que TÚ pides subir `master`** (un `git push`). Y master sube
  ya integrado y limpio. Ningún chat sube nada por su cuenta.

---

# CHULETARIO — lo que tú tecleas

> "Prompt" = se lo dices a un chat con tus palabras. "Comando" = lo escribes empezando por `/`.

### A) Soltar un fallo o mejora (lo más habitual)
Abre un chat cualquiera y escribe (prompt):
```
Eres el buzón. Usa /triaje.
Nota: <aquí tu queja tal cual, p.ej. "el botón de exportar recibos no filtra por fecha">
```
Puedes encadenar varias quejas seguidas; las reparte cada una a su sala.

### B) Poner a trabajar a TODOS los módulos sin abrir más ventanas (recomendado)
Abre **un solo chat** en la carpeta principal `SIGA` y escribe (comando):
```
/orquestar
```
Ese chat lanza por dentro un operario por cada sala con tareas, todos a la vez, y luego junta el
trabajo él mismo. Una ventana, varios operarios. No tienes que abrir nada más.

### B-bis) Poner a trabajar UN módulo en su propia ventana (modo clásico)
Abre un chat **en la carpeta de ese módulo** y escribe (comando):
```
/inbox
```
Carpetas: `SIGA-wt/economico`, `SIGA-wt/membresia`, `SIGA-wt/actividades`.
(El chat ya sabe quién es por la carpeta; solo lee su lista y se pone.)

### C) Juntar todo el trabajo (integrar)
Abre un chat **en la carpeta principal `SIGA`** y escribe (comando):
```
/integrar
```
Él fusiona las ramas terminadas en `master`, toca las piezas comunes y aplica migraciones.

### D) Subir a GitHub (cuando TÚ quieras)
En la carpeta principal `SIGA`, con master ya integrado, escribe (prompt):
```
Sube master a GitHub.
```
(O el comando git directo: `git push origin master`.) Esto es lo único que llega al remoto.

### E) Añadir una sala nueva (otro módulo)
En cualquier chat (prompt o comando):
```
/montar-agentes secretaria
```
Crea la carpeta `SIGA-wt/secretaria` lista para abrir su chat.

### F) Comandos git útiles (si quieres mirar tú mismo)
```
git worktree list                          # qué salas/carpetas hay y en qué rama
git log master..feature/economico --oneline   # qué ha hecho económico y master aún no tiene
git branch                                  # ramas en local
git branch -r                               # ramas en GitHub (solo verás master)
```

---

## ¿Me he perdido?
Dile a cualquier chat: *"léete .claude/PROTOCOLO_MULTIAGENTE.md y recuérdame cómo funciona esto"*.
Él te lo explica con el detalle que quieras.
