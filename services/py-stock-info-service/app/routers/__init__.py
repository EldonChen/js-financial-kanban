"""路由模块."""

from . import stocks, schedules, providers, historical_data, indicators

__all__ = ["stocks", "schedules", "providers", "historical_data", "indicators"]

from app.routers import stocks, schedules, providers

__all__ = ["stocks", "schedules", "providers"]
