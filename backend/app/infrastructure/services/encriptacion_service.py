"""Servicio de encriptación para datos sensibles usando Fernet (cryptography)."""

import os
import base64
import json
import re
import logging
from typing import Optional, Dict, Any

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class EncriptacionService:
    """Servicio para encriptar y desencriptar datos sensibles."""

    def __init__(self):
        self._fernet = None
        self._initialize_cipher()

    def _initialize_cipher(self) -> None:
        """Inicializa el cipher con la clave del entorno."""
        key = os.getenv('ENCRYPTION_KEY') or os.getenv('FERNET_KEY')
        if not key:
            # Generar clave temporal para desarrollo
            logger.warning("No se encontró ENCRYPTION_KEY, generando clave temporal")
            key = Fernet.generate_key().decode()

        self._fernet = Fernet(key.encode() if isinstance(key, str) else key)

    def encriptar_texto(self, texto: str) -> str:
        """Encripta un texto plano."""
        if not texto:
            return ""

        try:
            texto_bytes = texto.encode('utf-8')
            encriptado = self._fernet.encrypt(texto_bytes)
            return base64.urlsafe_b64encode(encriptado).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encriptando texto: {e}")
            raise

    def desencriptar_texto(self, texto_encriptado: str) -> str:
        """Desencripta un texto."""
        if not texto_encriptado:
            return ""

        try:
            encriptado_bytes = base64.urlsafe_b64decode(texto_encriptado.encode('utf-8'))
            desencriptado = self._fernet.decrypt(encriptado_bytes)
            return desencriptado.decode('utf-8')
        except Exception as e:
            logger.error(f"Error desencriptando texto: {e}")
            raise

    def encriptar_json(self, datos: Dict[str, Any]) -> str:
        """Encripta un diccionario JSON."""
        if not datos:
            return ""

        try:
            json_str = json.dumps(datos, ensure_ascii=False)
            return self.encriptar_texto(json_str)
        except Exception as e:
            logger.error(f"Error encriptando JSON: {e}")
            raise

    def desencriptar_json(self, texto_encriptado: str) -> Dict[str, Any]:
        """Desencripta y convierte a diccionario."""
        if not texto_encriptado:
            return {}

        try:
            json_str = self.desencriptar_texto(texto_encriptado)
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error desencriptando JSON: {e}")
            return {}

    def encriptar_iban(self, iban: str) -> str:
        """Encripta específicamente un IBAN."""
        # Formatear y validar IBAN antes de encriptar
        iban_limpio = self._limpiar_iban(iban)
        return self.encriptar_texto(iban_limpio)

    def desencriptar_iban(self, iban_encriptado: str) -> str:
        """Desencripta un IBAN."""
        iban = self.desencriptar_texto(iban_encriptado)
        return self._formatear_iban(iban)

    def _limpiar_iban(self, iban: str) -> str:
        """Limpia y valida formato IBAN."""
        if not iban:
            return ""

        # Eliminar espacios y convertir a mayúsculas
        iban_limpio = iban.replace(" ", "").upper()

        # Validar longitud mínima (ES: 24 caracteres)
        if len(iban_limpio) < 20:
            raise ValueError("IBAN demasiado corto")

        return iban_limpio

    def _formatear_iban(self, iban: str) -> str:
        """Formatea IBAN para visualización (bloques de 4)."""
        if not iban:
            return ""

        # Agrupar en bloques de 4 caracteres
        iban_limpio = iban.replace(" ", "")
        bloques = [iban_limpio[i:i+4] for i in range(0, len(iban_limpio), 4)]
        return " ".join(bloques)

    def encriptar_dni(self, dni: str) -> str:
        """Encripta un DNI/NIE."""
        dni_limpio = self._limpiar_dni(dni)
        return self.encriptar_texto(dni_limpio)

    def desencriptar_dni(self, dni_encriptado: str) -> str:
        """Desencripta un DNI/NIE."""
        return self.desencriptar_texto(dni_encriptado)

    def _limpiar_dni(self, dni: str) -> str:
        """Limpia y valida formato DNI/NIE."""
        if not dni:
            return ""

        # Eliminar espacios y convertir a mayúsculas
        dni_limpio = dni.replace(" ", "").upper()

        # Validar formato básico
        if len(dni_limpio) < 8:
            raise ValueError("DNI/NIE demasiado corto")

        return dni_limpio

    def generar_clave_segura(self) -> str:
        """Genera una clave de encriptación segura."""
        return Fernet.generate_key().decode('utf-8')

    def rotar_clave(self, nueva_clave: str) -> None:
        """Rota la clave de encriptación."""
        try:
            self._fernet = Fernet(nueva_clave.encode())
            logger.info("Clave de encriptación rotada exitosamente")
        except Exception as e:
            logger.error(f"Error rotando clave: {e}")
            raise


# Singleton global
_encriptacion_service = None


def get_encriptacion_service() -> EncriptacionService:
    """Factory para obtener el servicio de encriptación (singleton)."""
    global _encriptacion_service
    if _encriptacion_service is None:
        _encriptacion_service = EncriptacionService()
    return _encriptacion_service
