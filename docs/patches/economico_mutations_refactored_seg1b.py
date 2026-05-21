# SEGMENTO 1b/4 del resolver refactorizado
# Contiene: liquidar_remesa y registrar_pago_cuota_manual
# Precede al segmento 2 (remesas SEPA)

    @strawberry.mutation(permission_classes=[RequireTransaction("REM_PROCESS")])
    async def liquidar_remesa(
        self, info: strawberry.Info, remesa_id: UUID, cuenta_bancaria_id: UUID,
        fecha_liquidacion: date, cobradas: list[UUID],
        fallidas: Optional[list[FallidoBancoInput]] = None,
    ) -> ResultadoLiquidacionType:
        fallidas_dict = [
            {"orden_id": f.orden_id, "codigo": f.codigo,
             "motivo": f.motivo or "", "fecha": f.fecha.isoformat() if f.fecha else None}
            for f in (fallidas or [])
        ]
        res = await RemesaService(info.context.session).liquidar_remesa(
            remesa_id=remesa_id, fecha_liquidacion=fecha_liquidacion,
            cuenta_bancaria_id=cuenta_bancaria_id, cobradas=cobradas, fallidas=fallidas_dict,
        )
        return ResultadoLiquidacionType(
            n_cobradas=res["n_cobradas"], n_fallidas=res["n_fallidas"],
            importe_cobrado=res["importe_cobrado"],
            apunte_id=UUID(res["apunte_id"]) if res["apunte_id"] else None,
            asiento_id=UUID(res["asiento_id"]) if res["asiento_id"] else None,
            remesa_estado=res["remesa_estado"],
        )

    @strawberry.mutation
    async def registrar_pago_cuota_manual(
        self, info: strawberry.Info, cuota_id: UUID, cuenta_bancaria_id: UUID,
        importe: float, modo_ingreso: str, fecha_pago: Optional[date] = None,
        referencia: Optional[str] = None, observaciones: Optional[str] = None,
    ) -> str:
        apunte = await TesoreriaService(info.context.session).registrar_pago_cuota_manual(
            cuota_id=cuota_id, cuenta_bancaria_id=cuenta_bancaria_id,
            importe=Decimal(str(importe)), modo_ingreso=modo_ingreso,
            fecha_pago=fecha_pago, referencia=referencia, observaciones=observaciones,
        )
        return str(apunte.id)
