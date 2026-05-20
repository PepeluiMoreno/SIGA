"""Seeding: Plan de Cuentas de Entidades Sin Fines Lucrativos (PCESFL 2013).

Basado en el Plan General de Contabilidad para Entidades sin Fines Lucrativos
aprobado por RD 1491/2011. Adaptado para asociaciones y partidos políticos.

Cuentas clave que utilizan las reglas contables automáticas (RegistroContable):
  572  Bancos e instituciones de crédito c/c
  430  Usuarios y deudores por actividades propias
  721  Cuotas de socios y afiliados
  730  Donaciones y legados corrientes
  740  Subvenciones, donaciones y legados imputados al resultado del ejercicio
  749  Otros ingresos de gestión corriente
  629  Otros servicios

Ejecutar:
    docker exec <backend-container> python -m app.scripts.seeding.plan_cuentas_esfl

Idempotente: salta cuentas que ya existen (por código).
"""
import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.modules.economico.models.contabilidad import (
    CuentaContable,
    TipoCuentaContable,
)

A = TipoCuentaContable.ACTIVO
P = TipoCuentaContable.PASIVO
N = TipoCuentaContable.PATRIMONIO   # Neto / fondos propios
G = TipoCuentaContable.GASTO
I = TipoCuentaContable.INGRESO

# (codigo, nombre, tipo, nivel, padre_codigo, permite_asiento)
CUENTAS_PCESFL: list[tuple] = [

    # ══════════════════════════════════════════════════════════════════════════
    # GRUPO 1 — Financiación básica (fondos propios y patrimonio neto)
    # ══════════════════════════════════════════════════════════════════════════
    ("1",   "FINANCIACIÓN BÁSICA",                              N, 1, None,  False),

    ("10",  "Dotación / Fondo social",                          N, 2, "1",   False),
    ("100", "Dotación fundacional o fondo asociativo",          N, 3, "10",  True),

    ("11",  "Reservas",                                         N, 2, "1",   False),
    ("110", "Reservas estatutarias",                            N, 3, "11",  True),
    ("119", "Otras reservas",                                   N, 3, "11",  True),

    ("12",  "Excedentes de ejercicios anteriores",              N, 2, "1",   False),
    ("120", "Remanente",                                        N, 3, "12",  True),
    ("121", "Resultados negativos de ejercicios anteriores",    N, 3, "12",  True),

    ("13",  "Subvenciones, donaciones y legados recibidos",     N, 2, "1",   False),
    ("130", "Subvenciones oficiales de capital",                N, 3, "13",  True),
    ("132", "Donaciones y legados de capital",                  N, 3, "13",  True),

    ("14",  "Provisiones a largo plazo",                        P, 2, "1",   False),
    ("142", "Provisión por responsabilidades",                  P, 3, "14",  True),

    ("16",  "Deudas a largo plazo con entidades de crédito",    P, 2, "1",   False),
    ("160", "Préstamos a largo plazo",                          P, 3, "16",  True),

    ("17",  "Deudas a largo plazo",                             P, 2, "1",   False),
    ("170", "Deudas a largo plazo",                             P, 3, "17",  True),

    ("18",  "Pasivos por fianzas y garantías a largo plazo",    P, 2, "1",   False),
    ("180", "Fianzas recibidas a largo plazo",                  P, 3, "18",  True),

    ("129", "Excedente del ejercicio (resultado)",              N, 2, "1",   True),

    # ══════════════════════════════════════════════════════════════════════════
    # GRUPO 2 — Activo no corriente
    # ══════════════════════════════════════════════════════════════════════════
    ("2",   "ACTIVO NO CORRIENTE",                              A, 1, None,  False),

    ("20",  "Inmovilizaciones intangibles",                     A, 2, "2",   False),
    ("200", "Investigación y desarrollo",                       A, 3, "20",  True),
    ("201", "Concesiones administrativas",                      A, 3, "20",  True),
    ("202", "Propiedad industrial",                             A, 3, "20",  True),
    ("203", "Fondos editoriales y documentales",                A, 3, "20",  True),
    ("206", "Aplicaciones informáticas",                        A, 3, "20",  True),
    ("209", "Otro inmovilizado intangible",                     A, 3, "20",  True),

    ("21",  "Inmovilizaciones materiales",                      A, 2, "2",   False),
    ("210", "Terrenos y bienes naturales",                      A, 3, "21",  True),
    ("211", "Construcciones",                                   A, 3, "21",  True),
    ("213", "Maquinaria",                                       A, 3, "21",  True),
    ("214", "Útiles y herramientas",                            A, 3, "21",  True),
    ("215", "Otras instalaciones",                              A, 3, "21",  True),
    ("216", "Mobiliario",                                       A, 3, "21",  True),
    ("217", "Equipos informáticos",                             A, 3, "21",  True),
    ("218", "Elementos de transporte",                          A, 3, "21",  True),
    ("219", "Otro inmovilizado material",                       A, 3, "21",  True),

    ("23",  "Inmovilizaciones materiales en curso",             A, 2, "2",   False),
    ("230", "Adaptación de terrenos y bienes naturales",        A, 3, "23",  True),
    ("231", "Construcciones en curso",                          A, 3, "23",  True),

    ("28",  "Amortización acumulada del inmovilizado",          A, 2, "2",   False),
    ("280", "Amortización acumulada del inmovilizado intangible", A, 3, "28", True),
    ("281", "Amortización acumulada del inmovilizado material", A, 3, "28",  True),

    ("29",  "Deterioro de valor del inmovilizado",              A, 2, "2",   False),
    ("290", "Deterioro de valor del inmovilizado intangible",   A, 3, "29",  True),
    ("291", "Deterioro de valor del inmovilizado material",     A, 3, "29",  True),

    # ══════════════════════════════════════════════════════════════════════════
    # GRUPO 3 — Existencias
    # ══════════════════════════════════════════════════════════════════════════
    ("3",   "EXISTENCIAS",                                      A, 1, None,  False),
    ("30",  "Existencias de mercaderías",                       A, 2, "3",   False),
    ("300", "Mercaderías",                                      A, 3, "30",  True),
    ("32",  "Existencias de materias primas",                   A, 2, "3",   False),
    ("320", "Materias primas",                                  A, 3, "32",  True),
    ("33",  "Existencias de materiales fungibles",              A, 2, "3",   False),
    ("330", "Material de oficina y papelería",                  A, 3, "33",  True),

    # ══════════════════════════════════════════════════════════════════════════
    # GRUPO 4 — Acreedores y deudores
    # ══════════════════════════════════════════════════════════════════════════
    ("4",   "ACREEDORES Y DEUDORES",                            A, 1, None,  False),

    ("40",  "Proveedores",                                      P, 2, "4",   False),
    ("400", "Proveedores",                                      P, 3, "40",  True),
    ("401", "Proveedores, efectos comerciales a pagar",         P, 3, "40",  True),
    ("409", "Proveedores, facturas pendientes de recibir",      P, 3, "40",  True),

    ("41",  "Acreedores varios",                                P, 2, "4",   False),
    ("410", "Acreedores por prestaciones de servicios",         P, 3, "41",  True),
    ("411", "Acreedores, efectos comerciales a pagar",          P, 3, "41",  True),

    ("43",  "Usuarios y deudores de actividades propias",       A, 2, "4",   False),
    ("430", "Usuarios y deudores por actividades propias",      A, 3, "43",  True),
    ("431", "Deudores, efectos comerciales a cobrar",           A, 3, "43",  True),
    ("436", "Deterioro de valor de créditos a c/p",             A, 3, "43",  True),

    ("44",  "Patrocinadores, afiliados y otras cuentas",        A, 2, "4",   False),
    ("440", "Deudores por patrocinios",                         A, 3, "44",  True),
    ("441", "Socios y afiliados (cuotas pendientes de cobro)",  A, 3, "44",  True),

    ("46",  "Personal",                                         P, 2, "4",   False),
    ("460", "Anticipos de remuneraciones",                      A, 3, "46",  True),
    ("465", "Remuneraciones pendientes de pago",                P, 3, "46",  True),

    ("47",  "Administraciones públicas",                        A, 2, "4",   False),
    ("470", "Hacienda Pública, deudora por devolución de impuestos", A, 3, "47", True),
    ("471", "Organismos de la Seguridad Social, deudores",      A, 3, "47",  True),
    ("472", "Hacienda Pública, IVA soportado",                  A, 3, "47",  True),
    ("473", "Hacienda Pública, retenciones y pagos a cuenta",   A, 3, "47",  True),
    ("475", "Hacienda Pública, acreedora por retenciones",      P, 3, "47",  True),
    ("476", "Organismos de la Seguridad Social, acreedores",    P, 3, "47",  True),
    ("477", "Hacienda Pública, IVA repercutido",                P, 3, "47",  True),

    ("48",  "Ajustes por periodificación",                      A, 2, "4",   False),
    ("480", "Gastos anticipados",                               A, 3, "48",  True),
    ("485", "Ingresos anticipados",                             P, 3, "48",  True),

    # ══════════════════════════════════════════════════════════════════════════
    # GRUPO 5 — Cuentas financieras
    # ══════════════════════════════════════════════════════════════════════════
    ("5",   "CUENTAS FINANCIERAS",                              A, 1, None,  False),

    ("52",  "Deudas a corto plazo",                             P, 2, "5",   False),
    ("520", "Deudas a c/p con entidades de crédito",            P, 3, "52",  True),
    ("521", "Deudas a c/p",                                     P, 3, "52",  True),
    ("526", "Dividendos activos a pagar",                       P, 3, "52",  True),

    ("55",  "Otras cuentas no bancarias",                       P, 2, "5",   False),
    ("551", "Cuenta corriente con socios y administradores",    P, 3, "55",  True),
    ("554", "Cobros pendientes de aplicación",                  P, 3, "55",  True),

    ("57",  "Tesorería",                                        A, 2, "5",   False),
    ("570", "Caja, euros",                                      A, 3, "57",  True),
    ("571", "Caja, moneda extranjera",                          A, 3, "57",  True),
    ("572", "Bancos e instituciones de crédito c/c, euros",     A, 3, "57",  True),
    ("573", "Bancos e instituciones de crédito c/c, m/e",       A, 3, "57",  True),
    ("575", "Remesas en camino",                                A, 3, "57",  True),

    ("58",  "Activos no corrientes mantenidos para la venta",   A, 2, "5",   False),

    # ══════════════════════════════════════════════════════════════════════════
    # GRUPO 6 — Gastos
    # ══════════════════════════════════════════════════════════════════════════
    ("6",   "GASTOS",                                           G, 1, None,  False),

    ("60",  "Compras",                                          G, 2, "6",   False),
    ("600", "Compra de mercaderías",                            G, 3, "60",  True),
    ("601", "Compras de materias primas",                       G, 3, "60",  True),
    ("602", "Compras de otros aprovisionamientos",              G, 3, "60",  True),
    ("607", "Trabajos realizados por otras entidades",          G, 3, "60",  True),

    ("62",  "Servicios exteriores",                             G, 2, "6",   False),
    ("620", "Gastos de investigación y desarrollo del ejercicio", G, 3, "62", True),
    ("621", "Arrendamientos y cánones",                         G, 3, "62",  True),
    ("622", "Reparaciones y conservación",                      G, 3, "62",  True),
    ("623", "Servicios de profesionales independientes",        G, 3, "62",  True),
    ("624", "Transportes",                                      G, 3, "62",  True),
    ("625", "Primas de seguros",                                G, 3, "62",  True),
    ("626", "Servicios bancarios y similares",                  G, 3, "62",  True),
    ("627", "Publicidad, propaganda y relaciones públicas",     G, 3, "62",  True),
    ("628", "Suministros (agua, gas, electricidad, telefonía)", G, 3, "62",  True),
    ("629", "Otros servicios",                                  G, 3, "62",  True),

    ("63",  "Tributos",                                         G, 2, "6",   False),
    ("630", "Impuesto sobre beneficios / excedente",            G, 3, "63",  True),
    ("631", "Otros tributos",                                   G, 3, "63",  True),

    ("64",  "Gastos de personal",                               G, 2, "6",   False),
    ("640", "Sueldos y salarios",                               G, 3, "64",  True),
    ("641", "Indemnizaciones",                                  G, 3, "64",  True),
    ("642", "Seguridad Social a cargo de la entidad",           G, 3, "64",  True),
    ("643", "Retribuciones a largo plazo mediante sistemas de aportación definida", G, 3, "64", True),
    ("644", "Retribuciones al personal con acciones o participaciones propias", G, 3, "64", True),
    ("645", "Retribuciones a largo plazo mediante sistemas de prestación definida", G, 3, "64", True),
    ("649", "Otros gastos sociales",                            G, 3, "64",  True),

    ("65",  "Otros gastos de gestión",                          G, 2, "6",   False),
    ("650", "Pérdidas de créditos por actividades propias incobrables", G, 3, "65", True),
    ("651", "Resultados de operaciones con activos no corrientes", G, 3, "65", True),
    ("659", "Otros gastos de gestión corriente",                G, 3, "65",  True),

    ("66",  "Gastos financieros",                               G, 2, "6",   False),
    ("660", "Gastos por intereses de deudas a largo plazo",     G, 3, "66",  True),
    ("661", "Intereses de obligaciones y bonos",                G, 3, "66",  True),
    ("662", "Intereses de deudas a corto plazo",                G, 3, "66",  True),
    ("664", "Gastos por dividendos de acciones o participaciones", G, 3, "66", True),
    ("665", "Descuentos sobre ventas por pronto pago",          G, 3, "66",  True),
    ("666", "Pérdidas en participaciones y valores representativos de deuda", G, 3, "66", True),
    ("668", "Diferencias negativas de cambio",                  G, 3, "66",  True),
    ("669", "Otros gastos financieros",                         G, 3, "66",  True),

    ("67",  "Pérdidas procedentes de activos no corrientes",    G, 2, "6",   False),
    ("671", "Pérdidas procedentes del inmovilizado intangible", G, 3, "67",  True),
    ("672", "Pérdidas procedentes del inmovilizado material",   G, 3, "67",  True),

    ("68",  "Dotaciones para amortizaciones",                   G, 2, "6",   False),
    ("680", "Amortización del inmovilizado intangible",         G, 3, "68",  True),
    ("681", "Amortización del inmovilizado material",           G, 3, "68",  True),

    ("69",  "Pérdidas por deterioro y otras dotaciones",        G, 2, "6",   False),
    ("690", "Pérdidas por deterioro del inmovilizado intangible", G, 3, "69", True),
    ("691", "Pérdidas por deterioro del inmovilizado material", G, 3, "69",  True),
    ("694", "Pérdidas por deterioro de créditos por actividades propias", G, 3, "69", True),

    # ══════════════════════════════════════════════════════════════════════════
    # GRUPO 7 — Ingresos
    # ══════════════════════════════════════════════════════════════════════════
    ("7",   "INGRESOS",                                         I, 1, None,  False),

    ("72",  "Ingresos de la actividad propia",                  I, 2, "7",   False),
    ("720", "Ventas y prestaciones de servicios de actividades propias", I, 3, "72", True),
    ("721", "Cuotas de socios y afiliados",                     I, 3, "72",  True),
    ("722", "Ingresos por cuotas de acceso y formación",        I, 3, "72",  True),
    ("723", "Ingresos por venta de publicaciones",              I, 3, "72",  True),
    ("724", "Ingresos por eventos y actos públicos",            I, 3, "72",  True),
    ("725", "Ingresos por servicios a afiliados",               I, 3, "72",  True),

    ("73",  "Donaciones y legados corrientes",                  I, 2, "7",   False),
    ("730", "Donaciones y legados corrientes imputados a resultados", I, 3, "73", True),
    ("731", "Subvenciones, donaciones y legados imputados al excedente del ejercicio", I, 3, "73", True),

    ("74",  "Subvenciones e ingresos excepcionales",            I, 2, "7",   False),
    ("740", "Subvenciones oficiales a la explotación",          I, 3, "74",  True),
    ("741", "Otras subvenciones a la explotación",              I, 3, "74",  True),
    ("742", "Subvenciones, donaciones y legados de capital imputados al excedente", I, 3, "74", True),

    ("75",  "Otros ingresos de gestión",                        I, 2, "7",   False),
    ("751", "Ingresos por arrendamientos",                      I, 3, "75",  True),
    ("752", "Ingresos por propiedad industrial cedida en explotación", I, 3, "75", True),
    ("759", "Ingresos por servicios al personal",               I, 3, "75",  True),

    ("76",  "Ingresos financieros",                             I, 2, "7",   False),
    ("760", "Ingresos de participaciones en instrumentos de patrimonio", I, 3, "76", True),
    ("761", "Ingresos de valores representativos de deuda",     I, 3, "76",  True),
    ("762", "Ingresos de créditos a largo plazo",               I, 3, "76",  True),
    ("763", "Ingresos de créditos a corto plazo",               I, 3, "76",  True),
    ("765", "Descuentos sobre compras por pronto pago",         I, 3, "76",  True),
    ("768", "Diferencias positivas de cambio",                  I, 3, "76",  True),
    ("769", "Otros ingresos financieros",                       I, 3, "76",  True),

    ("77",  "Beneficios procedentes de activos no corrientes",  I, 2, "7",   False),
    ("771", "Beneficios procedentes del inmovilizado intangible", I, 3, "77", True),
    ("772", "Beneficios procedentes del inmovilizado material", I, 3, "77",  True),

    ("79",  "Excesos y aplicaciones de provisiones y pérdidas por deterioro", I, 2, "7", False),
    ("790", "Exceso de provisiones",                            I, 3, "79",  True),
    ("794", "Reversión del deterioro de créditos por actividades propias", I, 3, "79", True),

    # Cuenta especial para cuadre de resultados
    ("749", "Otros ingresos de gestión corriente",              I, 3, "75",  True),
]


async def cargar_plan_cuentas_esfl(session: AsyncSession) -> int:
    """Carga el plan de cuentas PCESFL 2013. Idempotente."""
    result = await session.execute(select(CuentaContable))
    existentes: dict[str, CuentaContable] = {
        c.codigo: c for c in result.scalars().all()
    }

    creadas = 0
    # Procesar por nivel para garantizar que los padres existen antes que los hijos.
    # Tras cada nivel, flush() asigna IDs de BD a las cuentas recién añadidas.
    filas_por_nivel: dict[int, list] = {}
    for row in CUENTAS_PCESFL:
        filas_por_nivel.setdefault(row[3], []).append(row)

    for nivel in sorted(filas_por_nivel.keys()):
        for codigo, nombre, tipo, _nivel, padre_codigo, permite_asiento in filas_por_nivel[nivel]:
            if codigo in existentes:
                continue

            padre_id = None
            if padre_codigo:
                padre = existentes.get(padre_codigo)
                if padre:
                    padre_id = padre.id

            cuenta = CuentaContable(
                codigo=codigo,
                nombre=nombre,
                tipo=tipo,
                nivel=nivel,
                padre_id=padre_id,
                permite_asiento=permite_asiento,
            )
            session.add(cuenta)
            existentes[codigo] = cuenta
            creadas += 1
        # Flush al terminar cada nivel para que las cuentas tengan id asignado
        # antes de que el siguiente nivel las referencie como padre.
        await session.flush()

    await session.commit()
    print(f"[plan_cuentas_esfl] {creadas} cuentas creadas (PCESFL 2013).")
    return creadas


async def seed():
    async with async_session() as session:
        creadas = await cargar_plan_cuentas_esfl(session)
        if creadas == 0:
            print("[plan_cuentas_esfl] Plan de cuentas ya estaba cargado.")


if __name__ == "__main__":
    asyncio.run(seed())
