"""Orquestador de poblado DEMO para staging (sin volcado MySQL).

Ejecuta, en orden de dependencias y de forma idempotente, todos los seeds
*autónomos* que dejan un entorno listo para pruebas: catálogos, estructura
territorial, roles/permisos, miembros, cuentas de acceso, cuotas, campañas y
actividades. NO ejecuta los seeds que dependen del volcado MySQL (esos solo
sirven para reproducir los datos reales en desarrollo).

Requisito previo: el backend ya arrancó al menos una vez (bootstrap crea
catálogos base, roles funcionales, SUPERADMIN + admin inicial y comunicación).

Ejecutar:
  docker compose -f docker-compose.dev.yml --env-file .env.dev exec backend \\
      python -m app.scripts.seeding.seed_demo_staging
"""
from __future__ import annotations

import subprocess
import sys

# Orden de ejecución. Cada entrada es (módulo, critico):
#   critico=True  → si falla, el poblado SE DETIENE (los pasos siguientes dependen
#                   de él; seguir dejaría la BD a medias). Es el grueso: catálogos,
#                   roles, estructura, perfiles, cuotas.
#   critico=False → su fallo se anota pero NO bloquea (pasos "de adorno" cuyo fallo
#                   no invalida lo demás: campañas, actividades, permisos por rol).
# El orden respeta las dependencias reales (ver mapa lee→crea): catálogos →
# roles → estructura → perfiles/cuotas → campañas/actividades → permisos.
PASOS = [
    # ── Catálogos contables / económicos ──
    ("plan_cuentas_esfl", True),
    ("descripciones_cuentas", False),       # solo actualiza descripciones de #1
    # ── Catálogos de dominio (prerrequisito de casi todo lo demás) ──
    ("seed_catalogos_miembros", True),
    ("seed_tipos_vinculacion", True),       # crea SOCIO → lo necesita seed_staging_perfiles
    ("seed_catalogos_accion", True),        # crea los UUIDs que usa seed_actividades_permanentes
    ("seed_catalogos_campania", True),
    ("seed_eventos_catalogos", True),
    ("seed_habilidades", True),
    # ── Roles organizativos (los funcionales y permisos base van en bootstrap) ──
    ("seed_roles_organizacionales", True),  # crea PRESIDENTE/TESORERO/… → los necesita perfiles
    # ── Estructura territorial + miembros + juntas + nombramientos (demo) ──
    ("seed_demo_europalaica", True),        # crea geografía/estructura/miembros
    # ── Cuentas de acceso por perfil (demo) — un usuario por perfil, contraseña «x» ──
    ("seed_staging_perfiles", True),        # depende de roles + SOCIO + estructura
    # ── Plan de cuotas + cuotas del ejercicio (demo) ──
    ("seed_demo_cuotas", False),            # depende de miembros; degrada si faltan
    # ── Campañas y actividades (demo) ──
    ("seed_campanias_europalaica", False),
    ("seed_actividades_permanentes", False),
    # ── Permisos por rol (idempotentes; su fallo no rompe el resto) ──
    ("seed_permisos_membresia_perfilado", False),
    ("seed_permisos_contactos", False),
    ("seed_permisos_voluntariado", False),
    ("seed_permisos_cuotas", False),
    ("seed_permisos_tesorero", False),
    ("seed_permisos_justificantes", False),
    ("seed_permisos_recibos", False),
    ("seed_permisos_donaciones", False),
    ("seed_permisos_ccaa", False),
    ("seed_permisos_cierre", False),
    ("seed_permisos_conciliacion", False),
    ("seed_permisos_modelo_182", False),
    ("seed_permisos_plan_cuentas", False),
    ("seed_permisos_export_socios", False),
]


def main() -> int:
    from app.scripts.seeding._guard import abort_if_production
    abort_if_production("poblado demo para staging")
    print("=" * 64)
    print("POBLADO DEMO PARA STAGING")
    print("=" * 64)
    fallos = []
    for i, (mod, critico) in enumerate(PASOS, 1):
        etiqueta = "crítico" if critico else "opcional"
        print(f"\n[{i}/{len(PASOS)}] {mod} ({etiqueta})")
        r = subprocess.run([sys.executable, "-m", f"app.scripts.seeding.{mod}"])
        if r.returncode != 0:
            if critico:
                print("\n" + "=" * 64)
                print(f"DETENIDO: el paso CRÍTICO '{mod}' falló (código {r.returncode}).")
                print("Los pasos siguientes dependen de él; abortar evita dejar la BD")
                print("a medias. Corrige la causa y vuelve a ejecutar (es idempotente).")
                print("=" * 64)
                return 2
            print(f"  ⚠ '{mod}' (opcional) terminó con código {r.returncode} (continúo)")
            fallos.append(mod)

    print("\n" + "=" * 64)
    if fallos:
        print(f"Completado, con {len(fallos)} paso(s) opcional(es) con incidencias: {', '.join(fallos)}")
        print("El núcleo (catálogos/roles/estructura/perfiles) se aplicó correctamente.")
    else:
        print("Poblado demo completado sin incidencias.")
    print("=" * 64)
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
