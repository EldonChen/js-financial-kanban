"""数据完整性检查服务."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class CompletenessChecker:
    """数据完整性检查服务."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """初始化完整性检查服务.
        
        Args:
            db: MongoDB 数据库实例
        """
        self.db = db
        self.collection = db["kline_data"]
    
    async def check_missing_data(
        self,
        ticker: str,
        period: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[datetime]:
        """检查缺失数据（返回缺失的日期列表）.
        
        Args:
            ticker: 股票代码
            period: 时间周期
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[datetime]: 缺失的日期列表
        """
        logger.info(f"检查 {ticker} 的数据完整性（{start_date} - {end_date}）")
        
        # 查询已有数据的日期列表
        cursor = self.collection.find(
            {
                "metadata.ticker": ticker,
                "metadata.period": period,
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            },
            {"timestamp": 1}
        ).sort("timestamp", 1)
        
        existing_dates = set()
        async for doc in cursor:
            existing_dates.add(doc["timestamp"].date())
        
        # 生成预期的日期范围（排除周末，如果是日线数据）
        expected_dates = self._generate_expected_dates(start_date, end_date, period)
        
        # 找出缺失的日期
        missing_dates = []
        for date in expected_dates:
            if date not in existing_dates:
                missing_dates.append(datetime.combine(date, datetime.min.time()))
        
        if missing_dates:
            logger.warning(f"{ticker} 缺失 {len(missing_dates)} 个交易日的数据")
        else:
            logger.info(f"{ticker} 数据完整，无缺失")
        
        return missing_dates
    
    def _generate_expected_dates(
        self,
        start_date: datetime,
        end_date: datetime,
        period: str
    ) -> List:
        """生成预期的日期范围.
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            period: 时间周期
            
        Returns:
            List[date]: 预期的日期列表
        """
        expected_dates = []
        current_date = start_date.date()
        end = end_date.date()
        
        # 如果是日线数据，排除周末
        if period == "1d":
            while current_date <= end:
                # 排除周末（周六=5，周日=6）
                if current_date.weekday() < 5:
                    expected_dates.append(current_date)
                current_date += timedelta(days=1)
        else:
            # 其他周期暂不处理，直接返回所有日期
            while current_date <= end:
                expected_dates.append(current_date)
                current_date += timedelta(days=1)
        
        return expected_dates
