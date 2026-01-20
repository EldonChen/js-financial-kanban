"""技术指标存储服务."""

import logging
from datetime import datetime, UTC
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import UpdateOne

from app.database import get_database
from app.models.indicator_data import prepare_indicator_document

logger = logging.getLogger(__name__)


class IndicatorStorage:
    """技术指标存储服务（保存指标数据到MongoDB）."""

    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        """初始化指标存储服务.

        Args:
            db: MongoDB 数据库对象（可选）
        """
        self.db = db if db is not None else get_database()
        self.collection = self.db.indicator_data

    async def save_indicator_data(
        self,
        ticker: str,
        period: str,
        indicator_type: str,
        indicator_name: str,
        indicator_data: list[dict[str, Any]],
    ) -> int:
        """保存技术指标数据到数据库（批量插入）.

        Args:
            ticker: 股票代码
            period: 时间周期
            indicator_type: 指标类型（MA, EMA, RSI, MACD, BOLL）
            indicator_name: 指标名称（MA5, MA10, RSI14等）
            indicator_data: 指标数据列表

        Returns:
            int: 保存的记录数量
        """
        if not indicator_data:
            return 0

        # 准备文档数据
        documents = []
        for data in indicator_data:
            document = {
                "timestamp": data["timestamp"],
                "metadata": {
                    "ticker": ticker,
                    "period": period,
                    "indicator_type": indicator_type,
                    "indicator_name": indicator_name,
                },
                "value": data["value"],
                "params": data.get("params"),
            }
            documents.append(document)

        try:
            # 批量插入
            result = await self.collection.insert_many(documents, ordered=False)
            inserted_count = len(result.inserted_ids)
            logger.info(
                f"保存指标数据成功：{ticker} {indicator_name} {period} - {inserted_count} 条"
            )
            return inserted_count
        except Exception as e:
            # 如果部分插入失败（如重复数据），仍然返回成功插入的数量
            logger.warning(f"保存指标数据部分失败：{ticker} {indicator_name} - {e}")
            return 0

    async def upsert_indicator_data(
        self,
        ticker: str,
        period: str,
        indicator_type: str,
        indicator_name: str,
        indicator_data: list[dict[str, Any]],
    ) -> dict[str, int]:
        """保存或更新技术指标数据（使用 upsert，避免重复）.

        Args:
            ticker: 股票代码
            period: 时间周期
            indicator_type: 指标类型
            indicator_name: 指标名称
            indicator_data: 指标数据列表

        Returns:
            dict: {"inserted": 插入数量, "updated": 更新数量}
        """
        if not indicator_data:
            return {"inserted": 0, "updated": 0}

        # 准备 bulk_write 操作
        operations = []
        for data in indicator_data:
            document = {
                "timestamp": data["timestamp"],
                "metadata": {
                    "ticker": ticker,
                    "period": period,
                    "indicator_type": indicator_type,
                    "indicator_name": indicator_name,
                },
                "value": data["value"],
                "params": data.get("params"),
            }

            # 使用 UpdateOne 进行 upsert
            operations.append(
                UpdateOne(
                    {
                        "timestamp": document["timestamp"],
                        "metadata.ticker": ticker,
                        "metadata.period": period,
                        "metadata.indicator_name": indicator_name,
                    },
                    {"$set": document},
                    upsert=True,
                )
            )

        try:
            # 批量 upsert
            result = await self.collection.bulk_write(operations, ordered=False)
            inserted_count = result.upserted_count
            updated_count = result.modified_count
            logger.info(
                f"Upsert 指标数据成功：{ticker} {indicator_name} {period} - 插入 {inserted_count} 条，更新 {updated_count} 条"
            )
            return {"inserted": inserted_count, "updated": updated_count}
        except Exception as e:
            logger.error(f"Upsert 指标数据失败：{ticker} {indicator_name} - {e}")
            raise

    async def delete_indicator_data(
        self,
        ticker: Optional[str] = None,
        period: Optional[str] = None,
        indicator_name: Optional[str] = None,
        before_date: Optional[datetime] = None,
    ) -> int:
        """删除技术指标数据.

        Args:
            ticker: 股票代码（可选）
            period: 时间周期（可选）
            indicator_name: 指标名称（可选）
            before_date: 删除指定日期之前的数据（可选）

        Returns:
            int: 删除的记录数量
        """
        # 构建查询条件
        query: dict[str, Any] = {}

        if ticker:
            query["metadata.ticker"] = ticker
        if period:
            query["metadata.period"] = period
        if indicator_name:
            query["metadata.indicator_name"] = indicator_name
        if before_date:
            query["timestamp"] = {"$lt": before_date}

        # 如果没有任何条件，拒绝删除（防止误操作）
        if not query:
            logger.warning("删除指标数据：未提供任何条件，拒绝删除全部数据")
            return 0

        # 执行删除
        result = await self.collection.delete_many(query)
        deleted_count = result.deleted_count
        logger.info(
            f"删除指标数据成功：{ticker or '全部'} {indicator_name or '全部'} {period or '全部'} - {deleted_count} 条"
        )
        return deleted_count
