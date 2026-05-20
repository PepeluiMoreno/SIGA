"""Generación del Libro Diario en formato CSV/Excel.

El Libro Diario es obligatorio por el Código de Comercio art. 25.1 — todos los
asientos del ejercicio en orden cronológico con sus apuntes.

NOTA: Se genera en CSV (UTF-8 con BOM, separador `;`, decimales con coma) porque
es el formato preferido por el ICAC y la mayoría de protectorados, y porque
no requiere librerías externas (reportlab/weasyprint no están en el contenedor
actual). Si se requiere PDF formal, añadir `reportlab` a requirements y
crear `generar_libro_diario_pdf()`.

El CSV se abre directamente en Excel/LibreOffice con la configuración española.
"""
import csv
import io
from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.contabilidad import (
    AsientoContable,
    ApunteContable,
    CuentaContable,
    EstadoAsientoContable,
)


def _fmt_importe(valor: Optional[Decimal]) -> str:
    """Formato español: 1.234,56 (sin separador de miles, decimal con coma)."""
    if valor is None or valor == 0:
        return ""
    s = f"{valor:.2f}"
    return s.replace(".", ",")


async def _cargar_asientos_ejercicio(
    session: AsyncSession, ejercicio: int
) -> List[Tuple[AsientoContable, List[Tuple[ApunteContable, str, str]]]]:
    """Carga todos los asientos CONFIRMADOS del ejercicio con sus apuntes y datos de cuenta."""
    q = (
        select(AsientoContable)
        .where(AsientoContable.ejercicio == ejercicio)
        .where(AsientoContable.estado == EstadoAsientoContable.CONFIRMADO)
        .order_by(AsientoContable.fecha, AsientoContable.numero_asiento)
    )
    result = await session.execute(q)
    asientos = list(result.scalars().all())

    salida = []
    for asiento in asientos:
        apuntes_data = []
        for apunte in sorted(asiento.apuntes, key=lambda a: (a.haber > 0, a.id)):
            # Buscar código y nombre de la cuenta
            cuenta_r = await session.execute(
                select(CuentaContable).where(CuentaContable.id == apunte.cuenta_id)
            )
            cuenta = cuenta_r.scalars().first()
            codigo = cuenta.codigo if cuenta else "???"
            nombre = cuenta.nombre if cuenta else ""
            apuntes_data.append((apunte, codigo, nombre))
        salida.append((asiento, apuntes_data))
    return salida


async def generar_libro_diario_csv(
    session: AsyncSession,
    ejercicio: int,
    organizacion_nombre: str = "Organización",
) -> bytes:
    """Genera el Libro Diario completo del ejercicio en formato CSV (UTF-8 BOM).

    Cada fila representa un apunte. Las columnas son:
    Nº Asiento | Fecha | Glosa | Cuenta | Nombre cuenta | Concepto | Debe | Haber

    Devuelve bytes listos para descarga (Content-Type: text/csv).
    """
    asientos = await _cargar_asientos_ejercicio(session, ejercicio)

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";", quoting=csv.QUOTE_MINIMAL)

    # Cabecera
    writer.writerow([f"{organizacion_nombre} - Libro Diario Ejercicio {ejercicio}"])
    writer.writerow([])
    writer.writerow([
        "Nº Asiento", "Fecha", "Glosa", "Cuenta", "Nombre cuenta",
        "Concepto", "Debe", "Haber",
    ])

    total_debe = Decimal("0")
    total_haber = Decimal("0")

    for asiento, apuntes_data in asientos:
        primer_apunte = True
        for apunte, codigo, nombre in apuntes_data:
            writer.writerow([
                asiento.numero_asiento if primer_apunte else "",
                asiento.fecha.strftime("%d/%m/%Y") if primer_apunte else "",
                asiento.glosa if primer_apunte else "",
                codigo,
                nombre,
                apunte.concepto or "",
                _fmt_importe(apunte.debe),
                _fmt_importe(apunte.haber),
            ])
            primer_apunte = False
            total_debe += apunte.debe or Decimal("0")
            total_haber += apunte.haber or Decimal("0")
        # Línea en blanco entre asientos
        writer.writerow([])

    # Totales
    writer.writerow([])
    writer.writerow([
        "", "", "TOTAL EJERCICIO", "", "", "",
        _fmt_importe(total_debe),
        _fmt_importe(total_haber),
    ])

    # UTF-8 BOM para Excel
    content = buffer.getvalue()
    return ("﻿" + content).encode("utf-8")
