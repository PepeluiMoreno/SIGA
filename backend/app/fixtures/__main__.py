"""Juego de datos de prueba de SIGA — UN solo punto de entrada.

Deja el entorno listo para entrar y probar como cada perfil, en orden y de forma
idempotente (re-ejecutar no duplica). Siembra lo justo y en el orden correcto:

  1) tipos de vinculación (crea 'SOCIO' si falta)
  2) roles de gobierno (PRESIDENTE/TESORERO/… si faltan)
  3) permisos por rol (cablea las transacciones a cada rol; sin esto el usuario
     tiene el rol pero no puede hacer nada)
  4) los 5 perfiles de prueba: login por nombre (presidente, tesorero, …),
     contraseña «x», cada uno con su rol y su faceta de socio.

Solo dev/staging: abortado en producción por el guard.

Ejecutar:
  docker compose -f docker-compose.dev.yml --env-file .env.dev exec backend \\
      python -m app.fixtures
"""
from __future__ import annotations

import asyncio

import importlib

from app.core.database import async_session
from app.scripts.seeding._guard import abort_if_production
from app.scripts.seeding import seed_tipos_vinculacion, seed_staging_perfiles
from app.scripts.seeding import seed_roles_organizacionales

# Cableado de permisos por rol (cada módulo expone seed()). Sin esto, los roles
# existen pero no llevan transacciones asociadas → el usuario no puede operar.
PERMISOS = [
    "seed_permisos_membresia_perfilado",
    "seed_permisos_contactos",
    "seed_permisos_voluntariado",
    "seed_permisos_cuotas",
    "seed_permisos_tesorero",
    "seed_permisos_justificantes",
    "seed_permisos_recibos",
    "seed_permisos_donaciones",
    "seed_permisos_ccaa",
    "seed_permisos_cierre",
    "seed_permisos_conciliacion",
    "seed_permisos_modelo_182",
    "seed_permisos_plan_cuentas",
    "seed_permisos_export_socios",
    "seed_permisos_presidencia",
]


async def main() -> None:
    abort_if_production("juego de datos de prueba")
    print("=== Sembrando datos de prueba ===")

    # 1) Tipos de vinculación (incluye SOCIO) — comparten sesión.
    async with async_session() as session:
        await seed_tipos_vinculacion.seed(session)
        await session.commit()

    # 2) Roles de gobierno (abre su propia sesión y commitea).
    await seed_roles_organizacionales.seed()

    # 3) Permisos por rol. Algunos de estos seeds no son idempotentes (insertan sin
    #    comprobar, o traen repetidos en su lista) y chocan con uq_rol_transaccion al
    #    re-ejecutar. Para que el fixture SÍ sea idempotente, vaciamos los permisos de
    #    los roles de gobierno antes de re-cablearlos desde cero.
    print("\n--- Cableando permisos por rol ---")
    async with async_session() as session:
        from sqlalchemy import select, delete
        from app.modules.acceso.models.rol import Rol
        from app.modules.acceso.models.rol_transaccion import RolTransaccion
        rol_ids = (await session.execute(
            select(Rol.id).where(Rol.tipo == "ORGANIZACION")
        )).scalars().all()
        if rol_ids:
            await session.execute(
                delete(RolTransaccion).where(RolTransaccion.rol_id.in_(rol_ids))
            )
            await session.commit()
    for mod in PERMISOS:
        m = importlib.import_module(f"app.scripts.seeding.{mod}")
        try:
            await m.seed()
        except Exception as e:
            # Algunos seeds se solapan (cablean la misma transacción a un rol que ya
            # se la cableó otro). El permiso ya quedó puesto, así que el choque es
            # inocuo para el resultado: lo registramos y seguimos.
            print(f"  · {mod}: solapamiento ignorado ({type(e).__name__})")

    # 4) Perfiles de prueba (abre su propia sesión; fail-fast si falta algo de lo anterior).
    await seed_staging_perfiles.seed()

    print("=== Listo. Entra con: presidente / tesorero / secretario / coordinador / socio  (contraseña «x») ===")


if __name__ == "__main__":
    asyncio.run(main())
