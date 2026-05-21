#!/bin/bash
# Aplica el refactor de la fase 3 en local.
# Ejecutar desde la raíz del repo con la rama refactor/coherencia-modulos activa.

set -e
SERVICES="backend/app/modules/economico/services"
GRAPHQL="backend/app/graphql"
PATCHES="docs/patches"

echo "==> Restaurando servicios económicos desde master..."
git checkout master -- \
  $SERVICES/tesoreria_service.py \
  $SERVICES/recibo_service.py \
  $SERVICES/cuota_service.py \
  $SERVICES/donacion_service.py \
  $GRAPHQL/economico_mutations.py

echo "==> Añadiendo métodos nuevos a los servicios..."
cat $PATCHES/tesoreria_service_nuevos_metodos.py >> $SERVICES/tesoreria_service.py
cat $PATCHES/recibo_service_nuevos_metodos.py    >> $SERVICES/recibo_service.py
cat $PATCHES/cuota_service_nuevos_metodos.py     >> $SERVICES/cuota_service.py
cat $PATCHES/donacion_service_nuevos_metodos.py  >> $SERVICES/donacion_service.py

echo "==> Ensamblando resolver refactorizado..."
cat \
  $PATCHES/economico_mutations_refactored_seg1a_tipos.py \
  $PATCHES/economico_mutations_refactored_seg1a_clase.py \
  $PATCHES/economico_mutations_refactored_seg1b.py \
  $PATCHES/economico_mutations_refactored_seg2.py \
  $PATCHES/economico_mutations_refactored_seg3.py \
  $PATCHES/economico_mutations_refactored_seg4.py \
  > $GRAPHQL/economico_mutations.py

echo "==> Verificando sintaxis Python..."
python3 -c "
import ast, sys
files = [
    '$SERVICES/tesoreria_service.py',
    '$SERVICES/recibo_service.py',
    '$SERVICES/cuota_service.py',
    '$SERVICES/donacion_service.py',
    '$GRAPHQL/economico_mutations.py',
]
ok = True
for f in files:
    try:
        ast.parse(open(f).read())
        print(f'OK  {f}')
    except SyntaxError as e:
        print(f'ERR {f}: {e}')
        ok = False
sys.exit(0 if ok else 1)
"

echo "==> Listo. Revisar cambios con: git diff --stat"
