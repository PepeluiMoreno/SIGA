from pydantic_settings import BaseSettings
from pydantic import computed_field, model_validator
from functools import lru_cache

from app.core.secrets import read_secret_file


class Settings(BaseSettings):
    # Supabase Pooler (Transaction mode)
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # URL pública de la aplicación (usada en links de email)
    app_url: str = "http://localhost:5173"

    # SMTP — opcionales: si están vacíos, se usa la configuración guardada en BD.
    # Prioridad: .env / secret del orquestador > tabla configuracion.
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""       # env: SMTP_USERNAME
    smtp_password: str = ""       # env: SMTP_PASSWORD
    smtp_from: str = ""           # env: SMTP_FROM  (si vacío usa smtp_username)
    smtp_encryption: str = "tls"  # env: SMTP_ENCRYPTION  (tls | ssl | none)

    @model_validator(mode="before")
    @classmethod
    def _aplicar_docker_secrets(cls, data):
        """Para cada campo, si existe ``<CAMPO>_FILE`` apuntando a un Docker
        secret legible, su valor prevalece sobre la variable de entorno.
        Conforme al Estándar de Ingeniería §4.5."""
        if isinstance(data, dict):
            for name in cls.model_fields:
                valor = read_secret_file(name.upper())
                if valor is not None:
                    data[name] = valor
        return data

    @computed_field
    @property
    def database_url(self) -> str:
        """URL con pooler para la app."""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
