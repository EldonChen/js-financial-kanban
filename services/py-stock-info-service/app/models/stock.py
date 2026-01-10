"""股票数据模型."""

from datetime import datetime, UTC
from typing import Optional
from app.database import get_database


async def init_stock_indexes():
    """初始化股票集合索引."""
    db = get_database()
    collection = db.stocks

    # 创建唯一索引：ticker
    await collection.create_index("ticker", unique=True)

    # 创建文本索引：name（支持模糊查询）
    await collection.create_index("name")

    # 创建普通索引：market
    await collection.create_index("market")

    # 创建普通索引：market_type（新增）
    await collection.create_index("market_type")

    # 创建复合索引：ticker + market
    await collection.create_index([("ticker", 1), ("market", 1)])

    # 创建复合索引：market_type + market（新增，用于按市场类型查询）
    await collection.create_index([("market_type", 1), ("market", 1)])

    print("✅ 股票集合索引初始化完成")


def stock_from_dict(stock_dict: dict) -> dict:
    """将 MongoDB 文档转换为响应格式."""
    if "_id" in stock_dict:
        stock_dict["id"] = str(stock_dict.pop("_id"))
    return stock_dict


def prepare_stock_document(stock_data: dict) -> dict:
    """准备股票文档用于存储."""
    now = datetime.now(UTC)
    document = {
        "ticker": stock_data["ticker"],
        "name": stock_data["name"],
        "market": stock_data.get("market"),
        "market_type": stock_data.get("market_type"),  # 新增：市场类型（A股、港股、美股）
        "sector": stock_data.get("sector"),
        "industry": stock_data.get("industry"),
        "currency": stock_data.get("currency"),
        "exchange": stock_data.get("exchange"),
        "country": stock_data.get("country"),
        "data_source": stock_data.get("data_source", "yfinance"),
        # 新增字段：财务指标（可选）
        "market_cap": stock_data.get("market_cap"),
        "pe_ratio": stock_data.get("pe_ratio"),
        "pb_ratio": stock_data.get("pb_ratio"),
        "dividend_yield": stock_data.get("dividend_yield"),
        # 新增字段：上市日期（可选）
        "listing_date": stock_data.get("listing_date"),
        "last_updated": stock_data.get("last_updated", now),
        "updated_at": now,
    }

    # 如果是新文档，设置 created_at
    if "created_at" not in stock_data:
        document["created_at"] = now

    return document
