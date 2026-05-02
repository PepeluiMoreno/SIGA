
from sqlalchemy import select
from decimal import Decimal
from datetime import date

from app.domains.financiero.models.tesoreria import MovimientoEconomico, TipoMovimiento

class TesoreriaService:

    def __init__(self, db):
        self.db = db

    async def registrar_ingreso(self, importe, concepto, actividad_id=None, miembro_id=None, origen="MANUAL"):
        if importe <= 0:
            raise ValueError("Importe inválido")

        mov = MovimientoEconomico(
            fecha=date.today(),
            importe=importe,
            concepto=concepto,
            tipo=TipoMovimiento.INGRESO,
            actividad_id=actividad_id,
            miembro_id=miembro_id,
            origen=origen
        )

        self.db.add(mov)
        await self.db.flush()
        return mov

    async def calcular_saldo(self):
        result = await self.db.execute(select(MovimientoEconomico))
        movimientos = result.scalars().all()

        saldo = Decimal("0")
        for m in movimientos:
            if m.tipo == TipoMovimiento.INGRESO:
                saldo += m.importe
            else:
                saldo -= m.importe

        return saldo
