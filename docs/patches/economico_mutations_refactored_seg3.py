# SEGMENTO 3/4 del resolver refactorizado economico_mutations.py
# Contiene: recibos (emitir lote/individual, cobrar, fallido, anular, comunicar, PDF, email)

    @strawberry.mutation(permission_classes=[RequireTransaction("RCB_EMIT_LOTE")])
    async def emitir_recibos_lote(
        self, info: strawberry.Info, ejercicio: int, tipo: str = "CUOTA_ORDINARIA",
        concepto: Optional[str] = None, miembro_ids: Optional[List[UUID]] = None,
        agrupacion_id: Optional[UUID] = None, fecha_vencimiento: Optional[date] = None,
    ) -> int:
        recibos = await ReciboService(info.context.session).emitir_lote(
            ejercicio=ejercicio, tipo=tipo, concepto=concepto,
            miembro_ids=miembro_ids, agrupacion_id=agrupacion_id, fecha_vencimiento=fecha_vencimiento,
        )
        return len(recibos)

    @strawberry.mutation(permission_classes=[RequireTransaction("RCB_EMIT_LOTE")])
    async def emitir_recibo_individual(
        self, info: strawberry.Info, ejercicio: int, miembro_id: UUID,
        concepto: str, importe: float, tipo: str = "EXTRAORDINARIA",
        cuota_id: Optional[UUID] = None, fecha_vencimiento: Optional[date] = None,
        observaciones: Optional[str] = None,
    ) -> str:
        recibo = await ReciboService(info.context.session).emitir_recibo_individual(
            ejercicio=ejercicio, miembro_id=miembro_id, concepto=concepto,
            importe=Decimal(str(importe)), tipo=tipo, cuota_id=cuota_id,
            fecha_vencimiento=fecha_vencimiento, observaciones=observaciones,
        )
        return str(recibo.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("RCB_MARCAR_COBRADO")])
    async def marcar_recibo_cobrado(
        self, info: strawberry.Info, recibo_id: UUID,
        cuenta_bancaria_id: Optional[UUID] = None, importe_cobrado: Optional[float] = None,
        fecha_cobro: Optional[date] = None, modo_cobro: Optional[str] = None,
        orden_cobro_id: Optional[UUID] = None, referencia: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> bool:
        await ReciboService(info.context.session).marcar_cobrado(
            recibo_id=recibo_id,
            importe_cobrado=Decimal(str(importe_cobrado)) if importe_cobrado is not None else None,
            fecha_cobro=fecha_cobro, modo_cobro=modo_cobro, orden_cobro_id=orden_cobro_id,
            cuenta_bancaria_id=cuenta_bancaria_id, referencia=referencia, observaciones=observaciones,
        )
        return True

    @strawberry.mutation
    async def marcar_recibo_fallido(
        self, info: strawberry.Info, recibo_id: UUID, codigo_sepa: str, motivo: Optional[str] = None,
    ) -> bool:
        await ReciboService(info.context.session).marcar_fallido(recibo_id, codigo_sepa, motivo)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("RCB_ANULAR")])
    async def anular_recibo(
        self, info: strawberry.Info, recibo_id: UUID, motivo: Optional[str] = None,
    ) -> bool:
        await ReciboService(info.context.session).anular_recibo(recibo_id, motivo)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("RCB_FAIL_NOTIFY")])
    async def comunicar_recibos_fallidos(
        self, info: strawberry.Info, recibo_ids: List[UUID], plantilla_email_id: UUID,
    ) -> int:
        # Antes: UPDATE directo en el resolver. Ahora: delega en ReciboService.
        return await ReciboService(info.context.session).comunicar_fallidos(recibo_ids, plantilla_email_id)

    @strawberry.mutation(permission_classes=[RequireTransaction("RCB_DESCARGAR_PDF")])
    async def descargar_recibo_pdf(self, info: strawberry.Info, recibo_id: UUID) -> str:
        # Antes: 40 líneas de reportlab en el resolver. Ahora: delega en ReciboService.
        return await ReciboService(info.context.session).generar_pdf(recibo_id)

    @strawberry.mutation(permission_classes=[RequireTransaction("RCB_ENVIAR_EMAIL")])
    async def enviar_recibo_email(
        self, info: strawberry.Info, recibo_id: UUID, plantilla_email_id: UUID,
    ) -> bool:
        await ReciboService(info.context.session).registrar_intencion_envio_email(recibo_id, plantilla_email_id)
        return True

    # ─── Justificantes de gasto ──────────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("JUST_PRESENTAR")])
    async def presentar_justificante_gasto(
        self, info: strawberry.Info, miembro_id: UUID, actividad_id: UUID,
        lineas: list[LineaJustificanteInput], partida_actividad_id: Optional[UUID] = None,
        agrupacion_id: Optional[UUID] = None, observaciones: Optional[str] = None,
        ejercicio: Optional[int] = None, presentado_por_tesorero_id: Optional[UUID] = None,
    ) -> str:
        if presentado_por_tesorero_id is not None:
            if not await info.context.check_permission("JUST_APROBAR"):
                raise PermissionError("Solo el tesorero puede presentar justificantes en nombre de otros socios.")
        if not lineas:
            raise ValueError("Debe haber al menos una línea de gasto.")
        lineas_norm = [{
            "concepto": l.concepto, "importe": Decimal(str(l.importe)),
            "fecha_gasto": l.fecha_gasto, "observaciones": l.observaciones,
        } for l in lineas]
        j = await JustificanteGastoService(info.context.session).presentar(
            miembro_id=miembro_id, actividad_id=actividad_id, lineas=lineas_norm,
            partida_actividad_id=partida_actividad_id, agrupacion_id=agrupacion_id,
            observaciones=observaciones, ejercicio=ejercicio,
            presentado_por_tesorero_id=presentado_por_tesorero_id,
        )
        return str(j.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("JUST_ACEPTAR")])
    async def aceptar_justificante_gasto(
        self, info: strawberry.Info, justificante_id: UUID, aceptador_id: UUID,
    ) -> bool:
        await JustificanteGastoService(info.context.session).aceptar(justificante_id, aceptador_id)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("JUST_APROBAR")])
    async def aprobar_justificante_gasto(
        self, info: strawberry.Info, justificante_id: UUID, aprobador_id: UUID,
    ) -> bool:
        await JustificanteGastoService(info.context.session).aprobar(justificante_id, aprobador_id)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("JUST_APROBAR")])
    async def rechazar_justificante_gasto(
        self, info: strawberry.Info, justificante_id: UUID, aprobador_id: UUID, motivo: str,
    ) -> bool:
        await JustificanteGastoService(info.context.session).rechazar(justificante_id, aprobador_id, motivo)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("JUST_PAGAR")])
    async def pagar_justificante_gasto(
        self, info: strawberry.Info, justificante_id: UUID, cuenta_bancaria_id: UUID,
        modo_pago: str = "TRANSFERENCIA", fecha_pago: Optional[date] = None,
        referencia: Optional[str] = None, cuenta_contable_id: Optional[UUID] = None,
    ) -> str:
        apunte = await JustificanteGastoService(info.context.session).pagar(
            justificante_id=justificante_id, cuenta_bancaria_id=cuenta_bancaria_id,
            modo_pago=modo_pago, fecha_pago=fecha_pago,
            referencia=referencia, cuenta_contable_id=cuenta_contable_id,
        )
        return str(apunte.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("JUST_PRESENTAR")])
    async def anular_justificante_gasto(
        self, info: strawberry.Info, justificante_id: UUID, motivo: Optional[str] = None,
    ) -> bool:
        await JustificanteGastoService(info.context.session).anular(justificante_id, motivo)
        return True
