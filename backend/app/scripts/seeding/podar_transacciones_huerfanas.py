"""Poda las transacciones HUÉRFANAS: las que existen en BD pero cuyo código ya no
declara ningún catalog.py (residuo de catálogos viejos).

CatalogSyncService crea/actualiza transacciones desde los catálogos, pero NUNCA
borra las que desaparecieron del código. Con el tiempo la BD acumula transacciones
legacy (p. ej. staging tenía 343 vs 174 declaradas). Este script las identifica
comparando contra la fuente de verdad (ModuleCatalog) y las elimina junto con sus
enlaces (roles_transacciones, funcionalidades_transacciones, flujos_aprobacion).

Por seguridad:
  - DRY-RUN por defecto: solo lista lo que borraría. Pasar `--aplicar` para borrar.
  - Importa TODOS los catálogos antes de calcular el set vigente (si faltara uno,
    sus transacciones se verían como huérfanas por error).

Uso:
  # ver qué se borraría (no toca nada):
  docker compose ... exec backend python -m app.scripts.seeding.podar_transacciones_huerfanas
  # aplicar:
  docker compose ... exec backend python -m app.scripts.seeding.podar_transacciones_huerfanas --aplicar
"""
from __future__ import annotations

import asyncio
import sys

from sqlalchemy import select, delete

from app.core.database import async_session
from app.modules.acceso.services.registry import ModuleCatalog
from app.modules.acceso.models.transaccion import Transaccion
from app.modules.acceso.models.rol_transaccion import RolTransaccion
from app.modules.acceso.models.funcionalidad import FuncionalidadTransaccion, FlujoAprobacion


def _cargar_todos_los_catalogos() -> None:
    """Importa los catalog.py de todos los módulos (efecto secundario: se registran).
    DEBE incluir TODOS para no marcar transacciones vigentes como huérfanas."""
    import importlib
    modulos = [
        "acceso", "membresia", "actividades", "economico",
        "configuracion", "proteccion_datos", "secretaria", "presidencia",
    ]
    for m in modulos:
        try:
            importlib.import_module(f"app.modules.{m}.catalog")
        except ImportError:
            pass


async def main() -> int:
    aplicar = "--aplicar" in sys.argv
    _cargar_todos_los_catalogos()

    vigentes = {t.codigo for t in ModuleCatalog.get_transacciones()}
    if not vigentes:
        print("ABORTADO: no se cargó ningún catálogo (set vigente vacío). No borro nada.", file=sys.stderr)
        return 2
    print(f"Transacciones declaradas en código (catálogos): {len(vigentes)}")

    async with async_session() as session:
        todas = (await session.execute(select(Transaccion))).scalars().all()
        huerfanas = [t for t in todas if t.codigo not in vigentes]
        print(f"Transacciones en BD: {len(todas)} · huérfanas (no declaradas): {len(huerfanas)}")

        if not huerfanas:
            print("Nada que podar. BD = catálogo.")
            return 0

        # Agrupa por prefijo para revisión rápida.
        por_prefijo: dict[str, int] = {}
        for t in huerfanas:
            por_prefijo[t.codigo.split("_")[0]] = por_prefijo.get(t.codigo.split("_")[0], 0) + 1
        print("Huérfanas por prefijo:")
        for pref, n in sorted(por_prefijo.items(), key=lambda x: -x[1]):
            print(f"  {pref:14s} {n}")
        print("Códigos huérfanos:")
        for t in sorted(huerfanas, key=lambda x: x.codigo):
            print(f"  - {t.codigo}")

        if not aplicar:
            print("\n[DRY-RUN] No se ha borrado nada. Re-ejecuta con --aplicar para podar.")
            return 0

        ids = [t.id for t in huerfanas]
        # Borra primero los enlaces (roles_transacciones y funcionalidades_transacciones
        # tienen ondelete CASCADE, pero los limpiamos explícitamente por claridad y
        # porque flujos_aprobacion es RESTRICT/SET NULL).
        await session.execute(delete(RolTransaccion).where(RolTransaccion.transaccion_id.in_(ids)))
        await session.execute(delete(FuncionalidadTransaccion).where(FuncionalidadTransaccion.transaccion_id.in_(ids)))
        # flujos_aprobacion: si alguna huérfana es referenciada por un flujo, abortar
        # (RESTRICT) para no romper un flujo de aprobación silenciosamente.
        flujos = (await session.execute(
            select(FlujoAprobacion).where(
                FlujoAprobacion.transaccion_inicio_id.in_(ids)
                | FlujoAprobacion.transaccion_aprobacion_id.in_(ids)
                | FlujoAprobacion.transaccion_rechazo_id.in_(ids)
            )
        )).scalars().all()
        if flujos:
            print(f"\n⚠ {len(flujos)} flujo(s) de aprobación referencian transacciones huérfanas; "
                  "revísalos antes de podar. No borro nada.", file=sys.stderr)
            await session.rollback()
            return 3

        await session.execute(delete(Transaccion).where(Transaccion.id.in_(ids)))
        await session.commit()
        print(f"\n✓ Podadas {len(huerfanas)} transacciones huérfanas y sus enlaces.")
        return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
