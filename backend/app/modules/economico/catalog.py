"""Catálogo de funcionalidades y transacciones del módulo Económico.

Fuente única de verdad de los permisos económicos. Todos los códigos siguen el
esquema canónico ECO_<ENTIDAD>_<ACCION>, de modo que cualquier permiso del
módulo es reconocible por su prefijo (criterio uniforme en todo el sistema).
"""

from ..acceso.services.registry import (
    ModuleCatalog,
    FuncionalidadDef,
    FuncionalidadTransaccionDef,
    TransaccionDef,
    AmbitoTransaccion,
)

MODULO = "economico"

_TRANSACCIONES = [
    # Tesorería
    TransaccionDef("ECO_CUENTA_LISTAR",          "Listar cuentas bancarias",            "CONSULTA"),
    TransaccionDef("ECO_CUENTA_CREAR",           "Crear cuenta bancaria",               "MUTACION"),
    TransaccionDef("ECO_MOVIMIENTO_REGISTRAR",   "Registrar movimiento de tesorería",   "MUTACION"),
    # Conciliación bancaria
    TransaccionDef("ECO_CONCILIACION_LISTAR",            "Listar conciliaciones",                 "CONSULTA"),
    TransaccionDef("ECO_CONCILIACION_IMPORTAR_EXTRACTO", "Importar extracto bancario",            "MUTACION"),
    TransaccionDef("ECO_CONCILIACION_CONCILIAR_APUNTE",  "Conciliar apunte con extracto",         "MUTACION"),
    TransaccionDef("ECO_CONCILIACION_REALIZAR",          "Realizar conciliación bancaria",        "MUTACION"),
    TransaccionDef("ECO_CONCILIACION_CONFIRMAR_PERIODO", "Confirmar conciliación de período",     "APROBACION"),
    # Contabilidad
    TransaccionDef("ECO_ASIENTO_CREAR",          "Crear asiento contable",              "MUTACION"),
    TransaccionDef("ECO_ASIENTO_APROBAR",        "Aprobar asiento contable",            "APROBACION"),
    TransaccionDef("ECO_BALANCE_CONSULTAR",      "Consultar balance contable",          "CONSULTA"),
    # Estructura de clasificación contable (plan de cuentas PCESFL o categorías fiscales,
    # según el modo de la organización — comparten permiso por ser la misma función)
    TransaccionDef("ECO_ESTRUCTURA_CONTABLE_LISTAR",    "Consultar estructura de clasificación contable", "CONSULTA"),
    TransaccionDef("ECO_ESTRUCTURA_CONTABLE_GESTIONAR", "Gestionar estructura de clasificación contable", "MUTACION"),
    # Cuotas
    TransaccionDef("ECO_CUOTA_LISTAR",                       "Listar cuotas",                          "CONSULTA"),
    TransaccionDef("ECO_CUOTA_CONFIGURAR",                  "Configurar cuotas del ejercicio",        "MUTACION"),
    TransaccionDef("ECO_CUOTA_GENERAR",                     "Generar cuotas anuales",                 "MUTACION"),
    TransaccionDef("ECO_CUOTA_REGISTRAR_PAGO",             "Registrar pago de cuota",                "MUTACION"),
    TransaccionDef("ECO_CUOTA_EXENTAR",                    "Exentar cuota",                          "MUTACION"),
    TransaccionDef("ECO_CUOTA_MOTIVO_REDUCCION_GESTIONAR", "Gestionar motivos de reducción de cuota", "MUTACION"),
    # Recibos
    TransaccionDef("ECO_RECIBO_LISTAR",            "Listar recibos",                       "CONSULTA"),
    TransaccionDef("ECO_RECIBO_EMITIR_LOTE",       "Emitir recibos en lote",               "MUTACION"),
    TransaccionDef("ECO_RECIBO_ANULAR",            "Anular recibo",                        "MUTACION"),
    TransaccionDef("ECO_RECIBO_DESCARGAR_PDF",     "Descargar PDF del recibo",             "CONSULTA"),
    TransaccionDef("ECO_RECIBO_ENVIAR_EMAIL",      "Enviar recibo por email al socio",     "MUTACION"),
    TransaccionDef("ECO_RECIBO_NOTIFICAR_FALLIDOS", "Comunicar recibos fallidos a socios", "MUTACION"),
    TransaccionDef("ECO_RECIBO_MARCAR_COBRADO",    "Marcar recibo cobrado manualmente",    "MUTACION"),
    # Remesas SEPA
    TransaccionDef("ECO_REMESA_LISTAR",             "Listar remesas",                       "CONSULTA"),
    TransaccionDef("ECO_REMESA_CREAR",              "Crear remesa SEPA",                    "MUTACION"),
    TransaccionDef("ECO_REMESA_PREVISUALIZAR",      "Previsualizar remesa",                 "CONSULTA"),
    TransaccionDef("ECO_REMESA_GENERAR_XML",        "Generar XML SEPA",                     "MUTACION"),
    TransaccionDef("ECO_REMESA_ENVIAR",             "Enviar remesa al banco",               "MUTACION"),
    TransaccionDef("ECO_REMESA_PROCESAR_RESPUESTA", "Procesar respuesta del banco",         "MUTACION"),
    TransaccionDef("ECO_REMESA_REENVIAR",           "Generar remesa de reenvío",            "MUTACION"),
    TransaccionDef("ECO_REMESA_ANULAR",             "Anular remesa",                        "MUTACION"),
    # Donaciones
    TransaccionDef("ECO_DONACION_LISTAR",              "Listar donaciones",                 "CONSULTA"),
    TransaccionDef("ECO_DONACION_REGISTRAR",           "Registrar donación",                "MUTACION"),
    TransaccionDef("ECO_DONACION_EMITIR_CERTIFICADO",  "Emitir certificado fiscal",         "MUTACION"),
    # Justificantes de gasto
    TransaccionDef("ECO_JUSTIFICANTE_LISTAR",    "Listar justificantes de gasto",          "CONSULTA"),
    TransaccionDef("ECO_JUSTIFICANTE_PRESENTAR", "Presentar justificante de gasto",        "MUTACION"),
    TransaccionDef("ECO_JUSTIFICANTE_ACEPTAR",   "Aceptar justificante de gasto",          "MUTACION"),
    TransaccionDef("ECO_JUSTIFICANTE_APROBAR",   "Aprobar justificante de gasto",          "APROBACION"),
    TransaccionDef("ECO_JUSTIFICANTE_PAGAR",     "Registrar pago de justificante",         "MUTACION"),
    # Cuentas Anuales
    TransaccionDef("ECO_CUENTAS_ANUALES_LISTAR",    "Consultar Cuentas Anuales",                "CONSULTA"),
    TransaccionDef("ECO_CUENTAS_ANUALES_GENERAR",   "Generar / editar Cuentas Anuales (Memoria)", "MUTACION"),
    TransaccionDef("ECO_CUENTAS_ANUALES_APROBAR",   "Aprobar Cuentas Anuales (junta)",          "APROBACION"),
    TransaccionDef("ECO_CUENTAS_ANUALES_DEPOSITAR", "Marcar Cuentas Anuales como depositadas",  "MUTACION"),
    # Modelo 182
    TransaccionDef("ECO_MODELO182_LISTAR",    "Consultar presentaciones Modelo 182",     "CONSULTA"),
    TransaccionDef("ECO_MODELO182_GENERAR",   "Generar Modelo 182",                      "MUTACION"),
    TransaccionDef("ECO_MODELO182_REGISTRAR", "Registrar presentación Modelo 182",       "MUTACION"),
    # Cierre de ejercicio
    TransaccionDef("ECO_CIERRE_CONSULTAR", "Consultar estado del cierre",                "CONSULTA"),
    TransaccionDef("ECO_CIERRE_EJECUTAR",  "Ejecutar cierre de ejercicio",               "APROBACION"),
    # Presupuesto
    TransaccionDef("ECO_PRESUPUESTO_CREAR",      "Crear planificación presupuestaria",  "MUTACION"),
    TransaccionDef("ECO_PRESUPUESTO_APROBAR",    "Aprobar presupuesto anual",           "APROBACION"),
    TransaccionDef("ECO_PRESUPUESTO_CONSULTAR",  "Consultar presupuesto",               "CONSULTA"),
    # Informes
    TransaccionDef("ECO_INFORME_FINANCIERO_VER", "Ver informes financieros",            "CONSULTA"),
]

for _t in _TRANSACCIONES:
    ModuleCatalog.register_transaccion(MODULO, _t)


def _func(codigo, nombre, descripcion, codigos, ambito=AmbitoTransaccion.TERRITORIAL):
    ModuleCatalog.register_funcionalidad(FuncionalidadDef(
        codigo=codigo,
        nombre=nombre,
        modulo=MODULO,
        descripcion=descripcion,
        transacciones=[FuncionalidadTransaccionDef(c, ambito) for c in codigos],
    ))


_func("TESORERIA_BASICA", "Tesorería básica",
      "Gestión de cuentas y movimientos de tesorería",
      ["ECO_CUENTA_LISTAR", "ECO_CUENTA_CREAR", "ECO_MOVIMIENTO_REGISTRAR"])

_func("CONCILIACION_BANCARIA", "Conciliación bancaria",
      "Importación de extractos y conciliación de apuntes con el banco",
      ["ECO_CONCILIACION_LISTAR", "ECO_CONCILIACION_IMPORTAR_EXTRACTO",
       "ECO_CONCILIACION_CONCILIAR_APUNTE", "ECO_CONCILIACION_REALIZAR",
       "ECO_CONCILIACION_CONFIRMAR_PERIODO"])

_func("CONTABILIDAD", "Contabilidad",
      "Asientos contables y balance",
      ["ECO_ASIENTO_CREAR", "ECO_ASIENTO_APROBAR", "ECO_BALANCE_CONSULTAR"])

_func("ESTRUCTURA_CLASIFICACION_CONTABLE", "Estructura de clasificación contable",
      "Gestión de la estructura de clasificación contable: plan de cuentas PCESFL "
      "en modo completo o categorías fiscales en modo simplificado. Un mismo "
      "permiso cubre ambos, por ser la misma función.",
      ["ECO_ESTRUCTURA_CONTABLE_LISTAR", "ECO_ESTRUCTURA_CONTABLE_GESTIONAR"])

_func("GESTION_CUOTAS", "Gestión de cuotas",
      "Configuración, generación, cobro y exención de cuotas",
      ["ECO_CUOTA_LISTAR", "ECO_CUOTA_CONFIGURAR", "ECO_CUOTA_GENERAR",
       "ECO_CUOTA_REGISTRAR_PAGO", "ECO_CUOTA_EXENTAR",
       "ECO_CUOTA_MOTIVO_REDUCCION_GESTIONAR"])

_func("GESTION_RECIBOS", "Gestión de recibos",
      "Emisión, envío, anulación y seguimiento de recibos de cuota",
      ["ECO_RECIBO_LISTAR", "ECO_RECIBO_EMITIR_LOTE", "ECO_RECIBO_ANULAR",
       "ECO_RECIBO_DESCARGAR_PDF", "ECO_RECIBO_ENVIAR_EMAIL",
       "ECO_RECIBO_NOTIFICAR_FALLIDOS", "ECO_RECIBO_MARCAR_COBRADO"])

_func("GESTION_REMESAS", "Gestión de remesas",
      "Generación, envío y procesamiento de remesas SEPA para cobro de cuotas",
      ["ECO_REMESA_LISTAR", "ECO_REMESA_CREAR", "ECO_REMESA_PREVISUALIZAR",
       "ECO_REMESA_GENERAR_XML", "ECO_REMESA_ENVIAR",
       "ECO_REMESA_PROCESAR_RESPUESTA", "ECO_REMESA_REENVIAR", "ECO_REMESA_ANULAR"])

_func("GESTION_DONACIONES", "Gestión de donaciones",
      "Registro de donaciones y emisión de certificados fiscales",
      ["ECO_DONACION_LISTAR", "ECO_DONACION_REGISTRAR", "ECO_DONACION_EMITIR_CERTIFICADO"])

_func("JUSTIFICANTES_GASTO", "Justificantes de gasto",
      "Ciclo de presentación, aceptación, aprobación y pago de justificantes",
      ["ECO_JUSTIFICANTE_LISTAR", "ECO_JUSTIFICANTE_PRESENTAR",
       "ECO_JUSTIFICANTE_ACEPTAR", "ECO_JUSTIFICANTE_APROBAR", "ECO_JUSTIFICANTE_PAGAR"])

_func("CUENTAS_ANUALES", "Cuentas anuales",
      "Generación, aprobación y depósito de las Cuentas Anuales",
      ["ECO_CUENTAS_ANUALES_LISTAR", "ECO_CUENTAS_ANUALES_GENERAR",
       "ECO_CUENTAS_ANUALES_APROBAR", "ECO_CUENTAS_ANUALES_DEPOSITAR"])

_func("MODELO_182", "Modelo 182",
      "Generación y registro de presentaciones del Modelo 182 (donativos)",
      ["ECO_MODELO182_LISTAR", "ECO_MODELO182_GENERAR", "ECO_MODELO182_REGISTRAR"])

_func("CIERRE_EJERCICIO", "Cierre de ejercicio",
      "Consulta y ejecución del cierre contable del ejercicio",
      ["ECO_CIERRE_CONSULTAR", "ECO_CIERRE_EJECUTAR"])

_func("PLANIFICACION_PRESUPUESTARIA", "Planificación presupuestaria",
      "Creación y aprobación del presupuesto anual",
      ["ECO_PRESUPUESTO_CREAR", "ECO_PRESUPUESTO_APROBAR", "ECO_PRESUPUESTO_CONSULTAR"])

_func("INFORMES_FINANCIEROS", "Informes financieros",
      "Consulta de informes financieros y cuadros de mando económicos",
      ["ECO_INFORME_FINANCIERO_VER"])
