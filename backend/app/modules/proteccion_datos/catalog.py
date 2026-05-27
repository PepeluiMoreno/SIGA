"""Catálogo de funcionalidades y transacciones del módulo Protección de Datos (RGPD).

Mapea las 6 fases del plan a funcionalidades RBAC. Prefijo `RGPD_` para
todas las transacciones (la palabra "skill" sigue prohibida en el
proyecto; aquí no aplica).
"""

from ..acceso.services.registry import (
    ModuleCatalog,
    FuncionalidadDef,
    FuncionalidadTransaccionDef,
    TransaccionDef,
    AmbitoTransaccion,
)

MODULO = "proteccion_datos"

_TRANSACCIONES = [
    # Fase 1 — RAT y encargados
    TransaccionDef("RGPD_RAT_LEER",                "Consultar Registro de Actividades de Tratamiento", "CONSULTA"),
    TransaccionDef("RGPD_RAT_GESTIONAR",           "Gestionar actividades del RAT",                    "MUTACION"),
    TransaccionDef("RGPD_ENCARGADO_GESTIONAR",     "Gestionar encargados del tratamiento",             "MUTACION"),

    # Fase 3 — derechos ARSULIPO
    TransaccionDef("RGPD_SOLICITUD_LEER",          "Consultar solicitudes de derechos",                "CONSULTA"),
    TransaccionDef("RGPD_SOLICITUD_REGISTRAR",     "Registrar solicitud de derecho",                   "MUTACION"),
    TransaccionDef("RGPD_SOLICITUD_TRAMITAR",      "Tramitar solicitud de derecho (cambios estado)",   "MUTACION"),
    TransaccionDef("RGPD_SOLICITUD_RESOLVER",      "Resolver solicitud de derecho",                    "APROBACION"),

    # Fase 4 — cláusulas y consentimientos
    TransaccionDef("RGPD_CLAUSULA_GESTIONAR",      "Gestionar cláusulas informativas",                 "MUTACION"),
    TransaccionDef("RGPD_CONSENTIMIENTO_LEER",     "Consultar consentimientos",                        "CONSULTA"),
    TransaccionDef("RGPD_CONSENTIMIENTO_REGISTRAR","Registrar / retirar consentimiento",               "MUTACION"),

    # Fase 5 — brechas
    TransaccionDef("RGPD_BRECHA_LEER",             "Consultar brechas de seguridad",                   "CONSULTA"),
    TransaccionDef("RGPD_BRECHA_REGISTRAR",        "Registrar brecha de seguridad",                    "MUTACION"),
    TransaccionDef("RGPD_BRECHA_NOTIFICAR_AEPD",   "Notificar brecha a la AEPD",                       "APROBACION"),
    TransaccionDef("RGPD_BRECHA_CERRAR",           "Cerrar brecha de seguridad",                       "APROBACION"),

    # Fase 6 — auditoría de accesos
    TransaccionDef("RGPD_AUDITORIA_LEER",          "Consultar log de accesos a datos personales",      "CONSULTA"),

    # Anonimización (ya existía operativamente, ahora bajo este catálogo)
    TransaccionDef("RGPD_ANONIMIZAR_MIEMBRO",      "Anonimizar datos de un miembro",                   "APROBACION"),
]

for _t in _TRANSACCIONES:
    ModuleCatalog.register_transaccion(MODULO, _t)


ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="RGPD_RAT",
    nombre="Registro de Actividades de Tratamiento",
    modulo=MODULO,
    descripcion="RAT (art. 30) y encargados del tratamiento (art. 28)",
    sistema=True,
    transacciones=[
        FuncionalidadTransaccionDef("RGPD_RAT_LEER",            AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("RGPD_RAT_GESTIONAR",       AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("RGPD_ENCARGADO_GESTIONAR", AmbitoTransaccion.GLOBAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="RGPD_DERECHOS",
    nombre="Derechos de los interesados (ARSULIPO)",
    modulo=MODULO,
    descripcion="Acceso, Rectificación, Supresión, Limitación, Portabilidad, Oposición",
    sistema=True,
    transacciones=[
        FuncionalidadTransaccionDef("RGPD_SOLICITUD_LEER",       AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("RGPD_SOLICITUD_REGISTRAR",  AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("RGPD_SOLICITUD_TRAMITAR",   AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("RGPD_SOLICITUD_RESOLVER",   AmbitoTransaccion.GLOBAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="RGPD_CONSENTIMIENTOS",
    nombre="Cláusulas informativas y consentimientos",
    modulo=MODULO,
    descripcion="Textos informativos versionados y consentimientos otorgados",
    sistema=True,
    transacciones=[
        FuncionalidadTransaccionDef("RGPD_CLAUSULA_GESTIONAR",       AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("RGPD_CONSENTIMIENTO_LEER",      AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("RGPD_CONSENTIMIENTO_REGISTRAR", AmbitoTransaccion.GLOBAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="RGPD_BRECHAS",
    nombre="Brechas de seguridad",
    modulo=MODULO,
    descripcion="Registro de incidencias y asistente de notificación AEPD",
    sistema=True,
    transacciones=[
        FuncionalidadTransaccionDef("RGPD_BRECHA_LEER",           AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("RGPD_BRECHA_REGISTRAR",      AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("RGPD_BRECHA_NOTIFICAR_AEPD", AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("RGPD_BRECHA_CERRAR",         AmbitoTransaccion.GLOBAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="RGPD_AUDITORIA",
    nombre="Auditoría de accesos a datos personales",
    modulo=MODULO,
    descripcion="Log append-only para responsabilidad proactiva (art. 5.2)",
    sistema=True,
    transacciones=[
        FuncionalidadTransaccionDef("RGPD_AUDITORIA_LEER",      AmbitoTransaccion.GLOBAL),
        FuncionalidadTransaccionDef("RGPD_ANONIMIZAR_MIEMBRO",  AmbitoTransaccion.GLOBAL),
    ],
))
