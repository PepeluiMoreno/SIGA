"""Seed de roles funcionales del sistema y sus transacciones.

Crea los roles funcionales (tipo FUNCIONAL) que el sistema necesita en cualquier
despliegue, con sus transacciones asociadas. Es idempotente y se invoca desde
bootstrap.py en cada arranque.

Roles que crea:
- PLANIFICADOR: diseña, crea y gestiona campañas, eventos y grupos de actividad.
- GESTOR_MIEMBROS: gestión operativa del padrón (sin acceso a administración del sistema).
- INTERVENTOR: control presupuestario — fija la cuota, elabora, aprueba y supervisa
  el presupuesto y su liquidación. No ejecuta pagos ni cobros (eso es de tesorería).
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
            "CAMPANA_LISTAR", "CAMP_VIEW", "CAMPANA_CREAR", "CAMPANA_EDITAR",
            "CAMP_ACTIVATE", "CAMP_CLOSE", "CAMP_CANCEL",
            "PART_ENROLL", "PART_REMOVE", "PART_HOURS",
            # Eventos
            "EVT_LIST", "EVT_VIEW", "EVT_CREATE", "EVT_EDIT",
            "EVT_CANCEL", "EVT_MANAGE_REG", "EVT_ATTENDANCE",
            # Grupos de trabajo
            "GRUPO_LISTAR", "TEAM_VIEW", "GRUPO_CREAR", "TEAM_EDIT",
            "TEAM_DISSOLVE", "TMBR_ADD", "TMBR_REMOVE",
            # Tareas y reuniones
            "TASK_CREATE", "TASK_UPDATE", "MEET_SCHEDULE",
            # Voluntariado / habilidades (para dotar de RR.HH. las actividades)
            "MEMBRESIA_VOLUNTARIO_LISTAR", "VOL_VIEW", "HAB_LIST", "MEMBRESIA_VOLUNTARIO_GESTIONAR",
            # Consulta de miembros (necesaria para asignar participantes y responsables)
            "MEMBRESIA_MIEMBRO_LISTAR", "SOC_VIEW",
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
            "MEMBRESIA_MIEMBRO_LISTAR", "SOC_VIEW", "MEMBRESIA_MIEMBRO_CREAR", "SOC_EDIT",
            "SOC_DEACTIVATE", "SOC_REACTIVATE", "SOC_CHANGE_TYPE", "MEMBRESIA_MIEMBRO_EXPORTAR",
            "TIPOSOC_MANAGE",
            "TRAS_REQUEST", "TRAS_LIST", "TRAS_APPROVE", "TRAS_REJECT",
            "TRAS_CANCEL", "TRAS_APPROVE_DEST", "TRAS_EXECUTE",
            "HAB_LIST", "MEMBRESIA_VOLUNTARIO_GESTIONAR", "HAB_VALIDATE",
            "AVAIL_VIEW", "AVAIL_EDIT",
            "MBR_HISTORY",
            "AGR_LIST", "AGR_VIEW",
            "RPT_MEMBERS",
        ],
    },
    {
        "codigo": "INTERVENTOR",
        "nombre": "Interventor/a",
        "descripcion": (
            "Control presupuestario de la entidad. Fija la cuota del ejercicio, "
            "elabora, aprueba y supervisa el presupuesto y su liquidación. "
            "No ejecuta cobros ni pagos: esa función es de tesorería."
        ),
        "nivel": 30,
        "es_territorial": True,
        "transacciones": [
            # Presupuesto: ciclo completo de planificación y control
            "ECO_PRESUPUESTO_CREAR", "ECO_PRESUPUESTO_APROBAR", "ECO_PRESUPUESTO_CONSULTAR",
            # Cuota del ejercicio: establecimiento y anulación (condición previa al presupuesto)
            "ECO_CUOTA_CONFIGURAR", "ECO_CUOTA_LISTAR", "CUOT_MOTIVO_LIST",
            # Consulta financiera de apoyo al control
            "ECO_BALANCE_CONSULTAR", "ECO_ESTRUCTURA_CONTABLE_LISTAR",
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
