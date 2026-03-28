from pydantic_settings import BaseSettings, SettingsConfigDict


class MixinSettings(BaseSettings):
    """Base settings class for all settings classes."""

    # В V2 используется model_config с типизацией SettingsConfigDict
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'  # Полезно: игнорирует лишние переменные в .env
    )
