"""
Punto de entrada de la aplicación AIEL.

API GraphQL con generación automática desde modelos SQLAlchemy usando Strawchemy.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.graphql.context import get_context
from app.graphql.schema_simple import schema

# Crear router GraphQL con contexto de sesión DB
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphiql=True,  # Habilitar GraphiQL playground
)

# Crear aplicación FastAPI
app = FastAPI(
    title="AIEL API",
    description="API GraphQL para gestión de asociación política con generación automática desde SQLAlchemy",
    version="0.1.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Ajustar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir router GraphQL
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    """Endpoint raíz con información de la API."""
    return {
        "name": "AIEL API",
        "version": "0.1.0",
        "graphql": "/graphql",
        "playground": "/graphql (GraphiQL)",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
