"""Catálogos base sembrados desde el bootstrap del backend.

Datos de partida que cualquier instalación greenfield necesita para
funcionar: estados (cuota, donación, tarea…), motivos (baja, reducción),
tipos (vinculación, reunión, convenio, organización), niveles
(estudios, habilidad), formas de pago y cláusulas RGPD iniciales.

Cada función es idempotente: inserta solo lo que falte por `nombre` o
`codigo`, según el caso. Se invoca desde `bootstrap.ensure_catalogos_base`.
"""
from __future__ import annotations

import uuid

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.membresia.models.tipo_vinculacion import TipoVinculacion
from app.modules.configuracion.models.estados import (
    EstadoCuota, EstadoTarea, EstadoParticipante, EstadoOrdenCobro,
    EstadoRemesa, EstadoDonacion, EstadoNotificacion,
)
from app.modules.economico.models.cobro.forma_pago import FormaPago
from app.modules.economico.models.cuotas import MotivoReduccionCuota
from app.modules.economico.models.presupuesto import EstadoPlanificacion
from app.modules.membresia.models.motivo_baja import MotivoBaja
from app.modules.membresia.models.nivel_estudios import NivelEstudios
from app.modules.membresia.models.nivel_habilidad import NivelHabilidad
from app.modules.membresia.models.tipo_entidad_juridica import TipoEntidadJuridica
from app.modules.proteccion_datos.models import ClausulaInformativa
from app.modules.secretaria.models.reunion import TipoReunion
from app.modules.secretaria.models.convenio import TipoConvenio


# ---------------------------------------------------------------------------
# Catálogos por nombre
# ---------------------------------------------------------------------------

_MOTIVOS_BAJA = [
    {"nombre": "Voluntaria",      "requiere_documentacion": False, "activo": True},
    {"nombre": "Fallecimiento",   "requiere_documentacion": False, "activo": True},
    {"nombre": "Incumplimiento",  "requiere_documentacion": False, "activo": True},
    {"nombre": "Disciplinario",   "requiere_documentacion": False, "activo": True},
]

_MOTIVOS_REDUCCION_CUOTA = [
    {"codigo": "JOVEN",    "nombre": "Estudiante / Joven",       "descripcion": "Cuota reducida para socios menores de 30 años o estudiantes acreditados", "porcentaje_reduccion": 90, "orden": 10, "activo": True},
    {"codigo": "PARADO",   "nombre": "Desempleado",              "descripcion": "Reducción para socios en situación de desempleo debidamente acreditada",   "porcentaje_reduccion": 90, "orden": 20, "activo": True},
    {"codigo": "JUBILADO", "nombre": "Pensionista / Jubilado",   "descripcion": "Reducción para socios jubilados o pensionistas",                          "porcentaje_reduccion": 50, "orden": 30, "activo": True},
    {"codigo": "HONOR",    "nombre": "Cuota honorífica",         "descripcion": "Socios de honor — no se les emite cuota",                                 "porcentaje_reduccion": 100, "orden": 40, "activo": True},
    {"codigo": "BECA",     "nombre": "Beca / situación social",  "descripcion": "Reducción total por beca o situación social acreditada",                  "porcentaje_reduccion": 100, "orden": 50, "activo": True},
]

# Catálogo canónico de tipos de vinculación (codigo estable; ver migración p2).
_TIPOS_VINCULACION = [
    {"nombre": "Firmante",     "codigo": "FIRMANTE",     "ambito": "central",     "area_responsable": "COMUNICACION_FIRMAS",            "requiere_satelite": False, "activo": True},
    {"nombre": "Simpatizante", "codigo": "SIMPATIZANTE", "ambito": "central",     "area_responsable": "COMUNICACION_SIMPATIZANTES",     "requiere_satelite": False, "activo": True},
    {"nombre": "Socio",        "codigo": "SOCIO",        "ambito": "territorial", "area_responsable": "MEMBRESIA_SOCIO_GESTIONAR",      "requiere_satelite": True,  "activo": True},
    {"nombre": "Voluntario",   "codigo": "VOLUNTARIO",   "ambito": "territorial", "area_responsable": "MEMBRESIA_VOLUNTARIO_GESTIONAR", "requiere_satelite": True,  "activo": True},
    {"nombre": "Donante",      "codigo": "DONANTE",      "ambito": "central",     "area_responsable": "TESORERIA_DONANTES",             "requiere_satelite": False, "activo": True},
    {"nombre": "Empleado",     "codigo": "EMPLEADO",     "ambito": "central",     "area_responsable": "RECURSOS_HUMANOS",               "requiere_satelite": True,  "activo": True},
]

_FORMAS_PAGO = [
    {"codigo": "TRANSFERENCIA", "nombre": "Transferencia bancaria", "descripcion": "Transferencia bancaria nacional", "activo": True},
    {"codigo": "DOMICILIACION", "nombre": "Domiciliación SEPA",     "descripcion": "Domiciliación bancaria SEPA",     "activo": True},
    {"codigo": "TARJETA",       "nombre": "Tarjeta",                "descripcion": "Pago con tarjeta",                "activo": True},
    {"codigo": "EFECTIVO",      "nombre": "Efectivo",               "descripcion": "Pago en efectivo",                "activo": True},
    {"codigo": "PAYPAL",        "nombre": "PayPal",                 "descripcion": "Cobro a una cuenta PayPal",        "activo": True},
    {"codigo": "BIZUM",         "nombre": "Bizum",                  "descripcion": "Cobro mediante Bizum al teléfono", "activo": True},
]

_NIVELES_ESTUDIOS = [
    {"nombre": "Sin estudios",        "descripcion": "Sin estudios formales",                          "orden": 0, "activo": True},
    {"nombre": "Educación Primaria",  "descripcion": "Educación primaria completa",                    "orden": 1, "activo": True},
    {"nombre": "ESO",                 "descripcion": "Educación Secundaria Obligatoria o equivalente", "orden": 2, "activo": True},
    {"nombre": "Bachillerato",        "descripcion": "Bachillerato o equivalente",                     "orden": 3, "activo": True},
    {"nombre": "FP de grado medio",   "descripcion": "Ciclo formativo de grado medio",                 "orden": 4, "activo": True},
    {"nombre": "FP de grado superior","descripcion": "Ciclo formativo de grado superior",              "orden": 5, "activo": True},
    {"nombre": "Grado universitario", "descripcion": "Grado, Diplomatura o Licenciatura",              "orden": 6, "activo": True},
    {"nombre": "Máster / Postgrado",  "descripcion": "Máster oficial o propio, Postgrado",             "orden": 7, "activo": True},
    {"nombre": "Doctorado",           "descripcion": "Doctor/a",                                       "orden": 8, "activo": True},
]

_NIVELES_HABILIDAD = [
    {"nombre": "Principiante", "descripcion": "Conocimientos básicos, sin experiencia práctica",      "orden": 0, "activo": True},
    {"nombre": "Suficiente",   "descripcion": "Puede desenvolverse con autonomía en tareas sencillas","orden": 1, "activo": True},
    {"nombre": "Bueno",        "descripcion": "Dominio sólido, capaz de resolver situaciones complejas", "orden": 2, "activo": True},
    {"nombre": "Experto/a",    "descripcion": "Dominio avanzado, puede formar a otras personas",      "orden": 3, "activo": True},
]


# ---------------------------------------------------------------------------
# Estados (EstadoBase: nombre, descripcion, orden, es_inicial, es_final, color)
# ---------------------------------------------------------------------------

_ESTADOS_CUOTA = [
    {"nombre": "Pendiente", "descripcion": "Cuota creada pero no cobrada",      "orden": 1, "es_inicial": True,  "es_final": False, "color": "warning"},
    {"nombre": "Cobrada",   "descripcion": "Cuota cobrada exitosamente",        "orden": 2, "es_inicial": False, "es_final": True,  "color": "success"},
    {"nombre": "Impagada",  "descripcion": "Intento de cobro fallido",          "orden": 3, "es_inicial": False, "es_final": False, "color": "danger"},
    {"nombre": "Anulada",   "descripcion": "Cuota anulada/cancelada",           "orden": 4, "es_inicial": False, "es_final": True,  "color": "secondary"},
    {"nombre": "Exenta",    "descripcion": "Cuota exenta de pago",              "orden": 5, "es_inicial": False, "es_final": True,  "color": "info"},
]

_ESTADOS_DONACION = [
    {"nombre": "REGISTRADA", "descripcion": "Donación registrada, pendiente de cobro", "orden": 1, "es_inicial": True,  "es_final": False, "color": None},
    {"nombre": "COBRADA",    "descripcion": "Donación recibida y contabilizada",        "orden": 2, "es_inicial": False, "es_final": False, "color": None},
    {"nombre": "ANULADA",    "descripcion": "Donación anulada o devuelta",              "orden": 99,"es_inicial": False, "es_final": True,  "color": None},
]

_ESTADOS_REMESA = [
    {"nombre": "Borrador",   "descripcion": "Remesa en creación",                 "orden": 1, "es_inicial": True,  "es_final": False, "color": "secondary"},
    {"nombre": "Generada",   "descripcion": "Remesa generada, pendiente de envío","orden": 2, "es_inicial": False, "es_final": False, "color": "info"},
    {"nombre": "Enviada",    "descripcion": "Remesa enviada al banco",            "orden": 3, "es_inicial": False, "es_final": False, "color": "primary"},
    {"nombre": "Procesada",  "descripcion": "Remesa procesada por el banco",      "orden": 4, "es_inicial": False, "es_final": True,  "color": "success"},
    {"nombre": "Parcial",    "descripcion": "Remesa procesada parcialmente",      "orden": 5, "es_inicial": False, "es_final": True,  "color": "warning"},
    {"nombre": "Rechazada",  "descripcion": "Remesa rechazada",                   "orden": 6, "es_inicial": False, "es_final": True,  "color": "danger"},
]

_ESTADOS_ORDEN_COBRO = [
    {"nombre": "Pendiente", "descripcion": "Orden creada, pendiente de procesar", "orden": 1, "es_inicial": True,  "es_final": False, "color": "warning"},
    {"nombre": "Procesada", "descripcion": "Orden procesada, cobro realizado",    "orden": 2, "es_inicial": False, "es_final": True,  "color": "success"},
    {"nombre": "Fallida",   "descripcion": "Cobro fallido",                       "orden": 3, "es_inicial": False, "es_final": True,  "color": "danger"},
    {"nombre": "Anulada",   "descripcion": "Orden anulada",                       "orden": 4, "es_inicial": False, "es_final": True,  "color": "secondary"},
]

_ESTADOS_TAREA = [
    {"nombre": "Pendiente",   "descripcion": "Tarea por hacer",                "orden": 1, "es_inicial": True,  "es_final": False, "color": "secondary"},
    {"nombre": "En Progreso", "descripcion": "Tarea en ejecución",             "orden": 2, "es_inicial": False, "es_final": False, "color": "primary"},
    {"nombre": "Bloqueada",   "descripcion": "Tarea bloqueada por dependencias","orden": 3, "es_inicial": False, "es_final": False, "color": "warning"},
    {"nombre": "Completada",  "descripcion": "Tarea finalizada",               "orden": 4, "es_inicial": False, "es_final": True,  "color": "success"},
    {"nombre": "Cancelada",   "descripcion": "Tarea cancelada",                "orden": 5, "es_inicial": False, "es_final": True,  "color": "danger"},
]

_ESTADOS_PARTICIPANTE = [
    {"nombre": "Incluido",   "descripcion": "Participante añadido a la campaña", "orden": 1, "es_inicial": True,  "es_final": False, "color": "info"},
    {"nombre": "Enviado",    "descripcion": "Comunicación enviada",              "orden": 2, "es_inicial": False, "es_final": False, "color": "primary"},
    {"nombre": "Entregado",  "descripcion": "Comunicación entregada",            "orden": 3, "es_inicial": False, "es_final": False, "color": "primary"},
    {"nombre": "Leído",      "descripcion": "Comunicación leída/abierta",        "orden": 4, "es_inicial": False, "es_final": False, "color": "success"},
    {"nombre": "Respondido", "descripcion": "Participante respondió",            "orden": 5, "es_inicial": False, "es_final": True,  "color": "success"},
    {"nombre": "Rebotado",   "descripcion": "Comunicación rebotada",             "orden": 6, "es_inicial": False, "es_final": True,  "color": "danger"},
    {"nombre": "Excluido",   "descripcion": "Participante excluido de la campaña", "orden": 7, "es_inicial": False, "es_final": True,  "color": "secondary"},
]

_ESTADOS_NOTIFICACION = [
    {"codigo": "PENDIENTE", "nombre": "Pendiente", "descripcion": "Notificación creada pero no enviada",         "orden": 1, "es_inicial": True,  "es_final": False, "color": "#F59E0B"},
    {"codigo": "ENVIADA",   "nombre": "Enviada",   "descripcion": "Notificación enviada al canal correspondiente","orden": 2, "es_inicial": False, "es_final": False, "color": "#0EA5E9"},
    {"codigo": "LEIDA",     "nombre": "Leída",     "descripcion": "Notificación leída por el usuario",           "orden": 3, "es_inicial": False, "es_final": True,  "color": "#22C55E"},
    {"codigo": "ERROR",     "nombre": "Error",     "descripcion": "Error al enviar la notificación",             "orden": 4, "es_inicial": False, "es_final": True,  "color": "#EF4444"},
]

# EstadoPlanificacion no hereda de EstadoBase (esquema propio: codigo, nombre,
# orden, color, es_final, activo). Lo sembramos por `codigo`.
_ESTADOS_PLANIFICACION = [
    {"codigo": "BORRADOR",     "nombre": "Borrador",     "orden": 1, "es_final": False, "color": "#9ca3af", "activo": True},
    {"codigo": "PROPUESTO",    "nombre": "Propuesto",    "orden": 2, "es_final": False, "color": "#3b82f6", "activo": True},
    {"codigo": "APROBADO",     "nombre": "Aprobado",     "orden": 3, "es_final": False, "color": "#22c55e", "activo": True},
    {"codigo": "EN_EJECUCION", "nombre": "En ejecución", "orden": 4, "es_final": False, "color": "#a855f7", "activo": True},
    {"codigo": "CERRADO",      "nombre": "Cerrado",      "orden": 5, "es_final": True,  "color": "#1f2937", "activo": True},
]

# Estados del módulo Secretaría — la BD tiene columna `codigo NOT NULL`
# que no está en el modelo Python. Se siembran con SQL crudo más abajo.
# (codigo, nombre, descripcion, orden, es_inicial, es_final, color)
_ESTADOS_REUNION = [
    ("CONVOCADA",     "Convocada",        "Reunión convocada, pendiente de celebrar", 1,  True,  False, "#3b82f6"),
    ("CELEBRADA",     "Celebrada",        "Reunión celebrada, sin acta aún",          2,  False, False, "#f59e0b"),
    ("ACTA_BORRADOR", "Acta en borrador", "Acta redactada, pendiente de aprobación",  3,  False, False, "#f97316"),
    ("ACTA_APROBADA", "Acta aprobada",    "Acta aprobada por el órgano",              4,  False, False, "#10b981"),
    ("FINALIZADA",    "Finalizada",       "Reunión y acta cerradas y firmadas",       5,  False, True,  "#22c55e"),
    ("CANCELADA",     "Cancelada",        "Reunión cancelada antes de celebrarse",    99, False, True,  "#94a3b8"),
]

_ESTADOS_ACTA = [
    ("BORRADOR", "Borrador", "Acta redactada en borrador",              1, True,  False, "#f97316"),
    ("APROBADA", "Aprobada", "Acta aprobada en reunión posterior",      2, False, False, "#3b82f6"),
    ("FIRMADA",  "Firmada",  "Acta firmada por secretario y presidente",3, False, True,  "#22c55e"),
]

_ESTADOS_EJECUCION_ACUERDO = [
    ("PENDIENTE",  "Pendiente",  "Acuerdo aprobado, pendiente de ejecución", 1,  True,  False, "#f59e0b"),
    ("EN_CURSO",   "En curso",   "Ejecución del acuerdo en marcha",          2,  False, False, "#3b82f6"),
    ("COMPLETADO", "Completado", "Acuerdo ejecutado y completado",           3,  False, True,  "#22c55e"),
    ("PARALIZADO", "Paralizado", "Ejecución paralizada por bloqueo",         4,  False, False, "#94a3b8"),
    ("DESCARTADO", "Descartado", "Acuerdo descartado sin ejecutar",          99, False, True,  "#ef4444"),
]

# estados_convenio tiene esquema distinto: solo nombre, descripcion, orden, activo
# (sin codigo, es_inicial, es_final, color). Lo sembramos en SQL crudo.
_ESTADOS_CONVENIO_SIMPLE = [
    ("Borrador",        "Borrador del convenio, sin firmar",          1),
    ("En negociación",  "Convenio en negociación con la contraparte", 2),
    ("Firmado",         "Convenio firmado por ambas partes",          3),
    ("Vigente",         "Convenio en período de vigencia",            4),
    ("Expirado",        "Convenio expirado por fin de plazo",         5),
    ("Rescindido",      "Convenio rescindido antes del plazo",        6),
]


# ---------------------------------------------------------------------------
# Tipos de reunión / convenio / organización
# ---------------------------------------------------------------------------

_TIPOS_REUNION = [
    {"nombre": "Asamblea General Ordinaria",      "descripcion": "Reunión anual ordinaria de todos los socios (Ley 1/2002 art. 11)", "organo": "ASAMBLEA_GENERAL", "quorum_primera_convocatoria": 50, "quorum_segunda_convocatoria": 0,    "antelacion_minima_dias": 15, "activo": True, "orden": 1},
    {"nombre": "Asamblea General Extraordinaria", "descripcion": "Convocada por la Junta o a petición de socios para asuntos urgentes", "organo": "ASAMBLEA_GENERAL", "quorum_primera_convocatoria": 50, "quorum_segunda_convocatoria": 0,    "antelacion_minima_dias": 10, "activo": True, "orden": 2},
    {"nombre": "Reunión de Junta Directiva",      "descripcion": "Reunión del órgano de representación y gestión",                 "organo": "JUNTA_DIRECTIVA",  "quorum_primera_convocatoria": 50, "quorum_segunda_convocatoria": None, "antelacion_minima_dias": 3,  "activo": True, "orden": 3},
    {"nombre": "Comisión de Trabajo",             "descripcion": "Reuniones de comisiones delegadas de la Junta",                  "organo": "COMISION",         "quorum_primera_convocatoria": None,"quorum_segunda_convocatoria": None, "antelacion_minima_dias": 2,  "activo": True, "orden": 4},
]

_TIPOS_CONVENIO = [
    {"nombre": "Convenio institucional de colaboración", "descripcion": "Acuerdos de colaboración con entidades sin contraprestación económica directa", "activo": True},
    {"nombre": "Acuerdo de patrocinio",                  "descripcion": "Aportaciones económicas a cambio de imagen o visibilidad",                       "activo": True},
    {"nombre": "Adhesión a red o plataforma",            "descripcion": "Incorporación a redes, federaciones o plataformas de tercer sector",            "activo": True},
    {"nombre": "Contrato de servicios",                  "descripcion": "Prestación de servicios con contraprestación económica",                          "activo": True},
    {"nombre": "Protocolo de actuación",                 "descripcion": "Acuerdos de coordinación operativa con administraciones públicas",                "activo": True},
]

_TIPOS_ORGANIZACION = [
    {"nombre": "Asociación",                "descripcion": "Asociación sin ánimo de lucro (Ley Orgánica 1/2002)", "permite_convenios": True,  "permite_jerarquia": False, "orden": 1,  "activo": True},
    {"nombre": "Fundación",                 "descripcion": "Fundación (Ley 50/2002)",                             "permite_convenios": True,  "permite_jerarquia": False, "orden": 2,  "activo": True},
    {"nombre": "Cooperativa",               "descripcion": "Sociedad cooperativa",                                "permite_convenios": True,  "permite_jerarquia": False, "orden": 3,  "activo": True},
    {"nombre": "Federación / Confederación","descripcion": "Agrupación de asociaciones u otras entidades",         "permite_convenios": True,  "permite_jerarquia": True,  "orden": 4,  "activo": True},
    {"nombre": "Administración Pública",    "descripcion": "Ayuntamiento, Comunidad Autónoma, Diputación, Estado","permite_convenios": True,  "permite_jerarquia": False, "orden": 5,  "activo": True},
    {"nombre": "Empresa",                   "descripcion": "Persona jurídica privada con ánimo de lucro",         "permite_convenios": True,  "permite_jerarquia": False, "orden": 6,  "activo": True},
    {"nombre": "Partido político",          "descripcion": "Formación política (Ley Orgánica 6/2002)",            "permite_convenios": True,  "permite_jerarquia": False, "orden": 7,  "activo": True},
    {"nombre": "Sindicato",                 "descripcion": "Organización sindical",                                "permite_convenios": True,  "permite_jerarquia": False, "orden": 8,  "activo": True},
    {"nombre": "Otra",                      "descripcion": "Otra forma jurídica",                                 "permite_convenios": True,  "permite_jerarquia": False, "orden": 99, "activo": True},
]



# ---------------------------------------------------------------------------
# Cláusulas RGPD iniciales (art. 13/14)
# ---------------------------------------------------------------------------

_CLAUSULAS_RGPD = [
    {
        "codigo": "ALTA_SOCIO", "version": 1, "vigente": True,
        "finalidad_corta": "Gestión de la condición de socio",
        "texto": (
            "Responsable: la asociación. Finalidad: gestionar la condición de socio "
            "(altas, cuotas, comunicaciones internas, participación en órganos). "
            "Base jurídica: ejecución del contrato asociativo (art. 6.1.b RGPD). "
            "Destinatarios: no se cederán datos a terceros salvo obligación legal "
            "o entidad financiera para gestión de cuotas. Plazo: durante la "
            "vigencia de la condición de socio + 6 años por obligaciones contables. "
            "Derechos: ARSULIPO, contactando con el DPD."
        ),
    },
    {
        "codigo": "ALTA_VOLUNTARIADO", "version": 1, "vigente": True,
        "finalidad_corta": "Inscripción como persona voluntaria",
        "texto": (
            "Responsable: la asociación. Finalidad: gestión de la actividad "
            "voluntaria (Ley 45/2015 del Voluntariado). Base jurídica: ejecución "
            "del acuerdo de incorporación. Destinatarios: aseguradora (a efectos "
            "de la cobertura obligatoria art. 14.1 Ley 45/2015). Plazo: 6 años "
            "tras finalizar la colaboración."
        ),
    },
    {
        "codigo": "DONACION", "version": 1, "vigente": True,
        "finalidad_corta": "Gestión de donaciones",
        "texto": (
            "Responsable: la asociación. Finalidad: registro y certificación "
            "fiscal de la donación (Ley 49/2002). Base jurídica: cumplimiento "
            "de obligación legal. Destinatarios: Agencia Tributaria (Modelo 182). "
            "Plazo: 6 años por obligaciones contables y fiscales."
        ),
    },
    {
        "codigo": "CONTACTO_WEB", "version": 1, "vigente": True,
        "finalidad_corta": "Atención de consultas por formulario web",
        "texto": (
            "Responsable: la asociación. Finalidad: atender la consulta enviada. "
            "Base jurídica: consentimiento del interesado al enviar el formulario. "
            "Destinatarios: no se ceden datos. Plazo: hasta la resolución de la "
            "consulta + 1 año, salvo que de ella se derive otra relación."
        ),
    },
    {
        "codigo": "COMUNICACIONES_INFORMATIVAS", "version": 1, "vigente": True,
        "finalidad_corta": "Envío de comunicaciones informativas",
        "texto": (
            "Responsable: la asociación. Finalidad: enviar boletines y "
            "comunicaciones sobre actividades de la asociación. Base jurídica: "
            "consentimiento (art. 6.1.a RGPD). Puede retirarse en cualquier "
            "momento desde el enlace del propio mensaje o contactando con el DPD."
        ),
    },
    {
        "codigo": "CESION_IMAGEN", "version": 1, "vigente": True,
        "finalidad_corta": "Cesión de imagen en actividades",
        "texto": (
            "Responsable: la asociación. Finalidad: difundir las actividades de "
            "la asociación con material gráfico (fotografías, vídeos) en web, "
            "redes sociales y memoria anual. Base jurídica: consentimiento. "
            "Puede retirarse en cualquier momento; las imágenes ya publicadas se "
            "retirarán en plazo razonable."
        ),
    },
    {
        "codigo": "DATOS_SALUD", "version": 1, "vigente": True,
        "finalidad_corta": "Tratamiento de datos de salud (art. 9 RGPD)",
        "texto": (
            "Responsable: la asociación. Finalidad: aplicar reducciones de "
            "cuota o adaptar la participación en actividades. Base jurídica: "
            "consentimiento explícito (art. 9.2.a RGPD). Destinatarios: no se "
            "ceden datos. Plazo: mientras dure la condición que motiva el "
            "tratamiento + 6 años."
        ),
    },
]


# ---------------------------------------------------------------------------
# Sembrado idempotente
# ---------------------------------------------------------------------------

async def _ensure_by_field(session: AsyncSession, model, field: str, items: list[dict]) -> int:
    """Inserta los items que no existan ya en BD comparando por `field`.
    Devuelve cuántos se han creado. Tolerante a duplicados preexistentes
    (usa `.first()` en vez de `.scalar_one_or_none()`).
    """
    creados = 0
    for data in items:
        existente = (
            await session.execute(select(model).where(getattr(model, field) == data[field]))
        ).scalars().first()
        if existente is None:
            session.add(model(id=uuid.uuid4(), **data))
            creados += 1
    if creados:
        await session.flush()
    return creados


async def ensure_catalogos_base(session: AsyncSession) -> None:
    """Siembra todos los catálogos esenciales para un entorno greenfield.

    Idempotente: compara por `nombre` (o `codigo`) y solo añade lo que falte.
    """
    resultados: dict[str, int] = {}

    # Estados que heredan de EstadoBase (por nombre)
    for model, items in (
        (EstadoCuota, _ESTADOS_CUOTA),
        (EstadoDonacion, _ESTADOS_DONACION),
        (EstadoRemesa, _ESTADOS_REMESA),
        (EstadoOrdenCobro, _ESTADOS_ORDEN_COBRO),
        (EstadoTarea, _ESTADOS_TAREA),
        (EstadoParticipante, _ESTADOS_PARTICIPANTE),
        (EstadoNotificacion, _ESTADOS_NOTIFICACION),
    ):
        n = await _ensure_by_field(session, model, "nombre", items)
        if n:
            resultados[model.__name__] = n

    # Estados de Secretaría: la BD añade `codigo NOT NULL` (migración) que
    # no está en el modelo ORM. Sembramos por SQL crudo, idempotente.
    for tabla, filas in (
        ("estados_reunion", _ESTADOS_REUNION),
        ("estados_acta", _ESTADOS_ACTA),
        ("estados_ejecucion_acuerdo", _ESTADOS_EJECUCION_ACUERDO),
    ):
        creados = 0
        for (codigo, nombre, descripcion, orden, es_inicial, es_final, color) in filas:
            existe = await session.execute(
                text(f"SELECT 1 FROM {tabla} WHERE codigo = :codigo LIMIT 1"),
                {"codigo": codigo},
            )
            if existe.first() is None:
                await session.execute(
                    text(
                        f"INSERT INTO {tabla} "
                        "(id, codigo, nombre, descripcion, orden, es_inicial, es_final, activo, color) "
                        "VALUES (gen_random_uuid(), :codigo, :nombre, :descripcion, :orden, :es_inicial, :es_final, TRUE, :color)"
                    ),
                    {
                        "codigo": codigo, "nombre": nombre, "descripcion": descripcion,
                        "orden": orden, "es_inicial": es_inicial, "es_final": es_final,
                        "color": color,
                    },
                )
                creados += 1
        if creados:
            resultados[tabla] = creados

    # estados_convenio: esquema reducido (sin codigo/es_inicial/es_final/color).
    creados_conv = 0
    for (nombre, descripcion, orden) in _ESTADOS_CONVENIO_SIMPLE:
        existe = await session.execute(
            text("SELECT 1 FROM estados_convenio WHERE nombre = :nombre LIMIT 1"),
            {"nombre": nombre},
        )
        if existe.first() is None:
            await session.execute(
                text(
                    "INSERT INTO estados_convenio "
                    "(id, nombre, descripcion, orden, activo) "
                    "VALUES (gen_random_uuid(), :nombre, :descripcion, :orden, TRUE)"
                ),
                {"nombre": nombre, "descripcion": descripcion, "orden": orden},
            )
            creados_conv += 1
    if creados_conv:
        resultados["estados_convenio"] = creados_conv

    # EstadoPlanificacion: esquema propio con `codigo` único
    n = await _ensure_by_field(session, EstadoPlanificacion, "codigo", _ESTADOS_PLANIFICACION)
    if n:
        resultados["EstadoPlanificacion"] = n

    # Catálogos por nombre
    for model, items in (
        (MotivoBaja, _MOTIVOS_BAJA),
        (TipoVinculacion, _TIPOS_VINCULACION),
        (NivelEstudios, _NIVELES_ESTUDIOS),
        (NivelHabilidad, _NIVELES_HABILIDAD),
        (TipoReunion, _TIPOS_REUNION),
        (TipoConvenio, _TIPOS_CONVENIO),
        (TipoEntidadJuridica, _TIPOS_ORGANIZACION),
    ):
        n = await _ensure_by_field(session, model, "nombre", items)
        if n:
            resultados[model.__name__] = n

    # Catálogos por código
    for model, items in (
        (MotivoReduccionCuota, _MOTIVOS_REDUCCION_CUOTA),
        (FormaPago, _FORMAS_PAGO),
    ):
        n = await _ensure_by_field(session, model, "codigo", items)
        if n:
            resultados[model.__name__] = n

    # Cláusulas RGPD: comparar por (codigo, version)
    creados_clausulas = 0
    for data in _CLAUSULAS_RGPD:
        existente = (
            await session.execute(
                select(ClausulaInformativa).where(
                    ClausulaInformativa.codigo == data["codigo"],
                    ClausulaInformativa.version == data["version"],
                )
            )
        ).scalar_one_or_none()
        if existente is None:
            session.add(ClausulaInformativa(id=uuid.uuid4(), **data))
            creados_clausulas += 1
    if creados_clausulas:
        await session.flush()
        resultados["ClausulaInformativa"] = creados_clausulas

    for modelo, n in resultados.items():
        print(f"[bootstrap] {modelo}: +{n} registros creados")
