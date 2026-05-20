"""Seed catálogos necesarios para miembros. Idempotente.

Crea:
- EstadoMiembro: Alta, Baja, Pendiente, Suspendido
- TipoMiembro: Ordinario, De honor, Simpatizante
- FormaPago: Transferencia bancaria, Domiciliación SEPA, Tarjeta, Efectivo

Se ejecuta via:
    docker exec <backend-container> python -m app.scripts.seeding.seed_catalogos_miembros
"""

import asyncio
import uuid
from sqlalchemy import select

from app.core.database import async_session
from app.modules.membresia.models.estado_miembro import EstadoMiembro
from app.modules.membresia.models.miembro import TipoMiembro
from app.modules.economico.models.cobro.forma_pago import FormaPago


ESTADOS_MIEMBRO = [
    {"nombre": "Alta",       "descripcion": "Miembro activo en la organización",              "color": "#28A745", "orden": 1, "es_inicial": True,  "activo": True},
    {"nombre": "Pendiente",  "descripcion": "Alta solicitada, pendiente de revisión",         "color": "#FFC107", "orden": 2, "es_inicial": False, "activo": True},
    {"nombre": "Suspendido", "descripcion": "Miembro temporalmente suspendido",               "color": "#FFA500", "orden": 3, "es_inicial": False, "activo": True},
    {"nombre": "Baja",       "descripcion": "Miembro dado de baja definitiva",                "color": "#DC3545", "orden": 4, "es_inicial": False, "activo": True},
]

TIPOS_MIEMBRO = [
    {"nombre": "Ordinario",   "descripcion": "Miembro de pleno derecho",                     "requiere_cuota": True,  "puede_votar": True,  "orden": 1, "activo": True},
    {"nombre": "De honor",    "descripcion": "Miembro honorario",                            "requiere_cuota": False, "puede_votar": False, "orden": 2, "activo": True},
    {"nombre": "Simpatizante","descripcion": "Simpatizante sin derecho a voto",              "requiere_cuota": False, "puede_votar": False, "orden": 3, "activo": True},
]

FORMAS_PAGO = [
    {"codigo": "TRANSFERENCIA", "nombre": "Transferencia bancaria",  "descripcion": "Transferencia bancaria nacional", "activo": True},
    {"codigo": "DOMICILIACION", "nombre": "Domiciliación SEPA",      "descripcion": "Domiciliación bancaria SEPA",      "activo": True},
    {"codigo": "TARJETA",       "nombre": "Tarjeta",                 "descripcion": "Pago con tarjeta",                 "activo": True},
    {"codigo": "EFECTIVO",      "nombre": "Efectivo",                "descripcion": "Pago en efectivo",                 "activo": True},
    {"codigo": "PAYPAL",        "nombre": "PayPal",                  "descripcion": "Cobro a una cuenta PayPal",        "activo": True},
    {"codigo": "BIZUM",         "nombre": "Bizum",                   "descripcion": "Cobro mediante Bizum al teléfono", "activo": True},
]


async def seed():
    async with async_session() as session:
        try:
            print("\n--- Estados de miembro ---")
            for data in ESTADOS_MIEMBRO:
                existing = (await session.execute(
                    select(EstadoMiembro).where(EstadoMiembro.nombre == data["nombre"])
                )).scalar_one_or_none()
                if not existing:
                    session.add(EstadoMiembro(id=uuid.uuid4(), **data))
                    print(f"  + {data['nombre']}")
                else:
                    print(f"  = {data['nombre']} (ya existe)")

            print("\n--- Tipos de miembro ---")
            for data in TIPOS_MIEMBRO:
                existing = (await session.execute(
                    select(TipoMiembro).where(TipoMiembro.nombre == data["nombre"])
                )).scalar_one_or_none()
                if not existing:
                    session.add(TipoMiembro(id=uuid.uuid4(), **data))
                    print(f"  + {data['nombre']}")
                else:
                    print(f"  = {data['nombre']} (ya existe)")

            print("\n--- Formas de pago ---")
            for data in FORMAS_PAGO:
                existing = (await session.execute(
                    select(FormaPago).where(FormaPago.codigo == data["codigo"])
                )).scalar_one_or_none()
                if not existing:
                    session.add(FormaPago(id=uuid.uuid4(), **data))
                    print(f"  + {data['nombre']}")
                else:
                    print(f"  = {data['nombre']} (ya existe)")

            await session.commit()
            print("\n[OK] Catálogos de miembros inicializados.")

        except Exception:
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed())
