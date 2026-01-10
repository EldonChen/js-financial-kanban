"""yfinance 数据源提供者."""

import asyncio
import logging
from typing import Optional, Dict, Any, List
import yfinance as yf
from app.services.providers.base import StockDataProvider
from app.services.providers.field_mapper import FieldMapper

logger = logging.getLogger(__name__)


class YFinanceProvider(StockDataProvider):
    """yfinance 数据源提供者.
    
    支持美股、港股市场。
    第一优先级：免费优先、无需认证。
    """

    @property
    def name(self) -> str:
        """数据源名称."""
        return "yfinance"

    @property
    def supported_markets(self) -> List[str]:
        """支持的市场列表."""
        return ["美股", "港股"]

    @property
    def priority(self) -> int:
        """数据源优先级：第一优先级."""
        return 1

    async def fetch_stock_info(
        self, ticker: str, market: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """获取单个股票信息.
        
        Args:
            ticker: 股票代码
            market: 市场类型（可选）
        
        Returns:
            股票信息字典，如果失败返回 None
        """
        try:
            # 在线程池中执行同步的 yfinance 调用
            loop = asyncio.get_event_loop()
            stock_data = await loop.run_in_executor(
                None, self._fetch_stock_info_sync, ticker
            )

            if stock_data:
                # 使用字段映射器统一格式
                mapped_data = FieldMapper.map_yfinance(stock_data)
                # 清洗字段
                cleaned_data = FieldMapper.clean_fields(mapped_data)
                return cleaned_data

            return None

        except Exception as e:
            logger.error(f"yfinance 获取股票 {ticker} 信息失败: {e}")
            return None

    async def fetch_all_tickers(
        self, market: Optional[str] = None
    ) -> List[str]:
        """获取所有股票代码列表.
        
        注意：yfinance 本身不直接提供全量股票列表，这里使用多种方式获取。
        
        Args:
            market: 市场类型（可选）
        
        Returns:
            股票代码列表
        """
        try:
            loop = asyncio.get_event_loop()
            
            # 使用多种方式获取股票列表
            tickers = await loop.run_in_executor(
                None, self._get_all_tickers_sync, market
            )
            return tickers

        except Exception as e:
            logger.error(f"yfinance 获取股票列表失败: {e}")
            return []

    async def is_available(self) -> bool:
        """检查数据源是否可用."""
        try:
            # 尝试获取一个已知股票（AAPL）的信息，如果能成功则说明可用
            loop = asyncio.get_event_loop()
            stock_data = await loop.run_in_executor(
                None, self._fetch_stock_info_sync, "AAPL"
            )
            return stock_data is not None
        except Exception as e:
            logger.warning(f"yfinance 可用性检查失败: {e}")
            return False

    def _fetch_stock_info_sync(self, ticker: str) -> Optional[Dict[str, Any]]:
        """获取股票信息（同步方法）.
        
        Args:
            ticker: 股票代码
        
        Returns:
            股票信息字典
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            if not info or "symbol" not in info:
                logger.warning(f"股票 {ticker} 信息不完整或不存在")
                return None

            return info

        except Exception as e:
            logger.error(f"yfinance 获取股票 {ticker} 信息失败: {e}")
            return None

    def _get_all_tickers_sync(
        self, market: Optional[str] = None
    ) -> List[str]:
        """获取所有股票代码列表（同步方法）.
        
        使用多种方式获取股票列表，包括：
        1. 预定义股票列表
        2. Yahoo Finance API 搜索
        3. 页面抓取（如果可用）
        
        Args:
            market: 市场类型（可选）
        
        Returns:
            股票代码列表
        """
        # 导入现有的获取股票列表函数
        from app.services.yfinance_service import get_all_tickers_from_yahoo

        try:
            tickers = get_all_tickers_from_yahoo()
            return tickers
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return []

    async def fetch_multiple_stocks(
        self, tickers: List[str], market: Optional[str] = None
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """批量获取多个股票信息（使用 yfinance Tickers 批量查询）.
        
        yfinance 支持使用 Tickers 类批量查询，比逐个查询快得多。
        
        Args:
            tickers: 股票代码列表
            market: 市场类型（可选）
        
        Returns:
            字典，key 为 ticker，value 为股票信息或 None
        """
        if not tickers:
            return {}

        try:
            loop = asyncio.get_event_loop()
            
            # 使用 yfinance 的 Tickers 类批量查询
            # 将股票代码列表转换为空格分隔的字符串
            ticker_string = " ".join(tickers)
            
            # 在线程池中执行同步的 yfinance 批量调用
            batch_results = await loop.run_in_executor(
                None, self._fetch_multiple_stocks_sync, ticker_string, tickers
            )
            
            # 映射和清洗字段
            results = {}
            for ticker, stock_data in batch_results.items():
                if stock_data:
                    mapped_data = FieldMapper.map_yfinance(stock_data)
                    cleaned_data = FieldMapper.clean_fields(mapped_data)
                    results[ticker] = cleaned_data
                else:
                    results[ticker] = None

            return results

        except Exception as e:
            logger.error(f"yfinance 批量获取股票信息失败: {e}")
            # 回退到逐个查询
            logger.info("回退到逐个查询模式")
            return await super().fetch_multiple_stocks(tickers, market)

    def _fetch_multiple_stocks_sync(
        self, ticker_string: str, tickers: List[str]
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """批量获取股票信息（同步方法）.
        
        使用 yfinance 的 Tickers 类批量查询。
        
        Args:
            ticker_string: 股票代码字符串（空格分隔）
            tickers: 股票代码列表（用于结果映射）
        
        Returns:
            字典，key 为 ticker，value 为股票信息或 None
        """
        results = {}
        
        try:
            # 使用 Tickers 批量创建 Ticker 对象
            tickers_obj = yf.Tickers(ticker_string)
            
            # 遍历每个 Ticker 对象获取信息
            for symbol, ticker_obj in tickers_obj.tickers.items():
                try:
                    info = ticker_obj.info
                    if info and "symbol" in info:
                        results[symbol] = info
                    else:
                        logger.warning(f"股票 {symbol} 信息不完整或不存在")
                        results[symbol] = None
                except Exception as e:
                    logger.error(f"获取股票 {symbol} 信息失败: {e}")
                    results[symbol] = None
            
            # 确保所有 tickers 都在结果中
            for ticker in tickers:
                if ticker not in results:
                    results[ticker] = None
            
            return results

        except Exception as e:
            logger.error(f"yfinance 批量获取股票信息失败: {e}")
            # 回退到逐个查询
            for ticker in tickers:
                results[ticker] = None
            return results
