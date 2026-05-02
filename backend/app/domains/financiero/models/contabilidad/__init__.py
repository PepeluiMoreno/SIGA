"""Subdominio contabilidad: partida doble y plan de cuentas PGC. Solo versión COMPLETA."""

from .plan_cuentas import CuentaContable
from .asiento import Asiento, LineaAsiento

__all__ = ['CuentaContable', 'Asiento', 'LineaAsiento']
