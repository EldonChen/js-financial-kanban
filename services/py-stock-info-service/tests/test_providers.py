"""数据源提供者测试."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.providers.akshare_provider import AkshareProvider
from app.services.providers.yfinance_provider import YFinanceProvider
from app.services.providers.easyquotation_provider import EasyQuotationProvider


class TestAkshareProvider:
    """AkshareProvider 测试类."""

    @pytest.fixture
    def provider(self):
        """创建 AkshareProvider 实例."""
        return AkshareProvider()

    def test_name(self, provider):
        """测试数据源名称."""
        assert provider.name == "akshare"

    def test_supported_markets(self, provider):
        """测试支持的市场."""
        assert "A股" in provider.supported_markets
        assert "港股" in provider.supported_markets
        assert "美股" in provider.supported_markets

    def test_priority(self, provider):
        """测试优先级."""
        assert provider.priority == 1  # 第一优先级

    def test_supports_market(self, provider):
        """测试市场支持检查."""
        assert provider.supports_market("A股") is True
        assert provider.supports_market("港股") is True
        assert provider.supports_market("美股") is True
        assert provider.supports_market(None) is True
        assert provider.supports_market("未知市场") is False

    @pytest.mark.asyncio
    async def test_fetch_stock_info_a_stock(self, provider):
        """测试获取 A 股股票信息."""
        with patch("app.services.providers.akshare_provider.ak.stock_individual_info_em") as mock_info:
            # Mock akshare 返回的数据
            import pandas as pd
            # akshare 返回的 DataFrame 格式：两列，第一列是字段名，第二列是值
            mock_df = pd.DataFrame({
                0: ["股票简称", "行业", "地区", "code", "name"],
                1: ["平安银行", "银行", "深圳", "000001", "平安银行"]
            })
            mock_info.return_value = mock_df

            result = await provider.fetch_stock_info("000001", market="A股")

            assert result is not None
            assert result["ticker"] == "000001"
            assert result["data_source"] == "akshare"
            assert result["market_type"] == "A股"

    @pytest.mark.asyncio
    async def test_fetch_stock_info_failed(self, provider):
        """测试获取股票信息失败."""
        with patch("app.services.providers.akshare_provider.ak.stock_individual_info_em") as mock_info:
            mock_info.side_effect = Exception("网络错误")

            result = await provider.fetch_stock_info("000001")

            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_all_tickers_a_stock(self, provider):
        """测试获取 A 股股票列表."""
        with patch("app.services.providers.akshare_provider.ak.stock_info_a_code_name") as mock_tickers:
            import pandas as pd
            mock_df = pd.DataFrame({
                "code": ["000001", "000002", "600000"],
                "name": ["平安银行", "万科A", "浦发银行"]
            })
            mock_tickers.return_value = mock_df

            result = await provider.fetch_all_tickers(market="A股")

            assert len(result) == 3
            assert "000001" in result
            assert "000002" in result
            assert "600000" in result

    @pytest.mark.asyncio
    async def test_is_available(self, provider):
        """测试可用性检查."""
        with patch("app.services.providers.akshare_provider.ak.stock_info_a_code_name") as mock_tickers:
            import pandas as pd
            mock_df = pd.DataFrame({"code": ["000001"], "name": ["测试"]})
            mock_tickers.return_value = mock_df

            result = await provider.is_available()

            assert result is True


class TestYFinanceProvider:
    """YFinanceProvider 测试类."""

    @pytest.fixture
    def provider(self):
        """创建 YFinanceProvider 实例."""
        return YFinanceProvider()

    def test_name(self, provider):
        """测试数据源名称."""
        assert provider.name == "yfinance"

    def test_supported_markets(self, provider):
        """测试支持的市场."""
        assert "美股" in provider.supported_markets
        assert "港股" in provider.supported_markets
        assert "A股" not in provider.supported_markets

    def test_priority(self, provider):
        """测试优先级."""
        assert provider.priority == 1  # 第一优先级

    @pytest.mark.asyncio
    async def test_fetch_stock_info_success(self, provider):
        """测试获取股票信息成功."""
        with patch("app.services.providers.yfinance_provider.yf.Ticker") as mock_ticker:
            mock_stock = Mock()
            mock_stock.info = {
                "symbol": "AAPL",
                "longName": "Apple Inc.",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "currency": "USD",
                "country": "United States",
            }
            mock_ticker.return_value = mock_stock

            result = await provider.fetch_stock_info("AAPL")

            assert result is not None
            assert result["ticker"] == "AAPL"
            assert result["name"] == "Apple Inc."
            assert result["data_source"] == "yfinance"
            assert result["market_type"] == "美股"

    @pytest.mark.asyncio
    async def test_fetch_stock_info_failed(self, provider):
        """测试获取股票信息失败."""
        with patch("app.services.providers.yfinance_provider.yf.Ticker") as mock_ticker:
            mock_ticker.side_effect = Exception("网络错误")

            result = await provider.fetch_stock_info("INVALID")

            assert result is None

    @pytest.mark.asyncio
    async def test_is_available(self, provider):
        """测试可用性检查."""
        with patch("app.services.providers.yfinance_provider.yf.Ticker") as mock_ticker:
            mock_stock = Mock()
            mock_stock.info = {"symbol": "AAPL"}
            mock_ticker.return_value = mock_stock

            result = await provider.is_available()

            assert result is True


class TestEasyQuotationProvider:
    """EasyQuotationProvider 测试类."""

    @pytest.fixture
    def provider(self):
        """创建 EasyQuotationProvider 实例."""
        with patch("easyquotation.use") as mock_use:
            mock_quotation = Mock()
            mock_use.return_value = mock_quotation
            provider = EasyQuotationProvider()
            provider.quotation = mock_quotation
            return provider

    def test_name(self, provider):
        """测试数据源名称."""
        assert provider.name == "easyquotation"

    def test_supported_markets(self, provider):
        """测试支持的市场."""
        assert "A股" in provider.supported_markets
        assert len(provider.supported_markets) == 1

    def test_priority(self, provider):
        """测试优先级."""
        assert provider.priority == 1  # 第一优先级

    @pytest.mark.asyncio
    async def test_fetch_stock_info_success(self, provider):
        """测试获取股票信息成功."""
        provider.quotation.real.return_value = {
            "000001": {
                "name": "平安银行",
                "now": 12.34,
                "open": 12.00,
                "close": 12.50,
            }
        }

        result = await provider.fetch_stock_info("000001")

        assert result is not None
        assert result["ticker"] == "000001"
        assert result["name"] == "平安银行"
        assert result["data_source"] == "easyquotation"
        assert result["market_type"] == "A股"

    @pytest.mark.asyncio
    async def test_fetch_stock_info_failed(self, provider):
        """测试获取股票信息失败."""
        provider.quotation.real.return_value = {}

        result = await provider.fetch_stock_info("000001")

        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_all_tickers_not_supported(self, provider):
        """测试获取股票列表（不支持）."""
        result = await provider.fetch_all_tickers()

        assert result == []

    @pytest.mark.asyncio
    async def test_is_available(self, provider):
        """测试可用性检查."""
        provider.quotation.real.return_value = {
            "000001": {"name": "平安银行"}
        }

        result = await provider.is_available()

        assert result is True
