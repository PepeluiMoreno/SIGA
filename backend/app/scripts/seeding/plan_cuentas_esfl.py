"""Script de seeding: Plan de Cuentas PCESFL 2013 simplificado."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.financiero.models.contabilidad import (
    CuentaContable,
    TipoCuentaContable,
)

CUENTAS_PCESFL = [
    # GRUPO 1: ACTIVO
    {"codigo": "1",   "nombre": "ACTIVO",                               "tipo": TipoCuentaContable.ACTIVO,      "nivel": 1, "padre_codigo": None,  "permite_asiento": False},
    {"codigo": "10",  "nombre": "Activo Corriente",                     "tipo": TipoCuentaContable.ACTIVO,      "nivel": 2, "padre_codigo": "1",   "permite_asiento": False},
    {"codigo": "100", "nombre": "Caja",                                 "tipo": TipoCuentaContable.ACTIVO,      "nivel": 3, "padre_codigo": "10",  "permite_asiento": True},
    {"codigo": "101", "nombre": "Bancos c/c",                           "tipo": TipoCuentaContable.ACTIVO,      "nivel": 3, "padre_codigo": "10",  "permite_asiento": True},
    {"codigo": "102", "nombre": "Valores negociables",                  "tipo": TipoCuentaContable.ACTIVO,      "nivel": 3, "padre_codigo": "10",  "permite_asiento": True},
    {"codigo": "11",  "nombre": "Deudores",                             "tipo": TipoCuentaContable.ACTIVO,      "nivel": 2, "padre_codigo": "1",   "permite_asiento": False},
    {"codigo": "110", "nombre": "Deudores por actividades propias",     "tipo": TipoCuentaContable.ACTIVO,      "nivel": 3, "padre_codigo": "11",  "permite_asiento": True},
    {"codigo": "111", "nombre": "Deudores por subvenciones",            "tipo": TipoCuentaContable.ACTIVO,      "nivel": 3, "padre_codigo": "11",  "permite_asiento": True},
    # GRUPO 2: PASIVO
    {"codigo": "2",   "nombre": "PASIVO",                               "tipo": TipoCuentaContable.PASIVO,      "nivel": 1, "padre_codigo": None,  "permite_asiento": False},
    {"codigo": "20",  "nombre": "Pasivo Corriente",                     "tipo": TipoCuentaContable.PASIVO,      "nivel": 2, "padre_codigo": "2",   "permite_asiento": False},
    {"codigo": "200", "nombre": "Acreedores por actividades propias",   "tipo": TipoCuentaContable.PASIVO,      "nivel": 3, "padre_codigo": "20",  "permite_asiento": True},
    {"codigo": "201", "nombre": "Acreedores por suministros",           "tipo": TipoCuentaContable.PASIVO,      "nivel": 3, "padre_codigo": "20",  "permite_asiento": True},
    # GRUPO 3: PATRIMONIO
    {"codigo": "3",   "nombre": "PATRIMONIO",                           "tipo": TipoCuentaContable.PATRIMONIO,  "nivel": 1, "padre_codigo": None,  "permite_asiento": False},
    {"codigo": "30",  "nombre": "Dotación fundacional",                 "tipo": TipoCuentaContable.PATRIMONIO,  "nivel": 2, "padre_codigo": "3",   "permite_asiento": False},
    {"codigo": "300", "nombre": "Dotación fundacional",                 "tipo": TipoCuentaContable.PATRIMONIO,  "nivel": 3, "padre_codigo": "30",  "permite_asiento": True,  "es_dotacion": True},
    {"codigo": "31",  "nombre": "Reservas",                             "tipo": TipoCuentaContable.PATRIMONIO,  "nivel": 2, "padre_codigo": "3",   "permite_asiento": False},
    {"codigo": "310", "nombre": "Reservas de patrimonio",               "tipo": TipoCuentaContable.PATRIMONIO,  "nivel": 3, "padre_codigo": "31",  "permite_asiento": True},
    # GRUPO 4: INGRESOS
    {"codigo": "4",   "nombre": "INGRESOS",                             "tipo": TipoCuentaContable.INGRESO,     "nivel": 1, "padre_codigo": None,  "permite_asiento": False},
    {"codigo": "40",  "nombre": "Ingresos de la actividad propia",      "tipo": TipoCuentaContable.INGRESO,     "nivel": 2, "padre_codigo": "4",   "permite_asiento": False},
    {"codigo": "400", "nombre": "Cuotas de miembros",                   "tipo": TipoCuentaContable.INGRESO,     "nivel": 3, "padre_codigo": "40",  "permite_asiento": True},
    {"codigo": "401", "nombre": "Ingresos por prestación de servicios", "tipo": TipoCuentaContable.INGRESO,     "nivel": 3, "padre_codigo": "40",  "permite_asiento": True},
    {"codigo": "41",  "nombre": "Donaciones",                           "tipo": TipoCuentaContable.INGRESO,     "nivel": 2, "padre_codigo": "4",   "permite_asiento": False},
    {"codigo": "410", "nombre": "Donaciones",                           "tipo": TipoCuentaContable.INGRESO,     "nivel": 3, "padre_codigo": "41",  "permite_asiento": True},
    {"codigo": "42",  "nombre": "Subvenciones",                         "tipo": TipoCuentaContable.INGRESO,     "nivel": 2, "padre_codigo": "4",   "permite_asiento": False},
    {"codigo": "420", "nombre": "Subvenciones del sector público",      "tipo": TipoCuentaContable.INGRESO,     "nivel": 3, "padre_codigo": "42",  "permite_asiento": True},
    {"codigo": "43",  "nombre": "Ingresos financieros",                 "tipo": TipoCuentaContable.INGRESO,     "nivel": 2, "padre_codigo": "4",   "permite_asiento": False},
    {"codigo": "430", "nombre": "Intereses de cuentas bancarias",       "tipo": TipoCuentaContable.INGRESO,     "nivel": 3, "padre_codigo": "43",  "permite_asiento": True},
    # GRUPO 5: GASTOS
    {"codigo": "5",   "nombre": "GASTOS",                               "tipo": TipoCuentaContable.GASTO,       "nivel": 1, "padre_codigo": None,  "permite_asiento": False},
    {"codigo": "50",  "nombre": "Gastos de actividades propias",        "tipo": TipoCuentaContable.GASTO,       "nivel": 2, "padre_codigo": "5",   "permite_asiento": False},
    {"codigo": "500", "nombre": "Suministros",                          "tipo": TipoCuentaContable.GASTO,       "nivel": 3, "padre_codigo": "50",  "permite_asiento": True},
    {"codigo": "501", "nombre": "Servicios externos",                   "tipo": TipoCuentaContable.GASTO,       "nivel": 3, "padre_codigo": "50",  "permite_asiento": True},
    {"codigo": "51",  "nombre": "Gastos de personal",                   "tipo": TipoCuentaContable.GASTO,       "nivel": 2, "padre_codigo": "5",   "permite_asiento": False},
    {"codigo": "510", "nombre": "Sueldos y salarios",                   "tipo": TipoCuentaContable.GASTO,       "nivel": 3, "padre_codigo": "51",  "permite_asiento": True},
    {"codigo": "511", "nombre": "Seguridad social",                     "tipo": TipoCuentaContable.GASTO,       "nivel": 3, "padre_codigo": "51",  "permite_asiento": True},
    {"codigo": "52",  "nombre": "Gastos de administración",             "tipo": TipoCuentaContable.GASTO,       "nivel": 2, "padre_codigo": "5",   "permite_asiento": False},
    {"codigo": "520", "nombre": "Alquileres",                           "tipo": TipoCuentaContable.GASTO,       "nivel": 3, "padre_codigo": "52",  "permite_asiento": True},
    {"codigo": "521", "nombre": "Servicios administrativos",            "tipo": TipoCuentaContable.GASTO,       "nivel": 3, "padre_codigo": "52",  "permite_asiento": True},
    {"codigo": "53",  "nombre": "Amortizaciones",                       "tipo": TipoCuentaContable.GASTO,       "nivel": 2, "padre_codigo": "5",   "permite_asiento": False},
    {"codigo": "530", "nombre": "Amortización de inmovilizado",         "tipo": TipoCuentaContable.GASTO,       "nivel": 3, "padre_codigo": "53",  "permite_asiento": True},
]


async def cargar_plan_cuentas_esfl(session: AsyncSession) -> int:
    """Carga el plan de cuentas PCESFL 2013. Idempotente."""
    result = await session.execute(select(CuentaContable))
    existentes: dict[str, CuentaContable] = {
        c.codigo: c for c in result.scalars().all()
    }

    creadas = 0
    for data in CUENTAS_PCESFL:
        codigo = data["codigo"]
        if codigo in existentes:
            continue
        padre_id = None
        if data.get("padre_codigo"):
            padre = existentes.get(data["padre_codigo"])
            if padre:
                padre_id = padre.id
        cuenta = CuentaContable(
            codigo=codigo,
            nombre=data["nombre"],
            tipo=data["tipo"],
            nivel=data["nivel"],
            padre_id=padre_id,
            permite_asiento=data.get("permite_asiento", False),
            es_dotacion=data.get("es_dotacion", False),
        )
        session.add(cuenta)
        existentes[codigo] = cuenta
        creadas += 1

    await session.commit()
    print(f"Plan de cuentas PCESFL 2013: {creadas} cuentas creadas.")
    return creadas
