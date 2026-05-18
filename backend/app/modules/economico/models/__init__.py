"""Modelos del módulo económico.

IMPORTANTE: tesoreria/ y contabilidad/ son paquetes (directorios con __init__.py).
Python los prefiere sobre los archivos .py del mismo nombre. Los archivos planos
tesoreria.py y contabilidad.py son legacy y ya no se importan aquí.
"""

from .cuotas import ImporteCuotaAnio, CuotaAnual, ModoIngreso
from .donaciones import DonacionConcepto, Donacion
from .remesas import Remesa, OrdenCobro
from .presupuesto import EstadoPlanificacion, CategoriaPartida, PartidaPresupuestaria, CompromisoPresupuestario, PlanificacionAnual
from .cobro import ProveedorPago, EstadoPago, TipoEventoPago, TipoPago, Pago, EventoPago, EstadoSuscripcion, Suscripcion, FormaPago
from .reclamaciones import EstadoReclamacion, Reclamacion, TipoAccionReclamacion, AccionReclamacion

# Tesorería — importa del PAQUETE tesoreria/ (no del archivo tesoreria.py)
from .tesoreria import (
    CuentaBancaria,
    ApunteCaja,
    TipoApunte,
    OrigenApunte,
    MovimientoTesoreria,        # alias de ApunteCaja
    TipoMovimientoTesoreria,    # alias de TipoApunte
    ExtractoBancario,
    Conciliacion,
    MetodoConciliacion,
    ConciliacionBancaria,
)

# Contabilidad — importa del PAQUETE contabilidad/ (no del archivo contabilidad.py)
from .contabilidad import (
    ReglaContable,
    CuentaContable,
    TipoCuentaContable,
    AsientoContable,
    ApunteContable,
    TipoAsientoContable,
    EstadoAsientoContable,
    BalanceContable,
)

__all__ = [
    # Cuotas
    'ImporteCuotaAnio', 'CuotaAnual', 'ModoIngreso',
    # Donaciones
    'DonacionConcepto', 'Donacion',
    # Remesas
    'Remesa', 'OrdenCobro',
    # Presupuesto
    'EstadoPlanificacion', 'CategoriaPartida', 'PartidaPresupuestaria', 'CompromisoPresupuestario', 'PlanificacionAnual',
    # Cobro
    'ProveedorPago', 'EstadoPago', 'TipoEventoPago', 'TipoPago', 'Pago', 'EventoPago', 'EstadoSuscripcion', 'Suscripcion', 'FormaPago',
    # Reclamaciones
    'EstadoReclamacion', 'Reclamacion', 'TipoAccionReclamacion', 'AccionReclamacion',
    # Tesorería
    'CuentaBancaria',
    'ApunteCaja', 'TipoApunte', 'OrigenApunte',
    'MovimientoTesoreria', 'TipoMovimientoTesoreria',
    'ExtractoBancario', 'Conciliacion', 'MetodoConciliacion',
    'ConciliacionBancaria',
    # Contabilidad
    'ReglaContable',
    'CuentaContable', 'TipoCuentaContable',
    'AsientoContable', 'ApunteContable',
    'TipoAsientoContable', 'EstadoAsientoContable',
    'BalanceContable',
]
