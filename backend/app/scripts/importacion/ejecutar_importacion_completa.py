"""
Script maestro para ejecutar la importación completa.

Ejecuta todos los scripts de importación en el orden correcto:
1. Crear catálogos base
2. Importar datos geográficos
3. Importar agrupaciones territoriales
4. Importar miembros
5. Importar importes de cuota
6. Importar cuotas anuales
7. Importar datos financieros complementarios
8. Validar importación

USO:
    python -m app.scripts.importacion.ejecutar_importacion_completa

IMPORTANTE:
- Antes de ejecutar, asegúrate de tener configurados los MYSQL_CONFIG en cada script
- Este proceso puede tomar varios minutos dependiendo del volumen de datos
- Se recomienda hacer un backup de PostgreSQL antes de ejecutar
"""
import asyncio
import sys
from datetime import datetime


async def ejecutar_script(nombre: str, modulo: str):
    """Ejecuta un script de importación."""

    print("\n" + "="*80)
    print(f"EJECUTANDO: {nombre}")
    print("="*80)
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        # Importar y ejecutar el módulo
        mod = __import__(modulo, fromlist=['main'])
        await mod.main()

        print(f"\n✓ {nombre} completado exitosamente")
        return True

    except Exception as e:
        print(f"\n✗ ERROR en {nombre}: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Ejecuta la importación completa."""

    print("\n" + "="*80)
    print("IMPORTACIÓN COMPLETA DE DATOS MYSQL → POSTGRESQL")
    print("="*80)
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    inicio = datetime.now()

    scripts = [
        ("1. Crear catálogos base", "app.scripts.importacion.1_crear_catalogos_base"),
        ("2. Importar datos geográficos", "app.scripts.importacion.2_importar_geografico"),
        ("3. Importar agrupaciones territoriales", "app.scripts.importacion.3_importar_agrupaciones"),
        ("4. Importar miembros", "app.scripts.importacion.4_importar_miembros"),
        ("5. Importar importes de cuota", "app.scripts.importacion.5_importar_importes_cuota"),
        ("6. Importar cuotas anuales", "app.scripts.importacion.6_importar_cuotas_anuales"),
        ("7. Importar datos financieros complementarios", "app.scripts.importacion.7_importar_financiero_complementario"),
        ("8. Validar importación", "app.scripts.importacion.8_validar_importacion")
    ]

    resultados = []

    for nombre, modulo in scripts:
        exito = await ejecutar_script(nombre, modulo)
        resultados.append((nombre, exito))

        if not exito:
            print("\n" + "="*80)
            print("⚠️  IMPORTACIÓN DETENIDA POR ERROR")
            print("="*80)
            print(f"\nFalló en: {nombre}")
            print("\nRevisar los errores anteriores y corregir antes de continuar.")
            sys.exit(1)

    fin = datetime.now()
    duracion = fin - inicio

    print("\n" + "="*80)
    print("RESUMEN DE IMPORTACIÓN")
    print("="*80 + "\n")

    print("Scripts ejecutados:")
    for nombre, exito in resultados:
        estado = "✓" if exito else "✗"
        print(f"  {estado} {nombre}")

    print(f"\nDuración total: {duracion}")
    print(f"Finalizado: {fin.strftime('%Y-%m-%d %H:%M:%S')}")

    todos_exitosos = all(exito for _, exito in resultados)

    if todos_exitosos:
        print("\n✅ IMPORTACIÓN COMPLETA EXITOSA")
    else:
        print("\n❌ IMPORTACIÓN COMPLETADA CON ERRORES")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Importación interrumpida por el usuario")
        sys.exit(1)
