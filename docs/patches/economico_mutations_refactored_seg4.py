# SEGMENTO 4/4 del resolver refactorizado economico_mutations.py
# Contiene: solicitudes reducción, incremento cuota, cuotas ejercicio, motivos, donaciones

    # ─── Solicitudes de reducción ────────────────────────────────────────

    @strawberry.mutation
    async def presentar_solicitud_reduccion_cuota(
        self, info: strawberry.Info, miembro_id: UUID, motivo_reduccion_id: UUID,
        texto_solicitud: Optional[str] = None, ejercicio: Optional[int] = None,
    ) -> str:
        sol = await CuotaService(info.context.session).presentar_solicitud_reduccion(
            miembro_id=miembro_id, motivo_reduccion_id=motivo_reduccion_id,
            texto_solicitud=texto_solicitud, ejercicio=ejercicio,
        )
        return str(sol.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CUOT_EXEMPT")])
    async def aprobar_solicitud_reduccion_cuota(
        self, info: strawberry.Info, solicitud_id: UUID, resuelto_por_id: UUID,
    ) -> bool:
        return await CuotaService(info.context.session).aprobar_solicitud_reduccion(solicitud_id, resuelto_por_id)

    @strawberry.mutation(permission_classes=[RequireTransaction("CUOT_EXEMPT")])
    async def rechazar_solicitud_reduccion_cuota(
        self, info: strawberry.Info, solicitud_id: UUID, resuelto_por_id: UUID, motivo: str,
    ) -> bool:
        return await CuotaService(info.context.session).rechazar_solicitud_reduccion(solicitud_id, resuelto_por_id, motivo)

    @strawberry.mutation
    async def anular_solicitud_reduccion_cuota(self, info: strawberry.Info, solicitud_id: UUID) -> bool:
        return await CuotaService(info.context.session).anular_solicitud_reduccion(solicitud_id)

    @strawberry.mutation
    async def modificar_incremento_cuota(
        self, info: strawberry.Info, miembro_id: UUID, incremento: Decimal,
        observaciones: Optional[str] = None,
    ) -> bool:
        return await CuotaService(info.context.session).modificar_incremento_cuota(
            miembro_id=miembro_id, incremento=incremento, observaciones=observaciones,
        )

    # ─── Cuotas del ejercicio ───────────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("CUOT_EJERCICIO_CONFIG")])
    async def configurar_cuota_ejercicio(
        self, info: strawberry.Info, ejercicio: int, importe_base: float,
        clonar_de: Optional[int] = None, observaciones: Optional[str] = None,
    ) -> UUID:
        cfg = await CuotaService(info.context.session).configurar_ejercicio(
            ejercicio=ejercicio, importe_base=Decimal(str(importe_base)),
            clonar_de=clonar_de, observaciones=observaciones,
        )
        return cfg.id

    @strawberry.mutation(permission_classes=[RequireTransaction("CUOT_EJERCICIO_CONFIG")])
    async def eliminar_cuota_ejercicio(self, info: strawberry.Info, ejercicio: int) -> bool:
        return await CuotaService(info.context.session).eliminar_cuota_ejercicio(ejercicio)

    @strawberry.mutation(permission_classes=[RequireTransaction("CUOT_GENERATE")])
    async def previsualizar_generacion_cuotas(
        self, info: strawberry.Info, ejercicio: int,
    ) -> PreviewGeneracionCuotasType:
        p = await CuotaService(info.context.session).previsualizar_generacion(ejercicio)
        return PreviewGeneracionCuotasType(
            ejercicio=p["ejercicio"], importe_base=p["importe_base"],
            desglose=[DesgloseTipoMiembroType(**d) for d in p["desglose"]],
            n_generables=p["n_generables"], n_excluidos=p["n_excluidos"],
            n_existentes=p["n_existentes"], total_esperado=p["total_esperado"],
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("CUOT_GENERATE")])
    async def generar_cuotas_individuales(
        self, info: strawberry.Info, ejercicio: int, fecha_vencimiento: Optional[date] = None,
    ) -> ResultadoGeneracionCuotasType:
        r = await CuotaService(info.context.session).generar_cuotas_individuales(ejercicio, fecha_vencimiento)
        return ResultadoGeneracionCuotasType(**r)

    @strawberry.mutation(permission_classes=[RequireTransaction("CUOT_GENERATE")])
    async def recalcular_cuota(self, info: strawberry.Info, cuota_id: UUID) -> UUID:
        c = await CuotaService(info.context.session).recalcular_cuota(cuota_id)
        return c.id

    @strawberry.mutation(permission_classes=[RequireTransaction("CUOT_MOTIVO_REDUC_MGMT")])
    async def crear_motivo_reduccion(
        self, info: strawberry.Info, codigo: str, nombre: str, porcentaje_reduccion: float,
        descripcion: Optional[str] = None, orden: Optional[int] = 0, activo: Optional[bool] = True,
    ) -> UUID:
        motivo = await CuotaService(info.context.session).crear_motivo_reduccion(
            codigo=codigo, nombre=nombre, porcentaje_reduccion=porcentaje_reduccion,
            descripcion=descripcion, orden=orden or 0, activo=activo if activo is not None else True,
        )
        return motivo.id

    @strawberry.mutation(permission_classes=[RequireTransaction("CUOT_MOTIVO_REDUC_MGMT")])
    async def actualizar_motivo_reduccion(
        self, info: strawberry.Info, id: UUID,
        codigo: Optional[str] = None, nombre: Optional[str] = None,
        porcentaje_reduccion: Optional[float] = None, descripcion: Optional[str] = None,
        orden: Optional[int] = None, activo: Optional[bool] = None,
    ) -> UUID:
        motivo = await CuotaService(info.context.session).actualizar_motivo_reduccion(
            motivo_id=id, codigo=codigo, nombre=nombre,
            porcentaje_reduccion=porcentaje_reduccion, descripcion=descripcion,
            orden=orden, activo=activo,
        )
        return motivo.id

    # ─── Donaciones ─────────────────────────────────────────────────

    @strawberry.mutation(permission_classes=[RequireTransaction("DON_CREATE")])
    async def registrar_donacion(
        self, info: strawberry.Info, importe: float, fecha_donacion: date,
        tipo: str = "DINERARIA", caracter: str = "PUNTUAL",
        miembro_id: Optional[UUID] = None, donante_nombre: Optional[str] = None,
        donante_dni: Optional[str] = None, donante_email: Optional[str] = None,
        donante_telefono: Optional[str] = None, concepto_id: Optional[UUID] = None,
        campania_id: Optional[UUID] = None, modo_ingreso: Optional[str] = None,
        referencia_pago: Optional[str] = None, descripcion_especie: Optional[str] = None,
        valoracion: Optional[float] = None, documento_valoracion: Optional[str] = None,
        anonima: bool = False, observaciones: Optional[str] = None,
        agrupacion_id: Optional[UUID] = None, cobrar_inmediato: bool = False,
        cuenta_bancaria_id: Optional[UUID] = None,
    ) -> str:
        donacion = await DonacionService(info.context.session).registrar(
            importe=Decimal(str(importe)), fecha_donacion=fecha_donacion, tipo=tipo, caracter=caracter,
            miembro_id=miembro_id, donante_nombre=donante_nombre, donante_dni=donante_dni,
            donante_email=donante_email, donante_telefono=donante_telefono,
            concepto_id=concepto_id, campania_id=campania_id, modo_ingreso=modo_ingreso,
            referencia_pago=referencia_pago, descripcion_especie=descripcion_especie,
            valoracion=Decimal(str(valoracion)) if valoracion is not None else None,
            documento_valoracion=documento_valoracion, anonima=anonima,
            observaciones=observaciones, agrupacion_id=agrupacion_id,
            cobrar_inmediato=cobrar_inmediato, cuenta_bancaria_id=cuenta_bancaria_id,
        )
        return str(donacion.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("DON_CREATE")])
    async def marcar_donacion_cobrada(
        self, info: strawberry.Info, donacion_id: UUID,
        cuenta_bancaria_id: Optional[UUID] = None, fecha_cobro: Optional[date] = None,
    ) -> str:
        d = await DonacionService(info.context.session).marcar_cobrada(
            donacion_id=donacion_id, cuenta_bancaria_id=cuenta_bancaria_id, fecha_cobro=fecha_cobro,
        )
        return str(d.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("DON_CREATE")])
    async def anular_donacion(
        self, info: strawberry.Info, donacion_id: UUID, motivo: Optional[str] = None,
    ) -> str:
        d = await DonacionService(info.context.session).anular(donacion_id=donacion_id, motivo=motivo)
        return str(d.id)

    @strawberry.mutation(permission_classes=[RequireTransaction("DON_CERT")])
    async def emitir_certificado_donacion_anual(
        self, info: strawberry.Info, ejercicio: int, nif_donante: str, tipo: str,
    ) -> CertificadoEmitidoType:
        """Ahora DonacionService lee los datos de la org internamente via _cfg_org()."""
        import base64
        svc = DonacionService(info.context.session)
        org_nombre, org_nif = await svc._cfg_org()
        numero, pdf_bytes = await svc.emitir_certificado_anual(
            ejercicio=ejercicio, nif_donante=nif_donante, tipo=tipo,
            organizacion_nombre=org_nombre, organizacion_nif=org_nif,
        )
        return CertificadoEmitidoType(numero=numero, pdf_base64=base64.b64encode(pdf_bytes).decode("ascii"))

    @strawberry.mutation(permission_classes=[RequireTransaction("DON_CERT")])
    async def listar_donaciones_certificables(
        self, info: strawberry.Info, ejercicio: int,
    ) -> list[CertificableDonacionType]:
        items = await DonacionService(info.context.session).listar_certificables_por_ejercicio(ejercicio)
        return [
            CertificableDonacionType(
                nif=item["nif"], nombre=item["nombre"], tipo=item["tipo"],
                total=float(item["total"]), n_donaciones=item["n"],
                donacion_ids=item["donacion_ids"], todas_certificadas=item["todas_certificadas"],
            )
            for item in items
        ]
