"""Modelos del dominio financiero.

Importar desde los subdominios directamente.
Este __init__ mantiene compatibilidad con imports existentes durante la transición.
"""

# Cuotas
from .cuotas import ImporteCuotaAnio, CuotaAnual

# Donaciones
from .donaciones import DonacionConcepto, Donacion

# Remesas
from .remesas import Remesa, OrdenCobro

# Cobro
from .cobro import ProveedorPago, TipoPago, Pago, EventoPago, Suscripcion

# Tesoreria
from .tesoreria import CuentaBancaria, ApunteCaja, ExtractoBancario, Conciliacion

# Reclamaciones
from .reclamaciones import Reclamacion, AccionReclamacion

# Contabilidad (solo versión COMPLETA — importar condicionalmente en runtime)
# from .contabilidad import CuentaContable, Asiento, LineaAsiento

__all__ = [
    # cuotas
    'ImporteCuotaAnio', 'CuotaAnual',
    # donaciones
    'DonacionConcepto', 'Donacion',
    # remesas
    'Remesa', 'OrdenCobro',
    # cobro
    'ProveedorPago', 'TipoPago', 'Pago', 'EventoPago', 'Suscripcion',
    # tesoreria
    'CuentaBancaria', 'ApunteCaja', 'ExtractoBancario', 'Conciliacion',
    # reclamaciones
    'Reclamacion', 'AccionReclamacion',
]
