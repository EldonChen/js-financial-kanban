"""数据源提供者模块."""

from app.services.providers.base import StockDataProvider
from app.services.providers.router import StockDataRouter, get_stock_data_router
from app.services.providers.akshare_provider import AkshareProvider
from app.services.providers.yfinance_provider import YFinanceProvider
from app.services.providers.easyquotation_provider import EasyQuotationProvider

__all__ = [
    "StockDataProvider",
    "StockDataRouter",
    "get_stock_data_router",
    "AkshareProvider",
    "YFinanceProvider",
    "EasyQuotationProvider",
]
