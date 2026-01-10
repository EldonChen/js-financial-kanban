"""数据源提供者抽象基类."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class StockDataProvider(ABC):
    """股票数据提供者抽象基类.
    
    所有数据源适配器必须实现此接口。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """数据源名称.
        
        Returns:
            数据源名称，如 'akshare', 'yfinance', 'tushare' 等
        """
        pass

    @property
    @abstractmethod
    def supported_markets(self) -> List[str]:
        """支持的市场列表.
        
        Returns:
            支持的市场列表，如 ['A股', '港股', '美股']
        """
        pass

    @property
    def priority(self) -> int:
        """数据源优先级.
        
        数字越小优先级越高。
        - 1: 第一优先级（免费优先、无需认证）
        - 2: 第二优先级（需要注册 API Key，存在限制）
        
        Returns:
            优先级数字
        """
        return 1  # 默认第一优先级

    @abstractmethod
    async def fetch_stock_info(
        self, ticker: str, market: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """获取单个股票信息.
        
        Args:
            ticker: 股票代码
            market: 市场类型（可选，用于区分不同市场的相同代码）
        
        Returns:
            股票信息字典，如果失败返回 None
            字典应包含以下字段（至少包含 ticker 和 name）：
            - ticker: 股票代码
            - name: 股票名称
            - market: 市场
            - market_type: 市场类型（A股、港股、美股等）
            - sector: 行业板块
            - industry: 细分行业
            - currency: 货币
            - exchange: 交易所代码
            - country: 国家
            - data_source: 数据来源（自动设置为数据源名称）
            - 其他可选字段...
        """
        pass

    @abstractmethod
    async def fetch_all_tickers(
        self, market: Optional[str] = None
    ) -> List[str]:
        """获取所有股票代码列表.
        
        Args:
            market: 市场类型（可选）
        
        Returns:
            股票代码列表
        """
        pass

    async def fetch_multiple_stocks(
        self, tickers: List[str], market: Optional[str] = None
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """批量获取多个股票信息（可选实现）.
        
        如果数据源支持批量查询，可以实现此方法以提高性能。
        如果不支持，可以回退到逐个查询。
        
        Args:
            tickers: 股票代码列表
            market: 市场类型（可选）
        
        Returns:
            字典，key 为 ticker，value 为股票信息或 None
        """
        # 默认实现：逐个查询
        results = {}
        for ticker in tickers:
            result = await self.fetch_stock_info(ticker, market)
            results[ticker] = result
        return results

    async def is_available(self) -> bool:
        """检查数据源是否可用.
        
        默认实现返回 True。子类可以重写此方法以实现更复杂的可用性检查。
        
        Returns:
            是否可用
        """
        return True

    def supports_market(self, market: Optional[str] = None) -> bool:
        """检查是否支持指定市场.
        
        Args:
            market: 市场类型（可选）
        
        Returns:
            是否支持
        """
        if market is None:
            return True
        return market in self.supported_markets
