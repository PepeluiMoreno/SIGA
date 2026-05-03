"""Catálogo de funcionalidades y transacciones del módulo Acceso.

Este archivo se importa en el arranque de la aplicación.
ModuleCatalog.register_* hace que aparezcan en la UI del EditorRol dinámicamente.
"""

from .services.registry import (
    ModuleCatalog,
    FuncionalidadDef,
    FuncionalidadTransaccionDef,
    TransaccionDef,
    AmbitoTransaccion,
)

MODULO = "acceso"

# ------------------------------------------------------------------
# Transacciones
# ------------------------------------------------------------------

_TRANSACCIONES = [
    TransaccionDef("ACCESO_ROL_LISTAR",       "Listar roles",                    "CONSULTA"),
    TransaccionDef("ACCESO_ROL_CREAR",        "Crear rol",                       "MUTACION"),
    TransaccionDef("ACCESO_ROL_EDITAR",       "Editar rol",                      "MUTACION"),
    TransaccionDef("ACCESO_ROL_ELIMINAR",     "Eliminar rol",                    "MUTACION"),
    TransaccionDef("ACCESO_ROL_ASIGNAR",      "Asignar rol a usuario",           "MUTACION"),
    TransaccionDef("ACCESO_ROL_REVOCAR",      "Revocar rol de usuario",          "MUTACION"),
    TransaccionDef("ACCESO_FUNC_LISTAR",      "Listar funcionalidades",          "CONSULTA"),
    TransaccionDef("ACCESO_FUNC_ASIGNAR",     "Asignar funcionalidad a rol",     "MUTACION"),
    TransaccionDef("ACCESO_FUNC_REVOCAR",     "Revocar funcionalidad de rol",    "MUTACION"),
    TransaccionDef("ACCESO_USUARIO_LISTAR",   "Listar usuarios",                 "CONSULTA"),
    TransaccionDef("ACCESO_USUARIO_CREAR",    "Crear usuario",                   "MUTACION"),
    TransaccionDef("ACCESO_USUARIO_EDITAR",   "Editar usuario",                  "MUTACION"),
    TransaccionDef("ACCESO_USUARIO_SUSPENDER","Suspender usuario",               "MUTACION"),
    TransaccionDef("ACCESO_AUDITORIA_LEER",   "Leer log de auditoría",           "CONSULTA"),
]

for _t in _TRANSACCIONES:
    ModuleCatalog.register_transaccion(MODULO, _t)

# ------------------------------------------------------------------
# Funcionalidades
# ------------------------------------------------------------------

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="GESTION_ROLES",
    nombre="Gestión de roles y permisos",
    modulo=MODULO,
    descripcion="Crear, editar y asignar roles y funcionalidades del sistema",
    sistema=True,
    transacciones=[
        FuncionalidadTransaccionDef("ACCESO_ROL_LISTAR",   AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("ACCESO_ROL_CREAR",    AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("ACCESO_ROL_EDITAR",   AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("ACCESO_ROL_ELIMINAR", AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("ACCESO_ROL_ASIGNAR",  AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ACCESO_ROL_REVOCAR",  AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ACCESO_FUNC_LISTAR",  AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("ACCESO_FUNC_ASIGNAR", AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("ACCESO_FUNC_REVOCAR", AmbitoTransaccion.GLOBAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="GESTION_USUARIOS",
    nombre="Gestión de usuarios",
    modulo=MODULO,
    descripcion="Alta, edición y suspensión de usuarios del sistema",
    sistema=True,
    transacciones=[
        FuncionalidadTransaccionDef("ACCESO_USUARIO_LISTAR",    AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ACCESO_USUARIO_CREAR",     AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ACCESO_USUARIO_EDITAR",    AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ACCESO_USUARIO_SUSPENDER", AmbitoTransaccion.TERRITORIAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="AUDITORIA_ACCESO",
    nombre="Auditoría de acceso",
    modulo=MODULO,
    descripcion="Consulta del log de auditoría del sistema",
    sistema=True,
    transacciones=[
        FuncionalidadTransaccionDef("ACCESO_AUDITORIA_LEER", AmbitoTransaccion.GLOBAL),
    ],
))
