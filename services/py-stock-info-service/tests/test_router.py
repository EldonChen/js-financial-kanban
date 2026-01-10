"""数据源路由器测试."""

import pytest
from unittest.mock import Mock, AsyncMock
from app.services.providers.router import StockDataRouter
from app.services.providers.base import StockDataProvider


class MockProvider(StockDataProvider):
    """Mock 数据源提供者."""

    def __init__(self, name: str, markets: list, priority: int = 1, available: bool = True):
        self._name = name
        self._markets = markets
        self._priority = priority
        self._available = available
        self.fetch_calls = []
        self.fetch_all_calls = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def supported_markets(self) -> list:
        return self._markets

    @property
    def priority(self) -> int:
        return self._priority

    async def fetch_stock_info(self, ticker: str, market: str = None):
        self.fetch_calls.append((ticker, market))
        if not self._available:
            return None
        return {
            "ticker": ticker,
            "name": f"Stock {ticker}",
            "data_source": self._name,
        }

    async def fetch_all_tickers(self, market: str = None):
        self.fetch_all_calls.append(market)
        if not self._available:
            return []
        return [f"{self._name}_ticker1", f"{self._name}_ticker2"]

    async def is_available(self) -> bool:
        return self._available


class TestStockDataRouter:
    """StockDataRouter 测试类."""

    @pytest.fixture
    def router(self):
        """创建路由器实例."""
        return StockDataRouter()

    @pytest.mark.asyncio
    async def test_register_provider(self, router):
        """测试注册数据源."""
        provider = MockProvider("test_provider", ["A股"], priority=1)

        router.register_provider(provider)

        assert "test_provider" in router.providers
        assert router.providers["test_provider"] == provider
        assert "A股" in router.market_providers
        assert "test_provider" in router.market_providers["A股"]

    @pytest.mark.asyncio
    async def test_register_multiple_providers_priority(self, router):
        """测试注册多个数据源，按优先级排序."""
        provider1 = MockProvider("provider1", ["A股"], priority=2)
        provider2 = MockProvider("provider2", ["A股"], priority=1)

        router.register_provider(provider1)
        router.register_provider(provider2)

        # 优先级小的应该排在前面
        assert router.market_providers["A股"][0] == "provider2"
        assert router.market_providers["A股"][1] == "provider1"

    @pytest.mark.asyncio
    async def test_fetch_stock_info_success(self, router):
        """测试获取股票信息成功."""
        provider = MockProvider("test_provider", ["A股"], priority=1)
        router.register_provider(provider)

        result = await router.fetch_stock_info("000001", market="A股")

        assert result is not None
        assert result["ticker"] == "000001"
        assert result["data_source"] == "test_provider"
        assert len(provider.fetch_calls) == 1

    @pytest.mark.asyncio
    async def test_fetch_stock_info_preferred_provider(self, router):
        """测试使用首选数据源."""
        provider1 = MockProvider("provider1", ["A股"], priority=1)
        provider2 = MockProvider("provider2", ["A股"], priority=1)
        router.register_provider(provider1)
        router.register_provider(provider2)

        result = await router.fetch_stock_info(
            "000001", market="A股", preferred_provider="provider2"
        )

        assert result is not None
        assert result["data_source"] == "provider2"
        # 首选数据源应该被调用
        assert len(provider2.fetch_calls) == 1
        # 其他数据源不应该被调用（因为首选数据源成功了）
        assert len(provider1.fetch_calls) == 0

    @pytest.mark.asyncio
    async def test_fetch_stock_info_fallback(self, router):
        """测试数据源失败时自动切换."""
        provider1 = MockProvider("provider1", ["A股"], priority=1, available=False)
        provider2 = MockProvider("provider2", ["A股"], priority=1, available=True)
        router.register_provider(provider1)
        router.register_provider(provider2)

        result = await router.fetch_stock_info("000001", market="A股")

        assert result is not None
        assert result["data_source"] == "provider2"
        # 两个数据源都应该被尝试
        assert len(provider1.fetch_calls) == 0  # provider1 不可用，不会被调用
        assert len(provider2.fetch_calls) == 1

    @pytest.mark.asyncio
    async def test_fetch_stock_info_all_failed(self, router):
        """测试所有数据源都失败."""
        provider1 = MockProvider("provider1", ["A股"], priority=1, available=False)
        provider2 = MockProvider("provider2", ["A股"], priority=1, available=False)
        router.register_provider(provider1)
        router.register_provider(provider2)

        result = await router.fetch_stock_info("000001", market="A股")

        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_all_tickers_success(self, router):
        """测试获取股票列表成功."""
        provider = MockProvider("test_provider", ["A股"], priority=1)
        router.register_provider(provider)

        result = await router.fetch_all_tickers(market="A股")

        assert len(result) == 2
        assert "test_provider_ticker1" in result
        assert "test_provider_ticker2" in result

    @pytest.mark.asyncio
    async def test_fetch_all_tickers_fallback(self, router):
        """测试获取股票列表失败时自动切换."""
        provider1 = MockProvider("provider1", ["A股"], priority=1, available=False)
        provider2 = MockProvider("provider2", ["A股"], priority=1, available=True)
        router.register_provider(provider1)
        router.register_provider(provider2)

        result = await router.fetch_all_tickers(market="A股")

        assert len(result) == 2
        assert "provider2_ticker1" in result

    @pytest.mark.asyncio
    async def test_get_providers_for_market(self, router):
        """测试获取指定市场的数据源列表."""
        provider1 = MockProvider("provider1", ["A股"], priority=1)
        provider2 = MockProvider("provider2", ["A股", "港股"], priority=1)
        provider3 = MockProvider("provider3", ["美股"], priority=1)
        router.register_provider(provider1)
        router.register_provider(provider2)
        router.register_provider(provider3)

        a_stock_providers = router.get_providers_for_market("A股")
        hk_stock_providers = router.get_providers_for_market("港股")
        us_stock_providers = router.get_providers_for_market("美股")

        assert "provider1" in a_stock_providers
        assert "provider2" in a_stock_providers
        assert "provider2" in hk_stock_providers
        assert "provider3" in us_stock_providers
        assert "provider1" not in us_stock_providers
