# SEGMENTO 1a — clase EconomicoFlujosMutation (tesorería + contabilidad + previsualizar liquidación)
# Continúa en seg1b, seg2, seg3, seg4

@strawberry.type
class EconomicoFlujosMutation:
    """Mutations del módulo Económico con lógica de negocio (no solo CRUD)."""

    # ─── Tesorería ────────────────────────────────────────────────────────────

    @strawberry.mutation
    async def registrar_apunte_caja(
        self, info: strawberry.Info, cuenta_id: UUID, fecha: date, importe: float,
        tipo: str, concepto: str, origen: Optional[str] = None,
        entidad_origen_tipo: Optional[str] = None, entidad_origen_id: Optional[UUID] = None,
        referencia_externa: Optional[str] = None, observaciones: Optional[str] = None,
        actividad_id: Optional[UUID] = None, campania_id: Optional[UUID] = None,
    ) -> str:
        session = info.context.session
        svc = TesoreriaService(session)
        if actividad_id is not None:
            campania_id = await svc.validar_imputacion_actividad(actividad_id, campania_id)
        apunte = await svc.registrar_apunte(
            cuenta_id=cuenta_id, fecha=fecha, importe=Decimal(str(importe)),
            tipo=TipoApunte(tipo), concepto=concepto,
            origen=OrigenApunte(origen) if origen else None,
            entidad_origen_tipo=entidad_origen_tipo, entidad_origen_id=entidad_origen_id,
            referencia_externa=referencia_externa, observaciones=observaciones,
            actividad_id=actividad_id, campania_id=campania_id,
        )
        await RegistroContable(session).generar_asiento_para_apunte(apunte)
        return str(apunte.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CON_CONCILIAR_APUNTE")])
    async def marcar_apunte_conciliado(
        self, info: strawberry.Info, apunte_id: UUID, fecha_conciliacion: Optional[date] = None,
    ) -> bool:
        await TesoreriaService(info.context.session).marcar_apunte_conciliado(apunte_id, fecha_conciliacion)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("CON_CONCILIAR_APUNTE")])
    async def desmarcar_apunte_conciliado(self, info: strawberry.Info, apunte_id: UUID) -> bool:
        await TesoreriaService(info.context.session).desmarcar_apunte_conciliado(apunte_id)
        return True

    @strawberry.mutation
    async def actualizar_metadatos_apunte_caja(
        self, info: strawberry.Info, apunte_id: UUID, concepto: Optional[str] = None,
        observaciones: Optional[str] = None, actividad_id: Optional[UUID] = None,
        campania_id: Optional[UUID] = None, categoria_fiscal_id: Optional[UUID] = None,
        limpiar_actividad: bool = False, limpiar_categoria_fiscal: bool = False,
    ) -> str:
        session = info.context.session
        svc = TesoreriaService(session)
        if actividad_id is not None and not limpiar_actividad:
            campania_id = await svc.validar_imputacion_actividad(actividad_id, campania_id)
        apunte = await svc.actualizar_metadatos_apunte(
            apunte_id, concepto=concepto, observaciones=observaciones,
            actividad_id=actividad_id, campania_id=campania_id,
            categoria_fiscal_id=categoria_fiscal_id,
            limpiar_actividad=limpiar_actividad, limpiar_categoria_fiscal=limpiar_categoria_fiscal,
        )
        return str(apunte.id)

    @strawberry.mutation
    async def anular_apunte_caja(self, info: strawberry.Info, apunte_id: UUID, motivo: str) -> str:
        contra = await TesoreriaService(info.context.session).anular_apunte(apunte_id, motivo)
        return str(contra.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CON_CONCILIAR_APUNTE")])
    async def conciliar_apunte_con_extracto(
        self, info: strawberry.Info, apunte_id: UUID, extracto_id: UUID, metodo: str = "MANUAL",
    ) -> str:
        c = await TesoreriaService(info.context.session).conciliar_apunte_con_extracto(
            apunte_id=apunte_id, extracto_id=extracto_id,
            metodo=MetodoConciliacion(metodo),
            usuario_id=getattr(info.context.user, 'id', None),
        )
        return str(c.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CON_CONFIRMAR_PERIODO")])
    async def confirmar_conciliacion_periodo(self, info: strawberry.Info, conciliacion_id: UUID) -> bool:
        await TesoreriaService(info.context.session).confirmar_conciliacion_periodo(conciliacion_id)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("CON_IMPORTAR_EXTRACTO")])
    async def importar_extracto_norma43(self, info: strawberry.Info, cuenta_id: UUID, archivo_b64: str) -> int:
        import base64
        svc = TesoreriaService(info.context.session)
        lineas = TesoreriaService.parse_norma43(base64.b64decode(archivo_b64))
        return len(await svc.importar_extracto(cuenta_id=cuenta_id, lineas=lineas))

    @strawberry.mutation(permission_classes=[RequireTransaction("CON_IMPORTAR_EXTRACTO")])
    async def importar_extracto_csv(self, info: strawberry.Info, cuenta_id: UUID, lineas_json: str) -> int:
        import json
        try:
            lineas = json.loads(lineas_json)
        except Exception as e:
            raise ValueError(f"CSV no parseable: {e}")
        if not isinstance(lineas, list):
            raise ValueError("Las líneas deben ser una lista JSON.")
        return len(await TesoreriaService(info.context.session).importar_extracto(cuenta_id=cuenta_id, lineas=lineas))

    @strawberry.mutation(permission_classes=[RequireTransaction("CON_CONCILIAR_APUNTE")])
    async def romper_conciliacion(self, info: strawberry.Info, conciliacion_id: UUID) -> bool:
        await TesoreriaService(info.context.session).romper_conciliacion(conciliacion_id)
        return True

    # ─── Contabilidad ─────────────────────────────────────────────────────────

    @strawberry.mutation
    async def confirmar_asiento_contable(self, info: strawberry.Info, asiento_id: UUID) -> bool:
        await ContabilidadService(info.context.session).confirmar_asiento(asiento_id)
        return True

    @strawberry.mutation
    async def anular_asiento_contable(self, info: strawberry.Info, asiento_id: UUID) -> bool:
        await ContabilidadService(info.context.session).anular_asiento(asiento_id)
        return True

    # ─── Liquidación automática ────────────────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("REM_PROCESS")])
    async def previsualizar_liquidacion_remesa(
        self, info: strawberry.Info, remesa_id: UUID, tipo_fichero: str,
        fichero_b64: Optional[str] = None,
        fallidos_manual: Optional[list[FallidoBancoInput]] = None,
    ) -> PreviewLiquidacionType:
        import base64
        svc = RemesaService(info.context.session)
        contenido = base64.b64decode(fichero_b64) if fichero_b64 else None
        fallidos_dict = [
            {"orden_id": f.orden_id, "codigo": f.codigo,
             "motivo": f.motivo or "", "fecha": f.fecha.isoformat() if f.fecha else None}
            for f in (fallidos_manual or [])
        ] or None
        preview = await svc.previsualizar_liquidacion(
            remesa_id=remesa_id, tipo_fichero=tipo_fichero,
            contenido=contenido, fallidos_manual=fallidos_dict,
        )
        return PreviewLiquidacionType(
            remesa_referencia=preview["remesa_referencia"],
            cobradas=[PreviewOrdenCobradaType(**c) for c in preview["cobradas"]],
            fallidas=[PreviewOrdenFallidaType(**f) for f in preview["fallidas"]],
            no_emparejadas=[PreviewSinEmparejarType(**n) for n in preview["no_emparejadas"]],
            totales=PreviewTotalesType(**preview["totales"]),
        )
    # continúa en seg1b.py
