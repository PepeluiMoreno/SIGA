"""Catálogo de funcionalidades y transacciones del módulo Secretaría."""

from ..acceso.services.registry import (
    ModuleCatalog,
    FuncionalidadDef,
    FuncionalidadTransaccionDef,
    TransaccionDef,
    AmbitoTransaccion,
)

MODULO = "secretaria"

_TRANSACCIONES = [
    # Reuniones
    TransaccionDef("SEC_REUNION_LISTAR",          "Listar reuniones",                    "CONSULTA"),
    TransaccionDef("SEC_REUNION_CREAR",           "Convocar reunión",                    "MUTACION"),
    TransaccionDef("SEC_REUNION_EDITAR",          "Editar reunión",                      "MUTACION"),
    TransaccionDef("SEC_REUNION_REGISTRAR_ASIST", "Registrar asistencia",                "MUTACION"),
    TransaccionDef("SEC_REUNION_CANCELAR",        "Cancelar reunión",                    "MUTACION"),
    # Orden del día y acuerdos
    TransaccionDef("SEC_ACUERDO_LISTAR",          "Listar acuerdos",                     "CONSULTA"),
    TransaccionDef("SEC_ACUERDO_CREAR",           "Registrar acuerdo",                   "MUTACION"),
    TransaccionDef("SEC_ACUERDO_EDITAR",          "Editar acuerdo",                      "MUTACION"),
    TransaccionDef("SEC_ACUERDO_SEGUIMIENTO",     "Actualizar seguimiento de acuerdo",   "MUTACION"),
    # Actas
    TransaccionDef("SEC_ACTA_LISTAR",             "Listar actas",                        "CONSULTA"),
    TransaccionDef("SEC_ACTA_CREAR",              "Redactar acta",                       "MUTACION"),
    TransaccionDef("SEC_ACTA_APROBAR",            "Aprobar acta",                        "APROBACION"),
    TransaccionDef("SEC_ACTA_FIRMAR",             "Firmar acta",                         "APROBACION"),
    TransaccionDef("SEC_ACTA_EXPORTAR",           "Exportar acta a PDF",                 "CONSULTA"),
    # Certificados
    TransaccionDef("SEC_CERTIFICADO_EMITIR",      "Emitir certificado de acuerdo",       "MUTACION"),
    TransaccionDef("SEC_CERTIFICADO_LISTAR",      "Listar certificados emitidos",        "CONSULTA"),
    # Libro de socios
    TransaccionDef("SEC_LIBRO_SOCIOS_GENERAR",    "Generar Libro de Socios",             "MUTACION"),
    TransaccionDef("SEC_LIBRO_SOCIOS_CONSULTAR",  "Consultar Libro de Socios",           "CONSULTA"),
    # Convenios
    TransaccionDef("SEC_CONVENIO_LISTAR",         "Listar convenios",                    "CONSULTA"),
    TransaccionDef("SEC_CONVENIO_CREAR",          "Registrar convenio",                  "MUTACION"),
    TransaccionDef("SEC_CONVENIO_EDITAR",         "Editar convenio",                     "MUTACION"),
    # Delegaciones
    TransaccionDef("SEC_DELEGACION_GESTIONAR",    "Gestionar delegaciones de firma",     "MUTACION"),
    TransaccionDef("SEC_DELEGACION_LISTAR",       "Listar delegaciones vigentes",        "CONSULTA"),
]

for _t in _TRANSACCIONES:
    ModuleCatalog.register_transaccion(MODULO, _t)

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="GESTION_REUNIONES",
    nombre="Gestión de reuniones",
    modulo=MODULO,
    descripcion="Convocatoria, celebración, asistencia y acuerdos de reuniones de órganos de gobierno",
    transacciones=[
        FuncionalidadTransaccionDef("SEC_REUNION_LISTAR",          AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("SEC_REUNION_CREAR",           AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("SEC_REUNION_EDITAR",          AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("SEC_REUNION_REGISTRAR_ASIST", AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("SEC_REUNION_CANCELAR",        AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("SEC_ACUERDO_LISTAR",          AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("SEC_ACUERDO_CREAR",           AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("SEC_ACUERDO_EDITAR",          AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("SEC_ACUERDO_SEGUIMIENTO",     AmbitoTransaccion.TERRITORIAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="GESTION_ACTAS",
    nombre="Gestión de actas",
    modulo=MODULO,
    descripcion="Redacción, aprobación, firma y exportación del Libro de Actas",
    transacciones=[
        FuncionalidadTransaccionDef("SEC_ACTA_LISTAR",    AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("SEC_ACTA_CREAR",     AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("SEC_ACTA_APROBAR",   AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("SEC_ACTA_FIRMAR",    AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("SEC_ACTA_EXPORTAR",  AmbitoTransaccion.TERRITORIAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="CERTIFICADOS_ACUERDOS",
    nombre="Certificados de acuerdos",
    modulo=MODULO,
    descripcion="Emisión de certificados de acuerdos para presentar ante terceros",
    transacciones=[
        FuncionalidadTransaccionDef("SEC_CERTIFICADO_EMITIR", AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("SEC_CERTIFICADO_LISTAR", AmbitoTransaccion.TERRITORIAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="LIBRO_SOCIOS",
    nombre="Libro de Socios",
    modulo=MODULO,
    descripcion="Generación y consulta del Libro de Socios (Ley 1/2002)",
    transacciones=[
        FuncionalidadTransaccionDef("SEC_LIBRO_SOCIOS_GENERAR",   AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("SEC_LIBRO_SOCIOS_CONSULTAR", AmbitoTransaccion.GLOBAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="CONVENIOS_INSTITUCIONALES",
    nombre="Convenios y delegaciones",
    modulo=MODULO,
    descripcion="Gestión de convenios firmados y delegaciones de representación",
    transacciones=[
        FuncionalidadTransaccionDef("SEC_CONVENIO_LISTAR",      AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("SEC_CONVENIO_CREAR",       AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("SEC_CONVENIO_EDITAR",      AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("SEC_DELEGACION_GESTIONAR", AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("SEC_DELEGACION_LISTAR",    AmbitoTransaccion.GLOBAL),
    ],
))
