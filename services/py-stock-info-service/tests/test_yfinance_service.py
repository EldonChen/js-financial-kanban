"""yfinance 服务测试."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.yfinance_service import (
    fetch_stock_info,
    transform_stock_info,
    fetch_stock_info_async,
    fetch_multiple_stocks,
    get_all_tickers_from_yahoo,
    fetch_all_stocks_from_yahoo,
)


class TestFetchStockInfo:
    """测试 fetch_stock_info 函数."""

    @patch("app.services.yfinance_service.yf")
    def test_fetch_stock_info_success(self, mock_yf):
        """测试成功抓取股票信息."""
        # Mock yfinance 返回的数据
        mock_ticker = Mock()
        mock_ticker.info = {
            "symbol": "AAPL",
            "longName": "Apple Inc.",
            "exchange": "NMS",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "currency": "USD",
            "country": "United States",
        }
        mock_yf.Ticker.return_value = mock_ticker

        result = fetch_stock_info("AAPL")

        assert result is not None
        assert result["ticker"] == "AAPL"
        assert result["name"] == "Apple Inc."
        assert result["market"] == "NMS"
        assert result["sector"] == "Technology"
        assert result["data_source"] == "yfinance"

    @patch("app.services.yfinance_service.yf")
    def test_fetch_stock_info_no_symbol(self, mock_yf):
        """测试股票信息中没有 symbol 字段."""
        mock_ticker = Mock()
        mock_ticker.info = {"name": "Test"}
        mock_yf.Ticker.return_value = mock_ticker

        result = fetch_stock_info("INVALID")

        assert result is None

    @patch("app.services.yfinance_service.yf")
    def test_fetch_stock_info_exception(self, mock_yf):
        """测试抓取股票信息时发生异常."""
        mock_yf.Ticker.side_effect = Exception("Network error")

        result = fetch_stock_info("AAPL")

        assert result is None


class TestTransformStockInfo:
    """测试 transform_stock_info 函数."""

    def test_transform_stock_info_complete(self):
        """测试完整数据转换."""
        info = {
            "symbol": "AAPL",
            "longName": "Apple Inc.",
            "exchange": "NMS",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "currency": "USD",
            "country": "United States",
        }

        result = transform_stock_info(info)

        assert result["ticker"] == "AAPL"
        assert result["name"] == "Apple Inc."
        assert result["market"] == "NMS"
        assert result["sector"] == "Technology"
        assert result["data_source"] == "yfinance"

    def test_transform_stock_info_short_name(self):
        """测试使用 shortName 作为名称."""
        info = {
            "symbol": "AAPL",
            "shortName": "Apple",
            "exchange": "NMS",
        }

        result = transform_stock_info(info)

        assert result["name"] == "Apple"

    def test_transform_stock_info_empty_fields(self):
        """测试空字段处理."""
        info = {
            "symbol": "AAPL",
            "longName": "Apple Inc.",
            "exchange": "",
            "sector": "",
        }

        result = transform_stock_info(info)

        assert result["exchange"] is None
        assert result["sector"] is None
        assert result["market"] is None


class TestFetchStockInfoAsync:
    """测试 fetch_stock_info_async 函数."""

    @pytest.mark.asyncio
    @patch("app.services.yfinance_service.fetch_stock_info")
    async def test_fetch_stock_info_async_success(self, mock_fetch):
        """测试异步抓取成功."""
        mock_fetch.return_value = {
            "ticker": "AAPL",
            "name": "Apple Inc.",
        }

        result = await fetch_stock_info_async("AAPL")

        assert result is not None
        assert result["ticker"] == "AAPL"
        mock_fetch.assert_called_once_with("AAPL")

    @pytest.mark.asyncio
    @patch("app.services.yfinance_service.fetch_stock_info")
    @patch("app.services.yfinance_service.asyncio.sleep")
    async def test_fetch_stock_info_async_retry(self, mock_sleep, mock_fetch):
        """测试异步抓取重试机制."""
        # 前两次返回 None，第三次成功
        mock_fetch.side_effect = [None, None, {"ticker": "AAPL", "name": "Apple Inc."}]

        result = await fetch_stock_info_async("AAPL", retry_count=3)

        assert result is not None
        assert mock_fetch.call_count == 3
        assert mock_sleep.call_count == 2  # 重试了2次

    @pytest.mark.asyncio
    @patch("app.services.yfinance_service.fetch_stock_info")
    async def test_fetch_stock_info_async_all_failed(self, mock_fetch):
        """测试异步抓取全部失败."""
        mock_fetch.return_value = None

        result = await fetch_stock_info_async("INVALID", retry_count=2)

        assert result is None
        assert mock_fetch.call_count == 2


class TestFetchMultipleStocks:
    """测试 fetch_multiple_stocks 函数."""

    @pytest.mark.asyncio
    @patch("app.services.yfinance_service.yf.Tickers")
    @patch("app.services.yfinance_service.asyncio.sleep")
    async def test_fetch_multiple_stocks_success(self, mock_sleep, mock_tickers_class):
        """测试批量抓取成功."""
        # Mock Tickers 对象
        mock_tickers_obj = Mock()
        
        # Mock 每个 Ticker 对象
        mock_aapl = Mock()
        mock_aapl.info = {
            "symbol": "AAPL",
            "longName": "Apple Inc.",
            "exchange": "NMS",
            "sector": "Technology",
            "currency": "USD",
        }
        
        mock_googl = Mock()
        mock_googl.info = {
            "symbol": "GOOGL",
            "longName": "Google",
            "exchange": "NMS",
            "sector": "Technology",
            "currency": "USD",
        }
        
        mock_msft = Mock()
        mock_msft.info = {}  # 空信息，模拟失败
        
        # 设置 tickers 字典
        mock_tickers_obj.tickers = {
            "AAPL": mock_aapl,
            "GOOGL": mock_googl,
            "MSFT": mock_msft,
        }
        
        # Mock Tickers 类返回对象
        mock_tickers_class.return_value = mock_tickers_obj

        result = await fetch_multiple_stocks(["AAPL", "GOOGL", "MSFT"], delay=0.1)

        assert len(result) == 3
        assert result["AAPL"] is not None
        assert result["AAPL"]["ticker"] == "AAPL"
        assert result["GOOGL"] is not None
        assert result["GOOGL"]["ticker"] == "GOOGL"
        assert result["MSFT"] is None  # 空信息应该返回 None
        assert mock_tickers_class.call_count == 1  # 只调用一次批量获取
        assert mock_sleep.call_count == 0  # 只有一批，不需要延迟


class TestGetAllTickersFromYahoo:
    """测试 get_all_tickers_from_yahoo 函数."""

    @patch("app.services.yfinance_service._get_sp500_tickers")
    @patch("app.services.yfinance_service._get_nasdaq_tickers")
    @patch("app.services.yfinance_service._scrape_yahoo_tickers")
    def test_get_all_tickers_success(
        self, mock_scrape, mock_nasdaq, mock_sp500
    ):
        """测试获取所有股票代码成功."""
        mock_sp500.return_value = ["AAPL", "MSFT", "GOOGL"]
        mock_nasdaq.return_value = ["AAPL", "AMZN", "TSLA"]
        mock_scrape.return_value = ["NVDA", "META"]

        result = get_all_tickers_from_yahoo()

        assert len(result) > 0
        assert "AAPL" in result
        assert "MSFT" in result
        assert "GOOGL" in result
        # 应该去重
        assert result.count("AAPL") == 1

    @patch("app.services.yfinance_service._get_sp500_tickers")
    @patch("app.services.yfinance_service._get_nasdaq_tickers")
    @patch("app.services.yfinance_service._scrape_yahoo_tickers")
    def test_get_all_tickers_partial_failure(
        self, mock_scrape, mock_nasdaq, mock_sp500
    ):
        """测试部分方法失败时仍能获取部分数据."""
        mock_sp500.return_value = ["AAPL", "MSFT"]
        mock_nasdaq.side_effect = Exception("Network error")
        mock_scrape.return_value = []

        result = get_all_tickers_from_yahoo()

        assert len(result) >= 2
        assert "AAPL" in result
        assert "MSFT" in result


class TestFetchAllStocksFromYahoo:
    """测试 fetch_all_stocks_from_yahoo 函数."""

    @pytest.mark.asyncio
    @patch("app.services.yfinance_service.get_all_tickers_from_yahoo")
    @patch("app.services.yfinance_service.fetch_multiple_stocks")
    async def test_fetch_all_stocks_success(self, mock_fetch_multiple, mock_get_tickers):
        """测试抓取所有股票成功."""
        mock_get_tickers.return_value = ["AAPL", "GOOGL", "MSFT"]
        mock_fetch_multiple.return_value = {
            "AAPL": {"ticker": "AAPL", "name": "Apple Inc."},
            "GOOGL": {"ticker": "GOOGL", "name": "Google"},
            "MSFT": None,  # 一个失败
        }

        result = await fetch_all_stocks_from_yahoo()

        assert result["total"] == 3
        assert result["success"] == 2
        assert result["failed"] == 1
        assert "AAPL" in result["tickers"]
        assert "results" in result

    @pytest.mark.asyncio
    @patch("app.services.yfinance_service.get_all_tickers_from_yahoo")
    async def test_fetch_all_stocks_no_tickers(self, mock_get_tickers):
        """测试没有获取到股票代码."""
        mock_get_tickers.return_value = []

        result = await fetch_all_stocks_from_yahoo()

        assert result["total"] == 0
        assert result["success"] == 0
        assert result["failed"] == 0
