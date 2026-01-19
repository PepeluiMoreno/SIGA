"""Servicio de seguridad y protección contra ataques."""

import re
import hashlib
import ipaddress
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .cache_service import get_cache_service, generar_cache_key
from .configuracion_service import ConfiguracionService

logger = logging.getLogger(__name__)


class SeguridadService:
    """Servicio de seguridad para proteger contra ataques y gestionar intentos fallidos."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.cache = get_cache_service()
        self.config = ConfiguracionService(session)

    async def registrar_intento_login(self, identificador: str, ip_address: str,
                                      exitoso: bool = False, usuario_id: Optional[str] = None) -> Dict[str, Any]:
        """Registra un intento de login."""
        try:
            key_intentos = generar_cache_key("intentos_login", identificador)
            key_ip = generar_cache_key("intentos_ip", ip_address)

            # Obtener configuración
            max_intentos = await self.config.get_int('MAX_INTENTOS_LOGIN', 5)
            tiempo_bloqueo = await self.config.get_int('TIEMPO_BLOQUEO_MINUTOS', 30)

            if exitoso:
                # Limpiar intentos fallidos si el login fue exitoso
                self.cache.delete(key_intentos)
                self.cache.delete(key_ip)

                # Actualizar último acceso del usuario
                if usuario_id:
                    from ...domains.usuarios.models.usuario import Usuario

                    result = await self.session.execute(
                        select(Usuario).where(Usuario.id == usuario_id)
                    )
                    usuario = result.scalar_one_or_none()

                    if usuario:
                        usuario.ultimo_acceso = datetime.utcnow()
                        usuario.intentos_login = 0
                        usuario.bloqueado_hasta = None
                        await self.session.commit()

                return {
                    'exitoso': True,
                    'intentos_restantes': max_intentos,
                    'bloqueado': False
                }

            else:
                # Incrementar contadores de intentos fallidos
                intentos_identificador = self.cache.increment(key_intentos)
                intentos_ip = self.cache.increment(key_ip)

                # Establecer TTL en los contadores
                if intentos_identificador == 1:
                    self.cache.set(key_intentos, 1, 3600)  # 1 hora
                if intentos_ip == 1:
                    self.cache.set(key_ip, 1, 3600)  # 1 hora

                # Verificar si se excedió el límite
                bloqueado = intentos_identificador >= max_intentos

                if bloqueado:
                    # Bloquear la IP también
                    self._bloquear_ip(ip_address, tiempo_bloqueo)

                    # Si hay usuario, bloquearlo en la BD
                    if usuario_id:
                        from ...domains.usuarios.models.usuario import Usuario

                        result = await self.session.execute(
                            select(Usuario).where(Usuario.id == usuario_id)
                        )
                        usuario = result.scalar_one_or_none()

                        if usuario:
                            usuario.bloqueado_hasta = datetime.utcnow() + timedelta(minutes=tiempo_bloqueo)
                            await self.session.commit()

                intentos_restantes = max(0, max_intentos - intentos_identificador)

                return {
                    'exitoso': False,
                    'intentos_restantes': intentos_restantes,
                    'bloqueado': bloqueado,
                    'tiempo_bloqueo_minutos': tiempo_bloqueo if bloqueado else 0
                }

        except Exception as e:
            logger.error(f"Error registrando intento de login: {e}")
            return {
                'exitoso': exitoso,
                'intentos_restantes': 0,
                'bloqueado': False,
                'error': str(e)
            }

    async def verificar_bloqueo_login(self, identificador: str, ip_address: str) -> Dict[str, Any]:
        """Verifica si un usuario o IP está bloqueado."""
        try:
            key_intentos = generar_cache_key("intentos_login", identificador)
            key_ip_bloqueada = generar_cache_key("ip_bloqueada", ip_address)

            # Verificar bloqueo de IP
            if self.cache.exists(key_ip_bloqueada):
                ttl = self.cache.get_ttl(key_ip_bloqueada)
                return {
                    'bloqueado': True,
                    'razon': 'IP_BLOQUEADA',
                    'tiempo_restante_segundos': ttl,
                    'mensaje': f'Esta IP está bloqueada temporalmente. Intente nuevamente en {ttl} segundos.'
                }

            # Verificar bloqueo de usuario
            intentos = self.cache.get(key_intentos, 0)
            max_intentos = await self.config.get_int('MAX_INTENTOS_LOGIN', 5)

            if intentos >= max_intentos:
                return {
                    'bloqueado': True,
                    'razon': 'USUARIO_BLOQUEADO',
                    'intentos_fallidos': intentos,
                    'mensaje': 'Usuario bloqueado por demasiados intentos fallidos.'
                }

            return {
                'bloqueado': False,
                'intentos_fallidos': intentos,
                'intentos_restantes': max_intentos - intentos
            }

        except Exception as e:
            logger.error(f"Error verificando bloqueo: {e}")
            return {
                'bloqueado': False,
                'error': str(e)
            }

    def _bloquear_ip(self, ip_address: str, minutos: int):
        """Bloquea una IP temporalmente."""
        key = generar_cache_key("ip_bloqueada", ip_address)
        self.cache.set(key, True, minutos * 60)
        logger.warning(f"IP bloqueada: {ip_address} por {minutos} minutos")

    async def registrar_cambio_contrasena(self, usuario_id: str, ip_address: str) -> bool:
        """Registra un cambio de contraseña exitoso."""
        try:
            key = generar_cache_key("cambio_contrasena", usuario_id)
            self.cache.set(key, {
                'fecha': datetime.utcnow().isoformat(),
                'ip': ip_address
            }, 86400)  # 24 horas

            return True

        except Exception as e:
            logger.error(f"Error registrando cambio de contraseña: {e}")
            return False

    async def verificar_cambio_contrasena_reciente(self, usuario_id: str,
                                                   horas_minimas: int = 24) -> Dict[str, Any]:
        """Verifica si se cambió la contraseña recientemente."""
        try:
            key = generar_cache_key("cambio_contrasena", usuario_id)
            cambio = self.cache.get(key)

            if cambio:
                fecha_cambio = datetime.fromisoformat(cambio['fecha'])
                tiempo_transcurrido = datetime.utcnow() - fecha_cambio

                if tiempo_transcurrido < timedelta(hours=horas_minimas):
                    return {
                        'cambiada_recientemente': True,
                        'tiempo_transcurrido_horas': tiempo_transcurrido.total_seconds() / 3600,
                        'tiempo_restante_horas': horas_minimas - (tiempo_transcurrido.total_seconds() / 3600),
                        'ip_cambio': cambio['ip']
                    }

            return {
                'cambiada_recientemente': False,
                'tiempo_transcurrido_horas': None,
                'tiempo_restante_horas': 0,
                'ip_cambio': None
            }

        except Exception as e:
            logger.error(f"Error verificando cambio de contraseña: {e}")
            return {
                'cambiada_recientemente': False,
                'error': str(e)
            }

    async def validar_fortaleza_contrasena(self, contrasena: str) -> Dict[str, Any]:
        """Valida la fortaleza de una contraseña."""
        try:
            longitud_minima = await self.config.get_int('CONTRASENA_LONGITUD_MINIMA', 8)
            requiere_mayusculas = await self.config.get_bool('CONTRASENA_REQUIERE_MAYUSCULAS', True)
            requiere_minusculas = await self.config.get_bool('CONTRASENA_REQUIERE_MINUSCULAS', True)
            requiere_numeros = await self.config.get_bool('CONTRASENA_REQUIERE_NUMEROS', True)
            requiere_especiales = await self.config.get_bool('CONTRASENA_REQUIERE_ESPECIALES', False)

            errores = []
            puntuacion = 0

            # Longitud
            if len(contrasena) < longitud_minima:
                errores.append(f"Debe tener al menos {longitud_minima} caracteres")
            else:
                puntuacion += 2

            if len(contrasena) >= 12:
                puntuacion += 2

            # Mayúsculas
            if requiere_mayusculas and not any(c.isupper() for c in contrasena):
                errores.append("Debe contener al menos una mayúscula")
            elif any(c.isupper() for c in contrasena):
                puntuacion += 1

            # Minúsculas
            if requiere_minusculas and not any(c.islower() for c in contrasena):
                errores.append("Debe contener al menos una minúscula")
            elif any(c.islower() for c in contrasena):
                puntuacion += 1

            # Números
            if requiere_numeros and not any(c.isdigit() for c in contrasena):
                errores.append("Debe contener al menos un número")
            elif any(c.isdigit() for c in contrasena):
                puntuacion += 1

            # Caracteres especiales
            especiales = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if requiere_especiales and not any(c in especiales for c in contrasena):
                errores.append("Debe contener al menos un carácter especial")
            elif any(c in especiales for c in contrasena):
                puntuacion += 2

            # Verificar contraseñas comunes
            contrasenas_comunes = ['123456', 'password', 'qwerty', 'admin', 'letmein']
            if contrasena.lower() in contrasenas_comunes:
                errores.append("No puede ser una contraseña común")
                puntuacion -= 3

            # Determinar nivel de fortaleza
            if puntuacion >= 8:
                fortaleza = 'FUERTE'
            elif puntuacion >= 5:
                fortaleza = 'MEDIA'
            else:
                fortaleza = 'DÉBIL'

            return {
                'valida': len(errores) == 0,
                'fortaleza': fortaleza,
                'puntuacion': puntuacion,
                'errores': errores,
                'longitud': len(contrasena)
            }

        except Exception as e:
            logger.error(f"Error validando fortaleza de contraseña: {e}")
            return {
                'valida': False,
                'fortaleza': 'ERROR',
                'puntuacion': 0,
                'errores': [str(e)],
                'longitud': len(contrasena)
            }

    async def verificar_ip_confiable(self, ip_address: str) -> bool:
        """Verifica si una IP está en la lista de IPs confiables."""
        try:
            # Obtener lista de IPs confiables desde configuración
            ips_confiables = await self.config.get_list('IPS_CONFIABLES', [])

            if not ips_confiables:
                return False

            ip = ipaddress.ip_address(ip_address)

            for ip_confiable in ips_confiables:
                try:
                    if '/' in ip_confiable:
                        # Es un rango CIDR
                        red = ipaddress.ip_network(ip_confiable, strict=False)
                        if ip in red:
                            return True
                    else:
                        # Es una IP individual
                        if ip == ipaddress.ip_address(ip_confiable):
                            return True
                except ValueError:
                    continue

            return False

        except Exception as e:
            logger.error(f"Error verificando IP confiable: {e}")
            return False

    async def registrar_intento_sesion(self, session_id: str, usuario_id: str,
                                       ip_address: str, user_agent: str) -> bool:
        """Registra información de sesión para auditoría."""
        try:
            key = generar_cache_key("sesion_info", session_id)

            datos_sesion = {
                'usuario_id': usuario_id,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'fecha_creacion': datetime.utcnow().isoformat(),
                'ultima_actividad': datetime.utcnow().isoformat()
            }

            # TTL de 24 horas
            self.cache.set(key, datos_sesion, 86400)

            return True

        except Exception as e:
            logger.error(f"Error registrando información de sesión: {e}")
            return False

    def actualizar_actividad_sesion(self, session_id: str) -> bool:
        """Actualiza la última actividad de una sesión."""
        try:
            key = generar_cache_key("sesion_info", session_id)
            datos_sesion = self.cache.get(key)

            if datos_sesion:
                datos_sesion['ultima_actividad'] = datetime.utcnow().isoformat()
                self.cache.set(key, datos_sesion, 86400)  # Renovar TTL
                return True

            return False

        except Exception as e:
            logger.error(f"Error actualizando actividad de sesión: {e}")
            return False

    def obtener_info_sesion(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene información de una sesión."""
        try:
            key = generar_cache_key("sesion_info", session_id)
            return self.cache.get(key)

        except Exception as e:
            logger.error(f"Error obteniendo información de sesión: {e}")
            return None

    def generar_hash_sesion(self, usuario_id: str, ip_address: str,
                           user_agent: str, timestamp: datetime) -> str:
        """Genera un hash único para la sesión."""
        data = f"{usuario_id}:{ip_address}:{user_agent}:{timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()

    def limpiar_datos_sensibles(self, texto: str) -> str:
        """Limpia datos sensibles de un texto para logging."""
        # Patrones comunes de datos sensibles
        patrones = [
            (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[TARJETA]'),  # Tarjetas
            (r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}[A-Z0-9]{1,16}\b', '[IBAN]'),  # IBAN
            (r'\b\d{8}[A-Z]\b', '[DNI]'),  # DNI español
            (r'\b[A-Z]\d{7}[A-Z]\b', '[NIE]'),  # NIE español
            (r'\b\d{4}-\d{2}-\d{2}\b', '[FECHA]'),  # Fechas
        ]

        texto_limpio = texto
        for patron, reemplazo in patrones:
            texto_limpio = re.sub(patron, reemplazo, texto_limpio, flags=re.IGNORECASE)

        return texto_limpio


# Funciones helper
def es_ip_interna(ip_address: str) -> bool:
    """Verifica si una IP es interna/privada."""
    try:
        ip = ipaddress.ip_address(ip_address)
        return ip.is_private
    except ValueError:
        return False


def calcular_intensidad_ataque(intentos_por_minuto: int) -> str:
    """Calcula la intensidad de un ataque basado en intentos por minuto."""
    if intentos_por_minuto > 100:
        return 'CRÍTICO'
    elif intentos_por_minuto > 50:
        return 'ALTO'
    elif intentos_por_minuto > 20:
        return 'MEDIO'
    elif intentos_por_minuto > 5:
        return 'BAJO'
    else:
        return 'MÍNIMO'
