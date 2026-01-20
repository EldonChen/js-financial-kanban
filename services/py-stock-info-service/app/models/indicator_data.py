"""技术指标数据模型."""

from datetime import datetime
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field, ConfigDict


class IndicatorMetadata(BaseModel):
    """技术指标元数据（metafield）."""

    ticker: str = Field(..., description="股票代码")
    period: str = Field(..., description="时间周期（1m, 5m, 15m, 30m, 60m, 1d, 1w, 1M）")
    indicator_type: str = Field(..., description="指标类型（MA, EMA, RSI, MACD, BOLL等）")
    indicator_name: str = Field(..., description="指标名称（MA5, MA10, RSI14等）")


class IndicatorData(BaseModel):
    """技术指标数据."""

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )

    timestamp: datetime = Field(..., description="时间戳")
    metadata: IndicatorMetadata = Field(..., description="元数据")
    value: float = Field(..., description="指标值")
    params: Optional[dict[str, Any]] = Field(None, description="指标参数")


async def ensure_indicator_data_collection(db: AsyncIOMotorDatabase):
    """确保 indicator_data TimeSeries Collection 存在.

    Args:
        db: MongoDB 数据库对象
    """
    # 检查集合是否存在
    collections = await db.list_collection_names()
    if "indicator_data" not in collections:
        # 创建 TimeSeries Collection
        await db.create_collection(
            "indicator_data",
            timeseries={
                "timeField": "timestamp",  # 时间字段
                "metaField": "metadata",  # 元数据字段
                "granularity": "hours",  # 粒度：hours（小时级别）
            },
        )


def prepare_indicator_document(indicator_data: dict[str, Any]) -> dict[str, Any]:
    """准备技术指标文档数据（用于插入到 MongoDB）.

    Args:
        indicator_data: 技术指标数据字典

    Returns:
        准备好的文档数据
    """
    # 确保 timestamp 是 datetime 对象
    if isinstance(indicator_data.get("timestamp"), str):
        indicator_data["timestamp"] = datetime.fromisoformat(
            indicator_data["timestamp"]
        )

    # 确保 metadata 字段存在
    if "metadata" not in indicator_data:
        indicator_data["metadata"] = {
            "ticker": indicator_data.get("ticker", ""),
            "period": indicator_data.get("period", "1d"),
            "indicator_type": indicator_data.get("indicator_type", ""),
            "indicator_name": indicator_data.get("indicator_name", ""),
        }

    # 移除顶层的 ticker, period, indicator_type, indicator_name（已在 metadata 中）
    for key in ["ticker", "period", "indicator_type", "indicator_name"]:
        indicator_data.pop(key, None)

    return indicator_data


def from_indicator_dict(data: dict[str, Any]) -> IndicatorData:
    """从字典创建 IndicatorData 对象.

    Args:
        data: 数据字典

    Returns:
        IndicatorData 对象
    """
    # 提取 metadata
    metadata = data.get("metadata", {})
    if not metadata:
        # 如果没有 metadata 字段，从顶层字段构建
        metadata = {
            "ticker": data.get("ticker", ""),
            "period": data.get("period", "1d"),
            "indicator_type": data.get("indicator_type", ""),
            "indicator_name": data.get("indicator_name", ""),
        }

    # 确保 timestamp 是 datetime 对象
    timestamp = data.get("timestamp")
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp)

    return IndicatorData(
        timestamp=timestamp,
        metadata=IndicatorMetadata(**metadata),
        value=data.get("value", 0.0),
        params=data.get("params"),
    )
