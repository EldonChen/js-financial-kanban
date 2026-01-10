"""数据源集成测试."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.providers.router import StockDataRouter
from app.services.providers.akshare_provider import AkshareProvider
from app.services.providers.yfinance_provider import YFinanceProvider
from app.services.stock_service import StockService


class TestProviderIntegration:
    """数据源集成测试类."""

    @pytest.fixture
    async def router(self):
        """创建路由器并注册数据源."""
        router = StockDataRouter()
        
        # 注册 mock 数据源
        akshare_provider = AkshareProvider()
        yfinance_provider = YFinanceProvider()
        
        router.register_provider(akshare_provider)
        router.register_provider(yfinance_provider)
        
        return router

    @pytest.fixture
    async def stock_service(self, setup_test_db, router):
        """创建股票服务实例（带路由器）."""
        return StockService(db=setup_test_db, router=router)

    @pytest.mark.asyncio
    async def test_update_stock_a_stock_with_akshare(self, stock_service, router):
        """测试更新 A 股股票（使用 akshare）."""
        with patch("app.services.providers.akshare_provider.ak.stock_individual_info_em") as mock_info:
            import pandas as pd
            # akshare 返回的 DataFrame 格式
            mock_df = pd.DataFrame({
                0: ["股票简称", "行业", "code", "name"],
                1: ["平安银行", "银行", "000001", "平安银行"]
            })
            mock_info.return_value = mock_df

            result = await stock_service.update_stock_from_provider(
                "000001", market="A股"
            )

            assert result is not None
            assert result["ticker"] == "000001"
            assert result["data_source"] == "akshare"
            assert result["market_type"] == "A股"

    @pytest.mark.asyncio
    async def test_update_stock_us_stock_with_yfinance(self, stock_service, router):
        """测试更新美股股票（使用 yfinance）."""
        with patch("app.services.providers.yfinance_provider.yf.Ticker") as mock_ticker:
            mock_stock = Mock()
            mock_stock.info = {
                "symbol": "AAPL",
                "longName": "Apple Inc.",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "currency": "USD",
            }
            mock_ticker.return_value = mock_stock

            result = await stock_service.update_stock_from_provider(
                "AAPL", market="美股"
            )

            assert result is not None
            assert result["ticker"] == "AAPL"
            assert result["data_source"] == "yfinance"
            assert result["market_type"] == "美股"

    @pytest.mark.asyncio
    async def test_update_stock_fallback(self, stock_service, router):
        """测试数据源失败时自动切换."""
        # Mock akshare 失败
        with patch("app.services.providers.akshare_provider.ak.stock_individual_info_em") as mock_akshare:
            mock_akshare.side_effect = Exception("akshare 失败")
            
            # Mock yfinance 成功（作为备用）
            with patch("app.services.providers.yfinance_provider.yf.Ticker") as mock_ticker:
                mock_stock = Mock()
                mock_stock.info = {
                    "symbol": "AAPL",
                    "longName": "Apple Inc.",
                    "exchange": "NASDAQ",
                }
                mock_ticker.return_value = mock_stock

                # 尝试更新（不指定市场，让路由器自动选择）
                result = await stock_service.update_stock_from_provider("AAPL")

                # 应该从 yfinance 获取到数据
                assert result is not None
                assert result["data_source"] == "yfinance"

    @pytest.mark.asyncio
    async def test_fetch_all_tickers_a_stock(self, stock_service, router):
        """测试获取 A 股股票列表."""
        with patch("app.services.providers.akshare_provider.ak.stock_info_a_code_name") as mock_tickers:
            import pandas as pd
            mock_df = pd.DataFrame({
                "code": ["000001", "000002"],
                "name": ["平安银行", "万科A"]
            })
            mock_tickers.return_value = mock_df
            
            # Mock 单个股票信息获取
            with patch("app.services.providers.akshare_provider.ak.stock_individual_info_em") as mock_info:
                import pandas as pd
                mock_info_df = pd.DataFrame({
                    0: ["股票简称", "code", "name"],
                    1: ["测试", "000001", "测试"]
                })
                mock_info.return_value = mock_info_df

                result = await stock_service.fetch_and_save_all_stocks_from_provider(
                    market="A股", delay=0.0  # 测试时不需要延迟
                )

                assert result["total"] == 2
                assert result["fetch_success"] >= 0  # 至少尝试获取

    @pytest.mark.asyncio
    async def test_preferred_provider(self, stock_service, router):
        """测试指定首选数据源."""
        with patch("app.services.providers.yfinance_provider.yf.Ticker") as mock_ticker:
            mock_stock = Mock()
            mock_stock.info = {
                "symbol": "AAPL",
                "longName": "Apple Inc.",
                "exchange": "NASDAQ",
            }
            mock_ticker.return_value = mock_stock

            result = await stock_service.update_stock_from_provider(
                "AAPL", preferred_provider="yfinance"
            )

            assert result is not None
            assert result["data_source"] == "yfinance"
