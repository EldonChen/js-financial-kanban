"""历史数据 Schema 定义."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class KlineDataResponse(BaseModel):
    """K线数据响应."""
    
    date: str = Field(..., description="日期（YYYY-MM-DD）")
    timestamp: str = Field(..., description="时间戳（ISO 8601格式）")
    open: float = Field(..., description="开盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    close: float = Field(..., description="收盘价")
    volume: float = Field(..., description="成交量")
    amount: Optional[float] = Field(None, description="成交额")
    adj_close: Optional[float] = Field(None, description="复权收盘价")
    data_source: str = Field(..., description="数据源")
    
    model_config = ConfigDict(from_attributes=True)


class HistoricalDataListResponse(BaseModel):
    """历史数据列表响应（不分页）."""
    
    ticker: str = Field(..., description="股票代码")
    period: str = Field(..., description="时间周期")
    count: int = Field(..., description="数据条数")
    data: list[KlineDataResponse] = Field(..., description="K线数据列表")


class HistoricalDataPageResponse(BaseModel):
    """历史数据分页响应."""
    
    items: list[KlineDataResponse] = Field(..., description="K线数据列表")
    total: int = Field(..., description="总条数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页条数")
    total_pages: int = Field(..., description="总页数")


class UpdateKlineDataResponse(BaseModel):
    """更新K线数据响应."""
    
    ticker: str = Field(..., description="股票代码")
    period: str = Field(..., description="时间周期")
    updated_count: int = Field(..., description="更新条数", alias="updated")
    new_count: int = Field(..., description="新增条数", alias="inserted")
    
    model_config = ConfigDict(populate_by_name=True)


class DeleteKlineDataResponse(BaseModel):
    """删除K线数据响应."""
    
    deleted_count: int = Field(..., description="删除条数")


class StatisticsResponse(BaseModel):
    """统计数据响应."""
    
    total_count: int = Field(..., description="总条数")
    start_date: str = Field(..., description="最早日期")
    end_date: str = Field(..., description="最新日期")
    missing_dates: list[str] = Field(default_factory=list, description="缺失日期列表")
    coverage_rate: Optional[float] = Field(None, description="数据覆盖率（0-1）")


class BatchUpdateRequest(BaseModel):
    """批量更新请求参数."""
    
    tickers: list[str] = Field(..., description="股票代码列表")
    period: str = Field("1d", description="时间周期")
    start_date: Optional[str] = Field(None, description="开始日期（YYYY-MM-DD）")
    end_date: Optional[str] = Field(None, description="结束日期（YYYY-MM-DD）")
