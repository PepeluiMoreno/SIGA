"""Seed cuotas anuales desde el volcado MySQL (CUOTAANIOSOCIO). Idempotente.

Join chain:
  CUOTAANIOSOCIO.CODSOCIO → SOCIO.CODSOCIO → SOCIO.CODUSER
  SOCIO.CODUSER → MIEMBRO.CODUSER → email → Miembro.id (DB)

CUOTAANIOSOCIO column indices (0-based):
  [0]  ANIOCUOTA
  [1]  CODSOCIO
  [2]  CODCUOTA
  [3]  CODAGRUPACION
  [4]  IMPORTECUOTAANIOEL
  [5]  NOMBRECUOTA
  [6]  IMPORTECUOTAANIOSOCIO   ← importe
  [7]  IMPORTECUOTAANIOPAGADA  ← importe_pagado
  [8]  IMPORTEGASTOSABONOCUOTA ← gastos_gestion
  [9]  FECHAPAGO
  [10] FECHAANOTACION
  [11] MODOINGRESO
  [12] CUENTAPAGO
  [13] ESTADOCUOTA
  [15] OBSERVACIONES

Se ejecuta via:
    docker exec <backend-container> python -m app.scripts.seeding.seed_cuotas
"""

import asyncio
import re
import uuid
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional

from sqlalchemy import select, func

from app.core.database import async_session
from app.modules.configuracion.models.estados import EstadoCuota
from app.modules.core.geografico.direccion import UnidadOrganizativa
from app.modules.economico.models.cuotas import CuotaAnual, ImporteCuotaAnio
from app.modules.membresia.models.miembro import Miembro

DUMP_FILE = "/tmp/dump.sql"
DUMP_FALLBACK = "/opt/docker/apps/SIGA/01_europa_laica_com-2026_02_17.sql"

# ---------------------------------------------------------------------------
# Parser (mismo que seed_miembros.py)
# ---------------------------------------------------------------------------

def parse_mysql_table(table_name: str, content: str) -> list[list]:
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
    result = []
    for v in values:
        if v in ("NULL", "null", ""):
            result.append(None)
        elif v.startswith("'") and v.endswith("'"):
            result.append(v[1:-1].replace("''", "'"))
        else:
            result.append(v)
    return result


def _parse_date(val: Optional[str]) -> Optional[date]:
    if not val or val.startswith("0000-00-00"):
        return None
    try:
        return date.fromisoformat(val[:10])
    except (ValueError, TypeError, IndexError):
        return None


def _parse_decimal(val: Optional[str]) -> Decimal:
    if not val:
        return Decimal("0.00")
    try:
        return Decimal(str(val).strip())
    except InvalidOperation:
        return Decimal("0.00")


# ---------------------------------------------------------------------------
# Mapeos
# ---------------------------------------------------------------------------

# MySQL ESTADOCUOTA → nombre EstadoCuota en DB (columna 'nombre', no 'codigo')
ESTADO_MAP: dict[str, str] = {
    "ABONADA":                  "Cobrada",
    "ABONADA-PARTE":            "Cobrada",
    "EXENTO":                   "Exenta",
    "NOABONADA":                "Impagada",
    "NOABONADA-DEVUELTA":       "Impagada",
    "NOABONADA-ERROR-CUENTA":   "Impagada",
    "PENDIENTE-COBRO":          "Pendiente",
    "BAJA-SOCIO":               "Anulada",
    "OTROS":                    "Anulada",
}

# MySQL MODOINGRESO → valor enum ModoIngreso
MODO_MAP: dict[str, str] = {
    "DOMICILIADA":  "SEPA",
    "METALICO":     "EFECTIVO",
    "PAYPAL":       "PAYPAL",
    "TARJETA":      "TARJETA",
    "TRANSFERENCIA": "TRANSFERENCIA",
    # CHEQUE y SIN-DATOS no tienen equivalente → None
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def seed():
    print("\n" + "=" * 60)
    print("SEED CUOTAS ANUALES (desde volcado MySQL)")
    print("=" * 60)

    dump_path = Path(DUMP_FILE) if Path(DUMP_FILE).exists() else Path(DUMP_FALLBACK)
    if not dump_path.exists():
        print(f"  [ERROR] volcado no encontrado en {DUMP_FILE} ni {DUMP_FALLBACK}")
        return

    print("  Leyendo dump…")
    content = dump_path.read_text(encoding="utf-8", errors="replace")

    miembro_rows = parse_mysql_table("MIEMBRO", content)
    socio_rows = parse_mysql_table("SOCIO", content)
    cuota_rows = parse_mysql_table("CUOTAANIOSOCIO", content)

    print(f"  MIEMBRO:        {len(miembro_rows)} filas")
    print(f"  SOCIO:          {len(socio_rows)} filas")
    print(f"  CUOTAANIOSOCIO: {len(cuota_rows)} filas")

    # CODUSER → email  (del dump MIEMBRO)
    coduser_to_email: dict[str, str] = {}
    for row in miembro_rows:
        if len(row) < 16:
            continue
        coduser = str(row[0]).strip() if row[0] else None
        email   = str(row[15]).strip() if row[15] else None
        if coduser and email:
            coduser_to_email[coduser] = email

    # CODSOCIO → CODUSER  (del dump SOCIO)
    codsocio_to_coduser: dict[str, str] = {}
    for row in socio_rows:
        if len(row) < 2:
            continue
        codsocio = str(row[0]).strip() if row[0] else None
        coduser  = str(row[1]).strip() if row[1] else None
        if codsocio and coduser:
            codsocio_to_coduser[codsocio] = coduser

    async with async_session() as session:

        # Verificar idempotencia
        n_existing = (await session.execute(select(func.count()).select_from(CuotaAnual))).scalar_one()
        if n_existing > 0:
            print(f"\n  [AVISO] cuotas_anuales ya tiene {n_existing} filas.")
            print("  Ejecuta primero: TRUNCATE TABLE cuotas_anuales CASCADE;")
            print("  Abortando.")
            return

        # Catálogos DB
        # email → {id, agrupacion_id}
        miembros_result = await session.execute(select(Miembro))
        email_to_miembro: dict[str, dict] = {}
        for m in miembros_result.scalars():
            if m.email and m.email not in email_to_miembro:
                email_to_miembro[m.email] = {"id": m.id, "agrupacion_id": m.agrupacion_id}

        # nombre_corto → UnidadOrganizativa.id
        agr_result = await session.execute(select(UnidadOrganizativa))
        agr_by_codigo: dict[str, uuid.UUID] = {}
        for a in agr_result.scalars():
            if a.nombre_corto:
                agr_by_codigo[a.nombre_corto] = a.id

        # EstadoCuota nombre → id
        estados_result = await session.execute(select(EstadoCuota))
        estado_by_codigo: dict[str, uuid.UUID] = {}
        for e in estados_result.scalars():
            estado_by_codigo[e.nombre] = e.id

        estado_pendiente_id = estado_by_codigo.get("Pendiente")
        if not estado_pendiente_id:
            print("  [ERROR] Estado 'PENDIENTE' no encontrado en la BD")
            return

        # ImporteCuotaAnio (ejercicio, codigo_cuota) → id
        imp_result = await session.execute(select(ImporteCuotaAnio))
        importe_by_key: dict[tuple, uuid.UUID] = {}
        for imp in imp_result.scalars():
            if imp.codigo_cuota:
                importe_by_key[(imp.ejercicio, imp.codigo_cuota)] = imp.id

        print(f"\n  Miembros en BD con email: {len(email_to_miembro)}")
        print(f"  Agrupaciones en BD:       {len(agr_by_codigo)}")
        print(f"  Estados cuota en BD:      {len(estado_by_codigo)}")
        print(f"  Importes cuota en BD:     {len(importe_by_key)}")

        # --- Procesar cuotas ---
        importadas = 0
        sin_miembro = 0
        sin_agrupacion = 0
        sin_estado = 0

        for row in cuota_rows:
            if len(row) < 14:
                continue

            aniocuota    = str(row[0]).strip() if row[0] else None
            codsocio     = str(row[1]).strip() if row[1] else None
            codcuota     = str(row[2]).strip() if row[2] else None   # General, Joven, Parado, Honorario
            codagrupacion = str(row[3]).strip() if row[3] else None
            importe      = _parse_decimal(row[6])
            importe_pag  = _parse_decimal(row[7])
            gastos       = _parse_decimal(row[8])
            fecha_pago   = _parse_date(str(row[9]) if row[9] else None)
            modoingreso  = str(row[11]).strip() if row[11] else None
            estadocuota  = str(row[13]).strip() if row[13] else None
            observ       = str(row[15]).strip() if len(row) > 15 and row[15] else None

            if not aniocuota or not codsocio:
                continue

            # Resolver miembro
            coduser = codsocio_to_coduser.get(codsocio)
            email   = coduser_to_email.get(coduser) if coduser else None
            miembro_info = email_to_miembro.get(email) if email else None
            if not miembro_info:
                sin_miembro += 1
                continue

            miembro_id     = miembro_info["id"]
            m_agrupacion_id = miembro_info["agrupacion_id"]

            # Resolver agrupación desde la propia cuota, con fallback al miembro
            agrupacion_id = agr_by_codigo.get(codagrupacion) if codagrupacion else None
            if not agrupacion_id:
                agrupacion_id = m_agrupacion_id
            if not agrupacion_id:
                sin_agrupacion += 1
                continue

            # Resolver estado
            codigo_db   = ESTADO_MAP.get(estadocuota, "Pendiente")
            estado_id   = estado_by_codigo.get(codigo_db, estado_pendiente_id)
            if not estado_id:
                sin_estado += 1
                continue

            # Modo ingreso
            modo_ingreso = MODO_MAP.get(modoingreso) if modoingreso else None

            # Vincular con importe_cuota_anio si existe
            ejercicio_int = int(aniocuota)
            importe_cuota_anio_id = importe_by_key.get((ejercicio_int, codcuota)) if codcuota else None

            cuota = CuotaAnual(
                miembro_id=miembro_id,
                ejercicio=ejercicio_int,
                agrupacion_id=agrupacion_id,
                codigo_cuota=codcuota,
                importe_cuota_anio_id=importe_cuota_anio_id,
                importe=importe,
                importe_pagado=importe_pag,
                gastos_gestion=gastos,
                estado_id=estado_id,
                modo_ingreso=modo_ingreso,
                fecha_pago=fecha_pago,
                observaciones=observ,
            )
            session.add(cuota)
            importadas += 1

            if importadas % 200 == 0:
                await session.flush()
                print(f"  … {importadas} cuotas procesadas")

        await session.commit()

        print(f"\n  Importadas:         {importadas}")
        print(f"  Sin miembro en BD:  {sin_miembro}")
        print(f"  Sin agrupación:     {sin_agrupacion}")
        print(f"  Sin estado:         {sin_estado}")


if __name__ == "__main__":
    asyncio.run(seed())
