"""Seed de categorías fiscales por defecto para contabilidad simplificada.

Estructura básica de ingresos y gastos para una asociación pequeña,
con el mapeo a los modelos tributarios habituales:
  - 182: declaración informativa de donativos (deducibles)
  - 347: operaciones con terceros > 3.005,06 € anuales

Idempotente: solo inserta las categorías que no existan ya (por código).
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.economico.models.contabilidad import CategoriaFiscal, TipoCategoriaFiscal


CATEGORIAS_DEFAULT = [
    # ── INGRESOS ──────────────────────────────────────────────────────────────
    {"codigo": "ING_CUOTAS",       "nombre": "Cuotas de asociados",        "tipo": "INGRESO", "orden": 1,  "m182": False, "m347": False, "color": "#22c55e",
     "descripcion": "Cuotas periódicas de los socios. No deducibles, no computan en 182."},
    {"codigo": "ING_DONATIVOS",    "nombre": "Donativos y donaciones",      "tipo": "INGRESO", "orden": 2,  "m182": True,  "m347": False, "color": "#16a34a",
     "descripcion": "Donativos deducibles — se declaran en el modelo 182."},
    {"codigo": "ING_SUBVENCIONES", "nombre": "Subvenciones",                "tipo": "INGRESO", "orden": 3,  "m182": False, "m347": False, "color": "#15803d",
     "descripcion": "Subvenciones públicas y privadas recibidas."},
    {"codigo": "ING_ACTIVIDADES",  "nombre": "Ingresos por actividades",    "tipo": "INGRESO", "orden": 4,  "m182": False, "m347": True,  "color": "#84cc16",
     "descripcion": "Inscripciones, ventas y prestación de servicios propios."},
    {"codigo": "ING_FINANCIEROS",  "nombre": "Ingresos financieros",        "tipo": "INGRESO", "orden": 5,  "m182": False, "m347": False, "color": "#65a30d",
     "descripcion": "Intereses de cuentas y otros rendimientos financieros."},
    {"codigo": "ING_OTROS",        "nombre": "Otros ingresos",              "tipo": "INGRESO", "orden": 9,  "m182": False, "m347": False, "color": "#a3a3a3",
     "descripcion": "Ingresos no clasificados en las categorías anteriores."},

    # ── GASTOS ────────────────────────────────────────────────────────────────
    {"codigo": "GAS_PERSONAL",     "nombre": "Gastos de personal",          "tipo": "GASTO",   "orden": 1,  "m182": False, "m347": False, "color": "#ef4444",
     "descripcion": "Salarios, seguridad social y otros gastos de personal."},
    {"codigo": "GAS_SUMINISTROS",  "nombre": "Suministros",                 "tipo": "GASTO",   "orden": 2,  "m182": False, "m347": True,  "color": "#dc2626",
     "descripcion": "Luz, agua, teléfono, internet y otros suministros."},
    {"codigo": "GAS_ALQUILER",     "nombre": "Alquileres",                  "tipo": "GASTO",   "orden": 3,  "m182": False, "m347": True,  "color": "#b91c1c",
     "descripcion": "Alquiler de local, salas y equipamiento."},
    {"codigo": "GAS_SERVICIOS",    "nombre": "Servicios externos",          "tipo": "GASTO",   "orden": 4,  "m182": False, "m347": True,  "color": "#f97316",
     "descripcion": "Gestoría, asesoría, notaría, servicios profesionales."},
    {"codigo": "GAS_ACTIVIDADES",  "nombre": "Gastos de actividades",       "tipo": "GASTO",   "orden": 5,  "m182": False, "m347": True,  "color": "#ea580c",
     "descripcion": "Materiales, catering y gastos directos de actividades propias."},
    {"codigo": "GAS_DESPLAZAMIENTO","nombre": "Desplazamientos y dietas",   "tipo": "GASTO",   "orden": 6,  "m182": False, "m347": False, "color": "#d97706",
     "descripcion": "Viajes, dietas y desplazamientos."},
    {"codigo": "GAS_BANCARIOS",    "nombre": "Gastos bancarios",            "tipo": "GASTO",   "orden": 7,  "m182": False, "m347": False, "color": "#92400e",
     "descripcion": "Comisiones bancarias y de pasarelas de pago."},
    {"codigo": "GAS_OTROS",        "nombre": "Otros gastos",                "tipo": "GASTO",   "orden": 9,  "m182": False, "m347": False, "color": "#a3a3a3",
     "descripcion": "Gastos no clasificados en las categorías anteriores."},
]


async def seed_categorias_fiscales(session: AsyncSession) -> int:
    """Crea las categorías fiscales que falten. Idempotente por código."""
    result = await session.execute(select(CategoriaFiscal.codigo))
    existentes = {row[0] for row in result.all()}

    creadas = 0
    for c in CATEGORIAS_DEFAULT:
        if c["codigo"] in existentes:
            continue
        categoria = CategoriaFiscal(
            codigo=c["codigo"],
            nombre=c["nombre"],
            descripcion=c["descripcion"],
            tipo=TipoCategoriaFiscal[c["tipo"]],
            computa_modelo_182=c["m182"],
            computa_modelo_347=c["m347"],
            orden=c["orden"],
            color=c["color"],
        )
        session.add(categoria)
        creadas += 1

    await session.commit()
    print(f"[categorias_fiscales] {creadas} creadas, {len(existentes)} ya existían")
    return creadas
