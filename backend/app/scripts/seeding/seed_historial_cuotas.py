"""Seed: historial de cuotas pagadas para los socios mockeados.

Para cada socio (no anonimizado, con agrupación) genera, por cada ejercicio de
su periodo de militancia [alta .. baja|hoy], la cadena contable completa:

    CuotaAnual (Cobrada)  →  Recibo COBRADO  →  ApunteCaja (INGRESO/CUOTA)
                                             →  AsientoContable (Debe 572 / Haber 721)

Inserción MASIVA (executemany) para que ~16k cuotas tarden segundos, no horas.
Idempotente: salta los pares (socio, ejercicio) que ya tienen cuota.
Determinista: semilla fija para las fechas de cobro.

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_historial_cuotas
"""
import asyncio
import random
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import text

from app.core.database import async_session

EJERCICIO_MIN = 2009
EJERCICIO_MAX = date.today().year
IMPORTE = Decimal("30.00")
SEED = 73


async def seed():
    rnd = random.Random(SEED)
    async with async_session() as session:
        # ── Resolución de referencias fijas ─────────────────────────────────
        cb_id = (await session.execute(text(
            "SELECT id FROM cuentas_bancarias WHERE activa=true LIMIT 1"
        ))).scalar()
        estado_cobrada = (await session.execute(text(
            "SELECT id FROM estados_cuota WHERE nombre='Cobrada' LIMIT 1"
        ))).scalar()
        cuenta_debe = (await session.execute(text(
            "SELECT id FROM cuentas_contables WHERE codigo='572' LIMIT 1"
        ))).scalar()
        cuenta_haber = (await session.execute(text(
            "SELECT id FROM cuentas_contables WHERE codigo='721' LIMIT 1"
        ))).scalar()
        if not all([cb_id, estado_cobrada, cuenta_debe, cuenta_haber]):
            print("✗ Faltan referencias (cuenta bancaria / estado / cuentas 572-721).")
            return

        # Socios objetivo.
        socios = (await session.execute(text(
            "SELECT id, fecha_alta, fecha_baja, agrupacion_id FROM miembros "
            "WHERE datos_anonimizados=false AND eliminado=false "
            "AND agrupacion_id IS NOT NULL AND fecha_alta IS NOT NULL"
        ))).all()

        # Pares (miembro, ejercicio) ya existentes.
        existentes = {
            (r[0], r[1]) for r in (await session.execute(text(
                "SELECT miembro_id, ejercicio FROM cuotas_anuales"
            ))).all()
        }

        # Contadores correlativos por ejercicio.
        n_asiento = {
            r[0]: r[1] for r in (await session.execute(text(
                "SELECT ejercicio, COALESCE(MAX(numero_asiento),0) FROM asientos_contables GROUP BY ejercicio"
            ))).all()
        }
        # Todos los números de recibo ocupados (datos legacy irregulares) — el
        # generador salta cualquier número ya en uso.
        usados_rec = {
            r[0] for r in (await session.execute(text(
                "SELECT numero_recibo FROM recibos"
            ))).all()
        }
        # Base alta para los recibos del seed: por encima de cualquier número
        # real (los ejercicios reales no superan ~1000 recibos/año).
        BASE_REC = 50000
        n_recibo = {}

        def siguiente_recibo(anio):
            while True:
                n_recibo[anio] = n_recibo.get(anio, BASE_REC) + 1
                num = f"REC-{anio}-{n_recibo[anio]:05d}"
                if num not in usados_rec:
                    usados_rec.add(num)
                    return num

        cuotas, recibos, asientos, apuntes_caja, apuntes_cont = [], [], [], [], []

        for mid, f_alta, f_baja, agr in socios:
            ini = max(f_alta.year, EJERCICIO_MIN)
            fin = min(f_baja.year if f_baja else EJERCICIO_MAX, EJERCICIO_MAX)
            for ej in range(ini, fin + 1):
                if (mid, ej) in existentes:
                    continue
                existentes.add((mid, ej))

                f_cobro = date(ej, rnd.randint(2, 11), rnd.randint(1, 28))
                cuota_id = uuid.uuid4()
                asiento_id = uuid.uuid4()
                apunte_id = uuid.uuid4()
                n_asiento[ej] = n_asiento.get(ej, 0) + 1
                numero_rec = siguiente_recibo(ej)
                concepto = f"Cuota {ej} cobrada ({numero_rec})"

                cuotas.append({
                    "id": cuota_id, "miembro_id": mid, "ejercicio": ej, "agrupacion_id": agr,
                    "importe": IMPORTE, "importe_pagado": IMPORTE, "gastos_gestion": Decimal("0.00"),
                    "estado_id": estado_cobrada, "codigo_cuota": "General", "modo_ingreso": "SEPA",
                    "fecha_pago": f_cobro, "fecha_vencimiento": date(ej, 3, 31),
                })
                recibos.append({
                    "id": uuid.uuid4(), "numero_recibo": numero_rec, "ejercicio": ej,
                    "tipo": "CUOTA_ORDINARIA", "concepto": f"Cuota ordinaria ejercicio {ej}",
                    "miembro_id": mid, "cuota_id": cuota_id, "importe": IMPORTE,
                    "importe_pagado": IMPORTE, "estado": "COBRADO", "modo_cobro": "TRANSFERENCIA",
                    "fecha_emision": date(ej, 1, 15), "fecha_cobro": f_cobro,
                })
                asientos.append({
                    "id": asiento_id, "ejercicio": ej, "numero_asiento": n_asiento[ej],
                    "fecha": f_cobro, "glosa": concepto, "tipo_asiento": "GESTION",
                    "estado": "CONFIRMADO",
                })
                apuntes_caja.append({
                    "id": apunte_id, "cuenta_bancaria_id": cb_id, "fecha": f_cobro,
                    "importe": IMPORTE, "tipo": "INGRESO", "origen": "CUOTA", "concepto": concepto,
                    "entidad_origen_tipo": "cuota_anual", "entidad_origen_id": cuota_id,
                    "asiento_id": asiento_id, "conciliado": False,
                })
                apuntes_cont.append({
                    "id": uuid.uuid4(), "asiento_id": asiento_id, "cuenta_id": cuenta_debe,
                    "debe": IMPORTE, "haber": Decimal("0.00"), "concepto": concepto,
                })
                apuntes_cont.append({
                    "id": uuid.uuid4(), "asiento_id": asiento_id, "cuenta_id": cuenta_haber,
                    "debe": Decimal("0.00"), "haber": IMPORTE, "concepto": concepto,
                })

        # ── Inserción masiva (orden de FK) ──────────────────────────────────
        if cuotas:
            await session.execute(text(
                "INSERT INTO cuotas_anuales (id, miembro_id, ejercicio, agrupacion_id, importe, "
                "importe_pagado, gastos_gestion, estado_id, codigo_cuota, modo_ingreso, fecha_pago, "
                "fecha_vencimiento, eliminado) VALUES (:id,:miembro_id,:ejercicio,:agrupacion_id,"
                ":importe,:importe_pagado,:gastos_gestion,:estado_id,:codigo_cuota,:modo_ingreso,"
                ":fecha_pago,:fecha_vencimiento,false)"
            ), cuotas)
            await session.execute(text(
                "INSERT INTO asientos_contables (id, ejercicio, numero_asiento, fecha, glosa, "
                "tipo_asiento, estado, eliminado) VALUES (:id,:ejercicio,:numero_asiento,:fecha,"
                ":glosa,:tipo_asiento,:estado,false)"
            ), asientos)
            await session.execute(text(
                "INSERT INTO recibos (id, numero_recibo, ejercicio, tipo, concepto, miembro_id, "
                "cuota_id, importe, importe_pagado, estado, modo_cobro, fecha_emision, fecha_cobro, "
                "eliminado) VALUES (:id,:numero_recibo,:ejercicio,:tipo,:concepto,:miembro_id,"
                ":cuota_id,:importe,:importe_pagado,:estado,:modo_cobro,:fecha_emision,:fecha_cobro,false)"
            ), recibos)
            await session.execute(text(
                "INSERT INTO apuntes_caja (id, cuenta_bancaria_id, fecha, importe, tipo, origen, "
                "concepto, entidad_origen_tipo, entidad_origen_id, asiento_id, conciliado, eliminado) "
                "VALUES (:id,:cuenta_bancaria_id,:fecha,:importe,:tipo,:origen,:concepto,"
                ":entidad_origen_tipo,:entidad_origen_id,:asiento_id,:conciliado,false)"
            ), apuntes_caja)
            await session.execute(text(
                "INSERT INTO apuntes_contables (id, asiento_id, cuenta_id, debe, haber, concepto, "
                "eliminado) VALUES (:id,:asiento_id,:cuenta_id,:debe,:haber,:concepto,false)"
            ), apuntes_cont)
            await session.commit()

        # ── Pasada 2: cuotas pagadas preexistentes sin cadena contable ──────
        # Coherencia: toda cuota pagada debe tener recibo + apunte + asiento.
        orphans = (await session.execute(text(
            "SELECT c.id, c.miembro_id, c.ejercicio, c.importe, c.fecha_pago "
            "FROM cuotas_anuales c WHERE c.importe_pagado > 0 "
            "AND NOT EXISTS (SELECT 1 FROM recibos r WHERE r.cuota_id = c.id)"
        ))).all()

        recibos2, asientos2, apuntes_caja2, apuntes_cont2 = [], [], [], []
        for cid, mid, ej, imp, fpago in orphans:
            f_cobro = fpago or date(ej, 6, 15)
            asiento_id = uuid.uuid4()
            n_asiento[ej] = n_asiento.get(ej, 0) + 1
            numero_rec = siguiente_recibo(ej)
            concepto = f"Cuota {ej} cobrada ({numero_rec})"
            recibos2.append({
                "id": uuid.uuid4(), "numero_recibo": numero_rec, "ejercicio": ej,
                "tipo": "CUOTA_ORDINARIA", "concepto": f"Cuota ordinaria ejercicio {ej}",
                "miembro_id": mid, "cuota_id": cid, "importe": imp, "importe_pagado": imp,
                "estado": "COBRADO", "modo_cobro": "TRANSFERENCIA",
                "fecha_emision": date(ej, 1, 15), "fecha_cobro": f_cobro,
            })
            asientos2.append({
                "id": asiento_id, "ejercicio": ej, "numero_asiento": n_asiento[ej],
                "fecha": f_cobro, "glosa": concepto, "tipo_asiento": "GESTION",
                "estado": "CONFIRMADO",
            })
            apuntes_caja2.append({
                "id": uuid.uuid4(), "cuenta_bancaria_id": cb_id, "fecha": f_cobro,
                "importe": imp, "tipo": "INGRESO", "origen": "CUOTA", "concepto": concepto,
                "entidad_origen_tipo": "cuota_anual", "entidad_origen_id": cid,
                "asiento_id": asiento_id, "conciliado": False,
            })
            apuntes_cont2.append({
                "id": uuid.uuid4(), "asiento_id": asiento_id, "cuenta_id": cuenta_debe,
                "debe": imp, "haber": Decimal("0.00"), "concepto": concepto,
            })
            apuntes_cont2.append({
                "id": uuid.uuid4(), "asiento_id": asiento_id, "cuenta_id": cuenta_haber,
                "debe": Decimal("0.00"), "haber": imp, "concepto": concepto,
            })

        if recibos2:
            await session.execute(text(
                "INSERT INTO asientos_contables (id, ejercicio, numero_asiento, fecha, glosa, "
                "tipo_asiento, estado, eliminado) VALUES (:id,:ejercicio,:numero_asiento,:fecha,"
                ":glosa,:tipo_asiento,:estado,false)"
            ), asientos2)
            await session.execute(text(
                "INSERT INTO recibos (id, numero_recibo, ejercicio, tipo, concepto, miembro_id, "
                "cuota_id, importe, importe_pagado, estado, modo_cobro, fecha_emision, fecha_cobro, "
                "eliminado) VALUES (:id,:numero_recibo,:ejercicio,:tipo,:concepto,:miembro_id,"
                ":cuota_id,:importe,:importe_pagado,:estado,:modo_cobro,:fecha_emision,:fecha_cobro,false)"
            ), recibos2)
            await session.execute(text(
                "INSERT INTO apuntes_caja (id, cuenta_bancaria_id, fecha, importe, tipo, origen, "
                "concepto, entidad_origen_tipo, entidad_origen_id, asiento_id, conciliado, eliminado) "
                "VALUES (:id,:cuenta_bancaria_id,:fecha,:importe,:tipo,:origen,:concepto,"
                ":entidad_origen_tipo,:entidad_origen_id,:asiento_id,:conciliado,false)"
            ), apuntes_caja2)
            await session.execute(text(
                "INSERT INTO apuntes_contables (id, asiento_id, cuenta_id, debe, haber, concepto, "
                "eliminado) VALUES (:id,:asiento_id,:cuenta_id,:debe,:haber,:concepto,false)"
            ), apuntes_cont2)
            await session.commit()

        print(f"✓ Historial de cuotas:")
        print(f"  Pasada 1 — cuotas nuevas:  {len(cuotas)} cuotas + cadena contable.")
        print(f"  Pasada 2 — pagadas sin asiento: {len(recibos2)} recibos + asientos generados.")


if __name__ == "__main__":
    asyncio.run(seed())
