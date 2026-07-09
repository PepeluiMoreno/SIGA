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


# --- IBAN (ISO 13616) -------------------------------------------------------

# Longitud del IBAN por país (los más comunes en el ámbito SEPA/EEE). Si el país
# no está en la tabla se valida solo estructura + dígito de control.
_IBAN_LONGITUDES = {
    "ES": 24, "PT": 25, "FR": 27, "IT": 27, "DE": 22, "GB": 22, "NL": 18,
    "BE": 16, "IE": 22, "LU": 20, "AT": 20, "FI": 18, "AD": 24, "MC": 27,
    "CH": 21, "PL": 28, "SE": 24, "DK": 18, "NO": 15, "GR": 27,
}


def normalizar_iban(iban: str | None) -> str:
    """Mayúsculas y sin espacios, guiones ni puntos."""
    return re.sub(r"[\s\-.]", "", (iban or "")).upper()


def validar_iban(iban: str | None) -> bool:
    """True si el IBAN es válido: estructura, longitud por país (si se conoce) y
    dígito de control ISO 13616 (mod-97 == 1)."""
    n = normalizar_iban(iban)
    if not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{10,30}", n):
        return False
    esperada = _IBAN_LONGITUDES.get(n[:2])
    if esperada is not None and len(n) != esperada:
        return False
    # Mueve los 4 primeros caracteres al final y convierte letras (A=10 … Z=35).
    reordenado = n[4:] + n[:4]
    convertido = "".join(str(int(ch, 36)) for ch in reordenado)
    return int(convertido) % 97 == 1
