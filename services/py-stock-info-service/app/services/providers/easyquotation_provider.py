"""easyquotation 数据源提供者."""

import asyncio
import logging
from typing import Optional, Dict, Any, List
import easyquotation
from app.services.providers.base import StockDataProvider
from app.services.providers.field_mapper import FieldMapper

logger = logging.getLogger(__name__)


class EasyQuotationProvider(StockDataProvider):
    """easyquotation 数据源提供者.
    
    支持 A 股实时行情。
    第一优先级：免费优先、无需认证。
    注意：不支持全量股票列表获取，仅用于实时行情补充。
    """

    def __init__(self):
        """初始化 easyquotation 提供者."""
        super().__init__()
        self.quotation = None
        self._init_quotation()

    def _init_quotation(self):
        """初始化 easyquotation 实例."""
        try:
            # 使用新浪财经数据源
            self.quotation = easyquotation.use("sina")
        except Exception as e:
            logger.warning(f"初始化 easyquotation 失败: {e}")
            self.quotation = None

    @property
    def name(self) -> str:
        """数据源名称."""
        return "easyquotation"

    @property
    def supported_markets(self) -> List[str]:
        """支持的市场列表."""
        return ["A股"]

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
        if not self.quotation:
            logger.warning("easyquotation 未初始化")
            return None

        try:
            # 在线程池中执行同步的 easyquotation 调用
            loop = asyncio.get_event_loop()
            stock_data = await loop.run_in_executor(
                None, self._fetch_stock_info_sync, ticker
            )

            if stock_data:
                # 使用字段映射器统一格式
                mapped_data = FieldMapper.map_easyquotation(stock_data, ticker)
                # 清洗字段
                cleaned_data = FieldMapper.clean_fields(mapped_data)
                return cleaned_data

            return None

        except Exception as e:
            logger.error(f"easyquotation 获取股票 {ticker} 信息失败: {e}")
            return None

    async def fetch_all_tickers(
        self, market: Optional[str] = None
    ) -> List[str]:
        """获取所有股票代码列表.
        
        注意：easyquotation 不支持全量股票列表获取。
        需要调用者提供股票代码列表。
        
        Args:
            market: 市场类型（可选）
        
        Returns:
            空列表（不支持全量股票列表）
        """
        logger.warning(
            "easyquotation 不支持全量股票列表获取，需要提供股票代码列表"
        )
        return []

    async def is_available(self) -> bool:
        """检查数据源是否可用."""
        if not self.quotation:
            return False

        try:
            # 尝试获取一个已知股票（000001）的实时行情
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, self._fetch_stock_info_sync, "000001"
            )
            return data is not None
        except Exception as e:
            logger.warning(f"easyquotation 可用性检查失败: {e}")
            return False

    def _fetch_stock_info_sync(self, ticker: str) -> Optional[Dict[str, Any]]:
        """获取股票信息（同步方法）.
        
        Args:
            ticker: 股票代码
        
        Returns:
            股票信息字典
        """
        try:
            if not self.quotation:
                return None

            # 获取实时行情
            data = self.quotation.real([ticker])

            if not data or ticker not in data:
                return None

            return data[ticker]

        except Exception as e:
            logger.error(f"easyquotation 获取股票 {ticker} 信息失败: {e}")
            return None
