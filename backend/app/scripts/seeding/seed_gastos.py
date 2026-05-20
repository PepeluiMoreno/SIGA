"""Seed: gastos de explotación por ejercicio, imputados a actividades de campaña.

Para cada ejercicio genera gastos (arrendamiento, suministros, servicios,
publicidad…) que suman ~84-95 % de los ingresos por cuotas de ese año, de modo
que cada ejercicio cierre con un pequeño excedente positivo.

Regla de imputación: si el ejercicio tiene actividades de campaña, cada gasto se
imputa a una de ellas (`apunte_caja.actividad_id` + `campania_id`, y el apunte
contable del grupo 6 lleva `actividad_id`). Los ejercicios sin actividades de
campaña reciben gastos generales sin imputar.

Cada gasto: ApunteCaja (GASTO) + AsientoContable (Debe 6xx / Haber 572).
Inserción masiva. Idempotente: salta ejercicios que ya tienen gastos.

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_gastos
"""
import asyncio
import random
import uuid
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import text

from app.core.database import async_session

SEED = 91
CENT = Decimal("0.01")

# (código cuenta gasto, concepto, peso, nº apuntes/año, ámbito de imputación)
#   PERM → actividad permanente (gasto estructural)
#   CAMP → actividad de campaña del ejercicio
CATEGORIAS = [
    ("621", "Arrendamiento del local", 0.30, 12, "PERM"),
    ("628", "Suministros (luz, agua, telefonía)", 0.14, 6, "PERM"),
    ("623", "Servicios profesionales (gestoría y asesoría)", 0.16, 4, "PERM"),
    ("627", "Publicidad, comunicación y actos", 0.13, 4, "CAMP"),
    ("629", "Otros servicios", 0.13, 5, "CAMP"),
    ("622", "Reparaciones y conservación", 0.06, 2, "PERM"),
    ("626", "Comisiones y servicios bancarios", 0.04, 4, "PERM"),
    ("625", "Primas de seguros", 0.04, 1, "PERM"),
]


async def seed():
    rnd = random.Random(SEED)
    async with async_session() as session:
        cb_id = (await session.execute(text(
            "SELECT id FROM cuentas_bancarias WHERE activa=true LIMIT 1"
        ))).scalar()
        cuenta_572 = (await session.execute(text(
            "SELECT id FROM cuentas_contables WHERE codigo='572' LIMIT 1"
        ))).scalar()
        cuentas_gasto = {
            cod: (await session.execute(text(
                "SELECT id FROM cuentas_contables WHERE codigo=:c LIMIT 1"
            ), {"c": cod})).scalar()
            for cod, _, _, _, _ in CATEGORIAS
        }
        if not cb_id or not cuenta_572 or not all(cuentas_gasto.values()):
            print("✗ Faltan cuentas (banco / 572 / grupo 6).")
            return

        # Ingresos por cuotas (cuenta 721) por ejercicio.
        ingresos = {
            r[0]: r[1] for r in (await session.execute(text(
                "SELECT a.ejercicio, sum(ac.haber) FROM asientos_contables a "
                "JOIN apuntes_contables ac ON ac.asiento_id=a.id "
                "JOIN cuentas_contables c ON c.id=ac.cuenta_id "
                "WHERE c.codigo='721' GROUP BY a.ejercicio"
            ))).all()
        }
        # Actividades de campaña por ejercicio (imputación de gastos de campaña).
        act_por_ej = {}
        for aid, camp, ej in (await session.execute(text(
            "SELECT id, campania_id, "
            "EXTRACT(YEAR FROM coalesce(fecha_inicio, fecha_creacion))::int "
            "FROM actividades WHERE campania_id IS NOT NULL AND eliminado=false"
        ))).all():
            act_por_ej.setdefault(int(ej), []).append((aid, camp))

        # Actividades permanentes (imputación de gastos estructurales).
        perm_acts = [r[0] for r in (await session.execute(text(
            "SELECT id FROM actividades WHERE caracter='PERMANENTE' AND eliminado=false"
        ))).all()]

        # Ejercicios que ya tienen gastos (idempotencia).
        con_gastos = {
            r[0] for r in (await session.execute(text(
                "SELECT DISTINCT a.ejercicio FROM asientos_contables a "
                "JOIN apuntes_contables ac ON ac.asiento_id=a.id "
                "JOIN cuentas_contables c ON c.id=ac.cuenta_id WHERE c.codigo LIKE '6%'"
            ))).all()
        }
        n_asiento = {
            r[0]: r[1] for r in (await session.execute(text(
                "SELECT ejercicio, COALESCE(MAX(numero_asiento),0) "
                "FROM asientos_contables GROUP BY ejercicio"
            ))).all()
        }

        asientos, apuntes_caja, apuntes_cont = [], [], []
        total_gastos = Decimal("0.00")
        n_imputados = 0
        ejercicios_hechos = 0

        for ej in sorted(ingresos):
            if ej in con_gastos:
                continue
            ingreso = Decimal(str(ingresos[ej]))
            if ingreso <= 0:
                continue
            objetivo = (ingreso * Decimal(str(rnd.uniform(0.84, 0.95)))).quantize(CENT)
            acts = act_por_ej.get(ej, [])

            for cod, concepto_base, peso, n_ap, ambito in CATEGORIAS:
                cat_total = (objetivo * Decimal(str(peso))).quantize(CENT)
                if cat_total <= 0:
                    continue
                base = (cat_total / n_ap).quantize(CENT, rounding=ROUND_HALF_UP)
                for k in range(n_ap):
                    imp = cat_total - base * (n_ap - 1) if k == n_ap - 1 else base
                    if imp <= 0:
                        continue
                    f = date(ej, rnd.randint(1, 12), rnd.randint(1, 28))
                    asiento_id = uuid.uuid4()
                    n_asiento[ej] = n_asiento.get(ej, 0) + 1
                    glosa = f"{concepto_base} {ej}"
                    # Regla de imputación: estructural → actividad permanente;
                    # de campaña → actividad de campaña del ejercicio.
                    if ambito == "CAMP" and acts:
                        act_id, camp_id = rnd.choice(acts)
                    elif perm_acts:
                        act_id, camp_id = rnd.choice(perm_acts), None
                    else:
                        act_id, camp_id = None, None
                    if act_id:
                        n_imputados += 1

                    asientos.append({
                        "id": asiento_id, "ejercicio": ej, "numero_asiento": n_asiento[ej],
                        "fecha": f, "glosa": glosa, "tipo_asiento": "GESTION",
                        "estado": "CONFIRMADO",
                    })
                    apuntes_caja.append({
                        "id": uuid.uuid4(), "cuenta_bancaria_id": cb_id, "fecha": f,
                        "importe": imp, "tipo": "GASTO", "concepto": glosa,
                        "asiento_id": asiento_id, "conciliado": True,
                        "actividad_id": act_id, "campania_id": camp_id,
                    })
                    apuntes_cont.append({
                        "id": uuid.uuid4(), "asiento_id": asiento_id,
                        "cuenta_id": cuentas_gasto[cod], "debe": imp,
                        "haber": Decimal("0.00"), "concepto": glosa,
                        "actividad_id": act_id,
                    })
                    apuntes_cont.append({
                        "id": uuid.uuid4(), "asiento_id": asiento_id,
                        "cuenta_id": cuenta_572, "debe": Decimal("0.00"),
                        "haber": imp, "concepto": glosa, "actividad_id": None,
                    })
                    total_gastos += imp
            ejercicios_hechos += 1

        if not asientos:
            print("Sin ejercicios nuevos para sembrar gastos (todo al día).")
            return

        await session.execute(text(
            "INSERT INTO asientos_contables (id, ejercicio, numero_asiento, fecha, glosa, "
            "tipo_asiento, estado, eliminado) VALUES (:id,:ejercicio,:numero_asiento,:fecha,"
            ":glosa,:tipo_asiento,:estado,false)"
        ), asientos)
        await session.execute(text(
            "INSERT INTO apuntes_caja (id, cuenta_bancaria_id, fecha, importe, tipo, concepto, "
            "asiento_id, conciliado, actividad_id, campania_id, eliminado) "
            "VALUES (:id,:cuenta_bancaria_id,:fecha,:importe,:tipo,:concepto,:asiento_id,"
            ":conciliado,:actividad_id,:campania_id,false)"
        ), apuntes_caja)
        await session.execute(text(
            "INSERT INTO apuntes_contables (id, asiento_id, cuenta_id, debe, haber, concepto, "
            "actividad_id, eliminado) VALUES (:id,:asiento_id,:cuenta_id,:debe,:haber,:concepto,"
            ":actividad_id,false)"
        ), apuntes_cont)
        await session.commit()

        print(f"✓ Gastos sembrados en {ejercicios_hechos} ejercicios — "
              f"{len(asientos)} asientos, total {total_gastos} € "
              f"({n_imputados} imputados a actividades de campaña).")


if __name__ == "__main__":
    asyncio.run(seed())
