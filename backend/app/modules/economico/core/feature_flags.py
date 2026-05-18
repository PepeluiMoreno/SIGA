"""Feature flags del módulo financiero."""

FINANCIERO_CONFIG = {
    "version": "COMPLETA",   # "SIMPLE" | "COMPLETA"
    "modulos_activos": {
        "cuotas": True,
        "donaciones": True,
        "remesas": True,
        "cobro": True,
        "reclamaciones": True,
        "presupuesto": True,
        "tesoreria": True,
        "contabilidad": True,
    }
}


def is_version_completa() -> bool:
    return FINANCIERO_CONFIG["version"] == "COMPLETA"


def modulo_activo(nombre: str) -> bool:
    return FINANCIERO_CONFIG["modulos_activos"].get(nombre, False)
