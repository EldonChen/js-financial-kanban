"""历史K线数据存储服务（保存数据到MongoDB）."""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import UpdateOne

from app.database import get_database
from app.models.kline_data import prepare_kline_document, validate_kline_data

logger = logging.getLogger(__name__)


class HistoricalDataStorage:
    """历史K线数据存储服务."""
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        """初始化数据存储服务.
        
        Args:
            db: MongoDB 数据库实例（可选）
        """
        self.db = db if db is not None else get_database()
        self.collection = self.db.kline_data
    
    async def save_kline_data(
        self,
        ticker: str,
        market: str,
        period: str,
        kline_data: List[Dict[str, Any]],
        data_source: str = "yfinance"
    ) -> int:
        """保存历史K线数据到数据库（批量插入）.
        
        Args:
            ticker: 股票代码
            market: 市场
            period: 时间周期
            kline_data: K线数据列表
            data_source: 数据来源
            
        Returns:
            int: 插入的数据条数
        """
        if not kline_data:
            logger.warning(f"没有数据可保存：{ticker}")
            return 0
        
        try:
            logger.info(f"开始保存 {ticker} 的 {len(kline_data)} 条数据到数据库")
            
            # 准备文档
            documents = []
            for data in kline_data:
                # 验证数据
                if not validate_kline_data(data):
                    logger.warning(f"数据验证失败，跳过: {data}")
                    continue
                
                # 准备文档
                doc = prepare_kline_document(ticker, market, period, data, data_source)
                documents.append(doc)
            
            if not documents:
                logger.warning(f"没有有效数据可保存：{ticker}")
                return 0
            
            # 批量插入
            result = await self.collection.insert_many(documents, ordered=False)
            inserted_count = len(result.inserted_ids)
            
            logger.info(f"成功保存 {ticker} 的 {inserted_count} 条数据")
            return inserted_count
            
        except Exception as e:
            logger.error(f"保存 {ticker} 数据失败: {str(e)}")
            return 0
    
    async def upsert_kline_data(
        self,
        ticker: str,
        market: str,
        period: str,
        kline_data: List[Dict[str, Any]],
        data_source: str = "yfinance"
    ) -> Dict[str, int]:
        """保存或更新历史K线数据（避免重复数据）.
        
        使用 bulk_write + UpdateOne 实现 upsert，性能更好。
        
        Args:
            ticker: 股票代码
            market: 市场
            period: 时间周期
            kline_data: K线数据列表
            data_source: 数据来源
            
        Returns:
            Dict[str, int]: {"inserted": 插入数, "updated": 更新数}
        """
        if not kline_data:
            logger.warning(f"没有数据可保存：{ticker}")
            return {"inserted": 0, "updated": 0}
        
        try:
            logger.info(f"开始 upsert {ticker} 的 {len(kline_data)} 条数据")
            
            # 准备 bulk operations
            operations = []
            for data in kline_data:
                # 验证数据
                if not validate_kline_data(data):
                    logger.warning(f"数据验证失败，跳过: {data}")
                    continue
                
                # 准备文档
                doc = prepare_kline_document(ticker, market, period, data, data_source)
                
                # 创建 upsert 操作
                # 使用 timestamp + metadata 作为唯一键
                filter_query = {
                    "timestamp": doc["timestamp"],
                    "metadata.ticker": ticker,
                    "metadata.period": period
                }
                
                operations.append(
                    UpdateOne(
                        filter_query,
                        {"$set": doc},
                        upsert=True
                    )
                )
            
            if not operations:
                logger.warning(f"没有有效数据可保存：{ticker}")
                return {"inserted": 0, "updated": 0}
            
            # 批量执行
            result = await self.collection.bulk_write(operations, ordered=False)
            
            inserted_count = result.upserted_count
            updated_count = result.modified_count
            
            logger.info(f"成功 upsert {ticker} 的数据: 插入 {inserted_count}, 更新 {updated_count}")
            return {"inserted": inserted_count, "updated": updated_count}
            
        except Exception as e:
            logger.error(f"Upsert {ticker} 数据失败: {str(e)}")
            return {"inserted": 0, "updated": 0}
    
    async def delete_kline_data(
        self,
        ticker: Optional[str] = None,
        period: Optional[str] = None,
        before_date: Optional[datetime] = None
    ) -> int:
        """删除历史K线数据.
        
        Args:
            ticker: 股票代码（可选，不提供则删除所有）
            period: 时间周期（可选）
            before_date: 删除指定日期之前的数据（可选）
            
        Returns:
            int: 删除的数据条数
        """
        try:
            # 构建查询条件
            query = {}
            
            if ticker:
                query["metadata.ticker"] = ticker
            
            if period:
                query["metadata.period"] = period
            
            if before_date:
                query["timestamp"] = {"$lt": before_date}
            
            # 如果没有任何条件，拒绝删除（避免误删除所有数据）
            if not query:
                logger.error("拒绝删除所有数据：必须提供至少一个删除条件")
                return 0
            
            logger.info(f"开始删除数据，条件: {query}")
            
            # 执行删除
            result = await self.collection.delete_many(query)
            deleted_count = result.deleted_count
            
            logger.info(f"成功删除 {deleted_count} 条数据")
            return deleted_count
            
        except Exception as e:
            logger.error(f"删除数据失败: {str(e)}")
            return 0
