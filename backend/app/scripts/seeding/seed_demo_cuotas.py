"""Plan de cuotas demo (sin volcado): tarifas anuales + cuotas del ejercicio.

Autónomo e idempotente. Inspirado en los importes reales de desarrollo:
  BASE 110/120/130 · General 50 · Joven 5 · Parado 5 · Honorario 0.

Crea:
  1. `importes_cuota_anio` para los ejercicios recientes (tarifas).
  2. `cuotas_anuales` del ejercicio actual para cada socio activo (estado "Alta"),
     repartidas entre Pendiente y Cobrada para que el módulo de cuotas tenga datos.

Ejecutar:
  docker exec <backend> python -m app.scripts.seeding.seed_demo_cuotas
"""
from __future__ import annotations

import asyncio
import random
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.modules.economico.models.cuotas import ImporteCuotaAnio, CuotaAnual
from app.modules.configuracion.models.estados import EstadoCuota
from app.modules.membresia.models.miembro import Miembro
from app.modules.membresia.models.estado_miembro import EstadoMiembro
from app.modules.core.geografico.direccion import UnidadOrganizativa

random.seed(20260529)

EJERCICIOS = [2024, 2025, 2026]
# codigo → (nombre base, importe). BASE varía por año.
TARIFAS = {
    "General":   Decimal("50.00"),
    "Joven":     Decimal("5.00"),
    "Parado":    Decimal("5.00"),
    "Honorario": Decimal("0.00"),
}
BASE_POR_ANIO = {2024: Decimal("110.00"), 2025: Decimal("120.00"), 2026: Decimal("130.00")}
EJERCICIO_ACTUAL = 2026


async def _seed_importes(s: AsyncSession) -> dict[tuple[int, str], ImporteCuotaAnio]:
    creados = 0
    out: dict[tuple[int, str], ImporteCuotaAnio] = {}
    for ej in EJERCICIOS:
        items = dict(TARIFAS)
        items["BASE"] = BASE_POR_ANIO[ej]
        for codigo, importe in items.items():
            existente = (await s.execute(
                select(ImporteCuotaAnio).where(
                    ImporteCuotaAnio.ejercicio == ej,
                    ImporteCuotaAnio.codigo_cuota == codigo,
                )
            )).scalar_one_or_none()
            if existente is None:
                existente = ImporteCuotaAnio(
                    ejercicio=ej, codigo_cuota=codigo, importe=importe,
                    nombre_cuota=f"{codigo} {ej}", activo=True,
                )
                s.add(existente)
                creados += 1
            out[(ej, codigo)] = existente
    await s.flush()
    print(f"  importes_cuota_anio: +{creados} tarifas")
    return out


async def _seed_cuotas_actuales(s: AsyncSession, importes) -> None:
    estados = {e.nombre: e for e in (await s.execute(select(EstadoCuota))).scalars().all()}
    est_pendiente = estados.get("Pendiente")
    est_cobrada = estados.get("Cobrada")
    if not est_pendiente or not est_cobrada:
        print("  ⚠ faltan estados de cuota (Pendiente/Cobrada); omito cuotas anuales")
        return

    estado_alta = (await s.execute(
        select(EstadoMiembro).where(EstadoMiembro.nombre == "Alta")
    )).scalar_one_or_none()
    raiz_id = await s.scalar(
        select(UnidadOrganizativa.id).where(UnidadOrganizativa.agrupacion_padre_id.is_(None))
    )

    q = select(Miembro).where(Miembro.eliminado == False)  # noqa: E712
    if estado_alta:
        q = q.where(Miembro.estado_id == estado_alta.id)
    miembros = (await s.execute(q)).scalars().all()

    imp_general = importes.get((EJERCICIO_ACTUAL, "General"))
    creados = 0
    for m in miembros:
        ya = await s.scalar(
            select(CuotaAnual.id).where(
                CuotaAnual.miembro_id == m.id, CuotaAnual.ejercicio == EJERCICIO_ACTUAL
            )
        )
        if ya:
            continue
        agrup = m.agrupacion_id or raiz_id
        if agrup is None:
            continue
        cobrada = random.random() < 0.6
        s.add(CuotaAnual(
            miembro_id=m.id, ejercicio=EJERCICIO_ACTUAL, agrupacion_id=agrup,
            importe_cuota_anio_id=imp_general.id if imp_general else None,
            codigo_cuota="General", importe=Decimal("50.00"),
            importe_pagado=Decimal("50.00") if cobrada else Decimal("0.00"),
            estado_id=(est_cobrada if cobrada else est_pendiente).id,
            fecha_pago=date(EJERCICIO_ACTUAL, 3, 15) if cobrada else None,
            fecha_vencimiento=date(EJERCICIO_ACTUAL, 1, 31),
        ))
        creados += 1
    print(f"  cuotas_anuales {EJERCICIO_ACTUAL}: +{creados} (socios activos)")


async def seed(session: AsyncSession | None = None) -> None:
    from app.scripts.seeding._guard import abort_if_production
    abort_if_production("seeding demo de cuotas")
    own = session is None
    if own:
        session = async_session()
        await session.__aenter__()
    try:
        print("Seed demo cuotas…")
        importes = await _seed_importes(session)
        await _seed_cuotas_actuales(session, importes)
        await session.commit()
        print("Listo.")
    finally:
        if own:
            await session.__aexit__(None, None, None)


if __name__ == "__main__":
    asyncio.run(seed())
