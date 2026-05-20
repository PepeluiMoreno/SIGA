"""Seed: cierre contable de los ejercicios 2009-2025.

Para cada ejercicio, en orden cronológico, genera:
  1. Asiento de REGULARIZACIÓN — salda grupos 6 y 7 contra la cta 129 (excedente).
  2. Asiento de CIERRE — salda todas las cuentas de balance (quedan a cero).
  3. Asiento de APERTURA del ejercicio siguiente — reabre los saldos.

El ejercicio 2026 queda abierto (en curso). Reutiliza CierreEjercicioService.

Pre-condiciones que el script prepara:
  - D8.4: concilia todos los apuntes de caja hasta 2025.
  - D9.3: confirma cualquier asiento que quedara en BORRADOR.

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_cierre_ejercicios
"""
import asyncio

from sqlalchemy import text

from app.core.database import async_session
from app.modules.economico.services.cierre_service import CierreEjercicioService

EJ_INICIAL = 2009
EJ_FINAL = 2025  # 2026 queda abierto


async def seed():
    async with async_session() as session:
        # D8.4 — conciliar todos los apuntes de caja de los ejercicios a cerrar.
        r1 = await session.execute(text(
            "UPDATE apuntes_caja SET conciliado=true "
            "WHERE fecha < '2026-01-01' AND conciliado=false"
        ))
        # D9.3 — no puede quedar ningún asiento en BORRADOR.
        r2 = await session.execute(text(
            "UPDATE asientos_contables SET estado='CONFIRMADO' "
            "WHERE estado='BORRADOR' AND ejercicio<=:ej"
        ), {"ej": EJ_FINAL})
        await session.commit()
        print(f"Preparación: {r1.rowcount} apuntes conciliados, "
              f"{r2.rowcount} borradores confirmados.")

        svc = CierreEjercicioService(session)
        cerrados, fallidos = 0, 0

        for ej in range(EJ_INICIAL, EJ_FINAL + 1):
            try:
                await svc.generar_asiento_regularizacion(ej)
                await svc.generar_asiento_cierre(ej)
                await svc.generar_asiento_apertura(ej + 1)
                await session.commit()
                cerrados += 1
                print(f"  ✓ Ejercicio {ej} cerrado (regularización + cierre + apertura {ej + 1}).")
            except Exception as e:  # noqa: BLE001
                await session.rollback()
                fallidos += 1
                print(f"  ⚠ Ejercicio {ej}: {e}")

        print(f"\n✓ Cierre completado: {cerrados} ejercicios cerrados, {fallidos} con incidencias. "
              f"2026 queda abierto.")


if __name__ == "__main__":
    asyncio.run(seed())
