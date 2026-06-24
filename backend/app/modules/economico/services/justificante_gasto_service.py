"""Servicio del flujo de Justificantes de Gasto.

Estados: PRESENTADO → APROBADO → PAGADO  (RECHAZADO / ANULADO como salidas)

El pago genera un ApunteCaja (TipoApunte.GASTO, origen=JUSTIFICANTE_GASTO) que
dispara el asiento contable automático si modo COMPLETA (ver RegistroContable).
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.justificantes_gasto import (
    JustificanteGasto, JustificanteGastoLinea, JustificanteGastoDocumento,
)
from ..models.tesoreria import ApunteCaja, TipoApunte, OrigenApunte
from .tesoreria_service import TesoreriaService
from .registro_contable import RegistroContable


class JustificanteGastoService:
    """Presentación, aprobación, rechazo, pago y anulación de justificantes."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Numeración ───────────────────────────────────────────────────────────

    async def siguiente_numero(
        self,
        ejercicio: int,
        agrupacion_nombre_corto: Optional[str] = None,
    ) -> str:
        """D7.4: JUST-{NOMBRE_CORTO}-{YYYY}-{NNNNN} si hay agrupación;
        JUST-{YYYY}-{NNNNN} si la actividad es global o sin grupo."""
        if agrupacion_nombre_corto:
            prefijo = f"JUST-{agrupacion_nombre_corto.upper()}-{ejercicio}-"
        else:
            prefijo = f"JUST-{ejercicio}-"
        result = await self.session.execute(
            select(func.count(JustificanteGasto.id)).where(
                JustificanteGasto.numero_justificante.like(f"{prefijo}%")
            )
        )
        cuenta = result.scalar() or 0
        return f"{prefijo}{(cuenta + 1):05d}"

    async def _derivar_agrupacion_de_actividad(self, actividad_id: UUID):
        """D7.4: deriva (agrupacion_id, nombre_corto) desde la actividad → grupo → agrupación.
        Si la actividad no tiene grupo o el grupo no tiene agrupación, devuelve (None, None).
        """
        from app.modules.actividades.models.actividad import Actividad
        from app.modules.actividades.models.grupo import GrupoTrabajo
        from app.modules.core.geografico.direccion import UnidadOrganizativa

        r = await self.session.execute(
            select(Actividad.grupo_id).where(Actividad.id == actividad_id)
        )
        grupo_id = r.scalar()
        if not grupo_id:
            return None, None
        r = await self.session.execute(
            select(GrupoTrabajo.agrupacion_id).where(GrupoTrabajo.id == grupo_id)
        )
        agrupacion_id = r.scalar()
        if not agrupacion_id:
            return None, None
        r = await self.session.execute(
            select(UnidadOrganizativa.nombre_corto).where(UnidadOrganizativa.id == agrupacion_id)
        )
        nombre_corto = r.scalar()
        return agrupacion_id, nombre_corto

    # ── Presentación (multi-línea) ──────────────────────────────────────────

    async def presentar(
        self,
        miembro_id: UUID,
        actividad_id: UUID,
        lineas: List[dict],
        partida_actividad_id: Optional[UUID] = None,
        agrupacion_id: Optional[UUID] = None,
        observaciones: Optional[str] = None,
        ejercicio: Optional[int] = None,
        presentado_por_tesorero_id: Optional[UUID] = None,
    ) -> JustificanteGasto:
        """Presenta un justificante de gasto con una o varias líneas referidas
        a la misma actividad.

        D7.2: el presentador NO selecciona la cuenta contable; la imputación se
              resolverá al librar el pago (anclada al tipo de actividad o
              definida manualmente por el tesorero).
        D7.4: deriva agrupación desde la actividad si no se pasa.
        D7.6: si `presentado_por_tesorero_id` está informado, el justificante
              nace en estado ACEPTADO (atajo del tesorero).

        `lineas`: lista de dicts con claves:
          - concepto (str, requerido)
          - importe (Decimal o número, requerido)
          - fecha_gasto (date, requerido)
          - observaciones (str, opcional)
        Debe haber al menos una línea.
        """
        if not lineas:
            raise ValueError("Debe haber al menos una línea de gasto.")
        normalizadas: List[dict] = []
        total = Decimal("0.00")
        for i, l in enumerate(lineas, start=1):
            c = (l.get("concepto") or "").strip()
            if not c:
                raise ValueError(f"Línea {i}: el concepto es obligatorio.")
            imp_raw = l.get("importe")
            if imp_raw is None:
                raise ValueError(f"Línea {i}: indica el importe.")
            imp = Decimal(str(imp_raw))
            if imp <= Decimal("0"):
                raise ValueError(f"Línea {i}: el importe debe ser positivo.")
            f = l.get("fecha_gasto")
            if not f:
                raise ValueError(f"Línea {i}: indica la fecha del gasto.")
            normalizadas.append({
                "concepto": c, "importe": imp, "fecha_gasto": f,
                "observaciones": (l.get("observaciones") or "").strip() or None,
            })
            total += imp

        ejercicio = ejercicio or normalizadas[0]["fecha_gasto"].year

        # D7.4: derivar agrupación desde la actividad si no la pasan
        agrupacion_nombre_corto = None
        if agrupacion_id is None:
            agrupacion_id, agrupacion_nombre_corto = await self._derivar_agrupacion_de_actividad(actividad_id)
        else:
            from app.modules.core.geografico.direccion import UnidadOrganizativa
            r = await self.session.execute(
                select(UnidadOrganizativa.nombre_corto).where(UnidadOrganizativa.id == agrupacion_id)
            )
            agrupacion_nombre_corto = r.scalar()

        numero = await self.siguiente_numero(ejercicio, agrupacion_nombre_corto)

        # D7.6: si lo presenta un tesorero a petición del socio → auto-aceptación
        estado_inicial = "PRESENTADO"
        aceptado_por_id = None
        fecha_aceptacion = None
        if presentado_por_tesorero_id is not None:
            estado_inicial = "ACEPTADO"
            aceptado_por_id = presentado_por_tesorero_id
            fecha_aceptacion = date.today()

        # Concepto/fecha de cabecera: el primero si hay una sola línea; resumen si hay varias
        if len(normalizadas) == 1:
            concepto_cab = normalizadas[0]["concepto"]
            fecha_cab = normalizadas[0]["fecha_gasto"]
        else:
            concepto_cab = f"Varios ({len(normalizadas)} conceptos)"
            fecha_cab = max(l["fecha_gasto"] for l in normalizadas)

        justificante = JustificanteGasto(
            numero_justificante=numero,
            ejercicio=ejercicio,
            miembro_id=miembro_id,
            actividad_id=actividad_id,
            partida_actividad_id=partida_actividad_id,
            cuenta_contable_id=None,  # se resuelve al pagar
            agrupacion_id=agrupacion_id,
            presentado_en_nombre_de_id=presentado_por_tesorero_id,
            estado=estado_inicial,
            aceptado_por_id=aceptado_por_id,
            fecha_aceptacion=fecha_aceptacion,
            concepto=concepto_cab,
            importe=total,
            fecha_gasto=fecha_cab,
            fecha_presentacion=date.today(),
            observaciones=observaciones,
        )
        self.session.add(justificante)
        await self.session.flush()

        # Crear líneas
        for l in normalizadas:
            self.session.add(JustificanteGastoLinea(
                justificante_id=justificante.id,
                concepto=l["concepto"],
                importe=l["importe"],
                fecha_gasto=l["fecha_gasto"],
                observaciones=l["observaciones"],
            ))

        await self.session.commit()
        await self.session.refresh(justificante)
        return justificante

    # ── Aceptación intermedia por responsable de actividad (D7.5) ────────────

    async def aceptar(
        self, justificante_id: UUID, aceptador_id: UUID
    ) -> JustificanteGasto:
        """D7.5: el responsable de la actividad acepta el justificante.

        Valida que `aceptador_id == actividad.responsable_id`. La gestión del
        permiso `JUST_ACEPTAR` la hace la capa de mutation.
        """
        from app.modules.actividades.models.actividad import Actividad
        justificante = await self.obtener(justificante_id)
        if not justificante:
            raise ValueError(f"Justificante {justificante_id} no encontrado")
        if not justificante.puede_aceptarse:
            raise ValueError(
                f"No se puede aceptar un justificante en estado {justificante.estado}. "
                f"Solo los PRESENTADO admiten aceptación."
            )

        # Validar que el aceptador es el responsable de la actividad
        r = await self.session.execute(
            select(Actividad.responsable_id).where(Actividad.id == justificante.actividad_id)
        )
        responsable_real = r.scalar()
        if responsable_real and responsable_real != aceptador_id:
            raise ValueError(
                "Solo el responsable de la actividad puede aceptar el justificante. "
                "Si no figuras como responsable, contacta con el coordinador."
            )

        justificante.estado = "ACEPTADO"
        justificante.aceptado_por_id = aceptador_id
        justificante.fecha_aceptacion = date.today()
        self.session.add(justificante)
        await self.session.commit()
        await self.session.refresh(justificante)
        return justificante

    # ── Aprobación / Rechazo ─────────────────────────────────────────────────

    async def aprobar(
        self, justificante_id: UUID, aprobador_id: UUID
    ) -> JustificanteGasto:
        """D7.1: el tesorero aprueba un justificante ya ACEPTADO por el responsable."""
        justificante = await self.obtener(justificante_id)
        if not justificante:
            raise ValueError(f"Justificante {justificante_id} no encontrado")
        if not justificante.puede_aprobarse:
            raise ValueError(
                f"No se puede aprobar un justificante en estado {justificante.estado}. "
                f"Debe estar ACEPTADO por el responsable de la actividad antes."
            )
        justificante.estado = "APROBADO"
        justificante.aprobado_por_id = aprobador_id
        justificante.fecha_aprobacion = date.today()
        self.session.add(justificante)
        await self.session.commit()
        await self.session.refresh(justificante)
        return justificante

    async def rechazar(
        self, justificante_id: UUID, aprobador_id: UUID, motivo: str
    ) -> JustificanteGasto:
        """Rechazo desde el responsable (estado PRESENTADO) o desde el tesorero
        (estado ACEPTADO). Motivo obligatorio."""
        justificante = await self.obtener(justificante_id)
        if not justificante:
            raise ValueError(f"Justificante {justificante_id} no encontrado")
        if justificante.estado not in ("PRESENTADO", "ACEPTADO"):
            raise ValueError(
                f"No se puede rechazar un justificante en estado {justificante.estado}"
            )
        if not motivo or not motivo.strip():
            raise ValueError("El rechazo requiere indicar un motivo")
        justificante.estado = "RECHAZADO"
        justificante.aprobado_por_id = aprobador_id
        justificante.fecha_aprobacion = date.today()
        justificante.motivo_rechazo = motivo.strip()
        self.session.add(justificante)
        await self.session.commit()
        await self.session.refresh(justificante)
        return justificante

    # ── Pago ─────────────────────────────────────────────────────────────────

    async def pagar(
        self,
        justificante_id: UUID,
        cuenta_bancaria_id: UUID,
        modo_pago: str = "TRANSFERENCIA",
        fecha_pago: Optional[date] = None,
        referencia: Optional[str] = None,
        cuenta_contable_id: Optional[UUID] = None,
    ) -> ApunteCaja:
        """Genera el ApunteCaja de GASTO y marca el justificante como PAGADO.

        D7.7-bis: la imputación contable se resuelve aquí, NO al presentar.
        Orden de resolución de la cuenta de gasto:
          1. `cuenta_contable_id` explícita en la llamada (decisión manual del tesorero).
          2. `actividad.tipo_actividad.cuenta_contable_default_id` (cuenta por defecto del tipo).
          3. `justificante.cuenta_contable_id` si ya estaba fijada (presentación legacy).
          4. Error: tesorero debe elegirla en el modal de pago.
        """
        justificante = await self.obtener(justificante_id)
        if not justificante:
            raise ValueError(f"Justificante {justificante_id} no encontrado")
        if not justificante.puede_pagarse:
            raise ValueError(
                f"Solo se puede pagar un justificante APROBADO (estado actual: {justificante.estado})"
            )

        # Resolver cuenta contable de imputación
        from app.modules.economico.models.contabilidad.plan_cuentas import (
            CuentaContable, TipoCuentaContable,
        )
        from app.modules.actividades.models.actividad import Actividad

        cuenta_resuelta_id = cuenta_contable_id
        if cuenta_resuelta_id is None:
            # Buscar cuenta_contable_default del tipo de actividad
            r = await self.session.execute(
                select(Actividad).where(Actividad.id == justificante.actividad_id)
            )
            act = r.scalars().first()
            if act and act.tipo_actividad and act.tipo_actividad.cuenta_contable_default_id:
                cuenta_resuelta_id = act.tipo_actividad.cuenta_contable_default_id
        if cuenta_resuelta_id is None:
            cuenta_resuelta_id = justificante.cuenta_contable_id  # legacy
        if cuenta_resuelta_id is None:
            raise ValueError(
                "Falta la cuenta contable de imputación. Asigna una cuenta por defecto al "
                "tipo de actividad o indícala manualmente al pagar."
            )

        # Validar que la cuenta es válida
        r = await self.session.execute(select(CuentaContable).where(CuentaContable.id == cuenta_resuelta_id))
        cuenta_obj = r.scalars().first()
        if not cuenta_obj:
            raise ValueError(f"Cuenta contable {cuenta_resuelta_id} no encontrada")
        if cuenta_obj.tipo != TipoCuentaContable.GASTO or not cuenta_obj.permite_asiento or not cuenta_obj.activa:
            raise ValueError(
                f"La cuenta {cuenta_obj.codigo} no admite imputación de gasto. "
                "Elige una cuenta del grupo 6 activa que permita apuntes."
            )

        # Fijar cuenta contable en el justificante (para el asiento posterior)
        justificante.cuenta_contable_id = cuenta_resuelta_id

        tesoreria = TesoreriaService(self.session)
        miembro = justificante.miembro
        nombre_miembro = (
            f"{miembro.nombre} {miembro.apellido1}".strip()
            if miembro
            else str(justificante.miembro_id)
        )

        apunte = await tesoreria.registrar_apunte(
            cuenta_id=cuenta_bancaria_id,
            fecha=fecha_pago or date.today(),
            importe=justificante.importe,
            tipo=TipoApunte.GASTO,
            concepto=f"{justificante.numero_justificante} - {justificante.concepto} ({nombre_miembro})",
            origen=OrigenApunte.JUSTIFICANTE_GASTO,
            entidad_origen_tipo="justificante_gasto",
            entidad_origen_id=justificante_id,
            referencia_externa=referencia,
        )

        # Generar asiento contable
        registro = RegistroContable(self.session)
        await registro.generar_asiento_para_apunte(apunte)

        # Marcar justificante como pagado
        justificante.estado = "PAGADO"
        justificante.apunte_caja_id = apunte.id
        justificante.cuenta_bancaria_id = cuenta_bancaria_id
        justificante.modo_pago = modo_pago
        justificante.fecha_pago = fecha_pago or date.today()
        self.session.add(justificante)
        await self.session.commit()

        return apunte

    # ── Anulación ────────────────────────────────────────────────────────────

    async def anular(
        self, justificante_id: UUID, motivo: Optional[str] = None
    ) -> JustificanteGasto:
        justificante = await self.obtener(justificante_id)
        if not justificante:
            raise ValueError(f"Justificante {justificante_id} no encontrado")
        if justificante.estado == "PAGADO":
            raise ValueError(
                "No se puede anular un justificante ya pagado — "
                "registrar un apunte de regularización en su lugar"
            )
        justificante.estado = "ANULADO"
        if motivo:
            obs_prev = justificante.observaciones or ""
            justificante.observaciones = f"{obs_prev}\nANULADO: {motivo}".strip()
        self.session.add(justificante)
        await self.session.commit()
        await self.session.refresh(justificante)
        return justificante

    # ── Consulta ─────────────────────────────────────────────────────────────

    async def obtener(self, justificante_id: UUID) -> Optional[JustificanteGasto]:
        r = await self.session.execute(
            select(JustificanteGasto).where(JustificanteGasto.id == justificante_id)
        )
        return r.scalars().first()

    async def listar(
        self,
        ejercicio: Optional[int] = None,
        miembro_id: Optional[UUID] = None,
        actividad_id: Optional[UUID] = None,
        agrupacion_id: Optional[UUID] = None,
        estado: Optional[str] = None,
    ) -> List[JustificanteGasto]:
        q = select(JustificanteGasto)
        filtros = []
        if ejercicio:
            filtros.append(JustificanteGasto.ejercicio == ejercicio)
        if miembro_id:
            filtros.append(JustificanteGasto.miembro_id == miembro_id)
        if actividad_id:
            filtros.append(JustificanteGasto.actividad_id == actividad_id)
        if agrupacion_id:
            filtros.append(JustificanteGasto.agrupacion_id == agrupacion_id)
        if estado:
            filtros.append(JustificanteGasto.estado == estado)
        if filtros:
            q = q.where(and_(*filtros))
        q = q.order_by(JustificanteGasto.numero_justificante.desc())
        r = await self.session.execute(q)
        return list(r.scalars().all())

    # ── Documentos probatorios ───────────────────────────────────────────────

    async def adjuntar_documento(
        self,
        justificante_id: UUID,
        nombre_archivo: str,
        url: str,
        mime_type: Optional[str] = None,
        tamano_bytes: Optional[int] = None,
        ocr_texto: Optional[str] = None,
        ocr_datos_json: Optional[str] = None,
    ) -> JustificanteGastoDocumento:
        """Registra un documento probatorio asociado a un justificante.

        El upload físico del archivo lo hace el endpoint REST. Aquí solo se
        registra la entrada en BD con la URL/path final.
        """
        justificante = await self.obtener(justificante_id)
        if not justificante:
            raise ValueError(f"Justificante {justificante_id} no encontrado")
        if justificante.estado in ("ANULADO",):
            raise ValueError("No se pueden adjuntar documentos a un justificante anulado.")
        doc = JustificanteGastoDocumento(
            justificante_id=justificante_id,
            nombre_archivo=nombre_archivo,
            url=url,
            mime_type=mime_type,
            tamano_bytes=tamano_bytes,
            ocr_texto=ocr_texto,
            ocr_datos_json=ocr_datos_json,
        )
        self.session.add(doc)
        await self.session.commit()
        await self.session.refresh(doc)
        return doc

    # ── Miembros elegibles para imputar a una actividad ─────────────────────

    async def miembros_elegibles_para_actividad(self, actividad_id: UUID):
        """Devuelve los miembros activos que pueden figurar como gastador en un
        justificante imputado a esta actividad.

        Reglas:
          - Actividad **de campaña**: miembros del grupo de trabajo de la actividad
            (`actividad.grupo_id`). Si la actividad no tiene grupo asignado,
            devuelve TODOS los miembros activos como fallback (no bloquea, deja
            elegir; el tesorero general puede saltarse la regla si hace falta).
          - Actividad **sin campaña** (permanente/puntual/recurrente interna):
            cualquier miembro activo (no aplica el filtro de equipo).
        """
        from app.modules.actividades.models.actividad import Actividad
        from app.modules.actividades.models.grupo import MiembroGrupo
        from app.modules.membresia.models.contacto import Contacto

        r = await self.session.execute(select(Actividad).where(Actividad.id == actividad_id))
        act = r.scalars().first()
        if not act:
            return []

        if act.campania_id and act.grupo_id:
            # Personas del grupo de la actividad (contactos activos)
            q = (
                select(Contacto)
                .join(MiembroGrupo, MiembroGrupo.miembro_id == Contacto.id)
                .where(
                    and_(
                        MiembroGrupo.grupo_id == act.grupo_id,
                        Contacto.activo.is_(True),
                        Contacto.eliminado.is_(False),
                    )
                )
                .order_by(Contacto.apellido1, Contacto.nombre)
            )
            r = await self.session.execute(q)
            return list(r.scalars().all())

        # Fallback (sin campaña, o de campaña sin grupo): todos los contactos activos
        r = await self.session.execute(
            select(Contacto)
            .where(and_(Contacto.activo.is_(True), Contacto.eliminado.is_(False)))
            .order_by(Contacto.apellido1, Contacto.nombre)
        )
        return list(r.scalars().all())

    async def eliminar_documento(self, documento_id: UUID) -> None:
        r = await self.session.execute(
            select(JustificanteGastoDocumento).where(JustificanteGastoDocumento.id == documento_id)
        )
        doc = r.scalars().first()
        if not doc:
            raise ValueError(f"Documento {documento_id} no encontrado")
        # Borrar archivo físico si existe (best-effort)
        try:
            import os
            from pathlib import Path
            p = Path(doc.url.lstrip("/"))
            # Solo intentar borrar si está bajo el directorio de uploads
            if "uploads/justificantes" in str(p):
                full = Path("/app") / p
                if full.exists():
                    os.remove(full)
        except Exception:
            pass
        await self.session.delete(doc)
        await self.session.commit()
