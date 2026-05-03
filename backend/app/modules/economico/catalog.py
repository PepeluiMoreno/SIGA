"""Catálogo de funcionalidades y transacciones del módulo Económico."""

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
    TransaccionDef("ECO_CONCILIACION_REALIZAR",  "Realizar conciliación bancaria",      "MUTACION"),
    # Contabilidad
    TransaccionDef("ECO_ASIENTO_CREAR",          "Crear asiento contable",              "MUTACION"),
    TransaccionDef("ECO_ASIENTO_APROBAR",        "Aprobar asiento contable",            "APROBACION"),
    TransaccionDef("ECO_BALANCE_CONSULTAR",      "Consultar balance contable",          "CONSULTA"),
    # Cuotas
    TransaccionDef("ECO_CUOTA_CONFIGURAR",       "Configurar cuotas anuales",           "MUTACION"),
    TransaccionDef("ECO_CUOTA_REGISTRAR_PAGO",   "Registrar pago de cuota",             "MUTACION"),
    # Donaciones
    TransaccionDef("ECO_DONACION_REGISTRAR",     "Registrar donación",                  "MUTACION"),
    TransaccionDef("ECO_DONACION_LISTAR",        "Listar donaciones",                   "CONSULTA"),
    # Remesas y cobro
    TransaccionDef("ECO_REMESA_GENERAR",         "Generar remesa de cobro",             "MUTACION"),
    TransaccionDef("ECO_REMESA_ENVIAR",          "Enviar remesa al banco",              "MUTACION"),
    # Presupuesto
    TransaccionDef("ECO_PRESUPUESTO_CREAR",      "Crear planificación presupuestaria",  "MUTACION"),
    TransaccionDef("ECO_PRESUPUESTO_APROBAR",    "Aprobar presupuesto anual",           "APROBACION"),
    TransaccionDef("ECO_PRESUPUESTO_CONSULTAR",  "Consultar presupuesto",               "CONSULTA"),
]

for _t in _TRANSACCIONES:
    ModuleCatalog.register_transaccion(MODULO, _t)

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="TESORERIA_BASICA",
    nombre="Tesorería básica",
    modulo=MODULO,
    descripcion="Gestión de cuentas y movimientos de tesorería",
    transacciones=[
        FuncionalidadTransaccionDef("ECO_CUENTA_LISTAR",         AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ECO_CUENTA_CREAR",          AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ECO_MOVIMIENTO_REGISTRAR",  AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ECO_CONCILIACION_REALIZAR", AmbitoTransaccion.TERRITORIAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="CONTABILIDAD",
    nombre="Contabilidad",
    modulo=MODULO,
    descripcion="Asientos contables y balance",
    transacciones=[
        FuncionalidadTransaccionDef("ECO_ASIENTO_CREAR",   AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ECO_ASIENTO_APROBAR", AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ECO_BALANCE_CONSULTAR", AmbitoTransaccion.TERRITORIAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="GESTION_CUOTAS",
    nombre="Gestión de cuotas",
    modulo=MODULO,
    descripcion="Configuración de cuotas y registro de pagos",
    transacciones=[
        FuncionalidadTransaccionDef("ECO_CUOTA_CONFIGURAR",    AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ECO_CUOTA_REGISTRAR_PAGO", AmbitoTransaccion.TERRITORIAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="GESTION_REMESAS",
    nombre="Gestión de remesas",
    modulo=MODULO,
    descripcion="Generación y envío de remesas bancarias para cobro de cuotas",
    transacciones=[
        FuncionalidadTransaccionDef("ECO_REMESA_GENERAR", AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ECO_REMESA_ENVIAR",  AmbitoTransaccion.TERRITORIAL),
    ],
))

ModuleCatalog.register_funcionalidad(FuncionalidadDef(
    codigo="PLANIFICACION_PRESUPUESTARIA",
    nombre="Planificación presupuestaria",
    modulo=MODULO,
    descripcion="Creación y aprobación del presupuesto anual",
    transacciones=[
        FuncionalidadTransaccionDef("ECO_PRESUPUESTO_CREAR",    AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ECO_PRESUPUESTO_APROBAR",  AmbitoTransaccion.TERRITORIAL),
        FuncionalidadTransaccionDef("ECO_PRESUPUESTO_CONSULTAR", AmbitoTransaccion.TERRITORIAL),
    ],
))
