"""GraphQL API con generación automática desde modelos SQLAlchemy."""

from strawchemy import Strawchemy

# Inicializar Strawchemy para PostgreSQL (async con asyncpg)
strawchemy = Strawchemy("postgresql")
