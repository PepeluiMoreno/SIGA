"""Catálogo de funcionalidades y transacciones del módulo Actividades."""

from ..acceso.services.registry import (
    ModuleCatalog,
    FuncionalidadDef,
    FuncionalidadTransaccionDef,
    TransaccionDef,
    FlujoAprobacionDef,
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
    TransaccionDef("CAMPANA_PROPONER_PRESUPUESTO",  "Proponer presupuesto de campaña",   "MUTACION"),
    TransaccionDef("CAMPANA_APROBAR_PRESUPUESTO",   "Aprobar presupuesto de campaña",    "APROBACION"),
    TransaccionDef("CAMPANA_RECHAZAR_PRESUPUESTO",  "Rechazar presupuesto de campaña",   "APROBACION"),
    # Grupos de trabajo
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
    TransaccionDef("ACTIVIDAD_PROPONER",        "Proponer actividad",                   "MUTACION"),
    TransaccionDef("ACTIVIDAD_APROBAR",         "Aprobar propuesta de actividad",       "APROBACION"),
    TransaccionDef("ACTIVIDAD_RECHAZAR",        "Rechazar propuesta de actividad",      "APROBACION"),
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
        FuncionalidadTransaccionDef("CAMPANA_EDITAR",  AmbitoTransaccion.PROPIO),
        FuncionalidadTransaccionDef("CAMPANA_PUBLICAR", AmbitoTransaccion.PROPIO),
        FuncionalidadTransaccionDef("CAMPANA_PROPONER_PRESUPUESTO", AmbitoTransaccion.PROPIO),
        FuncionalidadTransaccionDef("GRUPO_CREAR",              AmbitoTransaccion.PROPIO),
        FuncionalidadTransaccionDef("GRUPO_ASIGNAR_MIEMBRO",    AmbitoTransaccion.PROPIO),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="APROBACION_CAMPANAS",
    nombre="Aprobación de campañas",
    modulo=MODULO,
    descripcion="Aprobación de propuestas y presupuestos de campaña por la junta",
    transacciones=[
        FuncionalidadTransaccionDef("CAMPANA_APROBAR_PRESUPUESTO",  AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("CAMPANA_RECHAZAR_PRESUPUESTO", AmbitoTransaccion.TERRITORIAL),
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
        FuncionalidadTransaccionDef("EVENTO_EDITAR",   AmbitoTransaccion.PROPIO),
        FuncionalidadTransaccionDef("EVENTO_PUBLICAR", AmbitoTransaccion.PROPIO),
        FuncionalidadTransaccionDef("EVENTO_INSCRIBIR", AmbitoTransaccion.TERRITORIAL),
    ],
))

# Flujo de aprobación de presupuesto de campaña
ModuleCatalog.register_flujo(FlujoAprobacionDef(
    codigo="FLUJO_PRESUPUESTO_CAMPANA",
    nombre="Aprobación de presupuesto de campaña",
    descripcion=(
        "El diseñador propone un presupuesto; la junta directiva lo aprueba o rechaza"
    ),
    transaccion_inicio_codigo="CAMPANA_PROPONER_PRESUPUESTO",
    transaccion_aprobacion_codigo="CAMPANA_APROBAR_PRESUPUESTO",
    transaccion_rechazo_codigo="CAMPANA_RECHAZAR_PRESUPUESTO",
    rol_aprobador_codigo="JUNTA_DIRECTIVA",
    entidad="PropuestaPresupuestoCampana",
))
