"""
Script maestro INTERACTIVO para ejecutar la importación completa.

Permite seleccionar qué scripts ejecutar paso a paso.

USO:
    python -m app.scripts.importacion.ejecutar_importacion_interactiva

IMPORTANTE:
- Antes de ejecutar, asegúrate de tener configurados los MYSQL_CONFIG en cada script
- Este proceso puede tomar varios minutos dependiendo del volumen de datos
- Se recomienda hacer un backup de PostgreSQL antes de ejecutar
"""
import asyncio
import sys
from datetime import datetime


def preguntar_si_ejecutar(nombre: str, descripcion: str) -> bool:
    """Pregunta al usuario si desea ejecutar un paso."""

    print("\n" + "="*80)
    print(f"PASO: {nombre}")
    print("-"*80)
    print(f"{descripcion}")
    print("="*80)

    while True:
        respuesta = input("\n?Ejecutar este paso? (s/n/q para salir): ").strip().lower()

        if respuesta == 'q':
            print("\n[!]  Importación cancelada por el usuario")
            sys.exit(0)
        elif respuesta == 's':
            return True
        elif respuesta == 'n':
            print("  [-] Paso omitido")
            return False
        else:
            print("  Por favor responde 's' (sí), 'n' (no) o 'q' (salir)")


async def ejecutar_script(nombre: str, modulo: str):
    """Ejecuta un script de importación."""

    print("\n" + "-"*80)
    print(f"EJECUTANDO: {nombre}")
    print("-"*80)
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        # Importar y ejecutar el módulo
        mod = __import__(modulo, fromlist=['main'])
        await mod.main()

        print(f"\n[OK] {nombre} completado exitosamente")
        return True

    except Exception as e:
        print(f"\n[X] ERROR en {nombre}: {e}")
        import traceback
        traceback.print_exc()

        # Preguntar si continuar o detener
        print("\n" + "="*80)
        while True:
            respuesta = input("?Continuar con los siguientes pasos? (s/n): ").strip().lower()
            if respuesta == 'n':
                return False
            elif respuesta == 's':
                print("  ⚠ Continuando a pesar del error...")
                return True
            else:
                print("  Por favor responde 's' (sí) o 'n' (no)")


async def main():
    """Ejecuta la importación completa de forma interactiva."""

    print("\n" + "="*80)
    print("IMPORTACION COMPLETA DE DATOS MYSQL -> POSTGRESQL")
    print("MODO INTERACTIVO")
    print("="*80)
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("\nEn cada paso puedes elegir:")
    print("  - 's' para ejecutar el paso")
    print("  - 'n' para omitir el paso")
    print("  - 'q' para salir del proceso")
    print("\n" + "="*80)

    inicio = datetime.now()

    scripts = [
        {
            "nombre": "1. Crear catálogos base",
            "descripcion": "Crea tipos de miembro, estados de miembro, estados de cuota,\nestados de campaña, estados de actividad y estados de participante.\n\nREQUERIDO: Este paso es OBLIGATORIO antes de cualquier importación.",
            "modulo": "app.scripts.importacion.1_crear_catalogos_base"
        },
        {
            "nombre": "2. Importar datos geográficos",
            "descripcion": "Importa países y provincias desde MySQL.\nCrea tabla temporal temp_id_mapping para mapeo de IDs.\n\nREQUERIDO: Necesario para relacionar miembros y agrupaciones.",
            "modulo": "app.scripts.importacion.2_importar_geografico"
        },
        {
            "nombre": "3. Importar agrupaciones territoriales",
            "descripcion": "Importa agrupaciones territoriales con encriptación de IBANs.\nConsolida tablas AGRUPACIONTERRITORIAL y _estatal_y_internacional.\n\nREQUERIDO: Necesario para relacionar miembros y cuotas.",
            "modulo": "app.scripts.importacion.3_importar_agrupaciones"
        },
        {
            "nombre": "4. Importar miembros",
            "descripcion": "Importa miembros con TODA la lógica de mapeo:\n  - Encriptación de DNI/NIE e IBANs\n  - Priorización de teléfonos (móvil > fijo_casa > fijo_trabajo)\n  - Inferencia de provincia por código postal\n  - Inferencia de agrupación por última cuota\n  - Detección de voluntarios\n  - Manejo de bajas y fallecidos\n\nADVERTENCIA: Este es el script más complejo y puede tardar varios minutos.",
            "modulo": "app.scripts.importacion.4_importar_miembros"
        },
        {
            "nombre": "5. Importar importes de cuota",
            "descripcion": "Importa importes de cuota por año y tipo de miembro.\nGenera registros para cada combinación (ejercicio, tipo_miembro).\n\nREQUERIDO: Necesario para relacionar cuotas anuales.",
            "modulo": "app.scripts.importacion.5_importar_importes_cuota"
        },
        {
            "nombre": "6. Importar cuotas anuales",
            "descripcion": "Importa cuotas anuales de miembros.\nCalcula estados basados en importes y fechas.\nMapea modos de ingreso (SEPA, TRANSFERENCIA, etc.).\n\nADVERTENCIA: Puede tardar varios minutos con grandes volúmenes.",
            "modulo": "app.scripts.importacion.6_importar_cuotas_anuales"
        },
        {
            "nombre": "7. Importar datos financieros complementarios",
            "descripcion": "Importa:\n  - Conceptos de donación\n  - Donaciones\n  - Remesas SEPA\n  - Órdenes de cobro (consolida tablas históricas)\n\nOPCIONAL: Puedes omitir si solo necesitas miembros y cuotas.",
            "modulo": "app.scripts.importacion.7_importar_financiero_complementario"
        },
        {
            "nombre": "8. Validar importación",
            "descripcion": "Valida la integridad de la importación:\n  - Compara totales MySQL vs PostgreSQL\n  - Verifica integridad referencial\n  - Detecta datos huérfanos\n  - Valida lógica de negocio\n\nRECOMENDADO: Siempre ejecutar al final para verificar.",
            "modulo": "app.scripts.importacion.8_validar_importacion"
        }
    ]

    resultados = []

    for script_info in scripts:
        nombre = script_info["nombre"]
        descripcion = script_info["descripcion"]
        modulo = script_info["modulo"]

        # Preguntar si ejecutar
        ejecutar = preguntar_si_ejecutar(nombre, descripcion)

        if not ejecutar:
            resultados.append((nombre, None))  # None = omitido
            continue

        # Ejecutar script
        exito = await ejecutar_script(nombre, modulo)
        resultados.append((nombre, exito))

        if not exito:
            print("\n" + "="*80)
            print("[!]  PROCESO DETENIDO")
            print("="*80)
            break

    fin = datetime.now()
    duracion = fin - inicio

    print("\n" + "="*80)
    print("RESUMEN DE IMPORTACIÓN")
    print("="*80 + "\n")

    print("Scripts ejecutados:")
    for nombre, resultado in resultados:
        if resultado is None:
            estado = "[-]"
            texto = "OMITIDO"
        elif resultado:
            estado = "[OK]"
            texto = "EXITOSO"
        else:
            estado = "[X]"
            texto = "ERROR"

        print(f"  {estado} {nombre} - {texto}")

    print(f"\nDuración total: {duracion}")
    print(f"Finalizado: {fin.strftime('%Y-%m-%d %H:%M:%S')}")

    exitosos = sum(1 for _, r in resultados if r is True)
    errores = sum(1 for _, r in resultados if r is False)
    omitidos = sum(1 for _, r in resultados if r is None)

    if errores > 0:
        print(f"\n[ERROR] IMPORTACIÓN COMPLETADA CON {errores} ERRORES")
    elif exitosos > 0:
        print(f"\n[SUCCESS] IMPORTACIÓN EXITOSA - {exitosos} pasos completados")
    else:
        print(f"\n[-] NO SE EJECUTÓ NINGÚN PASO - {omitidos} pasos omitidos")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[!]  Importación interrumpida por el usuario")
        sys.exit(1)
