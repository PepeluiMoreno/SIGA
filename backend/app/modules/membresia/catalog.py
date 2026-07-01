"""Catálogo de funcionalidades y transacciones del módulo Membresía."""

from ..acceso.services.registry import (
    ModuleCatalog,
    FuncionalidadDef,
    FuncionalidadTransaccionDef,
    TransaccionDef,
    AmbitoTransaccion,
)

MODULO = "membresia"
# Contactos (base CRM): el modelo Contacto vive en este módulo pero se agrupa
# como su propio módulo en el control de acceso, con prefijo CONTACTO_.
MODULO_CONTACTOS = "contactos"

_TRANSACCIONES = [
    TransaccionDef("MEMBRESIA_SOCIO_GESTIONAR",      "Gestionar socios",                  "MUTACION"),
    TransaccionDef("MEMBRESIA_MIEMBRO_LISTAR",       "Listar miembros",                   "CONSULTA"),
    TransaccionDef("MEMBRESIA_MIEMBRO_CREAR",        "Registrar miembro",                 "MUTACION"),
    TransaccionDef("MEMBRESIA_MIEMBRO_EDITAR",       "Editar datos de miembro",           "MUTACION"),
    TransaccionDef("MEMBRESIA_MIS_DATOS_EDITAR",     "Editar mis propios datos",          "MUTACION"),
    TransaccionDef("MEMBRESIA_MIEMBRO_VALIDAR",      "Validar solicitud de miembro",      "APROBACION"),
    TransaccionDef("MEMBRESIA_MIEMBRO_SUSPENDER",    "Suspender miembro",                 "MUTACION"),
    TransaccionDef("MEMBRESIA_MIEMBRO_BAJA",         "Dar de baja a miembro",             "MUTACION"),
    TransaccionDef("MEMBRESIA_MIEMBRO_EXPORTAR",     "Exportar datos de miembros",        "CONSULTA"),
    TransaccionDef("MEMBRESIA_MIEMBRO_VER_IBAN",     "Ver datos bancarios del miembro",   "CONSULTA"),
    TransaccionDef("MEMBRESIA_MIEMBRO_EDITAR_DATOS_ECONOMICOS", "Editar datos económicos del miembro", "MUTACION"),
    TransaccionDef("MEMBRESIA_AGRUPACION_EDITAR",    "Editar agrupación territorial",     "MUTACION"),
    TransaccionDef("MEMBRESIA_TRASLADO_SOLICITAR",   "Solicitar traslado de agrupación",  "MUTACION"),
    TransaccionDef("MEMBRESIA_TRASLADO_APROBAR",     "Aprobar traslado",                  "APROBACION"),
    TransaccionDef("MEMBRESIA_TRASLADO_RECHAZAR",    "Rechazar traslado",                 "APROBACION"),
    TransaccionDef("MEMBRESIA_VOLUNTARIO_GESTIONAR", "Gestionar perfil de voluntario",    "MUTACION"),
    TransaccionDef("MEMBRESIA_CARGO_ASIGNAR",        "Asignar cargo en junta",            "MUTACION"),
    TransaccionDef("MEMBRESIA_CARGO_REVOCAR",        "Revocar cargo en junta",            "MUTACION"),
    TransaccionDef("MEMBRESIA_JUNTA_CONFIGURAR",     "Configurar junta directiva",        "MUTACION"),
]

for _t in _TRANSACCIONES:
    ModuleCatalog.register_transaccion(MODULO, _t)

_TRANSACCIONES_CONTACTOS = [
    TransaccionDef("CONTACTO_LISTAR",   "Listar contactos",        "CONSULTA"),
    TransaccionDef("CONTACTO_VER",      "Ver ficha de contacto",   "CONSULTA"),
    TransaccionDef("CONTACTO_CREAR",    "Crear contacto",          "MUTACION"),
    TransaccionDef("CONTACTO_EDITAR",   "Editar contacto",         "MUTACION"),
    TransaccionDef("CONTACTO_ELIMINAR", "Dar de baja contacto",    "MUTACION"),
]
for _t in _TRANSACCIONES_CONTACTOS:
    ModuleCatalog.register_transaccion(MODULO_CONTACTOS, _t)

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="GESTION_CONTACTOS",
    nombre="Gestión de contactos",
    modulo=MODULO_CONTACTOS,
    descripcion="Alta, edición, consulta y baja de contactos (base CRM)",
    transacciones=[
        FuncionalidadTransaccionDef("CONTACTO_LISTAR",   AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("CONTACTO_VER",      AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("CONTACTO_CREAR",    AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("CONTACTO_EDITAR",   AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("CONTACTO_ELIMINAR", AmbitoTransaccion.TERRITORIAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="GESTION_MIEMBROS",
    nombre="Gestión de miembros",
    modulo=MODULO,
    descripcion="Registro, edición, validación y baja de miembros",
    transacciones=[
        FuncionalidadTransaccionDef("MEMBRESIA_SOCIO_GESTIONAR",   AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("MEMBRESIA_MIEMBRO_LISTAR",    AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("MEMBRESIA_MIEMBRO_CREAR",     AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("MEMBRESIA_MIEMBRO_EDITAR",    AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("MEMBRESIA_MIEMBRO_VALIDAR",   AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("MEMBRESIA_MIEMBRO_SUSPENDER", AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("MEMBRESIA_MIEMBRO_BAJA",      AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("MEMBRESIA_MIEMBRO_EXPORTAR",  AmbitoTransaccion.TERRITORIAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="AUTOSERVICIO_MIS_DATOS",
    nombre="Mis datos (autoservicio)",
    modulo=MODULO,
    descripcion=(
        "Edición por el propio socio de sus datos personales (nombre, contacto, "
        "dirección, foto…). Ámbito PROPIO: cada usuario solo opera sobre su perfil; "
        "no alcanza a otros socios ni a datos económicos/territoriales (esos los "
        "gestiona la organización)."
    ),
    transacciones=[
        FuncionalidadTransaccionDef("MEMBRESIA_MIS_DATOS_EDITAR", AmbitoTransaccion.PROPIO),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="DATOS_ECONOMICOS_MIEMBRO",
    nombre="Datos económicos del miembro",
    modulo=MODULO,
    descripcion="Consulta y edición de datos bancarios y económicos de los miembros (información sensible)",
    transacciones=[
        FuncionalidadTransaccionDef("MEMBRESIA_MIEMBRO_VER_IBAN",              AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("MEMBRESIA_MIEMBRO_EDITAR_DATOS_ECONOMICOS", AmbitoTransaccion.TERRITORIAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="GESTION_AGRUPACIONES",
    nombre="Gestión de agrupaciones territoriales",
    modulo=MODULO,
    descripcion="Edición de las agrupaciones territoriales de la organización",
    transacciones=[
        FuncionalidadTransaccionDef("MEMBRESIA_AGRUPACION_EDITAR", AmbitoTransaccion.TERRITORIAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="GESTION_TRASLADOS",
    nombre="Gestión de traslados",
    modulo=MODULO,
    descripcion="Solicitud y aprobación de traslados entre agrupaciones",
    transacciones=[
        FuncionalidadTransaccionDef("MEMBRESIA_TRASLADO_SOLICITAR", AmbitoTransaccion.PROPIO),
        FuncionalidadTransaccionDef("MEMBRESIA_TRASLADO_APROBAR",   AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("MEMBRESIA_TRASLADO_RECHAZAR",  AmbitoTransaccion.TERRITORIAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="GESTION_JUNTAS",
    nombre="Gestión de juntas directivas",
    modulo=MODULO,
    descripcion="Configuración, asignación y revocación de cargos en juntas",
    sistema=True,
    transacciones=[
        FuncionalidadTransaccionDef("MEMBRESIA_JUNTA_CONFIGURAR", AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("MEMBRESIA_CARGO_ASIGNAR",    AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("MEMBRESIA_CARGO_REVOCAR",    AmbitoTransaccion.TERRITORIAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="PERFIL_VOLUNTARIO",
    nombre="Perfil de voluntario del contacto",
    modulo=MODULO,
    descripcion=(
        "Editar la condición de voluntario de un contacto: disponibilidad, competencias "
        "y formación. Voluntariado no es un módulo aparte, sino una condición del socio "
        "(vinculación VOLUNTARIO); se gestiona desde su ficha."
    ),
    transacciones=[
        FuncionalidadTransaccionDef("MEMBRESIA_VOLUNTARIO_GESTIONAR", AmbitoTransaccion.TERRITORIAL),
    ],
))
