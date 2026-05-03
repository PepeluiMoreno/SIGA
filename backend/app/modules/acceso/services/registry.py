"""Registro de catálogos de funcionalidades y transacciones por módulo.

Cada módulo declara su catalog.py llamando a register_funcionalidad() y
register_transaccion(). Al arrancar la aplicación, CatalogSyncService hace
upsert de estos registros en la base de datos, de forma que la UI siempre
refleja el estado actual del código.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..models.funcionalidad import AmbitoTransaccion


@dataclass(frozen=True)
class TransaccionDef:
    """Declaración de una transacción en el catálogo de un módulo."""
    codigo: str
    nombre: str
    tipo: str                        # CONSULTA | MUTACION | APROBACION
    descripcion: Optional[str] = None
    sistema: bool = True


@dataclass(frozen=True)
class FuncionalidadTransaccionDef:
    """Vínculo entre funcionalidad y transacción con ámbito."""
    transaccion_codigo: str
    ambito: AmbitoTransaccion = AmbitoTransaccion.TERRITORIAL


@dataclass(frozen=True)
class FlujoAprobacionDef:
    """Declaración de un flujo de aprobación en el catálogo."""
    codigo: str
    nombre: str
    transaccion_inicio_codigo: str
    transaccion_aprobacion_codigo: str
    rol_aprobador_codigo: str
    entidad: str
    transaccion_rechazo_codigo: Optional[str] = None
    descripcion: Optional[str] = None
    sistema: bool = True


@dataclass
class FuncionalidadDef:
    """Declaración de una funcionalidad en el catálogo de un módulo."""
    codigo: str
    nombre: str
    modulo: str
    transacciones: List[FuncionalidadTransaccionDef] = field(default_factory=list)
    descripcion: Optional[str] = None
    sistema: bool = False


class ModuleCatalog:
    """Registro global de funcionalidades y transacciones declaradas por módulos."""

    _funcionalidades: Dict[str, FuncionalidadDef] = {}
    _transacciones: Dict[str, TransaccionDef] = {}
    _flujos: Dict[str, FlujoAprobacionDef] = {}

    @classmethod
    def register_funcionalidad(cls, funcionalidad: FuncionalidadDef) -> None:
        if funcionalidad.codigo in cls._funcionalidades:
            raise ValueError(f"Funcionalidad '{funcionalidad.codigo}' ya registrada")
        cls._funcionalidades[funcionalidad.codigo] = funcionalidad

    @classmethod
    def register_transaccion(cls, modulo: str, transaccion: TransaccionDef) -> None:
        codigo = transaccion.codigo
        if codigo in cls._transacciones:
            raise ValueError(f"Transaccion '{codigo}' ya registrada")
        cls._transacciones[codigo] = transaccion

    @classmethod
    def register_flujo(cls, flujo: FlujoAprobacionDef) -> None:
        if flujo.codigo in cls._flujos:
            raise ValueError(f"FlujoAprobacion '{flujo.codigo}' ya registrado")
        cls._flujos[flujo.codigo] = flujo

    @classmethod
    def get_funcionalidades(cls) -> List[FuncionalidadDef]:
        return list(cls._funcionalidades.values())

    @classmethod
    def get_transacciones(cls) -> List[TransaccionDef]:
        return list(cls._transacciones.values())

    @classmethod
    def get_flujos(cls) -> List[FlujoAprobacionDef]:
        return list(cls._flujos.values())

    @classmethod
    def get_transacciones_by_modulo(cls, modulo: str) -> List[TransaccionDef]:
        prefix = f"{modulo.upper()}_"
        return [t for t in cls._transacciones.values() if t.codigo.startswith(prefix)]
