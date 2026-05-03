"""Builder async de la PermissionMatrix y cache global con invalidación por eventos.

Flujo:
  DB → SQLRepositories → AsyncPermissionMatrixBuilder → PermissionMatrixSnapshot
  Domain events → matrix_cache.invalidate() → rebuild en background
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Optional, Set

from sqlalchemy.ext.asyncio import AsyncSession

from .repositories import (
    SQLFunctionalityRepository,
    SQLPermissionRepository,
    SQLRoleRepository,
)

logger = logging.getLogger(__name__)


@dataclass
class PermissionMatrixSnapshot:
    """Snapshot inmutable del estado de permisos en un instante."""

    # role_id → frozenset de transaccion_id (vía RolTransaccion directo)
    role_transactions: Dict[str, FrozenSet[str]] = field(default_factory=dict)

    # role_id → frozenset de funcionalidad_id
    role_functionalities: Dict[str, FrozenSet[str]] = field(default_factory=dict)

    # funcionalidad_id → frozenset de transaccion_id
    functionality_transactions: Dict[str, FrozenSet[str]] = field(default_factory=dict)

    def can(self, role_ids: FrozenSet[str], transaction_id: str) -> bool:
        for rid in role_ids:
            if transaction_id in self.role_transactions.get(rid, frozenset()):
                return True
            for fid in self.role_functionalities.get(rid, frozenset()):
                if transaction_id in self.functionality_transactions.get(fid, frozenset()):
                    return True
        return False


class AsyncPermissionMatrixBuilder:

    def __init__(self, session: AsyncSession) -> None:
        self.roles = SQLRoleRepository(session)
        self.permissions = SQLPermissionRepository(session)
        self.functionalities = SQLFunctionalityRepository(session)

    async def build(self) -> PermissionMatrixSnapshot:
        snapshot = PermissionMatrixSnapshot()

        role_ids = await self.roles.get_all_role_ids()
        func_ids = await self.functionalities.get_all_functionality_ids()

        for rid in role_ids:
            txs = await self.permissions.get_transactions_by_role(rid)
            snapshot.role_transactions[rid] = frozenset(txs)

            funcs = await self.functionalities.get_functionalities_by_role(rid)
            snapshot.role_functionalities[rid] = frozenset(funcs)

        for fid in func_ids:
            txs = await self.functionalities.get_transactions_by_functionality(fid)
            snapshot.functionality_transactions[fid] = frozenset(txs)

        logger.info(
            "PermissionMatrix construida: %d roles, %d funcionalidades",
            len(role_ids),
            len(func_ids),
        )
        return snapshot


class PermissionMatrixCache:
    """Cache global con lock async para reconstrucción segura."""

    def __init__(self) -> None:
        self._snapshot: Optional[PermissionMatrixSnapshot] = None
        self._lock = asyncio.Lock()

    @property
    def snapshot(self) -> Optional[PermissionMatrixSnapshot]:
        return self._snapshot

    def is_ready(self) -> bool:
        return self._snapshot is not None

    async def rebuild(self, session: AsyncSession) -> None:
        async with self._lock:
            builder = AsyncPermissionMatrixBuilder(session)
            self._snapshot = await builder.build()

    def invalidate(self) -> None:
        self._snapshot = None
        logger.debug("PermissionMatrix invalidada")

    def can(self, role_ids: FrozenSet[str], transaction_id: str) -> bool:
        if self._snapshot is None:
            raise RuntimeError("PermissionMatrix no inicializada")
        return self._snapshot.can(role_ids, transaction_id)


# Instancia global — inicializada en el lifespan de FastAPI
matrix_cache = PermissionMatrixCache()


async def invalidate_and_rebuild(session: AsyncSession) -> None:
    """Punto de entrada para el event bus: invalida y reconstruye la matriz."""
    matrix_cache.invalidate()
    await matrix_cache.rebuild(session)
