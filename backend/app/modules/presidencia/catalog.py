"""Catálogo de funcionalidades y transacciones del módulo Presidencia.

Presidencia es el cuadro de mando de gobierno: un panel agregado que reúne, para
el órgano que preside una unidad, la información de gobierno que vive en otros
módulos (acuerdos y actas de secretaría, mandatos vigentes de membresía). Sus
transacciones llevan prefijo de módulo `PRESIDENCIA_` (como el resto del sistema)
y son asignables a cualquier rol; por defecto el seed las da a PRESIDENTE y
VICEPRESIDENTE.
"""

from ..acceso.services.registry import (
    ModuleCatalog,
    FuncionalidadDef,
    FuncionalidadTransaccionDef,
    TransaccionDef,
    AmbitoTransaccion,
)

MODULO = "presidencia"

_TRANSACCIONES = [
    TransaccionDef("PRESIDENCIA_CUADRO_MANDO_VER",        "Ver el cuadro de mando de gobierno",   "CONSULTA"),
    TransaccionDef("PRESIDENCIA_MANDATO_LISTAR",          "Listar mandatos vigentes",             "CONSULTA"),
    TransaccionDef("PRESIDENCIA_ACUERDO_SEGUIMIENTO_VER", "Ver el seguimiento de acuerdos",       "CONSULTA"),
]

for _t in _TRANSACCIONES:
    ModuleCatalog.register_transaccion(MODULO, _t)

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="CUADRO_MANDO_GOBIERNO",
    nombre="Cuadro de mando de gobierno",
    modulo=MODULO,
    descripcion="Panel agregado de presidencia: cuadro de mando, mandatos vigentes y seguimiento de acuerdos",
    transacciones=[
        FuncionalidadTransaccionDef("PRESIDENCIA_CUADRO_MANDO_VER",        AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("PRESIDENCIA_MANDATO_LISTAR",          AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("PRESIDENCIA_ACUERDO_SEGUIMIENTO_VER", AmbitoTransaccion.TERRITORIAL),
    ],
))
