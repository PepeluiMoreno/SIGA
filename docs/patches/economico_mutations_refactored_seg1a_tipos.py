"""Mutations GraphQL financieras con lógica de negocio compleja.

Complementan las mutations CRUD automáticas de strawchemy con operaciones
que requieren lógica de servicio. Cada método es un thin wrapper que:
  1. Extrae parámetros del input GraphQL
  2. Llama al servicio correspondiente
  3. Devuelve el resultado

Ninguna lógica de dominio aquí — todo está en los servicios del módulo económico.
"""
import strawberry
from datetime import date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from ..modules.economico.services.tesoreria_service import TesoreriaService
from ..modules.economico.services.contabilidad_service import ContabilidadService
from ..modules.economico.services.registro_contable import RegistroContable
from ..modules.economico.services.remesa_service import RemesaService
from ..modules.economico.services.recibo_service import ReciboService
from ..modules.economico.services.justificante_gasto_service import JustificanteGastoService
from ..modules.economico.services.donacion_service import DonacionService
from ..modules.economico.services.cuota_service import CuotaService
from ..modules.economico.models.tesoreria import TipoApunte, OrigenApunte, MetodoConciliacion
from .permissions import RequireTransaction


@strawberry.input
class FallidoBancoInput:
    orden_id: UUID
    codigo: str
    motivo: Optional[str] = None
    fecha: Optional[date] = None

@strawberry.input
class LineaJustificanteInput:
    concepto: str
    importe: float
    fecha_gasto: date
    observaciones: Optional[str] = None

@strawberry.type
class PreviewOrdenCobradaType:
    orden_id: UUID
    end_to_end_id: str
    importe: float
    miembro_nombre: str

@strawberry.type
class PreviewOrdenFallidaType:
    orden_id: UUID
    end_to_end_id: str
    codigo: str
    motivo: str
    fecha: Optional[str] = None
    importe: float

@strawberry.type
class PreviewSinEmparejarType:
    end_to_end_id: str
    motivo: str

@strawberry.type
class PreviewTotalesType:
    n_cobradas: int
    n_fallidas: int
    importe_cobrado: float

@strawberry.type
class PreviewLiquidacionType:
    remesa_referencia: str
    cobradas: list[PreviewOrdenCobradaType]
    fallidas: list[PreviewOrdenFallidaType]
    no_emparejadas: list[PreviewSinEmparejarType]
    totales: PreviewTotalesType

@strawberry.type
class ResultadoLiquidacionType:
    n_cobradas: int
    n_fallidas: int
    importe_cobrado: float
    apunte_id: Optional[UUID] = None
    asiento_id: Optional[UUID] = None
    remesa_estado: Optional[str] = None

@strawberry.type
class DesgloseTipoMiembroType:
    tipo_miembro_id: UUID
    tipo_miembro_nombre: str
    motivo_codigo: Optional[str] = None
    motivo_porcentaje: float = 0.0
    n_miembros: int = 0
    importe_unitario: float = 0.0
    total: float = 0.0
    excluido: bool = False

@strawberry.type
class PreviewGeneracionCuotasType:
    ejercicio: int
    importe_base: float
    desglose: list[DesgloseTipoMiembroType]
    n_generables: int
    n_excluidos: int
    n_existentes: int
    total_esperado: float

@strawberry.type
class ResultadoGeneracionCuotasType:
    ejercicio: int
    n_creadas: int
    n_omitidas_existentes: int
    n_omitidas_excluidas: int
    total_importe: float

@strawberry.type
class CuotaPreviewType:
    cuota_id: UUID
    miembro_id: UUID
    miembro_nombre: str
    importe_pendiente: float
    motivo_exclusion: str

@strawberry.type
class OrdinariaExistenteType:
    id: UUID
    referencia: str

@strawberry.type
class PreviewRemesaType:
    ejercicio: int
    n_incluidas: int
    n_excluidas: int
    importe_total: float
    incluidas: list[CuotaPreviewType]
    excluidas: list[CuotaPreviewType]
    ordinaria_existente: Optional[OrdinariaExistenteType] = None

@strawberry.type
class CertificableDonacionType:
    nif: str
    nombre: str
    tipo: str
    total: float
    n_donaciones: int
    donacion_ids: list[str]
    todas_certificadas: bool

@strawberry.type
class CertificadoEmitidoType:
    numero: str
    pdf_base64: str
