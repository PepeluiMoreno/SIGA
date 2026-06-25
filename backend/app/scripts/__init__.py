"""Scripts de inicialización y mantenimiento del sistema.

El seeding de datos de referencia en el arranque lo hace **exclusivamente**
`app/scripts/bootstrap.py` (invocado por el CMD del backend tras
`alembic upgrade head`). Este paquete no re-exporta mecanismos de
inicialización alternativos.
"""
