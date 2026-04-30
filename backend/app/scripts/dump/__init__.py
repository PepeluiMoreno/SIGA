"""
Scripts de volcado de datos desde MySQL a PostgreSQL.

Estos scripts están diseñados para conectarse directamente a MySQL y migrar
datos a PostgreSQL. Asumen disponibilidad del servidor MySQL legacy.

Orden de ejecución:
1. 1_crear_catalogos_base.py - Crear catálogos básicos (tipos, estados)
2. 2_importar_geografico.py - Países, provincias, municipios
3. 3_importar_agrupaciones.py - Agrupaciones territoriales con jerarquía
4. 4_importar_miembros.py - Miembros (miembros) con encriptación de datos
5. 5_importar_importes_cuota.py - Catálogo de importes de cuota
6. 6_importar_cuotas_anuales.py - Historial de cuotas anuales
7. 7_importar_financiero.py - Donaciones, remesas, órdenes de cobro
8. 8_validar_importacion.py - Validación de integridad

Requisitos:
- MySQL accesible (configurar en .env: MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
- PostgreSQL configurado y con esquema actualizado
- aiomysql instalado: pip install aiomysql
"""
