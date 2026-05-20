"""Seed: cobros históricos para el módulo económico.

Recorre las cuotas existentes 2021-2025 y, según su estado en BD:
- Si está pagada → emite Recibo COBRADO + ApunteCaja + asiento contable (Debe 572 / Haber 721)
- Si no está pagada → emite Recibo FALLIDO con código de rechazo SEPA aleatorio

Idempotente: salta cuotas que ya tienen un recibo emitido del ejercicio.
Determinista: usa semilla fija para fechas de cobro y códigos SEPA.

Uso (dentro del contenedor backend):
  docker exec siga_dev_backend python -m app.scripts.seeding.cobros_historicos
"""

import asyncio
import random
from datetime import date
from decimal import Decimal

from sqlalchemy import select, func

from app.core.database import async_session
from app.modules.economico.models.cuotas import CuotaAnual
from app.modules.economico.models.recibos import Recibo
from app.modules.economico.models.tesoreria import (
    ApunteCaja,
    CuentaBancaria,
    OrigenApunte,
    TipoApunte,
)
from app.modules.economico.services.registro_contable import RegistroContable
from app.modules.economico.core.feature_flags import is_version_completa


EJERCICIOS = list(range(2021, 2026))  # 2021–2025
SEED = 42

CODIGOS_SEPA_FALLIDO = [
    ("AM04", "Fondos insuficientes"),
    ("AC04", "Cuenta cerrada"),
    ("MD01", "Sin mandato vigente"),
    ("MS02", "Operación rechazada por el deudor"),
    ("AC13", "Tipo de cuenta inválido"),
]


async def seed_cobros_historicos() -> None:
    async with async_session() as session:
        if not await is_version_completa(session):
            print("✗ org.contabilidad_compleja=false. Activa la contabilidad completa antes de ejecutar este seed.")
            return

        rnd = random.Random(SEED)

        cb = (await session.execute(
            select(CuentaBancaria).where(CuentaBancaria.activa).limit(1)
        )).scalars().first()
        if not cb:
            print("✗ No hay cuenta bancaria activa.")
            return
        print(f"Cuenta bancaria destino: {cb.nombre} (IBAN {cb.iban})")

        registro = RegistroContable(session)

        tot_cobrados = 0
        tot_fallidos = 0

        for ejercicio in EJERCICIOS:
            print(f"\n── Ejercicio {ejercicio} ──")

            # Cuotas ya con recibo (idempotencia)
            existentes = (await session.execute(
                select(Recibo.cuota_id).where(Recibo.ejercicio == ejercicio)
            )).all()
            con_recibo = {row[0] for row in existentes if row[0]}

            cuotas_q = await session.execute(
                select(CuotaAnual)
                .where(CuotaAnual.ejercicio == ejercicio)
                .where(CuotaAnual.importe > 0)
            )
            cuotas = [c for c in cuotas_q.scalars().all() if c.id not in con_recibo]

            if not cuotas:
                print("  Sin cuotas nuevas para procesar.")
                continue

            # Contador correlativo continuando lo que ya haya en BD
            cnt = (await session.execute(
                select(func.count(Recibo.id)).where(Recibo.ejercicio == ejercicio)
            )).scalar() or 0
            contador = cnt + 1

            fecha_emision = date(ejercicio, 1, 15)
            cob_eje, fal_eje = 0, 0

            for cuota in cuotas:
                numero = f"REC-{ejercicio}-{contador:05d}"
                contador += 1

                pagada = cuota.importe_pagado >= cuota.importe

                if pagada:
                    mes = rnd.randint(1, 12)
                    dia = rnd.randint(1, 28)
                    fecha_cobro = date(ejercicio, mes, dia)
                    if fecha_cobro < fecha_emision:
                        fecha_cobro = fecha_emision

                    recibo = Recibo(
                        numero_recibo=numero,
                        ejercicio=ejercicio,
                        tipo="CUOTA_ORDINARIA",
                        concepto=f"Cuota ordinaria ejercicio {ejercicio}",
                        miembro_id=cuota.miembro_id,
                        cuota_id=cuota.id,
                        importe=cuota.importe,
                        importe_pagado=cuota.importe,
                        estado="COBRADO",
                        modo_cobro="TRANSFERENCIA",
                        fecha_emision=fecha_emision,
                        fecha_cobro=fecha_cobro,
                    )
                    session.add(recibo)

                    apunte = ApunteCaja(
                        cuenta_bancaria_id=cb.id,
                        fecha=fecha_cobro,
                        importe=cuota.importe,
                        tipo=TipoApunte.INGRESO,
                        origen=OrigenApunte.CUOTA,
                        concepto=f"Cuota {ejercicio} cobrada ({numero})",
                        entidad_origen_tipo="cuota_anual",
                        entidad_origen_id=cuota.id,
                    )
                    session.add(apunte)
                    await session.flush()

                    # Genera asiento Debe 572 / Haber 721 vía regla CUOTA/INGRESO
                    await registro.generar_asiento_para_apunte(apunte)
                    cob_eje += 1
                else:
                    cod, motivo = rnd.choice(CODIGOS_SEPA_FALLIDO)
                    recibo = Recibo(
                        numero_recibo=numero,
                        ejercicio=ejercicio,
                        tipo="CUOTA_ORDINARIA",
                        concepto=f"Cuota ordinaria ejercicio {ejercicio}",
                        miembro_id=cuota.miembro_id,
                        cuota_id=cuota.id,
                        importe=cuota.importe,
                        importe_pagado=Decimal("0.00"),
                        estado="FALLIDO",
                        modo_cobro="SEPA",
                        fecha_emision=fecha_emision,
                        observaciones=f"FALLIDO [{cod}]: {motivo}",
                    )
                    session.add(recibo)
                    fal_eje += 1

            await session.commit()
            print(f"  ✓ Cobrados: {cob_eje}   Fallidos: {fal_eje}   Total: {cob_eje + fal_eje}")
            tot_cobrados += cob_eje
            tot_fallidos += fal_eje

        total = tot_cobrados + tot_fallidos
        if total:
            print(f"\n══ RESUMEN ══")
            print(f"Recibos cobrados:  {tot_cobrados}  ({tot_cobrados * 100 // total}%)")
            print(f"Recibos fallidos:  {tot_fallidos}  ({tot_fallidos * 100 // total}%)")
            print(f"Total emitidos:    {total}")
        else:
            print("\nSin recibos nuevos generados.")


if __name__ == "__main__":
    asyncio.run(seed_cobros_historicos())
