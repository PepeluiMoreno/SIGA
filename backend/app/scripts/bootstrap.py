"""Bootstrap idempotente al arrancar el backend.

Sincroniza el catálogo de transacciones desde initial_data/transacciones.json,
asegura el rol SUPERADMIN con todas las transacciones asignadas y, si las
variables de entorno INITIAL_ADMIN_EMAIL e INITIAL_ADMIN_PASSWORD están
definidas, crea el usuario administrador inicial vinculado a SUPERADMIN.

Se invoca desde el CMD del Dockerfile tras `alembic upgrade head` y antes
de arrancar uvicorn. Es idempotente: si los registros ya existen no hace
nada destructivo.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import uuid

from sqlalchemy import select

from app.core.database import async_session
from app.core.security import hash_password, verify_password
from app.modules.acceso.models.rol import Rol, TipoRol
from app.modules.acceso.models.rol_transaccion import RolTransaccion
from app.modules.acceso.models.transaccion import Transaccion
from app.modules.acceso.models.usuario import Usuario, UsuarioRol
from app.modules.configuracion.models.configuracion import Configuracion


INITIAL_DATA_DIR = Path(__file__).resolve().parents[2] / "initial_data"
SUPERADMIN_CODE = "SUPERADMIN"


async def sync_transacciones(session) -> dict[str, Transaccion]:
    """Inserta o actualiza transacciones desde transacciones.json. Idempotente."""
    file_path = INITIAL_DATA_DIR / "transacciones.json"
    if not file_path.exists():
        print(f"[bootstrap] {file_path} no existe; se omite sync de transacciones")
        return {}

    data = json.loads(file_path.read_text(encoding="utf-8"))
    by_codigo: dict[str, Transaccion] = {}

    for entry in data["transacciones"]:
        codigo = entry["codigo"]
        existing = (
            await session.execute(
                select(Transaccion).where(Transaccion.codigo == codigo)
            )
        ).scalar_one_or_none()

        if existing is None:
            t = Transaccion(
                codigo=codigo,
                nombre=entry["nombre"],
                descripcion=entry.get("descripcion"),
                modulo=entry["modulo"],
                tipo=entry["tipo"],
                activa=entry.get("activa", True),
                sistema=entry.get("sistema", True),
            )
            session.add(t)
            by_codigo[codigo] = t
        else:
            existing.nombre = entry["nombre"]
            existing.descripcion = entry.get("descripcion")
            existing.modulo = entry["modulo"]
            existing.tipo = entry["tipo"]
            existing.activa = entry.get("activa", True)
            existing.sistema = entry.get("sistema", True)
            by_codigo[codigo] = existing

    await session.flush()
    return by_codigo


async def ensure_superadmin(
    session,
    transacciones: dict[str, Transaccion],
) -> Rol:
    """Asegura el rol SUPERADMIN y lo enlaza a todas las transacciones."""
    rol = (
        await session.execute(
            select(Rol).where(Rol.codigo == SUPERADMIN_CODE)
        )
    ).scalar_one_or_none()

    if rol is None:
        rol = Rol(
            codigo=SUPERADMIN_CODE,
            nombre="Super Administrador",
            descripcion="Acceso total al sistema (rol del sistema, no eliminable).",
            tipo=TipoRol.SISTEMA,
            nivel=100,
            es_territorial=False,
            sistema=True,
            activo=True,
        )
        session.add(rol)
        await session.flush()

    existing_links = {
        rt.transaccion_id
        for rt in (
            await session.execute(
                select(RolTransaccion).where(RolTransaccion.rol_id == rol.id)
            )
        ).scalars()
    }

    added = 0
    now = datetime.utcnow()
    for trans in transacciones.values():
        if trans.id not in existing_links:
            session.add(
                RolTransaccion(
                    rol_id=rol.id,
                    transaccion_id=trans.id,
                    fecha_creacion=now,
                    eliminado=False,
                )
            )
            added += 1
    await session.flush()
    if added:
        print(f"[bootstrap] SUPERADMIN: +{added} transacciones enlazadas")
    return rol


async def ensure_admin_user(session, superadmin: Rol) -> Optional[Usuario]:
    """Crea (si procede) el usuario admin inicial. Requiere variables de entorno."""
    email = os.getenv("INITIAL_ADMIN_EMAIL")
    password = os.getenv("INITIAL_ADMIN_PASSWORD")
    if not email or not password:
        print(
            "[bootstrap] INITIAL_ADMIN_EMAIL/INITIAL_ADMIN_PASSWORD no definidas; "
            "omito creación de admin inicial"
        )
        return None

    existing = (
        await session.execute(select(Usuario).where(Usuario.email == email))
    ).scalar_one_or_none()
    if existing:
        updated = False

        if not existing.activo:
            existing.activo = True
            updated = True

        if not existing.password_hash or not existing.password_hash.startswith("$2"):
            existing.password_hash = hash_password(password)
            updated = True

        has_superadmin = (
            await session.execute(
                select(UsuarioRol).where(
                    UsuarioRol.usuario_id == existing.id,
                    UsuarioRol.rol_id == superadmin.id,
                )
            )
        ).scalar_one_or_none()
        if has_superadmin is None:
            session.add(
                UsuarioRol(
                    usuario_id=existing.id,
                    rol_id=superadmin.id,
                    fecha_creacion=datetime.utcnow(),
                    eliminado=False,
                )
            )
            updated = True

        # Si el secret cambia, el siguiente arranque sincroniza la contraseña.
        if password and not verify_password(password, existing.password_hash):
            existing.password_hash = hash_password(password)
            updated = True

        if updated:
            await session.flush()
            print(f"[bootstrap] Usuario admin sincronizado: {email}")
        return existing

    usuario = Usuario(
        email=email,
        password_hash=hash_password(password),
        activo=True,
    )
    session.add(usuario)
    await session.flush()

    session.add(
        UsuarioRol(
            usuario_id=usuario.id,
            rol_id=superadmin.id,
            fecha_creacion=datetime.utcnow(),
            eliminado=False,
        )
    )
    await session.flush()
    print(f"[bootstrap] Usuario admin creado: {email}")
    return usuario



_ORG_DEFAULTS = [
    ('org.nombre',               'string', ''),
    ('org.nif',                  'string', ''),
    ('org.tipo_entidad',         'string', 'ASOCIACION'),
    ('org.contabilidad_compleja','bool',   'false'),
    ('org.sede_social',          'string', ''),
    ('org.localidad',            'string', ''),
    ('org.cp',                   'string', ''),
    ('org.provincia',            'string', ''),
    ('org.pais',                 'string', 'España'),
    ('org.telefono',             'string', ''),
    ('org.email',                'string', ''),
    ('org.web',                  'string', ''),
    ('org.rrss.twitter',         'string', ''),
    ('org.rrss.facebook',        'string', ''),
    ('org.rrss.instagram',       'string', ''),
    ('org.rrss.linkedin',        'string', ''),
    ('org.rrss.youtube',         'string', ''),
    ('org.logo',                       'string', ''),
    ('org.implantacion_geografica',     'string', ''),
    ('org.tipo_agrupacion_territorial', 'string', ''),
    ('org.multiterritorial',            'bool',   'false'),
    # Autenticación
    ('auth.modo',                       'string', 'LOCAL'),   # LOCAL | AUTHELIA | OIDC
    ('auth.authelia_url',               'string', ''),
    ('auth.oidc_issuer',                'string', ''),
    # SMTP (usado en modo LOCAL para envío de emails)
    ('smtp.host',                       'string', ''),
    ('smtp.port',                       'string', '587'),
    ('smtp.usuario',                    'string', ''),
    ('smtp.password',                   'string', ''),
    ('smtp.from',                       'string', ''),
    ('smtp.tls',                        'bool',   'true'),
    ('smtp.ssl',                        'bool',   'false'),
]


async def ensure_parametros_organizacion(session) -> None:
    """Crea las claves org.* con valores vacíos si no existen. Idempotente."""
    existing = {
        c.clave
        for c in (
            await session.execute(
                select(Configuracion).where(Configuracion.grupo == 'organizacion')
            )
        ).scalars()
    }
    added = 0
    now = datetime.utcnow()
    for clave, tipo_dato, valor_default in _ORG_DEFAULTS:
        if clave not in existing:
            session.add(Configuracion(
                id=uuid.uuid4(),
                clave=clave,
                valor=valor_default,
                tipo_dato=tipo_dato,
                grupo='organizacion',
                modificable=True,
                fecha_creacion=now,
            ))
            added += 1
    if added:
        await session.flush()
        print(f"[bootstrap] Parámetros organización: +{added} claves creadas")


async def main() -> None:
    async with async_session() as session:
        try:
            transacciones = await sync_transacciones(session)
            print(f"[bootstrap] Transacciones sincronizadas: {len(transacciones)}")
            superadmin = await ensure_superadmin(session, transacciones)
            print(f"[bootstrap] Rol SUPERADMIN listo (id={superadmin.id})")
            await ensure_admin_user(session, superadmin)
            await ensure_parametros_organizacion(session)
            await session.commit()
        except Exception:
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
