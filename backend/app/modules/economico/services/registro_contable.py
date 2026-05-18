"""RegistroContable: genera asientos de partida doble desde apuntes de caja.

Las reglas (origen, tipo → debe, haber) se leen de la tabla reglas_contables
en lugar del diccionario hardcodeado. Si la BD no tiene reglas se usa el fallback.
"""
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.tesoreria import ApunteCaja, TipoApunte, OrigenApunte
from ..models.contabilidad import (
    AsientoContable, ApunteContable,
    TipoAsientoContable, EstadoAsientoContable,
)
from ..core.feature_flags import is_version_completa
from .contabilidad_service import ContabilidadService
from .reglas_contables_service import ReglasContablesService

# Fallback hardcodeado — solo se usa si la tabla de reglas está vacía
_MAPA_FALLBACK = {
    ("CUOTA",    "INGRESO"):      ("572", "721"),
    ("CUOTA",    "GASTO"):        ("721", "572"),
    ("DONACION", "INGRESO"):      ("572", "730"),
    ("REMESA",   "INGRESO"):      ("572", "430"),
    ("REMESA",   "GASTO"):        ("430", "572"),
    ("PAGO",     "INGRESO"):      ("572", "721"),
    (None,       "GASTO"):        ("629", "572"),
    (None,       "INGRESO"):      ("572", "749"),
}


class RegistroContable:
    """Genera automáticamente asientos contables a partir de apuntes de caja."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.contabilidad = ContabilidadService(session)
        self.reglas_service = ReglasContablesService(session)

    async def _resolver_cuentas(
        self, tipo_apunte: str, origen: Optional[str]
    ) -> Optional[tuple[str, str]]:
        """Busca las cuentas en BD; si no hay reglas usa el fallback."""
        cuentas = await self.reglas_service.resolver_cuentas(tipo_apunte, origen)
        if cuentas:
            return cuentas

        # Fallback: diccionario estático
        clave = (origen, tipo_apunte)
        if clave in _MAPA_FALLBACK:
            return _MAPA_FALLBACK[clave]
        clave_comodin = (None, tipo_apunte)
        return _MAPA_FALLBACK.get(clave_comodin)

    async def generar_asiento_para_apunte(
        self, apunte: ApunteCaja
    ) -> Optional[AsientoContable]:
        """Si org.contabilidad_compleja está activo, genera el asiento de partida doble."""
        if not await is_version_completa(self.session):
            return None

        origen_str = apunte.origen.value if apunte.origen else None
        tipo_str = apunte.tipo.value

        cuentas = await self._resolver_cuentas(tipo_str, origen_str)
        if not cuentas:
            return None

        codigo_debe, codigo_haber = cuentas

        cuenta_debe = await self.contabilidad.obtener_cuenta_por_codigo(codigo_debe)
        cuenta_haber = await self.contabilidad.obtener_cuenta_por_codigo(codigo_haber)

        if not cuenta_debe or not cuenta_haber:
            return None  # Plan de cuentas no inicializado aún

        ejercicio = apunte.fecha.year
        asiento = await self.contabilidad.crear_asiento(
            ejercicio=ejercicio,
            fecha=apunte.fecha,
            glosa=apunte.concepto,
            tipo_asiento=TipoAsientoContable.GESTION,
        )

        await self.contabilidad.añadir_apunte(
            asiento_id=asiento.id,
            cuenta_id=cuenta_debe.id,
            debe=apunte.importe,
            concepto=apunte.concepto,
        )
        await self.contabilidad.añadir_apunte(
            asiento_id=asiento.id,
            cuenta_id=cuenta_haber.id,
            haber=apunte.importe,
            concepto=apunte.concepto,
        )

        asiento = await self.contabilidad.confirmar_asiento(asiento.id)

        apunte.asiento_id = asiento.id
        self.session.add(apunte)
        await self.session.commit()

        return asiento
