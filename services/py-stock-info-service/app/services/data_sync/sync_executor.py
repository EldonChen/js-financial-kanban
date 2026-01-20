"""同步执行器（执行同步任务）."""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class SyncExecutor:
    """同步执行器（执行同步任务）."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """初始化同步执行器.
        
        Args:
            db: MongoDB 数据库实例
        """
        self.db = db
    
    async def sync_daily_data(
        self,
        market: str,
        period: str,
        progress_callback: Optional[Callable]
    ) -> Dict[str, Any]:
        """每日数据同步任务.
        
        Args:
            market: 市场（A股、美股等）
            period: 时间周期
            progress_callback: 进度回调函数（可选）
            
        Returns:
            Dict: 同步结果
        """
        logger.info(f"开始每日数据同步：{market} - {period}")
        
        # 获取该市场的所有股票
        stocks_collection = self.db["stocks"]
        
        tickers = []
        markets = {}
        
        async for stock in stocks_collection.find({"market": market}):
            ticker = stock.get("ticker")
            if ticker:
                tickers.append(ticker)
                markets[ticker] = market
        
        logger.info(f"需要同步 {len(tickers)} 只股票")
        
        # 发送初始化进度
        if progress_callback:
            await progress_callback({
                "stage": "init",
                "message": f"开始同步 {market} 市场数据...",
                "progress": 0,
                "total": len(tickers)
            })
        
        # 这里需要调用 historical_data_service 来批量获取数据
        # 由于避免循环依赖，这里只记录需要同步的股票，实际同步由调用者完成
        logger.info(f"需要同步的股票：{len(tickers)} 只")
        
        return {
            "market": market,
            "period": period,
            "total": len(tickers),
            "tickers": tickers,
            "markets": markets
        }
    
    async def sync_incremental_data(
        self,
        ticker: str,
        market: str,
        period: str,
        data_source: Optional[str]
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
        
        # 这里需要调用 historical_data_service 来增量更新数据
        # 由于避免循环依赖，这里只记录需要更新的股票，实际更新由调用者完成
        logger.info(f"需要增量更新的股票：{ticker}")
        
        return {
            "ticker": ticker,
            "market": market,
            "period": period,
            "data_source": data_source
        }
    
    async def sync_market_data(
        self,
        market: str,
        period: str,
        priority_tickers: Optional[List[str]],
        progress_callback: Optional[Callable]
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
        
        # 获取该市场的所有股票
        stocks_collection = self.db["stocks"]
        
        tickers = []
        markets = {}
        
        # 如果有优先股票列表，先添加优先股票
        if priority_tickers:
            for ticker in priority_tickers:
                tickers.append(ticker)
                markets[ticker] = market
        
        # 添加其他股票
        async for stock in stocks_collection.find({"market": market}):
            ticker = stock.get("ticker")
            if ticker and ticker not in tickers:
                tickers.append(ticker)
                markets[ticker] = market
        
        logger.info(f"需要同步 {len(tickers)} 只股票（优先：{len(priority_tickers or [])} 只）")
        
        # 发送初始化进度
        if progress_callback:
            await progress_callback({
                "stage": "init",
                "message": f"开始同步 {market} 市场数据...",
                "progress": 0,
                "total": len(tickers)
            })
        
        # 这里需要调用 historical_data_service 来批量获取数据
        # 由于避免循环依赖，这里只记录需要同步的股票，实际同步由调用者完成
        logger.info(f"需要同步的股票：{len(tickers)} 只")
        
        return {
            "market": market,
            "period": period,
            "total": len(tickers),
            "priority_count": len(priority_tickers or []),
            "tickers": tickers,
            "markets": markets
        }
