"""Servicio de generación y gestión de remesas SEPA.

Flujo principal:
  1. generar_remesa()     → crea Remesa en estado Borrador + OrdenCobro por cada cuota pendiente
  2. generar_xml_sepa()   → produce el Pain.008.003.02 listo para enviar al banco
  3. marcar_enviada()     → cambia estado a Enviada (archivo guardado)
  4. liquidar_remesa()    → TesoreriaService.liquidar_remesa() (ApunteCaja + asiento)
"""
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4
from xml.etree.ElementTree import Element, SubElement, tostring
import re
import uuid as uuid_module

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.remesas import Remesa, OrdenCobro
from ..models.cuotas import CuotaAnual
from ..models.recibos import Recibo
from ..models.tesoreria import ApunteCaja, TipoApunte, OrigenApunte
from app.modules.configuracion.models.estados import EstadoCuota, EstadoRemesa, EstadoOrdenCobro
from app.modules.membresia.models.miembro import Miembro


def _resumen_orden(orden: OrdenCobro) -> dict:
    """Resumen de una orden para la previsualización de liquidación."""
    miembro_nombre = ""
    if orden.cuota and orden.cuota.miembro:
        m = orden.cuota.miembro
        miembro_nombre = f"{m.nombre or ''} {m.apellido1 or ''}".strip()
    return {
        "orden_id": str(orden.id),
        "end_to_end_id": orden.end_to_end_id,
        "importe": float(orden.importe),
        "miembro_nombre": miembro_nombre or "—",
    }


class RemesaService:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Generar remesa ────────────────────────────────────────────────────────

    async def generar_remesa(
        self,
        ejercicio: int,
        fecha_cobro: date,
        agrupacion_id: Optional[UUID] = None,
        observaciones: Optional[str] = None,
        tipo_remesa: str = "ORDINARIA",
        concepto: Optional[str] = None,
        seq_tipo: str = "RCUR",
    ) -> Remesa:
        """Crea una remesa ORDINARIA con las cuotas pendientes del ejercicio.

        Aplica las decisiones del flujo 3:
        - D3.1: tras crear la remesa, emite Recibos en bloque (modo_cobro=SEPA).
        - D3.2: bloquea si ya existe una remesa ORDINARIA no anulada para el ejercicio.
        - D3.3: excluye cuotas cuyo socio no tiene IBAN (las cuenta pero no las incluye).
        - D3.4: excluye cuotas que ya están en una OrdenCobro activa de otra remesa.
        """
        # Validación SEPA: fecha_cobro respeta plazo mínimo según seq_tipo
        self._validar_fecha_cobro_sepa(fecha_cobro, seq_tipo)

        # D3.2 — una sola remesa ORDINARIA por ejercicio
        if tipo_remesa == "ORDINARIA":
            existente = await self._buscar_ordinaria_activa(ejercicio)
            if existente:
                raise ValueError(
                    f"Ya existe una remesa ORDINARIA activa para el ejercicio {ejercicio} "
                    f"({existente.referencia}). Anula esa antes de crear otra."
                )

        # D3.7: el flujo es emitir → revisar → remesar. La remesa parte de
        # recibos EMITIDO+SEPA preexistentes (flujo 2), no los crea.
        recibos_elegibles, _excluidas = await self._recibos_sepa_emitidos_para_remesa(
            ejercicio, agrupacion_id
        )
        if not recibos_elegibles:
            raise ValueError(
                f"No hay recibos EMITIDO con modo_cobro=SEPA para el ejercicio {ejercicio}"
                + (" en la agrupación indicada" if agrupacion_id else "")
                + ". Emite primero el lote desde Recibos (flujo 2)."
            )

        est_rem_borrador = await self._estado_remesa("Borrador")
        est_oc_pendiente = await self._estado_orden_cobro("Pendiente")
        if not est_rem_borrador or not est_oc_pendiente:
            raise ValueError("Estados de remesa/orden no encontrados en BD")

        importe_total = sum(r.importe - r.importe_pagado for r in recibos_elegibles)

        # Referencia legible REM-{YYYY}-{NNN} (D4.1)
        referencia = await self._siguiente_referencia_remesa(date.today().year, tipo_remesa)

        remesa = Remesa(
            referencia=referencia,
            mensaje_id=referencia,
            fecha_creacion=date.today(),
            fecha_cobro=fecha_cobro,
            importe_total=importe_total,
            gastos=Decimal("0.00"),
            num_ordenes=len(recibos_elegibles),
            estado_id=est_rem_borrador.id,
            agrupacion_id=agrupacion_id,
            tipo_remesa=tipo_remesa,
            concepto=concepto or f"Cuota ordinaria ejercicio {ejercicio}",
            seq_tipo=seq_tipo,
            observaciones=observaciones,
        )
        self.session.add(remesa)
        await self.session.flush()

        for nseq, recibo in enumerate(recibos_elegibles, start=1):
            importe_orden = recibo.importe - recibo.importe_pagado
            mandato = f"MAND-{str(recibo.miembro_id)[:8].upper()}"
            iban = getattr(recibo.miembro, "iban", None) if recibo.miembro else None

            orden = OrdenCobro(
                remesa_id=remesa.id,
                cuota_id=recibo.cuota_id,
                nseq=nseq,
                importe=importe_orden,
                referencia_mandato=mandato,
                iban=iban,
                estado_id=est_oc_pendiente.id,
            )
            self.session.add(orden)
            await self.session.flush()  # necesitamos orden.id para enlazar al recibo

            # D3.7: enlazar el recibo preexistente con la orden
            recibo.orden_cobro_id = orden.id
            self.session.add(recibo)

        await self.session.commit()
        await self.session.refresh(remesa)
        return remesa

    # ── Remesa extraordinaria (concepto e importe libre) ──────────────────────

    async def generar_remesa_extraordinaria(
        self,
        ejercicio: int,
        fecha_cobro: date,
        concepto: str,
        miembro_ids: list[UUID],
        importe_por_miembro: Decimal,
        agrupacion_id: Optional[UUID] = None,
        observaciones: Optional[str] = None,
        seq_tipo: str = "OOFF",
    ) -> Remesa:
        """Crea una remesa EXTRAORDINARIA (derrama, cuota especial) con concepto e
        importe definidos por el tesorero. No depende de cuotas pendientes existentes.

        Para cargos únicos no recurrentes el SeqTp recomendado por SEPA es OOFF.
        """
        if not miembro_ids:
            raise ValueError("Debe indicarse al menos un miembro destinatario")
        if importe_por_miembro <= Decimal("0"):
            raise ValueError("El importe por miembro debe ser positivo")

        # Validación SEPA: fecha_cobro respeta plazo mínimo según seq_tipo
        self._validar_fecha_cobro_sepa(fecha_cobro, seq_tipo)

        est_rem_borrador = await self._estado_remesa("Borrador")
        est_oc_pendiente = await self._estado_orden_cobro("Pendiente")
        if not est_rem_borrador or not est_oc_pendiente:
            raise ValueError("Estados de remesa/orden no encontrados en BD")

        # Buscar miembros y validar IBAN
        miembros_q = await self.session.execute(
            select(Miembro).where(Miembro.id.in_(miembro_ids))
        )
        miembros = {m.id: m for m in miembros_q.scalars().all()}
        miembros_validos = [m for m in miembros.values() if getattr(m, "iban", None)]

        if not miembros_validos:
            raise ValueError("Ningún miembro indicado tiene IBAN registrado")

        importe_total = importe_por_miembro * len(miembros_validos)
        ts = date.today().strftime("%Y-%m-%dT%H-%M-%S")
        referencia = f"SEPA_EXTRAORDINARIA_{ts}.xml"

        remesa = Remesa(
            referencia=referencia,
            mensaje_id=referencia.replace(".xml", ""),
            fecha_creacion=date.today(),
            fecha_cobro=fecha_cobro,
            importe_total=importe_total,
            gastos=Decimal("0.00"),
            num_ordenes=len(miembros_validos),
            estado_id=est_rem_borrador.id,
            agrupacion_id=agrupacion_id,
            tipo_remesa="EXTRAORDINARIA",
            concepto=concepto,
            seq_tipo=seq_tipo,
            observaciones=observaciones,
        )
        self.session.add(remesa)
        await self.session.flush()

        for nseq, miembro in enumerate(miembros_validos, start=1):
            mandato = f"MAND-{str(miembro.id)[:8].upper()}"
            orden = OrdenCobro(
                remesa_id=remesa.id,
                cuota_id=None,  # No hay cuota asociada en una extraordinaria
                nseq=nseq,
                importe=importe_por_miembro,
                referencia_mandato=mandato,
                iban=miembro.iban,
                estado_id=est_oc_pendiente.id,
            )
            self.session.add(orden)

        await self.session.commit()
        await self.session.refresh(remesa)
        return remesa

    # ── Remesa de reenvío de fallidos ─────────────────────────────────────────

    async def generar_remesa_fallidos(
        self,
        remesa_origen_id: UUID,
        fecha_cobro: date,
        seq_tipo: str = "FRST",
        observaciones: Optional[str] = None,
    ) -> Remesa:
        """Genera una nueva remesa con las órdenes fallidas de una remesa origen.

        Por defecto SeqTp=FRST porque tras un fallido (especialmente MD01, AC04)
        el mandato debe tratarse como primera presentación (norma EPC131-08).
        """
        # Validación SEPA: fecha_cobro respeta plazo mínimo según seq_tipo
        self._validar_fecha_cobro_sepa(fecha_cobro, seq_tipo)

        est_rem_borrador = await self._estado_remesa("Borrador")
        est_oc_pendiente = await self._estado_orden_cobro("Pendiente")
        est_oc_fallida = await self._estado_orden_cobro("Fallida")
        if not est_rem_borrador or not est_oc_pendiente:
            raise ValueError("Estados de remesa/orden no encontrados en BD")
        if not est_oc_fallida:
            raise ValueError("Estado 'Fallida' de orden de cobro no encontrado")

        # Cargar remesa origen
        origen_r = await self.session.execute(select(Remesa).where(Remesa.id == remesa_origen_id))
        origen = origen_r.scalars().first()
        if not origen:
            raise ValueError(f"Remesa origen {remesa_origen_id} no encontrada")

        # Órdenes fallidas de la remesa origen
        ordenes_falladas_q = await self.session.execute(
            select(OrdenCobro)
            .where(OrdenCobro.remesa_id == remesa_origen_id)
            .where(OrdenCobro.estado_id == est_oc_fallida.id)
        )
        ordenes_falladas = list(ordenes_falladas_q.scalars().all())

        if not ordenes_falladas:
            raise ValueError(f"La remesa {remesa_origen_id} no tiene órdenes fallidas")

        # Filtrar las que admiten reenvío: MD01 (mandato inexistente) no se puede reenviar
        no_reenviables = {"MD01", "MD02", "MD07"}
        ordenes_reenviables = [
            o for o in ordenes_falladas
            if (o.codigo_rechazo or "").upper() not in no_reenviables
        ]
        if not ordenes_reenviables:
            raise ValueError(
                "Ninguna orden fallida puede reenviarse — todos los códigos de rechazo "
                "son no reenviables (ej. MD01: mandato inexistente)"
            )

        importe_total = sum(o.importe for o in ordenes_reenviables)
        ts = date.today().strftime("%Y-%m-%dT%H-%M-%S")
        referencia = f"SEPA_REENVIO_{ts}.xml"

        remesa = Remesa(
            referencia=referencia,
            mensaje_id=referencia.replace(".xml", ""),
            fecha_creacion=date.today(),
            fecha_cobro=fecha_cobro,
            importe_total=importe_total,
            gastos=Decimal("0.00"),
            num_ordenes=len(ordenes_reenviables),
            estado_id=est_rem_borrador.id,
            agrupacion_id=origen.agrupacion_id,
            tipo_remesa="REENVIO",
            concepto=f"Reenvío de fallidos de remesa {origen.referencia}",
            seq_tipo=seq_tipo,
            remesa_origen_id=remesa_origen_id,
            observaciones=observaciones,
        )
        self.session.add(remesa)
        await self.session.flush()

        # Crear nuevas órdenes de cobro clonando las falladas
        for nseq, origen_o in enumerate(ordenes_reenviables, start=1):
            nueva = OrdenCobro(
                remesa_id=remesa.id,
                cuota_id=origen_o.cuota_id,
                nseq=nseq,
                importe=origen_o.importe,
                referencia_mandato=origen_o.referencia_mandato,
                iban=origen_o.iban,
                estado_id=est_oc_pendiente.id,
            )
            self.session.add(nueva)

        await self.session.commit()
        await self.session.refresh(remesa)
        return remesa

    # ── Importar fallidos del banco ───────────────────────────────────────────

    async def importar_fallidos_banco(
        self,
        remesa_id: UUID,
        fallidos: list[dict],
    ) -> int:
        """Marca las órdenes indicadas como fallidas con código SEPA y motivo.

        fallidos: [{orden_id: UUID, codigo: str, motivo: str, fecha?: date}]
        Devuelve el número de órdenes marcadas como fallidas.
        """
        est_oc_fallida = await self._estado_orden_cobro("Fallida")
        if not est_oc_fallida:
            raise ValueError("Estado 'Fallida' de orden de cobro no encontrado")

        contador = 0
        for f in fallidos:
            orden_id = f.get("orden_id")
            codigo = f.get("codigo")
            motivo = f.get("motivo", "")
            fecha_r = f.get("fecha")
            if not orden_id or not codigo:
                continue

            r = await self.session.execute(
                select(OrdenCobro).where(
                    and_(OrdenCobro.id == orden_id, OrdenCobro.remesa_id == remesa_id)
                )
            )
            orden = r.scalars().first()
            if not orden:
                continue

            orden.marcar_fallida(codigo, motivo, fecha_r)
            orden.estado_id = est_oc_fallida.id
            self.session.add(orden)
            contador += 1

        await self.session.commit()
        return contador

    # ── Liquidación atómica de remesa (Flujo 4) ───────────────────────────────

    async def previsualizar_liquidacion(
        self,
        remesa_id: UUID,
        tipo_fichero: str,           # "pain002" | "camt054" | "manual"
        contenido: Optional[bytes] = None,
        fallidos_manual: Optional[list[dict]] = None,
    ) -> dict:
        """Empareja el contenido del fichero del banco con las órdenes de la remesa
        SIN tocar la BD. Devuelve una previsualización para que el tesorero confirme.

        Resultado:
        {
          "remesa_referencia": "...",
          "fecha_liquidacion": "YYYY-MM-DD" | None,
          "cobradas": [{orden_id, end_to_end_id, importe, miembro_nombre}],
          "fallidas": [{orden_id, end_to_end_id, codigo, motivo, fecha}],
          "no_emparejadas": [{end_to_end_id, motivo}],
          "totales": {n_cobradas, n_fallidas, importe_cobrado}
        }
        """
        from .sepa_parsers import (
            parse_pain002, parse_camt054, motivo_sepa, ResultadoPain002, ResultadoCamt054,
        )

        remesa_r = await self.session.execute(select(Remesa).where(Remesa.id == remesa_id))
        remesa = remesa_r.scalars().first()
        if not remesa:
            raise ValueError(f"Remesa {remesa_id} no encontrada")

        ordenes_r = await self.session.execute(
            select(OrdenCobro).where(OrdenCobro.remesa_id == remesa_id)
        )
        ordenes = list(ordenes_r.scalars().all())
        por_eei = {o.end_to_end_id: o for o in ordenes}

        cobradas: list[dict] = []
        fallidas: list[dict] = []
        no_emparejadas: list[dict] = []

        if tipo_fichero == "pain002":
            if not contenido:
                raise ValueError("Fichero pain.002 vacío")
            res = parse_pain002(contenido)
            ids_rechazados = {l.end_to_end_id for l in res.lineas if l.es_rechazada}
            for l in res.lineas:
                orden = por_eei.get(l.end_to_end_id)
                if not orden:
                    no_emparejadas.append({
                        "end_to_end_id": l.end_to_end_id,
                        "motivo": "EndToEndId no pertenece a esta remesa",
                    })
                    continue
                if l.es_rechazada:
                    fallidas.append({
                        "orden_id": str(orden.id),
                        "end_to_end_id": l.end_to_end_id,
                        "codigo": l.codigo_rechazo or "",
                        "motivo": l.motivo_rechazo or motivo_sepa(l.codigo_rechazo or ""),
                        "fecha": l.fecha_rechazo.isoformat() if l.fecha_rechazo else None,
                        "importe": float(orden.importe),
                    })
            # Las no listadas como rechazadas se asumen cobradas
            for orden in ordenes:
                if orden.end_to_end_id not in ids_rechazados and not any(
                    f["orden_id"] == str(orden.id) for f in fallidas
                ):
                    cobradas.append(_resumen_orden(orden))

        elif tipo_fichero == "camt054":
            if not contenido:
                raise ValueError("Fichero camt.054 vacío")
            res = parse_camt054(contenido)
            cobradas_eei = {c.end_to_end_id for c in res.cargos}
            for cargo in res.cargos:
                orden = por_eei.get(cargo.end_to_end_id)
                if not orden:
                    no_emparejadas.append({
                        "end_to_end_id": cargo.end_to_end_id,
                        "motivo": "EndToEndId no pertenece a esta remesa",
                    })
                    continue
                cobradas.append(_resumen_orden(orden))
            # En camt.054 las órdenes que no aparecen probablemente quedaron pendientes
            # (puede llegar un pain.002 con las rechazadas más tarde). Las marcamos
            # como tales en la previsualización para que el tesorero decida.
            for orden in ordenes:
                if orden.end_to_end_id not in cobradas_eei:
                    no_emparejadas.append({
                        "end_to_end_id": orden.end_to_end_id,
                        "motivo": "Orden no aparece en camt.054 — esperando pain.002 de rechazos",
                    })

        elif tipo_fichero == "manual":
            # Entrada manual: lista de fallidos. Las no listadas se consideran cobradas.
            ids_fallidos = set()
            for f in (fallidos_manual or []):
                orden_id = f.get("orden_id")
                orden = next((o for o in ordenes if str(o.id) == str(orden_id)), None)
                if not orden:
                    no_emparejadas.append({
                        "end_to_end_id": str(orden_id),
                        "motivo": "Orden no pertenece a esta remesa",
                    })
                    continue
                ids_fallidos.add(orden.id)
                fallidas.append({
                    "orden_id": str(orden.id),
                    "end_to_end_id": orden.end_to_end_id,
                    "codigo": f.get("codigo", ""),
                    "motivo": f.get("motivo", motivo_sepa(f.get("codigo", ""))),
                    "fecha": f.get("fecha"),
                    "importe": float(orden.importe),
                })
            for orden in ordenes:
                if orden.id not in ids_fallidos:
                    cobradas.append(_resumen_orden(orden))
        else:
            raise ValueError(f"Tipo de fichero no soportado: {tipo_fichero}")

        importe_cobrado = sum(c["importe"] for c in cobradas)
        return {
            "remesa_referencia": remesa.referencia,
            "fecha_liquidacion": None,  # el tesorero la introduce en la confirmación
            "cobradas": cobradas,
            "fallidas": fallidas,
            "no_emparejadas": no_emparejadas,
            "totales": {
                "n_cobradas": len(cobradas),
                "n_fallidas": len(fallidas),
                "importe_cobrado": importe_cobrado,
            },
        }

    async def liquidar_remesa(
        self,
        remesa_id: UUID,
        fecha_liquidacion: date,
        cuenta_bancaria_id: UUID,
        cobradas: list[UUID],
        fallidas: list[dict],
    ) -> dict:
        """Aplica el resultado del banco a la remesa en una sola transacción:
        - Cada cobrada: OrdenCobro→Procesada, Cuota.importe_pagado+=, Cuota→Cobrada si completa,
          Recibo asociado→COBRADO con fecha_cobro.
        - Cada fallida: OrdenCobro→Fallida con código/motivo, Recibo asociado→FALLIDO.
          NO se toca la cuota (D4.2: gestión manual del tesorero).
        - Se crea un ApunteCaja de ingreso por la suma de cobradas.
        - El RegistroContable genera el asiento Debe 572 / Haber 721|430.
        - La Remesa pasa a Procesada (si todas las órdenes están en estado terminal)
          o Parcial (si quedan Pendiente).

        fallidas: [{orden_id: UUID, codigo: str, motivo: str, fecha?: date}]

        Devuelve: {n_cobradas, n_fallidas, importe_cobrado, apunte_id?, asiento_id?, remesa_estado}
        """
        from .registro_contable import RegistroContable

        remesa_r = await self.session.execute(select(Remesa).where(Remesa.id == remesa_id))
        remesa = remesa_r.scalars().first()
        if not remesa:
            raise ValueError(f"Remesa {remesa_id} no encontrada")

        est_oc_procesada = await self._estado_orden_cobro("Procesada")
        est_oc_fallida = await self._estado_orden_cobro("Fallida")
        est_cuota_cobrada = await self._estado_cuota("Cobrada")
        est_rem_procesada = await self._estado_remesa("Procesada")
        est_rem_parcial = await self._estado_remesa("Parcial")
        if not (est_oc_procesada and est_oc_fallida and est_rem_procesada):
            raise ValueError("Estados de remesa/orden no encontrados en BD")

        importe_cobrado = Decimal("0.00")
        n_cobradas = 0
        n_fallidas = 0

        # ── Procesar cobradas ─────────────────────────────────────────────────
        for orden_id in cobradas:
            orden_r = await self.session.execute(
                select(OrdenCobro).where(OrdenCobro.id == orden_id).where(OrdenCobro.remesa_id == remesa_id)
            )
            orden = orden_r.scalars().first()
            if not orden:
                continue

            orden.estado_id = est_oc_procesada.id
            orden.fecha_procesamiento = fecha_liquidacion
            self.session.add(orden)
            importe_cobrado += orden.importe
            n_cobradas += 1

            # Actualizar cuota
            if orden.cuota_id:
                cuota_r = await self.session.execute(
                    select(CuotaAnual).where(CuotaAnual.id == orden.cuota_id)
                )
                cuota = cuota_r.scalars().first()
                if cuota:
                    cuota.importe_pagado = (cuota.importe_pagado or Decimal("0")) + orden.importe
                    cuota.fecha_pago = fecha_liquidacion
                    if cuota.importe_pagado >= cuota.importe and est_cuota_cobrada:
                        cuota.estado_id = est_cuota_cobrada.id
                    self.session.add(cuota)

            # Actualizar recibo asociado (por orden_cobro_id o por cuota_id)
            await self._marcar_recibo_cobrado(orden, fecha_liquidacion)

        # ── Procesar fallidas ─────────────────────────────────────────────────
        for f in fallidas:
            orden_id = f.get("orden_id")
            if not orden_id:
                continue
            orden_r = await self.session.execute(
                select(OrdenCobro).where(OrdenCobro.id == orden_id).where(OrdenCobro.remesa_id == remesa_id)
            )
            orden = orden_r.scalars().first()
            if not orden:
                continue

            codigo = f.get("codigo", "")
            motivo = f.get("motivo", "")
            fecha_r = f.get("fecha")
            if isinstance(fecha_r, str):
                try:
                    fecha_r = date.fromisoformat(fecha_r)
                except ValueError:
                    fecha_r = None
            orden.marcar_fallida(codigo, motivo, fecha_r or fecha_liquidacion)
            orden.estado_id = est_oc_fallida.id
            self.session.add(orden)
            n_fallidas += 1

            await self._marcar_recibo_fallido(orden, codigo, motivo)

        # ── Estado final de la remesa ─────────────────────────────────────────
        # Recargar TODAS las órdenes para evaluar
        todas_r = await self.session.execute(
            select(OrdenCobro).where(OrdenCobro.remesa_id == remesa_id)
        )
        todas = list(todas_r.scalars().all())
        pendientes = [
            o for o in todas
            if o.estado_id not in (est_oc_procesada.id, est_oc_fallida.id)
        ]
        if pendientes:
            # Hay órdenes aún en Pendiente → Parcial (si existe ese estado)
            remesa.estado_id = (est_rem_parcial.id if est_rem_parcial else est_rem_procesada.id)
        else:
            remesa.estado_id = est_rem_procesada.id
        self.session.add(remesa)

        # ── Apunte de caja + asiento ──────────────────────────────────────────
        apunte_id = None
        asiento_id = None
        if importe_cobrado > Decimal("0"):
            apunte = ApunteCaja(
                cuenta_bancaria_id=cuenta_bancaria_id,
                fecha=fecha_liquidacion,
                importe=importe_cobrado,
                tipo=TipoApunte.INGRESO,
                origen=OrigenApunte.REMESA,
                concepto=f"Liquidación remesa {remesa.referencia} ({n_cobradas} órdenes)",
                entidad_origen_tipo="remesa",
                entidad_origen_id=remesa_id,
            )
            self.session.add(apunte)
            await self.session.flush()
            apunte_id = apunte.id

            registro = RegistroContable(self.session)
            asiento = await registro.generar_asiento_para_apunte(apunte)
            asiento_id = asiento.id if asiento else None

        await self.session.commit()
        # Refrescar remesa para devolver su nombre de estado actualizado
        await self.session.refresh(remesa)

        estado_actual_r = await self.session.execute(
            select(EstadoRemesa).where(EstadoRemesa.id == remesa.estado_id)
        )
        estado_remesa = estado_actual_r.scalars().first()

        return {
            "n_cobradas": n_cobradas,
            "n_fallidas": n_fallidas,
            "importe_cobrado": float(importe_cobrado),
            "apunte_id": str(apunte_id) if apunte_id else None,
            "asiento_id": str(asiento_id) if asiento_id else None,
            "remesa_estado": estado_remesa.nombre if estado_remesa else None,
        }

    async def _marcar_recibo_cobrado(self, orden: OrdenCobro, fecha_cobro: date) -> None:
        """Busca el recibo asociado a la orden y lo marca como COBRADO."""
        # Estrategia: por orden_cobro_id primero, luego por cuota_id + estado EMITIDO
        recibo = None
        recibo_r = await self.session.execute(
            select(Recibo).where(Recibo.orden_cobro_id == orden.id)
        )
        recibo = recibo_r.scalars().first()
        if not recibo and orden.cuota_id:
            recibo_r = await self.session.execute(
                select(Recibo)
                .where(Recibo.cuota_id == orden.cuota_id)
                .where(Recibo.estado.in_(["EMITIDO", "FALLIDO"]))
                .order_by(Recibo.fecha_emision.desc())
            )
            recibo = recibo_r.scalars().first()
        if recibo:
            recibo.estado = "COBRADO"
            recibo.fecha_cobro = fecha_cobro
            recibo.importe_pagado = recibo.importe
            recibo.orden_cobro_id = orden.id
            self.session.add(recibo)

    async def _marcar_recibo_fallido(
        self, orden: OrdenCobro, codigo: str, motivo: str
    ) -> None:
        """Busca el recibo asociado a la orden y lo marca como FALLIDO."""
        recibo = None
        recibo_r = await self.session.execute(
            select(Recibo).where(Recibo.orden_cobro_id == orden.id)
        )
        recibo = recibo_r.scalars().first()
        if not recibo and orden.cuota_id:
            recibo_r = await self.session.execute(
                select(Recibo)
                .where(Recibo.cuota_id == orden.cuota_id)
                .where(Recibo.estado == "EMITIDO")
                .order_by(Recibo.fecha_emision.desc())
            )
            recibo = recibo_r.scalars().first()
        if recibo:
            recibo.estado = "FALLIDO"
            recibo.orden_cobro_id = orden.id
            sufijo = f"FALLIDO [{codigo}]" + (f": {motivo}" if motivo else "")
            obs_prev = recibo.observaciones or ""
            recibo.observaciones = f"{obs_prev}\n{sufijo}".strip()
            self.session.add(recibo)

    # ── Generar XML SEPA Pain.008.003.02 ─────────────────────────────────────

    async def generar_xml_sepa(
        self,
        remesa_id: UUID,
        creditor_name: Optional[str] = None,
        creditor_iban: Optional[str] = None,
        creditor_bic: Optional[str] = None,
        creditor_id: Optional[str] = None,
    ) -> bytes:
        """Genera el XML SEPA Direct Debit (Pain.008.003.02).

        D3.5: si no se pasan los datos del acreedor por argumento, se leen de
        `configuraciones` (claves `sepa_creditor_*`). Si faltan, lanza ValueError.
        """
        # D3.5: cargar acreedor desde configuraciones cuando no se pasa por argumento
        if not all([creditor_name, creditor_iban, creditor_bic, creditor_id]):
            cfg = await self._cargar_acreedor_sepa()
            creditor_name = creditor_name or cfg["name"]
            creditor_iban = creditor_iban or cfg["iban"]
            creditor_bic = creditor_bic or cfg["bic"]
            creditor_id = creditor_id or cfg["id"]
        faltan = [k for k, v in {
            "creditor_name": creditor_name,
            "creditor_iban": creditor_iban,
            "creditor_bic": creditor_bic,
            "creditor_id": creditor_id,
        }.items() if not v]
        if faltan:
            raise ValueError(
                "Faltan datos del acreedor SEPA en Parámetros Generales (sección SEPA): "
                + ", ".join(faltan)
            )

        result = await self.session.execute(
            select(Remesa).where(Remesa.id == remesa_id)
        )
        remesa = result.scalars().first()
        if not remesa:
            raise ValueError(f"Remesa {remesa_id} no encontrada")

        root = Element("Document", attrib={
            "xmlns": "urn:iso:std:iso:20022:tech:xsd:pain.008.003.02",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        })
        cstmr = SubElement(root, "CstmrDrctDbtInitn")

        # Group Header
        grp_hdr = SubElement(cstmr, "GrpHdr")
        SubElement(grp_hdr, "MsgId").text = remesa.mensaje_id or str(remesa.id)[:35]
        SubElement(grp_hdr, "CreDtTm").text = f"{date.today().isoformat()}T00:00:00"
        SubElement(grp_hdr, "NbOfTxs").text = str(remesa.num_ordenes)
        SubElement(grp_hdr, "CtrlSum").text = str(remesa.importe_total)
        init_pty = SubElement(grp_hdr, "InitgPty")
        SubElement(init_pty, "Nm").text = creditor_name[:70]

        # Payment Information block
        pmt_inf = SubElement(cstmr, "PmtInf")
        SubElement(pmt_inf, "PmtInfId").text = (remesa.mensaje_id or str(remesa.id))[:35]
        SubElement(pmt_inf, "PmtMtd").text = "DD"
        SubElement(pmt_inf, "NbOfTxs").text = str(remesa.num_ordenes)
        SubElement(pmt_inf, "CtrlSum").text = str(remesa.importe_total)

        pmt_tp_inf = SubElement(pmt_inf, "PmtTpInf")
        svc_lvl = SubElement(pmt_tp_inf, "SvcLvl")
        SubElement(svc_lvl, "Cd").text = "SEPA"
        lcl_instrm = SubElement(pmt_tp_inf, "LclInstrm")
        SubElement(lcl_instrm, "Cd").text = "CORE"
        # SeqTp del mandato SEPA — viene del campo de la remesa (FRST/RCUR/LAST/OOFF)
        SubElement(pmt_tp_inf, "SeqTp").text = remesa.seq_tipo or "RCUR"

        SubElement(pmt_inf, "ReqdColltnDt").text = remesa.fecha_cobro.isoformat()

        # Creditor
        cdtr = SubElement(pmt_inf, "Cdtr")
        SubElement(cdtr, "Nm").text = creditor_name[:70]
        cdtr_acct = SubElement(pmt_inf, "CdtrAcct")
        cdtr_id_elem = SubElement(cdtr_acct, "Id")
        SubElement(cdtr_id_elem, "IBAN").text = re.sub(r"\s", "", creditor_iban)
        cdtr_agt = SubElement(pmt_inf, "CdtrAgt")
        fin_instn_id = SubElement(cdtr_agt, "FinInstnId")
        SubElement(fin_instn_id, "BIC").text = creditor_bic

        cdtr_schme = SubElement(pmt_inf, "CdtrSchmeId")
        cdtr_schme_id = SubElement(cdtr_schme, "Id")
        prvt_id = SubElement(cdtr_schme_id, "PrvtId")
        othr = SubElement(prvt_id, "Othr")
        SubElement(othr, "Id").text = creditor_id
        schme_nm = SubElement(othr, "SchmeNm")
        SubElement(schme_nm, "Prtry").text = "SEPA"

        # Transactions
        for orden in remesa.ordenes:
            drct_dbt_tx_inf = SubElement(pmt_inf, "DrctDbtTxInf")

            pmt_id = SubElement(drct_dbt_tx_inf, "PmtId")
            # D4.1: EndToEndId legible {referencia_remesa}-{nseq:03d}
            # Permite emparejar la respuesta del banco (pain.002/camt.054) con la orden
            # sin exponer UUIDs al deudor ni a los extractos bancarios.
            SubElement(pmt_id, "EndToEndId").text = orden.end_to_end_id[:35]

            instd_amt = SubElement(drct_dbt_tx_inf, "InstdAmt", attrib={"Ccy": "EUR"})
            instd_amt.text = f"{orden.importe:.2f}"

            drct_dbt_tx = SubElement(drct_dbt_tx_inf, "DrctDbtTx")
            mndtn_rltd_inf = SubElement(drct_dbt_tx, "MndtRltdInf")
            SubElement(mndtn_rltd_inf, "MndtId").text = (orden.referencia_mandato or str(orden.id)[:35])
            SubElement(mndtn_rltd_inf, "DtOfSgntr").text = "2010-01-01"

            if orden.iban:
                dbtr_agt = SubElement(drct_dbt_tx_inf, "DbtrAgt")
                fi = SubElement(dbtr_agt, "FinInstnId")
                SubElement(fi, "Othr").text = "NOTPROVIDED"

                dbtr = SubElement(drct_dbt_tx_inf, "Dbtr")
                cuota = orden.cuota
                if cuota and cuota.miembro:
                    m = cuota.miembro
                    nombre = f"{m.nombre or ''} {m.apellido1 or ''}".strip()[:70]
                    SubElement(dbtr, "Nm").text = nombre or "DESCONOCIDO"
                else:
                    SubElement(dbtr, "Nm").text = "DESCONOCIDO"

                dbtr_acct = SubElement(drct_dbt_tx_inf, "DbtrAcct")
                dbtr_acct_id = SubElement(dbtr_acct, "Id")
                SubElement(dbtr_acct_id, "IBAN").text = re.sub(r"\s", "", orden.iban)

            purp = SubElement(drct_dbt_tx_inf, "Purp")
            SubElement(purp, "Cd").text = "OTHR"

            ustrd_rmt = SubElement(drct_dbt_tx_inf, "RmtInf")
            # Concepto del cobro: usa el de la remesa (más flexible), fallback al ejercicio
            if remesa.concepto:
                concepto_cobro = remesa.concepto
            else:
                cuota = orden.cuota
                ejercicio = cuota.ejercicio if cuota else "?"
                concepto_cobro = f"Cuota {ejercicio}"
            SubElement(ustrd_rmt, "Ustrd").text = concepto_cobro[:140]

        xml_bytes = b'<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(root, encoding="unicode").encode("utf-8")
        return xml_bytes

    async def marcar_enviada(self, remesa_id: UUID, archivo: Optional[str] = None) -> Remesa:
        estado_enviada = await self._estado_remesa("Enviada")
        result = await self.session.execute(select(Remesa).where(Remesa.id == remesa_id))
        remesa = result.scalars().first()
        if not remesa:
            raise ValueError("Remesa no encontrada")
        if estado_enviada:
            remesa.estado_id = estado_enviada.id
        remesa.fecha_envio = date.today()
        if archivo:
            remesa.archivo_sepa = archivo
        self.session.add(remesa)
        await self.session.commit()
        await self.session.refresh(remesa)
        return remesa

    async def listar_cuotas_pendientes(
        self,
        ejercicio: int,
        agrupacion_id: Optional[UUID] = None,
    ) -> list[CuotaAnual]:
        """Devuelve cuotas pendientes para previsualizar antes de crear la remesa."""
        est_pend = await self._estado_cuota("Pendiente")
        q = select(CuotaAnual).where(CuotaAnual.ejercicio == ejercicio)
        if est_pend:
            q = q.where(CuotaAnual.estado_id == est_pend.id)
        if agrupacion_id:
            q = q.where(CuotaAnual.agrupacion_id == agrupacion_id)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def previsualizar_remesa(
        self,
        ejercicio: int,
        agrupacion_id: Optional[UUID] = None,
    ) -> dict:
        """Previsualiza qué se incluiría en una remesa ORDINARIA, sin crearla.

        D3.7: parte de recibos EMITIDO+SEPA preexistentes (no de cuotas).
        Aplica D3.3 (excluir sin IBAN) y D3.4 (excluir ya en otra remesa activa).
        """
        ordinaria_existente = await self._buscar_ordinaria_activa(ejercicio)

        incluidos, excluidos = await self._recibos_sepa_emitidos_para_remesa(
            ejercicio, agrupacion_id
        )

        importe_incluido = sum(r.importe - r.importe_pagado for r in incluidos)

        def _resumen_recibo(r: "Recibo", motivo: str) -> dict:
            m = r.miembro
            nombre = f"{m.nombre or ''} {m.apellido1 or ''}".strip() if m else ""
            return {
                "cuota_id": str(r.cuota_id) if r.cuota_id else "",
                "miembro_id": str(r.miembro_id),
                "miembro_nombre": nombre,
                "importe_pendiente": float(r.importe - r.importe_pagado),
                "motivo_exclusion": motivo,
            }

        return {
            "ejercicio": ejercicio,
            "n_incluidas": len(incluidos),
            "n_excluidas": len(excluidos),
            "importe_total": float(importe_incluido),
            "incluidas": [_resumen_recibo(r, "") for r in incluidos],
            "excluidas": [_resumen_recibo(r, motivo) for r, motivo in excluidos],
            "ordinaria_existente": (
                {"id": str(ordinaria_existente.id), "referencia": ordinaria_existente.referencia}
                if ordinaria_existente else None
            ),
        }

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _buscar_ordinaria_activa(self, ejercicio: int) -> Optional[Remesa]:
        """D3.2: devuelve una remesa ORDINARIA del ejercicio si está activa
        (Borrador, Generada, Enviada, Procesada, Parcial). None si no hay o si
        está Anulada o Rechazada.
        """
        estados_activos = [
            e for e in (
                await self._estado_remesa("Borrador"),
                await self._estado_remesa("Generada"),
                await self._estado_remesa("Enviada"),
                await self._estado_remesa("Procesada"),
                await self._estado_remesa("Parcial"),
            ) if e is not None
        ]
        if not estados_activos:
            return None
        ids_activos = [e.id for e in estados_activos]

        # Las remesas ORDINARIAS no tienen ejercicio directo; lo derivamos
        # del concepto o de fecha_cobro. Usamos year(fecha_cobro) por estabilidad.
        from sqlalchemy import extract
        r = await self.session.execute(
            select(Remesa).where(
                and_(
                    Remesa.tipo_remesa == "ORDINARIA",
                    Remesa.estado_id.in_(ids_activos),
                    extract("year", Remesa.fecha_cobro) == ejercicio,
                )
            ).limit(1)
        )
        return r.scalars().first()

    async def _recibos_sepa_emitidos_para_remesa(
        self,
        ejercicio: int,
        agrupacion_id: Optional[UUID] = None,
    ) -> tuple[list["Recibo"], list[tuple["Recibo", str]]]:
        """D3.7: devuelve (incluidos, excluidos_con_motivo) de los Recibos
        ya emitidos con modo SEPA listos para incluirse en una remesa.

        Filtros:
        - `Recibo.tipo='CUOTA_ORDINARIA'` (las extraordinarias van en su propia remesa)
        - `Recibo.estado='EMITIDO'`
        - `Recibo.modo_cobro='SEPA'`
        - `Recibo.ejercicio=ejercicio`
        - `Recibo.orden_cobro_id IS NULL` (todavía no asignado a otra remesa)
        - El miembro tiene IBAN registrado (D3.3) — en su defecto se excluye con motivo
        - La cuota referenciada está en estado Pendiente
        - Opcionalmente, filtrado por agrupación
        """
        q = (
            select(Recibo)
            .where(Recibo.ejercicio == ejercicio)
            .where(Recibo.tipo == "CUOTA_ORDINARIA")
            .where(Recibo.estado == "EMITIDO")
            .where(Recibo.modo_cobro == "SEPA")
            .where(Recibo.orden_cobro_id.is_(None))
        )
        if agrupacion_id:
            # Recibos cuyo miembro pertenece a la agrupación (o, a futuro, recibo.agrupacion_id)
            q = q.join(Miembro, Miembro.id == Recibo.miembro_id).where(
                Miembro.agrupacion_id == agrupacion_id
            )
        result = await self.session.execute(q)
        candidatos = list(result.scalars().all())

        # Verificar estado Pendiente de la cuota y IBAN del miembro
        est_pend = await self._estado_cuota("Pendiente")
        incluidos: list[Recibo] = []
        excluidos: list[tuple[Recibo, str]] = []
        for recibo in candidatos:
            if not recibo.cuota_id:
                excluidos.append((recibo, "Sin cuota asociada"))
                continue
            cuota = recibo.cuota
            if not cuota or (est_pend and cuota.estado_id != est_pend.id):
                excluidos.append((recibo, "Cuota no Pendiente"))
                continue
            iban = getattr(recibo.miembro, "iban", None) if recibo.miembro else None
            if not iban:
                excluidos.append((recibo, "Sin IBAN"))
                continue
            incluidos.append(recibo)
        return incluidos, excluidos

    async def _cuotas_elegibles(
        self,
        ejercicio: int,
        agrupacion_id: Optional[UUID] = None,
    ) -> tuple[list[CuotaAnual], list[tuple[CuotaAnual, str]]]:
        """D3.3 + D3.4: devuelve (incluidas, excluidas_con_motivo) de las
        cuotas pendientes del ejercicio que cumplen los filtros para entrar
        en una remesa.

        Excluidas con motivo:
        - "Sin IBAN" si el socio no tiene IBAN registrado.
        - "Ya en remesa REM-XXX" si la cuota tiene una OrdenCobro activa en otra remesa.
        """
        est_pend = await self._estado_cuota("Pendiente")
        if not est_pend:
            return [], []

        q = select(CuotaAnual).where(
            CuotaAnual.ejercicio == ejercicio,
            CuotaAnual.estado_id == est_pend.id,
        )
        if agrupacion_id:
            q = q.where(CuotaAnual.agrupacion_id == agrupacion_id)
        result = await self.session.execute(q)
        candidatas = list(result.scalars().all())

        # Cuotas ya en una orden activa (D3.4)
        estados_oc_activos_q = await self.session.execute(
            select(EstadoOrdenCobro).where(EstadoOrdenCobro.nombre.in_(["Pendiente", "Procesada"]))
        )
        ids_oc_activos = [e.id for e in estados_oc_activos_q.scalars().all()]

        cuotas_con_orden_activa: dict[UUID, str] = {}
        if ids_oc_activos and candidatas:
            ocupacion = await self.session.execute(
                select(OrdenCobro.cuota_id, Remesa.referencia)
                .join(Remesa, Remesa.id == OrdenCobro.remesa_id)
                .where(
                    OrdenCobro.cuota_id.in_([c.id for c in candidatas]),
                    OrdenCobro.estado_id.in_(ids_oc_activos),
                )
            )
            for cuota_id, referencia in ocupacion.all():
                cuotas_con_orden_activa[cuota_id] = referencia

        incluidas: list[CuotaAnual] = []
        excluidas: list[tuple[CuotaAnual, str]] = []
        for c in candidatas:
            ref_existente = cuotas_con_orden_activa.get(c.id)
            if ref_existente:
                excluidas.append((c, f"Ya en remesa {ref_existente}"))
                continue
            iban = getattr(c.miembro, "iban", None) if c.miembro else None
            if not iban:
                excluidas.append((c, "Sin IBAN"))
                continue
            incluidas.append(c)
        return incluidas, excluidas

    async def _siguiente_referencia_remesa(self, ano: int, tipo_remesa: str) -> str:
        """Devuelve la siguiente referencia legible REM-{YYYY}-{NNN} dentro del año.
        REENVIO y EXTRAORDINARIA usan la misma serie correlativa.
        """
        # Buscar el máximo correlativo usado este año en cualquier tipo
        prefijo = f"REM-{ano}-"
        r = await self.session.execute(
            select(Remesa.referencia).where(Remesa.referencia.like(f"{prefijo}%"))
        )
        max_n = 0
        for (ref,) in r.all():
            try:
                n = int(ref[len(prefijo):][:3])
                max_n = max(max_n, n)
            except (ValueError, IndexError):
                continue
        return f"{prefijo}{max_n + 1:03d}"

    async def _emitir_recibos_para_remesa(self, remesa: Remesa) -> int:
        """D3.1: tras crear una remesa, emite un Recibo por cada OrdenCobro con
        estado EMITIDO, modo_cobro=SEPA, enlazando recibo.orden_cobro_id.
        Idempotente: si ya hay recibo para la orden, lo salta.
        """
        from .recibo_service import ReciboService

        ejercicio = remesa.fecha_cobro.year
        existentes_q = await self.session.execute(
            select(Recibo.orden_cobro_id).where(
                Recibo.orden_cobro_id.in_([o.id for o in (remesa.ordenes or [])])
            )
        )
        con_recibo = {r[0] for r in existentes_q.all() if r[0]}

        recibo_service = ReciboService(self.session)
        contador = 0
        agrupacion_nombre_corto = None
        if remesa.agrupacion is not None:
            agrupacion_nombre_corto = getattr(remesa.agrupacion, "nombre_corto", None)

        for orden in remesa.ordenes:
            if orden.id in con_recibo:
                continue
            numero = await recibo_service.siguiente_numero(
                ejercicio=ejercicio,
                agrupacion_nombre_corto=agrupacion_nombre_corto,
            )
            recibo = Recibo(
                numero_recibo=numero,
                ejercicio=ejercicio,
                tipo=("REENVIO" if remesa.tipo_remesa == "REENVIO"
                      else "EXTRAORDINARIA" if remesa.tipo_remesa == "EXTRAORDINARIA"
                      else "CUOTA_ORDINARIA"),
                concepto=remesa.concepto or f"Cuota ordinaria ejercicio {ejercicio}",
                miembro_id=orden.cuota.miembro_id if orden.cuota else None,
                cuota_id=orden.cuota_id,
                orden_cobro_id=orden.id,
                importe=orden.importe,
                importe_pagado=Decimal("0.00"),
                estado="EMITIDO",
                modo_cobro="SEPA",
                fecha_emision=date.today(),
            )
            self.session.add(recibo)
            contador += 1
        if contador:
            await self.session.commit()
        return contador


    def _validar_fecha_cobro_sepa(self, fecha_cobro: date, seq_tipo: str) -> None:
        """Valida que fecha_cobro respeta el plazo SEPA mínimo según seq_tipo.

        Norma EPC131-08 (SEPA Core Direct Debit Rulebook):
        - FRST (primer cobro de un mandato): mínimo 14 días naturales antes del cobro.
        - OOFF (cargo único): mismo plazo que FRST, 14 días.
        - RCUR (cobro recurrente): mínimo 2 días hábiles. Usamos 2 días naturales
          como aproximación conservadora.
        - LAST (último cobro de un mandato): 2 días, igual que RCUR.

        Lanza ValueError si no se cumple el plazo.
        """
        if fecha_cobro is None:
            raise ValueError("fecha_cobro es obligatoria")

        hoy = date.today()
        plazos_min_dias = {"FRST": 14, "OOFF": 14, "RCUR": 2, "LAST": 2}
        plazo = plazos_min_dias.get(seq_tipo)
        if plazo is None:
            raise ValueError(
                f"seq_tipo SEPA desconocido: '{seq_tipo}'. Valores válidos: FRST, RCUR, LAST, OOFF."
            )

        fecha_minima = hoy + timedelta(days=plazo)
        if fecha_cobro < fecha_minima:
            raise ValueError(
                f"fecha_cobro {fecha_cobro.isoformat()} no respeta el plazo SEPA mínimo "
                f"para seq_tipo={seq_tipo} ({plazo} días). "
                f"Debe ser ≥ {fecha_minima.isoformat()}."
            )

    async def _cargar_acreedor_sepa(self) -> dict:
        """D3.5: lee los datos del acreedor SEPA de la tabla `configuraciones`
        (grupo `organizacion`, claves `sepa.creditor_*`), gestionadas desde
        Parámetros Generales → sección SEPA.

        Devuelve dict con keys: name, iban, bic, id (vacíos si no configurados).
        """
        from app.modules.configuracion.models.configuracion import Configuracion
        r = await self.session.execute(
            select(Configuracion).where(
                Configuracion.clave.in_([
                    "sepa.creditor_name",
                    "sepa.creditor_iban",
                    "sepa.creditor_bic",
                    "sepa.creditor_id",
                ])
            )
        )
        valores = {c.clave: (c.valor or "") for c in r.scalars().all()}
        return {
            "name": valores.get("sepa.creditor_name", ""),
            "iban": valores.get("sepa.creditor_iban", ""),
            "bic":  valores.get("sepa.creditor_bic", ""),
            "id":   valores.get("sepa.creditor_id", ""),
        }

    async def anular_remesa(self, remesa_id: UUID) -> Remesa:
        """Anula una remesa en estado Borrador, Generada o Enviada.

        - La remesa pasa a estado Anulada.
        - Sus OrdenCobro pasan a estado Anulada.
        - Las cuotas asociadas vuelven a estar disponibles para incluirse en
          otra remesa (no se tocan; D3.4 las detectará como libres porque ya no
          hay orden activa).
        - Los Recibos emitidos (D3.1) pasan a estado ANULADO.

        No se permite anular una remesa Procesada o Parcial (ya hubo cobros).
        """
        r = await self.session.execute(
            select(Remesa).where(Remesa.id == remesa_id)
        )
        remesa = r.scalars().first()
        if not remesa:
            raise ValueError(f"Remesa {remesa_id} no encontrada")

        # Estados no anulables
        est_procesada = await self._estado_remesa("Procesada")
        est_parcial = await self._estado_remesa("Parcial")
        est_anulada_rem = await self._estado_remesa("Anulada") or await self._estado_remesa("Rechazada")
        est_anulada_oc = await self._estado_orden_cobro("Anulada")

        if (est_procesada and remesa.estado_id == est_procesada.id) or \
           (est_parcial and remesa.estado_id == est_parcial.id):
            raise ValueError("No se puede anular una remesa ya procesada (parcial o totalmente).")
        if not est_anulada_rem:
            raise ValueError("Estado 'Anulada' de remesa no encontrado en BD")

        remesa.estado_id = est_anulada_rem.id

        # Anular órdenes
        if est_anulada_oc:
            for orden in (remesa.ordenes or []):
                orden.estado_id = est_anulada_oc.id

        # Anular recibos asociados (D3.1)
        if remesa.ordenes:
            orden_ids = [o.id for o in remesa.ordenes]
            recibos_r = await self.session.execute(
                select(Recibo).where(
                    Recibo.orden_cobro_id.in_(orden_ids),
                    Recibo.estado.in_(["EMITIDO", "FALLIDO"]),
                )
            )
            for recibo in recibos_r.scalars().all():
                recibo.estado = "ANULADO"

        await self.session.commit()
        await self.session.refresh(remesa)
        return remesa

    async def _estado_cuota(self, nombre: str):
        r = await self.session.execute(select(EstadoCuota).where(EstadoCuota.nombre == nombre))
        return r.scalars().first()

    async def _estado_remesa(self, nombre: str):
        r = await self.session.execute(select(EstadoRemesa).where(EstadoRemesa.nombre == nombre))
        return r.scalars().first()

    async def _estado_orden_cobro(self, nombre: str):
        r = await self.session.execute(select(EstadoOrdenCobro).where(EstadoOrdenCobro.nombre == nombre))
        return r.scalars().first()
