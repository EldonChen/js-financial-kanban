"""历史K线数据获取服务（从数据源获取数据）."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import yfinance as yf
import akshare as ak
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database

logger = logging.getLogger(__name__)


class HistoricalDataFetcher:
    """历史K线数据获取服务."""
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        """初始化数据获取服务.
        
        Args:
            db: MongoDB 数据库实例（可选）
        """
        self.db = db if db is not None else get_database()
    
    async def fetch_from_yfinance(
        self,
        ticker: str,
        period: str = "1d",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """从 yfinance 获取历史K线数据（美股/港股）.
        
        Args:
            ticker: 股票代码
            period: 时间周期（1m, 5m, 15m, 30m, 60m, 1d, 1w, 1M）
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[Dict]: K线数据列表
        """
        try:
            logger.info(f"从 yfinance 获取 {ticker} 的历史数据，周期: {period}")
            
            # 创建 Ticker 对象
            stock = yf.Ticker(ticker)
            
            # 转换周期格式（yfinance 使用不同的周期格式）
            interval_map = {
                "1m": "1m",
                "5m": "5m",
                "15m": "15m",
                "30m": "30m",
                "60m": "60m",
                "1d": "1d",
                "1w": "1wk",
                "1M": "1mo"
            }
            yf_interval = interval_map.get(period, "1d")
            
            # 获取历史数据
            if start_date and end_date:
                df = stock.history(
                    start=start_date,
                    end=end_date,
                    interval=yf_interval
                )
            else:
                # 默认获取最近 1 年数据
                df = stock.history(period="1y", interval=yf_interval)
            
            # 如果没有数据，返回空列表
            if df.empty:
                logger.warning(f"yfinance 未返回 {ticker} 的数据")
                return []
            
            # 转换为字典列表
            kline_data = []
            for timestamp, row in df.iterrows():
                data = {
                    "timestamp": timestamp.to_pydatetime(),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                    "adj_close": float(row["Close"])  # yfinance 默认返回复权价格
                }
                kline_data.append(data)
            
            logger.info(f"成功获取 {ticker} 的 {len(kline_data)} 条数据")
            return kline_data
            
        except Exception as e:
            logger.error(f"从 yfinance 获取 {ticker} 数据失败: {str(e)}")
            return []
    
    async def fetch_from_akshare(
        self,
        ticker: str,
        period: str = "daily",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """从 akshare 获取历史K线数据（A股）.
        
        Args:
            ticker: 股票代码（如 000001.SZ, 600000.SH）
            period: 时间周期（daily, weekly, monthly）
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[Dict]: K线数据列表
        """
        try:
            logger.info(f"从 akshare 获取 {ticker} 的历史数据，周期: {period}")
            
            # 提取股票代码（akshare 使用纯数字代码）
            symbol = ticker.split(".")[0] if "." in ticker else ticker
            
            # 格式化日期（akshare 使用 YYYYMMDD 格式）
            start_str = start_date.strftime("%Y%m%d") if start_date else "19900101"
            end_str = end_date.strftime("%Y%m%d") if end_date else datetime.now().strftime("%Y%m%d")
            
            # 获取历史数据
            if period == "daily":
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period="daily",
                    start_date=start_str,
                    end_date=end_str,
                    adjust="qfq"  # 前复权
                )
            elif period == "weekly":
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period="weekly",
                    start_date=start_str,
                    end_date=end_str,
                    adjust="qfq"
                )
            elif period == "monthly":
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period="monthly",
                    start_date=start_str,
                    end_date=end_str,
                    adjust="qfq"
                )
            else:
                logger.error(f"不支持的周期: {period}")
                return []
            
            # 如果没有数据，返回空列表
            if df.empty:
                logger.warning(f"akshare 未返回 {ticker} 的数据")
                return []
            
            # 转换为字典列表（akshare 列名是中文）
            kline_data = []
            for _, row in df.iterrows():
                # 解析日期
                date_str = str(row["日期"])
                timestamp = datetime.strptime(date_str, "%Y-%m-%d")
                
                data = {
                    "timestamp": timestamp,
                    "open": float(row["开盘"]),
                    "high": float(row["最高"]),
                    "low": float(row["最低"]),
                    "close": float(row["收盘"]),
                    "volume": int(row["成交量"]),
                    "amount": float(row["成交额"]) if "成交额" in row else None,
                    "adj_close": float(row["收盘"])  # akshare 默认返回复权价格
                }
                kline_data.append(data)
            
            logger.info(f"成功获取 {ticker} 的 {len(kline_data)} 条数据")
            return kline_data
            
        except Exception as e:
            logger.error(f"从 akshare 获取 {ticker} 数据失败: {str(e)}")
            return []
    
    async def fetch_kline_data(
        self,
        ticker: str,
        market: str,
        period: str = "1d",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        data_source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取历史K线数据（自动选择数据源）.
        
        Args:
            ticker: 股票代码
            market: 市场（如 NASDAQ, A股）
            period: 时间周期
            start_date: 开始日期
            end_date: 结束日期
            data_source: 数据源（yfinance, akshare），如果不指定则自动选择
            
        Returns:
            List[Dict]: K线数据列表
        """
        # 自动选择数据源
        if data_source is None:
            if market in ["A股", "深圳", "上海"]:
                data_source = "akshare"
            else:
                data_source = "yfinance"
        
        # 根据数据源获取数据
        if data_source == "yfinance":
            return await self.fetch_from_yfinance(ticker, period, start_date, end_date)
        elif data_source == "akshare":
            # 转换周期格式
            period_map = {
                "1d": "daily",
                "1w": "weekly",
                "1M": "monthly"
            }
            ak_period = period_map.get(period, "daily")
            return await self.fetch_from_akshare(ticker, ak_period, start_date, end_date)
        else:
            logger.error(f"不支持的数据源: {data_source}")
            return []
