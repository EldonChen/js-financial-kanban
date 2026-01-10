"""数据源路由器."""

import logging
from typing import Optional, Dict, Any, List
from app.services.providers.base import StockDataProvider

logger = logging.getLogger(__name__)


class StockDataRouter:
    """数据源路由器，负责选择合适的数据源.
    
    根据市场类型和数据源优先级，自动选择合适的数据源。
    支持容错机制：主数据源失败时自动切换到备用数据源。
    """

    def __init__(self):
        """初始化路由器."""
        self.providers: Dict[str, StockDataProvider] = {}
        # 市场 -> 数据源列表（按优先级排序）
        self.market_providers: Dict[str, List[str]] = {}

    def register_provider(self, provider: StockDataProvider):
        """注册数据源.
        
        Args:
            provider: 数据源提供者实例
        """
        provider_name = provider.name
        self.providers[provider_name] = provider

        # 更新市场映射
        for market in provider.supported_markets:
            if market not in self.market_providers:
                self.market_providers[market] = []

            # 按优先级插入（优先级小的在前）
            provider_list = self.market_providers[market]
            inserted = False
            for idx, existing_name in enumerate(provider_list):
                existing_provider = self.providers[existing_name]
                if provider.priority < existing_provider.priority:
                    provider_list.insert(idx, provider_name)
                    inserted = True
                    break
                elif provider.priority == existing_provider.priority:
                    # 相同优先级，按注册顺序（后注册的排在后面）
                    continue

            if not inserted:
                provider_list.append(provider_name)

        logger.info(
            f"注册数据源: {provider_name} (优先级: {provider.priority}, "
            f"支持市场: {provider.supported_markets})"
        )

    async def fetch_stock_info(
        self,
        ticker: str,
        market: Optional[str] = None,
        preferred_provider: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """获取股票信息（带容错）.
        
        按优先级尝试多个数据源，直到成功或所有数据源都失败。
        
        Args:
            ticker: 股票代码
            market: 市场类型（可选）
            preferred_provider: 首选数据源名称（可选）
        
        Returns:
            股票信息字典，如果所有数据源都失败返回 None
        """
        # 1. 如果指定了首选数据源，先尝试
        if preferred_provider and preferred_provider in self.providers:
            provider = self.providers[preferred_provider]
            if await provider.is_available() and provider.supports_market(market):
                try:
                    result = await provider.fetch_stock_info(ticker, market)
                    if result:
                        logger.info(
                            f"从首选数据源 {preferred_provider} 获取股票 {ticker} 成功"
                        )
                        return result
                except Exception as e:
                    logger.warning(
                        f"首选数据源 {preferred_provider} 获取股票 {ticker} 失败: {e}"
                    )

        # 2. 根据市场选择数据源列表
        if market:
            provider_names = self.market_providers.get(market, [])
            # 如果市场没有映射，尝试所有数据源
            if not provider_names:
                provider_names = list(self.providers.keys())
        else:
            # 如果没有指定市场，尝试所有数据源
            provider_names = list(self.providers.keys())

        # 3. 按优先级尝试
        for provider_name in provider_names:
            # 跳过已经尝试过的首选数据源
            if provider_name == preferred_provider:
                continue

            provider = self.providers[provider_name]

            # 检查数据源是否可用
            if not await provider.is_available():
                logger.debug(f"数据源 {provider_name} 不可用，跳过")
                continue

            # 检查是否支持指定市场
            if not provider.supports_market(market):
                logger.debug(
                    f"数据源 {provider_name} 不支持市场 {market}，跳过"
                )
                continue

            try:
                result = await provider.fetch_stock_info(ticker, market)
                if result:
                    logger.info(
                        f"从数据源 {provider_name} 获取股票 {ticker} 成功"
                    )
                    return result
            except Exception as e:
                logger.warning(
                    f"数据源 {provider_name} 获取股票 {ticker} 失败: {e}"
                )
                continue

        logger.error(
            f"所有数据源都失败，无法获取股票 {ticker} (市场: {market})"
        )
        return None

    async def fetch_all_tickers(
        self,
        market: Optional[str] = None,
        preferred_provider: Optional[str] = None,
    ) -> List[str]:
        """获取所有股票代码列表（带容错）.
        
        Args:
            market: 市场类型（可选）
            preferred_provider: 首选数据源名称（可选）
        
        Returns:
            股票代码列表
        """
        # 1. 如果指定了首选数据源，先尝试
        if preferred_provider and preferred_provider in self.providers:
            provider = self.providers[preferred_provider]
            if await provider.is_available() and provider.supports_market(market):
                try:
                    result = await provider.fetch_all_tickers(market)
                    if result:
                        logger.info(
                            f"从首选数据源 {preferred_provider} 获取股票列表成功 "
                            f"(市场: {market}, 数量: {len(result)})"
                        )
                        return result
                except Exception as e:
                    logger.warning(
                        f"首选数据源 {preferred_provider} 获取股票列表失败: {e}"
                    )

        # 2. 根据市场选择数据源列表
        if market:
            provider_names = self.market_providers.get(market, [])
            if not provider_names:
                provider_names = list(self.providers.keys())
        else:
            provider_names = list(self.providers.keys())

        # 3. 按优先级尝试
        for provider_name in provider_names:
            if provider_name == preferred_provider:
                continue

            provider = self.providers[provider_name]

            if not await provider.is_available():
                logger.debug(f"数据源 {provider_name} 不可用，跳过")
                continue

            if not provider.supports_market(market):
                logger.debug(
                    f"数据源 {provider_name} 不支持市场 {market}，跳过"
                )
                continue

            try:
                result = await provider.fetch_all_tickers(market)
                if result:
                    logger.info(
                        f"从数据源 {provider_name} 获取股票列表成功 "
                        f"(市场: {market}, 数量: {len(result)})"
                    )
                    return result
            except Exception as e:
                logger.warning(
                    f"数据源 {provider_name} 获取股票列表失败: {e}"
                )
                continue

        logger.error(
            f"所有数据源都失败，无法获取股票列表 (市场: {market})"
        )
        return []

    async def fetch_multiple_stocks(
        self,
        tickers: List[str],
        market: Optional[str] = None,
        preferred_provider: Optional[str] = None,
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """批量获取多个股票信息（带容错，优先使用批量查询）.
        
        优先使用数据源的批量查询方法（如果支持），否则回退到逐个查询。
        
        Args:
            tickers: 股票代码列表
            market: 市场类型（可选）
            preferred_provider: 首选数据源名称（可选）
        
        Returns:
            字典，key 为 ticker，value 为股票信息或 None
        """
        if not tickers:
            return {}

        # 1. 如果指定了首选数据源，先尝试批量查询
        if preferred_provider and preferred_provider in self.providers:
            provider = self.providers[preferred_provider]
            if await provider.is_available() and provider.supports_market(market):
                try:
                    result = await provider.fetch_multiple_stocks(tickers, market)
                    if result and any(v is not None for v in result.values()):
                        logger.info(
                            f"从首选数据源 {preferred_provider} 批量获取股票信息成功 "
                            f"(市场: {market}, 数量: {len([v for v in result.values() if v])}/{len(tickers)})"
                        )
                        return result
                except Exception as e:
                    logger.warning(
                        f"首选数据源 {preferred_provider} 批量获取股票信息失败: {e}"
                    )

        # 2. 根据市场选择数据源列表
        if market:
            provider_names = self.market_providers.get(market, [])
            if not provider_names:
                provider_names = list(self.providers.keys())
        else:
            provider_names = list(self.providers.keys())

        # 3. 按优先级尝试批量查询
        for provider_name in provider_names:
            if provider_name == preferred_provider:
                continue

            provider = self.providers[provider_name]

            if not await provider.is_available():
                logger.debug(f"数据源 {provider_name} 不可用，跳过")
                continue

            if not provider.supports_market(market):
                logger.debug(
                    f"数据源 {provider_name} 不支持市场 {market}，跳过"
                )
                continue

            try:
                result = await provider.fetch_multiple_stocks(tickers, market)
                if result and any(v is not None for v in result.values()):
                    logger.info(
                        f"从数据源 {provider_name} 批量获取股票信息成功 "
                        f"(市场: {market}, 数量: {len([v for v in result.values() if v])}/{len(tickers)})"
                    )
                    return result
            except Exception as e:
                logger.warning(
                    f"数据源 {provider_name} 批量获取股票信息失败: {e}"
                )
                continue

        # 4. 如果所有批量查询都失败，回退到逐个查询
        logger.warning("所有数据源的批量查询都失败，回退到逐个查询模式")
        results = {}
        for ticker in tickers:
            stock_data = await self.fetch_stock_info(ticker, market=market)
            results[ticker] = stock_data
        return results

    def get_providers_for_market(
        self, market: Optional[str] = None
    ) -> List[str]:
        """获取指定市场的数据源列表（按优先级排序）.
        
        Args:
            market: 市场类型（可选）
        
        Returns:
            数据源名称列表
        """
        if market:
            return self.market_providers.get(market, [])
        return list(self.providers.keys())


# 全局路由器实例
_stock_data_router: Optional[StockDataRouter] = None


def get_stock_data_router() -> StockDataRouter:
    """获取全局数据源路由器实例.
    
    Returns:
        数据源路由器实例
    """
    global _stock_data_router
    if _stock_data_router is None:
        _stock_data_router = StockDataRouter()
    return _stock_data_router
