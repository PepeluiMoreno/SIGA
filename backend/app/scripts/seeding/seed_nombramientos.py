"""Seed de nombramientos históricos (cargos) desde el dump MySQL.

Mapea:
  - ROL + USUARIOTIENEROL → UsuarioRol + HistorialNombramiento
  - COORDINAAREAGESTIONAGRUP → HistorialNombramiento (rol COORDINADOR)
  - MIEMBRO.OBSERVACIONES (que contenga "junta directiva") → HistorialNombramiento

Se ejecuta via:
    docker exec <backend-container> python -m app.scripts.seeding.seed_nombramientos
"""
import asyncio
import re
import uuid
from datetime import date
from pathlib import Path
from typing import Optional

from sqlalchemy import select

from app.core.database import async_session
from app.modules.acceso.models.rol import Rol, TipoRol
from app.modules.acceso.models.usuario import Usuario, UsuarioRol
from app.modules.membresia.models.historial_nombramiento import HistorialNombramiento
from app.modules.membresia.models.miembro import Miembro
from app.modules.membresia.models.junta import JuntaDirectiva
from app.modules.core.geografico.agrupacion_territorial_view import AgrupacionTerritorial


DUMP_FILE = "/tmp/europa_laica_dump.sql"

# Mapeo codrol (MySQL) → codigo (SIGA Rol)
ROL_MAP = {
    "3": "PRESIDENTE",   # Presidente
    "4": "SECRETARIO",  # Secretario
    "5": "TESORERO",   # Tesorero
    "6": "COORDINADOR", # Coordinador
    "7": "VOCAL",       # Vocal
}

# Mapeo coduser → usuario_id (por email)
EMAIL_MAP: dict[str, uuid.UUID] = {}
# Mapeo coduser → miembro_id
MIEMBRO_MAP: dict[str, uuid.UUID] = {}
# Mapeo codagrupacion → agrupacion_id
AGRUPACION_MAP: dict[str, uuid.UUID] = {}


def parse_mysql_table(table_name: str, content: str) -> list:
    """Extrae todas las filas INSERT de una tabla del dump MySQL."""
    rows: list = []
    pattern = re.compile(
        rf"INSERT INTO `{re.escape(table_name)}`\s*\(.*?\)\s*VALUES\s*",
        re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(content):
        i = match.end()
        while i < len(content):
            if content[i] == "(":
                j = _find_matching_paren(content, i)
                inner = content[i + 1 : j]
                rows.append(_split_values(inner))
                i = j + 1
                while i < len(content) and content[i] in " ,;\n\r\t":
                    i += 1
            else:
                break
    return rows


def _find_matching_paren(text: str, start: int) -> int:
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


def _split_values(inner: str) -> list:
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
    return values


def _parse_date(val: Optional[str]) -> Optional[date]:
    """MySQL date → date object o None."""
    if not val or val.startswith("0000-00-00"):
        return None
    try:
        return date.fromisoformat(val[:10])
    except (ValueError, TypeError):
        return None


async def seed():
    print("\n" + "=" * 60)
    print("SEED NOMBRAMIENTOS (desde volcado MySQL)")
    print("=" * 60)

    dump_path = Path(DUMP_FILE)
    if not dump_path.exists():
        print(f"  [ERROR] {DUMP_FILE} no encontrado")
        return

    content = dump_path.read_text(encoding="utf-8", errors="replace")

    # --- Cargar mapeos ---
    async with async_session() as session:
        # Usuarios por email
        users = (await session.execute(select(Usuario))).scalars().all()
        for u in users:
            EMAIL_MAP[u.email.lower()] = u.id

        # Miembros por email (para mapear coduser → miembro_id)
        miembros = (await session.execute(select(Miembro))).scalars().all()
        for m in miembros:
            if m.email:
                MIEMBRO_MAP[m.email.lower()] = m.id

        # Agrupaciones por código (nombre_corto)
        agrupaciones = (await session.execute(select(AgrupacionTerritorial))).scalars().all()
        for a in agrupaciones:
            if a.nombre_corto:
                AGRUPACION_MAP[a.nombre_corto] = a.id

        # Roles organizacionales
        roles = (await session.execute(
            select(Rol).where(Rol.tipo == TipoRol.ORGANIZACION)
        )).scalars().all()
        rol_by_codigo: dict[str, Rol] = {r.codigo: r for r in roles}

        print(f"\n  Usuarios: {len(users)}")
        print(f"  Miembros: {len(miembros)}")
        print(f"  Agrupaciones: {len(agrupaciones)}")
        print(f"  Roles ORGANIZACION: {len(roles)}")

        # --- Parsear tablas del dump ---
        rol_rows = parse_mysql_table("USUARIOTIENEROL", content)
        coord_rows = parse_mysql_table("COORDINAAREAGESTIONAGRUP", content)
        miembro_rows = parse_mysql_table("MIEMBRO", content)

        print(f"\n  USUARIOTIENEROL: {len(rol_rows)} filas")
        print(f"  COORDINAAREAGESTIONAGRUP: {len(coord_rows)} filas")
        print(f"  MIEMBRO (para observaciones): {len(miembro_rows)} filas")

        # --- Procesar USUARIOTIENEROL (asignación de roles) ---
        nombramientos_creados = 0
        nombramientos_saltados = 0

        print("\n--- Procesando USUARIOTIENEROL ---")

        for row in rol_rows:
            if len(row) < 2:
                continue

            coduser = str(row[0]).strip()
            codrol = str(row[1]).strip()

            if codrol not in ROL_MAP:
                continue

            rol_codigo = ROL_MAP[codrol]
            if rol_codigo not in rol_by_codigo:
                print(f"  [WARN] Rol {rol_codigo} no encontrado")
                nombramientos_saltados += 1
                continue

            # Buscar miembro por coduser (en MIEMBRO rows)
            miembro_id = None
            for mrow in miembro_rows:
                if len(mrow) > 15 and str(mrow[15]).strip().lower() == coduser.lower():
                    email = str(mrow[15]).strip().lower()
                    if email in MIEMBRO_MAP:
                        miembro_id = MIEMBRO_MAP[email]
                        break

            if not miembro_id:
                nombramientos_saltados += 1
                continue

            # Crear HistorialNombramiento (simplificado: sin agrupacion_id por ahora)
            rol = rol_by_codigo[rol_codigo]

            # Verificar si ya existe
            existing = (await session.execute(
                select(HistorialNombramiento).where(
                    HistorialNombramiento.miembro_id == miembro_id,
                    HistorialNombramiento.rol_id == rol.id,
                    HistorialNombramiento.fecha_fin == None,
                    HistorialNombramiento.eliminado == False,
                )
            )).first()

            if existing:
                nombramientos_saltados += 1
                continue

            nom = HistorialNombramiento(
                miembro_id=miembro_id,
                rol_id=rol.id,
                agrupacion_id=None,  # TODO: mapear agrupación
                fecha_inicio=date(2020, 1, 1),  # Fecha aproximada
                fecha_fin=None,
                tipo_origen="MIGRACION",
                motivo=f"Migrado desde dump MySQL (coduser={coduser})",
            )
            session.add(nom)
            nombramientos_creados += 1

        # --- Procesar COORDINAAREAGESTIONAGRUP (coordinadores) ---
        print("\n--- Procesando COORDINAAREAGESTIONAGRUP ---")

        for row in coord_rows:
            if len(row) < 3:
                continue

            coduser = str(row[0]).strip()
            codagrupacion = str(row[1]).strip()
            fecha_str = str(row[2]).strip() if len(row) > 2 else None

            fecha_inicio = _parse_date(fecha_str) if fecha_str else date(2020, 1, 1)

            # Buscar miembro
            miembro_id = None
            for mrow in miembro_rows:
                if len(mrow) > 15 and str(mrow[15]).strip().lower() == coduser.lower():
                    email = str(mrow[15]).strip().lower()
                    if email in MIEMBRO_MAP:
                        miembro_id = MIEMBRO_MAP[email]
                        break

            if not miembro_id:
                nombramientos_saltados += 1
                continue

            # Buscar agrupación
            agrupacion_id = AGRUPACION_MAP.get(codagrupacion)

            # Rol COORDINADOR
            if "COORDINADOR" not in rol_by_codigo:
                print(f"  [WARN] Rol COORDINADOR no encontrado")
                nombramientos_saltados += 1
                continue

            # Verificar si ya existe
            existing = (await session.execute(
                select(HistorialNombramiento).where(
                    HistorialNombramiento.miembro_id == miembro_id,
                    HistorialNombramiento.rol_id == rol_by_codigo["COORDINADOR"].id,
                    HistorialNombramiento.agrupacion_id == agrupacion_id,
                    HistorialNombramiento.fecha_fin == None,
                    HistorialNombramiento.eliminado == False,
                )
            )).first()

            if existing:
                nombramientos_saltados += 1
                continue

            nom = HistorialNombramiento(
                miembro_id=miembro_id,
                rol_id=rol_by_codigo["COORDINADOR"].id,
                agrupacion_id=agrupacion_id,
                fecha_inicio=fecha_inicio,
                fecha_fin=None,
                tipo_origen="MIGRACION",
                motivo=f"Migrado desde COORDINAAREAGESTIONAGRUP (coduser={coduser})",
            )
            session.add(nom)
            nombramientos_creados += 1

        await session.commit()

        print(f"\n" + "-" * 60)
        print(f"  Nombramientos creados: {nombramientos_creados}")
        print(f"  Nombramientos saltados: {nombramientos_saltados}")
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(seed())
