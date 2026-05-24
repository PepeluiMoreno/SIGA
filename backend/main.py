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

        # 1b. Enlazar SUPERADMIN con las transacciones añadidas por catalog.py
        from app.scripts.bootstrap import (
            sync_superadmin_all_transactions,
            sync_roles_funcionales_catalog,
        )
        await sync_superadmin_all_transactions(session)
        # 1c. Re-enlazar roles funcionales con transacciones de catalog.py
        await sync_roles_funcionales_catalog(session)
        await session.commit()

        # 2. Construir la PermissionMatrix en memoria
        from app.modules.acceso.services.matrix import matrix_cache
        await matrix_cache.rebuild(session)
        logger.info("PermissionMatrix construida")

    # 3. Conectar event bus con invalidación de la matrix
    wire_matrix_invalidation(async_session)
    # 3b. Conectar handlers de comunicación (avisos de flujos de trabajo)
    from app.modules.core.comunicacion.handlers import wire_comunicacion_handlers
    wire_comunicacion_handlers(async_session)
    # 3c. Conectar handlers del chat interno (canal por grupo de trabajo)
    from app.modules.core.comunicacion.mensajeria.handlers import wire_chat_handlers
    wire_chat_handlers(async_session)
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

# Routers REST
from app.api.recibos import router as recibos_router
from app.api.remesas import router as remesas_router
try:
    from app.api.paypal import router as paypal_router
    _paypal_available = True
except ImportError:
    _paypal_available = False

app.include_router(recibos_router)
app.include_router(remesas_router)
if _paypal_available:
    app.include_router(paypal_router)


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


UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

MAX_DOC_SIZE = 30 * 1024 * 1024  # 30 MB


@app.post("/upload/actividades/{actividad_id}/documentos")
async def upload_documento_actividad(
    actividad_id: str,
    file: UploadFile = File(...),
    nombre: str = "",
    tipo_doc: str = "otro",
    authorization: Optional[str] = Header(None),
):
    """Sube un documento adjunto a una actividad."""
    from app.core.security import extract_bearer_token, load_user_from_token
    from app.core.database import async_session
    from app.modules.actividades.models.actividad import DocumentoActividad

    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")

    async with async_session() as session:
        user = await load_user_from_token(session, token)
        if not user:
            raise HTTPException(status_code=401, detail="Token inválido")

        content = await file.read()
        if len(content) > MAX_DOC_SIZE:
            raise HTTPException(status_code=400, detail="El archivo no puede superar 30 MB")

        act_dir = UPLOADS_DIR / "actividades" / actividad_id
        act_dir.mkdir(parents=True, exist_ok=True)
        nombre_archivo = file.filename or "documento"
        ruta = act_dir / nombre_archivo
        # Evitar colisiones
        if ruta.exists():
            stem, suffix = Path(nombre_archivo).stem, Path(nombre_archivo).suffix
            nombre_archivo = f"{stem}_{uuid_lib.uuid4().hex[:6]}{suffix}"
            ruta = act_dir / nombre_archivo
        ruta.write_bytes(content)

        ruta_relativa = f"actividades/{actividad_id}/{nombre_archivo}"
        doc = DocumentoActividad(
            actividad_id=uuid_lib.UUID(actividad_id),
            nombre=nombre or nombre_archivo,
            nombre_archivo=nombre_archivo,
            ruta=ruta_relativa,
            tipo_mime=file.content_type,
            tamanyo=len(content),
            tipo_doc=tipo_doc,
            subido_por_id=user.id,
        )
        session.add(doc)
        await session.commit()
        await session.refresh(doc)

        return {
            "id": str(doc.id),
            "nombre": doc.nombre,
            "ruta": doc.ruta,
            "tipo_mime": doc.tipo_mime,
            "tamanyo": doc.tamanyo,
            "url": f"/api/uploads/{ruta_relativa}",
        }


@app.post("/upload/partidas-actividad/{partida_id}/documentos")
async def upload_documento_partida_actividad(
    partida_id: str,
    file: UploadFile = File(...),
    nombre: str = "",
    tipo_doc: str = "otro",
    authorization: Optional[str] = Header(None),
):
    """Sube un justificante contable adjunto a una partida de actividad."""
    from app.core.security import extract_bearer_token, load_user_from_token
    from app.core.database import async_session
    from app.modules.actividades.models.actividad import DocumentoPartida, PartidaPresupuestoActividad
    from sqlalchemy import select as sa_select

    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")

    async with async_session() as session:
        user = await load_user_from_token(session, token)
        if not user:
            raise HTTPException(status_code=401, detail="Token inválido")

        content = await file.read()
        if len(content) > MAX_DOC_SIZE:
            raise HTTPException(status_code=400, detail="El archivo no puede superar 30 MB")

        doc_dir = UPLOADS_DIR / "justificantes" / "actividad" / partida_id
        doc_dir.mkdir(parents=True, exist_ok=True)
        nombre_archivo = file.filename or "justificante"
        ruta = doc_dir / nombre_archivo
        if ruta.exists():
            stem, suffix = Path(nombre_archivo).stem, Path(nombre_archivo).suffix
            nombre_archivo = f"{stem}_{uuid_lib.uuid4().hex[:6]}{suffix}"
            ruta = doc_dir / nombre_archivo
        ruta.write_bytes(content)

        ruta_relativa = f"justificantes/actividad/{partida_id}/{nombre_archivo}"
        doc = DocumentoPartida(
            partida_actividad_id=uuid_lib.UUID(partida_id),
            nombre=nombre or nombre_archivo,
            nombre_archivo=nombre_archivo,
            ruta=ruta_relativa,
            tipo_mime=file.content_type,
            tamanyo=len(content),
            tipo_doc=tipo_doc,
            subido_por_id=user.id,
        )
        session.add(doc)
        await session.commit()
        await session.refresh(doc)

        return {
            "id": str(doc.id),
            "nombre": doc.nombre,
            "ruta": doc.ruta,
            "tipo_mime": doc.tipo_mime,
            "tamanyo": doc.tamanyo,
            "url": f"/api/uploads/{ruta_relativa}",
        }


@app.post("/upload/partidas-campania/{partida_id}/documentos")
async def upload_documento_partida_campania(
    partida_id: str,
    file: UploadFile = File(...),
    nombre: str = "",
    tipo_doc: str = "otro",
    authorization: Optional[str] = Header(None),
):
    """Sube un justificante contable adjunto a una partida de campaña."""
    from app.core.security import extract_bearer_token, load_user_from_token
    from app.core.database import async_session
    from app.modules.actividades.models.actividad import DocumentoPartida

    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")

    async with async_session() as session:
        user = await load_user_from_token(session, token)
        if not user:
            raise HTTPException(status_code=401, detail="Token inválido")

        content = await file.read()
        if len(content) > MAX_DOC_SIZE:
            raise HTTPException(status_code=400, detail="El archivo no puede superar 30 MB")

        doc_dir = UPLOADS_DIR / "justificantes" / "campania" / partida_id
        doc_dir.mkdir(parents=True, exist_ok=True)
        nombre_archivo = file.filename or "justificante"
        ruta = doc_dir / nombre_archivo
        if ruta.exists():
            stem, suffix = Path(nombre_archivo).stem, Path(nombre_archivo).suffix
            nombre_archivo = f"{stem}_{uuid_lib.uuid4().hex[:6]}{suffix}"
            ruta = doc_dir / nombre_archivo
        ruta.write_bytes(content)

        ruta_relativa = f"justificantes/campania/{partida_id}/{nombre_archivo}"
        doc = DocumentoPartida(
            partida_campania_id=uuid_lib.UUID(partida_id),
            nombre=nombre or nombre_archivo,
            nombre_archivo=nombre_archivo,
            ruta=ruta_relativa,
            tipo_mime=file.content_type,
            tamanyo=len(content),
            tipo_doc=tipo_doc,
            subido_por_id=user.id,
        )
        session.add(doc)
        await session.commit()
        await session.refresh(doc)

        return {
            "id": str(doc.id),
            "nombre": doc.nombre,
            "ruta": doc.ruta,
            "tipo_mime": doc.tipo_mime,
            "tamanyo": doc.tamanyo,
            "url": f"/api/uploads/{ruta_relativa}",
        }


@app.post("/upload/justificantes/{justificante_id}/documentos")
async def upload_documento_justificante(
    justificante_id: str,
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None),
):
    """Sube un documento probatorio (factura, ticket, foto) asociado a un
    JustificanteGasto. Permite múltiples documentos por justificante.

    El OCR queda pendiente para un mini-ciclo aparte (requiere tesseract en imagen).
    """
    from app.core.security import extract_bearer_token, load_user_from_token
    from app.core.database import async_session
    from app.modules.economico.services.justificante_gasto_service import JustificanteGastoService

    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")

    async with async_session() as session:
        user = await load_user_from_token(session, token)
        if not user:
            raise HTTPException(status_code=401, detail="Token inválido")

        content = await file.read()
        if len(content) > MAX_DOC_SIZE:
            raise HTTPException(status_code=400, detail="El archivo no puede superar 30 MB")

        doc_dir = UPLOADS_DIR / "justificantes" / justificante_id
        doc_dir.mkdir(parents=True, exist_ok=True)
        nombre_archivo = file.filename or "documento"
        ruta = doc_dir / nombre_archivo
        if ruta.exists():
            stem, suffix = Path(nombre_archivo).stem, Path(nombre_archivo).suffix
            nombre_archivo = f"{stem}_{uuid_lib.uuid4().hex[:6]}{suffix}"
            ruta = doc_dir / nombre_archivo
        ruta.write_bytes(content)

        ruta_relativa = f"justificantes/{justificante_id}/{nombre_archivo}"
        url_publica = f"/api/uploads/{ruta_relativa}"

        try:
            service = JustificanteGastoService(session)
            doc = await service.adjuntar_documento(
                justificante_id=uuid_lib.UUID(justificante_id),
                nombre_archivo=nombre_archivo,
                url=url_publica,
                mime_type=file.content_type,
                tamano_bytes=len(content),
            )
        except ValueError as e:
            # Limpiar el archivo si el justificante no existe o está anulado
            try:
                ruta.unlink(missing_ok=True)
            except Exception:
                pass
            raise HTTPException(status_code=400, detail=str(e))

        return {
            "id": str(doc.id),
            "nombre_archivo": doc.nombre_archivo,
            "url": doc.url,
            "mime_type": doc.mime_type,
            "tamano_bytes": doc.tamano_bytes,
        }


@app.delete("/upload/justificantes/documentos/{documento_id}")
async def borrar_documento_justificante(
    documento_id: str,
    authorization: Optional[str] = Header(None),
):
    """Borra un documento probatorio asociado a un justificante (BD + archivo en disco)."""
    from app.core.security import extract_bearer_token, load_user_from_token
    from app.core.database import async_session
    from app.modules.economico.services.justificante_gasto_service import JustificanteGastoService

    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")

    async with async_session() as session:
        user = await load_user_from_token(session, token)
        if not user:
            raise HTTPException(status_code=401, detail="Token inválido")
        service = JustificanteGastoService(session)
        try:
            await service.eliminar_documento(uuid_lib.UUID(documento_id))
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return {"ok": True}


@app.post("/upload/solicitudes-reduccion/{solicitud_id}/documentos")
async def upload_documento_solicitud_reduccion(
    solicitud_id: str,
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None),
):
    """Sube un documento acreditativo (paro, jubilación, carné de estudiante…)
    a una SolicitudReduccionCuota. Permite varios documentos por solicitud."""
    from app.core.security import extract_bearer_token, load_user_from_token
    from app.core.database import async_session
    from app.modules.economico.models.cuotas import (
        SolicitudReduccionCuota, SolicitudReduccionCuotaDocumento,
    )

    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")

    async with async_session() as session:
        user = await load_user_from_token(session, token)
        if not user:
            raise HTTPException(status_code=401, detail="Token inválido")

        sol = await session.get(SolicitudReduccionCuota, uuid_lib.UUID(solicitud_id))
        if not sol:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")

        content = await file.read()
        if len(content) > MAX_DOC_SIZE:
            raise HTTPException(status_code=400, detail="El archivo no puede superar 30 MB")

        doc_dir = UPLOADS_DIR / "solicitudes-reduccion" / solicitud_id
        doc_dir.mkdir(parents=True, exist_ok=True)
        nombre_archivo = file.filename or "documento"
        ruta = doc_dir / nombre_archivo
        if ruta.exists():
            stem, suffix = Path(nombre_archivo).stem, Path(nombre_archivo).suffix
            nombre_archivo = f"{stem}_{uuid_lib.uuid4().hex[:6]}{suffix}"
            ruta = doc_dir / nombre_archivo
        ruta.write_bytes(content)

        ruta_relativa = f"solicitudes-reduccion/{solicitud_id}/{nombre_archivo}"
        doc = SolicitudReduccionCuotaDocumento(
            solicitud_id=sol.id,
            nombre_archivo=nombre_archivo,
            url=f"/api/uploads/{ruta_relativa}",
            mime_type=file.content_type,
            tamano_bytes=len(content),
        )
        session.add(doc)
        await session.commit()
        return {
            "id": str(doc.id),
            "nombre_archivo": doc.nombre_archivo,
            "url": doc.url,
            "mime_type": doc.mime_type,
            "tamano_bytes": doc.tamano_bytes,
        }


@app.delete("/upload/solicitudes-reduccion/documentos/{documento_id}")
async def borrar_documento_solicitud_reduccion(
    documento_id: str,
    authorization: Optional[str] = Header(None),
):
    """Borra un documento acreditativo de una solicitud (BD + archivo en disco)."""
    from app.core.security import extract_bearer_token, load_user_from_token
    from app.core.database import async_session
    from app.modules.economico.models.cuotas import SolicitudReduccionCuotaDocumento

    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")

    async with async_session() as session:
        user = await load_user_from_token(session, token)
        if not user:
            raise HTTPException(status_code=401, detail="Token inválido")
        doc = await session.get(SolicitudReduccionCuotaDocumento, uuid_lib.UUID(documento_id))
        if not doc:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        try:
            rel = doc.url.replace("/api/uploads/", "")
            (UPLOADS_DIR / rel).unlink(missing_ok=True)
        except Exception:
            pass
        await session.delete(doc)
        await session.commit()
        return {"ok": True}


@app.get("/")
async def root():
    return {
        "name": "SIGA API",
        "version": "0.2.0",
        "graphql": "/graphql",
    }


@app.get("/health")
async def health():
    from sqlalchemy import text
    from app.modules.acceso.services.matrix import matrix_cache
    from app.core.email_service import _load_smtp_config, ping_smtp

    db_status   = "ok"
    smtp_status = "not_configured"

    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
            try:
                cfg = await _load_smtp_config(session)
                if cfg.configured:
                    smtp_status = await ping_smtp(cfg, timeout=5.0)
                # else: smtp_status queda "not_configured"
            except Exception:
                smtp_status = "not_configured"
    except Exception:
        db_status = "error"

    overall = "ok" if db_status == "ok" and smtp_status in ("ok", "not_configured") else "degraded"
    return {
        "status": overall,
        "permission_matrix": "ready" if matrix_cache.is_ready() else "not_ready",
        "database": db_status,
        "smtp": smtp_status,
    }
