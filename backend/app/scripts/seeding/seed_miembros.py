"""Seed miembros desde el volcado MySQL (MIEMBRO + SOCIO). Idempotente.

Unifica las tablas MIEMBRO (datos personales) y SOCIO (suscripción)
del dump original en nuestro modelo Miembro unificado.

Se ejecuta via:
    docker exec <backend-container> python -m app.scripts.seeding.seed_miembros
"""

import asyncio
import re
import uuid
from pathlib import Path
from typing import Optional

from sqlalchemy import select

from app.core.database import async_session
from app.modules.core.geografico.direccion import AgrupacionTerritorial, Pais, Provincia
from app.modules.membresia.models.estado_miembro import EstadoMiembro
from app.modules.membresia.models.miembro import Miembro, TipoMiembro

DUMP_FILE = "/opt/docker/apps/SIGA/01_europa_laica_com-2026_02_17.sql"

# ---------------------------------------------------------------------------
# SQL dump parser
# ---------------------------------------------------------------------------

def parse_mysql_table(table_name: str, content: str) -> list[list]:
    """Extrae todas las filas INSERT de una tabla del dump MySQL."""
    rows: list[list] = []
    pattern = re.compile(
        rf"INSERT INTO `?{re.escape(table_name)}?`\s*\(.*?\)\s*VALUES\s*",
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
    """Encuentra el paréntesis de cierre equilibrado."""
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
    """Separa valores MySQL respetando comillas escapadas."""
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
    # Convertir a Python
    result = []
    for v in values:
        if v == "NULL" or v == "null" or v == "":
            result.append(None)
        elif v.startswith("'") and v.endswith("'"):
            result.append(v[1:-1].replace("''", "'"))
        else:
            result.append(v)
    return result


def _parse_date(val: Optional[str]) -> Optional[str]:
    """MySQL date → YYYY-MM-DD o None. Maneja '0000-00-00'."""
    if not val or val == "0000-00-00" or val == "0000-00-00 00:00:00":
        return None
    return val[:10] if len(val) >= 10 else None


# ---------------------------------------------------------------------------
# Mapeo de tipos de miembro MySQL → tipos SIGA
# ---------------------------------------------------------------------------

TIPO_MAP = {
    "socio": "Ordinario",
    "simpatizante": "Ordinario",
    "administrador": "Ordinario",
    "honor": "De honor",
    "colaborador": "Ordinario",
}


async def seed():
    print("\n" + "=" * 60)
    print("SEED MIEMBROS (desde volcado MySQL)")
    print("=" * 60)

    dump_path = Path(DUMP_FILE)
    if not dump_path.exists():
        print(f"  [ERROR] {DUMP_FILE} no encontrado")
        return

    content = dump_path.read_text(encoding="utf-8", errors="replace")

    miembro_rows = parse_mysql_table("MIEMBRO", content)
    socio_rows = parse_mysql_table("SOCIO", content)

    print(f"\n  MIEMBRO: {len(miembro_rows)} filas")
    print(f"  SOCIO:   {len(socio_rows)} filas")

    # Indexar SOCIO por CODUSER para JOIN
    socio_by_user: dict[str, list] = {}
    for row in socio_rows:
        if len(row) < 12:
            continue
        coduser = str(row[1]).strip()
        if coduser:
            socio_by_user[coduser] = row

    async with async_session() as session:
        # --- Catálogos de referencia ---
        espana = (await session.execute(select(Pais).where(Pais.codigo == "ES"))).scalar_one_or_none()
        if not espana:
            print("[ERROR] País España no encontrado")
            return

        prov_result = await session.execute(select(Provincia))
        prov_by_codigo: dict[str, uuid.UUID] = {}
        for p in prov_result.scalars():
            prov_by_codigo[p.codigo.zfill(2)] = p.id

        agr_result = await session.execute(select(AgrupacionTerritorial))
        agr_by_codigo: dict[str, uuid.UUID] = {}
        for a in agr_result.scalars():
            agr_by_codigo[a.nombre_corto] = a.id

        tipos = (await session.execute(select(TipoMiembro).where(TipoMiembro.activo == True))).scalars().all()
        tipo_by_nombre: dict[str, uuid.UUID] = {t.nombre: t.id for t in tipos}

        estados = (await session.execute(select(EstadoMiembro).where(EstadoMiembro.activo == True))).scalars().all()
        estado_by_nombre: dict[str, uuid.UUID] = {e.nombre: e.id for e in estados}

        estado_alta = estado_by_nombre.get("Alta")
        if not estado_alta:
            print("[ERROR] Estado 'Alta' no encontrado")
            return

        tipo_ordinario = tipo_by_nombre.get("Ordinario")
        if not tipo_ordinario:
            print("[ERROR] Tipo 'Ordinario' no encontrado")
            return

        # --- Detección de duplicados ---
        existing_emails: set[str] = set()
        existing_docs: set[str] = set()
        existing_result = await session.execute(select(Miembro.email, Miembro.numero_documento))
        for email, doc in existing_result:
            if email:
                existing_emails.add(email)
            if doc:
                existing_docs.add(doc)

        # --- Procesar miembros ---
        importados = 0
        saltados = 0

        for row in miembro_rows:
            if len(row) < 30:
                continue

            coduser = str(row[0]).strip() if row[0] else None
            tipomiembro_raw = str(row[2]).strip().lower() if row[2] else "socio"
            numdoc = str(row[3]).strip() if row[3] else None
            tipodoc = str(row[4]).strip() if row[4] else None
            ape1 = str(row[5]).strip() if row[5] else None
            ape2 = str(row[6]).strip() if row[6] else None
            nom = str(row[7]).strip() if row[7] else None
            sexo = str(row[8]).strip() if row[8] else None
            fechanac = _parse_date(str(row[9]) if row[9] else None)
            telfijo_casa = str(row[10]).strip() if row[10] else None
            telfijo_trabajo = str(row[11]).strip() if row[11] else None
            telmovil = str(row[12]).strip() if row[12] else None
            profesion = str(row[13]).strip() if row[13] else None
            estudios = str(row[14]).strip() if row[14] else None
            email = str(row[15]).strip() if row[15] else None
            colabora = str(row[19]).strip() if row[19] else None
            codpais_dom = str(row[20]).strip() if row[20] else "ES"
            direccion = str(row[21]).strip() if row[21] else None
            cp = str(row[22]).strip() if row[22] else None
            localidad = str(row[23]).strip() if row[23] else None
            codprov = str(row[24]).strip() if row[24] else None
            comentarios = str(row[27]).strip() if row[27] else None
            observaciones = str(row[28]).strip() if row[28] else None

            # Skip sin datos mínimos
            if not nom and not ape1 and not email:
                saltados += 1
                continue

            # Duplicados
            if email and email in existing_emails:
                saltados += 1
                continue
            if numdoc and numdoc in existing_docs:
                saltados += 1
                continue

            # --- Datos de SOCIO (si existe) ---
            socio = socio_by_user.get(coduser)
            agrupacion_id = None
            fecha_alta = None
            fecha_baja = None
            iban = None

            if socio and len(socio) >= 12:
                cod_agrupacion = str(socio[2]).strip() if socio[2] else None
                agrupacion_id = agr_by_codigo.get(cod_agrupacion)
                fecha_alta = _parse_date(str(socio[5]) if socio[5] else None)
                fecha_baja = _parse_date(str(socio[6]) if socio[6] else None)
                iban = str(socio[7]).strip() if socio[7] else None

            # --- Mapeo de tipo ---
            tipo_nombre = TIPO_MAP.get(tipomiembro_raw, "Ordinario")
            tipo_miembro_id = tipo_by_nombre.get(tipo_nombre, tipo_ordinario)

            # --- Mapeo de provincia ---
            provincia_id = None
            if codprov and codprov.zfill(2) in prov_by_codigo:
                provincia_id = prov_by_codigo[codprov.zfill(2)]

            # --- País de domicilio ---
            pais_domicilio_id = espana.id
            if codpais_dom and codpais_dom != "--":
                pais_r = await session.execute(select(Pais).where(Pais.codigo == codpais_dom))
                pais_obj = pais_r.scalar_one_or_none()
                if pais_obj:
                    pais_domicilio_id = pais_obj.id

            # --- Limpiar fechas inválidas ---
            if fechanac and fechanac.startswith("0000"):
                fechanac = None
            if fecha_alta and fecha_alta.startswith("0000"):
                fecha_alta = None
            if fecha_baja and fecha_baja.startswith("0000"):
                fecha_baja = None

            # --- Estado ---
            estado_id = estado_by_nombre.get("Baja", estado_alta) if fecha_baja else estado_alta

            # --- Observaciones combinadas ---
            obs_parts = []
            if comentarios:
                obs_parts.append(comentarios)
            if observaciones:
                obs_parts.append(observaciones)
            obs_final = "\n".join(obs_parts) if obs_parts else None

            # --- Crear miembro ---
            miembro = Miembro(
                nombre=nom or f"Miembro {coduser}",
                apellido1=ape1 or "Sin nombre",
                apellido2=ape2,
                sexo=sexo if sexo in ("H", "M") else None,
                fecha_nacimiento=fechanac,
                tipo_miembro_id=tipo_miembro_id,
                estado_id=estado_id,
                tipo_documento=tipodoc,
                numero_documento=numdoc,
                direccion=direccion,
                codigo_postal=cp,
                localidad=localidad,
                provincia_id=provincia_id,
                pais_domicilio_id=pais_domicilio_id,
                telefono=telmovil or telfijo_casa or telfijo_trabajo,
                telefono2=telfijo_trabajo if telfijo_trabajo != telmovil else None,
                email=email,
                agrupacion_id=agrupacion_id,
                iban=iban,
                fecha_alta=fecha_alta or "2001-01-01",
                fecha_baja=fecha_baja,
                observaciones=obs_final,
                es_voluntario=bool(colabora and colabora.lower() in ("si", "sí", "yes", "y")),
                activo=fecha_baja is None,
            )

            session.add(miembro)
            if email:
                existing_emails.add(email)
            if numdoc:
                existing_docs.add(numdoc)
            importados += 1

            if importados % 5 == 0:
                await session.flush()

        await session.commit()

        print(f"\n  Importados: {importados}")
        print(f"  Saltados (duplicados): {saltados}")


if __name__ == "__main__":
    asyncio.run(seed())
