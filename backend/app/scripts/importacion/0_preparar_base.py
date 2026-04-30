"""
Script para preparar la base de datos con datos iniciales.
Crea el usuario legacy y los catálogos base con auditoría correcta.
"""
import asyncio
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.core.database import get_database_url

# UUID fijo para el usuario legacy (importación de datos)
LEGACY_USER_ID = uuid.UUID('b03dd8ad-e547-4a2e-a0af-4c8e0956ef76')


async def crear_catalogos_base(session: AsyncSession):
    """Crea los catálogos base con auditoría correcta."""

    now = datetime.now()

    # Tipos de Miembro
    tipos_miembro = [
        ('miembro', 'miembro', 'Miembro de pleno derecho', True, True, 1),
        ('SIMPATIZANTE', 'Simpatizante', 'Simpatizante sin cuota', False, False, 2),
        ('VOLUNTARIO', 'Voluntario', 'Voluntario activo', False, False, 3),
        ('COLABORADOR', 'Colaborador', 'Colaborador externo', False, False, 4),
    ]

    for codigo, nombre, descripcion, requiere_cuota, puede_votar, orden in tipos_miembro:
        await session.execute(text('''
            INSERT INTO tipos_miembro (id, codigo, nombre, descripcion, requiere_cuota, puede_votar, orden, activo, fecha_creacion, eliminado, creado_por_id)
            VALUES (gen_random_uuid(), :codigo, :nombre, :descripcion, :requiere_cuota, :puede_votar, :orden, true, :fecha, false, :user_id)
            ON CONFLICT (codigo) DO NOTHING
        '''), {
            'codigo': codigo, 'nombre': nombre, 'descripcion': descripcion,
            'requiere_cuota': requiere_cuota, 'puede_votar': puede_votar, 'orden': orden,
            'fecha': now, 'user_id': LEGACY_USER_ID
        })
    print(f"  [OK] Tipos de miembro creados")

    # Estados de Miembro (sin es_inicial/es_final)
    estados_miembro = [
        ('PENDIENTE_APROBACION', 'Pendiente de aprobacion', 'Solicitud pendiente', '#FFC107', 1),
        ('ACTIVO', 'Activo', 'Miembro activo', '#28A745', 2),
        ('SUSPENDIDO', 'Suspendido', 'Miembro suspendido temporalmente', '#FD7E14', 3),
        ('BAJA', 'Baja', 'Miembro dado de baja', '#DC3545', 4),
    ]

    for codigo, nombre, descripcion, color, orden in estados_miembro:
        await session.execute(text('''
            INSERT INTO estados_miembro (id, codigo, nombre, descripcion, color, orden, activo, fecha_creacion, eliminado, creado_por_id)
            VALUES (gen_random_uuid(), :codigo, :nombre, :descripcion, :color, :orden, true, :fecha, false, :user_id)
            ON CONFLICT (codigo) DO NOTHING
        '''), {
            'codigo': codigo, 'nombre': nombre, 'descripcion': descripcion,
            'color': color, 'orden': orden,
            'fecha': now, 'user_id': LEGACY_USER_ID
        })
    print(f"  [OK] Estados de miembro creados")

    # Estados de Cuota (con es_inicial/es_final)
    estados_cuota = [
        ('PENDIENTE', 'Pendiente', 'Cuota pendiente de pago', '#FFC107', 1, True, False),
        ('PAGADA', 'Pagada', 'Cuota pagada', '#28A745', 2, False, True),
        ('PARCIAL', 'Pago parcial', 'Cuota con pago parcial', '#17A2B8', 3, False, False),
        ('VENCIDA', 'Vencida', 'Cuota vencida sin pagar', '#DC3545', 4, False, False),
        ('EXENTA', 'Exenta', 'Cuota exenta de pago', '#6C757D', 5, False, True),
        ('CANCELADA', 'Cancelada', 'Cuota cancelada', '#343A40', 6, False, True),
    ]

    for codigo, nombre, descripcion, color, orden, es_inicial, es_final in estados_cuota:
        await session.execute(text('''
            INSERT INTO estados_cuota (id, codigo, nombre, descripcion, color, orden, es_inicial, es_final, activo, fecha_creacion, eliminado, creado_por_id)
            VALUES (gen_random_uuid(), :codigo, :nombre, :descripcion, :color, :orden, :es_inicial, :es_final, true, :fecha, false, :user_id)
            ON CONFLICT (codigo) DO NOTHING
        '''), {
            'codigo': codigo, 'nombre': nombre, 'descripcion': descripcion,
            'color': color, 'orden': orden, 'es_inicial': es_inicial, 'es_final': es_final,
            'fecha': now, 'user_id': LEGACY_USER_ID
        })
    print(f"  [OK] Estados de cuota creados")

    # Estados de Campania (con es_inicial/es_final)
    estados_campania = [
        ('BORRADOR', 'Borrador', 'Campania en borrador', '#6C757D', 1, True, False),
        ('PLANIFICADA', 'Planificada', 'Campania planificada', '#17A2B8', 2, False, False),
        ('ACTIVA', 'Activa', 'Campania en curso', '#28A745', 3, False, False),
        ('SUSPENDIDA', 'Suspendida', 'Campania suspendida', '#FD7E14', 4, False, False),
        ('FINALIZADA', 'Finalizada', 'Campania finalizada', '#007BFF', 5, False, True),
        ('CANCELADA', 'Cancelada', 'Campania cancelada', '#DC3545', 6, False, True),
    ]

    for codigo, nombre, descripcion, color, orden, es_inicial, es_final in estados_campania:
        await session.execute(text('''
            INSERT INTO estados_campania (id, codigo, nombre, descripcion, color, orden, es_inicial, es_final, activo, fecha_creacion, eliminado, creado_por_id)
            VALUES (gen_random_uuid(), :codigo, :nombre, :descripcion, :color, :orden, :es_inicial, :es_final, true, :fecha, false, :user_id)
            ON CONFLICT (codigo) DO NOTHING
        '''), {
            'codigo': codigo, 'nombre': nombre, 'descripcion': descripcion,
            'color': color, 'orden': orden, 'es_inicial': es_inicial, 'es_final': es_final,
            'fecha': now, 'user_id': LEGACY_USER_ID
        })
    print(f"  [OK] Estados de campania creados")

    # Tipos de Campania
    tipos_campania = [
        ('CAPTACION', 'Captacion', 'Campania de captacion de miembros'),
        ('SENSIBILIZACION', 'Sensibilizacion', 'Campania de sensibilizacion'),
        ('RECAUDACION', 'Recaudacion', 'Campania de recaudacion de fondos'),
        ('FIRMAS', 'Recogida de firmas', 'Campania de recogida de firmas'),
        ('DIFUSION', 'Difusion', 'Campania de difusion'),
    ]

    for codigo, nombre, descripcion in tipos_campania:
        await session.execute(text('''
            INSERT INTO tipos_campania (id, codigo, nombre, descripcion, activo, fecha_creacion, eliminado, creado_por_id)
            VALUES (gen_random_uuid(), :codigo, :nombre, :descripcion, true, :fecha, false, :user_id)
            ON CONFLICT (codigo) DO NOTHING
        '''), {
            'codigo': codigo, 'nombre': nombre, 'descripcion': descripcion,
            'fecha': now, 'user_id': LEGACY_USER_ID
        })
    print(f"  [OK] Tipos de campania creados")

    # Motivos de Baja
    motivos_baja = [
        ('VOLUNTARIA', 'Baja voluntaria', 'El miembro solicita la baja voluntariamente', False),
        ('IMPAGO', 'Impago de cuotas', 'Baja por impago reiterado de cuotas', False),
        ('FALLECIMIENTO', 'Fallecimiento', 'Baja por fallecimiento del miembro', True),
        ('EXPULSION', 'Expulsion', 'Baja por expulsion disciplinaria', True),
    ]

    for codigo, nombre, descripcion, requiere_doc in motivos_baja:
        await session.execute(text('''
            INSERT INTO motivos_baja (id, codigo, nombre, descripcion, requiere_documentacion, activo, fecha_creacion, eliminado, creado_por_id)
            VALUES (gen_random_uuid(), :codigo, :nombre, :descripcion, :requiere_doc, true, :fecha, false, :user_id)
            ON CONFLICT (codigo) DO NOTHING
        '''), {
            'codigo': codigo, 'nombre': nombre, 'descripcion': descripcion,
            'requiere_doc': requiere_doc,
            'fecha': now, 'user_id': LEGACY_USER_ID
        })
    print(f"  [OK] Motivos de baja creados")

    await session.commit()


async def main():
    print("=" * 60)
    print("PREPARACION DE BASE DE DATOS")
    print("=" * 60)

    engine = create_async_engine(get_database_url(), echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print(f"\nUsuario legacy: {LEGACY_USER_ID}")
        print("\nCreando catalogos base...")
        await crear_catalogos_base(session)

    await engine.dispose()

    print("\n" + "=" * 60)
    print("[OK] BASE DE DATOS PREPARADA")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
