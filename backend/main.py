"""
Punto de entrada de la aplicación SIGA.

API GraphQL con generación automática desde modelos SQLAlchemy usando Strawchemy.
"""

from contextlib import asynccontextmanager
import logging
import uuid as uuid_lib
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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


MEDIA_DIR = Path("media/fotos")
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")


@app.post("/upload/foto-miembro/{miembro_id}")
async def upload_foto_miembro(
    miembro_id: str,
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None),
):
    """Sube o reemplaza la foto de perfil de un miembro."""
    from app.core.security import extract_bearer_token, load_user_from_token
    from app.core.database import async_session
    from sqlalchemy import update
    from app.modules.membresia.models.miembro import Miembro

    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")

    async with async_session() as session:
        user = await load_user_from_token(session, token)
        if not user:
            raise HTTPException(status_code=401, detail="Token inválido")

        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Solo se permiten imágenes")

        ext = Path(file.filename or "foto.jpg").suffix.lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
            raise HTTPException(status_code=400, detail="Formato no soportado")

        content = await file.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="El archivo no puede superar 5 MB")

        filename = f"{miembro_id}{ext}"
        (MEDIA_DIR / filename).write_bytes(content)

        foto_url = f"/api/media/fotos/{filename}"
        await session.execute(
            update(Miembro)
            .where(Miembro.id == uuid_lib.UUID(miembro_id))
            .values(foto_url=foto_url)
        )
        await session.commit()

        return {"fotoUrl": foto_url}


@app.post("/upload/foto-campania/{campania_id}")
async def upload_foto_campania(
    campania_id: str,
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None),
):
    """Sube o reemplaza la infografía principal de una campaña."""
    from app.core.security import extract_bearer_token, load_user_from_token
    from app.core.database import async_session
    from sqlalchemy import update
    from app.modules.actividades.models.campana import Campania

    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")

    async with async_session() as session:
        user = await load_user_from_token(session, token)
        if not user:
            raise HTTPException(status_code=401, detail="Token inválido")

        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Solo se permiten imágenes")

        ext = Path(file.filename or "foto.jpg").suffix.lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
            raise HTTPException(status_code=400, detail="Formato no soportado")

        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="El archivo no puede superar 10 MB")

        campania_dir = Path("media/campanias")
        campania_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{campania_id}{ext}"
        (campania_dir / filename).write_bytes(content)

        foto_url = f"/api/media/campanias/{filename}"
        await session.execute(
            update(Campania)
            .where(Campania.id == uuid_lib.UUID(campania_id))
            .values(foto_url=foto_url)
        )
        await session.commit()

        return {"fotoUrl": foto_url}


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
