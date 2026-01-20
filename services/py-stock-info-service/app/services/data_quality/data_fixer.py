"""数据修复服务."""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class DataFixer:
    """数据修复服务."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """初始化数据修复服务.
        
        Args:
            db: MongoDB 数据库实例
        """
        self.db = db
        self.collection = db["kline_data"]
    
    async def fix_missing_data(
        self,
        ticker: str,
        market: str,
        period: str,
        missing_dates: List[datetime]
    ) -> Dict[str, Any]:
        """修复缺失数据（从数据源重新获取）.
        
        Args:
            ticker: 股票代码
            market: 市场
            period: 时间周期
            missing_dates: 缺失的日期列表
            
        Returns:
            Dict: {"success": 成功数, "failed": 失败数}
        """
        logger.info(f"开始修复 {ticker} 的缺失数据，共 {len(missing_dates)} 个日期")
        
        success_count = 0
        failed_count = 0
        
        # 注意：这里需要调用 historical_data_service 来重新获取数据
        # 由于避免循环依赖，这里只记录需要修复的数据，实际修复由调用者完成
        logger.info(f"{ticker} 需要修复的日期：{len(missing_dates)} 个")
        
        return {
            "success": success_count,
            "failed": failed_count,
            "missing_dates": missing_dates
        }
    
    async def fix_duplicate_data(
        self,
        ticker: str,
        period: str
    ) -> Dict[str, Any]:
        """修复重复数据（删除重复记录）.
        
        Args:
            ticker: 股票代码
            period: 时间周期
            
        Returns:
            Dict: {"deleted": 删除的重复数据数量}
        """
        logger.info(f"开始修复 {ticker} 的重复数据")
        
        # 查找重复数据
        pipeline = [
            {
                "$match": {
                    "metadata.ticker": ticker,
                    "metadata.period": period
                }
            },
            {
                "$group": {
                    "_id": {
                        "ticker": "$metadata.ticker",
                        "period": "$metadata.period",
                        "timestamp": "$timestamp"
                    },
                    "count": {"$sum": 1},
                    "ids": {"$push": "$_id"}
                }
            },
            {
                "$match": {
                    "count": {"$gt": 1}
                }
            }
        ]
        
        deleted_count = 0
        
        async for doc in self.collection.aggregate(pipeline):
            # 保留第一个，删除其他重复数据
            ids_to_delete = doc["ids"][1:]
            result = await self.collection.delete_many({"_id": {"$in": ids_to_delete}})
            deleted_count += result.deleted_count
        
        if deleted_count > 0:
            logger.info(f"{ticker} 删除了 {deleted_count} 条重复数据")
        else:
            logger.info(f"{ticker} 无重复数据")
        
        return {"deleted": deleted_count}
