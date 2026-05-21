
    # ── Solicitudes de reducción de cuota ────────────────────────────────────

    async def presentar_solicitud_reduccion(
        self, miembro_id, motivo_reduccion_id, texto_solicitud=None, ejercicio=None,
    ):
        """Crea solicitud PRESENTADA. ValueError si ya hay una pendiente del ejercicio."""
        from ..models.cuotas import SolicitudReduccionCuota
        from datetime import date
        anio = ejercicio or date.today().year
        existe = await self.session.execute(
            select(SolicitudReduccionCuota).where(
                SolicitudReduccionCuota.miembro_id == miembro_id,
                SolicitudReduccionCuota.ejercicio == anio,
                SolicitudReduccionCuota.estado == "PRESENTADA",
                SolicitudReduccionCuota.eliminado == False,
            )
        )
        if existe.scalar_one_or_none():
            raise ValueError("Ya hay una solicitud de reducción pendiente para este ejercicio.")
        sol = SolicitudReduccionCuota(
            miembro_id=miembro_id, motivo_reduccion_id=motivo_reduccion_id,
            ejercicio=anio, estado="PRESENTADA",
            texto_solicitud=texto_solicitud, fecha_presentacion=date.today(),
        )
        self.session.add(sol)
        await self.session.commit()
        await self.session.refresh(sol)
        return sol

    async def aprobar_solicitud_reduccion(self, solicitud_id, resuelto_por_id):
        """Aprueba: actualiza miembro y recalcula CuotaAnual en curso."""
        from ..models.cuotas import SolicitudReduccionCuota, CuotaAnual, ImporteCuotaAnio
        from app.modules.membresia.models.miembro import Miembro
        from datetime import date
        sol = await self.session.get(SolicitudReduccionCuota, solicitud_id)
        if not sol:
            raise ValueError("Solicitud no encontrada.")
        if sol.estado != "PRESENTADA":
            raise ValueError(f"La solicitud no está pendiente (estado: {sol.estado}).")
        sol.estado = "APROBADA"
        sol.resuelto_por_id = resuelto_por_id
        sol.fecha_resolucion = date.today()
        miembro = await self.session.get(Miembro, sol.miembro_id)
        if miembro:
            miembro.motivo_reduccion_id = sol.motivo_reduccion_id
        motivo = await self.session.get(MotivoReduccionCuota, sol.motivo_reduccion_id)
        res = await self.session.execute(
            select(CuotaAnual).where(
                CuotaAnual.miembro_id == sol.miembro_id,
                CuotaAnual.ejercicio == sol.ejercicio,
                CuotaAnual.eliminado == False,
            )
        )
        cuota = res.scalar_one_or_none()
        if cuota and motivo and cuota.importe_pagado == Decimal("0.00"):
            cuota.motivo_reduccion_id = motivo.id
            if cuota.importe_cuota_anio_id:
                base = await self.session.get(ImporteCuotaAnio, cuota.importe_cuota_anio_id)
                if base:
                    cuota.importe = motivo.aplicar_a(base.importe)
        await self.session.commit()
        return True

    async def rechazar_solicitud_reduccion(self, solicitud_id, resuelto_por_id, motivo: str):
        from ..models.cuotas import SolicitudReduccionCuota
        from datetime import date
        sol = await self.session.get(SolicitudReduccionCuota, solicitud_id)
        if not sol or sol.estado != "PRESENTADA":
            raise ValueError("Solicitud no encontrada o no pendiente.")
        sol.estado = "RECHAZADA"
        sol.resuelto_por_id = resuelto_por_id
        sol.fecha_resolucion = date.today()
        sol.motivo_rechazo = motivo
        await self.session.commit()
        return True

    async def anular_solicitud_reduccion(self, solicitud_id):
        from ..models.cuotas import SolicitudReduccionCuota
        sol = await self.session.get(SolicitudReduccionCuota, solicitud_id)
        if not sol or sol.estado != "PRESENTADA":
            raise ValueError("Solicitud no encontrada o no en estado PRESENTADA.")
        sol.estado = "ANULADA"
        await self.session.commit()
        return True

    async def modificar_incremento_cuota(self, miembro_id, incremento: Decimal, observaciones=None):
        from ..models.cuotas import CuotaAnual, ImporteCuotaAnio
        from app.modules.membresia.models.miembro import Miembro
        from datetime import date
        if incremento < Decimal("0.00"):
            raise ValueError("El incremento no puede ser negativo.")
        miembro = await self.session.get(Miembro, miembro_id)
        if not miembro:
            raise ValueError("Miembro no encontrado.")
        miembro.incremento_cuota = incremento
        miembro.incremento_cuota_obs = (observaciones or "").strip() or None
        anio = date.today().year
        res = await self.session.execute(
            select(CuotaAnual).where(
                CuotaAnual.miembro_id == miembro_id, CuotaAnual.ejercicio == anio,
                CuotaAnual.eliminado == False,
            )
        )
        cuota = res.scalar_one_or_none()
        if cuota and cuota.importe_pagado == Decimal("0.00") and cuota.importe_cuota_anio_id:
            base = await self.session.get(ImporteCuotaAnio, cuota.importe_cuota_anio_id)
            if base:
                motivo = None
                if cuota.motivo_reduccion_id:
                    motivo = await self.session.get(MotivoReduccionCuota, cuota.motivo_reduccion_id)
                cuota.importe = (motivo.aplicar_a(base.importe) if motivo else base.importe) + incremento
        await self.session.commit()
        return True

    async def crear_motivo_reduccion(
        self, codigo: str, nombre: str, porcentaje_reduccion: float,
        descripcion=None, orden: int = 0, activo: bool = True,
    ):
        import uuid as _uuid
        if not (0 <= porcentaje_reduccion <= 100):
            raise ValueError("porcentaje_reduccion debe estar entre 0 y 100")
        motivo = MotivoReduccionCuota(
            id=_uuid.uuid4(), codigo=codigo, nombre=nombre, descripcion=descripcion,
            porcentaje_reduccion=Decimal(str(porcentaje_reduccion)), orden=orden, activo=activo,
        )
        self.session.add(motivo)
        await self.session.commit()
        await self.session.refresh(motivo)
        return motivo

    async def actualizar_motivo_reduccion(
        self, motivo_id, codigo=None, nombre=None, porcentaje_reduccion=None,
        descripcion=None, orden=None, activo=None,
    ):
        """D1.5: porcentaje congelado si ya hay recibos emitidos."""
        r = await self.session.execute(
            select(MotivoReduccionCuota).where(MotivoReduccionCuota.id == motivo_id)
        )
        motivo = r.scalars().first()
        if not motivo:
            raise ValueError(f"Motivo {motivo_id} no encontrado")
        if porcentaje_reduccion is not None:
            nuevo_pct = Decimal(str(porcentaje_reduccion))
            if nuevo_pct != motivo.porcentaje_reduccion:
                if await self.motivo_tiene_recibos(motivo.id):
                    raise ValueError(
                        "No se puede modificar el porcentaje de un motivo con recibos emitidos (D1.5)."
                    )
                if not (0 <= float(nuevo_pct) <= 100):
                    raise ValueError("porcentaje_reduccion debe estar entre 0 y 100")
                motivo.porcentaje_reduccion = nuevo_pct
        if codigo is not None: motivo.codigo = codigo
        if nombre is not None: motivo.nombre = nombre
        if descripcion is not None: motivo.descripcion = descripcion
        if orden is not None: motivo.orden = orden
        if activo is not None: motivo.activo = activo
        await self.session.commit()
        return motivo
