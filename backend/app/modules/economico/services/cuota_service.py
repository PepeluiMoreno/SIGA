"""Servicio del Flujo 1 — Establecimiento de cuotas del ejercicio.

Operaciones:
  - configurar_ejercicio(): crea / actualiza el registro de cuota base del año
    (en `importes_cuota_anio` con codigo_cuota='BASE'). Opcionalmente clona del
    ejercicio anterior.
  - previsualizar_generacion(): calcula nº de miembros y total esperado por tipo
    sin tocar la BD.
  - generar_cuotas_individuales(): crea `CuotaAnual` para cada miembro activo,
    aplicando el motivo de reducción del TipoMiembro. Idempotente.
  - recalcular_cuota(): recalcula el importe de una cuota con la config actual.

Decisiones aplicadas:
  D1.1 — cuota base + % reducción
  D1.2 — asignación automática por TipoMiembro
  D1.3 — configurar y generar son dos pasos separados
  D1.4 — motivo con %≥100 ⇒ no se genera CuotaAnual
  D1.7 — override individual `Miembro.motivo_reduccion_id` prevalece sobre `tipo_miembro.motivo_reduccion_id`
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.cuotas import (
    CuotaAnual,
    ImporteCuotaAnio,
    MotivoReduccionCuota,
)
from app.modules.membresia.models.miembro import Miembro, TipoMiembro
from app.modules.configuracion.models.estados import EstadoCuota


CODIGO_CUOTA_BASE = "BASE"  # codigo_cuota reservado para la cuota base del ejercicio

# Estados de planificación en los que los importes de ingresos son editables
_ESTADOS_EDITABLES_PRESUPUESTO = ("BORRADOR", "PROPUESTO")


class CuotaService:
    """Servicio del Flujo 1."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Configuración del ejercicio ───────────────────────────────────────────

    async def obtener_configuracion(self, ejercicio: int) -> Optional[ImporteCuotaAnio]:
        """Devuelve la fila BASE del ejercicio, o None si no existe."""
        r = await self.session.execute(
            select(ImporteCuotaAnio)
            .where(ImporteCuotaAnio.ejercicio == ejercicio)
            .where(ImporteCuotaAnio.codigo_cuota == CODIGO_CUOTA_BASE)
        )
        return r.scalars().first()

    async def configurar_ejercicio(
        self,
        ejercicio: int,
        importe_base: Decimal,
        clonar_de: Optional[int] = None,
        observaciones: Optional[str] = None,
    ) -> ImporteCuotaAnio:
        """Crea o actualiza la configuración de cuota base del ejercicio.

        Si `clonar_de` es un ejercicio previo con configuración, su importe base
        se ignora (la decisión final la da el parámetro `importe_base`); sirve
        de referencia para la UI.

        Cuando actualiza un registro existente, recalcula proporcionalmente los
        importes de todas las partidas INGRESO de planificaciones BORRADOR/PROPUESTO
        del mismo ejercicio.
        """
        existente = await self.obtener_configuracion(ejercicio)
        if existente:
            anterior = existente.importe
            existente.importe = importe_base
            existente.observaciones = observaciones
            self.session.add(existente)
            await self.session.commit()
            await self.session.refresh(existente)
            if anterior and anterior != importe_base and anterior > 0:
                ratio = (importe_base / anterior).quantize(Decimal("0.00001"))
                await self._recalcular_partidas_ingreso(ejercicio, ratio)
            return existente

        nueva = ImporteCuotaAnio(
            ejercicio=ejercicio,
            codigo_cuota=CODIGO_CUOTA_BASE,
            nombre_cuota=f"Cuota base {ejercicio}",
            importe=importe_base,
            activo=True,
            observaciones=observaciones,
        )
        self.session.add(nueva)
        await self.session.commit()
        await self.session.refresh(nueva)
        return nueva

    async def eliminar_cuota_ejercicio(self, ejercicio: int) -> bool:
        """Elimina la configuración BASE del ejercicio. Devuelve True si había algo que borrar."""
        existente = await self.obtener_configuracion(ejercicio)
        if not existente:
            return False
        await self.session.delete(existente)
        await self.session.commit()
        return True

    async def _recalcular_partidas_ingreso(self, ejercicio: int, ratio: Decimal) -> None:
        """Escala los importes presupuestados de las partidas INGRESO en planificaciones
        BORRADOR/PROPUESTO del ejercicio dado, aplicando el ratio indicado."""
        from ..models.presupuesto import PlanificacionAnual, PartidaPresupuestaria, EstadoPlanificacion

        r = await self.session.execute(
            select(PlanificacionAnual)
            .join(EstadoPlanificacion, PlanificacionAnual.estado_id == EstadoPlanificacion.id)
            .where(
                PlanificacionAnual.ejercicio == ejercicio,
                PlanificacionAnual.eliminado == False,
                EstadoPlanificacion.codigo.in_(_ESTADOS_EDITABLES_PRESUPUESTO),
            )
        )
        planificaciones = r.scalars().all()

        for plan in planificaciones:
            rp = await self.session.execute(
                select(PartidaPresupuestaria).where(
                    PartidaPresupuestaria.planificacion_id == plan.id,
                    PartidaPresupuestaria.tipo == "INGRESO",
                    PartidaPresupuestaria.eliminado == False,
                )
            )
            for partida in rp.scalars().all():
                nuevo = (partida.importe_presupuestado * ratio).quantize(Decimal("0.01"))
                partida.importe_presupuestado = nuevo
                partida.importe_inicial = partida.importe_inicial  # keep original
                self.session.add(partida)

        await self.session.commit()

    # ── Previsualización y generación ─────────────────────────────────────────

    async def previsualizar_generacion(self, ejercicio: int) -> dict:
        """Calcula nº de miembros activos por TipoMiembro y total a generar.

        No persiste nada. Se usa antes de A6 para que el tesorero valide.
        Aplica D1.4: tipos con motivo de %≥100 quedan listados como "excluidos".
        """
        config = await self.obtener_configuracion(ejercicio)
        if not config:
            raise ValueError(f"No hay configuración de cuota base para {ejercicio}")
        importe_base = config.importe

        # Cuotas ya existentes (idempotencia)
        existentes_r = await self.session.execute(
            select(func.count(CuotaAnual.id)).where(CuotaAnual.ejercicio == ejercicio)
        )
        existentes = existentes_r.scalar() or 0

        # Agrupar miembros activos por TipoMiembro
        miembros_q = await self.session.execute(
            select(Miembro.tipo_miembro_id, func.count(Miembro.id))
            .where(Miembro.activo == True)
            .group_by(Miembro.tipo_miembro_id)
        )
        cuenta_por_tipo: dict[UUID, int] = dict(miembros_q.all())

        # Cargar tipos con su motivo
        tipos_r = await self.session.execute(select(TipoMiembro).where(TipoMiembro.activo == True))
        tipos = list(tipos_r.scalars().all())

        desglose = []
        total_esperado = Decimal("0.00")
        n_generables = 0
        n_excluidos = 0
        for t in tipos:
            n_miembros = cuenta_por_tipo.get(t.id, 0)
            if not n_miembros:
                continue
            motivo = t.motivo_reduccion
            if motivo and motivo.excluye_cuota:
                desglose.append({
                    "tipo_miembro_id": str(t.id),
                    "tipo_miembro_nombre": t.nombre,
                    "motivo_codigo": motivo.codigo,
                    "motivo_porcentaje": float(motivo.porcentaje_reduccion),
                    "n_miembros": n_miembros,
                    "importe_unitario": 0.0,
                    "total": 0.0,
                    "excluido": True,
                })
                n_excluidos += n_miembros
                continue
            importe_efectivo = motivo.aplicar_a(importe_base) if motivo else importe_base
            total = importe_efectivo * n_miembros
            desglose.append({
                "tipo_miembro_id": str(t.id),
                "tipo_miembro_nombre": t.nombre,
                "motivo_codigo": motivo.codigo if motivo else None,
                "motivo_porcentaje": float(motivo.porcentaje_reduccion) if motivo else 0.0,
                "n_miembros": n_miembros,
                "importe_unitario": float(importe_efectivo),
                "total": float(total),
                "excluido": False,
            })
            n_generables += n_miembros
            total_esperado += total

        return {
            "ejercicio": ejercicio,
            "importe_base": float(importe_base),
            "desglose": desglose,
            "n_generables": n_generables,
            "n_excluidos": n_excluidos,
            "n_existentes": existentes,
            "total_esperado": float(total_esperado),
        }

    async def generar_cuotas_individuales(
        self,
        ejercicio: int,
        fecha_vencimiento: Optional[date] = None,
    ) -> dict:
        """Crea CuotaAnual para cada miembro activo según D1.2/D1.4. Idempotente.

        Devuelve: {n_creadas, n_omitidas_existentes, n_omitidas_excluidas, total_importe}
        """
        config = await self.obtener_configuracion(ejercicio)
        if not config:
            raise ValueError(f"No hay configuración de cuota base para {ejercicio}")
        importe_base = config.importe

        # Estado inicial Pendiente
        est_pend_r = await self.session.execute(
            select(EstadoCuota).where(EstadoCuota.nombre == "Pendiente")
        )
        est_pend = est_pend_r.scalars().first()
        if not est_pend:
            raise ValueError("Estado de cuota 'Pendiente' no encontrado en BD")

        # Cuotas ya existentes (set de miembro_id)
        ya_r = await self.session.execute(
            select(CuotaAnual.miembro_id).where(CuotaAnual.ejercicio == ejercicio)
        )
        ya = {row[0] for row in ya_r.all()}

        # Miembros activos con tipo + motivo (lazy='selectin' carga relaciones)
        miembros_r = await self.session.execute(
            select(Miembro).where(Miembro.activo == True)
        )
        miembros = list(miembros_r.scalars().all())

        n_creadas = 0
        n_omitidas_existentes = 0
        n_omitidas_excluidas = 0
        total_importe = Decimal("0.00")

        for m in miembros:
            if m.id in ya:
                n_omitidas_existentes += 1
                continue
            # D1.7: override individual prevalece sobre el motivo del TipoMiembro
            motivo = m.motivo_reduccion or (m.tipo_miembro.motivo_reduccion if m.tipo_miembro else None)
            if motivo and motivo.excluye_cuota:
                n_omitidas_excluidas += 1
                continue
            importe_efectivo = motivo.aplicar_a(importe_base) if motivo else importe_base
            # Incremento voluntario del socio: se suma al importe (no requiere aprobación)
            importe_efectivo = importe_efectivo + (m.incremento_cuota or Decimal("0.00"))

            cuota = CuotaAnual(
                miembro_id=m.id,
                ejercicio=ejercicio,
                agrupacion_id=m.agrupacion_id,
                importe_cuota_anio_id=config.id,
                codigo_cuota=motivo.codigo if motivo else CODIGO_CUOTA_BASE,
                importe=importe_efectivo,
                importe_pagado=Decimal("0.00"),
                estado_id=est_pend.id,
                fecha_vencimiento=fecha_vencimiento,
                motivo_reduccion_id=motivo.id if motivo else None,
            )
            self.session.add(cuota)
            n_creadas += 1
            total_importe += importe_efectivo

        await self.session.commit()
        return {
            "ejercicio": ejercicio,
            "n_creadas": n_creadas,
            "n_omitidas_existentes": n_omitidas_existentes,
            "n_omitidas_excluidas": n_omitidas_excluidas,
            "total_importe": float(total_importe),
        }

    async def recalcular_cuota(self, cuota_id: UUID) -> CuotaAnual:
        """Recalcula el importe de una cuota Pendiente con la configuración actual.

        Si la cuota ya tiene importe pagado parcialmente, lanza ValueError para
        evitar incoherencias. Para cuotas confirmadas, debe usarse un flujo de
        ajuste contable que está fuera de este flujo.
        """
        cuota_r = await self.session.execute(select(CuotaAnual).where(CuotaAnual.id == cuota_id))
        cuota = cuota_r.scalars().first()
        if not cuota:
            raise ValueError(f"Cuota {cuota_id} no encontrada")
        if cuota.importe_pagado and cuota.importe_pagado > Decimal("0"):
            raise ValueError("No se puede recalcular: la cuota ya tiene importes cobrados")

        config = await self.obtener_configuracion(cuota.ejercicio)
        if not config:
            raise ValueError(f"No hay configuración de cuota base para {cuota.ejercicio}")

        # D1.7: override individual prevalece sobre el motivo del TipoMiembro
        miembro = cuota.miembro
        motivo = None
        if miembro:
            motivo = miembro.motivo_reduccion or (
                miembro.tipo_miembro.motivo_reduccion if miembro.tipo_miembro else None
            )
        if motivo and motivo.excluye_cuota:
            raise ValueError("El miembro tiene ahora un motivo excluyente — anula esta cuota en su lugar")

        importe_efectivo = motivo.aplicar_a(config.importe) if motivo else config.importe
        # Incremento voluntario del socio: se suma al importe (no requiere aprobación)
        if miembro:
            importe_efectivo = importe_efectivo + (miembro.incremento_cuota or Decimal("0.00"))
        cuota.importe = importe_efectivo
        cuota.motivo_reduccion_id = motivo.id if motivo else None
        cuota.codigo_cuota = motivo.codigo if motivo else CODIGO_CUOTA_BASE
        self.session.add(cuota)
        await self.session.commit()
        await self.session.refresh(cuota)
        return cuota

    # ── CRUD del catálogo de motivos ──────────────────────────────────────────

    async def listar_motivos(self, solo_activos: bool = True) -> list[MotivoReduccionCuota]:
        q = select(MotivoReduccionCuota).order_by(MotivoReduccionCuota.orden, MotivoReduccionCuota.codigo)
        if solo_activos:
            q = q.where(MotivoReduccionCuota.activo == True)
        r = await self.session.execute(q)
        return list(r.scalars().all())

    async def motivo_tiene_recibos(self, motivo_id: UUID) -> bool:
        """D1.5: ¿el motivo tiene cuotas asociadas que ya hayan generado al menos un Recibo?

        Si devuelve true, su `porcentaje_reduccion` queda congelado: cambiarlo
        falsearía la trazabilidad de lo emitido al socio.
        """
        from ..models.recibos import Recibo
        r = await self.session.execute(
            select(func.count(Recibo.id))
            .join(CuotaAnual, CuotaAnual.id == Recibo.cuota_id)
            .where(CuotaAnual.motivo_reduccion_id == motivo_id)
        )
        return (r.scalar() or 0) > 0
