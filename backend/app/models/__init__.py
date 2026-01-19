"""
Imports de modelos para Alembic.
NOTA: Este archivo está siendo migrado a la arquitectura DDD.
Los imports legacy se mantienen temporalmente para compatibilidad.
"""

# Infraestructura
from ..infrastructure.base_model import Base

# Usuario
from ..domains.usuarios.models import Usuario, UsuarioRol

# Dominio Core
from ..domains.core.models import (
    Configuracion, ReglaValidacionConfig, HistorialConfiguracion,
    EstadoCuota, EstadoCampania, EstadoTarea, EstadoParticipante,
    EstadoOrdenCobro, EstadoRemesa, EstadoDonacion, HistorialEstado,
    Sesion, HistorialSeguridad, IPBloqueada, IntentoAcceso
)

# Dominio Geográfico
from ..domains.geografico.models import Pais, Provincia, Municipio, Direccion

# Dominio Notificaciones
from ..domains.notificaciones.models import TipoNotificacion, Notificacion, PreferenciaNotificacion

# Dominio Financiero (nuevos modelos)
from ..domains.financiero.models import (
    ImporteCuotaAnio, CuotaAnual, ModoIngreso,
    DonacionConcepto, Donacion,
    Remesa, OrdenCobro,
    EstadoPlanificacion, CategoriaPartida, PartidaPresupuestaria, PlanificacionAnual
)

# TODO: Migrar estos imports cuando se actualicen los dominios correspondientes
# from ..domains.core.models.tipologias import TipoMiembro, Rol, Transaccion, RolTransaccion
# from ..domains.miembros.models.agrupacion import AgrupacionTerritorial
# from ..domains.miembros.models.miembro import Miembro
# from ..domains.campanas.models.campania import (...)
# from ..domains.grupos.models.grupo_trabajo import (...)
# from ..domains.voluntariado.models.voluntariado import (...)
# from ..domains.actividades.models.actividad import (...)

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
