"""数据质量核心服务（协调各个子服务）."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.services.data_quality.completeness_checker import CompletenessChecker
from app.services.data_quality.accuracy_checker import AccuracyChecker
from app.services.data_quality.consistency_checker import ConsistencyChecker
from app.services.data_quality.data_fixer import DataFixer

logger = logging.getLogger(__name__)


class DataQualityService:
    """数据质量核心服务."""
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        """初始化数据质量服务.
        
        Args:
            db: MongoDB 数据库实例（可选）
        """
        self.db = db if db is not None else get_database()
        self.completeness_checker = CompletenessChecker(self.db)
        self.accuracy_checker = AccuracyChecker(self.db)
        self.consistency_checker = ConsistencyChecker(self.db)
        self.data_fixer = DataFixer(self.db)
    
    async def check_data_completeness(
        self,
        ticker: str,
        period: str = "1d",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """检查数据完整性（缺失数据检测）.
        
        Args:
            ticker: 股票代码
            period: 时间周期
            start_date: 开始日期（可选，默认最近 1 年）
            end_date: 结束日期（可选，默认今天）
            
        Returns:
            Dict: 检查结果
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        if end_date is None:
            end_date = datetime.now()
        
        logger.info(f"检查 {ticker} 的数据完整性")
        
        missing_dates = await self.completeness_checker.check_missing_data(
            ticker, period, start_date, end_date
        )
        
        return {
            "ticker": ticker,
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "status": "passed" if len(missing_dates) == 0 else "failed",
            "missing_count": len(missing_dates),
            "missing_dates": missing_dates[:20] if len(missing_dates) > 20 else missing_dates
        }
    
    async def check_data_accuracy(
        self,
        ticker: str,
        period: str = "1d",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """检查数据准确性（异常值检测、价格合理性检查）.
        
        Args:
            ticker: 股票代码
            period: 时间周期
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            
        Returns:
            Dict: 检查结果
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        if end_date is None:
            end_date = datetime.now()
        
        logger.info(f"检查 {ticker} 的数据准确性")
        
        # 检查异常值
        abnormal_values = await self.accuracy_checker.check_abnormal_values(
            ticker, period, start_date, end_date
        )
        
        # 检查价格合理性
        unreasonable_prices = await self.accuracy_checker.check_price_reasonableness(
            ticker, period, start_date, end_date
        )
        
        total_issues = len(abnormal_values) + len(unreasonable_prices)
        
        return {
            "ticker": ticker,
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "status": "passed" if total_issues == 0 else "failed",
            "abnormal_count": len(abnormal_values),
            "unreasonable_count": len(unreasonable_prices),
            "abnormal_values": abnormal_values[:10] if len(abnormal_values) > 10 else abnormal_values,
            "unreasonable_prices": unreasonable_prices[:10] if len(unreasonable_prices) > 10 else unreasonable_prices
        }
    
    async def check_data_consistency(
        self,
        ticker: str,
        period: str = "1d",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """检查数据一致性（价格逻辑检查）.
        
        Args:
            ticker: 股票代码
            period: 时间周期
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            
        Returns:
            Dict: 检查结果
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        if end_date is None:
            end_date = datetime.now()
        
        logger.info(f"检查 {ticker} 的数据一致性")
        
        inconsistent_data = await self.consistency_checker.check_price_logic(
            ticker, period, start_date, end_date
        )
        
        return {
            "ticker": ticker,
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "status": "passed" if len(inconsistent_data) == 0 else "failed",
            "inconsistent_count": len(inconsistent_data),
            "inconsistent_data": inconsistent_data[:10] if len(inconsistent_data) > 10 else inconsistent_data
        }
    
    async def check_duplicate_data(
        self,
        ticker: str,
        period: str = "1d"
    ) -> Dict[str, Any]:
        """检查重复数据.
        
        Args:
            ticker: 股票代码
            period: 时间周期
            
        Returns:
            Dict: 检查结果
        """
        logger.info(f"检查 {ticker} 的重复数据")
        
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
                    "count": {"$sum": 1}
                }
            },
            {
                "$match": {
                    "count": {"$gt": 1}
                }
            }
        ]
        
        duplicate_count = 0
        async for doc in self.db["kline_data"].aggregate(pipeline):
            duplicate_count += doc["count"] - 1
        
        return {
            "ticker": ticker,
            "period": period,
            "status": "passed" if duplicate_count == 0 else "failed",
            "duplicate_count": duplicate_count
        }
    
    async def fix_missing_data(
        self,
        ticker: str,
        market: str,
        period: str = "1d",
        missing_dates: Optional[list] = None
    ) -> Dict[str, Any]:
        """自动修复缺失数据.
        
        Args:
            ticker: 股票代码
            market: 市场
            period: 时间周期
            missing_dates: 缺失的日期列表（可选）
            
        Returns:
            Dict: 修复结果
        """
        logger.info(f"修复 {ticker} 的缺失数据")
        
        result = await self.data_fixer.fix_missing_data(
            ticker, market, period, missing_dates or []
        )
        
        return result
    
    async def run_quality_check(
        self,
        ticker: str,
        period: str = "1d",
        auto_fix: bool = False
    ) -> Dict[str, Any]:
        """运行完整的数据质量检查.
        
        Args:
            ticker: 股票代码
            period: 时间周期
            auto_fix: 是否自动修复数据问题
            
        Returns:
            Dict: 完整的检查结果
        """
        logger.info(f"开始对 {ticker} 进行完整的数据质量检查")
        
        # 执行所有检查
        completeness_result = await self.check_data_completeness(ticker, period)
        accuracy_result = await self.check_data_accuracy(ticker, period)
        consistency_result = await self.check_data_consistency(ticker, period)
        duplicate_result = await self.check_duplicate_data(ticker, period)
        
        # 如果需要自动修复
        fix_results = {}
        if auto_fix:
            logger.info(f"自动修复 {ticker} 的数据问题")
            
            # 修复重复数据
            if duplicate_result["status"] == "failed":
                fix_results["duplicate"] = await self.data_fixer.fix_duplicate_data(ticker, period)
        
        return {
            "ticker": ticker,
            "period": period,
            "completeness": completeness_result,
            "accuracy": accuracy_result,
            "consistency": consistency_result,
            "duplicate": duplicate_result,
            "fix_results": fix_results if auto_fix else None
        }
