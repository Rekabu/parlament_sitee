from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Настройки приложения.
    Читаются из .env файла автоматически.
    """
    secret_key: str = "dev-secret-key-change-me"
    database_url: str = "sqlite:///./parliament.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()