"""Cuentas de acceso demo (sin volcado) para probar cada perfil en staging/demo.

Autónomo e idempotente (por email). Crea una cuenta por perfil, vinculada a un
socio activo existente, y le asigna su rol:

  presidente.demo@siga.test     PRESIDENTE       (ámbito general)
  tesorero.demo@siga.test       TESORERO         (ámbito general)
  secretario.demo@siga.test     SECRETARIO       (ámbito general)
  interventor.demo@siga.test    INTERVENTOR      (ámbito general)
  planificador.demo@siga.test   PLANIFICADOR     (ámbito general) — coordinador de campañas
  coordinador.demo@siga.test    COORDINADOR      (ámbito territorial: una autonómica)

Todas con la misma contraseña DEMO_PASSWORD (cambiar en producción).

Ejecutar:
  docker exec <backend> python -m app.scripts.seeding.seed_demo_usuarios
"""
from __future__ import annotations

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.core.security import hash_password
from app.modules.acceso.models.usuario import Usuario, UsuarioRol
from app.modules.acceso.models.rol import Rol
from app.modules.membresia.models.miembro import Miembro
from app.modules.membresia.models.estado_miembro import EstadoMiembro
from app.modules.core.geografico.direccion import UnidadOrganizativa

DEMO_PASSWORD = "Demo2026!"

# (email, rol_codigo, ámbito): ámbito 'GLOBAL' → agrupacion_id NULL; 'TERRITORIAL' → autonómica
PERFILES = [
    ("presidente.demo@siga.test",   "PRESIDENTE",   "GLOBAL"),
    ("tesorero.demo@siga.test",     "TESORERO",     "GLOBAL"),
    ("secretario.demo@siga.test",   "SECRETARIO",   "GLOBAL"),
    ("interventor.demo@siga.test",  "INTERVENTOR",  "GLOBAL"),
    ("planificador.demo@siga.test", "PLANIFICADOR", "GLOBAL"),
    ("coordinador.demo@siga.test",  "COORDINADOR",  "TERRITORIAL"),
]


async def seed(session: AsyncSession | None = None) -> None:
    own = session is None
    if own:
        session = async_session()
        await session.__aenter__()
    try:
        print("Seed usuarios demo…")
        roles = {r.codigo: r for r in (await session.execute(select(Rol))).scalars().all()}
        # Una agrupación autonómica (hija directa de la raíz) para el ámbito territorial
        raiz_id = await session.scalar(
            select(UnidadOrganizativa.id).where(UnidadOrganizativa.agrupacion_padre_id.is_(None))
        )
        autonomica_id = await session.scalar(
            select(UnidadOrganizativa.id)
            .where(UnidadOrganizativa.agrupacion_padre_id == raiz_id)
            .order_by(UnidadOrganizativa.nombre)
        )
        # Socios activos disponibles para vincular (uno por cuenta)
        estado_alta = (await session.execute(
            select(EstadoMiembro).where(EstadoMiembro.nombre == "Alta")
        )).scalar_one_or_none()
        q = select(Miembro).where(Miembro.eliminado == False)  # noqa: E712
        if estado_alta:
            q = q.where(Miembro.estado_id == estado_alta.id)
        candidatos = list((await session.execute(q.order_by(Miembro.apellido1, Miembro.nombre))).scalars().all())
        usados = set()

        def siguiente_miembro():
            for m in candidatos:
                if m.id not in usados:
                    usados.add(m.id)
                    return m
            return None

        creados = 0
        for email, rol_codigo, ambito in PERFILES:
            rol = roles.get(rol_codigo)
            if not rol:
                print(f"  ⚠ rol {rol_codigo} no existe; omito {email}")
                continue
            usuario = (await session.execute(
                select(Usuario).where(Usuario.email == email)
            )).scalar_one_or_none()
            if usuario is None:
                miembro = siguiente_miembro()
                usuario = Usuario(
                    email=email, password_hash=hash_password(DEMO_PASSWORD),
                    activo=True, miembro_id=miembro.id if miembro else None,
                )
                session.add(usuario)
                await session.flush()
                creados += 1
            # Asignar el rol si no lo tiene ya
            agrup = None if ambito == "GLOBAL" else autonomica_id
            ya_rol = await session.scalar(
                select(UsuarioRol.id).where(
                    UsuarioRol.usuario_id == usuario.id, UsuarioRol.rol_id == rol.id
                )
            )
            if not ya_rol:
                session.add(UsuarioRol(
                    usuario_id=usuario.id, rol_id=rol.id, agrupacion_id=agrup, activo=True,
                ))
        await session.commit()
        print(f"  usuarios demo: +{creados} cuentas (contraseña: {DEMO_PASSWORD})")
        print("Listo.")
    finally:
        if own:
            await session.__aexit__(None, None, None)


if __name__ == "__main__":
    asyncio.run(seed())
