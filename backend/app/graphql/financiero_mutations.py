
import strawberry
from decimal import Decimal
from app.modules.economico.services.tesoreria_service import TesoreriaService

@strawberry.type
class FinancieroMutation:

    @strawberry.mutation
    async def registrarMovimiento(self, info, importe: float, concepto: str) -> int:
        service = TesoreriaService(info.context["db"])
        mov = await service.registrar_ingreso(
            importe=Decimal(importe),
            concepto=concepto
        )
        return mov.id
