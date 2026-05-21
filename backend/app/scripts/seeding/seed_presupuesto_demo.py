"""Seed de presupuesto demo 2025.

Crea:
  - ImporteCuotaAnio para 2025 (socio ordinario 120€, reducida 60€)
  - ImporteCuotaAnio para 2026 (130€ / 65€) para poder demo el ratio al clonar
  - PlanificacionAnual 2025 en estado APROBADO con partidas realistas
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
    # Idempotente: no hace nada si el presupuesto 2025 ya existe
    existe = await session.execute(
        select(PlanificacionAnual).where(PlanificacionAnual.ejercicio == 2025)
    )
    if existe.scalar_one_or_none():
        return

    # ── Categorías fiscales ──────────────────────────────────────────────────
    cats_result = await session.execute(select(CategoriaFiscal))
    cats = {c.codigo: c.id for c in cats_result.scalars().all()}

    # ── Estado APROBADO ──────────────────────────────────────────────────────
    estado_result = await session.execute(
        select(EstadoPlanificacion).where(EstadoPlanificacion.codigo == "APROBADO")
    )
    estado_aprobado = estado_result.scalar_one_or_none()
    if not estado_aprobado:
        return  # sin estados no podemos seedear

    # ── ImporteCuotaAnio 2025 y 2026 (generales, sin tipo específico) ────────
    # Dos cuotas por año: tarifa ordinaria (None = sin tipo concreto) y reducida.
    # Se usan como base para calcular el ratio al clonar el presupuesto.
    cuotas_existentes = await session.execute(
        select(ImporteCuotaAnio).where(ImporteCuotaAnio.ejercicio.in_([2025, 2026]))
    )
    ejercicios_con_cuota = {c.ejercicio for c in cuotas_existentes.scalars().all()}

    if 2025 not in ejercicios_con_cuota:
        session.add(ImporteCuotaAnio(ejercicio=2025, tipo_miembro_id=None, importe=Decimal("120.00")))
    if 2026 not in ejercicios_con_cuota:
        session.add(ImporteCuotaAnio(ejercicio=2026, tipo_miembro_id=None, importe=Decimal("130.00")))
    await session.flush()

    # ── Planificación 2025 ───────────────────────────────────────────────────
    plan = PlanificacionAnual(
        ejercicio=2025,
        nombre="Presupuesto 2025",
        descripcion="Presupuesto anual aprobado en asamblea general ordinaria",
        objetivos=(
            "Consolidar la sede y los programas de formación. "
            "Aumentar la base social en un 10%. "
            "Ejecutar la campaña de sensibilización prevista."
        ),
        estado_id=estado_aprobado.id,
        fecha_aprobacion=date(2025, 1, 25),
        control_disponibilidad=False,
    )
    session.add(plan)
    await session.flush()

    # ── Partidas ─────────────────────────────────────────────────────────────
    def _id(codigo):
        return cats.get(codigo)

    partidas = [
        # INGRESOS
        dict(tipo="INGRESO", codigo="2025-ING-01", nombre="Cuotas socios ordinarios",
             importe=Decimal("16000.00"), categoria_id=_id("ING_CUOTAS"),
             descripcion="120 socios ordinarios × 120 €/año + proyección nuevas altas"),
        dict(tipo="INGRESO", codigo="2025-ING-02", nombre="Cuotas socios tarifa reducida",
             importe=Decimal("3000.00"),  categoria_id=_id("ING_CUOTAS"),
             descripcion="50 socios tarifa reducida × 60 €/año"),
        dict(tipo="INGRESO", codigo="2025-ING-03", nombre="Subvención convocatoria municipal",
             importe=Decimal("2500.00"),  categoria_id=_id("ING_SUBVENCIONES"),
             descripcion="Programa de apoyo al tejido asociativo"),
        dict(tipo="INGRESO", codigo="2025-ING-04", nombre="Subvención autonómica",
             importe=Decimal("1500.00"),  categoria_id=_id("ING_SUBVENCIONES"),
             descripcion="Convocatoria de proyectos de participación ciudadana"),
        dict(tipo="INGRESO", codigo="2025-ING-05", nombre="Ingresos por actividades formativas",
             importe=Decimal("1500.00"),  categoria_id=_id("ING_ACTIVIDADES"),
             descripcion="Talleres y cursos con inscripción"),
        dict(tipo="INGRESO", codigo="2025-ING-06", nombre="Donaciones y microdonaciones",
             importe=Decimal("500.00"),   categoria_id=_id("ING_DONATIVOS")),
        dict(tipo="INGRESO", codigo="2025-ING-07", nombre="Otros ingresos varios",
             importe=Decimal("500.00"),   categoria_id=_id("ING_OTROS")),

        # GASTOS
        dict(tipo="GASTO",   codigo="2025-GAS-01", nombre="Coordinación y administración",
             importe=Decimal("8000.00"),  categoria_id=_id("GAS_PERSONAL"),
             descripcion="Honorarios coordinación (contrato servicios)"),
        dict(tipo="GASTO",   codigo="2025-GAS-02", nombre="Alquiler de sede",
             importe=Decimal("4800.00"),  categoria_id=_id("GAS_ALQUILER"),
             descripcion="400 €/mes × 12 meses"),
        dict(tipo="GASTO",   codigo="2025-GAS-03", nombre="Actividades de formación",
             importe=Decimal("3000.00"),  categoria_id=_id("GAS_ACTIVIDADES"),
             descripcion="Ponentes, materiales y espacios para talleres y cursos"),
        dict(tipo="GASTO",   codigo="2025-GAS-04", nombre="Campaña de sensibilización",
             importe=Decimal("2500.00"),  categoria_id=_id("GAS_ACTIVIDADES"),
             descripcion="Materiales, difusión y logística de la campaña anual"),
        dict(tipo="GASTO",   codigo="2025-GAS-05", nombre="Comunicación y web",
             importe=Decimal("1500.00"),  categoria_id=_id("GAS_SERVICIOS"),
             descripcion="Hosting, newsletter, redes sociales y diseño gráfico"),
        dict(tipo="GASTO",   codigo="2025-GAS-06", nombre="Suministros de oficina",
             importe=Decimal("1200.00"),  categoria_id=_id("GAS_SUMINISTROS")),
        dict(tipo="GASTO",   codigo="2025-GAS-07", nombre="Desplazamientos y dietas",
             importe=Decimal("1500.00"),  categoria_id=_id("GAS_DESPLAZAMIENTO")),
        dict(tipo="GASTO",   codigo="2025-GAS-08", nombre="Servicios externos (gestoría y asesoría)",
             importe=Decimal("1200.00"),  categoria_id=_id("GAS_SERVICIOS")),
        dict(tipo="GASTO",   codigo="2025-GAS-09", nombre="Gastos bancarios",
             importe=Decimal("300.00"),   categoria_id=_id("GAS_BANCARIOS")),
        dict(tipo="GASTO",   codigo="2025-GAS-10", nombre="Imprevistos y fondo de contingencia",
             importe=Decimal("500.00"),   categoria_id=_id("GAS_OTROS")),
    ]

    for p in partidas:
        session.add(PartidaPresupuestaria(
            planificacion_id=plan.id,
            ejercicio=2025,
            codigo=p["codigo"],
            nombre=p["nombre"],
            tipo=p["tipo"],
            importe_presupuestado=p["importe"],
            importe_inicial=p["importe"],
            categoria_id=p.get("categoria_id"),
            descripcion=p.get("descripcion"),
        ))

    await session.commit()
    print("[seed_presupuesto_demo] Presupuesto 2025 creado con",
          len(partidas), "partidas y cuotas 2025/2026")
