"""技术指标查询服务."""

import logging
from datetime import datetime
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database

logger = logging.getLogger(__name__)


class IndicatorQuery:
    """技术指标查询服务（查询指标数据）."""

    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        """初始化指标查询服务.

        Args:
            db: MongoDB 数据库对象（可选）
        """
        self.db = db if db is not None else get_database()
        self.collection = self.db.indicator_data

    async def query_by_indicator(
        self,
        ticker: str,
        indicator_name: str,
        period: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """按指标查询数据.

        Args:
            ticker: 股票代码
            indicator_name: 指标名称（如 MA5, RSI14）
            period: 时间周期
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            limit: 返回数量限制（可选）

        Returns:
            list[dict]: 指标数据列表
        """
        # 构建查询条件
        query: dict[str, Any] = {
            "metadata.ticker": ticker,
            "metadata.period": period,
            "metadata.indicator_name": indicator_name,
        }

        # 时间范围查询
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date

        # 执行查询
        cursor = self.collection.find(query).sort("timestamp", 1)
        if limit:
            cursor = cursor.limit(limit)

        # 获取结果
        results = []
        async for doc in cursor:
            # 移除 _id 字段
            doc.pop("_id", None)
            # 展开 metadata
            if "metadata" in doc:
                metadata = doc.pop("metadata")
                doc["ticker"] = metadata.get("ticker")
                doc["period"] = metadata.get("period")
                doc["indicator_type"] = metadata.get("indicator_type")
                doc["indicator_name"] = metadata.get("indicator_name")
            results.append(doc)

        logger.info(
            f"查询指标数据成功：{ticker} {indicator_name} {period} - {len(results)} 条"
        )
        return results

    async def get_latest_date(
        self, ticker: str, indicator_name: str, period: str
    ) -> Optional[datetime]:
        """获取最新数据的日期.

        Args:
            ticker: 股票代码
            indicator_name: 指标名称
            period: 时间周期

        Returns:
            datetime: 最新数据的日期，如果没有数据则返回 None
        """
        # 查询最新的一条数据
        doc = await self.collection.find_one(
            {
                "metadata.ticker": ticker,
                "metadata.period": period,
                "metadata.indicator_name": indicator_name,
            },
            sort=[("timestamp", -1)],
        )

        if doc:
            return doc["timestamp"]
        return None

    async def check_data_exists(
        self,
        ticker: str,
        indicator_name: str,
        period: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> bool:
        """检查指标数据是否存在.

        Args:
            ticker: 股票代码
            indicator_name: 指标名称
            period: 时间周期
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）

        Returns:
            bool: 数据是否存在
        """
        # 构建查询条件
        query: dict[str, Any] = {
            "metadata.ticker": ticker,
            "metadata.period": period,
            "metadata.indicator_name": indicator_name,
        }

        # 时间范围查询
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date

        # 检查是否存在
        count = await self.collection.count_documents(query, limit=1)
        return count > 0

    async def get_statistics(
        self, ticker: Optional[str] = None, indicator_name: Optional[str] = None
    ) -> dict[str, Any]:
        """获取指标数据统计信息.

        Args:
            ticker: 股票代码（可选）
            indicator_name: 指标名称（可选）

        Returns:
            dict: 统计信息
        """
        # 构建查询条件
        query: dict[str, Any] = {}
        if ticker:
            query["metadata.ticker"] = ticker
        if indicator_name:
            query["metadata.indicator_name"] = indicator_name

        # 获取总数
        total_count = await self.collection.count_documents(query)

        # 获取时间范围
        start_date = None
        end_date = None
        if total_count > 0:
            # 最早日期
            earliest_doc = await self.collection.find_one(
                query, sort=[("timestamp", 1)]
            )
            if earliest_doc:
                start_date = earliest_doc["timestamp"]

            # 最新日期
            latest_doc = await self.collection.find_one(query, sort=[("timestamp", -1)])
            if latest_doc:
                end_date = latest_doc["timestamp"]

        return {
            "ticker": ticker,
            "indicator_name": indicator_name,
            "total_count": total_count,
            "start_date": start_date,
            "end_date": end_date,
        }
