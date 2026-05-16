"""Seed de roles funcionales del sistema y sus transacciones.

Crea los roles funcionales (tipo FUNCIONAL) que el sistema necesita en cualquier
despliegue, con sus transacciones asociadas. Es idempotente y se invoca desde
bootstrap.py en cada arranque.

Roles que crea:
- PLANIFICADOR: diseña, crea y gestiona campañas, eventos y grupos de actividad.
- GESTOR_MIEMBROS: gestión operativa del padrón (sin acceso a administración del sistema).
"""

import uuid
from datetime import datetime

from sqlalchemy import select

from app.modules.acceso.models.rol import Rol, TipoRol
from app.modules.acceso.models.rol_transaccion import RolTransaccion
from app.modules.acceso.models.transaccion import Transaccion


# ---------------------------------------------------------------------------
# Definición de roles funcionales de sistema
# ---------------------------------------------------------------------------

_ROLES = [
    {
        "codigo": "PLANIFICADOR",
        "nombre": "Planificador",
        "descripcion": (
            "Diseña y gestiona campañas, eventos y grupos de actividad. "
            "Es candidato a responsable de cualquier actividad planificada."
        ),
        "nivel": 20,
        "es_territorial": True,   # El rol puede ser de ámbito territorial via UsuarioRol.agrupacion_id
        "transacciones": [
            # Campañas
            "CAMP_LIST", "CAMP_VIEW", "CAMP_CREATE", "CAMP_EDIT",
            "CAMP_ACTIVATE", "CAMP_CLOSE", "CAMP_CANCEL",
            "PART_ENROLL", "PART_REMOVE", "PART_HOURS",
            # Eventos
            "EVT_LIST", "EVT_VIEW", "EVT_CREATE", "EVT_EDIT",
            "EVT_CANCEL", "EVT_MANAGE_REG", "EVT_ATTENDANCE",
            # Grupos de trabajo
            "TEAM_LIST", "TEAM_VIEW", "TEAM_CREATE", "TEAM_EDIT",
            "TEAM_DISSOLVE", "TMBR_ADD", "TMBR_REMOVE",
            # Tareas y reuniones
            "TASK_CREATE", "TASK_UPDATE", "MEET_SCHEDULE",
            # Voluntariado / habilidades (para dotar de RR.HH. las actividades)
            "VOL_LIST", "VOL_VIEW", "HAB_LIST", "HAB_ASSIGN",
            # Consulta de miembros (necesaria para asignar participantes y responsables)
            "SOC_LIST", "SOC_VIEW",
            # Informes de actividad
            "RPT_CAMPAIGNS", "RPT_VOLUNTEERS",
        ],
    },
    {
        "codigo": "GESTOR_MIEMBROS",
        "nombre": "Gestor de miembros",
        "descripcion": (
            "Gestión operativa del padrón: altas, bajas, cambios de tipo y traslados. "
            "No tiene acceso a administración del sistema ni a finanzas."
        ),
        "nivel": 15,
        "es_territorial": True,
        "transacciones": [
            "SOC_LIST", "SOC_VIEW", "SOC_CREATE", "SOC_EDIT",
            "SOC_DEACTIVATE", "SOC_REACTIVATE", "SOC_CHANGE_TYPE", "SOC_EXPORT",
            "TIPOSOC_MANAGE",
            "TRAS_REQUEST", "TRAS_LIST", "TRAS_APPROVE", "TRAS_REJECT",
            "TRAS_CANCEL", "TRAS_APPROVE_DEST", "TRAS_EXECUTE",
            "HAB_LIST", "HAB_ASSIGN", "HAB_VALIDATE",
            "AVAIL_VIEW", "AVAIL_EDIT",
            "MBR_HISTORY",
            "AGR_LIST", "AGR_VIEW",
            "RPT_MEMBERS",
        ],
    },
]


async def seed(session, transacciones: dict) -> None:
    """Crea los roles funcionales de sistema y les asigna sus transacciones.

    Args:
        session: AsyncSession activa (la misma que usa bootstrap para no fragmentar la tx).
        transacciones: dict {codigo: Transaccion} cargado por sync_transacciones().
    """
    now = datetime.utcnow()

    for rol_def in _ROLES:
        # Obtener o crear el rol
        rol = (await session.execute(
            select(Rol).where(Rol.codigo == rol_def["codigo"])
        )).scalar_one_or_none()

        if rol is None:
            rol = Rol(
                id=uuid.uuid4(),
                codigo=rol_def["codigo"],
                nombre=rol_def["nombre"],
                descripcion=rol_def["descripcion"],
                tipo=TipoRol.FUNCIONAL,
                nivel=rol_def["nivel"],
                es_territorial=rol_def["es_territorial"],
                sistema=True,
                activo=True,
                fecha_creacion=now,
                eliminado=False,
            )
            session.add(rol)
            await session.flush()
            print(f"[bootstrap] Rol '{rol_def['codigo']}' creado")
        else:
            # Sincronizar nombre/descripción por si cambiaron
            rol.nombre = rol_def["nombre"]
            rol.descripcion = rol_def["descripcion"]

        # Asignar transacciones que le falten
        existing_trans_ids = {
            rt.transaccion_id
            for rt in (await session.execute(
                select(RolTransaccion).where(RolTransaccion.rol_id == rol.id)
            )).scalars()
        }

        added = 0
        for codigo in rol_def["transacciones"]:
            trans = transacciones.get(codigo)
            if trans is None:
                continue  # La transacción no existe todavía en el JSON
            if trans.id not in existing_trans_ids:
                session.add(RolTransaccion(
                    rol_id=rol.id,
                    transaccion_id=trans.id,
                    fecha_creacion=now,
                    eliminado=False,
                ))
                added += 1

        if added:
            await session.flush()
            print(f"[bootstrap] Rol '{rol_def['codigo']}': +{added} transacciones enlazadas")
