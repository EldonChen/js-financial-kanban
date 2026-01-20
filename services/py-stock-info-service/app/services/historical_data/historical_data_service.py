"""历史K线数据核心服务（协调各个子服务）."""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.services.historical_data.historical_data_fetcher import HistoricalDataFetcher
from app.services.historical_data.historical_data_storage import HistoricalDataStorage
from app.services.historical_data.historical_data_query import HistoricalDataQuery

logger = logging.getLogger(__name__)


class HistoricalDataService:
    """历史K线数据核心服务."""
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        """初始化历史数据服务.
        
        Args:
            db: MongoDB 数据库实例（可选）
        """
        self.db = db if db is not None else get_database()
        self.fetcher = HistoricalDataFetcher(self.db)
        self.storage = HistoricalDataStorage(self.db)
        self.query = HistoricalDataQuery(self.db)
    
    async def fetch_kline_data(
        self,
        ticker: str,
        market: str,
        period: str = "1d",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        data_source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取单只股票的历史K线数据.
        
        Args:
            ticker: 股票代码
            market: 市场
            period: 时间周期
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            data_source: 数据源（可选，自动选择）
            
        Returns:
            List[Dict]: K线数据列表
        """
        logger.info(f"开始获取 {ticker} 的历史K线数据")
        
        # 从数据源获取数据
        kline_data = await self.fetcher.fetch_kline_data(
            ticker, market, period, start_date, end_date, data_source
        )
        
        return kline_data
    
    async def fetch_and_save_kline_data(
        self,
        ticker: str,
        market: str,
        period: str = "1d",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        data_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取并保存单只股票的历史K线数据.
        
        Args:
            ticker: 股票代码
            market: 市场
            period: 时间周期
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            data_source: 数据源（可选）
            
        Returns:
            Dict: {"ticker": 股票代码, "saved": 保存条数, "updated": 更新条数}
        """
        logger.info(f"开始获取并保存 {ticker} 的历史K线数据")
        
        # 获取数据
        kline_data = await self.fetch_kline_data(
            ticker, market, period, start_date, end_date, data_source
        )
        
        if not kline_data:
            logger.warning(f"{ticker} 没有获取到数据")
            return {"ticker": ticker, "inserted": 0, "updated": 0}
        
        # 保存数据（使用 upsert 避免重复）
        result = await self.storage.upsert_kline_data(
            ticker, market, period, kline_data, data_source or "yfinance"
        )
        
        logger.info(f"{ticker} 数据保存完成: 插入 {result['inserted']}, 更新 {result['updated']}")
        return {
            "ticker": ticker,
            "inserted": result["inserted"],
            "updated": result["updated"]
        }
    
    async def query_kline_data(
        self,
        ticker: str,
        period: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """查询历史K线数据.
        
        Args:
            ticker: 股票代码
            period: 时间周期
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            limit: 返回数量限制（可选）
            
        Returns:
            List[Dict]: K线数据列表
        """
        logger.info(f"查询 {ticker} 的历史K线数据")
        
        kline_data = await self.query.query_by_ticker(
            ticker, period, start_date, end_date, limit
        )
        
        return kline_data
    
    async def update_kline_data_incremental(
        self,
        ticker: str,
        market: str,
        period: str = "1d",
        data_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """增量更新历史K线数据（只更新缺失的数据）.
        
        Args:
            ticker: 股票代码
            market: 市场
            period: 时间周期
            data_source: 数据源（可选）
            
        Returns:
            Dict: {"ticker": 股票代码, "inserted": 插入条数, "updated": 更新条数}
        """
        logger.info(f"开始增量更新 {ticker} 的历史K线数据")
        
        # 查询最新数据日期
        latest_date = await self.query.get_latest_date(ticker, period)
        
        # 如果没有历史数据，获取最近 1 年数据
        if latest_date is None:
            logger.info(f"{ticker} 没有历史数据，获取最近 1 年数据")
            start_date = datetime.now() - timedelta(days=365)
            end_date = datetime.now()
        else:
            # 获取从最新日期到当前日期的数据
            start_date = latest_date + timedelta(days=1)
            end_date = datetime.now()
            
            # 如果已经是最新数据，无需更新
            if start_date >= end_date:
                logger.info(f"{ticker} 数据已是最新，无需更新")
                return {"ticker": ticker, "inserted": 0, "updated": 0}
            
            logger.info(f"{ticker} 增量更新从 {start_date} 到 {end_date}")
        
        # 获取并保存数据
        result = await self.fetch_and_save_kline_data(
            ticker, market, period, start_date, end_date, data_source
        )
        
        return result
    
    async def delete_kline_data(
        self,
        ticker: Optional[str] = None,
        period: Optional[str] = None,
        before_date: Optional[datetime] = None
    ) -> int:
        """删除历史K线数据.
        
        Args:
            ticker: 股票代码（可选）
            period: 时间周期（可选）
            before_date: 删除指定日期之前的数据（可选）
            
        Returns:
            int: 删除的数据条数
        """
        logger.info(f"删除历史K线数据，ticker: {ticker}, period: {period}, before_date: {before_date}")
        
        deleted_count = await self.storage.delete_kline_data(ticker, period, before_date)
        
        return deleted_count
    
    async def get_kline_data_statistics(
        self,
        ticker: Optional[str] = None,
        period: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取历史K线数据统计信息.
        
        Args:
            ticker: 股票代码（可选）
            period: 时间周期（可选）
            
        Returns:
            Dict: 统计信息
        """
        logger.info(f"获取历史K线数据统计，ticker: {ticker}, period: {period}")
        
        statistics = await self.query.get_statistics(ticker, period)
        
        return statistics
    
    async def fetch_batch_kline_data(
        self,
        tickers: List[str],
        markets: Dict[str, str],
        period: str = "1d",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """批量获取股票的历史K线数据（支持 SSE 进度推送）.
        
        Args:
            tickers: 股票代码列表
            markets: 股票市场映射（{ticker: market}）
            period: 时间周期
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            progress_callback: 进度回调函数（可选）
            
        Returns:
            Dict: {"total": 总数, "success": 成功数, "failed": 失败数, "results": [结果列表]}
        """
        logger.info(f"批量获取 {len(tickers)} 只股票的历史K线数据")
        
        total = len(tickers)
        success_count = 0
        failed_count = 0
        results = []
        
        # 发送初始化进度
        if progress_callback:
            await progress_callback({
                "stage": "init",
                "message": f"开始批量获取历史K线数据...",
                "progress": 0,
                "total": total
            })
        
        # 遍历股票列表
        for idx, ticker in enumerate(tickers):
            try:
                market = markets.get(ticker, "NASDAQ")
                
                # 发送进度更新
                if progress_callback:
                    await progress_callback({
                        "stage": "fetching",
                        "message": f"正在获取 {ticker} 的数据... ({idx + 1}/{total})",
                        "progress": int((idx + 1) / total * 100),
                        "total": total,
                        "current": idx + 1,
                        "ticker": ticker
                    })
                
                # 获取并保存数据
                result = await self.fetch_and_save_kline_data(
                    ticker, market, period, start_date, end_date
                )
                
                if result["inserted"] > 0 or result["updated"] > 0:
                    success_count += 1
                    results.append({
                        "ticker": ticker,
                        "status": "success",
                        "inserted": result["inserted"],
                        "updated": result["updated"]
                    })
                else:
                    failed_count += 1
                    results.append({
                        "ticker": ticker,
                        "status": "failed",
                        "error": "未获取到数据"
                    })
                
                # 添加延迟，避免请求过快
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"批量获取 {ticker} 数据失败: {str(e)}")
                failed_count += 1
                results.append({
                    "ticker": ticker,
                    "status": "failed",
                    "error": str(e)
                })
        
        # 发送完成通知
        if progress_callback:
            await progress_callback({
                "stage": "completed",
                "message": f"批量获取完成：总数 {total}，成功 {success_count}，失败 {failed_count}",
                "progress": 100,
                "result": {
                    "total": total,
                    "success": success_count,
                    "failed": failed_count
                }
            })
        
        return {
            "total": total,
            "success": success_count,
            "failed": failed_count,
            "results": results
        }
