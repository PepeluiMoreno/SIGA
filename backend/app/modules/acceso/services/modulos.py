"""Registro de MÓDULOS y FUNCIONALIDADES de la aplicación y su estado (on/off).

Fuente de verdad ÚNICA de qué está encendido. El apagado tiene DOS granularidades:

  - MÓDULO: enciende/apaga un módulo entero (todas sus funcionalidades).
  - FUNCIONALIDAD: override fino sobre una funcionalidad concreta, que puede quedar
    ON aunque su módulo esté OFF (p.ej. "Aprobación de socios" con Secretaría OFF) o
    OFF aunque su módulo esté ON (p.ej. las funcionalidades económicas dentro de
    Membresía/Actividades cuando Económico está fuera del MVP).

Efecto (las 3 capas lo consultan a través de la columna `activa` de cada transacción,
que el CatalogSyncService fija según esto, y de la PermissionMatrix que la respeta):
  - Backend: la matrix ignora las transacciones inactivas → check_permission deniega.
  - Menú/rutas (frontend): `mis_transacciones` filtra por `activa`; el menú se apaga.
  - Configuración: query `modulos` / `funcionalidades` expone el estado (solo lectura).

De momento el estado se edita aquí, en código (solo lectura desde UI). Más adelante
podrá vivir en BD y togglearse desde Configuración por el superadmin.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModuloDef:
    """Un módulo de la aplicación y su estado."""
    codigo: str            # coincide con la constante MODULO del catalog.py
    nombre: str            # etiqueta legible para la UI
    activo: bool
    sistema: bool = False  # transversal: no se puede apagar (Configuración, Acceso)


# Orden = orden de aparición en la UI. `sistema=True` ⇒ siempre activo, no apagable.
MODULOS: tuple[ModuloDef, ...] = (
    # ── Transversales (siempre activos) ──────────────────────────────────────
    ModuloDef("acceso",          "Control de Acceso",    activo=True,  sistema=True),
    ModuloDef("configuracion",   "Configuración",        activo=True,  sistema=True),
    # ── MVP: encendidos ──────────────────────────────────────────────────────
    ModuloDef("membresia",       "Membresía",            activo=True),
    ModuloDef("contactos",       "Contactos (CRM)",      activo=True),
    ModuloDef("actividades",     "Actividades",          activo=True),
    # ── MVP: apagados ────────────────────────────────────────────────────────
    ModuloDef("economico",       "Económico",            activo=False),
    ModuloDef("secretaria",      "Secretaría",           activo=False),
    ModuloDef("presidencia",     "Presidencia",          activo=False),
    ModuloDef("proteccion_datos", "Protección de Datos", activo=False),
)

_POR_CODIGO = {m.codigo: m for m in MODULOS}

# Overrides por FUNCIONALIDAD (código de FuncionalidadDef → activa). Solo se listan
# las que se desvían del estado de su módulo:
#   - True  con módulo OFF ⇒ funcionalidad encendida pese a su módulo apagado.
#   - False con módulo ON  ⇒ funcionalidad apagada pese a su módulo encendido.
# Si una funcionalidad no aparece aquí, hereda el estado de su módulo.
FUNCIONALIDADES_OVERRIDE: dict[str, bool] = {
    # Secretaría OFF, pero la aprobación de socios entra al MVP:
    "APROBACION_SOCIOS": True,
    # Económico fuera del MVP: sus funcionalidades quedan OFF aunque vivan en
    # módulos encendidos (Membresía / Actividades).
    "DATOS_ECONOMICOS_MIEMBRO": False,     # membresia (ON) — IBAN/cuota del socio
    "FLUJO_PRESUPUESTO_CAMPANA": False,    # actividades (ON) — presupuesto de campaña
}


def modulo_activo(codigo: str | None) -> bool:
    """True si el módulo está activo (o es desconocido → se asume activo por seguridad
    de no romper transacciones sin módulo declarado)."""
    if codigo is None:
        return True
    m = _POR_CODIGO.get(codigo)
    return m.activo if m is not None else True


def funcionalidad_activa(codigo_funcionalidad: str, modulo: str | None) -> bool:
    """Estado efectivo de una funcionalidad: su override si lo tiene; si no, su módulo."""
    if codigo_funcionalidad in FUNCIONALIDADES_OVERRIDE:
        return FUNCIONALIDADES_OVERRIDE[codigo_funcionalidad]
    return modulo_activo(modulo)


def transaccion_activa_por_funcionalidades(
    modulo: str | None,
    funcionalidades: list[tuple[str, str | None]],
) -> bool:
    """Estado de una transacción a partir de sus funcionalidades y su módulo.

    `funcionalidades` = lista de (codigo_funcionalidad, modulo_de_esa_funcionalidad)
    a las que pertenece la transacción.

    Regla: una transacción está ACTIVA si está en al menos una funcionalidad activa.
    Si NO pertenece a ninguna funcionalidad, hereda el estado de su propio módulo
    (fallback para transacciones sueltas no agrupadas en funcionalidad).
    """
    if funcionalidades:
        return any(funcionalidad_activa(cod, mod) for (cod, mod) in funcionalidades)
    return modulo_activo(modulo)


def modulos_estado() -> list[ModuloDef]:
    """Lista de módulos con su estado, para exponer en Configuración (solo lectura)."""
    return list(MODULOS)
