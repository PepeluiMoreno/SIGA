"""Seeding de miembros ficticios para desarrollo."""

import asyncio
from datetime import date
from sqlalchemy import select

from app.core.database import async_session
from app.models import Miembro, TipoMiembro, EstadoMiembro
from app.domains.geografico.models.direccion import AgrupacionTerritorial


# Miembros ficticios para desarrollo.
# agrupacion_corto: nombre_corto de AgrupacionTerritorial (EL/AND/ARA/etc.)
# tipo_miembro:     nombre de TipoMiembro (Miembro/Simpatizante/Honorífico)
# estado:           nombre de EstadoMiembro (Activo/Baja/...)
# apellido1 puede ser "" para personas jurídicas (el modelo lo requiere NOT NULL)
MIEMBROS_FICTICIOS = [
    {
        "nombre": "María",
        "apellido1": "García",
        "apellido2": "López",
        "sexo": "M",
        "email": "maria.garcia@email.com",
        "telefono": "612 345 678",
        "agrupacion_corto": "MAD",
        "tipo_miembro": "Miembro",
        "estado": "Activo",
        "direccion": "Calle Mayor 15, 3º B",
        "codigo_postal": "28013",
        "localidad": "Madrid",
        "fecha_alta": date(2023, 1, 15),
    },
    {
        "nombre": "Juan",
        "apellido1": "Martínez",
        "apellido2": "Ruiz",
        "sexo": "H",
        "email": "juan.martinez@email.com",
        "telefono": "623 456 789",
        "agrupacion_corto": "EL",
        "tipo_miembro": "Miembro",
        "estado": "Activo",
        "direccion": "Avda. de la Constitución 42",
        "codigo_postal": "28001",
        "localidad": "Madrid",
        "fecha_alta": date(2022, 6, 20),
    },
    {
        "nombre": "Ana",
        "apellido1": "López",
        "apellido2": "Fernández",
        "sexo": "M",
        "email": "ana.lopez@email.com",
        "telefono": None,
        "agrupacion_corto": "CAT",
        "tipo_miembro": "Simpatizante",
        "estado": "Activo",
        "direccion": "Carrer de Pau Claris 108",
        "codigo_postal": "08009",
        "localidad": "Barcelona",
        "fecha_alta": date(2024, 2, 10),
    },
    {
        "nombre": "Carlos",
        "apellido1": "Sánchez",
        "apellido2": "Vega",
        "sexo": "H",
        "email": "carlos.sanchez@email.com",
        "telefono": "634 567 890",
        "agrupacion_corto": "VAL",
        "tipo_miembro": "Miembro",
        "estado": "Activo",
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
        "sexo": "M",
        "email": "laura.diaz@email.com",
        "telefono": "645 678 901",
        "agrupacion_corto": "AND",
        "tipo_miembro": "Miembro",
        "estado": "Baja",
        "direccion": "Calle Sierpes 45",
        "codigo_postal": "41004",
        "localidad": "Sevilla",
        "fecha_alta": date(2021, 11, 30),
        "fecha_baja": date(2024, 6, 15),
        "activo": False,
    },
    {
        "nombre": "Pedro",
        "apellido1": "Hernández",
        "apellido2": "Gil",
        "sexo": "H",
        "email": "pedro.hernandez@email.com",
        "telefono": "656 789 012",
        "agrupacion_corto": "MAD",
        "tipo_miembro": "Miembro",
        "estado": "Activo",
        "direccion": "Paseo de la Castellana 120",
        "codigo_postal": "28046",
        "localidad": "Madrid",
        "fecha_alta": date(2024, 1, 8),
    },
    {
        "nombre": "Elena",
        "apellido1": "Torres",
        "apellido2": "Blanco",
        "sexo": "M",
        "email": "elena.torres@email.com",
        "telefono": "667 890 123",
        "agrupacion_corto": "GAL",
        "tipo_miembro": "Simpatizante",
        "estado": "Activo",
        "direccion": "Rúa do Franco 25",
        "codigo_postal": "15702",
        "localidad": "Santiago de Compostela",
        "fecha_alta": date(2023, 7, 22),
    },
    {
        "nombre": "Roberto",
        "apellido1": "Díaz",
        "apellido2": "Campos",
        "sexo": "H",
        "email": "roberto.diaz@email.com",
        "telefono": "678 901 234",
        "agrupacion_corto": "ARA",
        "tipo_miembro": "Miembro",
        "estado": "Activo",
        "es_voluntario": True,
        "disponibilidad": "TARDES",
        "direccion": "Paseo Independencia 10",
        "codigo_postal": "50001",
        "localidad": "Zaragoza",
        "fecha_alta": date(2024, 3, 15),
    },
    {
        "nombre": "Asociación Ateneo Libre de Valencia",
        "apellido1": "",
        "apellido2": None,
        "email": "ateneo.libre.vlc@email.com",
        "telefono": "963 123 456",
        "agrupacion_corto": "VAL",
        "tipo_miembro": "Miembro",
        "estado": "Activo",
        "tipo_documento": "CIF",
        "numero_documento": "G12345678",
        "direccion": "Plaza del Ayuntamiento 5",
        "codigo_postal": "46002",
        "localidad": "Valencia",
        "fecha_alta": date(2020, 3, 1),
    },
    {
        "nombre": "Fundación Laicismo y Democracia",
        "apellido1": "",
        "apellido2": None,
        "email": "fundacion.laicismo@email.com",
        "telefono": "912 345 678",
        "agrupacion_corto": "EL",
        "tipo_miembro": "Miembro",
        "estado": "Activo",
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
        for raw in MIEMBROS_FICTICIOS:
            data = dict(raw)
            agrupacion_corto = data.pop("agrupacion_corto")
            tipo_nombre = data.pop("tipo_miembro")
            estado_nombre = data.pop("estado")

            # Comprobar si ya existe por email
            result = await db.execute(select(Miembro).where(Miembro.email == data["email"]))
            if result.scalar_one_or_none():
                print(f"  = Miembro ya existe: {data['nombre']}")
                continue

            # Resolver agrupación por nombre_corto
            agrup = (await db.execute(
                select(AgrupacionTerritorial).where(AgrupacionTerritorial.nombre_corto == agrupacion_corto)
            )).scalar_one_or_none()
            if not agrup:
                print(f"  ! Agrupación '{agrupacion_corto}' no encontrada para {data['nombre']} — omitido")
                continue

            # Resolver tipo de miembro por nombre
            tipo = (await db.execute(
                select(TipoMiembro).where(TipoMiembro.nombre == tipo_nombre)
            )).scalar_one_or_none()
            if not tipo:
                print(f"  ! TipoMiembro '{tipo_nombre}' no encontrado para {data['nombre']} — omitido")
                continue

            # Resolver estado por nombre
            estado = (await db.execute(
                select(EstadoMiembro).where(EstadoMiembro.nombre == estado_nombre)
            )).scalar_one_or_none()
            if not estado:
                print(f"  ! EstadoMiembro '{estado_nombre}' no encontrado para {data['nombre']} — omitido")
                continue

            miembro = Miembro(
                **data,
                agrupacion_id=agrup.id,
                tipo_miembro_id=tipo.id,
                estado_id=estado.id,
            )
            db.add(miembro)
            print(f"  + Miembro: {data['nombre']}")

        await db.commit()
        print("Miembros ficticios completados.")


if __name__ == "__main__":
    asyncio.run(seed_miembros())
