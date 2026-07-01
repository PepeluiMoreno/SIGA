"""Seeding de plantillas de campaña realistas para los 7 tipos de campaña.

⚠️ INCOMPLETO: la lista PLANTILLAS usa TIPOS/METAS/HAB/NIV a nivel de MÓDULO, que se
evalúan al importar (antes de resolver los UUIDs por nombre en seed()), por lo que
peta con KeyError. Para arreglarlo hay que construir PLANTILLAS DENTRO de seed(), tras
llamar a _resolver_catalogos(session). Los catálogos ya se resuelven por nombre (no por
UUID fijo) — solo falta mover la construcción de datos. Mientras tanto, las plantillas
se crean por UI (diseñándolas o vía "guardar campaña como plantilla").

Ejecutar con:
    docker exec siga_dev_backend python -m app.scripts.seed_plantillas_campania
"""
import asyncio
import uuid
from decimal import Decimal

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session as async_session_factory
from app.modules.actividades.models.campana import (
    PlantillaCampania, PlantillaMeta, PlantillaPartida,
    PlantillaActividad, PlantillaTarea,
)

# ── UUIDs de catálogos (de la BD) ─────────────────────────────────────────────

# Resolución de catálogos POR NOMBRE (no por UUID fijo). Cada clave del seed se mapea
# al nombre real del catálogo; los UUIDs se resuelven de la BD al ejecutar. Así el seed
# no depende de UUIDs concretos (que cambian entre siembras). Se rellenan en seed().
TIPOS: dict = {}
METAS: dict = {}
HAB: dict = {}
NIV: dict = {}

# clave del seed → nombre exacto del catálogo en BD.
_TIPOS_NOMBRE = {
    'captacion_socios': 'Captación de socios', 'recogida_firmas': 'Recogida de firmas',
    'formativa': 'Campaña formativa', 'sensibilizacion': 'Sensibilización',
    'comunicacion_mediatica': 'Comunicación mediática', 'movilizacion': 'Movilización',
    'accion_legal': 'Acción legal/institucional',
}
_METAS_NOMBRE = {
    'recaudacion': 'Recaudación', 'participantes': 'Participantes', 'firmas': 'Firmas',
    'visitas': 'Visitas', 'menciones': 'Menciones',
}
_HAB_NOMBRE = {
    'firmas_presencial': 'Recogida de firmas presencial', 'rrss': 'Redes sociales / Community mgmt',
    'prensa': 'Relaciones con medios de prensa', 'fotovideo': 'Fotografía y vídeo',
    'dinamizacion': 'Dinamización de grupos', 'relac_institucional': 'Relaciones institucionales',
    'docencia': 'Docencia y formación', 'web': 'Desarrollo web', 'seo': 'SEO y marketing digital',
    'derecho_admin': 'Derecho administrativo', 'materiales_didact': 'Elaboración de materiales didácticos',
    'redaccion': 'Redacción y comunicación escrita', 'soporte_inf': 'Soporte informático',
    'gestion_proyectos': 'Gestión de proyectos', 'fundraising': 'Fundraising / captación de fondos',
    'diseno': 'Diseño gráfico y maquetación', 'oratoria': 'Oratoria y presentaciones en público',
    'atencion_publico': 'Atención al público', 'difusion': 'Difusión de materiales',
    'coord_voluntarios': 'Coordinación de voluntarios', 'eventos': 'Organización de eventos',
    'adm': 'Gestión administrativa', 'derecho': 'Derecho general',
}
_NIV_NOMBRE = {
    'principiante': 'Principiante', 'suficiente': 'Suficiente', 'bueno': 'Bueno', 'experto': 'Experto/a',
}


async def _resolver_catalogos(session):
    """Rellena TIPOS/METAS/HAB/NIV resolviendo cada nombre a su UUID en la BD."""
    from sqlalchemy import text
    async def _map(tabla, claves_nombre):
        rows = dict((n, i) for (i, n) in (await session.execute(text(f"SELECT id, nombre FROM {tabla}"))).all())
        out = {}
        for clave, nombre in claves_nombre.items():
            if nombre in rows:
                out[clave] = rows[nombre]
            else:
                print(f"  ⚠ {tabla}: no existe '{nombre}' (clave {clave}); se omitirá")
        return out
    TIPOS.update(await _map('tipos_campania', _TIPOS_NOMBRE))
    METAS.update(await _map('tipos_meta_campania', _METAS_NOMBRE))
    HAB.update(await _map('habilidades', _HAB_NOMBRE))
    NIV.update(await _map('niveles_habilidad', _NIV_NOMBRE))


PLANTILLAS = [

    # ── 1. CAPTACIÓN DE SOCIOS ────────────────────────────────────────────────
    {
        'tipo': TIPOS['captacion_socios'],
        'nombre': 'Campaña de captación de socios',
        'descripcion': 'Plantilla estándar para campañas de captación presencial y digital con equipo formado.',
        'metas': [
            {'tipo': METAS['participantes'], 'valor': Decimal('50'),  'notas': 'Nuevas altas de socios/as'},
            {'tipo': METAS['participantes'], 'valor': Decimal('200'), 'notas': 'Personas contactadas (potenciales socios)'},
            {'tipo': METAS['visitas'],       'valor': Decimal('5'),   'notas': 'Puntos o actos de captación realizados'},
        ],
        'partidas': [
            {'concepto': 'Material impreso (trípticos, fichas de alta)', 'tipo': 'gasto',   'importe': Decimal('300')},
            {'concepto': 'Transporte del equipo captador',               'tipo': 'gasto',   'importe': Decimal('150')},
            {'concepto': 'Publicidad en redes sociales',                 'tipo': 'gasto',   'importe': Decimal('100')},
            {'concepto': 'Cuotas ingresadas de nuevos socios (est.)',    'tipo': 'ingreso', 'importe': Decimal('1500')},
        ],
        'actividades': [
            {
                'nombre': 'Preparación de materiales de captación',
                'descripcion': 'Diseño y producción de todos los materiales de comunicación y argumentario.',
                'offset': 0,
                'tareas': [
                    {'titulo': 'Diseñar tríptico y ficha de alta',           'horas': Decimal('8'),  'hab': HAB['diseno'],    'niv': NIV['bueno']},
                    {'titulo': 'Redactar argumentario de captación',         'horas': Decimal('4'),  'hab': HAB['redaccion'], 'niv': NIV['bueno']},
                    {'titulo': 'Preparar presentación de la asociación',     'horas': Decimal('3'),  'hab': HAB['oratoria'],  'niv': NIV['suficiente']},
                ],
            },
            {
                'nombre': 'Formación del equipo captador',
                'descripcion': 'Sesión práctica de formación para los/as voluntarios/as que harán la captación directa.',
                'offset': 7,
                'tareas': [
                    {'titulo': 'Diseñar guión de conversación puerta a puerta', 'horas': Decimal('3'), 'hab': HAB['redaccion'],    'niv': NIV['suficiente']},
                    {'titulo': 'Impartir formación al equipo captador',          'horas': Decimal('6'), 'hab': HAB['docencia'],     'niv': NIV['experto']},
                    {'titulo': 'Simular situaciones difíciles (role play)',      'horas': Decimal('2'), 'hab': HAB['dinamizacion'], 'niv': NIV['bueno']},
                ],
            },
            {
                'nombre': 'Despliegue en campo',
                'descripcion': 'Captación presencial en puntos acordados, eventos propios y espacios públicos.',
                'offset': 14,
                'tareas': [
                    {'titulo': 'Coordinar equipos por zonas y turnos',  'horas': Decimal('10'), 'hab': HAB['coord_voluntarios'], 'niv': NIV['bueno']},
                    {'titulo': 'Atención directa a potenciales socios', 'horas': Decimal('40'), 'hab': HAB['atencion_publico'],  'niv': NIV['suficiente']},
                    {'titulo': 'Registro de nuevas altas en el sistema','horas': Decimal('6'),  'hab': HAB['adm'],               'niv': NIV['suficiente']},
                ],
            },
            {
                'nombre': 'Seguimiento y cierre',
                'descripcion': 'Contacto con interesados que no formalizaron el alta, balance y comunicación de resultados.',
                'offset': 45,
                'tareas': [
                    {'titulo': 'Llamar a interesados pendientes de alta',      'horas': Decimal('8'), 'hab': HAB['atencion_publico'], 'niv': NIV['suficiente']},
                    {'titulo': 'Redactar informe de resultados de campaña',    'horas': Decimal('4'), 'hab': HAB['redaccion'],        'niv': NIV['bueno']},
                    {'titulo': 'Publicar resultados y agradecimientos en RRSS','horas': Decimal('2'), 'hab': HAB['rrss'],             'niv': NIV['suficiente']},
                ],
            },
        ],
    },

    # ── 2. RECOGIDA DE FIRMAS ─────────────────────────────────────────────────
    {
        'tipo': TIPOS['recogida_firmas'],
        'nombre': 'Recogida de firmas (online + presencial)',
        'descripcion': 'Plantilla para peticiones ciudadanas con recogida simultánea en plataformas digitales y en calle.',
        'metas': [
            {'tipo': METAS['firmas'],    'valor': Decimal('5000'),  'notas': 'Firmas totales (online + presencial)'},
            {'tipo': METAS['visitas'],   'valor': Decimal('15000'), 'notas': 'Visitas a la petición online'},
            {'tipo': METAS['menciones'], 'valor': Decimal('15'),    'notas': 'Apariciones en medios de comunicación'},
        ],
        'partidas': [
            {'concepto': 'Materiales impresos (pliegos, carteles)', 'tipo': 'gasto', 'importe': Decimal('200')},
            {'concepto': 'Publicidad digital (social ads)',          'tipo': 'gasto', 'importe': Decimal('200')},
            {'concepto': 'Organización acto de entrega',            'tipo': 'gasto', 'importe': Decimal('300')},
        ],
        'actividades': [
            {
                'nombre': 'Preparación de la petición',
                'descripcion': 'Redacción del texto, diseño visual y configuración de la plataforma online.',
                'offset': 0,
                'tareas': [
                    {'titulo': 'Redactar texto de la petición y demandas',        'horas': Decimal('6'), 'hab': HAB['redaccion'], 'niv': NIV['experto']},
                    {'titulo': 'Diseñar materiales de difusión (digital/impreso)','horas': Decimal('8'), 'hab': HAB['diseno'],    'niv': NIV['suficiente']},
                    {'titulo': 'Configurar petición en plataforma online',        'horas': Decimal('4'), 'hab': HAB['web'],       'niv': NIV['suficiente']},
                    {'titulo': 'Optimizar SEO y metadatos de la petición',        'horas': Decimal('3'), 'hab': HAB['seo'],       'niv': NIV['suficiente']},
                ],
            },
            {
                'nombre': 'Difusión digital',
                'descripcion': 'Amplificación online mediante redes sociales, email y prensa.',
                'offset': 3,
                'tareas': [
                    {'titulo': 'Gestionar redes sociales durante la campaña', 'horas': Decimal('20'), 'hab': HAB['rrss'],   'niv': NIV['bueno']},
                    {'titulo': 'Redactar nota de prensa y distribuirla',      'horas': Decimal('4'),  'hab': HAB['prensa'], 'niv': NIV['bueno']},
                    {'titulo': 'Contactar con influencers y organizaciones aliadas', 'horas': Decimal('4'), 'hab': HAB['rrss'], 'niv': NIV['bueno']},
                ],
            },
            {
                'nombre': 'Recogida presencial',
                'descripcion': 'Mesas de recogida en espacios públicos, mercados y eventos.',
                'offset': 3,
                'tareas': [
                    {'titulo': 'Coordinar puntos y turnos de recogida', 'horas': Decimal('8'),  'hab': HAB['coord_voluntarios'], 'niv': NIV['bueno']},
                    {'titulo': 'Recogida presencial de firmas',          'horas': Decimal('40'), 'hab': HAB['firmas_presencial'], 'niv': NIV['suficiente']},
                    {'titulo': 'Distribuir materiales en el entorno',   'horas': Decimal('16'), 'hab': HAB['difusion'],          'niv': NIV['principiante']},
                ],
            },
            {
                'nombre': 'Entrega oficial y comunicación',
                'descripcion': 'Acto público de entrega a la institución destinataria y cobertura mediática.',
                'offset': 30,
                'tareas': [
                    {'titulo': 'Redactar carta y escrito formal de entrega', 'horas': Decimal('3'), 'hab': HAB['derecho'],   'niv': NIV['suficiente']},
                    {'titulo': 'Organizar acto de entrega (logística)',       'horas': Decimal('8'), 'hab': HAB['eventos'],   'niv': NIV['suficiente']},
                    {'titulo': 'Fotografía y vídeo del acto de entrega',     'horas': Decimal('4'), 'hab': HAB['fotovideo'], 'niv': NIV['suficiente']},
                    {'titulo': 'Publicar crónica y fotos en RRSS',           'horas': Decimal('2'), 'hab': HAB['rrss'],      'niv': NIV['suficiente']},
                ],
            },
        ],
    },

    # ── 3. CAMPAÑA FORMATIVA ──────────────────────────────────────────────────
    {
        'tipo': TIPOS['formativa'],
        'nombre': 'Ciclo formativo para la membresía',
        'descripcion': 'Plantilla para talleres, cursos o jornadas formativas dirigidas a socios/as y simpatizantes.',
        'metas': [
            {'tipo': METAS['participantes'], 'valor': Decimal('80'),  'notas': 'Personas formadas (con asistencia mínima 80%)'},
            {'tipo': METAS['participantes'], 'valor': Decimal('120'), 'notas': 'Inscripciones recibidas'},
            {'tipo': METAS['visitas'],       'valor': Decimal('6'),   'notas': 'Sesiones formativas impartidas'},
        ],
        'partidas': [
            {'concepto': 'Material didáctico (impresión)',        'tipo': 'gasto',   'importe': Decimal('400')},
            {'concepto': 'Ponentes externos / honorarios',        'tipo': 'gasto',   'importe': Decimal('600')},
            {'concepto': 'Cuotas de inscripción',                'tipo': 'ingreso', 'importe': Decimal('800')},
            {'concepto': 'Subvención formación (si aplicable)',   'tipo': 'ingreso', 'importe': Decimal('500')},
        ],
        'actividades': [
            {
                'nombre': 'Diseño curricular y pedagógico',
                'descripcion': 'Definición del programa, objetivos de aprendizaje y metodología.',
                'offset': 0,
                'tareas': [
                    {'titulo': 'Diseñar programa y objetivos de aprendizaje',     'horas': Decimal('12'), 'hab': HAB['docencia'],           'niv': NIV['experto']},
                    {'titulo': 'Elaborar materiales didácticos y presentaciones', 'horas': Decimal('20'), 'hab': HAB['materiales_didact'],  'niv': NIV['bueno']},
                    {'titulo': 'Diseñar ejercicios prácticos y evaluaciones',     'horas': Decimal('8'),  'hab': HAB['docencia'],           'niv': NIV['bueno']},
                ],
            },
            {
                'nombre': 'Comunicación y captación de participantes',
                'descripcion': 'Difusión del programa y gestión del proceso de inscripción.',
                'offset': 7,
                'tareas': [
                    {'titulo': 'Diseñar comunicaciones del ciclo formativo', 'horas': Decimal('6'), 'hab': HAB['diseno'],  'niv': NIV['suficiente']},
                    {'titulo': 'Difundir en RRSS y newsletter',              'horas': Decimal('8'), 'hab': HAB['rrss'],    'niv': NIV['suficiente']},
                    {'titulo': 'Gestionar inscripciones y confirmaciones',   'horas': Decimal('4'), 'hab': HAB['adm'],     'niv': NIV['suficiente']},
                ],
            },
            {
                'nombre': 'Impartición del ciclo',
                'descripcion': 'Desarrollo de las sesiones formativas con soporte técnico.',
                'offset': 21,
                'tareas': [
                    {'titulo': 'Impartir sesiones formativas',        'horas': Decimal('30'), 'hab': HAB['docencia'],    'niv': NIV['experto']},
                    {'titulo': 'Dinamizar grupos y debates',          'horas': Decimal('20'), 'hab': HAB['dinamizacion'],'niv': NIV['bueno']},
                    {'titulo': 'Soporte técnico (proyección, audio)', 'horas': Decimal('8'),  'hab': HAB['soporte_inf'], 'niv': NIV['suficiente']},
                ],
            },
            {
                'nombre': 'Evaluación y memoria',
                'descripcion': 'Recogida de valoraciones, redacción de memoria y envío de certificados.',
                'offset': 60,
                'tareas': [
                    {'titulo': 'Procesar encuestas de satisfacción',         'horas': Decimal('4'), 'hab': HAB['adm'],       'niv': NIV['suficiente']},
                    {'titulo': 'Redactar memoria de la acción formativa',    'horas': Decimal('6'), 'hab': HAB['redaccion'], 'niv': NIV['bueno']},
                    {'titulo': 'Emitir y enviar certificados de asistencia', 'horas': Decimal('2'), 'hab': HAB['adm'],       'niv': NIV['suficiente']},
                ],
            },
        ],
    },

    # ── 4. SENSIBILIZACIÓN ────────────────────────────────────────────────────
    {
        'tipo': TIPOS['sensibilizacion'],
        'nombre': 'Campaña de sensibilización social',
        'descripcion': 'Plantilla para campañas de comunicación y concienciación ciudadana con acciones presenciales y digitales.',
        'metas': [
            {'tipo': METAS['participantes'], 'valor': Decimal('500'),  'notas': 'Personas impactadas directamente (charlas, actos)'},
            {'tipo': METAS['menciones'],     'valor': Decimal('20'),   'notas': 'Apariciones en medios'},
            {'tipo': METAS['visitas'],       'valor': Decimal('5000'), 'notas': 'Visualizaciones del contenido digital'},
        ],
        'partidas': [
            {'concepto': 'Producción de vídeo de sensibilización', 'tipo': 'gasto', 'importe': Decimal('800')},
            {'concepto': 'Diseño e impresión de materiales',       'tipo': 'gasto', 'importe': Decimal('400')},
            {'concepto': 'Publicidad digital',                     'tipo': 'gasto', 'importe': Decimal('300')},
            {'concepto': 'Logística de charlas (desplazamientos)', 'tipo': 'gasto', 'importe': Decimal('200')},
        ],
        'actividades': [
            {
                'nombre': 'Diseño de la campaña',
                'descripcion': 'Definición del mensaje central, identidad visual y producción de contenidos.',
                'offset': 0,
                'tareas': [
                    {'titulo': 'Definir mensajes clave y público objetivo',  'horas': Decimal('8'),  'hab': HAB['redaccion'], 'niv': NIV['experto']},
                    {'titulo': 'Diseñar identidad visual de la campaña',     'horas': Decimal('12'), 'hab': HAB['diseno'],    'niv': NIV['bueno']},
                    {'titulo': 'Producir vídeo o pieza audiovisual central', 'horas': Decimal('16'), 'hab': HAB['fotovideo'], 'niv': NIV['bueno']},
                    {'titulo': 'Preparar contenidos para la web',            'horas': Decimal('4'),  'hab': HAB['web'],       'niv': NIV['suficiente']},
                ],
            },
            {
                'nombre': 'Difusión digital',
                'descripcion': 'Despliegue online: redes sociales, email y posicionamiento.',
                'offset': 7,
                'tareas': [
                    {'titulo': 'Gestionar RRSS durante la campaña',     'horas': Decimal('30'), 'hab': HAB['rrss'],     'niv': NIV['bueno']},
                    {'titulo': 'Enviar newsletter a la membresía',      'horas': Decimal('4'),  'hab': HAB['redaccion'],'niv': NIV['suficiente']},
                    {'titulo': 'Optimizar posicionamiento de contenidos','horas': Decimal('4'),  'hab': HAB['seo'],      'niv': NIV['suficiente']},
                ],
            },
            {
                'nombre': 'Acciones presenciales de sensibilización',
                'descripcion': 'Charlas en centros educativos, asociaciones de vecinos y espacios públicos.',
                'offset': 14,
                'tareas': [
                    {'titulo': 'Coordinar agenda y contactar centros',      'horas': Decimal('10'), 'hab': HAB['adm'],          'niv': NIV['suficiente']},
                    {'titulo': 'Impartir charlas de sensibilización',       'horas': Decimal('20'), 'hab': HAB['oratoria'],     'niv': NIV['experto']},
                    {'titulo': 'Distribuir materiales en actos y espacios', 'horas': Decimal('16'), 'hab': HAB['difusion'],     'niv': NIV['principiante']},
                ],
            },
            {
                'nombre': 'Evaluación de impacto',
                'descripcion': 'Monitorización de resultados y redacción de informe final.',
                'offset': 45,
                'tareas': [
                    {'titulo': 'Monitorizar apariciones en medios',     'horas': Decimal('6'), 'hab': HAB['prensa'],    'niv': NIV['suficiente']},
                    {'titulo': 'Redactar informe final de campaña',     'horas': Decimal('8'), 'hab': HAB['redaccion'], 'niv': NIV['bueno']},
                    {'titulo': 'Compartir resultados con la membresía', 'horas': Decimal('2'), 'hab': HAB['rrss'],      'niv': NIV['suficiente']},
                ],
            },
        ],
    },

    # ── 5. COMUNICACIÓN MEDIÁTICA ─────────────────────────────────────────────
    {
        'tipo': TIPOS['comunicacion_mediatica'],
        'nombre': 'Campaña de comunicación en medios',
        'descripcion': 'Plantilla para acciones de visibilidad pública: ruedas de prensa, notas, entrevistas y cobertura digital.',
        'metas': [
            {'tipo': METAS['menciones'],     'valor': Decimal('30'),   'notas': 'Impactos en medios (TV, radio, prensa digital)'},
            {'tipo': METAS['visitas'],       'valor': Decimal('8000'), 'notas': 'Visualizaciones de contenido digital'},
            {'tipo': METAS['participantes'], 'valor': Decimal('200'),  'notas': 'Personas informadas directamente'},
        ],
        'partidas': [
            {'concepto': 'Producción audiovisual (vídeos, fotos)',       'tipo': 'gasto', 'importe': Decimal('600')},
            {'concepto': 'Impresión de dossiers de prensa',             'tipo': 'gasto', 'importe': Decimal('150')},
            {'concepto': 'Organización rueda de prensa (espacio, etc.)','tipo': 'gasto', 'importe': Decimal('300')},
            {'concepto': 'Publicidad digital (amplificación)',          'tipo': 'gasto', 'importe': Decimal('400')},
        ],
        'actividades': [
            {
                'nombre': 'Preparación de contenidos y dossieres',
                'descripcion': 'Elaboración del material informativo y audiovisual para medios.',
                'offset': 0,
                'tareas': [
                    {'titulo': 'Redactar dossier de prensa completo',    'horas': Decimal('8'),  'hab': HAB['prensa'],    'niv': NIV['experto']},
                    {'titulo': 'Redactar notas de prensa (2-3 versiones)','horas': Decimal('6'), 'hab': HAB['redaccion'], 'niv': NIV['bueno']},
                    {'titulo': 'Producir material audiovisual de apoyo', 'horas': Decimal('12'), 'hab': HAB['fotovideo'], 'niv': NIV['bueno']},
                ],
            },
            {
                'nombre': 'Gestión de medios de comunicación',
                'descripcion': 'Contacto con redacciones, coordinación de entrevistas y rueda de prensa.',
                'offset': 0,
                'tareas': [
                    {'titulo': 'Actualizar base de datos de medios y contactos', 'horas': Decimal('4'), 'hab': HAB['prensa'],              'niv': NIV['bueno']},
                    {'titulo': 'Distribuir nota de prensa y hacer seguimiento',  'horas': Decimal('6'), 'hab': HAB['prensa'],              'niv': NIV['experto']},
                    {'titulo': 'Coordinar entrevistas y apariciones',            'horas': Decimal('8'), 'hab': HAB['relac_institucional'], 'niv': NIV['bueno']},
                    {'titulo': 'Organizar y conducir rueda de prensa',           'horas': Decimal('6'), 'hab': HAB['eventos'],             'niv': NIV['bueno']},
                ],
            },
            {
                'nombre': 'Cobertura digital en tiempo real',
                'descripcion': 'Gestión de redes sociales durante la campaña para amplificar el impacto.',
                'offset': 0,
                'tareas': [
                    {'titulo': 'Gestionar RRSS durante la campaña',     'horas': Decimal('20'), 'hab': HAB['rrss'], 'niv': NIV['experto']},
                    {'titulo': 'Amplificación y SEO de contenidos web', 'horas': Decimal('8'),  'hab': HAB['seo'],  'niv': NIV['bueno']},
                ],
            },
            {
                'nombre': 'Monitorización y evaluación de impacto',
                'descripcion': 'Seguimiento de apariciones, análisis y memoria final.',
                'offset': 30,
                'tareas': [
                    {'titulo': 'Elaborar clipping de apariciones en medios', 'horas': Decimal('8'), 'hab': HAB['prensa'],    'niv': NIV['suficiente']},
                    {'titulo': 'Redactar informe de impacto mediático',      'horas': Decimal('6'), 'hab': HAB['redaccion'], 'niv': NIV['bueno']},
                ],
            },
        ],
    },

    # ── 6. MOVILIZACIÓN ───────────────────────────────────────────────────────
    {
        'tipo': TIPOS['movilizacion'],
        'nombre': 'Convocatoria de movilización ciudadana',
        'descripcion': 'Plantilla para manifestaciones, concentraciones o actos de movilización con convocatoria amplia.',
        'metas': [
            {'tipo': METAS['participantes'], 'valor': Decimal('500'),  'notas': 'Asistentes al acto principal'},
            {'tipo': METAS['menciones'],     'valor': Decimal('20'),   'notas': 'Apariciones en medios de comunicación'},
            {'tipo': METAS['firmas'],        'valor': Decimal('1000'), 'notas': 'Adhesiones al manifiesto o convocatoria'},
        ],
        'partidas': [
            {'concepto': 'Impresión de pancartas y materiales',   'tipo': 'gasto', 'importe': Decimal('500')},
            {'concepto': 'Megafonía y equipos de sonido',         'tipo': 'gasto', 'importe': Decimal('300')},
            {'concepto': 'Publicidad digital de la convocatoria', 'tipo': 'gasto', 'importe': Decimal('200')},
            {'concepto': 'Seguros y gestiones administrativas',   'tipo': 'gasto', 'importe': Decimal('100')},
        ],
        'actividades': [
            {
                'nombre': 'Preparación política y alianzas',
                'descripcion': 'Redacción del manifiesto, coordinación con otras organizaciones y negociación institucional.',
                'offset': 0,
                'tareas': [
                    {'titulo': 'Redactar manifiesto o plataforma unitaria', 'horas': Decimal('6'), 'hab': HAB['redaccion'],          'niv': NIV['experto']},
                    {'titulo': 'Coordinar con organizaciones aliadas',      'horas': Decimal('8'), 'hab': HAB['relac_institucional'],'niv': NIV['bueno']},
                    {'titulo': 'Solicitar autorizaciones y permisos',       'horas': Decimal('4'), 'hab': HAB['derecho_admin'],      'niv': NIV['suficiente']},
                ],
            },
            {
                'nombre': 'Difusión de la convocatoria',
                'descripcion': 'Movilización en redes sociales, prensa y distribución física en el territorio.',
                'offset': 7,
                'tareas': [
                    {'titulo': 'Gestionar RRSS de la convocatoria',   'horas': Decimal('20'), 'hab': HAB['rrss'],    'niv': NIV['bueno']},
                    {'titulo': 'Enviar nota de prensa a medios',      'horas': Decimal('4'),  'hab': HAB['prensa'],  'niv': NIV['bueno']},
                    {'titulo': 'Distribuir convocatoria en barrios',  'horas': Decimal('20'), 'hab': HAB['difusion'],'niv': NIV['principiante']},
                ],
            },
            {
                'nombre': 'Organización logística del acto',
                'descripcion': 'Coordinación de todos los elementos materiales y humanos para el día del acto.',
                'offset': 14,
                'tareas': [
                    {'titulo': 'Planificar recorrido, orden y seguridad',        'horas': Decimal('8'),  'hab': HAB['gestion_proyectos'], 'niv': NIV['bueno']},
                    {'titulo': 'Coordinar voluntarios/as para el servicio de orden', 'horas': Decimal('12'), 'hab': HAB['coord_voluntarios'], 'niv': NIV['bueno']},
                    {'titulo': 'Organizar megafonía, escenario y materiales',    'horas': Decimal('8'),  'hab': HAB['eventos'],          'niv': NIV['bueno']},
                ],
            },
            {
                'nombre': 'Durante el acto',
                'descripcion': 'Cobertura en tiempo real, atención a participantes y gestión de incidencias.',
                'offset': 21,
                'tareas': [
                    {'titulo': 'Atender a participantes en puntos de acogida', 'horas': Decimal('8'), 'hab': HAB['atencion_publico'], 'niv': NIV['suficiente']},
                    {'titulo': 'Fotografía y vídeo del acto',                  'horas': Decimal('8'), 'hab': HAB['fotovideo'],        'niv': NIV['bueno']},
                    {'titulo': 'Publicar en RRSS en tiempo real',              'horas': Decimal('4'), 'hab': HAB['rrss'],             'niv': NIV['bueno']},
                ],
            },
            {
                'nombre': 'Comunicación post-acto',
                'descripcion': 'Difusión de resultados, crónica y seguimiento mediático.',
                'offset': 22,
                'tareas': [
                    {'titulo': 'Publicar crónica e imágenes en RRSS y web',  'horas': Decimal('4'), 'hab': HAB['rrss'],     'niv': NIV['bueno']},
                    {'titulo': 'Enviar nota de prensa con balance del acto', 'horas': Decimal('3'), 'hab': HAB['prensa'],   'niv': NIV['bueno']},
                    {'titulo': 'Comunicar resultados a la membresía',        'horas': Decimal('2'), 'hab': HAB['redaccion'],'niv': NIV['suficiente']},
                ],
            },
        ],
    },

    # ── 7. ACCIÓN LEGAL / INSTITUCIONAL ──────────────────────────────────────
    {
        'tipo': TIPOS['accion_legal'],
        'nombre': 'Acción legal e institucional',
        'descripcion': 'Plantilla para recursos, denuncias, alegaciones y acciones de incidencia ante administraciones.',
        'metas': [
            {'tipo': METAS['menciones'],     'valor': Decimal('10'), 'notas': 'Apariciones en medios sobre el caso'},
            {'tipo': METAS['participantes'], 'valor': Decimal('50'), 'notas': 'Personas afectadas asesoradas o representadas'},
        ],
        'partidas': [
            {'concepto': 'Honorarios jurídicos externos (si aplicable)', 'tipo': 'gasto', 'importe': Decimal('0')},
            {'concepto': 'Tasas y costas procesales',                    'tipo': 'gasto', 'importe': Decimal('200')},
            {'concepto': 'Documentación, copias y notaría',              'tipo': 'gasto', 'importe': Decimal('100')},
            {'concepto': 'Logística de reuniones institucionales',       'tipo': 'gasto', 'importe': Decimal('150')},
        ],
        'actividades': [
            {
                'nombre': 'Análisis jurídico y estrategia',
                'descripcion': 'Investigación del marco legal aplicable, dictamen y diseño de la estrategia de acción.',
                'offset': 0,
                'tareas': [
                    {'titulo': 'Investigar jurisprudencia y normativa aplicable', 'horas': Decimal('20'), 'hab': HAB['derecho'],       'niv': NIV['experto']},
                    {'titulo': 'Analizar vía administrativa y posibles recursos', 'horas': Decimal('16'), 'hab': HAB['derecho_admin'], 'niv': NIV['experto']},
                    {'titulo': 'Redactar dictamen jurídico interno',             'horas': Decimal('12'), 'hab': HAB['derecho'],       'niv': NIV['experto']},
                ],
            },
            {
                'nombre': 'Elaboración del escrito o recurso',
                'descripcion': 'Redacción, documentación y revisión del escrito jurídico formal.',
                'offset': 14,
                'tareas': [
                    {'titulo': 'Redactar recurso, denuncia o alegaciones',     'horas': Decimal('20'), 'hab': HAB['derecho_admin'], 'niv': NIV['experto']},
                    {'titulo': 'Recopilar documentación y pruebas necesarias', 'horas': Decimal('8'),  'hab': HAB['adm'],           'niv': NIV['bueno']},
                    {'titulo': 'Revisar y corregir el escrito final',          'horas': Decimal('6'),  'hab': HAB['derecho'],       'niv': NIV['experto']},
                    {'titulo': 'Registrar o presentar ante el organismo',      'horas': Decimal('2'),  'hab': HAB['derecho_admin'], 'niv': NIV['suficiente']},
                ],
            },
            {
                'nombre': 'Incidencia institucional',
                'descripcion': 'Reuniones con representantes institucionales y comunicación oficial.',
                'offset': 14,
                'tareas': [
                    {'titulo': 'Redactar comunicación formal a organismos',       'horas': Decimal('6'), 'hab': HAB['relac_institucional'], 'niv': NIV['experto']},
                    {'titulo': 'Coordinar y preparar reunión con representantes', 'horas': Decimal('6'), 'hab': HAB['relac_institucional'], 'niv': NIV['bueno']},
                    {'titulo': 'Preparar presentación del caso y propuestas',     'horas': Decimal('6'), 'hab': HAB['oratoria'],           'niv': NIV['bueno']},
                ],
            },
            {
                'nombre': 'Comunicación pública del caso',
                'descripcion': 'Difusión en medios y redes para presión social e información a la membresía.',
                'offset': 21,
                'tareas': [
                    {'titulo': 'Redactar nota de prensa sobre la acción legal', 'horas': Decimal('4'), 'hab': HAB['prensa'],    'niv': NIV['bueno']},
                    {'titulo': 'Difundir en RRSS y web',                        'horas': Decimal('4'), 'hab': HAB['rrss'],      'niv': NIV['suficiente']},
                    {'titulo': 'Informar a la membresía por email',             'horas': Decimal('2'), 'hab': HAB['redaccion'], 'niv': NIV['suficiente']},
                ],
            },
            {
                'nombre': 'Seguimiento y resolución',
                'descripcion': 'Monitorización de la respuesta institucional y comunicación de avances.',
                'offset': 60,
                'tareas': [
                    {'titulo': 'Monitorizar plazos y respuesta de la administración', 'horas': Decimal('6'), 'hab': HAB['derecho_admin'], 'niv': NIV['suficiente']},
                    {'titulo': 'Redactar informe de seguimiento del caso',            'horas': Decimal('8'), 'hab': HAB['derecho'],       'niv': NIV['bueno']},
                    {'titulo': 'Comunicar avances a la membresía',                   'horas': Decimal('3'), 'hab': HAB['redaccion'],     'niv': NIV['suficiente']},
                ],
            },
        ],
    },
]


async def seed(session: AsyncSession) -> None:
    print("[seed_plantillas] Limpiando plantillas existentes…")
    await session.execute(delete(PlantillaCampania))
    await session.flush()

    for pl in PLANTILLAS:
        print(f"  → {pl['nombre']}")
        plantilla = PlantillaCampania(
            tipo_campania_id=pl['tipo'],
            nombre=pl['nombre'],
            descripcion=pl['descripcion'],
            activo=True,
        )
        session.add(plantilla)
        await session.flush()

        for i, m in enumerate(pl['metas']):
            session.add(PlantillaMeta(
                plantilla_id=plantilla.id,
                tipo_meta_id=m['tipo'],
                valor_sugerido=m['valor'],
                notas=m.get('notas'),
                orden=i + 1,
            ))

        for i, p in enumerate(pl['partidas']):
            session.add(PlantillaPartida(
                plantilla_id=plantilla.id,
                concepto=p['concepto'],
                tipo_partida=p['tipo'],
                importe_estimado=p['importe'],
                orden=i + 1,
            ))

        for ia, act in enumerate(pl['actividades']):
            actividad = PlantillaActividad(
                plantilla_id=plantilla.id,
                nombre=act['nombre'],
                descripcion=act.get('descripcion'),
                duracion_dias=act['offset'],
                orden=ia + 1,
            )
            session.add(actividad)
            await session.flush()

            for it, t in enumerate(act['tareas']):
                session.add(PlantillaTarea(
                    actividad_id=actividad.id,
                    titulo=t['titulo'],
                    horas_estimadas=t['horas'],
                    habilidad_id=t.get('hab'),
                    nivel_habilidad_id=t.get('niv'),
                    orden=it + 1,
                ))

    await session.commit()
    print("[seed_plantillas] ✓ Completado.")


async def main() -> None:
    async with async_session_factory() as session:
        await seed(session)


if __name__ == '__main__':
    asyncio.run(main())
