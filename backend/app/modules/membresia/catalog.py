"""Catálogo de funcionalidades y transacciones del módulo Membresía."""

from ..acceso.services.registry import (
    ModuleCatalog,
    FuncionalidadDef,
    FuncionalidadTransaccionDef,
    TransaccionDef,
    AmbitoTransaccion,
)

MODULO = "membresia"

_TRANSACCIONES = [
    TransaccionDef("MEMBRESIA_MIEMBRO_LISTAR",       "Listar miembros",                   "CONSULTA"),
    TransaccionDef("MEMBRESIA_MIEMBRO_CREAR",        "Registrar miembro",                 "MUTACION"),
    TransaccionDef("MEMBRESIA_MIEMBRO_EDITAR",       "Editar datos de miembro",           "MUTACION"),
    TransaccionDef("MEMBRESIA_MIEMBRO_VALIDAR",      "Validar solicitud de miembro",      "APROBACION"),
    TransaccionDef("MEMBRESIA_MIEMBRO_SUSPENDER",    "Suspender miembro",                 "MUTACION"),
    TransaccionDef("MEMBRESIA_MIEMBRO_BAJA",         "Dar de baja a miembro",             "MUTACION"),
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

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="GESTION_MIEMBROS",
    nombre="Gestión de miembros",
    modulo=MODULO,
    descripcion="Registro, edición, validación y baja de miembros",
    transacciones=[
        FuncionalidadTransaccionDef("MEMBRESIA_MIEMBRO_LISTAR",    AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("MEMBRESIA_MIEMBRO_CREAR",     AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("MEMBRESIA_MIEMBRO_EDITAR",    AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("MEMBRESIA_MIEMBRO_VALIDAR",   AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("MEMBRESIA_MIEMBRO_SUSPENDER", AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("MEMBRESIA_MIEMBRO_BAJA",      AmbitoTransaccion.TERRITORIAL),
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
    codigo="GESTION_VOLUNTARIADO",
    nombre="Gestión de voluntariado",
    modulo=MODULO,
    descripcion="Competencias, formación y disponibilidad de voluntarios",
    transacciones=[
        FuncionalidadTransaccionDef("MEMBRESIA_VOLUNTARIO_GESTIONAR", AmbitoTransaccion.TERRITORIAL),
    ],
))
