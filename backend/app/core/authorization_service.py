# authorization_service.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Set, Dict, Optional, FrozenSet, Tuple
from functools import lru_cache


# =========================================================
# DTOs
# =========================================================

@dataclass(frozen=True)
class AuthorizationResult:
    allowed: bool
    reason: str | None = None


@dataclass(frozen=True)
class AuthContext:
    """
    Contexto de ejecución:
    - agrupación territorial activa
    - junta/cargo (si aplica)
    - origen de ejecución (graphql, job, admin)
    """
    user_id: str
    territory_id: Optional[str] = None
    source: str = "graphql"


# =========================================================
# Ports (Infra interfaces)
# =========================================================

class RoleRepository(Protocol):
    def get_direct_roles(self, user_id: str) -> Set[str]: ...
    def get_roles_by_positions(self, user_id: str, territory_id: Optional[str]) -> Set[str]: ...


class PermissionRepository(Protocol):
    def get_transactions_by_role(self, role_id: str) -> Set[str]: ...


class FunctionalityRepository(Protocol):
    def get_transactions_by_functionality(self, functionality: str) -> Set[str]: ...
    def get_functionalities_by_role(self, role_id: str) -> Set[str]: ...


# =========================================================
# Core Service
# =========================================================

class AuthorizationService:
    """
    Authorization engine:
    RBAC + jerarquía organizativa + capa de funcionalidad + cache.
    """

    def __init__(
        self,
        role_repo: RoleRepository,
        permission_repo: PermissionRepository,
        functionality_repo: FunctionalityRepository,
    ):
        self.role_repo = role_repo
        self.permission_repo = permission_repo
        self.functionality_repo = functionality_repo

    # =====================================================
    # Public API
    # =====================================================

    def check(
        self,
        context: AuthContext,
        transaction: str,
    ) -> AuthorizationResult:

        roles = self._resolve_effective_roles(
            context.user_id,
            context.territory_id,
        )

        if not roles:
            return AuthorizationResult(False, "NO_ROLES")

        allowed = self._is_transaction_allowed(roles, transaction)

        if not allowed:
            return AuthorizationResult(False, "TRANSACTION_DENIED")

        return AuthorizationResult(True)

    # =====================================================
    # Role resolution (core hierarchy logic)
    # =====================================================

    def _resolve_effective_roles(
        self,
        user_id: str,
        territory_id: Optional[str],
    ) -> FrozenSet[str]:

        direct = self.role_repo.get_direct_roles(user_id)
        positional = self.role_repo.get_roles_by_positions(user_id, territory_id)

        return frozenset(direct | positional)

    # =====================================================
    # Permission evaluation layer
    # =====================================================

    def _is_transaction_allowed(
        self,
        roles: FrozenSet[str],
        transaction: str,
    ) -> bool:

        # 1. direct role → transaction mapping
        if self._check_role_transaction(roles, transaction):
            return True

        # 2. role → functionality → transaction mapping
        if self._check_functionality_chain(roles, transaction):
            return True

        return False

    # =====================================================
    # Direct role → transaction
    # =====================================================

    def _check_role_transaction(
        self,
        roles: FrozenSet[str],
        transaction: str,
    ) -> bool:
        for role in roles:
            if transaction in self._cached_role_transactions(role):
                return True
        return False

    # =====================================================
    # Role → functionality → transaction
    # =====================================================

    def _check_functionality_chain(
        self,
        roles: FrozenSet[str],
        transaction: str,
    ) -> bool:

        for role in roles:
            functionalities = self._cached_role_functionalities(role)

            for f in functionalities:
                if transaction in self._cached_functionality_transactions(f):
                    return True

        return False

    # =====================================================
    # CACHE LAYER (critical for performance)
    # =====================================================

    @lru_cache(maxsize=4096)
    def _cached_role_transactions(self, role_id: str) -> FrozenSet[str]:
        return frozenset(self.permission_repo.get_transactions_by_role(role_id))

    @lru_cache(maxsize=2048)
    def _cached_role_functionalities(self, role_id: str) -> FrozenSet[str]:
        return frozenset(self.functionality_repo.get_functionalities_by_role(role_id))

    @lru_cache(maxsize=4096)
    def _cached_functionality_transactions(self, functionality: str) -> FrozenSet[str]:
        return frozenset(
            self.functionality_repo.get_transactions_by_functionality(functionality)
        )

    # =====================================================
    # Cache invalidation helpers (important in real systems)
    # =====================================================

    def invalidate_role(self, role_id: str) -> None:
        self._cached_role_transactions.cache_clear()
        self._cached_role_functionalities.cache_clear()

    def invalidate_functionality(self, functionality: str) -> None:
        self._cached_functionality_transactions.cache_clear()