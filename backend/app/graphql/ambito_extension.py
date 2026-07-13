"""Filtrado territorial de LECTURA para los campos generados por strawchemy.

El motor territorial (`RequireTransaction(..., objetivo=…)`) cierra la **escritura**: no
puedes dar de baja a un socio de otro territorio. Pero la lectura seguía abierta: los
campos de strawchemy (`contactos`, `actividades`, …) generan su propio SQL y no pasan por
ningún resolver nuestro, así que devolvían el padrón **entero** de la organización. Una
coordinadora local no podía tocar a un socio de otra agrupación… pero los veía a todos.

`FiltrarPorAmbito` envuelve el resolver del campo y descarta las filas que caen fuera del
ámbito del usuario. Se declara junto al campo:

    contactos: list[ContactoType] = campo(
        filter_input=ContactoFilter, extensions=[FiltrarPorAmbito()],
    )

Es un filtro **post-consulta**: strawchemy trae las filas y aquí se recortan. No es lo más
eficiente —lo ideal sería inyectar el WHERE en el SQL— pero es lo que la librería permite
sin reescribir su generación de queries, y el filtrado en cliente ya es el patrón del
proyecto (las queries de strawchemy no aceptan `limit`/`offset`).
"""

from __future__ import annotations

from typing import Any

from strawberry.extensions import FieldExtension


class FiltrarPorAmbito(FieldExtension):
    """Recorta el resultado de un campo al ámbito territorial del usuario.

    `atributo` es el campo por el que la fila declara su territorio. Si una fila no lo
    tiene, **se descarta**: falla cerrado, porque un `None` permisivo convertiría el
    olvido de una columna en una fuga del padrón.

    Ámbito `None` = global (superadmin) → pasa todo sin tocar.
    """

    def __init__(self, atributo: str = "agrupacion_id") -> None:
        self.atributo = atributo

    async def resolve_async(self, next_, source: Any, info, **kwargs: Any) -> Any:
        resultado = await next_(source, info, **kwargs)

        ambito = await info.context.get_ambito()
        if ambito is None:
            return resultado
        if not isinstance(resultado, list):
            # Campo de un solo objeto: se deja pasar o se anula.
            if resultado is None:
                return None
            return resultado if getattr(resultado, self.atributo, None) in ambito else None

        return [
            fila for fila in resultado
            if getattr(fila, self.atributo, None) in ambito
        ]
