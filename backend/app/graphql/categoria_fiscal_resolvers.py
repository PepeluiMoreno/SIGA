"""Resolvers GraphQL para categorías fiscales (contabilidad simplificada)."""

import uuid
from typing import List, Optional

import strawberry

from app.graphql.permissions import RequireTransaction
from app.modules.economico.services.categoria_fiscal_service import CategoriaFiscalService
from app.modules.economico.models.contabilidad import TipoCategoriaFiscal


@strawberry.type
class CategoriaFiscalType:
    id: uuid.UUID
    codigo: str
    nombre: str
    descripcion: Optional[str]
    tipo: str
    computa_modelo_182: bool
    computa_modelo_347: bool
    casilla_modelo: Optional[str]
    orden: int
    color: Optional[str]
    activa: bool

    @staticmethod
    def from_model(m) -> "CategoriaFiscalType":
        return CategoriaFiscalType(
            id=m.id,
            codigo=m.codigo,
            nombre=m.nombre,
            descripcion=m.descripcion,
            tipo=m.tipo.value if hasattr(m.tipo, "value") else m.tipo,
            computa_modelo_182=m.computa_modelo_182,
            computa_modelo_347=m.computa_modelo_347,
            casilla_modelo=m.casilla_modelo,
            orden=m.orden,
            color=m.color,
            activa=m.activa,
        )


@strawberry.input
class CrearCategoriaFiscalInput:
    codigo: str
    nombre: str
    tipo: str  # INGRESO | GASTO
    descripcion: Optional[str] = None
    computa_modelo_182: bool = False
    computa_modelo_347: bool = False
    casilla_modelo: Optional[str] = None
    orden: int = 10
    color: Optional[str] = None


@strawberry.input
class ActualizarCategoriaFiscalInput:
    id: uuid.UUID
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    computa_modelo_182: Optional[bool] = None
    computa_modelo_347: Optional[bool] = None
    casilla_modelo: Optional[str] = None
    orden: Optional[int] = None
    color: Optional[str] = None
    activa: Optional[bool] = None


@strawberry.type
class CategoriaFiscalQuery:

    @strawberry.field(permission_classes=[RequireTransaction("ECO_ESTRUCTURA_CONTABLE_LISTAR")])
    async def categorias_fiscales(
        self,
        info: strawberry.Info,
        tipo: Optional[str] = None,
        activas_solo: bool = True,
    ) -> List[CategoriaFiscalType]:
        service = CategoriaFiscalService(info.context.session)
        tipo_enum = TipoCategoriaFiscal[tipo] if tipo else None
        items = await service.listar(tipo=tipo_enum, activas_solo=activas_solo)
        return [CategoriaFiscalType.from_model(c) for c in items]


@strawberry.type
class CategoriaFiscalMutation:

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_ESTRUCTURA_CONTABLE_GESTIONAR")])
    async def crear_categoria_fiscal(
        self, info: strawberry.Info, data: CrearCategoriaFiscalInput
    ) -> CategoriaFiscalType:
        service = CategoriaFiscalService(info.context.session)
        categoria = await service.crear(
            codigo=data.codigo,
            nombre=data.nombre,
            tipo=TipoCategoriaFiscal[data.tipo],
            descripcion=data.descripcion,
            computa_modelo_182=data.computa_modelo_182,
            computa_modelo_347=data.computa_modelo_347,
            casilla_modelo=data.casilla_modelo,
            orden=data.orden,
            color=data.color,
            creado_por_id=info.context.current_user.id if info.context.current_user else None,
        )
        return CategoriaFiscalType.from_model(categoria)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_ESTRUCTURA_CONTABLE_GESTIONAR")])
    async def actualizar_categoria_fiscal(
        self, info: strawberry.Info, data: ActualizarCategoriaFiscalInput
    ) -> CategoriaFiscalType:
        service = CategoriaFiscalService(info.context.session)
        cambios = {
            k: v for k, v in {
                "codigo": data.codigo,
                "nombre": data.nombre,
                "descripcion": data.descripcion,
                "computa_modelo_182": data.computa_modelo_182,
                "computa_modelo_347": data.computa_modelo_347,
                "casilla_modelo": data.casilla_modelo,
                "orden": data.orden,
                "color": data.color,
                "activa": data.activa,
            }.items() if v is not None
        }
        categoria = await service.actualizar(data.id, **cambios)
        return CategoriaFiscalType.from_model(categoria)

    @strawberry.mutation(permission_classes=[RequireTransaction("ECO_ESTRUCTURA_CONTABLE_GESTIONAR")])
    async def eliminar_categoria_fiscal(
        self, info: strawberry.Info, categoria_id: uuid.UUID
    ) -> bool:
        service = CategoriaFiscalService(info.context.session)
        await service.eliminar(categoria_id)
        return True
