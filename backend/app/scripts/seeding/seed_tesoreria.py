"""Seed de tesorería: cuenta bancaria principal + ApunteCaja históricos desde remesas.

Requisito previo:
  - seed_remesas.py ya ejecutado (tabla remesas poblada)

Qué hace:
  1. Crea (o recupera si ya existe) la cuenta bancaria principal de la organización.
     IBAN por defecto: ES00 0000 0000 0000 0000 0000 (placeholder — actualizar en UI).
     Se puede sobreescribir con la variable CUENTA_IBAN al ejecutar.
  2. Por cada remesa Procesada genera:
       · ApunteCaja INGRESO  → importe_total   (origen=REMESA)
       · ApunteCaja GASTO    → gastos          (origen=REMESA, solo si gastos > 0)
     Los apuntes históricos NO disparan asientos contables automáticos
     (evita generar 18 asientos retroactivos; el usuario puede generar el balance
     del ejercicio desde la UI cuando quiera).
  3. Actualiza el saldo_actual de la cuenta con los movimientos netos.

Idempotente: salta remesas cuyo ApunteCaja ya existe (referencia_externa = remesa.id).

Ejecutar:
    docker exec <backend-container> python -m app.scripts.seeding.seed_tesoreria
    # Con IBAN propio:
    docker exec <backend-container> env CUENTA_IBAN=ES7620770024003102575766 \\
        python -m app.scripts.seeding.seed_tesoreria
"""
import asyncio
import os
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.core.database import async_session
from app.modules.economico.models.tesoreria import (
    CuentaBancaria,
    ApunteCaja,
    TipoApunte,
    OrigenApunte,
)
from app.modules.economico.models.remesas import Remesa
from app.modules.configuracion.models.estados import EstadoRemesa

CUENTA_IBAN    = os.getenv("CUENTA_IBAN", "ES0000000000000000000000")
CUENTA_NOMBRE  = os.getenv("CUENTA_NOMBRE", "Cuenta bancaria principal")
CUENTA_BANCO   = os.getenv("CUENTA_BANCO", "")


async def seed():
    print("\n" + "=" * 60)
    print("SEED TESORERÍA (cuenta bancaria + apuntes históricos de remesas)")
    print("=" * 60)

    async with async_session() as session:

        # ── 1. Cuenta bancaria ──────────────────────────────────────────────
        cuenta_result = await session.execute(
            select(CuentaBancaria).where(CuentaBancaria.iban == CUENTA_IBAN)
        )
        cuenta = cuenta_result.scalars().first()

        if cuenta:
            print(f"\n  Cuenta bancaria existente: {cuenta.nombre} ({cuenta.iban})")
        else:
            cuenta = CuentaBancaria(
                nombre=CUENTA_NOMBRE,
                iban=CUENTA_IBAN,
                banco_nombre=CUENTA_BANCO or "Sin especificar",
                activa=True,
                saldo_actual=Decimal("0.00"),
            )
            session.add(cuenta)
            await session.flush()
            print(f"\n  Cuenta bancaria creada: {cuenta.nombre} ({cuenta.iban})")
            if CUENTA_IBAN == "ES0000000000000000000000":
                print("  [AVISO] IBAN placeholder — actualiza el IBAN real en Tesorería → Cuentas.")

        # ── 2. Apuntes existentes para esta cuenta (idempotencia) ──────────
        apuntes_result = await session.execute(
            select(ApunteCaja.referencia_externa).where(
                ApunteCaja.cuenta_bancaria_id == cuenta.id,
                ApunteCaja.origen == OrigenApunte.REMESA,
            )
        )
        ya_procesadas: set[str] = {r for r in apuntes_result.scalars() if r}

        # ── 3. Remesas procesadas ───────────────────────────────────────────
        rem_result = await session.execute(
            select(Remesa).order_by(Remesa.fecha_cobro)
        )
        remesas = list(rem_result.scalars().all())
        print(f"  Remesas en BD: {len(remesas)}")

        creados_ingreso = 0
        creados_gasto   = 0
        saltadas        = 0

        for remesa in remesas:
            remesa_id_str = str(remesa.id)

            if remesa_id_str in ya_procesadas:
                saltadas += 1
                continue

            fecha = remesa.fecha_cobro or remesa.fecha_creacion or date.today()

            # Apunte de ingreso: importe_total cobrado
            ingreso = ApunteCaja(
                cuenta_bancaria_id=cuenta.id,
                fecha=fecha,
                importe=remesa.importe_total,
                tipo=TipoApunte.INGRESO,
                concepto=f"Cobro remesa SEPA {remesa.referencia[:40]}",
                origen=OrigenApunte.REMESA,
                entidad_origen_tipo="remesa",
                entidad_origen_id=remesa.id,
                referencia_externa=remesa_id_str,
                conciliado=True,
            )
            session.add(ingreso)
            cuenta.saldo_actual += remesa.importe_total
            creados_ingreso += 1

            # Apunte de gasto: comisiones bancarias (si las hay)
            if remesa.gastos and remesa.gastos > Decimal("0.00"):
                gasto = ApunteCaja(
                    cuenta_bancaria_id=cuenta.id,
                    fecha=fecha,
                    importe=remesa.gastos,
                    tipo=TipoApunte.GASTO,
                    concepto=f"Gastos bancarios remesa {remesa.referencia[:35]}",
                    origen=OrigenApunte.REMESA,
                    entidad_origen_tipo="remesa",
                    entidad_origen_id=remesa.id,
                    referencia_externa=f"{remesa_id_str}_gastos",
                    conciliado=True,
                )
                session.add(gasto)
                cuenta.saldo_actual -= remesa.gastos
                creados_gasto += 1

        session.add(cuenta)
        await session.commit()

        print(f"\n  Apuntes de ingreso creados : {creados_ingreso}")
        print(f"  Apuntes de gastos creados  : {creados_gasto}")
        print(f"  Remesas ya procesadas      : {saltadas}")
        print(f"  Saldo actual de la cuenta  : {cuenta.saldo_actual:.2f} €")
        print("\n  [OK] Tesorería histórica cargada.")
        print("  Siguiente paso: actualizar el IBAN real en Tesorería → Cuentas Bancarias.")


if __name__ == "__main__":
    asyncio.run(seed())
