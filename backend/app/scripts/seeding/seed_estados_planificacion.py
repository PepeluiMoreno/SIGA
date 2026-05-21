"""Seed de estados de planificación presupuestaria.

Ciclo de vida del presupuesto:
  BORRADOR → PROPUESTO → APROBADO → EN_EJECUCION → CERRADO

Idempotente por código.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.economico.models.presupuesto import EstadoPlanificacion


ESTADOS = [
    {"codigo": "BORRADOR",     "nombre": "Borrador",      "orden": 1, "color": "#9ca3af", "es_final": False},
    {"codigo": "PROPUESTO",    "nombre": "Propuesto",     "orden": 2, "color": "#3b82f6", "es_final": False},
    {"codigo": "APROBADO",     "nombre": "Aprobado",      "orden": 3, "color": "#22c55e", "es_final": False},
    {"codigo": "EN_EJECUCION", "nombre": "En ejecución",  "orden": 4, "color": "#a855f7", "es_final": False},
    {"codigo": "CERRADO",      "nombre": "Cerrado",       "orden": 5, "color": "#1f2937", "es_final": True},
]


async def seed_estados_planificacion(session: AsyncSession) -> int:
    """Crea los estados de planificación que falten. Idempotente por código."""
    result = await session.execute(select(EstadoPlanificacion.codigo))
    existentes = {row[0] for row in result.all()}

    creados = 0
    for e in ESTADOS:
        if e["codigo"] in existentes:
            continue
        session.add(EstadoPlanificacion(
            codigo=e["codigo"],
            nombre=e["nombre"],
            orden=e["orden"],
            color=e["color"],
            es_final=e["es_final"],
        ))
        creados += 1

    await session.commit()
    print(f"[estados_planificacion] {creados} creados, {len(existentes)} ya existían")
    return creados
