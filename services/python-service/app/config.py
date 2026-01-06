"""应用配置管理."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置."""

    # MongoDB 配置
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "financial_kanban"

    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8000

    # 环境
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
