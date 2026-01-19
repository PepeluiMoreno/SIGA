"""
Script para establecer la jerarquia de agrupaciones territoriales ya importadas.

Este script actualiza el campo agrupacion_padre_id basandose en los codigos:
- Estatal (0) -> sin padre
- Autonomicas (100000, 200000, etc.) -> padre estatal (0)
- Provinciales (104000, 111000, etc.) -> padre autonomica (100000, 200000, etc.)
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from app.core.database import get_database_url
from app.domains.geografico.models.direccion import AgrupacionTerritorial


async def main():
    """Funcion principal."""

    print("\n" + "="*80)
    print("ESTABLECER JERARQUIA DE AGRUPACIONES TERRITORIALES")
    print("="*80 + "\n")

    # Conectar a PostgreSQL
    print("Conectando a PostgreSQL...")
    database_url = get_database_url()
    engine = create_async_engine(
        database_url,
        echo=False,
        connect_args={"statement_cache_size": 0}
    )
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # Cargar todas las agrupaciones
            print("\nCargando agrupaciones...")
            result = await session.execute(
                select(AgrupacionTerritorial).order_by(AgrupacionTerritorial.codigo)
            )
            agrupaciones = result.scalars().all()
            print(f"  [OK] {len(agrupaciones)} agrupaciones encontradas")

            # Crear mapeo codigo -> UUID
            mapeo = {agrup.codigo: agrup.id for agrup in agrupaciones}

            # Establecer jerarquia
            print("\nEstableciendo jerarquia...")
            actualizadas = 0
            sin_padre = 0

            for agrup in agrupaciones:
                try:
                    codigo = int(agrup.codigo)
                except (ValueError, TypeError):
                    sin_padre += 1
                    continue

                codigo_padre = None

                # Logica de jerarquia
                if codigo == 0 or codigo >= 70000000:
                    # Estatal/Internacional no tienen padre
                    sin_padre += 1
                    continue

                elif codigo >= 100000:
                    # Puede ser autonomica o provincial
                    if codigo % 100000 == 0:
                        # Es autonomica (100000, 200000, etc.) -> padre es estatal (0)
                        codigo_padre = '0'
                    else:
                        # Es provincial o local -> buscar autonomica
                        base_autonomica = (codigo // 100000) * 100000
                        codigo_padre = str(base_autonomica)

                # Buscar UUID del padre
                if codigo_padre and codigo_padre in mapeo:
                    uuid_padre = mapeo[codigo_padre]

                    # Actualizar agrupacion con su padre
                    await session.execute(
                        text("""
                        UPDATE agrupaciones_territoriales
                        SET agrupacion_padre_id = :padre_id
                        WHERE id = :agrupacion_id
                        """),
                        {"padre_id": uuid_padre, "agrupacion_id": agrup.id}
                    )
                    actualizadas += 1

                    if actualizadas % 10 == 0:
                        print(f"  Procesadas {actualizadas} relaciones...")
                else:
                    sin_padre += 1

            # Commit
            await session.commit()

            print(f"\n  [OK] {actualizadas} relaciones de jerarquia establecidas")
            print(f"  [INFO] {sin_padre} agrupaciones sin padre (nivel superior)")

            # Verificar resultados
            print("\nVerificando jerarquia establecida...")
            result = await session.execute(
                select(AgrupacionTerritorial.tipo,
                       text("COUNT(*) as total"),
                       text("COUNT(agrupacion_padre_id) as con_padre"))
                .group_by(AgrupacionTerritorial.tipo)
            )

            print("\nResumen por tipo:")
            for row in result.all():
                tipo = row[0]
                total = row[1]
                con_padre = row[2]
                print(f"  {tipo:15} - Total: {total:3} | Con padre: {con_padre:3}")

            print("\n" + "="*80)
            print("[OK] JERARQUIA ESTABLECIDA")
            print("="*80)

        except Exception as e:
            await session.rollback()
            print(f"\n[ERROR]: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
