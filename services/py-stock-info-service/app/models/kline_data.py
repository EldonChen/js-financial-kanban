"""K线数据模型（MongoDB TimeSeries Collection）."""

from datetime import datetime, UTC
from typing import Optional, Dict, Any
from app.database import get_database


async def init_kline_data_collection():
    """初始化K线数据 TimeSeries Collection."""
    db = get_database()
    
    # 检查集合是否已存在
    collections = await db.list_collection_names()
    if "kline_data" in collections:
        print("✅ K线数据集合已存在，跳过创建")
        return
    
    # 创建 TimeSeries Collection
    await db.create_collection(
        "kline_data",
        timeseries={
            "timeField": "timestamp",      # 时间字段（必填）
            "metaField": "metadata",       # 元数据字段（不经常变化的数据）
            "granularity": "hours"         # 粒度：hours（适合日线、周线、月线）
        }
    )
    
    # TimeSeries Collection 会自动创建以下索引：
    # 1. timestamp 索引
    # 2. metadata 字段索引
    # 3. metadata + timestamp 复合索引
    
    # 如果需要额外的查询优化，可以创建以下索引：
    # 1. 数据源查询索引
    collection = db.kline_data
    await collection.create_index("data_source")
    
    print("✅ K线数据 TimeSeries Collection 创建完成")


def kline_data_from_dict(kline_dict: dict) -> dict:
    """将 MongoDB 文档转换为响应格式."""
    if "_id" in kline_dict:
        kline_dict.pop("_id")  # TimeSeries Collection 的 _id 不需要返回
    
    # 展开 metadata 字段
    if "metadata" in kline_dict:
        metadata = kline_dict.pop("metadata")
        kline_dict["ticker"] = metadata.get("ticker")
        kline_dict["market"] = metadata.get("market")
        kline_dict["period"] = metadata.get("period")
    
    # 将 timestamp 转换为 ISO 格式字符串
    if "timestamp" in kline_dict and isinstance(kline_dict["timestamp"], datetime):
        kline_dict["date"] = kline_dict["timestamp"].isoformat()
    
    return kline_dict


def prepare_kline_document(
    ticker: str,
    market: str,
    period: str,
    kline_data: Dict[str, Any],
    data_source: str = "yfinance"
) -> dict:
    """准备K线文档用于存储到 TimeSeries Collection.
    
    Args:
        ticker: 股票代码
        market: 市场（如 NASDAQ, A股）
        period: 时间周期（1m, 5m, 15m, 30m, 60m, 1d, 1w, 1M）
        kline_data: K线数据字典，包含 timestamp, open, high, low, close, volume 等字段
        data_source: 数据来源（yfinance, akshare）
        
    Returns:
        dict: 格式化后的文档，符合 TimeSeries Collection 结构
    """
    # 解析 timestamp（支持多种格式）
    timestamp = kline_data.get("timestamp")
    if isinstance(timestamp, str):
        # 如果是字符串，尝试解析
        timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    elif isinstance(timestamp, datetime):
        # 如果已经是 datetime，确保是 UTC 时区
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)
    else:
        # 如果没有 timestamp，使用当前时间
        timestamp = datetime.now(UTC)
    
    document = {
        "timestamp": timestamp,              # 时间字段（必填，TimeSeries 要求）
        "metadata": {                        # 元数据字段（不经常变化）
            "ticker": ticker,
            "market": market,
            "period": period
        },
        # 测量字段（OHLCV 数据）
        "open": float(kline_data.get("open", 0)),
        "high": float(kline_data.get("high", 0)),
        "low": float(kline_data.get("low", 0)),
        "close": float(kline_data.get("close", 0)),
        "volume": int(kline_data.get("volume", 0)),
        "amount": float(kline_data.get("amount", 0)) if kline_data.get("amount") else None,  # A股常用
        "adj_close": float(kline_data.get("adj_close")) if kline_data.get("adj_close") else None,  # 复权收盘价
        "data_source": data_source           # 数据来源
    }
    
    # 移除 None 值
    document = {k: v for k, v in document.items() if v is not None}
    
    return document


def validate_kline_data(kline_data: Dict[str, Any]) -> bool:
    """验证K线数据的完整性和合理性.
    
    Args:
        kline_data: K线数据字典
        
    Returns:
        bool: 数据是否有效
    """
    # 必需字段检查
    required_fields = ["open", "high", "low", "close", "volume"]
    for field in required_fields:
        if field not in kline_data or kline_data[field] is None:
            return False
    
    # 价格逻辑检查
    open_price = float(kline_data["open"])
    high_price = float(kline_data["high"])
    low_price = float(kline_data["low"])
    close_price = float(kline_data["close"])
    volume = int(kline_data["volume"])
    
    # 1. high >= low
    if high_price < low_price:
        return False
    
    # 2. high >= open, high >= close
    if high_price < open_price or high_price < close_price:
        return False
    
    # 3. low <= open, low <= close
    if low_price > open_price or low_price > close_price:
        return False
    
    # 4. volume >= 0
    if volume < 0:
        return False
    
    # 5. 价格 > 0
    if open_price <= 0 or high_price <= 0 or low_price <= 0 or close_price <= 0:
        return False
    
    return True
