---
description: Prepara los worktrees + identidades de los agentes (no abre chats, eso lo haces tú)
---

Prepara la infraestructura de worktrees del entorno multi-agente. Esto NO abre chats: crea las
carpetas y la identidad de cada agente para que el usuario abra un chat apuntando a cada una.

1. Decide qué módulos preparar:
   - sin argumentos → los de por defecto (`economico membresia actividades`)
   - `$ARGUMENTS` con nombres → solo esos
   - `--todos` → los 10 módulos backend
2. Ejecuta `bash scripts/montar-agentes.sh $ARGUMENTS`.
3. Muestra al usuario la salida final (la lista «abre un chat en cada carpeta») y recuérdale:
   - que el árbol principal `/opt/docker/apps/SIGA` es el **integrador**,
   - que cada `../SIGA-wt/<modulo>` es el agente de ese módulo,
   - que el **buzón** es un chat aparte (cualquier carpeta) al que le dice «eres el buzón».
4. Si el usuario quiere añadir más módulos luego, basta con volver a ejecutar el script con esos
   nombres; es idempotente.

Reglas y roles completos en `.claude/PROTOCOLO_MULTIAGENTE.md`.

$ARGUMENTS
