"""Lectura de secretos conforme al Estándar de Ingeniería (CI/CD, Secretos y
Despliegue).

Patrón normativo: el código lee toda credencial sensible con el patrón
``<VAR>_FILE`` (Docker secret montado como fichero en ``/run/secrets``) y cae a
la variable de entorno ``<VAR>`` solo por compatibilidad de desarrollo.

En desarrollo (optiplex-790) basta el fallback a env var; en staging/producción
las credenciales se entregan como Docker secret y ``<VAR>_FILE`` apunta al
fichero, de modo que nunca quedan visibles en ``docker inspect`` ni en Portainer.
"""
from __future__ import annotations

import os


def read_secret_file(var: str) -> str | None:
    """Devuelve el contenido de ``<VAR>_FILE`` si apunta a un fichero legible.

    Retorna ``None`` si no hay ``<VAR>_FILE`` o el fichero no existe, para que el
    llamante pueda decidir el fallback.
    """
    path = os.environ.get(f"{var}_FILE")
    if path and os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read().rstrip("\r\n")
    return None


def read_secret_env(var: str, default: str = "") -> str:
    """Lee ``<VAR>_FILE`` (Docker secret) y cae a ``<VAR>`` (env) por compatibilidad."""
    file_value = read_secret_file(var)
    if file_value is not None:
        return file_value
    return os.environ.get(var, default)
