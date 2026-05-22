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
from app.modules.actividades.models.accion import TipoAccion
from app.modules.actividades.models.campana import TipoCampania
from app.modules.actividades.models.grupo import TipoGrupo
from app.modules.configuracion.models.configuracion import Configuracion
from app.modules.configuracion.models.estados import EstadoCampania, EstadoAccion
from app.modules.configuracion.models.tema_ui import TemaUI
from app.modules.core.comunicacion.plantilla_email import PlantillaEmail
from app.modules.core.geografico.direccion import UnidadOrganizativa
from app.modules.core.geografico.nivel_organizativo import (
    NivelOrganizativo, NaturalezaUnidad, VinculoUnidad
)
from app.modules.membresia.models.estado_miembro import EstadoMiembro
from app.modules.membresia.models.historial_nombramiento import HistorialNombramiento
from app.modules.membresia.models.miembro import Miembro, TipoMiembro
from app.modules.economico.models.cobro.forma_pago import FormaPago  # noqa: F401 — registra mapper
from app.scripts.seeding.seed_init_accesos import seed as seed_roles_funcionales
from app.scripts.seeding.seed_comunicacion import seed_comunicacion


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
    ('org.rrss.telegram',        'string', ''),
    ('org.logo',                       'string', ''),
    ('org.implantacion_geografica',     'string', ''),
    ('org.tipo_agrupacion_territorial', 'string', ''),
    ('org.multiterritorial',            'bool',   'false'),
    ('org.numero_registro',             'string', ''),
    ('org.denominacion_miembro',              'string', 'miembro'),
    ('org.denominacion_miembro_plural',       'string', 'miembros'),
    ('org.denominacion_organo_gobierno',      'string', 'junta directiva'),
    ('org.denominacion_organo_gobierno_plural','string', 'juntas directivas'),
    ('org.edad_max_joven',                    'int',    '30'),
    # Autenticación
    ('auth.modo',                       'string', 'LOCAL'),   # LOCAL | AUTHELIA | OIDC
    ('auth.authelia_url',               'string', ''),
    ('auth.oidc_issuer',                'string', ''),
    ('auth.session_inactividad_minutos','int',    '30'),
    ('auth.session_maximo_minutos',     'int',    '480'),
    # Apariencia
    ('org.tema',                        'string', 'violeta'),
    ('org.fuente_principal',            'string', 'Inter'),
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


_NIVEL_NOMBRES = {1: 'Sede central', 2: 'Delegación', 3: 'Grupo local'}


async def ensure_niveles_organizativos(session) -> None:
    """Inicializa NivelOrganizativo según la profundidad real de agrupaciones.

    Calcula la máxima profundidad jerárquica de unidades_organizativas y crea
    un tipo TERRITORIAL/INTERNA por cada nivel (1=raíz, 2=siguiente, …) si no existe.
    Luego asigna tipo_id a cada agrupacion según su profundidad. Idempotente.
    """
    from sqlalchemy import text

    # Calcular profundidades con CTE recursiva directa en SQL
    depth_rows = (await session.execute(text("""
        WITH RECURSIVE d AS (
          SELECT id, 0 AS depth
          FROM unidades_organizativas
          WHERE agrupacion_padre_id IS NULL AND eliminado = false
          UNION ALL
          SELECT a.id, d.depth + 1
          FROM unidades_organizativas a
          JOIN d ON a.agrupacion_padre_id = d.id
          WHERE a.eliminado = false
        )
        SELECT id, depth FROM d
    """))).fetchall()

    if not depth_rows:
        return  # sin agrupaciones, nada que hacer

    max_depth = max(r.depth for r in depth_rows)

    # Obtener tipos territoriales ya existentes por nivel
    existing_tipos = {
        t.nivel: t
        for t in (await session.execute(
            select(NivelOrganizativo).where(
                NivelOrganizativo.eliminado == False,
                NivelOrganizativo.naturaleza == NaturalezaUnidad.TERRITORIAL,
            )
        )).scalars()
        if t.nivel is not None
    }

    now = datetime.utcnow()
    padre_id = None
    for nivel in range(1, max_depth + 2):
        if nivel not in existing_tipos:
            nombre = _NIVEL_NOMBRES.get(nivel, f'Nivel {nivel}')
            tipo = NivelOrganizativo(
                id=uuid.uuid4(),
                nombre=nombre,
                naturaleza=NaturalezaUnidad.TERRITORIAL,
                vinculo=VinculoUnidad.INTERNA,
                nivel=nivel,
                padre_tipo_id=padre_id,
                activo=True,
            )
            # BaseModel audit fields
            tipo.fecha_creacion = now
            tipo.eliminado = False
            session.add(tipo)
            await session.flush()
            existing_tipos[nivel] = tipo
            print(f"[bootstrap] NivelOrganizativo nivel={nivel} '{nombre}' creado")
        padre_id = existing_tipos[nivel].id

    # Asignar tipo_id a agrupaciones según su profundidad (depth → nivel = depth+1)
    depth_map = {str(r.id): r.depth for r in depth_rows}
    agrupaciones = (await session.execute(
        select(UnidadOrganizativa).where(UnidadOrganizativa.eliminado == False)
    )).scalars().all()

    updated = 0
    for agr in agrupaciones:
        depth = depth_map.get(str(agr.id))
        if depth is None:
            continue
        nivel_esperado = depth + 1
        tipo_esperado = existing_tipos.get(nivel_esperado)
        if tipo_esperado and agr.tipo_id != tipo_esperado.id:
            agr.tipo_id = tipo_esperado.id
            updated += 1

    if updated:
        await session.flush()
        print(f"[bootstrap] Agrupaciones con tipo_id actualizado: {updated}")


_TEMAS = [
    {
        "nombre": "Violeta", "slug": "violeta",
        "t50": "#f5f3ff", "t100": "#ede9fe", "t200": "#ddd6fe", "t300": "#c4b5fd",
        "t400": "#a78bfa", "t500": "#8b5cf6", "t600": "#7c3aed", "t700": "#6d28d9",
        "t800": "#5b21b6", "t900": "#4c1d95",
        "sidebar": "hsl(262,82%,20%)", "topbar": "#ffffff", "page_bg": "#f5f3ff",
        "card_bg": "#ffffff", "text_main": "#111827", "text_muted": "#6b7280",
        "border_color": "#e5e7eb",
    },
    {
        "nombre": "Azul", "slug": "azul",
        "t50": "#eff6ff", "t100": "#dbeafe", "t200": "#bfdbfe", "t300": "#93c5fd",
        "t400": "#60a5fa", "t500": "#3b82f6", "t600": "#2563eb", "t700": "#1d4ed8",
        "t800": "#1e40af", "t900": "#1e3a8a",
        "sidebar": "hsl(219,82%,20%)", "topbar": "#ffffff", "page_bg": "#eff6ff",
        "card_bg": "#ffffff", "text_main": "#111827", "text_muted": "#6b7280",
        "border_color": "#e5e7eb",
    },
    {
        "nombre": "Esmeralda", "slug": "esmeralda",
        "t50": "#ecfdf5", "t100": "#d1fae5", "t200": "#a7f3d0", "t300": "#6ee7b7",
        "t400": "#34d399", "t500": "#10b981", "t600": "#059669", "t700": "#047857",
        "t800": "#065f46", "t900": "#064e3b",
        "sidebar": "hsl(158,75%,15%)", "topbar": "#ffffff", "page_bg": "#ecfdf5",
        "card_bg": "#ffffff", "text_main": "#111827", "text_muted": "#6b7280",
        "border_color": "#e5e7eb",
    },
    {
        "nombre": "Granate", "slug": "granate",
        "t50": "#fff1f2", "t100": "#ffe4e6", "t200": "#fecdd3", "t300": "#fda4af",
        "t400": "#fb7185", "t500": "#f43f5e", "t600": "#e11d48", "t700": "#be123c",
        "t800": "#9f1239", "t900": "#881337",
        "sidebar": "hsl(344,80%,18%)", "topbar": "#ffffff", "page_bg": "#fff1f2",
        "card_bg": "#ffffff", "text_main": "#111827", "text_muted": "#6b7280",
        "border_color": "#e5e7eb",
    },
    {
        "nombre": "Pizarra", "slug": "pizarra",
        "t50": "#f8fafc", "t100": "#f1f5f9", "t200": "#e2e8f0", "t300": "#cbd5e1",
        "t400": "#94a3b8", "t500": "#64748b", "t600": "#475569", "t700": "#334155",
        "t800": "#1e293b", "t900": "#0f172a",
        "sidebar": "hsl(215,28%,17%)", "topbar": "#ffffff", "page_bg": "#f8fafc",
        "card_bg": "#ffffff", "text_main": "#111827", "text_muted": "#6b7280",
        "border_color": "#e5e7eb",
    },
    {
        "nombre": "Ámbar", "slug": "ambar",
        "t50": "#fffbeb", "t100": "#fef3c7", "t200": "#fde68a", "t300": "#fcd34d",
        "t400": "#fbbf24", "t500": "#f59e0b", "t600": "#d97706", "t700": "#b45309",
        "t800": "#92400e", "t900": "#78350f",
        "sidebar": "hsl(25,75%,18%)", "topbar": "#ffffff", "page_bg": "#fffbeb",
        "card_bg": "#ffffff", "text_main": "#111827", "text_muted": "#6b7280",
        "border_color": "#e5e7eb",
    },
]


async def ensure_temas_ui(session) -> None:
    """Crea o actualiza los temas de UI predefinidos. Idempotente por slug."""
    added = updated = 0
    for t in _TEMAS:
        existing = (
            await session.execute(select(TemaUI).where(TemaUI.slug == t["slug"]))
        ).scalar_one_or_none()
        if existing is None:
            session.add(TemaUI(
                id=uuid.uuid4(), nombre=t["nombre"], slug=t["slug"],
                t50=t["t50"], t100=t["t100"], t200=t["t200"], t300=t["t300"],
                t400=t["t400"], t500=t["t500"], t600=t["t600"], t700=t["t700"],
                t800=t["t800"], t900=t["t900"],
                sidebar=t["sidebar"], topbar=t["topbar"], page_bg=t["page_bg"],
                card_bg=t["card_bg"], text_main=t["text_main"],
                text_muted=t["text_muted"], border_color=t["border_color"],
                sistema=True, activo=True,
            ))
            added += 1
        else:
            for k in ("t50","t100","t200","t300","t400","t500","t600","t700","t800","t900",
                      "sidebar","topbar","page_bg","card_bg","text_main","text_muted","border_color"):
                setattr(existing, k, t[k])
            updated += 1
    if added or updated:
        await session.flush()
        print(f"[bootstrap] TemaUI: +{added} creados, ~{updated} actualizados")


_TIPOS_GRUPO = [
    {"nombre": "Permanente", "descripcion": "Grupo estable con actividad continuada", "es_permanente": True,  "activo": True},
    {"nombre": "Temporal",   "descripcion": "Grupo creado para un proyecto o campaña concreta", "es_permanente": False, "activo": True},
    {"nombre": "Comisión",   "descripcion": "Comisión de trabajo específica",          "es_permanente": True,  "activo": True},
]

_TIPOS_ACCION = [
    {"id": uuid.UUID("11111111-0001-0000-0000-000000000001"), "nombre": "Evento público",        "descripcion": "Concentración, mitin, marcha o acto público",       "tiene_lugar": True,  "tiene_participantes": True},
    {"id": uuid.UUID("11111111-ac01-0000-0000-000000000002"), "nombre": "Reunión",               "descripcion": "Reunión interna del grupo o de coordinación",       "tiene_lugar": True,  "tiene_participantes": True},
    {"id": uuid.UUID("11111111-ac01-0000-0000-000000000003"), "nombre": "Taller / Formación",    "descripcion": "Actividad formativa o de capacitación",             "tiene_lugar": True,  "tiene_participantes": True},
    {"id": uuid.UUID("11111111-ac01-0000-0000-000000000004"), "nombre": "Acción de comunicación","descripcion": "Nota de prensa, publicación, campaña en redes",      "tiene_lugar": False, "tiene_participantes": False},
    {"id": uuid.UUID("11111111-ac01-0000-0000-000000000005"), "nombre": "Acción legal",          "descripcion": "Denuncia, recurso, acción judicial o administrativa","tiene_lugar": False, "tiene_participantes": False},
    {"id": uuid.UUID("11111111-ac01-0000-0000-000000000006"), "nombre": "Trabajo voluntario",    "descripcion": "Jornada de voluntariado, recogida de firmas",        "tiene_lugar": True,  "tiene_participantes": True},
    {"id": uuid.UUID("11111111-ac01-0000-0000-000000000007"), "nombre": "Recaudación",           "descripcion": "Campaña de fundraising, colecta, subvención",       "tiene_lugar": False, "tiene_participantes": False},
]

_ESTADOS_ACCION = [
    {"id": uuid.UUID("22222222-ac01-0000-0000-000000000001"), "nombre": "Propuesta",             "orden": 1, "es_inicial": True},
    {"id": uuid.UUID("22222222-ac01-0000-0000-000000000007"), "nombre": "Pendiente aprobación",  "orden": 2},
    {"id": uuid.UUID("22222222-ac01-0000-0000-000000000002"), "nombre": "Aprobada",              "orden": 3},
    {"id": uuid.UUID("22222222-ac01-0000-0000-000000000003"), "nombre": "En preparación",       "orden": 4},
    {"id": uuid.UUID("22222222-ac01-0000-0000-000000000004"), "nombre": "En curso",              "orden": 5},
    {"id": uuid.UUID("22222222-ac01-0000-0000-000000000005"), "nombre": "Finalizada",            "orden": 6, "es_final": True},
    {"id": uuid.UUID("22222222-ac01-0000-0000-000000000006"), "nombre": "Cancelada",             "orden": 7, "es_final": True},
]

_TIPOS_CAMPANIA = [
    "Recogida de firmas",
    "Sensibilización",
    "Captación de socios",
    "Campaña formativa",
    "Movilización",
    "Acción legal/institucional",
    "Comunicación mediática",
]

_ESTADOS_CAMPANIA = [
    {"id": uuid.UUID("f181fc67-a7e1-44db-8b57-344f37bfe1c4"), "nombre": "Borrador",   "orden": 1, "es_inicial": True,  "color": "#6B7280", "es_inmutable": True},
    {"id": uuid.UUID("2a55d055-7055-4657-9f1d-30ba76277bd6"), "nombre": "Programada", "orden": 2,                       "color": "#3B82F6", "es_inmutable": True},
    {"id": uuid.UUID("c7d882d2-1aa0-4e74-b212-95ea731c19a0"), "nombre": "En curso",   "orden": 3,                       "color": "#10B981", "es_inmutable": True},
    {"id": uuid.UUID("05b3edc1-1230-48ee-b7e5-fb7c5f632eff"), "nombre": "Pausada",    "orden": 4,                       "color": "#F59E0B", "es_inmutable": True},
    {"id": uuid.UUID("7db81ba1-b5ed-4834-8b11-dd1d6c46d71f"), "nombre": "Finalizada", "orden": 5, "es_final": True,    "color": "#6366F1", "es_inmutable": True},
    {"id": uuid.UUID("156dbbf9-46de-4550-ab2a-a7fef2a546ff"), "nombre": "Cancelada",  "orden": 6, "es_final": True,    "color": "#EF4444", "es_inmutable": True},
]

_TIPOS_MIEMBRO = [
    {"nombre": "Ordinario",    "descripcion": "Miembro de pleno derecho",        "requiere_cuota": True,  "puede_votar": True,  "orden": 1},
    {"nombre": "De honor",     "descripcion": "Miembro honorario",               "requiere_cuota": False, "puede_votar": False, "orden": 2},
    {"nombre": "Simpatizante", "descripcion": "Simpatizante sin derecho a voto", "requiere_cuota": False, "puede_votar": False, "orden": 3},
]

_ESTADOS_MIEMBRO = [
    {"nombre": "Alta",       "descripcion": "Miembro activo en la organización",      "color": "#28A745", "orden": 1, "es_inicial": True},
    {"nombre": "Pendiente",  "descripcion": "Alta solicitada, pendiente de revisión", "color": "#FFC107", "orden": 2},
    {"nombre": "Suspendido", "descripcion": "Miembro temporalmente suspendido",       "color": "#FFA500", "orden": 3},
    {"nombre": "Baja",       "descripcion": "Miembro dado de baja definitiva",        "color": "#DC3545", "orden": 4, "es_final": True},
]


async def ensure_catalogos_iniciales(session) -> None:
    """Puebla los catálogos operativos si están vacíos. Idempotente."""
    now = datetime.utcnow()
    totals: dict[str, int] = {}

    # TipoGrupo
    for d in _TIPOS_GRUPO:
        if not (await session.execute(select(TipoGrupo).where(TipoGrupo.nombre == d["nombre"]))).scalar_one_or_none():
            session.add(TipoGrupo(id=uuid.uuid4(), **d))
            totals["TipoGrupo"] = totals.get("TipoGrupo", 0) + 1

    # TipoAccion (UUIDs fijos)
    for d in _TIPOS_ACCION:
        if not await session.get(TipoAccion, d["id"]):
            session.add(TipoAccion(**d))
            totals["TipoAccion"] = totals.get("TipoAccion", 0) + 1

    # EstadoAccion (por nombre — previene duplicados si ya existe con otro UUID)
    for d in _ESTADOS_ACCION:
        if not (await session.execute(select(EstadoAccion).where(EstadoAccion.nombre == d["nombre"]))).scalar_one_or_none():
            session.add(EstadoAccion(**d))
            totals["EstadoAccion"] = totals.get("EstadoAccion", 0) + 1

    # TipoCampania
    for nombre in _TIPOS_CAMPANIA:
        if not (await session.execute(select(TipoCampania).where(TipoCampania.nombre == nombre))).scalar_one_or_none():
            session.add(TipoCampania(id=uuid.uuid4(), nombre=nombre, activo=True))
            totals["TipoCampania"] = totals.get("TipoCampania", 0) + 1

    # EstadoCampania (por nombre — previene duplicados si ya existe con otro UUID)
    for d in _ESTADOS_CAMPANIA:
        if not (await session.execute(select(EstadoCampania).where(EstadoCampania.nombre == d["nombre"]))).scalar_one_or_none():
            session.add(EstadoCampania(**d))
            totals["EstadoCampania"] = totals.get("EstadoCampania", 0) + 1

    # TipoMiembro
    for d in _TIPOS_MIEMBRO:
        if not (await session.execute(select(TipoMiembro).where(TipoMiembro.nombre == d["nombre"]))).scalar_one_or_none():
            session.add(TipoMiembro(id=uuid.uuid4(), activo=True, **d))
            totals["TipoMiembro"] = totals.get("TipoMiembro", 0) + 1

    # EstadoMiembro
    for d in _ESTADOS_MIEMBRO:
        if not (await session.execute(select(EstadoMiembro).where(EstadoMiembro.nombre == d["nombre"]))).scalar_one_or_none():
            session.add(EstadoMiembro(id=uuid.uuid4(), activo=True, **d))
            totals["EstadoMiembro"] = totals.get("EstadoMiembro", 0) + 1

    if totals:
        await session.flush()
        for k, v in totals.items():
            print(f"[bootstrap] {k}: +{v} registros creados")


_PLANTILLAS_EMAIL = [
    {
        "codigo": "CAMP_APROBACION",
        "nombre": "Convocatoria de campaña",
        "descripcion": "Correo enviado a la membresía del ámbito territorial para anunciar la aprobación y programación de una campaña y captar voluntarios.",
        "modulo": "campanias",
        "asunto": "{{ nombre_campania }} — Te necesitamos",
        "cuerpo_html": """\
<p>Estimado/a {{ nombre_miembro }},</p>

<p>
  Te anunciamos la aprobación de la campaña
  <strong>{{ nombre_campania }}</strong>{% if lema %} — <em>{{ lema }}</em>{% endif %}.
</p>

{% if objetivo_principal %}
<p>
  <strong>Objetivos:</strong><br>
  {{ objetivo_principal }}
</p>
{% endif %}

{% if presupuesto_estimado %}
<p>
  Su consecución implica un presupuesto estimado de <strong>{{ presupuesto_estimado }} €</strong>.
</p>
{% endif %}

{% if requisitos_recursos %}
<p>
  <strong>Equipo necesario:</strong>
</p>
<ul>
  {% for req in requisitos_recursos %}
  <li>{{ req.habilidad }} — nivel {{ req.nivel }}: {{ req.horas }} horas</li>
  {% endfor %}
</ul>
{% endif %}

<p>
  Si tienes tiempo y ganas de participar,
  <a href="{{ url_campanias }}">consulta la convocatoria completa en la aplicación</a>
  y postúlate para formar parte del equipo de campaña.
</p>

<p>¡Contamos contigo!</p>

<p>
  Un saludo,<br>
  <strong>{{ nombre_organizacion }}</strong>
</p>
""",
        "variables_disponibles": [
            {"clave": "nombre_miembro",        "descripcion": "Nombre y primer apellido del destinatario"},
            {"clave": "nombre_campania",        "descripcion": "Nombre de la campaña"},
            {"clave": "lema",                   "descripcion": "Lema o eslogan de la campaña"},
            {"clave": "objetivo_principal",     "descripcion": "Texto del objetivo principal"},
            {"clave": "presupuesto_estimado",   "descripcion": "Presupuesto estimado en euros"},
            {"clave": "requisitos_recursos",    "descripcion": "Lista de requisitos de horas ({habilidad, nivel, horas})"},
            {"clave": "url_campanias",          "descripcion": "URL de la sección de campañas en la aplicación"},
            {"clave": "nombre_organizacion",    "descripcion": "Nombre de la organización"},
        ],
    },
]


async def ensure_plantillas_email(session) -> None:
    """Crea plantillas de email predeterminadas si no existen. Idempotente por código."""
    now = datetime.utcnow()
    added = 0
    for p in _PLANTILLAS_EMAIL:
        existing = (
            await session.execute(
                select(PlantillaEmail).where(PlantillaEmail.codigo == p["codigo"])
            )
        ).scalar_one_or_none()
        if existing is None:
            session.add(PlantillaEmail(
                id=uuid.uuid4(),
                codigo=p["codigo"],
                nombre=p["nombre"],
                descripcion=p["descripcion"],
                modulo=p["modulo"],
                asunto=p["asunto"],
                cuerpo_html=p["cuerpo_html"],
                variables_disponibles=p["variables_disponibles"],
                activo=True,
            ))
            added += 1
    if added:
        await session.flush()
        print(f"[bootstrap] PlantillaEmail: +{added} creadas")


async def sync_superadmin_all_transactions(session) -> None:
    """Enlaza SUPERADMIN con TODAS las transacciones presentes en la DB.

    Garantiza que el SUPERADMIN tenga acceso a las transacciones declaradas
    en catalog.py (añadidas por CatalogSyncService en el lifespan de FastAPI),
    que no estaban en la DB cuando bootstrap.py corrió por primera vez.
    """
    superadmin = (
        await session.execute(select(Rol).where(Rol.codigo == SUPERADMIN_CODE))
    ).scalar_one_or_none()
    if superadmin is None:
        return

    all_trans_ids = frozenset(
        row[0] for row in (await session.execute(select(Transaccion.id))).all()
    )
    existing_links = frozenset(
        row[0] for row in (await session.execute(
            select(RolTransaccion.transaccion_id).where(RolTransaccion.rol_id == superadmin.id)
        )).all()
    )

    missing = all_trans_ids - existing_links
    if not missing:
        return

    now = datetime.utcnow()
    for trans_id in missing:
        session.add(RolTransaccion(
            rol_id=superadmin.id,
            transaccion_id=trans_id,
            fecha_creacion=now,
            eliminado=False,
        ))
    await session.flush()
    print(f"[lifespan] SUPERADMIN: +{len(missing)} transacciones enlazadas")


async def sync_roles_funcionales_catalog(session) -> None:
    """Re-enlaza los roles funcionales con las transacciones de catalog.py.

    seed_roles_funcionales() corre en bootstrap antes de que CatalogSyncService
    sincronice las transacciones declaradas en los catalog.py de cada módulo
    (p. ej. ECO_PRESUPUESTO_*). Esta función vuelve a ejecutar el seed con el
    catálogo ya completo en la BD. Es idempotente.
    """
    todas = {
        t.codigo: t
        for t in (await session.execute(select(Transaccion))).scalars()
    }
    await seed_roles_funcionales(session, todas)


_PLANIFICADOR_CODE = "PLANIFICADOR"


async def ensure_coordinadores_usuarios(session) -> None:
    """Crea cuentas de usuario y asigna rol PLANIFICADOR a los coordinadores importados.

    Idempotente: no duplica usuarios ni roles. Solo actúa sobre nombramientos
    con tipo_origen='IMPORTACION' y estado='ACTIVO'.
    """
    nombramientos = (await session.execute(
        select(HistorialNombramiento).where(
            HistorialNombramiento.tipo_origen == 'IMPORTACION',
            HistorialNombramiento.estado == 'ACTIVO',
            HistorialNombramiento.eliminado == False,
        )
    )).scalars().all()

    if not nombramientos:
        return

    planificador = (await session.execute(
        select(Rol).where(Rol.codigo == _PLANIFICADOR_CODE)
    )).scalar_one_or_none()
    if planificador is None:
        print(f"[bootstrap] Rol {_PLANIFICADOR_CODE} no encontrado; omitiendo coordinadores")
        return

    pwd_hash = hash_password("CAMBIAME")
    now = datetime.utcnow()
    creados = roles_creados = 0

    for nombramiento in nombramientos:
        miembro = (await session.execute(
            select(Miembro).where(Miembro.id == nombramiento.miembro_id)
        )).scalar_one_or_none()

        if not miembro or not miembro.email:
            continue

        email = miembro.email.lower().strip()

        # Buscar primero por miembro_id (constraint único): un miembro tiene como
        # mucho un usuario, aunque su email haya cambiado respecto al de la cuenta.
        usuario = (await session.execute(
            select(Usuario).where(Usuario.miembro_id == miembro.id, Usuario.eliminado == False)
        )).scalar_one_or_none()
        if usuario is None:
            usuario = (await session.execute(
                select(Usuario).where(Usuario.email == email, Usuario.eliminado == False)
            )).scalar_one_or_none()

        if usuario is None:
            usuario = Usuario(
                id=uuid.uuid4(),
                email=email,
                password_hash=pwd_hash,
                activo=True,
                miembro_id=miembro.id,
                intentos_login=0,
                eliminado=False,
                fecha_creacion=now,
            )
            session.add(usuario)
            await session.flush()
            creados += 1

        existing_role = (await session.execute(
            select(UsuarioRol).where(
                UsuarioRol.usuario_id == usuario.id,
                UsuarioRol.rol_id == planificador.id,
                UsuarioRol.agrupacion_id == nombramiento.agrupacion_id,
                UsuarioRol.eliminado == False,
            )
        )).scalar_one_or_none()

        if existing_role is None:
            session.add(UsuarioRol(
                id=uuid.uuid4(),
                usuario_id=usuario.id,
                rol_id=planificador.id,
                agrupacion_id=nombramiento.agrupacion_id,
                activo=True,
                eliminado=False,
                nombramiento_id=nombramiento.id,
                fecha_creacion=now,
            ))
            roles_creados += 1

    if creados or roles_creados:
        await session.flush()
        print(f"[bootstrap] Coordinadores: +{creados} usuarios, +{roles_creados} roles PLANIFICADOR")


async def main() -> None:
    async with async_session() as session:
        try:
            transacciones = await sync_transacciones(session)
            print(f"[bootstrap] Transacciones sincronizadas: {len(transacciones)}")
            superadmin = await ensure_superadmin(session, transacciones)
            print(f"[bootstrap] Rol SUPERADMIN listo (id={superadmin.id})")
            await ensure_admin_user(session, superadmin)
            await ensure_parametros_organizacion(session)
            await ensure_niveles_organizativos(session)
            await ensure_temas_ui(session)
            await ensure_catalogos_iniciales(session)
            await ensure_plantillas_email(session)
            await seed_comunicacion(session)
            await seed_roles_funcionales(session, transacciones)
            await ensure_coordinadores_usuarios(session)
            await session.commit()
        except Exception:
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
