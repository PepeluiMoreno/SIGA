"""Módulo transversal de Protección de Datos (RGPD / LOPDGDD).

Cubre las 6 fases del plan en `docs/modulo_rgpd.md`:

1. Catálogos base: encargados del tratamiento, RAT (art. 30).
2. Retención y bloqueo: plazos por tipo de dato, purga diferida.
3. Derechos ARSULIPO: SolicitudDerechoRGPD con plazo 1 mes.
4. Consentimientos versionados + cláusulas informativas (art. 13/14).
5. Brechas de seguridad + asistente de notificación AEPD 72 h.
6. Auditoría de accesos a datos personales.

`catalog.py` se carga desde `main.py` al startup (igual que los demás
módulos), no aquí, para evitar import circular con `core.security`.
"""

from .models import (
    EncargadoTratamiento,
    ActividadTratamiento,
    ActividadTratamientoEncargado,
    ClausulaInformativa,
    Consentimiento,
    SolicitudDerechoRGPD,
    BrechaSeguridad,
    AuditoriaAccesoDatos,
)

__all__ = [
    'EncargadoTratamiento',
    'ActividadTratamiento',
    'ActividadTratamientoEncargado',
    'ClausulaInformativa',
    'Consentimiento',
    'SolicitudDerechoRGPD',
    'BrechaSeguridad',
    'AuditoriaAccesoDatos',
]
