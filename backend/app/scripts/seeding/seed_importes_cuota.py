"""Seed importes_cuota_anio desde IMPORTEDESCUOTAANIO del volcado MySQL.

Tabla origen:  IMPORTEDESCUOTAANIO (ANIOCUOTA, CODCUOTA, IMPORTECUOTAANIOEL, NOMBRECUOTA, DESCRIPCIONCUOTA)
Tabla destino: importes_cuota_anio

Las tarifas en el volcado son:
  General   → cuota completa (€30→€40→€50→€60 según el año)
  Joven     → persona 18-25 años (€0 hasta 2013, luego €5)
  Parado    → persona en paro (€0 hasta 2013, luego €5)
  Honorario → miembro de honor, exento (€0)

Se ejecuta via:
    docker exec <backend-container> python -m app.scripts.seeding.seed_importes_cuota

Idempotente: salta filas que ya existen (ejercicio + codigo_cuota).
"""
import asyncio
import re
import uuid
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select

from app.core.database import async_session
from app.modules.economico.models.cuotas import ImporteCuotaAnio

DUMP_FILE = "/tmp/dump.sql"
DUMP_FALLBACK = "/opt/docker/apps/SIGA/01_europa_laica_com-2026_02_17.sql"

DESCRIPCION_CUOTA = {
    "General":   "Cuota general sin bonificaciones",
    "Honorario": "Miembro honorario o de honor, exento de cuota",
    "Joven":     "Tarifa reducida para jóvenes entre 18 y 25 años",
    "Parado":    "Tarifa reducida por situación de desempleo o dificultad económica",
}


# ── Parser de volcado MySQL ───────────────────────────────────────────────────

def _find_matching_paren(text: str, start: int) -> int:
    in_str = False
    j = start
    while j < len(text):
        ch = text[j]
        if ch == "'" and not in_str:
            in_str = True
        elif ch == "'" and in_str:
            if j + 1 < len(text) and text[j + 1] == "'":
                j += 2
                continue
            in_str = False
        elif ch == ")" and not in_str:
            return j
        j += 1
    return len(text) - 1


def _split_values(inner: str) -> list:
    vals: list = []
    i = 0
    while i < len(inner):
        c = inner[i]
        if c == "'":
            j = i + 1
            buf = []
            while j < len(inner):
                if inner[j] == "'" and j + 1 < len(inner) and inner[j + 1] == "'":
                    buf.append("'")
                    j += 2
                elif inner[j] == "'":
                    break
                else:
                    buf.append(inner[j])
                    j += 1
            vals.append("".join(buf))
            i = j + 1
        elif c == "N" and inner[i:i+4] == "NULL":
            vals.append(None)
            i += 4
        elif c in " ,\t\r\n":
            i += 1
        else:
            j = i
            while j < len(inner) and inner[j] not in ",)":
                j += 1
            token = inner[i:j].strip()
            vals.append(token if token != "NULL" else None)
            i = j
    return vals


def parse_mysql_table(table_name: str, content: str) -> list[list]:
    rows: list[list] = []
    pattern = re.compile(
        rf"INSERT INTO `?{re.escape(table_name)}`?\s*\(.*?\)\s*VALUES\s*",
        re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(content):
        i = match.end()
        while i < len(content):
            if content[i] == "(":
                j = _find_matching_paren(content, i)
                inner = content[i + 1: j]
                rows.append(_split_values(inner))
                i = j + 1
                while i < len(content) and content[i] in " ,;\n\r\t":
                    i += 1
            else:
                break
    return rows


# ── Seed principal ────────────────────────────────────────────────────────────

async def seed():
    dump_path = DUMP_FILE if Path(DUMP_FILE).exists() else DUMP_FALLBACK
    if not Path(dump_path).exists():
        print(f"[ERROR] No se encontró volcado en {dump_path}")
        return

    print(f"[seed_importes_cuota] Leyendo volcado: {dump_path}")
    content = Path(dump_path).read_text(encoding="utf-8", errors="replace")

    rows = parse_mysql_table("IMPORTEDESCUOTAANIO", content)
    print(f"  Filas IMPORTEDESCUOTAANIO: {len(rows)}")

    async with async_session() as session:
        # Cargar existentes (ejercicio, codigo_cuota) para idempotencia
        result = await session.execute(select(ImporteCuotaAnio))
        existentes: set[tuple] = {
            (r.ejercicio, r.codigo_cuota)
            for r in result.scalars()
            if r.codigo_cuota
        }
        print(f"  Ya existen en BD: {len(existentes)}")

        creados = 0
        saltados = 0

        for row in rows:
            if len(row) < 3:
                continue
            ejercicio_raw = row[0]
            codigo_cuota  = str(row[1]).strip() if row[1] else None
            importe_raw   = row[2]
            descripcion   = str(row[4]).strip() if len(row) > 4 and row[4] else None

            try:
                ejercicio = int(ejercicio_raw)
            except (TypeError, ValueError):
                continue

            if not codigo_cuota:
                continue

            if (ejercicio, codigo_cuota) in existentes:
                saltados += 1
                continue

            importe = Decimal(str(importe_raw)) if importe_raw else Decimal("0.00")
            desc_legible = DESCRIPCION_CUOTA.get(codigo_cuota, descripcion or codigo_cuota)

            obj = ImporteCuotaAnio(
                id=uuid.uuid4(),
                ejercicio=ejercicio,
                codigo_cuota=codigo_cuota,
                tipo_miembro_id=None,
                importe=importe,
                nombre_cuota=f"{codigo_cuota} {ejercicio}",
                activo=True,
                observaciones=desc_legible,
            )
            session.add(obj)
            existentes.add((ejercicio, codigo_cuota))
            creados += 1

            if creados % 50 == 0:
                await session.flush()
                print(f"  … {creados} creados")

        await session.commit()
        print(f"\n  Creados:  {creados}")
        print(f"  Saltados: {saltados}")
        print("[seed_importes_cuota] COMPLETADO")


if __name__ == "__main__":
    asyncio.run(seed())
