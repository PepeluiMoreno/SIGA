# PARTE 2/2 del CampaniaService
# Contiene: aplicar_plantilla, CRUD de plantillas, clonar, propagar_a_subcampanias
# Ver parte 1 en campania_service_p1.py para imports, __init__ y métodos básicos

    async def aplicar_plantilla(
        self, campania_id: uuid.UUID, plantilla_id: uuid.UUID,
    ) -> "Campania":
        """Clona metas, partidas, actividades y tareas de una plantilla a la campaña."""
        from app.modules.actividades.models.actividad import Actividad, TipoActividad
        from app.modules.actividades.models.tarea import Tarea
        from app.modules.configuracion.models.estados import EstadoAccion, EstadoTarea
        from sqlalchemy import select
        from datetime import timedelta

        plantilla = (await self.session.execute(
            select(PlantillaCampania).where(PlantillaCampania.id == plantilla_id)
        )).scalar_one()
        campania = await self._get(campania_id)

        default_tipo = (await self.session.execute(
            select(TipoActividad).order_by(TipoActividad.nombre).limit(1)
        )).scalar_one_or_none()
        default_ea = (await self.session.execute(
            select(EstadoAccion).order_by(EstadoAccion.orden.asc().nulls_last()).limit(1)
        )).scalar_one_or_none()
        default_et = (await self.session.execute(
            select(EstadoTarea).order_by(EstadoTarea.orden.asc().nulls_last()).limit(1)
        )).scalar_one_or_none()

        for pm in plantilla.metas:
            self.session.add(MetaCampania(
                campania_id=campania_id, tipo_meta_id=pm.tipo_meta_id,
                valor_planificado=pm.valor_sugerido, notas=pm.notas, orden=pm.orden,
            ))
        for pp in plantilla.partidas:
            self.session.add(PartidaPresupuestoCampania(
                campania_id=campania_id, concepto=pp.concepto,
                importe_estimado=pp.importe_estimado, tipo_partida=pp.tipo_partida, orden=pp.orden,
            ))
        for pa in plantilla.actividades:
            act = Actividad(
                nombre=pa.nombre, descripcion=pa.descripcion,
                tipo_actividad_id=pa.tipo_actividad_id or (default_tipo.id if default_tipo else None),
                estado_id=default_ea.id if default_ea else None, campania_id=campania_id,
            )
            if campania.fecha_inicio_plan and pa.duracion_dias is not None:
                act.fecha_inicio = campania.fecha_inicio_plan + timedelta(days=pa.duracion_dias)
            self.session.add(act)
            await self.session.flush()
            for pt in pa.tareas:
                self.session.add(Tarea(
                    titulo=pt.titulo, descripcion=pt.descripcion,
                    horas_estimadas=pt.horas_estimadas, orden=pt.orden,
                    actividad_id=act.id, estado_id=default_et.id if default_et else None,
                ))
        await self.session.commit()
        return await self._get(campania_id)

    async def crear_plantilla(self, tipo_campania_id, nombre, descripcion=None, activo=True):
        from sqlalchemy import select
        p = PlantillaCampania(tipo_campania_id=tipo_campania_id, nombre=nombre,
                               descripcion=descripcion, activo=activo)
        self.session.add(p)
        await self.session.commit()
        return (await self.session.execute(select(PlantillaCampania).where(PlantillaCampania.id == p.id))).scalar_one()

    async def actualizar_plantilla(self, plantilla_id, campos: dict):
        from sqlalchemy import select
        p = (await self.session.execute(select(PlantillaCampania).where(PlantillaCampania.id == plantilla_id))).scalar_one()
        for k, v in campos.items():
            if v is not None:
                setattr(p, k, v)
        await self.session.commit()
        return (await self.session.execute(select(PlantillaCampania).where(PlantillaCampania.id == plantilla_id))).scalar_one()

    async def guardar_metas_plantilla(self, plantilla_id, metas: list):
        from sqlalchemy import select
        await self.session.execute(sa_delete(PlantillaMeta).where(PlantillaMeta.plantilla_id == plantilla_id))
        for m in metas:
            self.session.add(PlantillaMeta(plantilla_id=plantilla_id, **m))
        await self.session.commit()
        return (await self.session.execute(select(PlantillaCampania).where(PlantillaCampania.id == plantilla_id))).scalar_one()

    async def guardar_partidas_plantilla(self, plantilla_id, partidas: list):
        from sqlalchemy import select
        await self.session.execute(sa_delete(PlantillaPartida).where(PlantillaPartida.plantilla_id == plantilla_id))
        for p in partidas:
            self.session.add(PlantillaPartida(plantilla_id=plantilla_id, **p))
        await self.session.commit()
        return (await self.session.execute(select(PlantillaCampania).where(PlantillaCampania.id == plantilla_id))).scalar_one()

    async def clonar(
        self, campania_id, nombre, offset_dias=0,
        incluir_metas=True, incluir_partidas=True, incluir_canales=True,
        incluir_actividades=True, incluir_subcampanias=False, padre_id=None,
    ):
        """Clona una campaña con todas sus entidades. Soporta recursión para subcampañas."""
        from app.modules.actividades.models.actividad import Actividad
        from app.modules.actividades.models.tarea import Tarea
        from app.modules.configuracion.models.estados import EstadoAccion, EstadoTarea, EstadoCampania
        from sqlalchemy import select
        from datetime import timedelta

        origen = (await self.session.execute(select(Campania).where(Campania.id == campania_id))).scalar_one()
        estado_inicial = (await self.session.execute(
            select(EstadoCampania).order_by(EstadoCampania.orden.asc().nulls_last()).limit(1)
        )).scalar_one_or_none()

        nueva = Campania(
            nombre=nombre, tipo_campania_id=origen.tipo_campania_id,
            estado_id=estado_inicial.id if estado_inicial else origen.estado_id,
            lema=origen.lema, descripcion_corta=origen.descripcion_corta,
            descripcion_larga=origen.descripcion_larga, url_externa=origen.url_externa,
            foto_url=origen.foto_url, objetivo_principal=origen.objetivo_principal,
            responsable_id=origen.responsable_id, agrupacion_id=origen.agrupacion_id,
            es_recurrente=origen.es_recurrente, periodicidad=origen.periodicidad,
            padre_id=padre_id,
            fecha_inicio_plan=(origen.fecha_inicio_plan + timedelta(days=offset_dias) if origen.fecha_inicio_plan else None),
            fecha_fin_plan=(origen.fecha_fin_plan + timedelta(days=offset_dias) if origen.fecha_fin_plan else None),
        )
        self.session.add(nueva)
        await self.session.flush()

        if incluir_metas:
            for m in origen.metas:
                self.session.add(MetaCampania(campania_id=nueva.id, tipo_meta_id=m.tipo_meta_id,
                                               unidad=m.unidad, valor_planificado=m.valor_planificado))
        if incluir_canales:
            for c in origen.canales:
                self.session.add(CanalDifusionCampania(campania_id=nueva.id, canal_id=c.canal_id, notas=c.notas))
        if incluir_partidas:
            for p in origen.partidas_presupuesto:
                self.session.add(PartidaPresupuestoCampania(campania_id=nueva.id, concepto=p.concepto,
                    importe_estimado=p.importe_estimado, tipo_partida=p.tipo_partida, orden=p.orden))
        if incluir_actividades:
            default_ea = (await self.session.execute(select(EstadoAccion).order_by(EstadoAccion.orden.asc().nulls_last()).limit(1))).scalar_one_or_none()
            default_et = (await self.session.execute(select(EstadoTarea).order_by(EstadoTarea.orden.asc().nulls_last()).limit(1))).scalar_one_or_none()
            for act in (await self.session.execute(select(Actividad).where(Actividad.campania_id == origen.id))).scalars().all():
                nueva_act = Actividad(
                    nombre=act.nombre, descripcion=act.descripcion, tipo_actividad_id=act.tipo_actividad_id,
                    estado_id=default_ea.id if default_ea else act.estado_id, campania_id=nueva.id,
                    grupo_id=act.grupo_id, responsable_id=act.responsable_id,
                    lugar=act.lugar, aforo=act.aforo, es_online=act.es_online, url_online=act.url_online,
                    presupuesto_estimado=act.presupuesto_estimado,
                    fecha_inicio=(act.fecha_inicio + timedelta(days=offset_dias) if act.fecha_inicio else None),
                    fecha_fin=(act.fecha_fin + timedelta(days=offset_dias) if act.fecha_fin else None),
                )
                self.session.add(nueva_act)
                await self.session.flush()
                for t in (await self.session.execute(select(Tarea).where(Tarea.actividad_id == act.id))).scalars().all():
                    self.session.add(Tarea(titulo=t.titulo, descripcion=t.descripcion,
                        horas_estimadas=t.horas_estimadas, orden=t.orden, actividad_id=nueva_act.id,
                        estado_id=default_et.id if default_et else t.estado_id))
        if incluir_subcampanias:
            for hija in (await self.session.execute(select(Campania).where(Campania.padre_id == origen.id))).scalars().all():
                await self.clonar(hija.id, f"{nombre} — {hija.nombre}",
                    offset_dias=offset_dias, incluir_metas=incluir_metas,
                    incluir_partidas=incluir_partidas, incluir_canales=incluir_canales,
                    incluir_actividades=incluir_actividades, incluir_subcampanias=True, padre_id=nueva.id)

        await self.session.commit()
        await self.session.refresh(nueva)
        return nueva

    CAMPOS_PROPAGABLES = frozenset({
        "tipo_campania_id", "responsable_id", "agrupacion_id",
        "objetivo_principal", "periodicidad", "es_recurrente",
    })

    async def propagar_a_subcampanias(self, campania_id, campos: list):
        from sqlalchemy import select
        campos_validos = [c for c in campos if c in self.CAMPOS_PROPAGABLES]
        if not campos_validos:
            return []
        padre = (await self.session.execute(select(Campania).where(Campania.id == campania_id))).scalar_one()
        valores = {c: getattr(padre, c) for c in campos_validos}
        procesadas = []
        cola = [campania_id]
        while cola:
            pid = cola.pop(0)
            for h in (await self.session.execute(select(Campania).where(Campania.padre_id == pid))).scalars().all():
                for campo, valor in valores.items():
                    setattr(h, campo, valor)
                procesadas.append(h.id)
                cola.append(h.id)
        await self.session.commit()
        if not procesadas:
            return []
        return list((await self.session.execute(select(Campania).where(Campania.id.in_(procesadas)))).scalars().all())
