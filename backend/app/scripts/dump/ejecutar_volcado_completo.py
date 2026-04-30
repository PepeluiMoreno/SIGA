#!/usr/bin/env python
"""
Script principal para ejecutar el volcado completo de MySQL a PostgreSQL.

Este script ejecuta todos los scripts de importación en orden.
Requiere conexión a MySQL legacy y PostgreSQL destino.

Configuración necesaria en .env:
- MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
- DATABASE_URL para PostgreSQL

Uso:
    python -m app.scripts.dump.ejecutar_volcado_completo
    python -m app.scripts.dump.ejecutar_volcado_completo --desde 4
    python -m app.scripts.dump.ejecutar_volcado_completo --solo 7
"""
import asyncio
import sys
import argparse
from datetime import datetime

# Scripts en orden de ejecución
SCRIPTS = [
    ("1_crear_catalogos_base", "Crear catálogos base (tipos, estados)"),
    ("2_importar_geografico", "Importar datos geográficos (países, provincias)"),
    ("3_importar_agrupaciones", "Importar agrupaciones territoriales"),
    ("3b_establecer_jerarquia", "Establecer jerarquía de agrupaciones"),
    ("4_importar_miembros", "Importar miembros (miembros)"),
    ("5_importar_importes_cuota", "Importar catálogo de importes de cuota"),
    ("6_importar_cuotas_anuales", "Importar historial de cuotas anuales"),
    ("7_importar_financiero", "Importar datos financieros (donaciones, remesas)"),
    ("8_validar_importacion", "Validar integridad de importación"),
]


async def ejecutar_script(nombre_modulo: str, descripcion: str) -> bool:
    """Ejecuta un script de importación."""
    print(f"\n{'='*80}")
    print(f"EJECUTANDO: {descripcion}")
    print(f"Módulo: {nombre_modulo}")
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    try:
        # Importar y ejecutar el módulo
        modulo = __import__(f"app.scripts.dump.{nombre_modulo}", fromlist=["main"])
        await modulo.main()
        print(f"\n[OK] {descripcion} completado")
        return True
    except Exception as e:
        print(f"\n[ERROR] {descripcion} falló: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Ejecutar volcado de MySQL a PostgreSQL")
    parser.add_argument("--desde", type=int, default=1, help="Número de script desde el cual comenzar (1-8)")
    parser.add_argument("--hasta", type=int, default=8, help="Número de script hasta el cual ejecutar (1-8)")
    parser.add_argument("--solo", type=int, help="Ejecutar solo un script específico (1-8)")
    args = parser.parse_args()

    print("\n" + "="*80)
    print("VOLCADO COMPLETO MySQL → PostgreSQL")
    print("="*80)
    print(f"\nInicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Determinar qué scripts ejecutar
    if args.solo:
        desde = args.solo
        hasta = args.solo
    else:
        desde = args.desde
        hasta = args.hasta

    # Validar rango
    if desde < 1 or hasta > len(SCRIPTS) or desde > hasta:
        print(f"[ERROR] Rango inválido. Use valores entre 1 y {len(SCRIPTS)}")
        sys.exit(1)

    print(f"\nScripts a ejecutar: {desde} - {hasta}")
    print("\nLista de scripts:")
    for i, (nombre, desc) in enumerate(SCRIPTS, 1):
        marca = ">>>" if desde <= i <= hasta else "   "
        print(f"  {marca} {i}. {desc}")

    # Confirmar
    print("\n" + "-"*80)
    print("Presiona ENTER para continuar o Ctrl+C para cancelar...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nOperación cancelada.")
        sys.exit(0)

    # Ejecutar scripts
    resultados = []
    for i, (nombre, desc) in enumerate(SCRIPTS, 1):
        if desde <= i <= hasta:
            exito = await ejecutar_script(nombre, desc)
            resultados.append((i, nombre, desc, exito))

            if not exito:
                print(f"\n[ADVERTENCIA] Script {i} falló. ¿Continuar? (s/N)")
                try:
                    resp = input().strip().lower()
                    if resp != 's':
                        print("Volcado interrumpido.")
                        break
                except KeyboardInterrupt:
                    print("\nVoldado interrumpido.")
                    break

    # Resumen final
    print("\n" + "="*80)
    print("RESUMEN DEL VOLCADO")
    print("="*80)
    print(f"\nFin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nResultados:")
    for i, nombre, desc, exito in resultados:
        estado = "[OK]" if exito else "[FALLO]"
        print(f"  {i}. {estado} {desc}")

    # Estadísticas
    exitosos = sum(1 for _, _, _, e in resultados if e)
    fallidos = sum(1 for _, _, _, e in resultados if not e)
    print(f"\nTotal: {len(resultados)} scripts ejecutados")
    print(f"  Exitosos: {exitosos}")
    print(f"  Fallidos: {fallidos}")

    if fallidos > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
