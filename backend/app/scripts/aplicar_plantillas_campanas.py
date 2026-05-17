"""Aplica la plantilla correspondiente a cada campaña sembrada por scraping.

Condición de idempotencia: si la campaña ya tiene metas o partidas, se salta.
Uso: docker exec siga_dev_backend python -m app.scripts.aplicar_plantillas_campanas
"""
import asyncio
import uuid
from datetime import timedelta

from sqlalchemy import select, func, text
from sqlalchemy.orm import selectinload

from app.core.database import async_session
from app.modules.actividades.models.campana import (
    Campania, MetaCampania, PartidaPresupuestoCampania,
    PlantillaCampania,
)
from app.modules.actividades.models.actividad import Actividad
from app.modules.actividades.models.tarea import Tarea


async def aplicar_plantilla_a_campania(
    session, campania: Campania, plantilla: PlantillaCampania,
    default_tipo_actividad_id: uuid.UUID,
    default_estado_actividad_id: uuid.UUID,
    default_estado_tarea_id: uuid.UUID,
):
    # Metas
    for pm in plantilla.metas:
        session.add(MetaCampania(
            campania_id=campania.id,
            tipo_meta_id=pm.tipo_meta_id,
            valor_planificado=pm.valor_sugerido,
            notas=pm.notas,
            orden=pm.orden,
        ))

    # Partidas
    for pp in plantilla.partidas:
        session.add(PartidaPresupuestoCampania(
            campania_id=campania.id,
            concepto=pp.concepto,
            importe_estimado=pp.importe_estimado,
            tipo_partida=pp.tipo_partida,
            orden=pp.orden,
        ))

    # Actividades + tareas
    for pa in plantilla.actividades:
        tipo_id = pa.tipo_actividad_id or default_tipo_actividad_id
        actividad = Actividad(
            nombre=pa.nombre,
            descripcion=pa.descripcion,
            tipo_actividad_id=tipo_id,
            estado_id=default_estado_actividad_id,
            campania_id=campania.id,
        )
        if campania.fecha_inicio_plan and pa.duracion_dias is not None:
            actividad.fecha_inicio = campania.fecha_inicio_plan + timedelta(days=pa.duracion_dias)
        session.add(actividad)
        await session.flush()

        for pt in pa.tareas:
            session.add(Tarea(
                titulo=pt.titulo,
                descripcion=pt.descripcion,
                horas_estimadas=pt.horas_estimadas,
                orden=pt.orden,
                actividad_id=actividad.id,
                estado_id=default_estado_tarea_id,
            ))


async def main():
    async with async_session() as session:
        # Defaults requeridos por NOT NULL en actividades
        default_tipo_actividad_id = (
            await session.execute(text("SELECT id FROM tipos_accion ORDER BY nombre LIMIT 1"))
        ).scalar()
        default_estado_actividad_id = (
            await session.execute(text("SELECT id FROM estados_accion WHERE nombre='En preparación' LIMIT 1"))
        ).scalar() or (
            await session.execute(text("SELECT id FROM estados_accion ORDER BY nombre LIMIT 1"))
        ).scalar()
        default_estado_tarea_id = (
            await session.execute(text("SELECT id FROM estados_tarea WHERE nombre='Pendiente' LIMIT 1"))
        ).scalar() or (
            await session.execute(text("SELECT id FROM estados_tarea ORDER BY nombre LIMIT 1"))
        ).scalar()

        # Cargar plantillas con sus relaciones, indexadas por tipo_campania_id
        stmt_plantillas = (
            select(PlantillaCampania)
            .where(PlantillaCampania.activo == True)
            .options(
                selectinload(PlantillaCampania.metas),
                selectinload(PlantillaCampania.partidas),
                selectinload(PlantillaCampania.actividades).selectinload(
                    PlantillaCampania.actividades.property.mapper.class_.tareas
                ),
            )
        )
        result = await session.execute(stmt_plantillas)
        plantillas_por_tipo = {p.tipo_campania_id: p for p in result.scalars().all()}

        # Cargar campañas
        stmt_campanas = select(Campania).where(Campania.eliminado == False)
        result = await session.execute(stmt_campanas)
        campanas = result.scalars().all()

        aplicadas = 0
        saltadas_sin_plantilla = 0
        saltadas_ya_tienen = 0

        for campania in campanas:
            if campania.tipo_campania_id is None:
                saltadas_sin_plantilla += 1
                continue

            plantilla = plantillas_por_tipo.get(campania.tipo_campania_id)
            if plantilla is None:
                print(f"  [sin plantilla] {campania.nombre[:60]}")
                saltadas_sin_plantilla += 1
                continue

            # Idempotencia: saltar si ya tiene metas o partidas
            count_metas = (await session.execute(
                select(func.count()).select_from(MetaCampania)
                .where(MetaCampania.campania_id == campania.id)
            )).scalar()
            count_partidas = (await session.execute(
                select(func.count()).select_from(PartidaPresupuestoCampania)
                .where(PartidaPresupuestoCampania.campania_id == campania.id)
            )).scalar()

            if count_metas > 0 or count_partidas > 0:
                print(f"  [ya tiene datos] {campania.nombre[:60]} ({count_metas} metas, {count_partidas} partidas)")
                saltadas_ya_tienen += 1
                continue

            await aplicar_plantilla_a_campania(
                session, campania, plantilla,
                default_tipo_actividad_id, default_estado_actividad_id, default_estado_tarea_id
            )
            print(f"  [OK] {campania.nombre[:60]} ← {plantilla.nombre}")
            aplicadas += 1

        await session.commit()
        print(f"\nResumen: {aplicadas} aplicadas, {saltadas_ya_tienen} ya tenían datos, {saltadas_sin_plantilla} sin plantilla.")


if __name__ == "__main__":
    asyncio.run(main())
