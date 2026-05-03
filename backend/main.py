"""
Punto de entrada de la aplicación SIGA.

API GraphQL con generación automática desde modelos SQLAlchemy usando Strawchemy.
"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.core.database import async_session
from app.core.events import event_bus, wire_matrix_invalidation
from app.graphql.context import get_context
from app.graphql.schema_simple import schema

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialización al arrancar: sincroniza catálogos y construye la PermissionMatrix."""
    async with async_session() as session:
        # 1. Sincronizar catálogos declarados en código → DB
        from app.modules.acceso.services.catalog_sync import CatalogSyncService
        from app.modules.acceso import catalog as _acceso_catalog  # noqa: F401  registro side-effect

        # Importar catálogos de todos los módulos para que se auto-registren
        try:
            from app.modules.membresia import catalog as _membresia_catalog  # noqa: F401
        except ImportError:
            pass
        try:
            from app.modules.actividades import catalog as _actividades_catalog  # noqa: F401
        except ImportError:
            pass
        try:
            from app.modules.economico import catalog as _economico_catalog  # noqa: F401
        except ImportError:
            pass
        try:
            from app.modules.configuracion import catalog as _configuracion_catalog  # noqa: F401
        except ImportError:
            pass

        sync = CatalogSyncService(session)
        await sync.sync()
        logger.info("Catálogos sincronizados")

        # 2. Construir la PermissionMatrix en memoria
        from app.modules.acceso.services.matrix import matrix_cache
        await matrix_cache.rebuild(session)
        logger.info("PermissionMatrix construida")

    # 3. Conectar event bus con invalidación de la matrix
    wire_matrix_invalidation(async_session)
    logger.info("Event bus conectado")

    yield
    # Teardown (si se necesita cerrar conexiones externas)


# Crear aplicación FastAPI
app = FastAPI(
    title="SIGA API",
    description="API GraphQL para gestión de asociación política",
    version="0.2.0",
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Ajustar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router GraphQL
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    return {
        "name": "SIGA API",
        "version": "0.2.0",
        "graphql": "/graphql",
    }


@app.get("/health")
async def health():
    from app.modules.acceso.services.matrix import matrix_cache
    return {
        "status": "ok",
        "permission_matrix": "ready" if matrix_cache.is_ready() else "not_ready",
    }
