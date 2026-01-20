"""数据同步核心服务（协调各个子服务）."""

import logging
from typing import Dict, Any, Optional, Callable, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.services.data_sync.sync_scheduler import SyncScheduler
from app.services.data_sync.sync_executor import SyncExecutor
from app.services.historical_data.historical_data_service import HistoricalDataService
from app.services.data_quality.data_quality_service import DataQualityService

logger = logging.getLogger(__name__)


class DataSyncService:
    """数据同步核心服务."""
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        """初始化数据同步服务.
        
        Args:
            db: MongoDB 数据库实例（可选）
        """
        self.db = db if db is not None else get_database()
        self.scheduler = SyncScheduler(self.db)
        self.executor = SyncExecutor(self.db)
        self.historical_data_service = HistoricalDataService(self.db)
        self.data_quality_service = DataQualityService(self.db)
    
    async def sync_daily_data(
        self,
        market: Optional[str] = None,
        period: str = "1d",
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """每日数据同步任务.
        
        Args:
            market: 市场（可选，不提供则同步所有市场）
            period: 时间周期
            progress_callback: 进度回调函数（可选）
            
        Returns:
            Dict: 同步结果
        """
        logger.info(f"开始每日数据同步：{market or '所有市场'} - {period}")
        
        # 执行同步
        result = await self.executor.sync_daily_data(market, period, progress_callback)
        
        # 调用 historical_data_service 批量获取数据
        tickers = result["tickers"]
        markets = result["markets"]
        
        if tickers:
            batch_result = await self.historical_data_service.fetch_batch_kline_data(
                tickers, markets, period, progress_callback=progress_callback
            )
            
            return batch_result
        
        return result
    
    async def sync_incremental_data(
        self,
        ticker: str,
        market: str,
        period: str = "1d",
        data_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """增量数据更新（只更新缺失的数据）.
        
        Args:
            ticker: 股票代码
            market: 市场
            period: 时间周期
            data_source: 数据源（可选）
            
        Returns:
            Dict: 更新结果
        """
        logger.info(f"开始增量更新 {ticker} 的数据")
        
        # 调用 historical_data_service 增量更新数据
        result = await self.historical_data_service.update_kline_data_incremental(
            ticker, market, period, data_source
        )
        
        return result
    
    async def sync_market_data(
        self,
        market: str,
        period: str = "1d",
        priority_tickers: Optional[List[str]] = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """按市场同步数据.
        
        Args:
            market: 市场（A股、美股等）
            period: 时间周期
            priority_tickers: 优先同步的股票代码列表（可选）
            progress_callback: 进度回调函数（可选）
            
        Returns:
            Dict: 同步结果
        """
        logger.info(f"开始按市场同步数据：{market} - {period}")
        
        # 执行同步
        result = await self.executor.sync_market_data(
            market, period, priority_tickers, progress_callback
        )
        
        # 调用 historical_data_service 批量获取数据
        tickers = result["tickers"]
        markets = result["markets"]
        
        if tickers:
            batch_result = await self.historical_data_service.fetch_batch_kline_data(
                tickers, markets, period, progress_callback=progress_callback
            )
            
            return batch_result
        
        return result
    
    def start_scheduler(self):
        """启动定时任务调度器."""
        logger.info("启动定时任务调度器")
        
        # 添加每日同步任务：A股 18:00
        self.scheduler.add_daily_sync_job(
            self.sync_daily_data,
            market="A股",
            hour=18,
            minute=0,
            job_id="daily_sync_a_share"
        )
        
        # 添加每日同步任务：美股 23:00
        self.scheduler.add_daily_sync_job(
            self.sync_daily_data,
            market="美股",
            hour=23,
            minute=0,
            job_id="daily_sync_us_stock"
        )
        
        # 添加每周数据质量检查：周日 23:00
        # 注意：这里需要传递一个 lambda 函数，因为 run_quality_check 需要 ticker 参数
        # 在实际使用中，可能需要遍历所有股票进行质量检查
        
        # 启动调度器
        self.scheduler.start()
        
        logger.info("定时任务调度器已启动")
    
    def shutdown_scheduler(self, wait: bool = True):
        """关闭定时任务调度器.
        
        Args:
            wait: 是否等待所有任务完成
        """
        logger.info("关闭定时任务调度器")
        self.scheduler.shutdown(wait=wait)
        logger.info("定时任务调度器已关闭")
    
    def get_sync_status(self) -> Dict[str, Any]:
        """获取同步状态.
        
        Returns:
            Dict: 同步状态信息
        """
        jobs = self.scheduler.get_jobs()
        
        job_list = []
        for job in jobs:
            job_list.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time,
                "trigger": str(job.trigger)
            })
        
        return {
            "scheduler_running": self.scheduler.scheduler.running,
            "jobs": job_list
        }
