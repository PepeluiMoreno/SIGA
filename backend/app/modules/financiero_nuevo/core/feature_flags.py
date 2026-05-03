
FINANCIERO_CONFIG = {
    "version": "SIMPLE",
    "modulos_activos": {
        "tesoreria": True,
        "contabilidad": False
    }
}

def is_version_completa():
    return FINANCIERO_CONFIG["version"] == "COMPLETA"
