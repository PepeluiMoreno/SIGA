"""Asignación de transacciones a roles (M2M con auditoría)."""

import uuid

from sqlalchemy import ForeignKey, Uuid, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....infrastructure.base_model import BaseModel


class RolTransaccion(BaseModel):
    """Permiso: un rol puede ejecutar una transacción.

    Conserva auditoría (creado_por_id de BaseModel) para saber quién y cuándo
    asignó cada permiso.
    """
    __tablename__ = 'roles_transacciones'
    __table_args__ = (
        UniqueConstraint('rol_id', 'transaccion_id', name='uq_rol_transaccion'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    rol_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('roles.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    transaccion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey('transacciones.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    rol: Mapped["Rol"] = relationship(back_populates="transacciones", lazy="selectin")
    transaccion: Mapped["Transaccion"] = relationship(back_populates="roles", lazy="selectin")

    def __repr__(self) -> str:
        return f"<RolTransaccion(rol_id='{self.rol_id}', transaccion_id='{self.transaccion_id}')>"
