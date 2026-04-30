"""Seeding de miembros ficticios para desarrollo."""

import asyncio
from datetime import date
from sqlalchemy import select

from app.core.database import async_session
from app.models import Miembro, AgrupacionTerritorial, TipoMiembro


# Miembros ficticios para desarrollo
MIEMBROS_FICTICIOS = [
    # Personas físicas con membresía indirecta (a través de agrupaciones territoriales)
    {
        "nombre": "María",
        "apellido1": "García",
        "apellido2": "López",
        "email": "maria.garcia@email.com",
        "telefono": "612 345 678",
        "tipo_persona": "FISICA",
        "tipo_membresia": "INDIRECTA",
        "agrupacion_codigo": "MAD",
        "tipo_miembro_codigo": "miembro",
        "direccion": "Calle Mayor 15, 3º B",
        "codigo_postal": "28013",
        "localidad": "Madrid",
        "fecha_alta": date(2023, 1, 15),
    },
    {
        "nombre": "Juan",
        "apellido1": "Martínez",
        "apellido2": "Ruiz",
        "email": "juan.martinez@email.com",
        "telefono": "623 456 789",
        "tipo_persona": "FISICA",
        "tipo_membresia": "DIRECTA",
        "agrupacion_codigo": "EL",
        "tipo_miembro_codigo": "miembro",
        "direccion": "Avda. de la Constitución 42",
        "codigo_postal": "28001",
        "localidad": "Madrid",
        "fecha_alta": date(2022, 6, 20),
    },
    {
        "nombre": "Ana",
        "apellido1": "López",
        "apellido2": "Fernández",
        "email": "ana.lopez@email.com",
        "telefono": None,
        "tipo_persona": "FISICA",
        "tipo_membresia": "INDIRECTA",
        "agrupacion_codigo": "CAT",
        "tipo_miembro_codigo": "SIMPATIZANTE",
        "direccion": "Carrer de Pau Claris 108",
        "codigo_postal": "08009",
        "localidad": "Barcelona",
        "fecha_alta": date(2024, 2, 10),
    },
    {
        "nombre": "Carlos",
        "apellido1": "Sánchez",
        "apellido2": "Vega",
        "email": "carlos.sanchez@email.com",
        "telefono": "634 567 890",
        "tipo_persona": "FISICA",
        "tipo_membresia": "INDIRECTA",
        "agrupacion_codigo": "VAL",
        "tipo_miembro_codigo": "miembro",
        "es_voluntario": True,
        "disponibilidad": "FINES_SEMANA",
        "direccion": "Calle Colón 22",
        "codigo_postal": "46004",
        "localidad": "Valencia",
        "fecha_alta": date(2023, 9, 5),
    },
    {
        "nombre": "Laura",
        "apellido1": "Díaz",
        "apellido2": "Moreno",
        "email": "laura.diaz@email.com",
        "telefono": "645 678 901",
        "tipo_persona": "FISICA",
        "tipo_membresia": "INDIRECTA",
        "agrupacion_codigo": "AND",
        "tipo_miembro_codigo": "miembro",
        "direccion": "Calle Sierpes 45",
        "codigo_postal": "41004",
        "localidad": "Sevilla",
        "fecha_alta": date(2021, 11, 30),
        "fecha_baja": date(2024, 6, 15),
    },
    {
        "nombre": "Pedro",
        "apellido1": "Hernández",
        "apellido2": "Gil",
        "email": "pedro.hernandez@email.com",
        "telefono": "656 789 012",
        "tipo_persona": "FISICA",
        "tipo_membresia": "INDIRECTA",
        "agrupacion_codigo": "MAD",
        "tipo_miembro_codigo": "miembro",
        "direccion": "Paseo de la Castellana 120",
        "codigo_postal": "28046",
        "localidad": "Madrid",
        "fecha_alta": date(2024, 1, 8),
    },
    {
        "nombre": "Elena",
        "apellido1": "Torres",
        "apellido2": "Blanco",
        "email": "elena.torres@email.com",
        "telefono": "667 890 123",
        "tipo_persona": "FISICA",
        "tipo_membresia": "INDIRECTA",
        "agrupacion_codigo": "GAL",
        "tipo_miembro_codigo": "SIMPATIZANTE",
        "direccion": "Rúa do Franco 25",
        "codigo_postal": "15702",
        "localidad": "Santiago de Compostela",
        "fecha_alta": date(2023, 7, 22),
    },
    {
        "nombre": "Roberto",
        "apellido1": "Díaz",
        "apellido2": "Campos",
        "email": "roberto.diaz@email.com",
        "telefono": "678 901 234",
        "tipo_persona": "FISICA",
        "tipo_membresia": "INDIRECTA",
        "agrupacion_codigo": "ARA",
        "tipo_miembro_codigo": "miembro",
        "es_voluntario": True,
        "disponibilidad": "TARDES",
        "direccion": "Paseo Independencia 10",
        "codigo_postal": "50001",
        "localidad": "Zaragoza",
        "fecha_alta": date(2024, 3, 15),
    },
    # Personas jurídicas (asociaciones)
    {
        "nombre": "Asociación Ateneo Libre de Valencia",
        "apellido1": None,
        "apellido2": None,
        "email": "ateneo.libre.vlc@email.com",
        "telefono": "963 123 456",
        "tipo_persona": "JURIDICA",
        "tipo_membresia": "INDIRECTA",
        "agrupacion_codigo": "VAL",
        "tipo_miembro_codigo": "miembro",
        "tipo_documento": "CIF",
        "numero_documento": "G12345678",
        "direccion": "Plaza del Ayuntamiento 5",
        "codigo_postal": "46002",
        "localidad": "Valencia",
        "fecha_alta": date(2020, 3, 1),
    },
    {
        "nombre": "Fundación Laicismo y Democracia",
        "apellido1": None,
        "apellido2": None,
        "email": "fundacion.laicismo@email.com",
        "telefono": "912 345 678",
        "tipo_persona": "JURIDICA",
        "tipo_membresia": "DIRECTA",
        "agrupacion_codigo": "EL",
        "tipo_miembro_codigo": "miembro",
        "tipo_documento": "CIF",
        "numero_documento": "G87654321",
        "direccion": "Calle Gran Vía 30",
        "codigo_postal": "28013",
        "localidad": "Madrid",
        "fecha_alta": date(2019, 1, 15),
    },
]


async def seed_miembros():
    async with async_session() as db:
        for miembro_data in MIEMBROS_FICTICIOS:
            # Buscar si ya existe por email
            result = await db.execute(
                select(Miembro).where(Miembro.email == miembro_data["email"])
            )
            if result.scalar_one_or_none():
                print(f"  = Miembro ya existe: {miembro_data['nombre']}")
                continue

            # Obtener agrupación por código
            agrup_result = await db.execute(
                select(AgrupacionTerritorial).where(
                    AgrupacionTerritorial.codigo == miembro_data.pop("agrupacion_codigo")
                )
            )
            agrupacion = agrup_result.scalar_one_or_none()

            # Obtener tipo de miembro por código
            tipo_result = await db.execute(
                select(TipoMiembro).where(
                    TipoMiembro.codigo == miembro_data.pop("tipo_miembro_codigo")
                )
            )
            tipo_miembro = tipo_result.scalar_one_or_none()

            if not agrupacion or not tipo_miembro:
                print(f"  ! Error: Agrupación o tipo de miembro no encontrado para {miembro_data['nombre']}")
                continue

            miembro = Miembro(
                **miembro_data,
                agrupacion_id=agrupacion.id,
                tipo_miembro_id=tipo_miembro.id,
            )
            db.add(miembro)
            print(f"  + Miembro: {miembro_data['nombre']}")

        await db.commit()
        print("Miembros ficticios completados.")


if __name__ == "__main__":
    asyncio.run(seed_miembros())
