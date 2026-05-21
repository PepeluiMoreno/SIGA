# SEGMENTO 2/4 del resolver refactorizado economico_mutations.py
# Continua desde mut_seg1.py. Contiene: remesas SEPA (generar, enviar, extraordinaria, fallidos, preview, anular, XML, importar)

    async def generar_remesa_sepa(
        self, info: strawberry.Info, ejercicio: int, fecha_cobro: date,
        agrupacion_id: Optional[UUID] = None, observaciones: Optional[str] = None,
    ) -> str:
        remesa = await RemesaService(info.context.session).generar_remesa(
            ejercicio=ejercicio, fecha_cobro=fecha_cobro,
            agrupacion_id=agrupacion_id, observaciones=observaciones,
        )
        return str(remesa.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("REM_SEND")])
    async def marcar_remesa_enviada(self, info: strawberry.Info, remesa_id: UUID) -> bool:
        await RemesaService(info.context.session).marcar_enviada(remesa_id)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("REM_CREATE")])
    async def generar_remesa_extraordinaria(
        self, info: strawberry.Info, ejercicio: int, fecha_cobro: date,
        concepto: str, miembro_ids: List[UUID], importe_por_miembro: float,
        agrupacion_id: Optional[UUID] = None, observaciones: Optional[str] = None,
    ) -> str:
        remesa = await RemesaService(info.context.session).generar_remesa_extraordinaria(
            ejercicio=ejercicio, fecha_cobro=fecha_cobro, concepto=concepto,
            miembro_ids=miembro_ids, importe_por_miembro=Decimal(str(importe_por_miembro)),
            agrupacion_id=agrupacion_id, observaciones=observaciones,
        )
        return str(remesa.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("REM_RESEND")])
    async def generar_remesa_fallidos(
        self, info: strawberry.Info, remesa_origen_id: UUID, fecha_cobro: date,
        observaciones: Optional[str] = None,
    ) -> str:
        remesa = await RemesaService(info.context.session).generar_remesa_fallidos(
            remesa_origen_id=remesa_origen_id, fecha_cobro=fecha_cobro, observaciones=observaciones,
        )
        return str(remesa.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("REM_PREVIEW")])
    async def previsualizar_remesa(
        self, info: strawberry.Info, ejercicio: int, agrupacion_id: Optional[UUID] = None,
    ) -> PreviewRemesaType:
        preview = await RemesaService(info.context.session).previsualizar_remesa(
            ejercicio=ejercicio, agrupacion_id=agrupacion_id,
        )
        def _linea(c):
            return CuotaPreviewType(
                cuota_id=UUID(c["cuota_id"]), miembro_id=UUID(c["miembro_id"]),
                miembro_nombre=c["miembro_nombre"], importe_pendiente=c["importe_pendiente"],
                motivo_exclusion=c["motivo_exclusion"],
            )
        ord_ex = preview.get("ordinaria_existente")
        return PreviewRemesaType(
            ejercicio=preview["ejercicio"], n_incluidas=preview["n_incluidas"],
            n_excluidas=preview["n_excluidas"], importe_total=preview["importe_total"],
            incluidas=[_linea(c) for c in preview["incluidas"]],
            excluidas=[_linea(c) for c in preview["excluidas"]],
            ordinaria_existente=(
                OrdinariaExistenteType(id=UUID(ord_ex["id"]), referencia=ord_ex["referencia"])
                if ord_ex else None
            ),
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("REM_ANULAR")])
    async def anular_remesa(self, info: strawberry.Info, remesa_id: UUID) -> bool:
        await RemesaService(info.context.session).anular_remesa(remesa_id=remesa_id)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("REM_XML")])
    async def generar_xml_sepa(self, info: strawberry.Info, remesa_id: UUID) -> str:
        import base64
        xml_bytes = await RemesaService(info.context.session).generar_xml_sepa(remesa_id=remesa_id)
        return base64.b64encode(xml_bytes).decode("ascii")

    @strawberry.mutation
    async def importar_fallidos_banco(
        self, info: strawberry.Info, remesa_id: UUID, fallidos: List[FallidoBancoInput],
    ) -> int:
        fallidos_dict = [
            {"orden_id": f.orden_id, "codigo": f.codigo,
             "motivo": f.motivo or "", "fecha": f.fecha}
            for f in fallidos
        ]
        return await RemesaService(info.context.session).importar_fallidos_banco(remesa_id, fallidos_dict)
