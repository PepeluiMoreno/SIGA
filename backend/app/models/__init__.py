"""
Imports de modelos para Alembic.
NOTA: Este archivo está siendo migrado a la arquitectura DDD.
Los imports legacy se mantienen temporalmente para compatibilidad.
"""

# Infraestructura
from ..infrastructure.base_model import Base

# Usuario
from ..modules.usuarios.models import Usuario, UsuarioRol

# Dominio Core
from ..modules.core.models import (
    Configuracion, ReglaValidacionConfig, HistorialConfiguracion,
    EstadoCuota, EstadoCampania, EstadoTarea, EstadoParticipante,
    EstadoOrdenCobro, EstadoRemesa, EstadoDonacion, HistorialEstado,
    Sesion, HistorialSeguridad, IPBloqueada, IntentoAcceso
)

# Dominio Geográfico
from ..modules.geografico.models import Pais, Provincia, Municipio, Direccion

# Dominio Notificaciones
from ..modules.notificaciones.models import TipoNotificacion, Notificacion, PreferenciaNotificacion

# Dominio Financiero (nuevos modelos)
from ..modules.financiero.models import (
    ImporteCuotaAnio, CuotaAnual, ModoIngreso,
    DonacionConcepto, Donacion,
    Remesa, OrdenCobro,
    EstadoPlanificacion, CategoriaPartida, PartidaPresupuestaria, PlanificacionAnual
)

# Dominio Administración
from ..modules.administracion.models import Transaccion, Rol, RolTransaccion, LogAuditoria

# Dominio Eventos
from ..modules.eventos.models import (
    TipoEvento, EstadoEvento, Evento, ParticipanteEvento, MaterialEvento,
    GrupoEvento, TareaEvento, GastoEvento,
)

# Dominio Miembros
from ..modules.miembros.models import (
    TipoMiembro, EstadoMiembro, MotivoBaja, TipoCargo, Miembro,
    Skill, MiembroSkill, FranjaDisponibilidad, HistorialAgrupacion, SolicitudTraslado,
)

__all__ = [
    'Base',
    'Usuario',
    'UsuarioRol',
    'Configuracion',
    'EstadoCuota',
    'Pais',
    'Provincia',
    'Municipio',
    'Direccion',
    'TipoNotificacion',
    'Notificacion',
    'ImporteCuotaAnio',
    'CuotaAnual',
    'Donacion',
    'Remesa',
    'OrdenCobro',
    'EstadoPlanificacion',
    'CategoriaPartida',
    'PartidaPresupuestaria',
    'PlanificacionAnual',
]
