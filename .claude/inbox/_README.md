# Bandejas de entrada (inbox) — coordinación multi-agente

Este directorio es la **cola en ficheros** del entorno multi-agente. No contiene código; son
colas de trabajo en markdown, append-only, que conectan al usuario, al buzón y a los agentes.
Ver el protocolo completo en [`../PROTOCOLO_MULTIAGENTE.md`](../PROTOCOLO_MULTIAGENTE.md).

## Ficheros

| Fichero | Quién escribe | Quién lee |
|---|---|---|
| `<modulo>.md` | el buzón (`/triaje`), o cualquiera dejando una nota | el agente de ese módulo (`/inbox`) |
| `integrador.md` | agentes de módulo (`/pedir-cableado`) | el integrador (`/integrar`) |
| `_triage_log.md` | el buzón (auditoría de cada reparto) | quien quiera revisar el histórico |

Hay una bandeja por módulo de SIGA: `acceso`, `actividades`, `economico`, `membresia`,
`secretaria`, `configuracion`, `proteccion_datos`, `core`, `organizaciones`, `administracion`.
(El frontend `comunicaciones` cae en `core`; `presidencia` cae en `organizaciones`.)

## Formato de una entrada de bandeja de módulo

Una entrada = un bloque. Append al final del fichero. Estados: `[ABIERTO]` → `[EN CURSO]` → `[HECHO]`.

```markdown
## [ABIERTO] 2026-06-26T14:30 · origen:buzón · prioridad:media
**Para:** economico
**Asunto:** El cálculo de cuota prorrateada redondea mal en altas a mitad de mes
**Detalle:** (texto literal de la nota del usuario, sin interpretar de más)
**Pista de ubicación:** backend/app/modules/economico/services/cuota_service.py
---
```

Cuando el agente lo resuelve, edita ese bloque:
- cambia `[ABIERTO]` → `[HECHO]`
- añade una línea `**Resuelto:** <hash-commit> · <una línea de qué se hizo>`

`prioridad` ∈ `alta` | `media` | `baja`. `origen` ∈ `buzón` | `usuario` | `<otro-modulo>`.

## Formato de una petición de cableado (→ `integrador.md`)

```markdown
## [PENDIENTE] 2026-06-26T15:00 · de:economico · rama:feature/economico
**Necesito en zona caliente:**
- router/index.js: añadir ruta `/economico/remesas-sepa` → vista `RemesasSepa.vue` (ya creada en mi rama)
- schema_simple.py: exponer Query `remesasSepa` (resolver en economico_resolvers.py, ya commiteado)
- main.py: ya importa economico.catalog, sin cambios
**Tras mergear mi rama**, aplica estos cableados.
---
```

El integrador, al hacerlo, cambia `[PENDIENTE]` → `[CABLEADO]` y añade el hash del commit de cableado.

## Reglas

- **Append-only**: nunca borres entradas; cámbiales el estado. El histórico es la auditoría.
- **Una nota = un destinatario**: si una nota toca dos módulos, el buzón crea dos entradas
  (una por bandeja) y lo anota en `_triage_log.md`.
- **Texto literal del usuario**: el buzón copia la queja tal cual en `**Detalle:**`; puede
  añadir su interpretación en `**Pista de ubicación:**`, pero no reescribe lo que dijo el usuario.
