"""Geografía de España: ETL de SIGA (la T jerarquiza; ODM solo extrae).

Política de ODM (docs/PENDIENTE_recursos_derivados.md, 2026-06-06): ODM produce
piezas crudas; el ENSAMBLAJE/transformación es del consumidor. Por eso aquí:

  E) se consume de ODM el dataset PLANO «España - Municipios (INE)» (una fila por
     municipio: cpro, cmun, nombre — el recurso lee las 52 hojas del codmun.xlsx);
  T) se CONSTRUYE en SIGA el árbol territorial País→CCAA→Provincia→Municipio
     (función `construir_jerarquia`), rellenando CCAA/provincia con el nomenclátor
     oficial del INE embebido (el codmun.xlsx no trae CODAUTO ni nombres de CCAA/
     provincia) y resolviendo la pertenencia provincia→CCAA;
  L) se vuelca a `entidades_geograficas` (`cargar_geografia`), idempotente.

Fuentes (en orden de preferencia):
  --jsonl  RUTA   snapshot local de municipios crudos (instalación offline)
  --odm-url URL --query NOMBRE   dataset de Municipios en la API de datos de ODM

Uso:
  python -m app.scripts.seeding.seed_geografia_odm --jsonl data/municipios_ine.jsonl
  python -m app.scripts.seeding.seed_geografia_odm \
      --odm-url https://odmgr.pepelui.es/graphql/data --query espanaMunicipiosIne
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


# ── Nomenclátor oficial INE (referencia estable; el codmun.xlsx no lo trae) ──────
CCAA_NOMBRES: Dict[str, str] = {
    "01": "Andalucía", "02": "Aragón", "03": "Asturias, Principado de",
    "04": "Balears, Illes", "05": "Canarias", "06": "Cantabria",
    "07": "Castilla y León", "08": "Castilla - La Mancha", "09": "Cataluña",
    "10": "Comunitat Valenciana", "11": "Extremadura", "12": "Galicia",
    "13": "Madrid, Comunidad de", "14": "Murcia, Región de",
    "15": "Navarra, Comunidad Foral de", "16": "País Vasco", "17": "Rioja, La",
    "18": "Ceuta", "19": "Melilla",
}
PROV_NOMBRES: Dict[str, str] = {
    "01": "Araba/Álava", "02": "Albacete", "03": "Alicante/Alacant", "04": "Almería",
    "05": "Ávila", "06": "Badajoz", "07": "Balears, Illes", "08": "Barcelona",
    "09": "Burgos", "10": "Cáceres", "11": "Cádiz", "12": "Castellón/Castelló",
    "13": "Ciudad Real", "14": "Córdoba", "15": "Coruña, A", "16": "Cuenca",
    "17": "Girona", "18": "Granada", "19": "Guadalajara", "20": "Gipuzkoa",
    "21": "Huelva", "22": "Huesca", "23": "Jaén", "24": "León", "25": "Lleida",
    "26": "Rioja, La", "27": "Lugo", "28": "Madrid", "29": "Málaga", "30": "Murcia",
    "31": "Navarra", "32": "Ourense", "33": "Asturias", "34": "Palencia",
    "35": "Palmas, Las", "36": "Pontevedra", "37": "Salamanca",
    "38": "Santa Cruz de Tenerife", "39": "Cantabria", "40": "Segovia",
    "41": "Sevilla", "42": "Soria", "43": "Tarragona", "44": "Teruel", "45": "Toledo",
    "46": "Valencia/València", "47": "Valladolid", "48": "Bizkaia", "49": "Zamora",
    "50": "Zaragoza", "51": "Ceuta", "52": "Melilla",
}
# Provincia (CPRO) → Comunidad Autónoma (CODAUTO).
PROV_A_CCAA: Dict[str, str] = {
    "01": "16", "02": "08", "03": "10", "04": "01", "05": "07", "06": "11",
    "07": "04", "08": "09", "09": "07", "10": "11", "11": "01", "12": "10",
    "13": "08", "14": "01", "15": "12", "16": "08", "17": "09", "18": "01",
    "19": "08", "20": "16", "21": "01", "22": "02", "23": "01", "24": "07",
    "25": "09", "26": "17", "27": "12", "28": "13", "29": "01", "30": "14",
    "31": "15", "32": "12", "33": "03", "34": "07", "35": "05", "36": "12",
    "37": "07", "38": "05", "39": "06", "40": "07", "41": "01", "42": "07",
    "43": "09", "44": "02", "45": "08", "46": "10", "47": "07", "48": "16",
    "49": "07", "50": "02", "51": "18", "52": "19",
}

_PAIS_CODIGO, _PAIS_NOMBRE, _SEP = "ES", "España", " > "

# tipo → nombres candidatos del catálogo AmbitoGeografico de SIGA
_TIPO_A_AMBITO: Dict[str, tuple] = {
    "pais":      ("País", "Pais", "Estatal", "Nacional"),
    "comunidad": ("CCAA", "Comunidad Autónoma", "Comunidad autónoma", "Autonómico"),
    "provincia": ("Provincia", "Provincial"),
    "municipio": ("Municipio", "Municipal", "Local"),
}


def _pad(value: Any, width: int) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    if s == "":
        return None
    if s.endswith(".0"):
        s = s[:-2]
    return s.zfill(width)


def normalizar_toponimo(nombre: str) -> str:
    """Antepone el artículo/cualificador que el INE pospone tras coma, para mostrar
    o componer: 'Rioja, La'→'La Rioja', 'Coruña, A'→'A Coruña', 'Palmas, Las'→
    'Las Palmas', 'Madrid, Comunidad de'→'Comunidad de Madrid'. Idempotente (sin
    coma no cambia)."""
    if not nombre or ", " not in nombre:
        return nombre
    base, sufijo = nombre.split(", ", 1)
    return f"{sufijo} {base}".strip()


# ── T) Transformación: municipios planos → árbol territorial ────────────────────
def construir_jerarquia(municipios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """De filas crudas de municipios (cpro, cmun, nombre) construye el árbol
    País → CCAA → Provincia → Municipio. `codigo` es la clave de enlace única
    prefijada por tipo (ES / CA## / PR## / MU#####), porque los códigos INE de CCAA
    y provincia son ambos de 2 dígitos y colisionan; `codigo_ine` es el natural."""
    cpro_keys = ("cpro", "CPRO")
    cmun_keys = ("cmun", "CMUN")
    nombre_keys = ("nombre", "NOMBRE")

    def _first(d, keys):
        for k in keys:
            if k in d and d[k] not in (None, ""):
                return d[k]
        return None

    out: List[Dict[str, Any]] = [{
        "codigo": _PAIS_CODIGO, "codigo_ine": _PAIS_CODIGO, "nombre": _PAIS_NOMBRE,
        "tipo": "pais", "nivel": 0, "padre_id": None, "ruta": _PAIS_NOMBRE,
    }]

    ccaa_vistas: Dict[str, str] = {}
    prov_vistas: set = set()
    municipios_norm: List[Dict[str, str]] = []

    for row in municipios:
        cp = _pad(_first(row, cpro_keys), 2)
        cm = _pad(_first(row, cmun_keys), 3)
        nom = _first(row, nombre_keys)
        nom = str(nom).strip() if nom is not None else ""
        ca = PROV_A_CCAA.get(cp) if cp else None
        if not ca or not cp or not cm or not nom:
            continue
        ccaa_vistas.setdefault(ca, normalizar_toponimo(CCAA_NOMBRES.get(ca, ca)))
        municipios_norm.append({"ca": ca, "cp": cp, "codigo_ine": cp + cm,
                                "nombre": normalizar_toponimo(nom)})

    for ca in sorted(ccaa_vistas):
        out.append({
            "codigo": "CA" + ca, "codigo_ine": ca, "nombre": ccaa_vistas[ca],
            "tipo": "comunidad", "nivel": 1, "padre_id": _PAIS_CODIGO,
            "ruta": _SEP.join([_PAIS_NOMBRE, ccaa_vistas[ca]]),
        })

    for m in municipios_norm:
        if m["cp"] not in prov_vistas:
            prov_vistas.add(m["cp"])
            ca_nom = ccaa_vistas.get(m["ca"], m["ca"])
            prov_nom = normalizar_toponimo(PROV_NOMBRES.get(m["cp"], m["cp"]))
            out.append({
                "codigo": "PR" + m["cp"], "codigo_ine": m["cp"], "nombre": prov_nom,
                "tipo": "provincia", "nivel": 2, "padre_id": "CA" + m["ca"],
                "ruta": _SEP.join([_PAIS_NOMBRE, ca_nom, prov_nom]),
            })

    for m in municipios_norm:
        ca_nom = ccaa_vistas.get(m["ca"], m["ca"])
        prov_nom = normalizar_toponimo(PROV_NOMBRES.get(m["cp"], m["cp"]))
        out.append({
            "codigo": "MU" + m["codigo_ine"], "codigo_ine": m["codigo_ine"],
            "nombre": m["nombre"], "tipo": "municipio", "nivel": 3,
            "padre_id": "PR" + m["cp"],
            "ruta": _SEP.join([_PAIS_NOMBRE, ca_nom, prov_nom, m["nombre"]]),
        })

    return out


# ── L) Carga idempotente a entidades_geograficas ────────────────────────────────
async def _mapa_ambitos(session: AsyncSession) -> Dict[str, Optional[Any]]:
    rows = (await session.execute(select(AmbitoGeografico))).scalars().all()
    por_nombre = {a.nombre.strip().lower(): a.id for a in rows}
    return {tipo: next((por_nombre[c.lower()] for c in cands if c.lower() in por_nombre), None)
            for tipo, cands in _TIPO_A_AMBITO.items()}


async def cargar_geografia(session: AsyncSession, registros: List[Dict[str, Any]]) -> Dict[str, int]:
    """Vuelca registros de árbol (codigo/codigo_ine/nombre/tipo/nivel/padre_id/ruta)
    a `entidades_geograficas`. Idempotente: upsert por `codigo`; 2 pasadas (nodos →
    enlace de padres por código)."""
    ambito_de = await _mapa_ambitos(session)
    existentes = {e.codigo: e for e in (await session.execute(select(EntidadGeografica))).scalars().all()}
    creados = actualizados = 0

    for r in registros:
        codigo, nombre = r.get("codigo"), r.get("nombre")
        if not codigo or not nombre:
            continue
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
        ent.ambito_geografico_id = ambito_de.get((r.get("tipo") or "").strip().lower())
        ent.activo = True

    await session.flush()

    for r in registros:
        ent = existentes.get(r.get("codigo"))
        if ent is None:
            continue
        padre = r.get("padre_id")
        ent.padre_id = existentes[padre].id if padre and padre in existentes else None

    await session.commit()
    return {"total": len(registros), "creados": creados, "actualizados": actualizados}


# ── E) Fuentes de municipios crudos ─────────────────────────────────────────────
def cargar_municipios_jsonl(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read().strip()
    return json.loads(txt) if txt.startswith("[") else [json.loads(l) for l in txt.splitlines() if l.strip()]


def fetch_municipios_odm(query_name: str, base_url: str, timeout: int = 60) -> List[Dict[str, Any]]:
    """Lee TODOS los municipios del dataset plano de ODM (API de datos GraphQL)."""
    import urllib.request
    fields = "cpro cmun nombre"
    limit, offset, out = 5000, 0, []
    while True:
        gql = f"{{ {query_name}(limit: {limit}, offset: {offset}) {{ total items {{ {fields} }} }} }}"
        req = urllib.request.Request(base_url, data=json.dumps({"query": gql}).encode(),
                                     headers={"Content-Type": "application/json"})
        body = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
        if body.get("errors"):
            raise RuntimeError(f"ODM data API ({query_name}): {body['errors'][0].get('message')}")
        page = body["data"][query_name]
        out.extend(page["items"])
        offset += limit
        if offset >= page["total"]:
            break
    return out


async def backfill_referencias(session: AsyncSession) -> Dict[str, int]:
    """Backfill transitorio: rellena `entidad_geografica_id` desde las FKs viejas.

    - Contacto.provincia_id  → nodo provincia (codigo 'PR'+codigo INE).
    - UnidadOrganizativa.municipio_id → nodo municipio ('MU'+codigo); si no, su
      provincia_id → nodo provincia. Idempotente (solo rellena lo que esté a NULL).
    """
    from app.modules.membresia.models.contacto import Contacto
    from app.modules.core.geografico.direccion import UnidadOrganizativa, Provincia, Municipio
    ents = {e.codigo: e for e in (await session.execute(select(EntidadGeografica))).scalars().all()}
    prov = {p.id: p for p in (await session.execute(select(Provincia))).scalars().all()}
    muni = {m.id: m for m in (await session.execute(select(Municipio))).scalars().all()}

    def _ent_prov(pid):
        p = prov.get(pid)
        return ents.get("PR" + str(p.codigo).zfill(2)) if p else None

    def _ent_muni(mid):
        m = muni.get(mid)
        return ents.get("MU" + str(m.codigo).zfill(5)) if m else None

    c_set = u_set = 0
    contactos = (await session.execute(
        select(Contacto).where(Contacto.provincia_id.isnot(None), Contacto.entidad_geografica_id.is_(None))
    )).scalars().all()
    for c in contactos:
        e = _ent_prov(c.provincia_id)
        if e:
            c.entidad_geografica_id = e.id
            c_set += 1

    unidades = (await session.execute(
        select(UnidadOrganizativa).where(UnidadOrganizativa.entidad_geografica_id.is_(None))
    )).scalars().all()
    for u in unidades:
        e = (_ent_muni(u.municipio_id) if u.municipio_id else None) or (_ent_prov(u.provincia_id) if u.provincia_id else None)
        if e:
            u.entidad_geografica_id = e.id
            u_set += 1

    await session.commit()
    return {"contactos_actualizados": c_set, "unidades_actualizadas": u_set}


async def _main(args) -> None:
    municipios = cargar_municipios_jsonl(args.jsonl) if args.jsonl else fetch_municipios_odm(args.query, args.odm_url)
    print(f"Municipios crudos: {len(municipios)}")
    arbol = construir_jerarquia(municipios)
    print(f"Nodos del árbol (país+CCAA+provincias+municipios): {len(arbol)}")
    async with async_session() as session:
        stats = await cargar_geografia(session, arbol)
    print(f"✅ Geografía cargada: {stats}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="ETL de geografía de España (E: ODM municipios · T: jerarquía · L: SIGA)")
    p.add_argument("--jsonl", help="Snapshot local de municipios crudos (JSONL o JSON array)")
    p.add_argument("--odm-url", default=os.environ.get("ODMGR_DATA_URL", "https://odmgr.pepelui.es/graphql/data"))
    p.add_argument("--query", default="espanaMunicipiosIne",
                   help="Nombre de la query del dataset de Municipios en la API de datos de ODM")
    asyncio.run(_main(p.parse_args()))
