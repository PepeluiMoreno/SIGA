"""Mockeo de datos personales de los socios (privacidad del entorno dev/demo).

NO borra ni crea miembros — mantiene los registros y todas sus relaciones.
Sobre cada miembro (salvo el del usuario propietario) sustituye los datos
identificativos por valores ficticios:
  - apellido1, apellido2, numero_documento (DNI válido)
  - email y teléfonos (para que el entorno nunca contacte a personas reales)
El nombre de pila se conserva (poco identificativo por sí solo).

Además simula el ciclo RGPD: marca un subconjunto como "solicita supresión" y,
de esos, anonimiza una parte (datos_anonimizados = true).

Idempotente: re-ejecutarlo vuelve a mockear.

Uso:
  docker exec siga_dev_backend python -m app.scripts.seeding.seed_mock_socios
"""
import asyncio
import random
import unicodedata
from datetime import date, timedelta

from sqlalchemy import select

from app.core.database import async_session
from app.modules.membresia.models.miembro import Miembro

# Email del miembro propietario que se conserva intacto.
EMAIL_PROPIETARIO = "morgomez"

APELLIDOS = [
    "García", "Rodríguez", "González", "Fernández", "López", "Martínez",
    "Sánchez", "Pérez", "Gómez", "Martín", "Jiménez", "Ruiz", "Hernández",
    "Díaz", "Moreno", "Muñoz", "Álvarez", "Romero", "Alonso", "Gutiérrez",
    "Navarro", "Torres", "Domínguez", "Vázquez", "Ramos", "Gil", "Ramírez",
    "Serrano", "Blanco", "Suárez", "Molina", "Morales", "Ortega", "Delgado",
    "Castro", "Ortiz", "Rubio", "Marín", "Sanz", "Iglesias", "Núñez", "Medina",
    "Garrido", "Cortés", "Castillo", "Santos", "Lozano", "Guerrero", "Cano",
    "Prieto", "Méndez", "Cruz", "Calvo", "Gallego", "Vidal", "León", "Herrera",
    "Peña", "Flores", "Cabrera", "Campos", "Vega", "Fuentes", "Carrasco",
    "Caballero", "Reyes", "Nieto", "Aguilar", "Pascual", "Santana", "Herrero",
]

LETRAS_DNI = "TRWAGMYFPDXBNJZSQVHLCKE"

TIPOS_VIA = ["Calle", "Avenida", "Plaza", "Paseo", "Camino", "Ronda", "Travesía"]
VIAS = [
    "Mayor", "Real", "Nueva", "del Sol", "de la Constitución", "del Carmen",
    "de la Paz", "San Juan", "de la Iglesia", "del Río", "de las Flores",
    "de la Estación", "Larga", "del Parque", "de Andalucía", "Cervantes",
    "Goya", "del Pilar", "de la Fuente", "de la Alameda", "Colón", "Triana",
    "de Extremadura", "del Mar", "de la Libertad", "de Aragón", "Velázquez",
]
LOCALIDADES = [
    "Villanueva del Río", "San Fernando", "La Puebla", "Los Barrios",
    "Villaverde", "Santa María", "El Ejido", "Torrelavega", "Alcalá",
    "Mairena", "Dos Hermanas", "Móstoles", "Getafe", "Alcobendas",
    "Aranjuez", "Manzanares", "Ribadeo", "Calatayud", "Antequera",
    "Mérida", "Ponferrada", "Vélez", "Utrera", "Carmona", "Estepona",
]


def quitar_acentos(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)
    )


def gen_dni(usados: set) -> str:
    while True:
        n = random.randint(10_000_000, 99_999_999)
        dni = f"{n}{LETRAS_DNI[n % 23]}"
        if dni not in usados:
            usados.add(dni)
            return dni


def gen_telefono() -> str:
    return random.choice("67") + "".join(random.choices("0123456789", k=8))


async def seed():
    async with async_session() as session:
        miembros = list((await session.execute(select(Miembro))).scalars().all())

        # Conjunto de DNIs ya presentes para no colisionar con el UNIQUE.
        usados_dni = {m.numero_documento for m in miembros if m.numero_documento}

        objetivo = [
            m for m in miembros
            if not (m.email and EMAIL_PROPIETARIO in m.email.lower())
        ]
        random.seed(20260520)  # reproducible

        for i, m in enumerate(objetivo):
            ap1 = random.choice(APELLIDOS)
            ap2 = random.choice(APELLIDOS)
            # Liberar el DNI viejo del set y asignar uno nuevo único.
            if m.numero_documento in usados_dni:
                usados_dni.discard(m.numero_documento)
            m.apellido1 = ap1
            m.apellido2 = ap2
            m.numero_documento = gen_dni(usados_dni)
            nom = quitar_acentos((m.nombre or "socio").split()[0]).lower()
            m.email = f"{nom}.{quitar_acentos(ap1).lower()}{i}@ejemplo.test"
            m.telefono = gen_telefono()
            if m.telefono2:
                m.telefono2 = gen_telefono()
            # Dirección postal ficticia (la provincia se conserva por coherencia
            # con la agrupación territorial del socio).
            m.direccion = (
                f"{random.choice(TIPOS_VIA)} {random.choice(VIAS)}, "
                f"{random.randint(1, 180)}"
            )
            m.codigo_postal = f"{random.randint(1, 52):02d}{random.randint(0, 999):03d}"
            m.localidad = random.choice(LOCALIDADES)

        # ── Simulación del ciclo RGPD ────────────────────────────────────────
        # ~6% solicita supresión; de esos, ~55% acaba anonimizado.
        candidatos = list(objetivo)
        random.shuffle(candidatos)
        n_solicita = max(1, round(len(candidatos) * 0.06))
        solicitan = candidatos[:n_solicita]
        hoy = date.today()

        n_anon = 0
        for j, m in enumerate(solicitan):
            m.solicita_supresion_datos = True
            m.fecha_solicitud_supresion = hoy - timedelta(days=random.randint(5, 600))
            if j % 100 < 55:  # ~55% de los que solicitan -> anonimizados
                m.nombre = "Anonimizado"
                m.apellido1 = "Anonimizado"
                m.apellido2 = None
                m.numero_documento = None
                m.fecha_nacimiento = None
                m.sexo = None
                m.tipo_documento = None
                m.direccion = None
                m.codigo_postal = None
                m.localidad = None
                m.telefono = None
                m.telefono2 = None
                m.email = None
                m.iban = None
                m.swift_bic = None
                m.referencia_pago = None
                m.foto_url = None
                m.observaciones = None
                m.observaciones_voluntariado = None
                m.datos_anonimizados = True
                m.fecha_anonimizacion = m.fecha_solicitud_supresion + timedelta(
                    days=random.randint(1, 30)
                )
                n_anon += 1

        await session.commit()
        print(
            f"✓ Mock socios: {len(objetivo)} miembros con datos ficticios "
            f"(propietario conservado). RGPD simulado: {n_solicita} solicitan "
            f"supresión, {n_anon} anonimizados."
        )


if __name__ == "__main__":
    asyncio.run(seed())
