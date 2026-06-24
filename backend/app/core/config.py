from pydantic_settings import BaseSettings
from pydantic import computed_field
from functools import lru_cache


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

    # --- Formulario público de firmas (laicismo.org) ---
    # Captcha anti-bot. Proveedor: turnstile | hcaptcha | disabled (solo dev).
    captcha_provider: str = "turnstile"
    captcha_secret: str = ""            # env: CAPTCHA_SECRET

    # Base pública del API SIGA para los enlaces de verificación del email.
    # Si queda vacío, se usa app_url. Ej: https://api.laicismo.org
    siga_api_url: str = ""              # env: SIGA_API_URL

    # Orígenes CORS permitidos para el formulario público (coma-separados).
    # Ej: "https://laicismo.org,https://www.laicismo.org"
    firmas_cors_origins: str = ""       # env: FIRMAS_CORS_ORIGINS

    # Página de agradecimiento tras confirmar la firma (en laicismo.org).
    firmas_gracias_url: str = ""        # env: FIRMAS_GRACIAS_URL

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
