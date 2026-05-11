"""
Seed de campañas reales de Europa Laica (laicismo.org).

Idempotente: omite campañas que ya existen por nombre.
Usa los tipos y estados existentes (lookup por nombre).
"""
import asyncio
import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from app.core.database import get_database_url


# ── Datos de las campañas ────────────────────────────────────────────────────
# Formato:
# (nombre, tipo_nombre, estado_nombre, fecha_inicio, fecha_fin,
#  lema, descripcion_corta, objetivo_principal, meta_firmas, url_externa)
#
# fecha_inicio/fin: None o date(yyyy, m, d)
# meta_firmas: None o entero

CAMPANIAS = [
    # ── Recogida de firmas ──────────────────────────────────────────────────
    (
        "Por una escuela pública, laica y gratuita",
        "Recogida de firmas", "En Curso",
        date(2019, 9, 1), None,
        "La escuela pública es de todos y todas",
        "Petición para que la asignatura de Religión sea retirada del currículo escolar obligatorio "
        "y de los conciertos con centros religiosos.",
        "Conseguir que el Gobierno elimine la asignatura de Religión de los currículos oficiales "
        "de la educación pública y reforme el sistema de conciertos educativos.",
        100000,
        "https://laicismo.org/campanas/escuela-laica",
    ),
    (
        "Retirada de los crucifijos de los espacios públicos",
        "Recogida de firmas", "En Curso",
        date(2018, 3, 1), None,
        "Los juzgados, comisarías y hospitales son de todos",
        "Petición para que se retiren los símbolos religiosos de edificios públicos: "
        "juzgados, comisarías, hospitales, cuarteles y centros educativos públicos.",
        "Lograr la retirada efectiva de crucifijos y demás símbolos religiosos de todos "
        "los espacios e instituciones del Estado.",
        50000,
        "https://laicismo.org/campanas/crucifijos-espacios-publicos",
    ),
    (
        "Denuncia del Concordato entre España y la Santa Sede",
        "Recogida de firmas", "En Curso",
        date(2017, 1, 15), None,
        "Un Estado laico no puede tener Concordato",
        "El Concordato de 1979 otorga privilegios y exenciones a la Iglesia Católica "
        "incompatibles con la neutralidad del Estado. Pedimos su denuncia formal.",
        "Obtener el apoyo ciudadano necesario para que el Congreso de los Diputados debata "
        "y apruebe la denuncia del Concordato y los Acuerdos de 1979 con la Santa Sede.",
        150000,
        "https://laicismo.org/campanas/concordato",
    ),
    (
        "Fin a las exenciones fiscales de la Iglesia Católica",
        "Recogida de firmas", "En Curso",
        date(2020, 2, 1), None,
        "Que cada entidad tribute según la ley",
        "La Iglesia Católica disfruta de exenciones fiscales en IBI, IVA e IRPF que suponen "
        "miles de millones de euros al año sustraídos a las arcas públicas.",
        "Conseguir la supresión de los privilegios fiscales de la Iglesia Católica, "
        "equiparando su tributación a la de otras entidades sin ánimo de lucro.",
        75000,
        "https://laicismo.org/campanas/exenciones-fiscales",
    ),
    (
        "Recuperación de bienes inmatriculados por la Iglesia",
        "Recogida de firmas", "En Curso",
        date(2021, 6, 1), None,
        "Lo que es del pueblo, al pueblo",
        "La Iglesia Católica inmatriculó más de 34.000 bienes entre 1998 y 2015 "
        "sirviéndose de una ley franquista. Muchos de esos bienes son de titularidad pública.",
        "Lograr la reversión al patrimonio público de los bienes inmatriculados ilegítimamente "
        "y la modificación legislativa que impida nuevas inmatriculaciones.",
        60000,
        "https://laicismo.org/campanas/inmatriculaciones",
    ),
    (
        "No a la Religión evaluable en la escuela pública",
        "Recogida de firmas", "Finalizada",
        date(2014, 10, 1), date(2015, 6, 30),
        "La fe no puntúa",
        "Campaña contra la LOMCE que recuperaba la asignatura de Religión como evaluable "
        "y con efecto en la nota media del expediente académico.",
        "Impedir que la asignatura de Religión vuelva a tener valor académico en la escuela pública.",
        80000,
        "https://laicismo.org/campanas/religion-lomce",
    ),

    # ── Acción legal/institucional ───────────────────────────────────────────
    (
        "Ley Orgánica de Libertad de Conciencia",
        "Acción legal/institucional", "En Curso",
        date(2016, 11, 1), None,
        "Un marco legal para el siglo XXI",
        "España carece de una ley integral de libertad de conciencia. Impulsamos una propuesta "
        "legislativa que reconozca de forma efectiva el derecho a la libertad ideológica y religiosa "
        "de todas las personas, sobre bases laicas.",
        "Conseguir que el Congreso de los Diputados apruebe una Ley Orgánica de Libertad "
        "de Conciencia que derogue la Ley Orgánica de Libertad Religiosa de 1980.",
        None,
        "https://laicismo.org/campanas/ley-libertad-conciencia",
    ),
    (
        "Recurso contra la presencia de la Religión en el currículo LOMLOE",
        "Acción legal/institucional", "Finalizada",
        date(2022, 1, 10), date(2023, 4, 30),
        "Por la plena laicidad del currículo",
        "Recurso ante el Tribunal Supremo por los preceptos de la LOMLOE que mantienen "
        "la Religión en el horario lectivo como asignatura de oferta obligatoria para los centros.",
        "Obtener una sentencia que declare inconstitucionales los artículos de la LOMLOE "
        "que obligan a los centros públicos a impartir Religión.",
        None,
        "https://laicismo.org/campanas/recurso-lomloe",
    ),
    (
        "Neutralidad religiosa en los actos del Estado",
        "Acción legal/institucional", "En Curso",
        date(2019, 5, 1), None,
        "El Estado no tiene religión",
        "Denuncia de la participación institucional de miembros del Gobierno y Jefatura del Estado "
        "en ceremonias religiosas con carácter oficial.",
        "Lograr que los poderes públicos dejen de participar con carácter oficial en actos "
        "religiosos de cualquier confesión y se garantice la neutralidad religiosa del Estado.",
        None,
        "https://laicismo.org/campanas/neutralidad-estado",
    ),

    # ── Sensibilización ─────────────────────────────────────────────────────
    (
        "Por la separación efectiva Iglesia-Estado",
        "Sensibilización", "En Curso",
        date(2015, 9, 1), None,
        "Laicidad: libertad para todas las personas",
        "Campaña de concienciación sobre la necesidad de completar la separación entre "
        "las confesiones religiosas y el Estado español, conforme al artículo 16.3 de la Constitución.",
        "Aumentar el conocimiento ciudadano sobre los privilegios de la Iglesia Católica "
        "y promover el apoyo a políticas que garanticen la laicidad del Estado.",
        None,
        "https://laicismo.org/campanas/separacion-iglesia-estado",
    ),
    (
        "Laicidad en los medios de comunicación públicos",
        "Sensibilización", "En Curso",
        date(2020, 9, 1), None,
        "RTVE es de todos, no solo de los creyentes",
        "RTVE emite programación religiosa con fondos públicos en horarios de máxima audiencia. "
        "Pedimos que los medios públicos sean neutrales en materia religiosa.",
        "Conseguir que RTVE y los medios autonómicos públicos eliminen la programación religiosa "
        "de su parrilla o la equiparen con contenido de otras confesiones y del laicismo.",
        None,
        "https://laicismo.org/campanas/medios-publicos-laicos",
    ),
    (
        "Educación laica para una ciudadanía libre",
        "Sensibilización", "En Curso",
        date(2017, 9, 1), None,
        "Educar en libertad, no en dogmas",
        "Campaña divulgativa sobre la importancia de la educación laica y el pensamiento crítico "
        "frente al adoctrinamiento religioso en edades tempranas.",
        "Extender el conocimiento de los principios de la educación laica entre familias, "
        "docentes y sociedad en general.",
        None,
        "https://laicismo.org/campanas/educacion-laica",
    ),

    # ── Movilización ────────────────────────────────────────────────────────
    (
        "Jornadas Anuales por la Laicidad 2024",
        "Movilización", "Finalizada",
        date(2024, 10, 18), date(2024, 10, 20),
        "Construyendo el Estado laico del siglo XXI",
        "Encuentro anual de personas y colectivos comprometidos con la laicidad. "
        "Debates, conferencias y propuestas de acción colectiva.",
        "Reunir a los movimientos laicos españoles para debatir el estado del laicismo "
        "y coordinar acciones conjuntas durante el próximo año.",
        None,
        "https://laicismo.org/campanas/jornadas-2024",
    ),
    (
        "Jornadas Anuales por la Laicidad 2023",
        "Movilización", "Finalizada",
        date(2023, 10, 20), date(2023, 10, 22),
        "Laicidad y democracia",
        "XVIII edición de las Jornadas Anuales de Europa Laica, dedicadas a analizar "
        "la relación entre laicidad y democracia en el contexto europeo.",
        "Impulsar el debate político y social sobre el papel de la laicidad como base "
        "del sistema democrático.",
        None,
        "https://laicismo.org/campanas/jornadas-2023",
    ),
    (
        "Concentración: Laicidad ya",
        "Movilización", "Finalizada",
        date(2022, 5, 14), date(2022, 5, 14),
        "El Estado es de todos, no de la Iglesia",
        "Concentración en Madrid ante el Ministerio de la Presidencia para exigir "
        "medidas concretas de laicidad al Gobierno de coalición.",
        "Presionar al Gobierno para que cumpla sus compromisos en materia de laicidad "
        "y presente el proyecto de ley de libertad de conciencia.",
        None,
        "https://laicismo.org/campanas/concentracion-2022",
    ),

    # ── Campaña formativa ───────────────────────────────────────────────────
    (
        "Curso: Laicismo y derechos fundamentales",
        "Campaña formativa", "En Curso",
        date(2023, 1, 1), None,
        "Conoce tus derechos, defiende la laicidad",
        "Itinerario formativo online sobre el marco jurídico de la libertad de conciencia "
        "y los derechos fundamentales en España y Europa.",
        "Capacitar a activistas y ciudadanía en el conocimiento jurídico y filosófico "
        "del laicismo para defender sus derechos.",
        None,
        "https://laicismo.org/campanas/curso-laicismo-derechos",
    ),
    (
        "Talleres de educación laica para docentes",
        "Campaña formativa", "Finalizada",
        date(2021, 9, 1), date(2022, 6, 30),
        "Docentes comprometidos con la laicidad",
        "Talleres presenciales y online dirigidos a profesorado de primaria y secundaria "
        "sobre cómo abordar la laicidad y la diversidad religiosa en el aula.",
        "Dotar al profesorado de herramientas pedagógicas para trabajar la laicidad, "
        "el pensamiento crítico y la diversidad de creencias en el entorno escolar.",
        None,
        "https://laicismo.org/campanas/talleres-docentes",
    ),

    # ── Captación de socios ─────────────────────────────────────────────────
    (
        "Hazte socia/o de Europa Laica",
        "Captación de socios", "En Curso",
        date(2015, 1, 1), None,
        "Tu cuota hace posible la laicidad",
        "Campaña permanente de captación de nuevas personas socias para financiar "
        "las actividades de Europa Laica.",
        "Alcanzar y superar los 5.000 socios y socias para garantizar la sostenibilidad "
        "económica de la organización.",
        None,
        "https://laicismo.org/campanas/hazte-socia",
    ),

    # ── Comunicación mediática ──────────────────────────────────────────────
    (
        "Europa Laica en los medios: agenda laica 2024",
        "Comunicación mediática", "Finalizada",
        date(2024, 1, 1), date(2024, 12, 31),
        "Presencia laica en el debate público",
        "Plan de comunicación para aumentar la presencia de Europa Laica en medios "
        "de comunicación, programas de debate y foros de opinión durante 2024.",
        "Incrementar las apariciones en medios nacionales y regionales, publicar "
        "al menos 4 notas de prensa mensuales y participar en debates televisivos.",
        None,
        "https://laicismo.org/prensa",
    ),
    (
        "Redes sociales por la laicidad",
        "Comunicación mediática", "En Curso",
        date(2019, 3, 1), None,
        "#LaicidadYa en todas las redes",
        "Estrategia de presencia y comunicación de Europa Laica en redes sociales: "
        "Twitter/X, Instagram, Facebook y YouTube.",
        "Aumentar la comunidad online de Europa Laica y difundir los valores laicos "
        "a través de contenido de calidad en redes sociales.",
        None,
        "https://laicismo.org/campanas/redes-sociales",
    ),
]


async def seed(session: AsyncSession):
    # ── Cargar lookup tables ─────────────────────────────────────────────────
    tipos = {}
    res = await session.execute(text("SELECT id, nombre FROM tipos_campania WHERE activo = true"))
    for row in res.fetchall():
        tipos[row.nombre] = row.id

    estados = {}
    res = await session.execute(text("SELECT id, nombre FROM estados_campania ORDER BY orden"))
    for row in res.fetchall():
        # Guardar el último que coincida (preferimos los del seed_catalogos)
        estados[row.nombre.strip()] = row.id

    # Agrupación nacional: Europa Laica
    res = await session.execute(
        text("SELECT id FROM agrupaciones_territoriales WHERE nombre = 'Europa Laica' LIMIT 1")
    )
    row = res.fetchone()
    agrupacion_id = row[0] if row else None

    print(f"\n— Tipos disponibles: {list(tipos.keys())}")
    print(f"— Estados disponibles: {list(estados.keys())}")
    print(f"— Agrupación nacional: {'Europa Laica (' + str(agrupacion_id) + ')' if agrupacion_id else 'NO ENCONTRADA'}")

    # ── Insertar campañas ─────────────────────────────────────────────────────
    print("\n— Campañas Europa Laica —")
    creadas = 0
    for (
        nombre, tipo_nombre, estado_nombre,
        fecha_inicio, fecha_fin,
        lema, descripcion_corta, objetivo_principal, meta_firmas, url_externa,
    ) in CAMPANIAS:
        # Idempotencia: skip si ya existe
        res = await session.execute(
            text("SELECT id FROM campanias WHERE nombre = :n"), {"n": nombre}
        )
        if res.fetchone():
            print(f"  [ya existe] {nombre}")
            continue

        tipo_id = tipos.get(tipo_nombre)
        estado_id = estados.get(estado_nombre)

        if not tipo_id:
            print(f"  [WARN] Tipo '{tipo_nombre}' no encontrado, saltando: {nombre}")
            continue
        if not estado_id:
            print(f"  [WARN] Estado '{estado_nombre}' no encontrado, saltando: {nombre}")
            continue

        await session.execute(
            text("""
                INSERT INTO campanias (
                    id, nombre, lema, descripcion_corta, objetivo_principal,
                    tipo_campania_id, estado_id,
                    fecha_inicio_plan, fecha_fin_plan,
                    meta_firmas, url_externa, agrupacion_id
                ) VALUES (
                    :id, :nombre, :lema, :descripcion_corta, :objetivo_principal,
                    :tipo_id, :estado_id,
                    :fecha_inicio, :fecha_fin,
                    :meta_firmas, :url_externa, :agrupacion_id
                )
            """),
            {
                "id": str(uuid.uuid4()),
                "nombre": nombre,
                "lema": lema,
                "descripcion_corta": descripcion_corta,
                "objetivo_principal": objetivo_principal,
                "tipo_id": str(tipo_id),
                "estado_id": str(estado_id),
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "meta_firmas": meta_firmas,
                "url_externa": url_externa,
                "agrupacion_id": str(agrupacion_id) if agrupacion_id else None,
            },
        )
        print(f"  [+] [{tipo_nombre}] {nombre}")
        creadas += 1

    await session.commit()
    print(f"\n[OK] {creadas} campañas nuevas creadas.")


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
