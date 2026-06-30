"""Cuentas de acceso por PERFIL para staging/demo (autónomo e idempotente).

Crea un juego de usuarios ficticios, uno por cada perfil que se quiere poder
probar de un vistazo, todos con la MISMA contraseña sencilla (por defecto "x").
Cada usuario:

  - tiene un Contacto (persona física) con nombre reconocible ("Presidenta
    Demo", "Tesorero Demo", …) para identificarlo en el directorio,
  - una cuenta Usuario ligada a ese contacto (login por email),
  - su vinculación de socio (Vinculacion SOCIO + Socio) — todos son socios,
  - y, salvo el "socio normal", su rol de gobierno (UsuarioRol).

Se entra SOLO con el nombre (el username, p. ej. «presidente») o con el email,
indistintamente: el login acepta ambos. username = el rol en minúscula.

Perfiles sembrados (username · email · rol):

  presidente   presidente@siga.test     PRESIDENTE   (ámbito general)
  secretario   secretario@siga.test     SECRETARIO   (ámbito general)
  tesorero     tesorero@siga.test       TESORERO     (ámbito general)
  coordinador  coordinador@siga.test    COORDINADOR  (ámbito territorial: una autonómica)
  socio        socio@siga.test          —            (socio normal, sin rol de gobierno)

Idempotente: identifica cada usuario por email y cada contacto por su
numero_documento ("PERFIL-<ROL>"). Re-ejecutar no duplica.

ADVERTENCIA: contraseña trivial. SOLO para entornos de prueba (staging/demo),
NUNCA en producción.

Ejecutar:
  docker compose -f docker-compose.dev.yml --env-file .env.dev exec backend \\
      python -m app.scripts.seeding.seed_staging_perfiles
"""
from __future__ import annotations

import asyncio
import os
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.core.security import hash_password
from app.modules.acceso.models.usuario import Usuario, UsuarioRol
from app.modules.acceso.models.rol import Rol
from app.modules.membresia.models.contacto import Contacto
from app.modules.membresia.models.vinculacion import Vinculacion, Socio
from app.modules.membresia.models.tipo_vinculacion import TipoVinculacion
from app.modules.core.geografico.direccion import UnidadOrganizativa

# Contraseña común a todas las cuentas demo. Configurable por env, "x" por defecto.
PASSWORD = os.getenv("SIGA_STAGING_PASSWORD", "x")

# (username, email, nombre, apellido1, rol_codigo|None, ámbito): ámbito 'GLOBAL'
# → sin agrupación; 'TERRITORIAL' → una autonómica. rol None = socio normal.
# El username (el rol en minúscula) permite entrar SOLO con el nombre, p. ej.
# «presidente» / «x» — el login acepta indistintamente email o username.
PERFILES = [
    ("presidente",  "presidente@siga.test",  "Presidenta",  "Demo", "PRESIDENTE",  "GLOBAL"),
    ("secretario",  "secretario@siga.test",  "Secretario",  "Demo", "SECRETARIO",  "GLOBAL"),
    ("tesorero",    "tesorero@siga.test",    "Tesorero",    "Demo", "TESORERO",    "GLOBAL"),
    ("coordinador", "coordinador@siga.test", "Coordinador", "Demo", "COORDINADOR", "TERRITORIAL"),
    ("socio",       "socio@siga.test",       "Socio",       "Demo", None,          "GLOBAL"),
]


async def seed(session: AsyncSession | None = None) -> None:
    from app.scripts.seeding._guard import abort_if_production
    abort_if_production("seeding de perfiles de prueba")
    own = session is None
    if own:
        session = async_session()
        await session.__aenter__()
    try:
        from app.scripts.seeding._guard import require
        print("Seed perfiles staging…")

        roles = {r.codigo: r for r in (await session.execute(select(Rol))).scalars().all()}
        tipo_socio = (await session.execute(
            select(TipoVinculacion).where(TipoVinculacion.codigo == "SOCIO")
        )).scalar_one_or_none()

        # Prerrequisitos duros: sin ellos los perfiles quedarían a medias (sin vinculación
        # de socio o sin rol). Fail-fast en vez de degradar en silencio.
        require(tipo_socio is not None,
                "el TipoVinculacion 'SOCIO'", "seed_tipos_vinculacion")
        roles_necesarios = {p[4] for p in PERFILES if p[4]}
        faltan_roles = roles_necesarios - set(roles)
        require(not faltan_roles,
                f"los roles de gobierno {sorted(faltan_roles)}", "seed_roles_organizacionales")

        # Una autonómica (hija directa de la raíz) para el ámbito territorial del coordinador.
        raiz_id = await session.scalar(
            select(UnidadOrganizativa.id).where(UnidadOrganizativa.agrupacion_padre_id.is_(None))
        )
        autonomica_id = None
        if raiz_id:
            autonomica_id = await session.scalar(
                select(UnidadOrganizativa.id)
                .where(UnidadOrganizativa.agrupacion_padre_id == raiz_id)
                .order_by(UnidadOrganizativa.nombre)
            )

        creados_usr = 0
        creados_ctc = 0
        n_socio = 0
        for username, email, nombre, apellido1, rol_codigo, ambito in PERFILES:
            doc = f"PERFIL-{(rol_codigo or 'SOCIO')}"

            # 1) Contacto (persona física), idempotente por numero_documento.
            contacto = (await session.execute(
                select(Contacto).where(Contacto.numero_documento == doc)
            )).scalar_one_or_none()
            if contacto is None:
                contacto = Contacto(
                    tipo="PERSONA_FISICA",
                    nombre=nombre,
                    apellido1=apellido1,
                    numero_documento=doc,
                    email=email,
                    agrupacion_id=autonomica_id if ambito == "TERRITORIAL" else None,
                    activo=True,
                )
                session.add(contacto)
                await session.flush()
                creados_ctc += 1

            # 2) Vinculación de socio (todos son socios), idempotente.
            if tipo_socio is not None:
                tiene_socio = await session.scalar(
                    select(Vinculacion.id).where(
                        Vinculacion.contacto_id == contacto.id,
                        Vinculacion.tipo_vinculacion_id == tipo_socio.id,
                    )
                )
                if not tiene_socio:
                    n_socio += 1
                    vinc = Vinculacion(
                        contacto_id=contacto.id,
                        tipo_vinculacion_id=tipo_socio.id,
                        fecha_inicio=date(2024, 1, 1),
                        estado="activa",
                        agrupacion_id=contacto.agrupacion_id,
                    )
                    session.add(vinc)
                    await session.flush()
                    session.add(Socio(
                        vinculacion_id=vinc.id,
                        numero_socio=f"DEMO-{doc}",
                        cuota_mensual=10,
                    ))

            # 3) Usuario ligado al contacto, idempotente por email.
            usuario = (await session.execute(
                select(Usuario).where(Usuario.email == email)
            )).scalar_one_or_none()
            if usuario is None:
                usuario = Usuario(
                    username=username,
                    email=email,
                    password_hash=hash_password(PASSWORD),
                    activo=True,
                    contacto_id=contacto.id,
                )
                session.add(usuario)
                await session.flush()
                creados_usr += 1
            else:
                # Reafirma username, contraseña y vínculo en cada corrida (cómodo en demo).
                usuario.username = username
                usuario.password_hash = hash_password(PASSWORD)
                usuario.contacto_id = contacto.id
                usuario.activo = True

            # 4) Rol de gobierno (salvo socio normal), idempotente.
            # El rol existe seguro: lo garantiza el require() de prerrequisitos.
            if rol_codigo:
                rol = roles[rol_codigo]
                agrup = autonomica_id if ambito == "TERRITORIAL" else None
                ya_rol = await session.scalar(
                    select(UsuarioRol.id).where(
                        UsuarioRol.usuario_id == usuario.id,
                        UsuarioRol.rol_id == rol.id,
                    )
                )
                if not ya_rol:
                    session.add(UsuarioRol(
                        usuario_id=usuario.id, rol_id=rol.id,
                        agrupacion_id=agrup, activo=True,
                    ))

        await session.commit()
        print(f"  contactos: +{creados_ctc} · usuarios: +{creados_usr} · socios: +{n_socio}")
        print(f"  contraseña de todas las cuentas: «{PASSWORD}»")
        print("  entra con el nombre (o el email): " + ", ".join(p[0] for p in PERFILES))
        print("Listo.")
    finally:
        if own:
            await session.__aexit__(None, None, None)


if __name__ == "__main__":
    asyncio.run(seed())
