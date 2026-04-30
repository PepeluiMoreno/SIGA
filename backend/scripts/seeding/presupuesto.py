"""Seeding de planificación anual y partidas presupuestarias usando mutations GraphQL."""

import asyncio
from datetime import date
from decimal import Decimal

from .graphql_client import execute_mutation, execute_query


# Queries para obtener catálogos
GET_ESTADOS_PLANIFICACION = """
query {
    estadosPlanificacion { id codigo nombre }
}
"""

GET_CATEGORIAS_PARTIDA = """
query {
    categoriasPartida { id codigo nombre }
}
"""

GET_PLANIFICACION_ANUAL = """
query GetPlanificacion($ejercicio: Int!) {
    planificacionAnual(ejercicio: $ejercicio) { id ejercicio nombre }
}
"""

# Mutations
CREAR_PLANIFICACION = """
mutation CrearPlanificacion($input: PlanificacionAnualInput!) {
    crearPlanificacionAnual(input: $input) {
        id ejercicio nombre presupuestoTotal
    }
}
"""

APROBAR_PLANIFICACION = """
mutation AprobarPlanificacion($id: UUID!, $fechaAprobacion: Date!) {
    aprobarPlanificacion(id: $id, fechaAprobacion: $fechaAprobacion) {
        id estadoId fechaAprobacion
    }
}
"""

CREAR_PARTIDA = """
mutation CrearPartida($input: PartidaPresupuestariaInput!) {
    crearPartidaPresupuestaria(input: $input) {
        id codigo nombre importePresupuestado
    }
}
"""


async def seed_planificacion_y_partidas():
    """Crear planificación anual 2026 y partidas presupuestarias usando GraphQL."""

    # Verificar si ya existe la planificación 2026
    try:
        result = await execute_query(GET_PLANIFICACION_ANUAL, {"ejercicio": 2026})
        if result.get("planificacionAnual"):
            print("  = Planificación 2026 ya existe")
            return
    except Exception:
        pass

    # Obtener estados de planificación
    estados = await execute_query(GET_ESTADOS_PLANIFICACION)
    estado_borrador = next(
        (e for e in estados.get("estadosPlanificacion", []) if e["codigo"] == "BORRADOR"),
        None
    )

    if not estado_borrador:
        print("  ! Estado BORRADOR no encontrado")
        return

    # Crear planificación 2026
    plan_input = {
        "ejercicio": 2026,
        "nombre": "Plan Anual 2026",
        "descripcion": "Planificación de actividades para el ejercicio 2026",
        "objetivos": "1. Aumentar la visibilidad de la organización\\n2. Captar 200 nuevos miembros\\n3. Organizar 4 campañas nacionales",
        "estadoId": estado_borrador["id"],
        "presupuestoTotal": "50000.00"
    }

    result = await execute_mutation(CREAR_PLANIFICACION, {"input": plan_input})
    plan = result.get("crearPlanificacionAnual")

    if not plan:
        print("  ! Error al crear planificación")
        return

    print(f"  + Planificación: {plan['nombre']}")
    plan_id = plan["id"]

    # Aprobar la planificación
    await execute_mutation(APROBAR_PLANIFICACION, {
        "id": plan_id,
        "fechaAprobacion": "2025-12-15"
    })
    print("  + Planificación aprobada")

    # Obtener categorías de partida
    categorias_result = await execute_query(GET_CATEGORIAS_PARTIDA)
    categorias = {c["codigo"]: c["id"] for c in categorias_result.get("categoriasPartida", [])}

    # Crear partidas presupuestarias
    partidas_data = [
        {"codigo": "2026-CAMP-001", "nombre": "Campaña Laicismo Escolar", "tipo": "GASTO", "categoria": "CAMPANIAS", "importe": "8000.00"},
        {"codigo": "2026-CAMP-002", "nombre": "Campaña Separación Iglesia-Estado", "tipo": "GASTO", "categoria": "CAMPANIAS", "importe": "6000.00"},
        {"codigo": "2026-CAMP-003", "nombre": "Campaña Memoria Histórica", "tipo": "GASTO", "categoria": "CAMPANIAS", "importe": "5000.00"},
        {"codigo": "2026-EVT-001", "nombre": "Jornadas Anuales de Laicismo", "tipo": "GASTO", "categoria": "EVENTOS", "importe": "10000.00"},
        {"codigo": "2026-EVT-002", "nombre": "Encuentro Nacional de Agrupaciones", "tipo": "GASTO", "categoria": "EVENTOS", "importe": "4000.00"},
        {"codigo": "2026-FORM-001", "nombre": "Formación de Voluntarios", "tipo": "GASTO", "categoria": "FORMACION", "importe": "3000.00"},
        {"codigo": "2026-COM-001", "nombre": "Comunicación y RRSS", "tipo": "GASTO", "categoria": "COMUNICACION", "importe": "5000.00"},
        {"codigo": "2026-DESP-001", "nombre": "Desplazamientos y dietas", "tipo": "GASTO", "categoria": "DESPLAZAMIENTOS", "importe": "4000.00"},
    ]

    for p in partidas_data:
        partida_input = {
            "codigo": p["codigo"],
            "nombre": p["nombre"],
            "descripcion": f"Partida para {p['nombre']}",
            "ejercicio": 2026,
            "tipo": p["tipo"],
            "categoriaId": categorias.get(p["categoria"]),
            "importePresupuestado": p["importe"],
            "planificacionId": plan_id
        }

        try:
            result = await execute_mutation(CREAR_PARTIDA, {"input": partida_input})
            partida = result.get("crearPartidaPresupuestaria")
            if partida:
                print(f"  + Partida: {partida['codigo']} - {partida['nombre']}")
        except Exception as e:
            print(f"  ! Error al crear partida {p['codigo']}: {e}")

    print("Planificación y partidas completadas.")


if __name__ == "__main__":
    asyncio.run(seed_planificacion_y_partidas())
