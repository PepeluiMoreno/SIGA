"""Servicio de gestión de Recibos.

El recibo es el justificante numerado correlativamente (REC-YYYY-NNNNN) del cobro
de cuotas y otros conceptos. Da soporte a:
- Emisión en lote (al inicio del ejercicio para todos los socios)
- Emisión individual (alta a media campaña, derramas selectivas)
- Marcado de cobrado tras liquidación de remesa o pago manual
- Marcado de fallido con código SEPA

Cumplimiento: Código de Comercio art. 25; PCESFL 2013 norma 1ª.
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.recibos import Recibo
from ..models.cuotas import CuotaAnual
from app.modules.configuracion.models.estados import EstadoCuota


class ReciboService:
    """Emisión y gestión del ciclo de vida de los recibos."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Numeración ───────────────────────────────────────────────────────────

    async def siguiente_numero(
        self,
        ejercicio: int,
        agrupacion_nombre_corto: Optional[str] = None,
    ) -> str:
        """Devuelve el siguiente número correlativo (D2.3).

        Formato si hay agrupación: `REC-{NOMBRE_CORTO}-{YYYY}-{NNNNN}`.
        Si no hay agrupación: legacy `REC-{YYYY}-{NNNNN}`.

        El correlativo se reinicia cada ejercicio dentro de cada serie
        (cada agrupación es una serie independiente; los recibos sin agrupación
        forman la serie central).
        """
        if agrupacion_nombre_corto:
            prefijo = f"REC-{agrupacion_nombre_corto.upper()}-{ejercicio}-"
        else:
            prefijo = f"REC-{ejercicio}-"

        result = await self.session.execute(
            select(func.count(Recibo.id)).where(Recibo.numero_recibo.like(f"{prefijo}%"))
        )
        cuenta = result.scalar() or 0
        return f"{prefijo}{cuenta + 1:05d}"

    # ── Emisión ──────────────────────────────────────────────────────────────

    async def emitir_lote(
        self,
        ejercicio: int,
        tipo: str = "CUOTA_ORDINARIA",
        concepto: Optional[str] = None,
        vinculacion_socio_ids: Optional[List[UUID]] = None,
        agrupacion_id: Optional[UUID] = None,
        fecha_emision: Optional[date] = None,
        fecha_vencimiento: Optional[date] = None,
    ) -> List[Recibo]:
        """Emite un lote de recibos para las cuotas pendientes del ejercicio.

        Si miembro_ids está vacío y agrupacion_id es None, emite recibos para
        TODAS las cuotas pendientes del ejercicio.
        Si concepto es None, se usa "Cuota ordinaria ejercicio YYYY".
        """
        concepto_default = f"Cuota ordinaria ejercicio {ejercicio}"
        concepto = concepto or concepto_default
        fecha_emision = fecha_emision or date.today()

        # Buscar cuotas pendientes del ejercicio (excluye las ya facturadas)
        est_pend = await self._estado_cuota("Pendiente")
        if not est_pend:
            raise ValueError("Estado 'Pendiente' de cuota no encontrado en BD")

        # Cuotas que ya tienen recibo emitido del mismo ejercicio/tipo
        recibos_existentes = await self.session.execute(
            select(Recibo.cuota_id).where(
                and_(
                    Recibo.ejercicio == ejercicio,
                    Recibo.tipo == tipo,
                    Recibo.estado.in_(["EMITIDO", "COBRADO"]),
                )
            )
        )
        cuotas_con_recibo = {row[0] for row in recibos_existentes.all() if row[0] is not None}

        q = select(CuotaAnual).where(
            CuotaAnual.ejercicio == ejercicio,
            CuotaAnual.estado_id == est_pend.id,
        )
        if vinculacion_socio_ids:
            q = q.where(CuotaAnual.vinculacion_socio_id.in_(vinculacion_socio_ids))
        if agrupacion_id:
            q = q.where(CuotaAnual.agrupacion_id == agrupacion_id)

        result = await self.session.execute(q)
        cuotas = [c for c in result.scalars().all() if c.id not in cuotas_con_recibo]

        if not cuotas:
            return []

        # Emitir recibos con numeración correlativa
        # Obtenemos el contador inicial una sola vez para evitar N consultas
        result = await self.session.execute(
            select(func.count(Recibo.id)).where(Recibo.ejercicio == ejercicio)
        )
        contador = (result.scalar() or 0) + 1

        recibos = []
        for cuota in cuotas:
            numero = f"REC-{ejercicio}-{contador:05d}"
            importe_pendiente = cuota.importe - cuota.importe_pagado
            recibo = Recibo(
                numero_recibo=numero,
                ejercicio=ejercicio,
                tipo=tipo,
                concepto=concepto,
                vinculacion_socio_id=cuota.vinculacion_socio_id,
                cuota_id=cuota.id,
                importe=importe_pendiente,
                importe_pagado=Decimal("0.00"),
                estado="EMITIDO",
                modo_cobro=cuota.modo_ingreso.value if cuota.modo_ingreso else None,
                fecha_emision=fecha_emision,
                fecha_vencimiento=fecha_vencimiento,
            )
            self.session.add(recibo)
            recibos.append(recibo)
            contador += 1

        await self.session.commit()
        for r in recibos:
            await self.session.refresh(r)
        return recibos

    async def emitir_recibo_individual(
        self,
        ejercicio: int,
        vinculacion_socio_id: UUID,
        concepto: str,
        importe: Decimal,
        tipo: str = "EXTRAORDINARIA",
        cuota_id: Optional[UUID] = None,
        fecha_vencimiento: Optional[date] = None,
        observaciones: Optional[str] = None,
    ) -> Recibo:
        """Emite un recibo individual (ej: cuota extraordinaria, derrama, donación)."""
        numero = await self.siguiente_numero(ejercicio)
        recibo = Recibo(
            numero_recibo=numero,
            ejercicio=ejercicio,
            tipo=tipo,
            concepto=concepto,
            vinculacion_socio_id=vinculacion_socio_id,
            cuota_id=cuota_id,
            importe=importe,
            importe_pagado=Decimal("0.00"),
            estado="EMITIDO",
            fecha_emision=date.today(),
            fecha_vencimiento=fecha_vencimiento,
            observaciones=observaciones,
        )
        self.session.add(recibo)
        await self.session.commit()
        await self.session.refresh(recibo)
        return recibo

    # ── Listado y consulta ───────────────────────────────────────────────────

    async def listar_recibos(
        self,
        ejercicio: Optional[int] = None,
        estado: Optional[str] = None,
        vinculacion_socio_id: Optional[UUID] = None,
        tipo: Optional[str] = None,
    ) -> List[Recibo]:
        q = select(Recibo)
        filtros = []
        if ejercicio:
            filtros.append(Recibo.ejercicio == ejercicio)
        if estado:
            filtros.append(Recibo.estado == estado)
        if vinculacion_socio_id:
            filtros.append(Recibo.vinculacion_socio_id == vinculacion_socio_id)
        if tipo:
            filtros.append(Recibo.tipo == tipo)
        if filtros:
            q = q.where(and_(*filtros))
        q = q.order_by(Recibo.numero_recibo)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def obtener_recibo(self, recibo_id: UUID) -> Optional[Recibo]:
        result = await self.session.execute(select(Recibo).where(Recibo.id == recibo_id))
        return result.scalars().first()

    # ── Cambios de estado ────────────────────────────────────────────────────

    async def marcar_cobrado(
        self,
        recibo_id: UUID,
        importe_cobrado: Optional[Decimal] = None,
        fecha_cobro: Optional[date] = None,
        modo_cobro: Optional[str] = None,
        orden_cobro_id: Optional[UUID] = None,
        cuenta_bancaria_id: Optional[UUID] = None,
        referencia: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> Recibo:
        """Marca un recibo como cobrado. D5.1: si se indica `cuenta_bancaria_id`
        y el cobro NO viene de una orden SEPA, orquesta la cadena completa:
        recibo → cuota → ApunteCaja → asiento contable, en una transacción.

        Cuando `orden_cobro_id` está presente (flujo 4 liquidación de remesa),
        la cuenta bancaria y el apunte ya los crea `liquidar_remesa`; aquí solo
        cambiamos el estado del recibo.
        """
        recibo = await self.obtener_recibo(recibo_id)
        if not recibo:
            raise ValueError(f"Recibo {recibo_id} no encontrado")

        if recibo.estado == "ANULADO":
            raise ValueError(f"El recibo {recibo.numero_recibo} está anulado")

        importe_cobrado = importe_cobrado if importe_cobrado is not None else (recibo.importe - recibo.importe_pagado)
        recibo.importe_pagado = recibo.importe_pagado + importe_cobrado
        recibo.fecha_cobro = fecha_cobro or date.today()
        if modo_cobro:
            recibo.modo_cobro = modo_cobro
        if orden_cobro_id:
            recibo.orden_cobro_id = orden_cobro_id
        if recibo.importe_pagado >= recibo.importe:
            recibo.estado = "COBRADO"
        self.session.add(recibo)
        await self.session.flush()

        # D5.1: si es cobro manual (no SEPA) y hay cuenta bancaria + cuota,
        # delegar en TesoreriaService para crear apunte y asiento en cascada.
        if cuenta_bancaria_id and not orden_cobro_id and recibo.cuota_id:
            from .tesoreria_service import TesoreriaService
            tesoreria = TesoreriaService(self.session)
            await tesoreria.registrar_pago_cuota_manual(
                cuota_id=recibo.cuota_id,
                cuenta_bancaria_id=cuenta_bancaria_id,
                importe=importe_cobrado,
                modo_ingreso=modo_cobro or "MANUAL",
                fecha_pago=recibo.fecha_cobro,
                referencia=referencia,
                observaciones=observaciones,
            )

        await self.session.commit()
        await self.session.refresh(recibo)
        return recibo

    async def marcar_fallido(
        self,
        recibo_id: UUID,
        codigo_sepa: str,
        motivo: Optional[str] = None,
    ) -> Recibo:
        recibo = await self.obtener_recibo(recibo_id)
        if not recibo:
            raise ValueError(f"Recibo {recibo_id} no encontrado")
        recibo.estado = "FALLIDO"
        obs_prev = recibo.observaciones or ""
        sufijo = f"FALLIDO [{codigo_sepa}]" + (f": {motivo}" if motivo else "")
        recibo.observaciones = f"{obs_prev}\n{sufijo}".strip()
        self.session.add(recibo)
        await self.session.commit()
        await self.session.refresh(recibo)
        return recibo

    async def anular_recibo(self, recibo_id: UUID, motivo: Optional[str] = None) -> Recibo:
        recibo = await self.obtener_recibo(recibo_id)
        if not recibo:
            raise ValueError(f"Recibo {recibo_id} no encontrado")
        if recibo.estado == "COBRADO":
            raise ValueError("No se puede anular un recibo ya cobrado")
        recibo.estado = "ANULADO"
        if motivo:
            obs_prev = recibo.observaciones or ""
            recibo.observaciones = f"{obs_prev}\nANULADO: {motivo}".strip()
        self.session.add(recibo)
        await self.session.commit()
        await self.session.refresh(recibo)
        return recibo

    # ── Helpers ──────────────────────────────────────────────────────────────

    async def _estado_cuota(self, nombre: str):
        r = await self.session.execute(select(EstadoCuota).where(EstadoCuota.nombre == nombre))
        return r.scalars().first()
