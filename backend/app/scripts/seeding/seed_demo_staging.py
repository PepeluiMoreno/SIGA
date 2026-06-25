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

# Orden de ejecución. Cada entrada es un módulo runnable por `python -m`.
PASOS = [
    # ── Catálogos contables / económicos ──
    "plan_cuentas_esfl",
    "descripciones_cuentas",
    # ── Catálogos de dominio ──
    "seed_catalogos_miembros",
    "seed_tipos_vinculacion",
    "seed_catalogos_accion",
    "seed_catalogos_campania",
    "seed_eventos_catalogos",
    "seed_habilidades",
    # ── Roles organizativos (los funcionales y permisos base van en bootstrap) ──
    "seed_roles_organizacionales",
    # ── Estructura territorial + miembros + juntas + nombramientos (demo) ──
    "seed_demo_europalaica",
    # ── Cuentas de acceso por perfil (demo) ──
    "seed_demo_usuarios",
    # ── Plan de cuotas + cuotas del ejercicio (demo) ──
    "seed_demo_cuotas",
    # ── Campañas y actividades (demo) ──
    "seed_campanias_europalaica",
    "seed_actividades_permanentes",
    # ── Permisos por rol (idempotentes) ──
    "seed_permisos_membresia_perfilado",
    "seed_permisos_contactos",
    "seed_permisos_voluntariado",
    "seed_permisos_cuotas",
    "seed_permisos_tesorero",
    "seed_permisos_justificantes",
    "seed_permisos_recibos",
    "seed_permisos_donaciones",
    "seed_permisos_ccaa",
    "seed_permisos_cierre",
    "seed_permisos_conciliacion",
    "seed_permisos_modelo_182",
    "seed_permisos_plan_cuentas",
    "seed_permisos_export_socios",
]


def main() -> int:
    print("=" * 64)
    print("POBLADO DEMO PARA STAGING")
    print("=" * 64)
    fallos = []
    for i, mod in enumerate(PASOS, 1):
        print(f"\n[{i}/{len(PASOS)}] {mod}")
        r = subprocess.run([sys.executable, "-m", f"app.scripts.seeding.{mod}"])
        if r.returncode != 0:
            print(f"  ⚠ '{mod}' terminó con código {r.returncode} (continúo)")
            fallos.append(mod)

    print("\n" + "=" * 64)
    if fallos:
        print(f"Terminado con {len(fallos)} paso(s) con incidencias: {', '.join(fallos)}")
        print("Revisa esos seeds; el resto se aplicó.")
    else:
        print("Poblado demo completado sin incidencias.")
    print("=" * 64)
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
