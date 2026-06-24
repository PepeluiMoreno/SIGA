"""MÓDULO OBSOLETO — Organizacion eliminada.

El modelo `Organizacion` quedó obsoleto: tenía sustituta por sus dos caras.
  - Delegación territorial interna (con o sin personalidad jurídica propia)
    → `UnidadOrganizativa` (app.modules.core.geografico.direccion), que es la
      estructura territorial canónica a la que apuntan todas las agrupacion_id.
  - Entidad externa que participa o conviene
    → `Contacto` de tipo PERSONA_JURIDICA (app.modules.membresia.models.contacto),
      tipificada por `TipoEntidadJuridica`.

El catálogo `TipoOrganizacion` se reaprovechó como `TipoEntidadJuridica`.
El `Convenio` que colgaba de aquí se sustituye por el satélite Convenio de
participación (app.modules.secretaria.models.convenio).

Este fichero se mantiene vacío temporalmente para no romper imports legacy
durante la transición; debe eliminarse junto con el módulo `organizaciones`.
"""
