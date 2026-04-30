"""Seeding de transacciones del sistema."""

import asyncio
from sqlalchemy import select

from app.core.database import async_session
from app.models import Transaccion, Rol, RolTransaccion
from app.models.tipologias import TipoTransaccion


# Transacciones organizadas por módulo
TRANSACCIONES = [
    # === miembroS ===
    {"codigo": "ALTA_miembro", "nombre": "Alta de miembro", "tipo": TipoTransaccion.MUTATION, "modulo": "miembros"},
    {"codigo": "CONFIRMAR_ALTA_miembro", "nombre": "Confirmar alta de miembro", "tipo": TipoTransaccion.MUTATION, "modulo": "miembros"},
    {"codigo": "BAJA_miembro", "nombre": "Baja de miembro", "tipo": TipoTransaccion.MUTATION, "modulo": "miembros"},
    {"codigo": "VER_miembro", "nombre": "Ver datos de miembro", "tipo": TipoTransaccion.QUERY, "modulo": "miembros"},
    {"codigo": "ACTUALIZAR_miembro", "nombre": "Actualizar datos de miembro", "tipo": TipoTransaccion.MUTATION, "modulo": "miembros"},
    {"codigo": "LISTAR_miembroS", "nombre": "Listar miembros", "tipo": TipoTransaccion.QUERY, "modulo": "miembros"},
    {"codigo": "EXPORTAR_miembroS", "nombre": "Exportar miembros a Excel", "tipo": TipoTransaccion.QUERY, "modulo": "miembros"},

    # === SIMPATIZANTES ===
    {"codigo": "ALTA_SIMPATIZANTE", "nombre": "Alta de simpatizante", "tipo": TipoTransaccion.MUTATION, "modulo": "simpatizantes"},
    {"codigo": "BAJA_SIMPATIZANTE", "nombre": "Baja de simpatizante", "tipo": TipoTransaccion.MUTATION, "modulo": "simpatizantes"},
    {"codigo": "SIMPATIZANTE_A_miembro", "nombre": "Convertir simpatizante a miembro", "tipo": TipoTransaccion.MUTATION, "modulo": "simpatizantes"},

    # === CUOTAS ===
    {"codigo": "VER_CUOTAS", "nombre": "Ver cuotas", "tipo": TipoTransaccion.QUERY, "modulo": "cuotas"},
    {"codigo": "CREAR_CUOTA", "nombre": "Crear cuota", "tipo": TipoTransaccion.MUTATION, "modulo": "cuotas"},
    {"codigo": "PAGAR_CUOTA", "nombre": "Pagar cuota", "tipo": TipoTransaccion.MUTATION, "modulo": "cuotas"},
    {"codigo": "ANOTAR_INGRESO_CUOTA", "nombre": "Anotar ingreso de cuota", "tipo": TipoTransaccion.MUTATION, "modulo": "cuotas"},
    {"codigo": "VER_TOTALES_CUOTAS", "nombre": "Ver totales de cuotas", "tipo": TipoTransaccion.QUERY, "modulo": "cuotas"},
    {"codigo": "EXPORTAR_CUOTAS", "nombre": "Exportar cuotas", "tipo": TipoTransaccion.QUERY, "modulo": "cuotas"},
    {"codigo": "GESTIONAR_CUOTAS_VIGENTES", "nombre": "Gestionar cuotas vigentes", "tipo": TipoTransaccion.MUTATION, "modulo": "cuotas"},

    # === DONACIONES ===
    {"codigo": "VER_DONACIONES", "nombre": "Ver donaciones", "tipo": TipoTransaccion.QUERY, "modulo": "donaciones"},
    {"codigo": "CREAR_DONACION", "nombre": "Crear donación", "tipo": TipoTransaccion.MUTATION, "modulo": "donaciones"},
    {"codigo": "ANOTAR_INGRESO_DONACION", "nombre": "Anotar ingreso de donación", "tipo": TipoTransaccion.MUTATION, "modulo": "donaciones"},
    {"codigo": "ANULAR_DONACION", "nombre": "Anular donación", "tipo": TipoTransaccion.MUTATION, "modulo": "donaciones"},
    {"codigo": "GESTIONAR_CONCEPTOS_DONACION", "nombre": "Gestionar conceptos de donación", "tipo": TipoTransaccion.MUTATION, "modulo": "donaciones"},

    # === REMESAS SEPA ===
    {"codigo": "VER_REMESAS", "nombre": "Ver remesas", "tipo": TipoTransaccion.QUERY, "modulo": "remesas"},
    {"codigo": "CREAR_REMESA", "nombre": "Crear remesa", "tipo": TipoTransaccion.MUTATION, "modulo": "remesas"},
    {"codigo": "GENERAR_SEPA_XML", "nombre": "Generar fichero SEPA XML", "tipo": TipoTransaccion.MUTATION, "modulo": "remesas"},
    {"codigo": "ELIMINAR_REMESA", "nombre": "Eliminar remesa", "tipo": TipoTransaccion.MUTATION, "modulo": "remesas"},
    {"codigo": "ACTUALIZAR_CUOTAS_REMESA", "nombre": "Actualizar cuotas cobradas en remesa", "tipo": TipoTransaccion.MUTATION, "modulo": "remesas"},

    # === AGRUPACIONES ===
    {"codigo": "VER_AGRUPACIONES", "nombre": "Ver agrupaciones", "tipo": TipoTransaccion.QUERY, "modulo": "agrupaciones"},
    {"codigo": "ACTUALIZAR_AGRUPACION", "nombre": "Actualizar agrupación", "tipo": TipoTransaccion.MUTATION, "modulo": "agrupaciones"},

    # === EMAILS ===
    {"codigo": "ENVIAR_EMAIL_miembroS", "nombre": "Enviar email a miembros", "tipo": TipoTransaccion.MUTATION, "modulo": "emails"},
    {"codigo": "ENVIAR_EMAIL_SIMPATIZANTES", "nombre": "Enviar email a simpatizantes", "tipo": TipoTransaccion.MUTATION, "modulo": "emails"},
    {"codigo": "ENVIAR_AVISO_COBRO", "nombre": "Enviar aviso de próximo cobro", "tipo": TipoTransaccion.MUTATION, "modulo": "emails"},

    # === ROLES Y PERMISOS ===
    {"codigo": "GESTIONAR_ROLES", "nombre": "Gestionar roles", "tipo": TipoTransaccion.MUTATION, "modulo": "admin"},
    {"codigo": "ASIGNAR_ROL_COORDINADOR", "nombre": "Asignar rol coordinador", "tipo": TipoTransaccion.MUTATION, "modulo": "admin"},
    {"codigo": "ASIGNAR_ROL_PRESIDENTE", "nombre": "Asignar rol presidente", "tipo": TipoTransaccion.MUTATION, "modulo": "admin"},
    {"codigo": "ASIGNAR_ROL_TESORERO", "nombre": "Asignar rol tesorero", "tipo": TipoTransaccion.MUTATION, "modulo": "admin"},
    {"codigo": "ASIGNAR_ROL_ADMIN", "nombre": "Asignar rol administrador", "tipo": TipoTransaccion.MUTATION, "modulo": "admin"},

    # === ADMINISTRACIÓN ===
    {"codigo": "CAMBIAR_MODO_SISTEMA", "nombre": "Cambiar modo explotación/mantenimiento", "tipo": TipoTransaccion.MUTATION, "modulo": "admin"},
    {"codigo": "CIERRE_ANIO", "nombre": "Cierre de año / Apertura año nuevo", "tipo": TipoTransaccion.MUTATION, "modulo": "admin"},
    {"codigo": "IMPORTAR_DATOS", "nombre": "Importar datos desde Excel", "tipo": TipoTransaccion.MUTATION, "modulo": "admin"},

    # === ESTADÍSTICAS ===
    {"codigo": "VER_ESTADISTICAS", "nombre": "Ver estadísticas", "tipo": TipoTransaccion.QUERY, "modulo": "estadisticas"},
    {"codigo": "EXPORTAR_INFORME_ANUAL", "nombre": "Exportar informe anual", "tipo": TipoTransaccion.QUERY, "modulo": "estadisticas"},
]

# Permisos: qué roles pueden ejecutar qué transacciones
PERMISOS = {
    "miembro": [
        "VER_miembro", "ACTUALIZAR_miembro", "PAGAR_CUOTA", "CREAR_DONACION",
    ],
    "SIMPATIZANTE": [
        "ALTA_SIMPATIZANTE", "SIMPATIZANTE_A_miembro",
    ],
    "PRESIDENTE": [
        "LISTAR_miembroS", "VER_miembro", "ACTUALIZAR_miembro", "ALTA_miembro", "BAJA_miembro",
        "CONFIRMAR_ALTA_miembro", "EXPORTAR_miembroS",
        "VER_AGRUPACIONES", "ACTUALIZAR_AGRUPACION",
        "ENVIAR_EMAIL_miembroS",
        "VER_ESTADISTICAS", "EXPORTAR_INFORME_ANUAL",
        "ASIGNAR_ROL_COORDINADOR", "ASIGNAR_ROL_PRESIDENTE", "ASIGNAR_ROL_TESORERO",
    ],
    "TESORERO": [
        "LISTAR_miembroS", "VER_miembro", "ACTUALIZAR_miembro", "ALTA_miembro", "BAJA_miembro",
        "VER_CUOTAS", "CREAR_CUOTA", "ANOTAR_INGRESO_CUOTA", "VER_TOTALES_CUOTAS",
        "EXPORTAR_CUOTAS", "GESTIONAR_CUOTAS_VIGENTES",
        "VER_DONACIONES", "ANOTAR_INGRESO_DONACION", "ANULAR_DONACION",
        "GESTIONAR_CONCEPTOS_DONACION",
        "VER_REMESAS", "CREAR_REMESA", "GENERAR_SEPA_XML", "ELIMINAR_REMESA",
        "ACTUALIZAR_CUOTAS_REMESA",
        "ENVIAR_AVISO_COBRO",
    ],
    "COORDINADOR": [
        "LISTAR_miembroS", "VER_miembro", "ACTUALIZAR_miembro", "ALTA_miembro", "BAJA_miembro",
        "EXPORTAR_miembroS",
        "ENVIAR_EMAIL_miembroS",
    ],
    "GESTOR_SIMPS": [
        "ENVIAR_EMAIL_SIMPATIZANTES",
    ],
    "Admin": [
        # Admin tiene acceso a todo
        *[t["codigo"] for t in TRANSACCIONES],
    ],
    "MANTENIMIENTO": [
        "CAMBIAR_MODO_SISTEMA", "CIERRE_ANIO",
    ],
}


async def seed_transacciones():
    async with async_session() as db:
        # Crear transacciones
        for tx_data in TRANSACCIONES:
            result = await db.execute(
                select(Transaccion).where(Transaccion.codigo == tx_data["codigo"])
            )
            if not result.scalar_one_or_none():
                tx = Transaccion(**tx_data, activo=True)
                db.add(tx)
                print(f"  + Transaccion: {tx_data['codigo']}")

        await db.commit()
        print("Transacciones completadas.")


async def seed_permisos():
    async with async_session() as db:
        for rol_codigo, tx_codigos in PERMISOS.items():
            # Obtener rol
            result = await db.execute(select(Rol).where(Rol.codigo == rol_codigo))
            rol = result.scalar_one_or_none()
            if not rol:
                print(f"  ! Rol no encontrado: {rol_codigo}")
                continue

            for tx_codigo in tx_codigos:
                # Obtener transacción
                result = await db.execute(
                    select(Transaccion).where(Transaccion.codigo == tx_codigo)
                )
                tx = result.scalar_one_or_none()
                if not tx:
                    continue

                # Verificar si ya existe el permiso
                result = await db.execute(
                    select(RolTransaccion).where(
                        RolTransaccion.rol_id == rol.id,
                        RolTransaccion.transaccion_id == tx.id,
                    )
                )
                if not result.scalar_one_or_none():
                    permiso = RolTransaccion(rol_id=rol.id, transaccion_id=tx.id)
                    db.add(permiso)

            print(f"  + Permisos para: {rol_codigo}")

        await db.commit()
        print("Permisos completados.")


async def main():
    print("=== Seeding Transacciones ===")
    await seed_transacciones()
    print("\n=== Seeding Permisos ===")
    await seed_permisos()


if __name__ == "__main__":
    asyncio.run(main())
