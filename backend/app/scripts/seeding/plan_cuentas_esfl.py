"""Script para cargar el Plan de Cuentas de Entidades Sin Fines Lucrativos (PCESFL 2013)."""

from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.financiero.models.contabilidad import (
    CuentaContable,
    TipoCuentaContable,
)


async def cargar_plan_cuentas_esfl(session: AsyncSession) -> None:
    """Carga el plan de cuentas simplificado PCESFL 2013."""

    # Estructura simplificada del PCESFL 2013
    cuentas_data = [
        # GRUPO 1: FINANCIERO (ACTIVO)
        {
            "codigo": "1",
            "nombre": "ACTIVO",
            "tipo": TipoCuentaContable.ACTIVO,
            "nivel": 1,
            "padre_id": None,
        },
        {
            "codigo": "10",
            "nombre": "Activo Corriente",
            "tipo": TipoCuentaContable.ACTIVO,
            "nivel": 2,
            "padre_id": None,
        },
        {
            "codigo": "100",
            "nombre": "Caja",
            "tipo": TipoCuentaContable.ACTIVO,
            "nivel": 3,
            "padre_id": None,
        },
        {
            "codigo": "101",
            "nombre": "Bancos c/c",
            "tipo": TipoCuentaContable.ACTIVO,
            "nivel": 3,
            "padre_id": None,
        },
        {
            "codigo": "102",
            "nombre": "Valores negociables",
            "tipo": TipoCuentaContable.ACTIVO,
            "nivel": 3,
            "padre_id": None,
        },
        {
            "codigo": "11",
            "nombre": "Deudores",
            "tipo": TipoCuentaContable.ACTIVO,
            "nivel": 2,
            "padre_id": None,
        },
        {
            "codigo": "110",
            "nombre": "Deudores por actividades propias",
            "tipo": TipoCuentaContable.ACTIVO,
            "nivel": 3,
            "padre_id": None,
        },
        {
            "codigo": "111",
            "nombre": "Deudores por subvenciones",
            "tipo": TipoCuentaContable.ACTIVO,
            "nivel": 3,
            "padre_id": None,
        },
        # GRUPO 2: PASIVO
        {
            "codigo": "2",
            "nombre": "PASIVO",
            "tipo": TipoCuentaContable.PASIVO,
            "nivel": 1,
            "padre_id": None,
        },
        {
            "codigo": "20",
            "nombre": "Pasivo Corriente",
            "tipo": TipoCuentaContable.PASIVO,
            "nivel": 2,
            "padre_id": None,
        },
        {
            "codigo": "200",
            "nombre": "Acreedores por actividades propias",
            "tipo": TipoCuentaContable.PASIVO,
            "nivel": 3,
            "padre_id": None,
        },
        {
            "codigo": "201",
            "nombre": "Acreedores por suministros",
            "tipo": TipoCuentaContable.PASIVO,
            "nivel": 3,
            "padre_id": None,
        },
        # GRUPO 3: PATRIMONIO
        {
            "codigo": "3",
            "nombre": "PATRIMONIO",
            "tipo": TipoCuentaContable.PATRIMONIO,
            "nivel": 1,
            "padre_id": None,
        },
        {
            "codigo": "30",
            "nombre": "Dotación fundacional",
            "tipo": TipoCuentaContable.PATRIMONIO,
            "nivel": 2,
            "padre_id": None,
        },
        {
            "codigo": "300",
            "nombre": "Dotación fundacional",
            "tipo": TipoCuentaContable.PATRIMONIO,
            "nivel": 3,
            "padre_id": None,
            "es_dotacion": True,
        },
        {
            "codigo": "31",
            "nombre": "Reservas",
            "tipo": TipoCuentaContable.PATRIMONIO,
            "nivel": 2,
            "padre_id": None,
        },
        {
            "codigo": "310",
            "nombre": "Reservas de patrimonio",
            "tipo": TipoCuentaContable.PATRIMONIO,
            "nivel": 3,
            "padre_id": None,
        },
        # GRUPO 4: INGRESOS
        {
            "codigo": "4",
            "nombre": "INGRESOS",
            "tipo": TipoCuentaContable.INGRESO,
            "nivel": 1,
            "padre_id": None,
        },
        {
            "codigo": "40",
            "nombre": "Ingresos de la actividad propia",
            "tipo": TipoCuentaContable.INGRESO,
            "nivel": 2,
            "padre_id": None,
        },
        {
            "codigo": "400",
            "nombre": "Cuotas de miembros",
            "tipo": TipoCuentaContable.INGRESO,
            "nivel": 3,
            "padre_id": None,
        },
        {
            "codigo": "401",
            "nombre": "Ingresos por prestación de servicios",
            "tipo": TipoCuentaContable.INGRESO,
            "nivel": 3,
            "padre_id": None,
        },
        {
            "codigo": "41",
            "nombre": "Donaciones",
            "tipo": TipoCuentaContable.INGRESO,
            "nivel": 2,
            "padre_id": None,
        },
        {
            "codigo": "410",
            "nombre": "Donaciones",
            "tipo": TipoCuentaContable.INGRESO,
            "nivel": 3,
            "padre_id": None,
        },
        {
            "codigo": "42",
            "nombre": "Subvenciones",
            "tipo": TipoCuentaContable.INGRESO,
            "nivel": 2,
            "padre_id": None,
        },
        {
            "codigo": "420",
            "nombre": "Subvenciones del sector público",
            "tipo": TipoCuentaContable.INGRESO,
            "nivel": 3,
            "padre_id": None,
        },
        {
            "codigo": "43",
            "nombre": "Ingresos financieros",
            "tipo": TipoCuentaContable.INGRESO,
            "nivel": 2,
            "padre_id": None,
        },
        {
            "codigo": "430",
            "nombre": "Intereses de cuentas bancarias",
            "tipo": TipoCuentaContable.INGRESO,
            "nivel": 3,
            "padre_id": None,
        },
        # GRUPO 5: GASTOS
        {
            "codigo": "5",
            "nombre": "GASTOS",
            "tipo": TipoCuentaContable.GASTO,
            "nivel": 1,
            "padre_id": None,
        },
        {
            "codigo": "50",
            "nombre": "Gastos de actividades propias",
            "tipo": TipoCuentaContable.GASTO,
            "nivel": 2,
            "padre_id": None,
        },
        {
            "codigo": "500",
            "nombre": "Suministros",
            "tipo": TipoCuentaContable.GASTO,
            "nivel": 3,
            "padre_id": None,
        },
        {
            "codigo": "501",
            "nombre": "Servicios externos",
            "tipo": TipoCuentaContable.GASTO,
            "nivel": 3,
            "padre_id": None,
        },
        {
            "codigo": "51",
            "nombre": "Gastos de personal",
            "tipo": TipoCuentaContable.GASTO,
            "nivel": 2,
            "padre_id": None,
        },
        {
            "codigo": "510",
            "nombre": "Sueldos y salarios",
            "tipo": TipoCuentaContable.GASTO,
            "nivel": 3,
            "padre_id": None,
        },
        {
            "codigo": "511",
            "nombre": "Seguridad social",
            "tipo": TipoCuentaContable.GASTO,
            "nivel": 3,
            "padre_id": None,
        },
        {
            "codigo": "52",
            "nombre": "Gastos de administración",
            "tipo": TipoCuentaContable.GASTO,
            "nivel": 2,
            "padre_id": None,
        },
        {
            "codigo": "520",
            "nombre": "Alquileres",
            "tipo": TipoCuentaContable.GASTO,
            "nivel": 3,
            "padre_id": None,
        },
        {
            "codigo": "521",
            "nombre": "Servicios administrativos",
            "tipo": TipoCuentaContable.GASTO,
            "nivel": 3,
            "padre_id": None,
        },
        {
            "codigo": "53",
            "nombre": "Amortizaciones",
            "tipo": TipoCuentaContable.GASTO,
            "nivel": 2,
            "padre_id": None,
        },
        {
            "codigo": "530",
            "nombre": "Amortización de inmovilizado",
            "tipo": TipoCuentaContable.GASTO,
            "nivel": 3,
            "padre_id": None,
        },
    ]

    # Crear las cuentas
    for cuenta_data in cuentas_data:
        # Verificar si ya existe
        existing = await session.execute(
            "SELECT * FROM cuentas_contables WHERE codigo = :codigo",
            {"codigo": cuenta_data["codigo"]},
        )
        if not existing.scalars().first():
            cuenta = CuentaContable(**cuenta_data)
            session.add(cuenta)

    await session.commit()
    print("Plan de cuentas PCESFL 2013 cargado exitosamente")
