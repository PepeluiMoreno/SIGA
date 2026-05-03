# permission_matrix.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Set, FrozenSet, Iterable


# =========================================================
# Core concept: in-memory permission matrix
# =========================================================

@dataclass(frozen=True)
class PermissionMatrixSnapshot:
    """
    Snapshot inmutable de permisos precalculados.

    Estructura:
    - role → functionalities
    - role → transactions
    - functionality → transactions
    """

    role_to_transactions: Dict[str, FrozenSet[str]]
    role_to_functionalities: Dict[str, FrozenSet[str]]
    functionality_to_transactions: Dict[str, FrozenSet[str]]


# =========================================================
# Builder (from repositories)
# =========================================================

class PermissionMatrixBuilder:
    """
    Construye una matriz de permisos optimizada para runtime.
    Ideal para cache global o regeneración por eventos.
    """

    def __init__(
        self,
        role_repo,
        permission_repo,
        functionality_repo,
    ):
        self.role_repo = role_repo
        self.permission_repo = permission_repo
        self.functionality_repo = functionality_repo

    def build(self) -> PermissionMatrixSnapshot:

        roles = self.role_repo.get_all_roles()

        role_to_transactions: Dict[str, FrozenSet[str]] = {}
        role_to_functionalities: Dict[str, FrozenSet[str]] = {}
        functionality_to_transactions: Dict[str, FrozenSet[str]] = {}

        # -------------------------------
        # Build role mappings
        # -------------------------------
        for role in roles:

            transactions = self.permission_repo.get_transactions_by_role(role)
            functionalities = self.functionality_repo.get_functionalities_by_role(role)

            role_to_transactions[role] = frozenset(transactions)
            role_to_functionalities[role] = frozenset(functionalities)

        # -------------------------------
        # Build functionality mappings
        # -------------------------------
        all_functionalities = self.functionality_repo.get_all_functionalities()

        for f in all_functionalities:
            transactions = self.functionality_repo.get_transactions_by_functionality(f)
            functionality_to_transactions[f] = frozenset(transactions)

        return PermissionMatrixSnapshot(
            role_to_transactions=role_to_transactions,
            role_to_functionalities=role_to_functionalities,
            functionality_to_transactions=functionality_to_transactions,
        )


# =========================================================
# Runtime evaluator (fast path)
# =========================================================

class PermissionMatrix:
    """
    Motor de evaluación ultra rápido en memoria.
    Usado por AuthorizationService.
    """

    def __init__(self, snapshot: PermissionMatrixSnapshot):
        self.snapshot = snapshot

    # -------------------------------
    # Direct role → transaction
    # -------------------------------
    def role_allows_transaction(self, role: str, transaction: str) -> bool:
        return transaction in self.snapshot.role_to_transactions.get(role, frozenset())

    # -------------------------------
    # Role → functionality
    # -------------------------------
    def role_has_functionality(self, role: str, functionality: str) -> bool:
        return functionality in self.snapshot.role_to_functionalities.get(role, frozenset())

    # -------------------------------
    # Functionality → transaction
    # -------------------------------
    def functionality_allows_transaction(
        self,
        functionality: str,
        transaction: str,
    ) -> bool:
        return transaction in self.snapshot.functionality_to_transactions.get(
            functionality,
            frozenset(),
        )

    # -------------------------------
    # Combined evaluation
    # -------------------------------
    def role_allows_via_functionality(
        self,
        role: str,
        transaction: str,
    ) -> bool:

        functionalities = self.snapshot.role_to_functionalities.get(role, frozenset())

        for f in functionalities:
            if self.functionality_allows_transaction(f, transaction):
                return True

        return False


# =========================================================
# Cache layer (singleton-style optional)
# =========================================================

class PermissionMatrixCache:
    """
    Cache de snapshot completo.
    Se regenera solo cuando cambian roles/permisos.
    """

    def __init__(self):
        self._snapshot: PermissionMatrixSnapshot | None = None

    def get(self) -> PermissionMatrixSnapshot:
        if self._snapshot is None:
            raise RuntimeError("PermissionMatrix not initialized")
        return self._snapshot

    def set(self, snapshot: PermissionMatrixSnapshot) -> None:
        self._snapshot = snapshot

    def invalidate(self) -> None:
        self._snapshot = None