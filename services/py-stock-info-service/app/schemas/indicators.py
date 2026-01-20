"""技术指标 Schema 定义."""

from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class SupportedIndicator(BaseModel):
    """支持的技术指标."""
    
    name: str = Field(..., description="指标名称（如 MA5, RSI14）")
    display_name: str = Field(..., description="显示名称")
    type: str = Field(..., description="指标类型（MA, EMA, RSI, MACD, BOLL）")
    category: str = Field(..., description="指标分类（trend, momentum, volatility, volume）")
    description: Optional[str] = Field(None, description="指标描述")
    params: dict[str, Any] = Field(default_factory=dict, description="默认参数")
    
    model_config = ConfigDict(from_attributes=True)


class IndicatorDataResponse(BaseModel):
    """技术指标数据响应."""
    
    date: str = Field(..., description="日期（YYYY-MM-DD）")
    timestamp: str = Field(..., description="时间戳（ISO 8601格式）")
    indicator_name: str = Field(..., description="指标名称")
    value: float | dict[str, float] = Field(..., description="指标值（单值或多值）")
    params: Optional[dict[str, Any]] = Field(None, description="指标参数")
    
    model_config = ConfigDict(from_attributes=True)


class IndicatorListResponse(BaseModel):
    """技术指标列表响应（不分页）."""
    
    ticker: str = Field(..., description="股票代码")
    indicator_name: str = Field(..., description="指标名称")
    period: str = Field(..., description="时间周期")
    count: int = Field(..., description="数据条数")
    data: list[IndicatorDataResponse] = Field(..., description="指标数据列表")


class IndicatorPageResponse(BaseModel):
    """技术指标分页响应."""
    
    items: list[IndicatorDataResponse] = Field(..., description="指标数据列表")
    total: int = Field(..., description="总条数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页条数")
    total_pages: int = Field(..., description="总页数")


class CalculateIndicatorRequest(BaseModel):
    """计算指标请求参数."""
    
    indicator_params: Optional[dict[str, Any]] = Field(
        None, 
        description="指标参数（可选，如 {period: 5}）"
    )


class BatchCalculateRequest(BaseModel):
    """批量计算请求参数."""
    
    tickers: list[str] = Field(..., description="股票代码列表")
    indicator_names: list[str] = Field(..., description="指标名称列表")
    period: str = Field("1d", description="时间周期")
    start_date: Optional[str] = Field(None, description="开始日期（YYYY-MM-DD）")
    end_date: Optional[str] = Field(None, description="结束日期（YYYY-MM-DD）")
