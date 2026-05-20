"""Seed: cierre simulado de ejercicios pasados.

Por cada ejercicio cerrado (2021-2024) crea un único movimiento de GASTO en la
cuenta bancaria principal que iguala los ingresos cobrados de ese ejercicio.
Resultado: el saldo en cuenta queda únicamente con lo cobrado del ejercicio en
curso (2025), simulando que cada año cerró a cero (gastos = ingresos).

Idempotente: salta si ya existe un apunte con concepto que empiece por
"Cierre simulado ejercicio X — ".

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.cierre_simulado_ejercicios
"""

import asyncio
from datetime import date
from decimal import Decimal

from sqlalchemy import select, func

from app.core.database import async_session
from app.modules.economico.models.tesoreria import (
    ApunteCaja,
    CuentaBancaria,
    OrigenApunte,
    TipoApunte,
)
from app.modules.economico.services.registro_contable import RegistroContable
from app.modules.economico.core.feature_flags import is_version_completa


EJERCICIOS_A_CERRAR = [2021, 2022, 2023, 2024]


async def cierre_simulado() -> None:
    async with async_session() as session:
        if not await is_version_completa(session):
            print("✗ org.contabilidad_compleja=false. Activa la contabilidad completa antes.")
            return

        cb = (await session.execute(
            select(CuentaBancaria).where(CuentaBancaria.activa).limit(1)
        )).scalars().first()
        if not cb:
            print("✗ No hay cuenta bancaria activa.")
            return
        print(f"Cuenta bancaria: {cb.nombre} (saldo actual: {cb.saldo_actual or 0} €)")

        registro = RegistroContable(session)

        for ejercicio in EJERCICIOS_A_CERRAR:
            # Idempotencia: ¿ya hay cierre simulado de este ejercicio?
            existente_q = await session.execute(
                select(ApunteCaja).where(
                    ApunteCaja.concepto.like(f"Cierre simulado ejercicio {ejercicio}%")
                ).limit(1)
            )
            if existente_q.scalars().first():
                print(f"  · {ejercicio}: ya cerrado simuladamente, salto")
                continue

            # Total ingresado en ese ejercicio
            total_r = await session.execute(
                select(func.coalesce(func.sum(ApunteCaja.importe), 0))
                .where(ApunteCaja.tipo == TipoApunte.INGRESO)
                .where(ApunteCaja.cuenta_bancaria_id == cb.id)
                .where(func.extract('year', ApunteCaja.fecha) == ejercicio)
            )
            total_ingreso = Decimal(str(total_r.scalar() or 0))

            if total_ingreso <= Decimal("0"):
                print(f"  · {ejercicio}: sin ingresos, salto")
                continue

            apunte = ApunteCaja(
                cuenta_bancaria_id=cb.id,
                fecha=date(ejercicio, 12, 31),
                importe=total_ingreso,
                tipo=TipoApunte.GASTO,
                origen=None,  # dispara la regla comodín (null)/GASTO → 629/572
                concepto=f"Cierre simulado ejercicio {ejercicio} — gastos del ejercicio",
            )
            session.add(apunte)
            await session.flush()

            asiento = await registro.generar_asiento_para_apunte(apunte)
            await session.commit()
            print(f"  ✓ {ejercicio}: gasto de {total_ingreso} € (asiento {asiento.id if asiento else 'sin'})")

        # Recalcular saldo
        await session.refresh(cb)
        ingreso_q = await session.execute(
            select(func.coalesce(func.sum(ApunteCaja.importe), 0))
            .where(ApunteCaja.tipo == TipoApunte.INGRESO)
            .where(ApunteCaja.cuenta_bancaria_id == cb.id)
        )
        gasto_q = await session.execute(
            select(func.coalesce(func.sum(ApunteCaja.importe), 0))
            .where(ApunteCaja.tipo == TipoApunte.GASTO)
            .where(ApunteCaja.cuenta_bancaria_id == cb.id)
        )
        ingresos = Decimal(str(ingreso_q.scalar() or 0))
        gastos = Decimal(str(gasto_q.scalar() or 0))
        saldo = ingresos - gastos
        print(f"\n══ Saldo final calculado en {cb.nombre} ══")
        print(f"   Ingresos totales:  {ingresos} €")
        print(f"   Gastos totales:    {gastos} €")
        print(f"   SALDO:             {saldo} €  (debería ≈ ingresos 2025)")


if __name__ == "__main__":
    asyncio.run(cierre_simulado())
