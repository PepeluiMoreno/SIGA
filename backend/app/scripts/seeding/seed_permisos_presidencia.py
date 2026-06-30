"""Asigna las transacciones PRESIDENCIA_* a los roles PRESIDENTE y VICEPRESIDENTE.

El cuadro de mando de gobierno (módulo presidencia) lo ven por defecto la
presidencia y la vicepresidencia. Idempotente: solo inserta los enlaces que aún
no existan.

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_permisos_presidencia
"""
import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select

from app.core.database import async_session
from app.modules.acceso.models.rol import Rol
from app.modules.acceso.models.transaccion import Transaccion
from app.modules.acceso.models.rol_transaccion import RolTransaccion


TRANSACCIONES_PRESIDENCIA = [
    "PRESIDENCIA_CUADRO_MANDO_VER",
    "PRESIDENCIA_MANDATO_LISTAR",
    "PRESIDENCIA_ACUERDO_SEGUIMIENTO_VER",
]

ROLES_DESTINO = ["PRESIDENTE", "VICEPRESIDENTE"]


async def seed():
    async with async_session() as session:
        trans_by_codigo = {
            t.codigo: t for t in (await session.execute(
                select(Transaccion).where(Transaccion.codigo.in_(TRANSACCIONES_PRESIDENCIA))
            )).scalars().all()
        }
        faltan = set(TRANSACCIONES_PRESIDENCIA) - set(trans_by_codigo)
        if faltan:
            print(f"  ⚠ transacciones no encontradas (¿falta sincronizar el catálogo?): {sorted(faltan)}")

        now = datetime.utcnow()
        total = 0
        for codigo_rol in ROLES_DESTINO:
            rol = (await session.execute(
                select(Rol).where(Rol.codigo == codigo_rol)
            )).scalars().first()
            if not rol:
                print(f"  ⚠ rol {codigo_rol} no existe; se omite. Ejecuta antes seed_roles_organizacionales.")
                continue

            existentes = {row[0] for row in (await session.execute(
                select(RolTransaccion.transaccion_id).where(RolTransaccion.rol_id == rol.id)
            )).all()}

            creadas = 0
            for codigo in TRANSACCIONES_PRESIDENCIA:
                t = trans_by_codigo.get(codigo)
                if not t or t.id in existentes:
                    continue
                session.add(RolTransaccion(
                    id=uuid.uuid4(), rol_id=rol.id, transaccion_id=t.id,
                    fecha_creacion=now, eliminado=False,
                ))
                creadas += 1
            total += creadas
            print(f"  ✓ {codigo_rol}: +{creadas} transacciones de presidencia enlazadas.")

        await session.commit()
        print(f"Permisos de presidencia: +{total} enlaces en total.")


if __name__ == "__main__":
    asyncio.run(seed())
