"""Capa de seguridad: hash de contraseñas y JWT."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domains.usuarios.models.usuario import Usuario
from .config import get_settings


# bcrypt impone un máximo de 72 bytes en la contraseña.
_BCRYPT_MAX_BYTES = 72


class TokenError(Exception):
    """Token inválido, expirado o ausente."""


def _to_bytes(plain: str) -> bytes:
    encoded = plain.encode("utf-8")
    return encoded[:_BCRYPT_MAX_BYTES]


def hash_password(plain: str) -> str:
    """Genera el hash bcrypt de una contraseña."""
    salted = bcrypt.hashpw(_to_bytes(plain), bcrypt.gensalt())
    return salted.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica una contraseña contra su hash bcrypt."""
    try:
        return bcrypt.checkpw(_to_bytes(plain), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(
    usuario_id: uuid.UUID,
    *,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Genera un JWT firmado con el usuario_id como subject."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.jwt_expire_minutes))
    payload = {
        "sub": str(usuario_id),
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Decodifica y valida un JWT. Lanza TokenError si es inválido o expiró."""
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("Token expirado") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenError("Token inválido") from exc


def extract_bearer_token(authorization_header: Optional[str]) -> Optional[str]:
    """Extrae el token de un header Authorization 'Bearer <token>'."""
    if not authorization_header:
        return None
    parts = authorization_header.split(maxsplit=1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1].strip() or None


async def load_user_from_token(session: AsyncSession, token: str) -> Optional[Usuario]:
    """Decodifica el token y carga el usuario asociado. None si no es válido."""
    try:
        payload = decode_access_token(token)
    except TokenError:
        return None
    sub = payload.get("sub")
    if not sub:
        return None
    try:
        usuario_id = uuid.UUID(sub)
    except (ValueError, TypeError):
        return None
    stmt = select(Usuario).where(Usuario.id == usuario_id, Usuario.activo == True)  # noqa: E712
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
