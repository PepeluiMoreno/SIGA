from .actividad_service import ActividadService
from .campania_service_p1 import CampaniaService  # ensamblado: p1 + p2

__all__ = ["ActividadService", "CampaniaService"]

# NOTA: Para produccion, ensamblar campania_service.py completo:
#   cat campania_service_p1.py campania_service_p2.py > campania_service.py
# Y cambiar el import a: from .campania_service import CampaniaService
