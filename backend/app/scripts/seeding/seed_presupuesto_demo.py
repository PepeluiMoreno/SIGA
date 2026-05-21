"""Seed de presupuestos demo 2024 y 2025 (CERRADOS) con datos de ejecución.

Crea:
  - ImporteCuotaAnio BASE para 2024 (110 €), 2025 (120 €), 2026 (130 €)
  - PlanificacionAnual 2024 en CERRADO con partidas e importes ejecutados
  - PlanificacionAnual 2025 en CERRADO con partidas e importes ejecutados
"""

from decimal import Decimal
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.economico.models.cuotas import ImporteCuotaAnio
from app.modules.economico.models.presupuesto import (
    PlanificacionAnual,
    PartidaPresupuestaria,
    EstadoPlanificacion,
)
from app.modules.economico.models.contabilidad.categoria_fiscal import CategoriaFiscal


async def seed_presupuesto_demo(session: AsyncSession) -> None:
    # Idempotente: no hace nada si los presupuestos de 2024 o 2025 ya existen
    existe = await session.execute(
        select(PlanificacionAnual).where(PlanificacionAnual.ejercicio.in_([2024, 2025]))
    )
    if existe.scalars().first():
        return

    # ── Categorías fiscales (pueden estar vacías, se usan como hint visual) ──
    cats_result = await session.execute(select(CategoriaFiscal))
    cats = {c.codigo: c.id for c in cats_result.scalars().all()}

    # ── Estados ──────────────────────────────────────────────────────────────
    estados_result = await session.execute(select(EstadoPlanificacion))
    estados = {e.codigo: e for e in estados_result.scalars().all()}
    if not estados:
        return

    estado_cerrado = estados.get("CERRADO")
    if not estado_cerrado:
        return

    # ── ImporteCuotaAnio BASE para 2024, 2025 y 2026 ─────────────────────────
    cuotas_existentes = await session.execute(
        select(ImporteCuotaAnio).where(ImporteCuotaAnio.ejercicio.in_([2024, 2025, 2026]))
    )
    ejercicios_con_cuota = {c.ejercicio for c in cuotas_existentes.scalars().all()
                            if c.codigo_cuota == "BASE"}

    cuotas_a_crear = [
        (2024, "Cuota base 2024", Decimal("110.00")),
        (2025, "Cuota base 2025", Decimal("120.00")),
        (2026, "Cuota base 2026", Decimal("130.00")),
    ]
    for ejercicio, nombre, importe in cuotas_a_crear:
        if ejercicio not in ejercicios_con_cuota:
            session.add(ImporteCuotaAnio(
                ejercicio=ejercicio, codigo_cuota="BASE",
                nombre_cuota=nombre, importe=importe,
            ))
    await session.flush()

    # ── Helper ────────────────────────────────────────────────────────────────
    def _cat(codigo):
        return cats.get(codigo)

    def _partida(plan_id, ejercicio, tipo, codigo, nombre, presupuestado, ejecutado,
                 comprometido=None, descripcion=None, categoria=None):
        return PartidaPresupuestaria(
            planificacion_id=plan_id,
            ejercicio=ejercicio,
            tipo=tipo,
            codigo=codigo,
            nombre=nombre,
            importe_presupuestado=Decimal(str(presupuestado)),
            importe_inicial=Decimal(str(presupuestado)),
            importe_ejecutado=Decimal(str(ejecutado)),
            importe_comprometido=Decimal(str(comprometido or 0)),
            descripcion=descripcion,
            categoria_id=categoria,
        )

    # ══════════════════════════════════════════════════════════════════════════
    # PRESUPUESTO 2024 — CERRADO
    # ══════════════════════════════════════════════════════════════════════════
    plan24 = PlanificacionAnual(
        ejercicio=2024,
        nombre="Presupuesto 2024",
        descripcion="Presupuesto anual. Primer año con cuota diferenciada por perfiles.",
        objetivos=(
            "Fortalecer los servicios de atención a la base social. "
            "Ampliar la red de colaboradores. "
            "Consolidar la presencia digital de la entidad."
        ),
        estado_id=estado_cerrado.id,
        fecha_aprobacion=date(2024, 1, 20),
        control_disponibilidad=False,
    )
    session.add(plan24)
    await session.flush()

    partidas_2024 = [
        # INGRESOS — total presupuestado 21 000 €, ejecutado 20 350 €
        _partida(plan24.id, 2024, "INGRESO", "2024-ING-01",
                 "Cuotas socios ordinarios",     14500, 13970,
                 descripcion="115 socios × 110 €  (tasa cobro 96%)",
                 categoria=_cat("ING_CUOTAS")),
        _partida(plan24.id, 2024, "INGRESO", "2024-ING-02",
                 "Cuotas socios reducidas",       2750,  2530,
                 descripcion="50 socios reducidos × 55 €  (tasa cobro 92%)",
                 categoria=_cat("ING_CUOTAS")),
        _partida(plan24.id, 2024, "INGRESO", "2024-ING-03",
                 "Subvención programa municipal",  2000,  2000,
                 descripcion="Concedida íntegramente",
                 categoria=_cat("ING_SUBVENCIONES")),
        _partida(plan24.id, 2024, "INGRESO", "2024-ING-04",
                 "Ingresos actividades formativas", 1200, 1050,
                 descripcion="Talleres con inscripción abierta",
                 categoria=_cat("ING_ACTIVIDADES")),
        _partida(plan24.id, 2024, "INGRESO", "2024-ING-05",
                 "Donaciones y colectas",            550,   800,
                 descripcion="Por encima de lo previsto — campaña viral",
                 categoria=_cat("ING_DONATIVOS")),

        # GASTOS — total presupuestado 20 000 €, ejecutado 19 620 €
        _partida(plan24.id, 2024, "GASTO", "2024-GAS-01",
                 "Coordinación y administración",  7500,  7250,
                 descripcion="Contrato servicios coordinador/a",
                 categoria=_cat("GAS_PERSONAL")),
        _partida(plan24.id, 2024, "GASTO", "2024-GAS-02",
                 "Alquiler de sede",               4800,  4800,
                 descripcion="400 €/mes × 12",
                 categoria=_cat("GAS_ALQUILER")),
        _partida(plan24.id, 2024, "GASTO", "2024-GAS-03",
                 "Actividades formativas",          2800,  2640,
                 descripcion="Ponentes, materiales y espacios",
                 categoria=_cat("GAS_ACTIVIDADES")),
        _partida(plan24.id, 2024, "GASTO", "2024-GAS-04",
                 "Comunicación y web",              1300,  1180,
                 categoria=_cat("GAS_SERVICIOS")),
        _partida(plan24.id, 2024, "GASTO", "2024-GAS-05",
                 "Suministros de oficina",           800,   740,
                 categoria=_cat("GAS_SUMINISTROS")),
        _partida(plan24.id, 2024, "GASTO", "2024-GAS-06",
                 "Desplazamientos y dietas",         900,   870,
                 categoria=_cat("GAS_DESPLAZAMIENTO")),
        _partida(plan24.id, 2024, "GASTO", "2024-GAS-07",
                 "Gestoría y asesoría jurídica",     900,   900,
                 categoria=_cat("GAS_SERVICIOS")),
        _partida(plan24.id, 2024, "GASTO", "2024-GAS-08",
                 "Gastos bancarios",                 200,   180,
                 categoria=_cat("GAS_BANCARIOS")),
        _partida(plan24.id, 2024, "GASTO", "2024-GAS-09",
                 "Imprevistos / contingencia",       800,   60,
                 descripcion="Fondo apenas utilizado"),
    ]
    for p in partidas_2024:
        session.add(p)

    # ══════════════════════════════════════════════════════════════════════════
    # PRESUPUESTO 2025 — CERRADO
    # ══════════════════════════════════════════════════════════════════════════
    plan25 = PlanificacionAnual(
        ejercicio=2025,
        nombre="Presupuesto 2025",
        descripcion="Presupuesto anual aprobado en asamblea general ordinaria.",
        objetivos=(
            "Consolidar la sede y los programas de formación. "
            "Aumentar la base social en un 10%. "
            "Ejecutar la campaña de sensibilización prevista."
        ),
        estado_id=estado_cerrado.id,
        fecha_aprobacion=date(2025, 1, 25),
        control_disponibilidad=False,
    )
    session.add(plan25)
    await session.flush()

    partidas_2025 = [
        # INGRESOS — total presupuestado 25 500 €, ejecutado 24 900 €
        _partida(plan25.id, 2025, "INGRESO", "2025-ING-01",
                 "Cuotas socios ordinarios",       16000, 15360,
                 descripcion="120 socios × 120 €  (tasa cobro 96%)",
                 categoria=_cat("ING_CUOTAS")),
        _partida(plan25.id, 2025, "INGRESO", "2025-ING-02",
                 "Cuotas socios tarifa reducida",   3000,  2700,
                 descripcion="50 socios × 60 €  (tasa cobro 90%)",
                 categoria=_cat("ING_CUOTAS")),
        _partida(plan25.id, 2025, "INGRESO", "2025-ING-03",
                 "Subvención convocatoria municipal", 2500, 2500,
                 categoria=_cat("ING_SUBVENCIONES")),
        _partida(plan25.id, 2025, "INGRESO", "2025-ING-04",
                 "Subvención autonómica",            1500, 1500,
                 descripcion="Proyecto participación ciudadana",
                 categoria=_cat("ING_SUBVENCIONES")),
        _partida(plan25.id, 2025, "INGRESO", "2025-ING-05",
                 "Ingresos actividades formativas",  1500, 1640,
                 descripcion="Superado objetivo — nuevos talleres",
                 categoria=_cat("ING_ACTIVIDADES")),
        _partida(plan25.id, 2025, "INGRESO", "2025-ING-06",
                 "Donaciones y microdonaciones",      500,  700,
                 categoria=_cat("ING_DONATIVOS")),
        _partida(plan25.id, 2025, "INGRESO", "2025-ING-07",
                 "Otros ingresos varios",             500,  500,
                 categoria=_cat("ING_OTROS")),

        # GASTOS — total presupuestado 24 800 €, ejecutado 24 200 €
        _partida(plan25.id, 2025, "GASTO", "2025-GAS-01",
                 "Coordinación y administración",   8000, 8000,
                 descripcion="Honorarios coordinación (contrato servicios)",
                 categoria=_cat("GAS_PERSONAL")),
        _partida(plan25.id, 2025, "GASTO", "2025-GAS-02",
                 "Alquiler de sede",                4800, 4800,
                 descripcion="400 €/mes × 12",
                 categoria=_cat("GAS_ALQUILER")),
        _partida(plan25.id, 2025, "GASTO", "2025-GAS-03",
                 "Actividades de formación",        3000, 2950,
                 descripcion="Ponentes, materiales y espacios",
                 categoria=_cat("GAS_ACTIVIDADES")),
        _partida(plan25.id, 2025, "GASTO", "2025-GAS-04",
                 "Campaña de sensibilización",      2500, 2480,
                 descripcion="Materiales, difusión y logística",
                 categoria=_cat("GAS_ACTIVIDADES")),
        _partida(plan25.id, 2025, "GASTO", "2025-GAS-05",
                 "Comunicación y web",              1500, 1420,
                 descripcion="Hosting, newsletter, redes y diseño",
                 categoria=_cat("GAS_SERVICIOS")),
        _partida(plan25.id, 2025, "GASTO", "2025-GAS-06",
                 "Suministros de oficina",          1200, 1050,
                 categoria=_cat("GAS_SUMINISTROS")),
        _partida(plan25.id, 2025, "GASTO", "2025-GAS-07",
                 "Desplazamientos y dietas",        1500, 1320,
                 categoria=_cat("GAS_DESPLAZAMIENTO")),
        _partida(plan25.id, 2025, "GASTO", "2025-GAS-08",
                 "Gestoría y asesoría",             1200, 1180,
                 categoria=_cat("GAS_SERVICIOS")),
        _partida(plan25.id, 2025, "GASTO", "2025-GAS-09",
                 "Gastos bancarios",                 300,  270,
                 categoria=_cat("GAS_BANCARIOS")),
        _partida(plan25.id, 2025, "GASTO", "2025-GAS-10",
                 "Imprevistos y contingencia",       800,  730,
                 categoria=_cat("GAS_OTROS")),
    ]
    for p in partidas_2025:
        session.add(p)

    await session.commit()
    print(f"[seed_presupuesto_demo] Presupuestos 2024 ({len(partidas_2024)} partidas) "
          f"y 2025 ({len(partidas_2025)} partidas) creados en estado CERRADO")
