"""
Seed de catálogos de voluntariado: NivelEstudios, NivelHabilidad,
CategoriaHabilidad y Habilidad.

Idempotente: omite registros que ya existen por nombre.
"""
import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.database import get_database_url
from app.modules.membresia.models.nivel_estudios import NivelEstudios
from app.modules.membresia.models.nivel_habilidad import NivelHabilidad
from app.modules.membresia.models.categoria_habilidad import CategoriaHabilidad
from app.modules.membresia.models.habilidad import Habilidad


# ── Niveles de estudios (orden ascendente de formación) ──────────────────────
NIVELES_ESTUDIOS = [
    (0,  "Sin estudios",         "Sin estudios formales"),
    (1,  "Educación Primaria",   "Educación primaria completa"),
    (2,  "ESO",                  "Educación Secundaria Obligatoria o equivalente"),
    (3,  "Bachillerato",         "Bachillerato o equivalente"),
    (4,  "FP de grado medio",    "Ciclo formativo de grado medio"),
    (5,  "FP de grado superior", "Ciclo formativo de grado superior"),
    (6,  "Grado universitario",  "Grado, Diplomatura o Licenciatura"),
    (7,  "Máster / Postgrado",   "Máster oficial o propio, Postgrado"),
    (8,  "Doctorado",            "Doctor/a"),
]

# ── Niveles de habilidad / experiencia ───────────────────────────────────────
NIVELES_HABILIDAD = [
    (0, "Principiante", "Conocimientos básicos, sin experiencia práctica"),
    (1, "Suficiente",   "Puede desenvolverse con autonomía en tareas sencillas"),
    (2, "Bueno",        "Dominio sólido, capaz de resolver situaciones complejas"),
    (3, "Experto/a",    "Dominio avanzado, puede formar a otras personas"),
]

# ── Habilidades (nombre, categoría, descripción) ─────────────────────────────
HABILIDADES = [
    # Comunicación
    ("Redacción y comunicación escrita",     "Comunicación", "Redacción de textos, informes y comunicados"),
    ("Redes sociales / Community mgmt",      "Comunicación", "Gestión de perfiles y campañas en redes sociales"),
    ("Diseño gráfico y maquetación",         "Comunicación", "Carteles, folletos y materiales visuales"),
    ("Fotografía y vídeo",                   "Comunicación", "Producción audiovisual y edición de contenido"),
    ("Relaciones con medios de prensa",      "Comunicación", "Notas de prensa, portavoces y gestión de entrevistas"),
    ("Oratoria y presentaciones en público", "Comunicación", "Charlas, ponencias y dinamización de actos"),

    # Organización
    ("Organización de eventos",              "Organización", "Coordinación logística de actos y jornadas"),
    ("Coordinación de voluntarios",          "Organización", "Gestión y motivación de equipos de voluntariado"),
    ("Gestión administrativa",               "Organización", "Tramitación, archivo y gestión documental"),
    ("Gestión de proyectos",                 "Organización", "Planificación, seguimiento y cierre de proyectos"),

    # Legal
    ("Derecho general",                      "Legal",        "Asesoría jurídica de carácter general"),
    ("Derecho administrativo",               "Legal",        "Recursos, reclamaciones y procedimientos administrativos"),
    ("Relaciones institucionales",           "Legal",        "Interlocución con administraciones y actividades de lobbying"),

    # Formación
    ("Docencia y formación",                 "Formación",    "Impartición de cursos, talleres y sesiones formativas"),
    ("Elaboración de materiales didácticos", "Formación",    "Creación de contenidos educativos y guías pedagógicas"),
    ("Dinamización de grupos",               "Formación",    "Facilitación de debates y metodologías participativas"),

    # Tecnología
    ("Desarrollo web",                       "Tecnología",   "Desarrollo frontend, backend o gestión de CMS"),
    ("Soporte informático",                  "Tecnología",   "Mantenimiento de equipos y resolución de incidencias"),
    ("SEO y marketing digital",              "Tecnología",   "Posicionamiento web y gestión de campañas online"),

    # Idiomas
    ("Inglés",                               "Idiomas",      "Nivel comunicativo o superior"),
    ("Francés",                              "Idiomas",      "Nivel comunicativo o superior"),
    ("Traducción e interpretación",          "Idiomas",      "Traducción de documentos e interpretación simultánea"),

    # Finanzas
    ("Contabilidad",                         "Finanzas",     "Registro contable y gestión económica de la asociación"),
    ("Fundraising / captación de fondos",    "Finanzas",     "Búsqueda y gestión de donantes y patrocinadores"),
    ("Gestión de subvenciones",              "Finanzas",     "Solicitud, seguimiento y justificación de ayudas públicas"),

    # Campo
    ("Recogida de firmas presencial",        "Campo",        "Organización de mesas de recogida y captación en calle"),
    ("Difusión de materiales",               "Campo",        "Buzoneo, pegada de carteles y reparto de folletos"),
    ("Atención al público",                  "Campo",        "Información y orientación a ciudadanos en actos y stands"),
]


async def seed(session: AsyncSession):
    # ── NivelEstudios ────────────────────────────────────────────────────────
    print("\n— Niveles de estudios —")
    for orden, nombre, descripcion in NIVELES_ESTUDIOS:
        res = await session.execute(select(NivelEstudios).where(NivelEstudios.nombre == nombre))
        if res.scalar_one_or_none():
            print(f"  [ya existe] {nombre}")
            continue
        session.add(NivelEstudios(id=uuid.uuid4(), nombre=nombre, descripcion=descripcion, orden=orden, activo=True))
        print(f"  [+] {nombre}")
    await session.commit()

    # ── NivelHabilidad ───────────────────────────────────────────────────────
    print("\n— Niveles de habilidad —")
    for orden, nombre, descripcion in NIVELES_HABILIDAD:
        res = await session.execute(select(NivelHabilidad).where(NivelHabilidad.nombre == nombre))
        if res.scalar_one_or_none():
            print(f"  [ya existe] {nombre}")
            continue
        session.add(NivelHabilidad(id=uuid.uuid4(), nombre=nombre, descripcion=descripcion, orden=orden, activo=True))
        print(f"  [+] {nombre}")
    await session.commit()

    # ── CategoriaHabilidad (se deducen de HABILIDADES) ───────────────────────
    print("\n— Categorías de habilidad —")
    categorias_vistas = {}
    for _, cat_nombre, _ in HABILIDADES:
        if cat_nombre in categorias_vistas:
            continue
        res = await session.execute(select(CategoriaHabilidad).where(CategoriaHabilidad.nombre == cat_nombre))
        obj = res.scalar_one_or_none()
        if obj:
            categorias_vistas[cat_nombre] = obj.id
            print(f"  [ya existe] {cat_nombre}")
        else:
            new_id = uuid.uuid4()
            session.add(CategoriaHabilidad(id=new_id, nombre=cat_nombre, activo=True))
            categorias_vistas[cat_nombre] = new_id
            print(f"  [+] {cat_nombre}")
    await session.commit()

    # ── Habilidades ──────────────────────────────────────────────────────────
    print("\n— Habilidades de voluntariado —")
    creadas = 0
    for nombre, cat_nombre, descripcion in HABILIDADES:
        res = await session.execute(select(Habilidad).where(Habilidad.nombre == nombre))
        if res.scalar_one_or_none():
            print(f"  [ya existe] {nombre}")
            continue
        session.add(Habilidad(
            id=uuid.uuid4(),
            nombre=nombre,
            categoria_id=categorias_vistas.get(cat_nombre),
            descripcion=descripcion,
            activo=True,
        ))
        print(f"  [+] [{cat_nombre}] {nombre}")
        creadas += 1
    await session.commit()
    print(f"\n[OK] {creadas} habilidades nuevas.")


async def main():
    url = get_database_url()
    engine = create_async_engine(
        url, echo=False,
        connect_args={"server_settings": {"jit": "off"}, "statement_cache_size": 0},
    )
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        await seed(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
