"""Validación y normalización de documentos de identidad españoles (NIF/DNI/NIE).

Se usa para desduplicar personas físicas por su NIF (p. ej. firmantes de una
recogida de firmas). No cubre CIF (personas jurídicas) ni pasaporte: para la
identidad de una persona física la clave estable es el DNI/NIE.
"""
from __future__ import annotations

import re

_LETRAS = "TRWAGMYFPDXBNJZSQVHLCKE"
_NIE_PREFIJO = {"X": "0", "Y": "1", "Z": "2"}


def normalizar_documento(numero: str | None) -> str:
    """Mayúsculas y sin espacios, guiones ni puntos."""
    return re.sub(r"[\s\-.]", "", (numero or "")).upper()


def es_dni_valido(numero: str) -> bool:
    m = re.fullmatch(r"(\d{8})([A-Z])", numero)
    if not m:
        return False
    return _LETRAS[int(m.group(1)) % 23] == m.group(2)


def es_nie_valido(numero: str) -> bool:
    m = re.fullmatch(r"([XYZ])(\d{7})([A-Z])", numero)
    if not m:
        return False
    base = _NIE_PREFIJO[m.group(1)] + m.group(2)
    return _LETRAS[int(base) % 23] == m.group(3)


def validar_nif(numero: str | None) -> bool:
    """True si es un DNI o NIE válido (con letra de control correcta)."""
    n = normalizar_documento(numero)
    return es_dni_valido(n) or es_nie_valido(n)
