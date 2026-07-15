"""Reserva de fondos: compromisos presupuestarios de campañas/actividades.

Una campaña con presupuesto aprobado **reserva** fondos contra una partida del presupuesto
anual: crea un `CompromisoPresupuestario` que incrementa `PartidaPresupuestaria.importe_comprometido`
y, por tanto, reduce el `importe_disponible` de esa partida. Es el modelo contable ortodoxo
de compromiso → ejecución.

Hasta ahora esto no existía: `comprometer_importe`/`liberar_importe` estaban escritos en el
modelo pero no los llamaba nadie, y `CompromisoPresupuestario.campania_id` era un UUID suelto.
Este servicio cierra ese hueco.

**Política de sobregiro (decidida): avisa, no bloquea.** Si el importe excede el disponible de
la partida, la reserva se hace igualmente y se marca el sobregiro para que los informes lo
muestren; la corrección (reasignar, ampliar la partida) es una decisión humana posterior.

Idempotencia: quien dispara la reserva (el ejecutor del acuerdo de presupuesto) es
responsable de no llamar dos veces; este servicio no deduplica por sí mismo, pero
`liberar_compromiso` es seguro de llamar sobre un compromiso ya liberado.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.economico.models.presupuesto import (
    CompromisoPresupuestario, PartidaPresupuestaria,
)


@dataclass
class ResultadoReserva:
    """Lo que devuelve una reserva: el compromiso creado y si hubo sobregiro."""
    compromiso: CompromisoPresupuestario
    sobregiro: bool
    importe_excedido: Decimal  # cuánto se pasó del disponible (0 si no hubo sobregiro)


class ReservaService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _partida(self, partida_id: uuid.UUID) -> PartidaPresupuestaria:
        partida = (await self.session.execute(
            select(PartidaPresupuestaria).where(PartidaPresupuestaria.id == partida_id)
        )).scalar_one_or_none()
        if partida is None:
            raise ValueError("La partida presupuestaria no existe.")
        return partida

    async def reservar(
        self, *, partida_id: uuid.UUID, importe: Decimal,
        campania_id: Optional[uuid.UUID] = None,
        actividad_id: Optional[uuid.UUID] = None,
        concepto: Optional[str] = None,
        fecha: Optional[date] = None,
    ) -> ResultadoReserva:
        """Crea un compromiso contra una partida y actualiza su importe comprometido.

        Exactamente uno de `campania_id`/`actividad_id` debe venir. Sobregiro: si el importe
        supera el disponible, se compromete igualmente y `sobregiro=True`.
        """
        if bool(campania_id) == bool(actividad_id):
            raise ValueError("Indica exactamente una campaña o una actividad para la reserva.")
        if importe <= 0:
            raise ValueError("El importe a reservar debe ser positivo.")

        partida = await self._partida(partida_id)

        # Política sobregiro-avisa: comprometemos SIEMPRE (no usamos el booleano de
        # comprometer_importe para bloquear), pero medimos el exceso sobre el disponible.
        disponible = partida.importe_disponible
        sobregiro = importe > disponible
        excedido = (importe - disponible) if sobregiro else Decimal("0.00")
        partida.importe_comprometido += importe

        compromiso = CompromisoPresupuestario(
            id=uuid.uuid4(),
            partida_id=partida.id,
            campania_id=campania_id,
            actividad_id=actividad_id,
            importe_comprometido=importe,
            concepto=concepto,
            fecha_compromiso=fecha or date.today(),
            estado="activo",
        )
        self.session.add(compromiso)
        await self.session.flush()
        return ResultadoReserva(compromiso=compromiso, sobregiro=sobregiro, importe_excedido=excedido)

    async def liberar_compromiso(self, compromiso_id: uuid.UUID) -> CompromisoPresupuestario:
        """Devuelve un compromiso activo a disponible. Idempotente: si ya está liberado
        o ejecutado, no vuelve a tocar la partida."""
        compromiso = (await self.session.execute(
            select(CompromisoPresupuestario).where(CompromisoPresupuestario.id == compromiso_id)
        )).scalar_one_or_none()
        if compromiso is None:
            raise ValueError("El compromiso no existe.")
        if compromiso.estado != "activo":
            return compromiso  # ya liberado/ejecutado: nada que devolver
        partida = await self._partida(compromiso.partida_id)
        partida.liberar_importe(compromiso.importe_comprometido)
        compromiso.estado = "liberado"
        await self.session.flush()
        return compromiso

    async def compromiso_de_campania(self, campania_id: uuid.UUID) -> Optional[CompromisoPresupuestario]:
        """El compromiso activo de una campaña, si existe (para idempotencia del ejecutor)."""
        return (await self.session.execute(
            select(CompromisoPresupuestario).where(
                CompromisoPresupuestario.campania_id == campania_id,
                CompromisoPresupuestario.estado == "activo",
            )
        )).scalar_one_or_none()
