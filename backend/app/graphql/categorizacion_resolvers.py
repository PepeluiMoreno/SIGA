"""Resolvers GraphQL para reglas de categorización y clasificación de apuntes."""

import uuid
from typing import List, Optional

import strawberry

from app.graphql.permissions import RequireTransaction
from app.modules.economico.services.regla_categorizacion_service import ReglaCategorizacionService
from app.modules.economico.services.categorizacion_service import CategorizacionService
from app.modules.economico.models.contabilidad import TipoCoincidencia


@strawberry.type
class ReglaCategorizacionDetailType:
    id: uuid.UUID
    patron: str
    tipo_coincidencia: str
    tipo_apunte: Optional[str]
    categoria_fiscal_id: uuid.UUID
    orden: int
    descripcion: Optional[str]
    activa: bool

    @staticmethod
    def from_model(m) -> "ReglaCategorizacionDetailType":
        return ReglaCategorizacionDetailType(
            id=m.id,
            patron=m.patron,
            tipo_coincidencia=m.tipo_coincidencia.value if hasattr(m.tipo_coincidencia, "value") else m.tipo_coincidencia,
            tipo_apunte=m.tipo_apunte,
            categoria_fiscal_id=m.categoria_fiscal_id,
            orden=m.orden,
            descripcion=m.descripcion,
            activa=m.activa,
        )


@strawberry.input
class CrearReglaCategorizacionInput:
    patron: str
    categoria_fiscal_id: uuid.UUID
    tipo_coincidencia: str = "CONTIENE"
    tipo_apunte: Optional[str] = None
    orden: int = 10
    descripcion: Optional[str] = None


@strawberry.input
class ActualizarReglaCategorizacionInput:
    id: uuid.UUID
    patron: Optional[str] = None
    categoria_fiscal_id: Optional[uuid.UUID] = None
    tipo_coincidencia: Optional[str] = None
    tipo_apunte: Optional[str] = None
    orden: Optional[int] = None
    descripcion: Optional[str] = None
    activa: Optional[bool] = None


@strawberry.type
class ResultadoClasificacionType:
    procesados: int
    clasificados: int


@strawberry.type
class CategorizacionQuery:

    @strawberry.field(permission_classes=[RequireTransaction("ECO_ESTRUCTURA_CONTABLE_LISTAR")])
    async def reglas_categorizacion(
        self, info: strawberry.Info, activas_solo: bool = False
    ) -> List[ReglaCategorizacionDetailType]:
        service = ReglaCategorizacionService(info.context.session)
        items = await service.listar(activas_solo=activas_solo)
        return [ReglaCategorizacionDetailType.from_model(r) for r in items]

    @strawberry.field(permission_classes=[RequireTransaction("ECO_ESTRUCTURA_CONTABLE_LISTAR")])
    async def apuntes_sin_clasificar(
        self, info: strawberry.Info, ejercicio: Optional[int] = None
    ) -> int:
        service = CategorizacionService(info.context.session)
        return await service.contar_sin_clasificar(ejercicio=ejercicio)


@strawberry.type
class CategorizacionMutation:

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_ESTRUCTURA_CONTABLE_GESTIONAR")])
    async def crear_regla_categorizacion(
        self, info: strawberry.Info, data: CrearReglaCategorizacionInput
    ) -> ReglaCategorizacionDetailType:
        service = ReglaCategorizacionService(info.context.session)
        regla = await service.crear(
            patron=data.patron,
            categoria_fiscal_id=data.categoria_fiscal_id,
            tipo_coincidencia=TipoCoincidencia[data.tipo_coincidencia],
            tipo_apunte=data.tipo_apunte,
            orden=data.orden,
            descripcion=data.descripcion,
            creado_por_id=info.context.current_user.id if info.context.current_user else None,
        )
        return ReglaCategorizacionDetailType.from_model(regla)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_ESTRUCTURA_CONTABLE_GESTIONAR")])
    async def actualizar_regla_categorizacion(
        self, info: strawberry.Info, data: ActualizarReglaCategorizacionInput
    ) -> ReglaCategorizacionDetailType:
        service = ReglaCategorizacionService(info.context.session)
        cambios = {}
        if data.patron is not None:
            cambios["patron"] = data.patron
        if data.categoria_fiscal_id is not None:
            cambios["categoria_fiscal_id"] = data.categoria_fiscal_id
        if data.tipo_coincidencia is not None:
            cambios["tipo_coincidencia"] = TipoCoincidencia[data.tipo_coincidencia]
        if data.tipo_apunte is not None:
            cambios["tipo_apunte"] = data.tipo_apunte
        if data.orden is not None:
            cambios["orden"] = data.orden
        if data.descripcion is not None:
            cambios["descripcion"] = data.descripcion
        if data.activa is not None:
            cambios["activa"] = data.activa
        regla = await service.actualizar(data.id, **cambios)
        return ReglaCategorizacionDetailType.from_model(regla)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_ESTRUCTURA_CONTABLE_GESTIONAR")])
    async def eliminar_regla_categorizacion(
        self, info: strawberry.Info, regla_id: uuid.UUID
    ) -> bool:
        service = ReglaCategorizacionService(info.context.session)
        await service.eliminar(regla_id)
        return True

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_ESTRUCTURA_CONTABLE_GESTIONAR")])
    async def clasificar_apuntes_pendientes(
        self, info: strawberry.Info, ejercicio: Optional[int] = None, forzar: bool = False
    ) -> ResultadoClasificacionType:
        """Aplica derivación por origen + reglas a los apuntes sin clasificar."""
        service = CategorizacionService(info.context.session)
        res = await service.clasificar_pendientes(ejercicio=ejercicio, forzar=forzar)
        return ResultadoClasificacionType(
            procesados=res["procesados"], clasificados=res["clasificados"]
        )

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_ESTRUCTURA_CONTABLE_GESTIONAR")])
    async def asignar_categoria_masiva(
        self,
        info: strawberry.Info,
        apunte_ids: List[uuid.UUID],
        categoria_fiscal_id: uuid.UUID,
    ) -> int:
        """Asigna una categoría a un lote de apuntes seleccionados. Devuelve cuántos se actualizaron."""
        service = CategorizacionService(info.context.session)
        return await service.asignar_categoria_masiva(apunte_ids, categoria_fiscal_id)
