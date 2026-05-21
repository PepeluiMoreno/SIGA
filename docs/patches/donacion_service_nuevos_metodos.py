
    async def _cfg_org(self) -> tuple:
        """Lee nombre y NIF de la organización desde la tabla de configuraciones."""
        from app.modules.configuracion.models.configuracion import Configuracion
        async def _get(clave: str, default: str = "") -> str:
            r = await self.session.execute(
                select(Configuracion).where(Configuracion.clave == clave)
            )
            row = r.scalars().first()
            return (row.valor if row and row.valor else default) or default
        nombre = (
            await _get("organizacion.nombre")
            or await _get("org.nombre")
            or "Asociación"
        )
        nif = (
            await _get("organizacion.nif")
            or await _get("org.nif")
            or "—"
        )
        return nombre, nif
