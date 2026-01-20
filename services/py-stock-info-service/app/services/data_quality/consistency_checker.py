"""数据一致性检查服务."""

import logging
from datetime import datetime
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class ConsistencyChecker:
    """数据一致性检查服务."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """初始化一致性检查服务.
        
        Args:
            db: MongoDB 数据库实例
        """
        self.db = db
        self.collection = db["kline_data"]
    
    async def check_price_logic(
        self,
        ticker: str,
        period: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """检查价格逻辑一致性（high >= low, high >= open, high >= close 等）.
        
        Args:
            ticker: 股票代码
            period: 时间周期
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[Dict]: 不一致的数据列表
        """
        logger.info(f"检查 {ticker} 的价格逻辑一致性（{start_date} - {end_date}）")
        
        inconsistent_data = []
        
        # 查询数据
        cursor = self.collection.find(
            {
                "metadata.ticker": ticker,
                "metadata.period": period,
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
        ).sort("timestamp", 1)
        
        async for doc in cursor:
            timestamp = doc.get("timestamp")
            open_price = doc.get("open")
            high = doc.get("high")
            low = doc.get("low")
            close_price = doc.get("close")
            volume = doc.get("volume")
            
            # 检查：high >= low
            if high is not None and low is not None and high < low:
                inconsistent_data.append({
                    "ticker": ticker,
                    "timestamp": timestamp,
                    "type": "high_low_inconsistency",
                    "high": high,
                    "low": low,
                    "description": f"最高价 ({high}) < 最低价 ({low})"
                })
            
            # 检查：high >= open
            if high is not None and open_price is not None and high < open_price:
                inconsistent_data.append({
                    "ticker": ticker,
                    "timestamp": timestamp,
                    "type": "high_open_inconsistency",
                    "high": high,
                    "open": open_price,
                    "description": f"最高价 ({high}) < 开盘价 ({open_price})"
                })
            
            # 检查：high >= close
            if high is not None and close_price is not None and high < close_price:
                inconsistent_data.append({
                    "ticker": ticker,
                    "timestamp": timestamp,
                    "type": "high_close_inconsistency",
                    "high": high,
                    "close": close_price,
                    "description": f"最高价 ({high}) < 收盘价 ({close_price})"
                })
            
            # 检查：low <= open
            if low is not None and open_price is not None and low > open_price:
                inconsistent_data.append({
                    "ticker": ticker,
                    "timestamp": timestamp,
                    "type": "low_open_inconsistency",
                    "low": low,
                    "open": open_price,
                    "description": f"最低价 ({low}) > 开盘价 ({open_price})"
                })
            
            # 检查：low <= close
            if low is not None and close_price is not None and low > close_price:
                inconsistent_data.append({
                    "ticker": ticker,
                    "timestamp": timestamp,
                    "type": "low_close_inconsistency",
                    "low": low,
                    "close": close_price,
                    "description": f"最低价 ({low}) > 收盘价 ({close_price})"
                })
            
            # 检查：volume >= 0
            if volume is not None and volume < 0:
                inconsistent_data.append({
                    "ticker": ticker,
                    "timestamp": timestamp,
                    "type": "negative_volume",
                    "volume": volume,
                    "description": f"成交量为负数 ({volume})"
                })
        
        if inconsistent_data:
            logger.warning(f"{ticker} 发现 {len(inconsistent_data)} 个价格逻辑不一致")
        else:
            logger.info(f"{ticker} 价格逻辑一致")
        
        return inconsistent_data
