"""Seed idempotente del subsistema de comunicación.

Siembra, por código y sin duplicar:
  - Los estados de notificación (PENDIENTE, ENVIADA, LEIDA, ERROR).
  - El catálogo de tipos de notificación que disparan los flujos de trabajo.

La PRIORIDAD de cada tipo decide si, además del aviso in-app, se envía email:
ALTA y URGENTE ⇒ también email; NORMAL y BAJA ⇒ solo in-app.

Idempotente: crea lo que falta y actualiza los campos editables de lo existente
(nombre, descripción, prioridad, canales, icono, color, activo), conservando el
id. Pensado para ejecutarse en cada arranque del bootstrap.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.configuracion.models.estados import EstadoNotificacion
from app.modules.core.comunicacion import TipoNotificacion


# ── Estados de notificación ──────────────────────────────────────────────────

_ESTADOS = [
    {"codigo": "PENDIENTE", "nombre": "Pendiente", "orden": 1, "es_inicial": True,
     "color": "#F59E0B", "descripcion": "Notificación creada pero no enviada"},
    {"codigo": "ENVIADA",   "nombre": "Enviada",   "orden": 2,
     "color": "#0EA5E9", "descripcion": "Notificación enviada al canal correspondiente"},
    {"codigo": "LEIDA",     "nombre": "Leída",     "orden": 3,
     "color": "#22C55E", "descripcion": "Notificación leída por el usuario"},
    {"codigo": "ERROR",     "nombre": "Error",     "orden": 4, "es_final": True,
     "color": "#EF4444", "descripcion": "Error al enviar la notificación"},
]


# ── Catálogo de tipos de notificación de flujos de trabajo ───────────────────
#
# categoria: agrupador funcional (FINANCIERO, SECRETARIA, MEMBRESIA, ACTIVIDADES,
#            SISTEMA). prioridad: BAJA | NORMAL | ALTA | URGENTE (decide email).
# requiere_accion: si el destinatario debe hacer algo (visar, aprobar, firmar).

_TIPOS = [
    # — Económico / Presupuestos —
    {"codigo": "PRESUPUESTO_DESVIACION", "nombre": "Desviación presupuestaria",
     "categoria": "FINANCIERO", "prioridad": "NORMAL", "requiere_accion": False,
     "icono": "chart-bar", "color": "#F59E0B",
     "descripcion": "Una partida presupuestaria se ha sobreejecutado o agotado."},

    # — Económico / Remesas y cobro —
    {"codigo": "REMESA_LISTA_ENVIO", "nombre": "Remesa lista para envío",
     "categoria": "FINANCIERO", "prioridad": "ALTA", "requiere_accion": True,
     "icono": "banknotes", "color": "#0EA5E9",
     "descripcion": "Una remesa SEPA está generada y pendiente de envío al banco."},
    {"codigo": "REMESA_DEVOLUCION", "nombre": "Devolución de remesa",
     "categoria": "FINANCIERO", "prioridad": "ALTA", "requiere_accion": True,
     "icono": "arrow-uturn-left", "color": "#EF4444",
     "descripcion": "El banco ha devuelto uno o varios adeudos de una remesa."},

    # — Económico / Cuotas —
    {"codigo": "CUOTA_REDUCCION_SOLICITADA", "nombre": "Solicitud de reducción de cuota",
     "categoria": "FINANCIERO", "prioridad": "NORMAL", "requiere_accion": True,
     "icono": "receipt-percent", "color": "#F59E0B",
     "descripcion": "Un socio ha solicitado una reducción o exención de cuota."},
    {"codigo": "CUOTA_REDUCCION_RESUELTA", "nombre": "Resolución de reducción de cuota",
     "categoria": "FINANCIERO", "prioridad": "ALTA", "requiere_accion": False,
     "icono": "check-badge", "color": "#22C55E",
     "descripcion": "Se ha resuelto una solicitud de reducción o exención de cuota."},

    # — Secretaría / Reuniones y actas —
    {"codigo": "SECRETARIA_CONVOCATORIA", "nombre": "Convocatoria de reunión",
     "categoria": "SECRETARIA", "prioridad": "ALTA", "requiere_accion": True,
     "icono": "calendar-days", "color": "#0EA5E9",
     "descripcion": "Se ha convocado una reunión de un órgano de gobierno."},
    {"codigo": "SECRETARIA_ACTA_BORRADOR", "nombre": "Acta en borrador",
     "categoria": "SECRETARIA", "prioridad": "NORMAL", "requiere_accion": True,
     "icono": "document-text", "color": "#F59E0B",
     "descripcion": "Hay un acta en borrador pendiente de revisión."},
    {"codigo": "SECRETARIA_ACTA_APROBADA", "nombre": "Acta aprobada",
     "categoria": "SECRETARIA", "prioridad": "ALTA", "requiere_accion": True,
     "icono": "document-check", "color": "#22C55E",
     "descripcion": "Un acta ha sido aprobada y está lista para su firma."},

    # — Membresía / Nombramientos y traslados —
    {"codigo": "NOMBRAMIENTO_PENDIENTE_APROBACION", "nombre": "Nombramiento pendiente de aprobación",
     "categoria": "MEMBRESIA", "prioridad": "ALTA", "requiere_accion": True,
     "icono": "user-plus", "color": "#0EA5E9",
     "descripcion": "Un nombramiento de cargo está pendiente de tu aprobación."},
    {"codigo": "TRASLADO_SOLICITADO", "nombre": "Solicitud de traslado",
     "categoria": "MEMBRESIA", "prioridad": "NORMAL", "requiere_accion": True,
     "icono": "arrows-right-left", "color": "#F59E0B",
     "descripcion": "Un socio ha solicitado el traslado a otra agrupación."},
    {"codigo": "TRASLADO_RESUELTO", "nombre": "Resolución de traslado",
     "categoria": "MEMBRESIA", "prioridad": "ALTA", "requiere_accion": False,
     "icono": "check-badge", "color": "#22C55E",
     "descripcion": "Se ha resuelto una solicitud de traslado de agrupación."},
    {"codigo": "MIEMBRO_PERFIL_INCOMPLETO", "nombre": "Perfil de socio incompleto",
     "categoria": "MEMBRESIA", "prioridad": "NORMAL", "requiere_accion": True,
     "icono": "exclamation-triangle", "color": "#F59E0B",
     "descripcion": "Un miembro tiene campos clave sin rellenar (tipo, estado, email o teléfono)."},

    # — Actividades / Campañas y grupos —
    {"codigo": "TAREA_ASIGNADA", "nombre": "Tarea asignada",
     "categoria": "ACTIVIDADES", "prioridad": "NORMAL", "requiere_accion": True,
     "icono": "clipboard-document-list", "color": "#0EA5E9",
     "descripcion": "Se te ha asignado una tarea en un grupo de trabajo."},
    {"codigo": "GRUPO_REUNION_CONVOCADA", "nombre": "Reunión de grupo convocada",
     "categoria": "ACTIVIDADES", "prioridad": "ALTA", "requiere_accion": True,
     "icono": "users", "color": "#0EA5E9",
     "descripcion": "Se ha convocado una reunión de un grupo de trabajo."},

    # — Acceso / Seguridad —
    {"codigo": "SEGURIDAD_IP_BLOQUEADA", "nombre": "IP bloqueada",
     "categoria": "SISTEMA", "prioridad": "URGENTE", "requiere_accion": False,
     "icono": "shield-exclamation", "color": "#EF4444",
     "descripcion": "Se ha bloqueado una IP por intentos de acceso anómalos."},
]

# Campos que se actualizan en registros existentes (no tocan el id).
_CAMPOS_TIPO_ACTUALIZABLES = (
    "nombre", "descripcion", "categoria", "prioridad",
    "requiere_accion", "icono", "color",
)


async def ensure_estados_notificacion(session: AsyncSession) -> None:
    """Crea/actualiza los estados de notificación. Idempotente por código."""
    added = updated = 0
    for data in _ESTADOS:
        existing = (
            await session.execute(
                select(EstadoNotificacion).where(EstadoNotificacion.codigo == data["codigo"])
            )
        ).scalar_one_or_none()
        if existing is None:
            session.add(EstadoNotificacion(id=uuid.uuid4(), activo=True, **data))
            added += 1
        else:
            for campo in ("nombre", "descripcion", "orden", "color"):
                if campo in data and getattr(existing, campo) != data[campo]:
                    setattr(existing, campo, data[campo])
                    updated += 1
    if added or updated:
        await session.flush()
        print(f"[bootstrap] EstadoNotificacion: +{added} creados, {updated} actualizados")


async def ensure_tipos_notificacion(session: AsyncSession) -> None:
    """Crea/actualiza el catálogo de tipos de notificación. Idempotente por código."""
    added = updated = 0
    for data in _TIPOS:
        existing = (
            await session.execute(
                select(TipoNotificacion).where(TipoNotificacion.codigo == data["codigo"])
            )
        ).scalar_one_or_none()
        if existing is None:
            session.add(TipoNotificacion(
                id=uuid.uuid4(),
                codigo=data["codigo"],
                nombre=data["nombre"],
                descripcion=data.get("descripcion"),
                categoria=data["categoria"],
                prioridad=data["prioridad"],
                requiere_accion=data.get("requiere_accion", False),
                icono=data.get("icono"),
                color=data.get("color"),
                permite_email=True,
                permite_push=True,
                permite_inapp=True,
                permite_sms=False,
                activo=True,
            ))
            added += 1
        else:
            cambiado = False
            for campo in _CAMPOS_TIPO_ACTUALIZABLES:
                if campo in data and getattr(existing, campo) != data[campo]:
                    setattr(existing, campo, data[campo])
                    cambiado = True
            if cambiado:
                updated += 1
    if added or updated:
        await session.flush()
        print(f"[bootstrap] TipoNotificacion: +{added} creados, {updated} actualizados")


async def seed_comunicacion(session: AsyncSession) -> None:
    """Punto de entrada del seed de comunicación (estados + tipos)."""
    await ensure_estados_notificacion(session)
    await ensure_tipos_notificacion(session)
