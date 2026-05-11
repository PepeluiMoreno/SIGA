"""Crea usuarios de aplicación para miembros con cargos en el volcado MySQL.

Extrae del dump los miembros que tienen rol de cargo directivo o coordinación
(Presidente, Tesorero, Coordinador) y disponen de email, los empareja con los
Miembro ya importados en SIGA por email, y crea un Usuario vinculado con el
rol PLANIFICADOR asignado.

Criterios de inclusión:
  - ESTADO = 'alta' en USUARIO
  - Tienen al menos un rol de cargo en USUARIOTIENEROL (CODROL 3, 4, 5, 6, 7)
    o aparecen en COORDINAAREAGESTIONAGRUP
  - EMAIL no nulo en MIEMBRO
  - Se puede emparejar con un Miembro SIGA por email

Uso:
    docker exec <backend> python -m app.scripts.seeding.seed_usuarios_volcado
"""
import asyncio
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import select

from app.core.database import async_session
from app.core.security import hash_password
from app.modules.acceso.models.rol import Rol
from app.modules.acceso.models.usuario import Usuario, UsuarioRol
from app.modules.membresia.models.miembro import Miembro


DUMP_FILE = "/tmp/europa_laica_dump.sql"

# Códigos de rol que equivalen a un cargo directivo / coordinación
CODROS_CARGO = {"3", "4", "5", "6", "7"}   # Presidente, Secretario, Tesorero, Coordinador, Vocal


# ---------------------------------------------------------------------------
# Parser SQL (mismo patrón que el resto de seeds)
# ---------------------------------------------------------------------------

def _parse_table(table_name: str, content: str) -> list[list]:
    rows: list = []
    pattern = re.compile(
        rf"INSERT INTO `{re.escape(table_name)}`\s*\(.*?\)\s*VALUES\s*",
        re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(content):
        i = match.end()
        while i < len(content):
            if content[i] == "(":
                j = _paren(content, i)
                rows.append(_split(content[i + 1: j]))
                i = j + 1
                while i < len(content) and content[i] in " ,;\n\r\t":
                    i += 1
            else:
                break
    return rows


def _paren(text: str, start: int) -> int:
    depth = 0
    j = start
    while j < len(text):
        ch = text[j]
        if ch == "'" and depth <= 0:
            depth = 1
        elif ch == "'" and depth == 1:
            if j + 1 < len(text) and text[j + 1] == "'":
                j += 2
                continue
            depth = 0
        elif ch == ")" and depth == 0:
            return j
        j += 1
    return len(text) - 1


def _split(inner: str) -> list:
    values: list[str] = []
    current = ""
    in_string = False
    i = 0
    while i < len(inner):
        ch = inner[i]
        if in_string:
            if ch == "'" and i + 1 < len(inner) and inner[i + 1] == "'":
                current += "'"
                i += 2
                continue
            elif ch == "'":
                in_string = False
            else:
                current += ch
        else:
            if ch == "'":
                in_string = True
            elif ch == ",":
                values.append(current.strip())
                current = ""
            else:
                current += ch
        i += 1
    if current.strip():
        values.append(current.strip())
    result = []
    for v in values:
        if v in ("NULL", "null", ""):
            result.append(None)
        elif v.startswith("'") and v.endswith("'"):
            result.append(v[1:-1].replace("''", "'"))
        else:
            result.append(v)
    return result


# ---------------------------------------------------------------------------
# Lógica principal
# ---------------------------------------------------------------------------

async def seed():
    print("\n" + "=" * 60)
    print("SEED USUARIOS VOLCADO (miembros con cargos)")
    print("=" * 60)

    dump_path = Path(DUMP_FILE)
    if not dump_path.exists():
        print(f"  [ERROR] {DUMP_FILE} no encontrado")
        return

    content = dump_path.read_text(encoding="utf-8", errors="replace")

    # --- Parsear tablas ---
    usuario_rows = _parse_table("USUARIO", content)
    miembro_rows = _parse_table("MIEMBRO", content)
    rol_rows = _parse_table("USUARIOTIENEROL", content)
    coord_rows = _parse_table("COORDINAAREAGESTIONAGRUP", content)

    print(f"  USUARIO: {len(usuario_rows)} filas")
    print(f"  MIEMBRO: {len(miembro_rows)} filas")
    print(f"  USUARIOTIENEROL: {len(rol_rows)} filas")
    print(f"  COORDINAAREAGESTIONAGRUP: {len(coord_rows)} filas")

    # --- CODUSERs con cargo ---
    codusers_cargo: set[str] = set()
    for row in rol_rows:
        if len(row) >= 2 and str(row[1]).strip() in CODROS_CARGO:
            codusers_cargo.add(str(row[0]).strip())
    for row in coord_rows:
        if len(row) >= 1:
            codusers_cargo.add(str(row[0]).strip())
    print(f"\n  CODUSERs con cargo: {len(codusers_cargo)}")

    # --- Índice de USUARIO por CODUSER ---
    usuario_by_coduser: dict[str, dict] = {}
    for row in usuario_rows:
        if len(row) >= 4:
            coduser = str(row[0]).strip()
            estado = str(row[3]).strip().lower() if row[3] else ""  # col: CODUSER,USUARIO,PASSUSUARIO,ESTADO
            usuario_by_coduser[coduser] = {"estado": estado}

    # --- Índice email → CODUSER desde MIEMBRO ---
    email_by_coduser: dict[str, str] = {}
    for row in miembro_rows:
        if len(row) >= 16:
            coduser = str(row[0]).strip()
            email = str(row[15]).strip().lower() if row[15] else None
            if email and "@" in email:
                email_by_coduser[coduser] = email

    # --- Candidatos: cargo + alta + email ---
    candidatos: list[tuple[str, str]] = []  # (coduser, email)
    for coduser in codusers_cargo:
        u = usuario_by_coduser.get(coduser)
        if u is None:
            continue
        if "alta" not in u["estado"]:
            continue
        email = email_by_coduser.get(coduser)
        if not email:
            continue
        candidatos.append((coduser, email))

    print(f"  Candidatos (cargo+alta+email): {len(candidatos)}")

    # --- Procesar en base de datos ---
    async with async_session() as session:
        # Rol PLANIFICADOR
        planificador = (await session.execute(
            select(Rol).where(Rol.codigo == "PLANIFICADOR")
        )).scalar_one_or_none()
        if planificador is None:
            print("  [ERROR] Rol PLANIFICADOR no encontrado. Ejecuta bootstrap primero.")
            return

        # Índice Miembro por email
        miembros_siga = (await session.execute(select(Miembro))).scalars().all()
        miembro_by_email: dict[str, Miembro] = {
            m.email.lower(): m for m in miembros_siga if m.email
        }

        # Índice Usuario existente por email
        usuarios_siga = (await session.execute(select(Usuario))).scalars().all()
        usuario_by_email: dict[str, Usuario] = {
            u.email.lower(): u for u in usuarios_siga if u.email
        }

        creados = 0
        vinculados = 0
        saltados = 0
        now = datetime.utcnow()

        for coduser, email in candidatos:
            miembro = miembro_by_email.get(email)
            if miembro is None:
                print(f"  [SKIP] {email}: sin Miembro SIGA")
                saltados += 1
                continue

            # Obtener o crear Usuario
            usuario = usuario_by_email.get(email)
            if usuario is None:
                usuario = Usuario(
                    email=email,
                    password_hash=hash_password("CAMBIAME"),
                    activo=True,
                    fecha_creacion=now,
                )
                session.add(usuario)
                await session.flush()
                usuario_by_email[email] = usuario
                creados += 1
                print(f"  [CREAR] Usuario {email}")
            else:
                print(f"  [EXISTE] Usuario {email}")

            # Vincular miembro_id si no está ya vinculado
            if usuario.miembro_id is None and miembro.id is not None:
                # Verificar que el miembro no tiene otro usuario
                other = (await session.execute(
                    select(Usuario).where(Usuario.miembro_id == miembro.id)
                )).scalar_one_or_none()
                if other is None or other.id == usuario.id:
                    usuario.miembro_id = miembro.id
                    vinculados += 1

            # Asignar PLANIFICADOR si no lo tiene ya
            existing_rol = (await session.execute(
                select(UsuarioRol).where(
                    UsuarioRol.usuario_id == usuario.id,
                    UsuarioRol.rol_id == planificador.id,
                )
            )).scalar_one_or_none()
            if existing_rol is None:
                session.add(UsuarioRol(
                    usuario_id=usuario.id,
                    rol_id=planificador.id,
                    fecha_creacion=now,
                    eliminado=False,
                ))

        await session.commit()
        print(f"\n" + "-" * 60)
        print(f"  Usuarios creados:  {creados}")
        print(f"  Miembro vinculado: {vinculados}")
        print(f"  Saltados:          {saltados}")
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(seed())
