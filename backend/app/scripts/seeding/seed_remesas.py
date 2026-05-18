"""Seed remesas y ordenes_cobro desde el volcado MySQL.

Tablas origen:
  REMESAS_SEPAXML  → remesas
  ORDENES_COBRO    → ordenes_cobro

Mapeado de estados:
  REMESAS:
    ANOTADO_EN_CUOTAANIOSOCIO=='SI' → 'Procesada'
    otro                            → 'Enviada'

  ORDENES_COBRO (ESTADOCUOTA):
    ABONADA / ABONADA-PARTE         → 'Procesada'
    NOABONADA-DEVUELTA              → 'Fallida'
    PENDIENTE-COBRO                 → 'Pendiente'
    otro                            → 'Pendiente'

Dependencias:
  - cuotas_anuales ya pobladas (seed_cuotas.py ejecutado antes)
  - miembros importados
  - estados_remesa y estados_orden_cobro ya existentes

Ejecutar:
    docker exec <backend-container> python -m app.scripts.seeding.seed_remesas
"""
import asyncio
import re
import uuid
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

from sqlalchemy import select

from app.core.database import async_session
from app.modules.economico.models.remesas import Remesa, OrdenCobro
from app.modules.economico.models.cuotas import CuotaAnual
from app.modules.membresia.models.miembro import Miembro
from app.modules.configuracion.models.estados import EstadoRemesa, EstadoOrdenCobro

DUMP_FILE = "/tmp/dump.sql"
DUMP_FALLBACK = "/opt/docker/apps/SIGA/01_europa_laica_com-2026_02_17.sql"

ESTADO_ORDEN_MAP = {
    "ABONADA":           "Procesada",
    "ABONADA-PARTE":     "Procesada",
    "NOABONADA-DEVUELTA": "Fallida",
    "PENDIENTE-COBRO":   "Pendiente",
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


def _parse_date(val: Optional[str]) -> Optional[date]:
    if not val or val in ("NULL", "0000-00-00", ""):
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(val.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _parse_decimal(val) -> Decimal:
    try:
        return Decimal(str(val)) if val not in (None, "NULL", "") else Decimal("0.00")
    except Exception:
        return Decimal("0.00")


# ── Seed principal ────────────────────────────────────────────────────────────

async def seed():
    dump_path = DUMP_FILE if Path(DUMP_FILE).exists() else DUMP_FALLBACK
    if not Path(dump_path).exists():
        print(f"[ERROR] No se encontró volcado en {dump_path}")
        return

    print(f"[seed_remesas] Leyendo volcado: {dump_path}")
    content = Path(dump_path).read_text(encoding="utf-8", errors="replace")

    remesa_rows = parse_mysql_table("REMESAS_SEPAXML", content)
    orden_rows  = parse_mysql_table("ORDENES_COBRO", content)
    print(f"  REMESAS_SEPAXML:  {len(remesa_rows)} filas")
    print(f"  ORDENES_COBRO:    {len(orden_rows)} filas")

    # ── Cargar tablas de referencia ──────────────────────────────────────────

    # También leemos SOCIO para mapear CODSOCIO → CODUSER y luego a miembro
    socio_rows = parse_mysql_table("SOCIO", content)
    # SOCIO cols: CODSOCIO[0], CODUSER[1], email[2?]  — detectar dinámicamente
    # estructura: CODSOCIO, CODUSER, CODAGRUPACION, NOMBRE, ...
    # Revisamos: el volcado SOCIO tiene: CODSOCIO,CODUSER,CODAGRUPACION,NOMBRE,APELLIDO1,...
    codsocio_to_coduser: dict[str, str] = {}
    for sr in socio_rows:
        if len(sr) >= 2 and sr[0] and sr[1]:
            codsocio_to_coduser[str(sr[0]).strip()] = str(sr[1]).strip()

    # MIEMBRO (en MySQL: MIEMBRO o USUARIO según el dump)
    miembro_rows = parse_mysql_table("MIEMBRO", content)
    coduser_to_email: dict[str, str] = {}
    for mr in miembro_rows:
        # MIEMBRO cols: CODUSER[0], ..., EMAIL[15]
        if len(mr) < 16 or not mr[0] or not mr[15]:
            continue
        coduser_to_email[str(mr[0]).strip()] = str(mr[15]).strip().lower()

    async with async_session() as session:
        # Estados remesa
        r_estados = await session.execute(select(EstadoRemesa))
        estado_remesa_by_nombre: dict[str, uuid.UUID] = {
            e.nombre: e.id for e in r_estados.scalars()
        }

        # Estados orden cobro
        oc_estados = await session.execute(select(EstadoOrdenCobro))
        estado_orden_by_nombre: dict[str, uuid.UUID] = {
            e.nombre: e.id for e in oc_estados.scalars()
        }

        # Miembros email → id
        m_result = await session.execute(select(Miembro.id, Miembro.email))
        email_to_miembro_id: dict[str, uuid.UUID] = {
            row.email.lower(): row.id for row in m_result if row.email
        }

        # Cuotas (miembro_id, ejercicio) → cuota_id
        c_result = await session.execute(select(CuotaAnual.id, CuotaAnual.miembro_id, CuotaAnual.ejercicio))
        cuota_key_to_id: dict[tuple, uuid.UUID] = {
            (str(row.miembro_id), row.ejercicio): row.id for row in c_result
        }

        # Remesas existentes (referencia/archivo → id)  para idempotencia
        rem_result = await session.execute(select(Remesa.id, Remesa.referencia))
        remesa_by_archivo: dict[str, uuid.UUID] = {r.referencia: r.id for r in rem_result}

        # ── Crear remesas ────────────────────────────────────────────────────
        # REMESAS_SEPAXML cols:
        # [0] NOMARCHIVOSEPAXML  [1] DIRECTORIOARCHIVOREMESA  [2] ANIOCUOTA
        # [3] FECHA_CREACION_ARCHIVO_SEPA  [4] FECHAORDENCOBRO  [5] FECHAPAGO
        # [6] FECHAALTASEXENTOSPAGO  [7] FECHAANOTACIONPAGO
        # [8] ANOTADO_EN_CUOTAANIOSOCIO  [9] IMPORTEREMESA  [10] IMPORTEGASTOSREMESA
        # [11] NUMRECIBOS  [12] CODUSER  [13] OBSERVACIONES

        estado_procesada_id = estado_remesa_by_nombre.get("Procesada")
        estado_enviada_id   = estado_remesa_by_nombre.get("Enviada")

        remesas_creadas = 0
        for row in remesa_rows:
            if len(row) < 12:
                continue
            archivo      = str(row[0]).strip() if row[0] else None
            if not archivo:
                continue
            if archivo in remesa_by_archivo:
                continue  # ya existe

            fecha_creacion = _parse_date(str(row[3]) if row[3] else None)
            fecha_envio    = _parse_date(str(row[4]) if row[4] else None)
            fecha_cobro    = _parse_date(str(row[5]) if row[5] else None)
            anotado        = str(row[8]).strip().upper() if row[8] else "NO"
            importe_total  = _parse_decimal(row[9])
            gastos         = _parse_decimal(row[10])
            num_ordenes    = int(row[11]) if row[11] else 0
            observaciones  = str(row[13]).strip() if len(row) > 13 and row[13] else None

            estado_id = estado_procesada_id if anotado == "SI" else estado_enviada_id

            # mensaje_id: eliminar extensión del nombre de archivo
            mensaje_id = archivo.replace(".xml", "").replace(".XML", "")

            remesa = Remesa(
                id=uuid.uuid4(),
                referencia=archivo,
                archivo_sepa=archivo,
                mensaje_id=mensaje_id,
                fecha_creacion=fecha_creacion or date.today(),
                fecha_envio=fecha_envio,
                fecha_cobro=fecha_cobro,
                importe_total=importe_total,
                gastos=gastos,
                num_ordenes=num_ordenes,
                estado_id=estado_id,
                observaciones=observaciones,
            )
            session.add(remesa)
            remesa_by_archivo[archivo] = remesa.id
            remesas_creadas += 1

        await session.flush()
        print(f"  Remesas creadas: {remesas_creadas}")

        # ── Crear órdenes de cobro ────────────────────────────────────────────
        # ORDENES_COBRO cols:
        # [0] NOMARCHIVOSEPAXML  [1] CODSOCIO  [2] FECHAORDENCOBRO
        # [3] ANIOCUOTA  [4] CUENTAIBAN  [5] SECUENCIAADEUDOSEPA
        # [6] FECHAACTUALIZACUENTA  [7] ANOTADO_EN_CUOTAANIOSOCIO
        # [8] FECHAPAGO  [9] FECHAANOTACION  [10] ESTADOCUOTA
        # [11] CUOTADONACIONPENDIENTEPAGO  [12] IMPORTECUOTAANIOPAGADA
        # [13] IMPORTEGASTOSABONOCUOTA  [14] IMPORTEGASTOSDEVOLUCION
        # [15] FECHADEVOLUCION  [16] MOTIVODEVOLUCION  [17] CODCUOTA
        # [18] IMPORTECUOTAANIOEL  [19] IMPORTECUOTAANIOSOCIO
        # [20] ESTADOCUOTA_ANTES_REMESA  [21] IMPORTECUOTAANIOPAGADA_ANTES_REMESA
        # ...  [25] CODAGRUPACION  [26] NOMAGRUPACION  [27] OBSERVACIONES

        estado_pendiente_oc = estado_orden_by_nombre.get("Pendiente")
        estado_procesada_oc = estado_orden_by_nombre.get("Procesada")
        estado_fallida_oc   = estado_orden_by_nombre.get("Fallida")

        ordenes_creadas  = 0
        sin_remesa       = 0
        sin_cuota        = 0
        sin_miembro      = 0

        # Cargar ordenes existentes para idempotencia (remesa_id, cuota_id)
        oc_result = await session.execute(select(OrdenCobro.remesa_id, OrdenCobro.cuota_id))
        ordenes_existentes: set[tuple] = {(str(r.remesa_id), str(r.cuota_id)) for r in oc_result}

        for row in orden_rows:
            if len(row) < 12:
                continue

            archivo    = str(row[0]).strip() if row[0] else None
            codsocio   = str(row[1]).strip() if row[1] else None
            aniocuota  = str(row[3]).strip() if row[3] else None
            iban       = str(row[4]).strip() if row[4] else None
            fecha_pago = _parse_date(str(row[8]) if row[8] else None)
            estado_oc  = str(row[10]).strip().upper() if row[10] else "PENDIENTE-COBRO"
            importe    = _parse_decimal(row[11])
            motivo     = str(row[16]).strip() if len(row) > 16 and row[16] else None

            if not archivo or not codsocio or not aniocuota:
                continue

            remesa_id = remesa_by_archivo.get(archivo)
            if not remesa_id:
                sin_remesa += 1
                continue

            # Resolver miembro vía CODSOCIO → CODUSER → email → miembro_id
            coduser  = codsocio_to_coduser.get(codsocio)
            email    = coduser_to_email.get(coduser) if coduser else None
            miembro_id = email_to_miembro_id.get(email) if email else None
            if not miembro_id:
                sin_miembro += 1
                continue

            try:
                ejercicio_int = int(aniocuota)
            except (TypeError, ValueError):
                continue

            cuota_id = cuota_key_to_id.get((str(miembro_id), ejercicio_int))
            if not cuota_id:
                sin_cuota += 1
                continue

            key = (str(remesa_id), str(cuota_id))
            if key in ordenes_existentes:
                continue

            # Estado orden
            estado_nombre = ESTADO_ORDEN_MAP.get(estado_oc, "Pendiente")
            if estado_nombre == "Procesada":
                estado_oc_id = estado_procesada_oc
            elif estado_nombre == "Fallida":
                estado_oc_id = estado_fallida_oc
            else:
                estado_oc_id = estado_pendiente_oc

            orden = OrdenCobro(
                id=uuid.uuid4(),
                remesa_id=remesa_id,
                cuota_id=cuota_id,
                importe=importe,
                referencia_mandato=f"MAND-{codsocio}",
                iban=iban,
                estado_id=estado_oc_id,
                fecha_procesamiento=fecha_pago,
                motivo_rechazo=motivo,
            )
            session.add(orden)
            ordenes_existentes.add(key)
            ordenes_creadas += 1

            if ordenes_creadas % 500 == 0:
                await session.flush()
                print(f"  … {ordenes_creadas} órdenes procesadas")

        await session.commit()

    print(f"  Órdenes creadas:   {ordenes_creadas}")
    print(f"  Sin remesa:        {sin_remesa}")
    print(f"  Sin miembro en BD: {sin_miembro}")
    print(f"  Sin cuota en BD:   {sin_cuota}")
    print("[seed_remesas] COMPLETADO")


if __name__ == "__main__":
    asyncio.run(seed())
