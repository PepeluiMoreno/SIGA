
    # ─── Validación de imputación (reutilizable) ─────────────────────────────────────

    async def validar_imputacion_actividad(
        self,
        actividad_id,
        campania_id=None,
    ):
        """Valida que la actividad sea imputable: no plantilla recurrente, campaña no cerrada.

        Devuelve el campania_id efectivo (puede derivarse de la actividad).
        Raises ValueError si hay restricción.
        """
        from app.modules.actividades.models.actividad import Actividad
        from app.modules.actividades.models.campana import Campania
        r = await self.session.execute(
            select(Actividad).where(Actividad.id == actividad_id)
        )
        actividad = r.scalars().first()
        if not actividad:
            raise ValueError(f"Actividad {actividad_id} no encontrada.")
        if actividad.caracter == "RECURRENTE" and actividad.padre_id is None:
            raise ValueError(
                "No se puede imputar a una plantilla recurrente. "
                "Elige una instancia concreta."
            )
        if actividad.campania_id:
            rc = await self.session.execute(
                select(Campania).where(Campania.id == actividad.campania_id)
            )
            camp = rc.scalars().first()
            if camp and camp.esta_cerrada:
                raise ValueError(
                    f"La campaña «{camp.nombre}» está cerrada y no admite nuevos gastos/ingresos."
                )
            campania_id = actividad.campania_id
        return campania_id
