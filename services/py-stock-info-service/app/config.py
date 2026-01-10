"""应用配置管理."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置."""

    # MongoDB 配置
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "financial_kanban"

    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8001  # 使用不同端口避免与 python-service 冲突

    # 环境
    environment: str = "development"

    # 日志配置
    log_level: str = "INFO"  # 开发环境默认 INFO，生产环境建议 WARNING

    # 数据源配置（第一优先级：免费优先、无需认证）
    enable_akshare: bool = True  # 默认启用
    enable_yfinance: bool = True  # 默认启用
    enable_easyquotation: bool = False  # 默认关闭（仅用于实时行情）

    # 数据源配置（第二优先级：需要注册 API Key，存在限制）
    enable_tushare: bool = False  # 默认关闭（需要 token）
    tushare_token: str = ""  # Tushare token
    enable_iex_cloud: bool = False  # 默认关闭（需要 API Key）
    iex_cloud_api_key: str = ""  # IEX Cloud API Key
    enable_alpha_vantage: bool = False  # 默认关闭（需要 API Key）
    alpha_vantage_api_key: str = ""  # Alpha Vantage API Key

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
