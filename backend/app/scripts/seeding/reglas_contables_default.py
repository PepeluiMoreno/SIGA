"""Seed de reglas contables por defecto (PCESFL 2013).

Idempotente: solo inserta si la tabla está vacía.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.economico.models.contabilidad import ReglaContable

REGLAS_DEFAULT = [
    # Cuotas de socios
    {"origen": "CUOTA",    "tipo_apunte": "INGRESO",      "debe": "572", "haber": "721", "descripcion": "Cobro de cuota socio → Banco / Cuotas socios",          "orden": 1},
    {"origen": "CUOTA",    "tipo_apunte": "GASTO",        "debe": "721", "haber": "572", "descripcion": "Devolución cuota → Cuotas socios / Banco",               "orden": 2},
    # Donaciones
    {"origen": "DONACION", "tipo_apunte": "INGRESO",      "debe": "572", "haber": "730", "descripcion": "Donación recibida → Banco / Donaciones corrientes",       "orden": 3},
    # Remesas SEPA
    {"origen": "REMESA",   "tipo_apunte": "INGRESO",      "debe": "572", "haber": "430", "descripcion": "Cobro remesa → Banco / Deudores por actividades",        "orden": 4},
    {"origen": "REMESA",   "tipo_apunte": "GASTO",        "debe": "430", "haber": "572", "descripcion": "Devolución remesa → Deudores / Banco",                   "orden": 5},
    # Cobro por pasarela de pago (PayPal, etc.)
    {"origen": "PAGO",     "tipo_apunte": "INGRESO",      "debe": "572", "haber": "721", "descripcion": "Pago online → Banco / Cuotas socios",                    "orden": 6},
    {"origen": "PAGO",     "tipo_apunte": "GASTO",        "debe": "629", "haber": "572", "descripcion": "Comisión pasarela → Gastos / Banco",                     "orden": 7},
    # Manuales (comodín — origen NULL)
    {"origen": None,       "tipo_apunte": "INGRESO",      "debe": "572", "haber": "749", "descripcion": "Ingreso manual → Banco / Otros ingresos",                "orden": 90},
    {"origen": None,       "tipo_apunte": "GASTO",        "debe": "629", "haber": "572", "descripcion": "Gasto manual → Otros gastos / Banco",                   "orden": 91},
]


async def cargar_reglas_contables(session: AsyncSession) -> int:
    """Carga reglas por defecto si la tabla está vacía. Idempotente."""
    result = await session.execute(select(ReglaContable))
    if result.scalars().first():
        print("Reglas contables: ya existen, omitiendo seed.")
        return 0

    creadas = 0
    for r in REGLAS_DEFAULT:
        regla = ReglaContable(
            origen=r["origen"],
            tipo_apunte=r["tipo_apunte"],
            cuenta_debe_codigo=r["debe"],
            cuenta_haber_codigo=r["haber"],
            descripcion=r["descripcion"],
            orden=r["orden"],
        )
        session.add(regla)
        creadas += 1

    await session.commit()
    print(f"Reglas contables: {creadas} reglas por defecto creadas.")
    return creadas
