"""Catálogo de funcionalidades y transacciones del módulo Configuración."""

from ..acceso.services.registry import (
    ModuleCatalog,
    FuncionalidadDef,
    FuncionalidadTransaccionDef,
    TransaccionDef,
    AmbitoTransaccion,
)

MODULO = "configuracion"

_TRANSACCIONES = [
    TransaccionDef("CFG_CONFIGURACION_LEER",       "Leer configuración del sistema",       "CONSULTA"),
    TransaccionDef("CFG_CONFIGURACION_EDITAR",     "Editar configuración del sistema",     "MUTACION"),
    TransaccionDef("CFG_ESTADO_GESTIONAR",         "Gestionar estados del sistema",        "MUTACION"),
    TransaccionDef("CFG_ORGANIZACION_GESTIONAR",   "Gestionar organizaciones colaboradoras","MUTACION"),
    TransaccionDef("CFG_CONVENIO_CREAR",           "Crear convenio de colaboración",       "MUTACION"),
    TransaccionDef("CFG_CONVENIO_APROBAR",         "Aprobar convenio de colaboración",     "APROBACION"),
    TransaccionDef("CFG_TERRITORIO_CREAR",         "Crear agrupación territorial",         "MUTACION"),
    TransaccionDef("CFG_TERRITORIO_EDITAR",        "Editar agrupación territorial",        "MUTACION"),
    TransaccionDef("CFG_TERRITORIO_ELIMINAR",      "Eliminar agrupación territorial",      "MUTACION"),
    TransaccionDef("CFG_FLAG_MULTITERRITORIAL",    "Activar/desactivar modo multiterritorial", "MUTACION"),
]

for _t in _TRANSACCIONES:
    ModuleCatalog.register_transaccion(MODULO, _t)

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="CONFIGURACION_SISTEMA",
    nombre="Configuración del sistema",
    modulo=MODULO,
    descripcion="Parámetros globales, estados y feature flags",
    sistema=True,
    transacciones=[
        FuncionalidadTransaccionDef("CFG_CONFIGURACION_LEER",      AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("CFG_CONFIGURACION_EDITAR",    AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("CFG_ESTADO_GESTIONAR",        AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("CFG_FLAG_MULTITERRITORIAL",   AmbitoTransaccion.GLOBAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="GESTION_TERRITORIOS",
    nombre="Gestión territorial",
    modulo=MODULO,
    descripcion="Creación y edición de agrupaciones territoriales",
    sistema=True,
    transacciones=[
        FuncionalidadTransaccionDef("CFG_TERRITORIO_CREAR",   AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("CFG_TERRITORIO_EDITAR",  AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("CFG_TERRITORIO_ELIMINAR", AmbitoTransaccion.GLOBAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="GESTION_COLABORACIONES",
    nombre="Gestión de colaboraciones",
    modulo=MODULO,
    descripcion="Organizaciones colaboradoras y convenios",
    transacciones=[
        FuncionalidadTransaccionDef("CFG_ORGANIZACION_GESTIONAR", AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("CFG_CONVENIO_CREAR",         AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("CFG_CONVENIO_APROBAR",       AmbitoTransaccion.GLOBAL),
    ],
))
