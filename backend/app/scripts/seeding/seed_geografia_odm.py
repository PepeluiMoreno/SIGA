"""Importa la geografía de España desde OpenDataManager (ODM).

Consume el recurso consolidado «España - Geografía jerárquica (INE)» de ODM —que
entrega la división territorial completa (País → CCAA → Provincia → Municipio) como
un dataset recursivo (`codigo`, `codigo_ine`, `nombre`, `tipo`, `nivel`, `padre_id`,
`ruta`)— y lo vuelca 1:1 a la tabla `entidades_geograficas` de SIGA.

Idempotente: upsert por `codigo` (clave única prefijada ES/CA##/PR##/MU#####, que
evita la colisión de códigos INE de 2 dígitos entre CCAA y provincia). El `tipo` del
nodo se mapea al catálogo `AmbitoGeografico`.

Fuentes (en orden de preferencia):
  --jsonl  RUTA   lee un snapshot local (instalación offline / reproducible)
  --odm-url URL --query NOMBRE   lee de la API de datos GraphQL de ODM

Uso:
  python -m app.scripts.seeding.seed_geografia_odm --jsonl data/geo_jerarquia.jsonl
  python -m app.scripts.seeding.seed_geografia_odm \
      --odm-url https://odmgr.pepelui.es/graphql/data --query espanaGeografiaJerarquicaIne
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.modules.core.geografico.entidad_geografica import EntidadGeografica
from app.modules.core.geografico.nivel_organizativo import AmbitoGeografico


# tipo del recurso ODM → nombres candidatos del catálogo AmbitoGeografico de SIGA.
_TIPO_A_AMBITO: Dict[str, tuple] = {
    "pais":      ("País", "Pais", "Estatal", "Nacional"),
    "comunidad": ("CCAA", "Comunidad Autónoma", "Comunidad autónoma", "Autonómico"),
    "provincia": ("Provincia", "Provincial"),
    "municipio": ("Municipio", "Municipal", "Local"),
}


async def _mapa_ambitos(session: AsyncSession) -> Dict[str, Optional[Any]]:
    """tipo (pais/comunidad/provincia/municipio) → id de AmbitoGeografico (o None)."""
    rows = (await session.execute(select(AmbitoGeografico))).scalars().all()
    por_nombre = {a.nombre.strip().lower(): a.id for a in rows}
    out: Dict[str, Optional[Any]] = {}
    for tipo, candidatos in _TIPO_A_AMBITO.items():
        out[tipo] = next((por_nombre[c.lower()] for c in candidatos if c.lower() in por_nombre), None)
    return out


async def cargar_geografia(session: AsyncSession, registros: List[Dict[str, Any]]) -> Dict[str, int]:
    """Vuelca los registros del dataset de ODM a `entidades_geograficas` (idempotente).

    Dos pasadas: (1) upsert de cada nodo por `codigo`; (2) fijar `padre_id` casando
    `padre_id` del registro (código del padre) → id de la entidad ya persistida.
    """
    ambito_de = await _mapa_ambitos(session)

    existentes = {
        e.codigo: e for e in (await session.execute(select(EntidadGeografica))).scalars().all()
    }

    creados = actualizados = 0

    # Pasada 1 — nodos (sin padre todavía)
    for r in registros:
        codigo = r.get("codigo")
        nombre = r.get("nombre")
        if not codigo or not nombre:
            continue
        tipo = (r.get("tipo") or "").strip().lower()
        ambito_id = ambito_de.get(tipo)
        ent = existentes.get(codigo)
        if ent is None:
            ent = EntidadGeografica(codigo=codigo)
            session.add(ent)
            existentes[codigo] = ent
            creados += 1
        else:
            actualizados += 1
        ent.nombre = nombre
        ent.codigo_ine = r.get("codigo_ine")
        ent.nivel = r.get("nivel")
        ent.ruta = r.get("ruta")
        ent.ambito_geografico_id = ambito_id
        ent.activo = True

    await session.flush()  # asigna ids a los nuevos

    # Pasada 2 — enlazar padres
    for r in registros:
        codigo = r.get("codigo")
        padre_cod = r.get("padre_id")
        ent = existentes.get(codigo)
        if ent is None:
            continue
        ent.padre_id = existentes[padre_cod].id if padre_cod and padre_cod in existentes else None

    await session.commit()
    return {"total": len(registros), "creados": creados, "actualizados": actualizados}


def cargar_desde_jsonl(path: str) -> List[Dict[str, Any]]:
    """Lee un snapshot local (una fila JSON por línea, o un array JSON)."""
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read().strip()
    if txt.startswith("["):
        return json.loads(txt)
    return [json.loads(line) for line in txt.splitlines() if line.strip()]


def fetch_desde_odm(query_name: str, base_url: str, timeout: int = 60) -> List[Dict[str, Any]]:
    """Lee TODOS los registros del dataset de la API de datos GraphQL de ODM."""
    import urllib.request
    fields = "codigo codigo_ine nombre tipo nivel padre_id ruta"
    limit, offset, out = 5000, 0, []
    while True:
        gql = f"{{ {query_name}(limit: {limit}, offset: {offset}) {{ total items {{ {fields} }} }} }}"
        req = urllib.request.Request(
            base_url, data=json.dumps({"query": gql}).encode(),
            headers={"Content-Type": "application/json"},
        )
        body = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
        if body.get("errors"):
            raise RuntimeError(f"ODM data API ({query_name}): {body['errors'][0].get('message')}")
        page = body["data"][query_name]
        out.extend(page["items"])
        offset += limit
        if offset >= page["total"]:
            break
    return out


async def _main(args) -> None:
    if args.jsonl:
        registros = cargar_desde_jsonl(args.jsonl)
    else:
        registros = fetch_desde_odm(args.query, args.odm_url)
    print(f"Registros de geografía a cargar: {len(registros)}")
    async with async_session() as session:
        stats = await cargar_geografia(session, registros)
    print(f"✅ Geografía cargada: {stats}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Importa la geografía jerárquica de España desde ODM")
    p.add_argument("--jsonl", help="Ruta a un snapshot local (JSONL o JSON array)")
    p.add_argument("--odm-url", default=os.environ.get("ODMGR_DATA_URL", "https://odmgr.pepelui.es/graphql/data"))
    p.add_argument("--query", default="espanaGeografiaJerarquicaIne",
                   help="Nombre de la query del dataset en la API de datos de ODM")
    asyncio.run(_main(p.parse_args()))
