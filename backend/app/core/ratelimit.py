"""Limitador de tasa sencillo en memoria (ventana deslizante por clave).

Pensado como segunda barrera tras el captcha en el endpoint público de firmas.

LIMITACIÓN: el estado vive en el proceso. Con varios workers de uvicorn/gunicorn
cada uno lleva su propia cuenta, así que el límite efectivo se multiplica por el
nº de workers. Para un control estricto y compartido, mover a Redis o apoyarse en
la tabla `ips_bloqueadas`/`intentos_acceso`. El captcha sigue siendo la defensa
principal; esto solo amortigua ráfagas.
"""
from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from typing import Deque, Dict


class RateLimiter:
    def __init__(self, max_eventos: int, ventana_seg: float) -> None:
        self.max_eventos = max_eventos
        self.ventana_seg = ventana_seg
        self._eventos: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def permitido(self, clave: str) -> bool:
        """Registra un intento para `clave` y devuelve si está dentro del límite."""
        ahora = time.monotonic()
        corte = ahora - self.ventana_seg
        with self._lock:
            cola = self._eventos[clave]
            while cola and cola[0] < corte:
                cola.popleft()
            if len(cola) >= self.max_eventos:
                return False
            cola.append(ahora)
            # Limpieza oportunista para no acumular claves muertas.
            if len(self._eventos) > 10_000:
                self._purgar(corte)
            return True

    def _purgar(self, corte: float) -> None:
        muertas = [k for k, c in self._eventos.items() if not c or c[-1] < corte]
        for k in muertas:
            self._eventos.pop(k, None)


# Límites para la ingesta pública de firmas.
# Por IP: 10 envíos / 10 min. Por email: 5 / hora (evita machacar a una persona).
limiter_firmas_ip = RateLimiter(max_eventos=10, ventana_seg=600)
limiter_firmas_email = RateLimiter(max_eventos=5, ventana_seg=3600)
