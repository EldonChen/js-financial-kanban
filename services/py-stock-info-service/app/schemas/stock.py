"""股票数据模式."""

from datetime import datetime, UTC
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class StockBase(BaseModel):
    """股票基础模式."""

    ticker: str = Field(..., description="股票代码", min_length=1, max_length=20)
    name: str = Field(..., description="股票名称", min_length=1, max_length=200)
    market: Optional[str] = Field(None, description="市场（NASDAQ, NYSE, SSE, SZSE 等）", max_length=50)
    market_type: Optional[str] = Field(None, description="市场类型（A股、港股、美股）", max_length=20)
    sector: Optional[str] = Field(None, description="行业板块", max_length=100)
    industry: Optional[str] = Field(None, description="细分行业", max_length=200)
    currency: Optional[str] = Field(None, description="货币", max_length=10)
    exchange: Optional[str] = Field(None, description="交易所代码", max_length=50)
    country: Optional[str] = Field(None, description="国家", max_length=100)
    # 财务指标（可选）
    market_cap: Optional[float] = Field(None, description="市值")
    pe_ratio: Optional[float] = Field(None, description="市盈率")
    pb_ratio: Optional[float] = Field(None, description="市净率")
    dividend_yield: Optional[float] = Field(None, description="股息率")
    # 上市日期（可选）
    listing_date: Optional[datetime] = Field(None, description="上市日期")
    data_source: str = Field(default="yfinance", description="数据来源")


class StockCreate(StockBase):
    """创建股票的模式."""

    pass


class StockUpdate(BaseModel):
    """更新股票的模式."""

    name: Optional[str] = Field(None, description="股票名称", min_length=1, max_length=200)
    market: Optional[str] = Field(None, description="市场", max_length=50)
    market_type: Optional[str] = Field(None, description="市场类型", max_length=20)
    sector: Optional[str] = Field(None, description="行业板块", max_length=100)
    industry: Optional[str] = Field(None, description="细分行业", max_length=200)
    currency: Optional[str] = Field(None, description="货币", max_length=10)
    exchange: Optional[str] = Field(None, description="交易所代码", max_length=50)
    country: Optional[str] = Field(None, description="国家", max_length=100)
    market_cap: Optional[float] = Field(None, description="市值")
    pe_ratio: Optional[float] = Field(None, description="市盈率")
    pb_ratio: Optional[float] = Field(None, description="市净率")
    dividend_yield: Optional[float] = Field(None, description="股息率")
    listing_date: Optional[datetime] = Field(None, description="上市日期")


class StockResponse(StockBase):
    """股票响应模式."""

    id: str = Field(..., description="股票 ID")
    last_updated: datetime = Field(..., description="最后更新时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "market": "NASDAQ",
                "market_type": "美股",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "currency": "USD",
                "exchange": "NMS",
                "country": "United States",
                "market_cap": 3000000000000,
                "pe_ratio": 30.5,
                "pb_ratio": 45.2,
                "dividend_yield": 0.005,
                "data_source": "yfinance",
                "last_updated": "2024-01-01T00:00:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }
    )


class StockQueryParams(BaseModel):
    """股票查询参数."""

    ticker: Optional[str] = Field(None, description="股票代码（精确匹配）")
    name: Optional[str] = Field(None, description="股票名称（模糊查询）")
    market: Optional[str] = Field(None, description="市场（精确匹配）")
    market_type: Optional[str] = Field(None, description="市场类型（精确匹配：A股、港股、美股）")
    sector: Optional[str] = Field(None, description="行业板块（精确匹配）")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")


class BatchUpdateRequest(BaseModel):
    """批量更新请求."""

    tickers: list[str] = Field(..., description="股票代码列表", min_length=1)
