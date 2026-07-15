"""Catálogo de funcionalidades y transacciones del módulo Actividades."""

from ..acceso.services.registry import (
    ModuleCatalog,
    FuncionalidadDef,
    FuncionalidadTransaccionDef,
    TransaccionDef,
    AmbitoTransaccion,
)

MODULO = "actividades"

_TRANSACCIONES = [
    # Campañas
    TransaccionDef("CAMPANA_LISTAR",             "Listar campañas",                      "CONSULTA"),
    TransaccionDef("CAMPANA_CREAR",              "Crear campaña",                        "MUTACION"),
    TransaccionDef("CAMPANA_EDITAR",             "Editar campaña",                       "MUTACION"),
    TransaccionDef("CAMPANA_PUBLICAR",           "Publicar campaña",                     "MUTACION"),
    TransaccionDef("CAMPANA_CERRAR",             "Cerrar campaña",                       "MUTACION"),
    TransaccionDef("CAMPANA_ELIMINAR",           "Eliminar campaña",                     "MUTACION"),
    TransaccionDef("CAMPANA_APROBAR_PRESUPUESTO",   "Aprobar presupuesto de campaña",    "APROBACION"),
    TransaccionDef("CAMPANA_APROBAR",            "Aprobar campaña",                      "APROBACION"),
    # Grupos de trabajo
    TransaccionDef("GRUPO_LISTAR",              "Listar grupos de trabajo",             "CONSULTA"),
    TransaccionDef("GRUPO_CREAR",               "Crear grupo de trabajo",               "MUTACION"),
    TransaccionDef("GRUPO_EDITAR",              "Editar grupo de trabajo",              "MUTACION"),
    TransaccionDef("GRUPO_ASIGNAR_MIEMBRO",     "Asignar miembro a grupo",              "MUTACION"),
    TransaccionDef("GRUPO_CONVOCAR_REUNION",    "Convocar reunión de grupo",            "MUTACION"),
    # Eventos
    TransaccionDef("EVENTO_LISTAR",             "Listar eventos",                       "CONSULTA"),
    TransaccionDef("EVENTO_CREAR",              "Crear evento",                         "MUTACION"),
    TransaccionDef("EVENTO_EDITAR",             "Editar evento",                        "MUTACION"),
    TransaccionDef("EVENTO_PUBLICAR",           "Publicar evento",                      "MUTACION"),
    TransaccionDef("EVENTO_INSCRIBIR",          "Inscribir participante en evento",     "MUTACION"),
    # Actividades generales
    TransaccionDef("ACTIVIDAD_LISTAR",          "Listar actividades",                   "CONSULTA"),
    TransaccionDef("ACTIVIDAD_CREAR",           "Crear actividad",                      "MUTACION"),
    TransaccionDef("ACTIVIDAD_EDITAR",          "Editar actividad",                     "MUTACION"),
    TransaccionDef("ACTIVIDAD_PROPONER",        "Proponer actividad",                   "MUTACION"),
    TransaccionDef("ACTIVIDAD_APROBAR",         "Aprobar propuesta de actividad",       "APROBACION"),
    TransaccionDef("ACTIVIDAD_RECHAZAR",        "Rechazar propuesta de actividad",      "APROBACION"),
    TransaccionDef("ACTIVIDAD_PARTICIPANTE_GESTIONAR", "Gestionar participantes",       "MUTACION"),
    TransaccionDef("ACTIVIDAD_CATALOGO_GESTIONAR",     "Gestionar catálogos de actividad", "MUTACION"),
]

for _t in _TRANSACCIONES:
    ModuleCatalog.register_transaccion(MODULO, _t)

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="DISENO_CAMPANA",
    nombre="Diseño de campaña",
    modulo=MODULO,
    descripcion="Creación y gestión de campañas, equipos y presupuesto",
    transacciones=[
        FuncionalidadTransaccionDef("CAMPANA_LISTAR",  AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("CAMPANA_CREAR",   AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("CAMPANA_EDITAR",  AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("CAMPANA_ELIMINAR", AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("CAMPANA_PUBLICAR", AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("GRUPO_LISTAR",             AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("GRUPO_CREAR",              AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("GRUPO_EDITAR",             AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("GRUPO_ASIGNAR_MIEMBRO",    AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("GRUPO_CONVOCAR_REUNION",   AmbitoTransaccion.TERRITORIAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="GESTION_ACTIVIDADES",
    nombre="Gestión de actividades",
    modulo=MODULO,
    descripcion="Creación, edición, participantes y catálogos de actividades",
    transacciones=[
        FuncionalidadTransaccionDef("ACTIVIDAD_LISTAR",                 AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ACTIVIDAD_CREAR",                  AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ACTIVIDAD_EDITAR",                 AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ACTIVIDAD_PROPONER",              AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ACTIVIDAD_PARTICIPANTE_GESTIONAR", AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ACTIVIDAD_CATALOGO_GESTIONAR",     AmbitoTransaccion.GLOBAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="APROBACION_CAMPANAS",
    nombre="Aprobación de campañas",
    modulo=MODULO,
    descripcion="Aprobación de propuestas y presupuestos de campaña por la junta",
    transacciones=[
        FuncionalidadTransaccionDef("CAMPANA_APROBAR",              AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("CAMPANA_APROBAR_PRESUPUESTO",  AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("CAMPANA_CERRAR",               AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ACTIVIDAD_APROBAR",            AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ACTIVIDAD_RECHAZAR",           AmbitoTransaccion.TERRITORIAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="GESTION_EVENTOS",
    nombre="Gestión de eventos",
    modulo=MODULO,
    descripcion="Creación, publicación e inscripción a eventos",
    transacciones=[
        FuncionalidadTransaccionDef("EVENTO_LISTAR",   AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("EVENTO_CREAR",    AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("EVENTO_EDITAR",   AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("EVENTO_PUBLICAR", AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("EVENTO_INSCRIBIR", AmbitoTransaccion.TERRITORIAL),
    ],
))

# El presupuesto de campaña se aprueba por ACUERDO de un órgano (patrón secretaría:
# AcuerdoPresupuestoCampania + AcuerdoEjecucionService.ejecutar_aprobacion_presupuesto),
# no por un FlujoAprobacion declarativo. Aquel FLUJO_PRESUPUESTO_CAMPANA nunca tuvo motor
# y apuntaba a una entidad inexistente; se retiró junto con las transacciones
# PROPONER/RECHAZAR_PRESUPUESTO (huérfanas). La reserva la protege CAMPANA_APROBAR_PRESUPUESTO.
# Ver docs/arquitectura/DESCENTRALIZACION.md y el plan de maduración de campañas.
