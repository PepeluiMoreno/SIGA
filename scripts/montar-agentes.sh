#!/usr/bin/env bash
#
# montar-agentes.sh — prepara el entorno multi-agente de SIGA.
#
# Crea un git worktree por cada módulo indicado (rama feature/<modulo>) y escribe en cada uno
# su .claude/AGENTE.local.md con su identidad. También deja listo el árbol principal como
# INTEGRADOR. NO arranca chats: tú abres un chat de Claude Code apuntando a cada carpeta.
#
# Uso:
#   ./scripts/montar-agentes.sh                      # módulos por defecto (economico membresia actividades)
#   ./scripts/montar-agentes.sh economico membresia  # solo esos
#   ./scripts/montar-agentes.sh --todos              # los 10 módulos backend
#
# Idempotente: si un worktree ya existe, lo respeta y solo reescribe su AGENTE.local.md.

set -euo pipefail

# Raíz del repo (este script vive en scripts/)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WT_BASE="$(dirname "$REPO_ROOT")/$(basename "$REPO_ROOT")-wt"   # p.ej. /opt/docker/apps/SIGA-wt

TODOS_LOS_MODULOS=(acceso actividades administracion configuracion core economico membresia organizaciones proteccion_datos secretaria)
DEFAULT_MODULOS=(economico membresia actividades)

# --- parseo de argumentos ---
if [[ $# -eq 0 ]]; then
  MODULOS=("${DEFAULT_MODULOS[@]}")
elif [[ "${1:-}" == "--todos" ]]; then
  MODULOS=("${TODOS_LOS_MODULOS[@]}")
else
  MODULOS=("$@")
fi

cd "$REPO_ROOT"

echo "▸ Repo:        $REPO_ROOT"
echo "▸ Worktrees:   $WT_BASE/<modulo>"
echo "▸ Módulos:     ${MODULOS[*]}"
echo

# --- 1. El árbol principal es el INTEGRADOR ---
mkdir -p "$REPO_ROOT/.claude"
cat > "$REPO_ROOT/.claude/AGENTE.local.md" <<'EOF'
# Identidad de este agente (NO versionar)
ROL=integrador
MODULO=-
RAMA=master

Soy el integrador. Único que toca zonas calientes, mergea ramas y corre migraciones.
Al arrancar, ejecuto /integrar. Reglas en .claude/PROTOCOLO_MULTIAGENTE.md.
EOF
echo "✓ árbol principal marcado como INTEGRADOR (master)"

# --- 2. Un worktree por módulo ---
mkdir -p "$WT_BASE"
for m in "${MODULOS[@]}"; do
  wt_dir="$WT_BASE/$m"
  rama="feature/$m"

  if git worktree list --porcelain | grep -qx "worktree $wt_dir"; then
    echo "• $m: worktree ya existe en $wt_dir (lo respeto)"
  else
    # crea la rama desde master si no existe; reutiliza si ya existe
    if git show-ref --verify --quiet "refs/heads/$rama"; then
      git worktree add "$wt_dir" "$rama"
    else
      git worktree add "$wt_dir" -b "$rama" master
    fi
    echo "✓ $m: worktree creado en $wt_dir (rama $rama)"
  fi

  # escribe su identidad (idempotente)
  mkdir -p "$wt_dir/.claude"
  cat > "$wt_dir/.claude/AGENTE.local.md" <<EOF
# Identidad de este agente (NO versionar)
ROL=modulo
MODULO=$m
RAMA=$rama

Soy el agente del módulo "$m". Edito SOLO ficheros de mi módulo (ownership en
.claude/PROTOCOLO_MULTIAGENTE.md §2). Para zonas calientes uso /pedir-cableado.
Al arrancar, ejecuto /inbox. No mergeo, no corro alembic upgrade, no arranco mi propio stack.
EOF
done

echo
echo "▸ Estado de worktrees:"
git worktree list
echo
echo "════════════════════════════════════════════════════════════════════"
echo " LISTO. Ahora abre un chat de Claude Code en cada carpeta:"
echo
echo "   INTEGRADOR →  $REPO_ROOT"
for m in "${MODULOS[@]}"; do
  printf "   %-10s →  %s\n" "$m" "$WT_BASE/$m"
done
echo
echo " El BUZÓN puede ser un chat en cualquier carpeta (no toca código);"
echo " márcalo a mano creando .claude/AGENTE.local.md con ROL=buzon, o"
echo " simplemente dile al chat: «eres el buzón, usa /triaje»."
echo "════════════════════════════════════════════════════════════════════"
