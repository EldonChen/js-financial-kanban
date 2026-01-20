"""历史K线数据查询服务（查询数据）."""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.models.kline_data import kline_data_from_dict

logger = logging.getLogger(__name__)


class HistoricalDataQuery:
    """历史K线数据查询服务."""
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        """初始化数据查询服务.
        
        Args:
            db: MongoDB 数据库实例（可选）
        """
        self.db = db if db is not None else get_database()
        self.collection = self.db.kline_data
    
    async def query_by_ticker(
        self,
        ticker: str,
        period: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
        sort_desc: bool = True
    ) -> List[Dict[str, Any]]:
        """按股票代码查询历史K线数据.
        
        Args:
            ticker: 股票代码
            period: 时间周期
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            limit: 返回数量限制（可选）
            sort_desc: 是否按时间降序排序（默认 True）
            
        Returns:
            List[Dict]: K线数据列表
        """
        try:
            logger.info(f"查询 {ticker} 的历史数据，周期: {period}")
            
            # 构建查询条件
            query = {
                "metadata.ticker": ticker,
                "metadata.period": period
            }
            
            # 添加时间范围条件
            if start_date or end_date:
                time_query = {}
                if start_date:
                    time_query["$gte"] = start_date
                if end_date:
                    time_query["$lte"] = end_date
                query["timestamp"] = time_query
            
            # 执行查询
            cursor = self.collection.find(query)
            
            # 排序
            if sort_desc:
                cursor = cursor.sort("timestamp", -1)
            else:
                cursor = cursor.sort("timestamp", 1)
            
            # 限制数量
            if limit:
                cursor = cursor.limit(limit)
            
            # 获取结果
            documents = await cursor.to_list(length=None)
            
            # 转换格式
            kline_data = [kline_data_from_dict(doc) for doc in documents]
            
            logger.info(f"查询到 {ticker} 的 {len(kline_data)} 条数据")
            return kline_data
            
        except Exception as e:
            logger.error(f"查询 {ticker} 数据失败: {str(e)}")
            return []
    
    async def get_latest_date(
        self,
        ticker: str,
        period: str
    ) -> Optional[datetime]:
        """获取指定股票的最新数据日期.
        
        Args:
            ticker: 股票代码
            period: 时间周期
            
        Returns:
            Optional[datetime]: 最新数据日期，如果没有数据则返回 None
        """
        try:
            logger.info(f"查询 {ticker} 的最新数据日期")
            
            # 查询最新一条数据
            document = await self.collection.find_one(
                {
                    "metadata.ticker": ticker,
                    "metadata.period": period
                },
                sort=[("timestamp", -1)]
            )
            
            if document:
                latest_date = document["timestamp"]
                logger.info(f"{ticker} 的最新数据日期: {latest_date}")
                return latest_date
            else:
                logger.info(f"{ticker} 没有历史数据")
                return None
                
        except Exception as e:
            logger.error(f"查询 {ticker} 最新数据日期失败: {str(e)}")
            return None
    
    async def get_date_range(
        self,
        ticker: str,
        period: str
    ) -> Optional[Dict[str, datetime]]:
        """获取指定股票的数据日期范围.
        
        Args:
            ticker: 股票代码
            period: 时间周期
            
        Returns:
            Optional[Dict]: {"start_date": 最早日期, "end_date": 最晚日期}
        """
        try:
            logger.info(f"查询 {ticker} 的数据日期范围")
            
            query = {
                "metadata.ticker": ticker,
                "metadata.period": period
            }
            
            # 查询最早数据
            earliest = await self.collection.find_one(
                query,
                sort=[("timestamp", 1)]
            )
            
            # 查询最晚数据
            latest = await self.collection.find_one(
                query,
                sort=[("timestamp", -1)]
            )
            
            if earliest and latest:
                date_range = {
                    "start_date": earliest["timestamp"],
                    "end_date": latest["timestamp"]
                }
                logger.info(f"{ticker} 的数据日期范围: {date_range}")
                return date_range
            else:
                logger.info(f"{ticker} 没有历史数据")
                return None
                
        except Exception as e:
            logger.error(f"查询 {ticker} 数据日期范围失败: {str(e)}")
            return None
    
    async def get_statistics(
        self,
        ticker: Optional[str] = None,
        period: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取历史K线数据统计信息.
        
        Args:
            ticker: 股票代码（可选，不提供则返回所有股票的统计）
            period: 时间周期（可选）
            
        Returns:
            Dict: 统计信息
        """
        try:
            logger.info(f"查询历史数据统计，ticker: {ticker}, period: {period}")
            
            # 构建查询条件
            query = {}
            if ticker:
                query["metadata.ticker"] = ticker
            if period:
                query["metadata.period"] = period
            
            # 查询总数
            total_count = await self.collection.count_documents(query)
            
            # 如果指定了 ticker，查询日期范围
            date_range = None
            if ticker and period:
                date_range = await self.get_date_range(ticker, period)
            
            statistics = {
                "total_count": total_count,
                "query": {
                    "ticker": ticker,
                    "period": period
                }
            }
            
            if date_range:
                statistics["start_date"] = date_range["start_date"]
                statistics["end_date"] = date_range["end_date"]
            
            logger.info(f"统计信息: {statistics}")
            return statistics
            
        except Exception as e:
            logger.error(f"查询统计信息失败: {str(e)}")
            return {
                "total_count": 0,
                "error": str(e)
            }
    
    async def check_data_exists(
        self,
        ticker: str,
        period: str,
        start_date: datetime,
        end_date: datetime
    ) -> bool:
        """检查指定时间范围内是否有数据.
        
        Args:
            ticker: 股票代码
            period: 时间周期
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            bool: 是否有数据
        """
        try:
            count = await self.collection.count_documents({
                "metadata.ticker": ticker,
                "metadata.period": period,
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            })
            return count > 0
        except Exception as e:
            logger.error(f"检查数据是否存在失败: {str(e)}")
            return False
