"""股票服务测试."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, UTC
from app.services.stock_service import StockService
from app.schemas.stock import StockQueryParams


class TestStockService:
    """股票服务测试类."""

    @pytest.fixture
    async def stock_service(self, setup_test_db):
        """创建股票服务实例."""
        return StockService(db=setup_test_db)

    @pytest.mark.asyncio
    async def test_get_stock_by_ticker_success(self, stock_service, sample_stock):
        """测试根据股票代码获取股票信息成功."""
        # 先插入股票
        await stock_service.collection.insert_one(
            {
                **sample_stock,
                "_id": "test_id",
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
                "last_updated": datetime.now(UTC),
            }
        )

        result = await stock_service.get_stock_by_ticker("AAPL")

        assert result is not None
        assert result["ticker"] == "AAPL"
        assert result["name"] == "Apple Inc."
        assert "id" in result

    @pytest.mark.asyncio
    async def test_get_stock_by_ticker_not_found(self, stock_service):
        """测试获取不存在的股票."""
        result = await stock_service.get_stock_by_ticker("INVALID")

        assert result is None

    @pytest.mark.asyncio
    async def test_query_stocks_empty(self, stock_service):
        """测试查询空列表."""
        params = StockQueryParams()
        result = await stock_service.query_stocks(params)

        assert result["total"] == 0
        assert result["items"] == []
        assert result["page"] == 1

    @pytest.mark.asyncio
    async def test_query_stocks_with_filter(self, stock_service, sample_stock):
        """测试带筛选条件的查询."""
        # 插入多个股票
        stocks = [
            {**sample_stock, "ticker": "AAPL", "market": "NASDAQ"},
            {**sample_stock, "ticker": "GOOGL", "market": "NASDAQ"},
            {**sample_stock, "ticker": "MSFT", "market": "NYSE"},
        ]
        for stock in stocks:
            await stock_service.collection.insert_one(
                {
                    **stock,
                    "created_at": datetime.now(UTC),
                    "updated_at": datetime.now(UTC),
                    "last_updated": datetime.now(UTC),
                }
            )

        # 按市场筛选
        params = StockQueryParams(market="NASDAQ")
        result = await stock_service.query_stocks(params)

        assert result["total"] == 2
        assert all(item["market"] == "NASDAQ" for item in result["items"])

    @pytest.mark.asyncio
    async def test_query_stocks_name_fuzzy(self, stock_service, sample_stock):
        """测试股票名称模糊查询."""
        stocks = [
            {**sample_stock, "ticker": "AAPL", "name": "Apple Inc."},
            {**sample_stock, "ticker": "GOOGL", "name": "Google Inc."},
            {**sample_stock, "ticker": "MSFT", "name": "Microsoft Corp."},
        ]
        for stock in stocks:
            await stock_service.collection.insert_one(
                {
                    **stock,
                    "created_at": datetime.now(UTC),
                    "updated_at": datetime.now(UTC),
                    "last_updated": datetime.now(UTC),
                }
            )

        # 模糊查询包含 "Apple"
        params = StockQueryParams(name="Apple")
        result = await stock_service.query_stocks(params)

        assert result["total"] >= 1
        assert any("Apple" in item["name"] for item in result["items"])

    @pytest.mark.asyncio
    async def test_query_stocks_pagination(self, stock_service, sample_stock):
        """测试分页功能."""
        # 插入多个股票
        for i in range(25):
            await stock_service.collection.insert_one(
                {
                    **sample_stock,
                    "ticker": f"TICK{i:03d}",
                    "created_at": datetime.now(UTC),
                    "updated_at": datetime.now(UTC),
                    "last_updated": datetime.now(UTC),
                }
            )

        # 第一页
        params = StockQueryParams(page=1, page_size=10)
        result = await stock_service.query_stocks(params)

        assert result["total"] == 25
        assert len(result["items"]) == 10
        assert result["page"] == 1
        assert result["total_pages"] == 3

        # 第二页
        params = StockQueryParams(page=2, page_size=10)
        result = await stock_service.query_stocks(params)

        assert len(result["items"]) == 10
        assert result["page"] == 2

    @pytest.mark.asyncio
    async def test_upsert_stock_new(self, stock_service, sample_stock):
        """测试插入新股票."""
        result = await stock_service.upsert_stock(sample_stock)

        assert result is not None
        assert result["ticker"] == "AAPL"
        assert "id" in result
        assert "created_at" in result

        # 验证已插入数据库
        count = await stock_service.collection.count_documents({"ticker": "AAPL"})
        assert count == 1

    @pytest.mark.asyncio
    async def test_upsert_stock_update(self, stock_service, sample_stock):
        """测试更新已存在的股票."""
        # 先插入
        await stock_service.upsert_stock(sample_stock)

        # 更新
        updated_data = {**sample_stock, "name": "Apple Inc. Updated"}
        result = await stock_service.upsert_stock(updated_data)

        assert result["name"] == "Apple Inc. Updated"

        # 验证数据库中只有一个文档
        count = await stock_service.collection.count_documents({"ticker": "AAPL"})
        assert count == 1

    @pytest.mark.asyncio
    @patch("app.services.stock_service.fetch_stock_info_async")
    async def test_update_stock_from_yfinance_success(
        self, mock_fetch, stock_service
    ):
        """测试从 yfinance 更新股票成功."""
        mock_fetch.return_value = {
            "ticker": "AAPL",
            "name": "Apple Inc.",
            "market": "NASDAQ",
            "data_source": "yfinance",
        }

        result = await stock_service.update_stock_from_yfinance("AAPL")

        assert result is not None
        assert result["ticker"] == "AAPL"
        mock_fetch.assert_called_once_with("AAPL")

    @pytest.mark.asyncio
    @patch("app.services.stock_service.fetch_stock_info_async")
    async def test_update_stock_from_yfinance_failed(self, mock_fetch, stock_service):
        """测试从 yfinance 更新股票失败."""
        mock_fetch.return_value = None

        result = await stock_service.update_stock_from_yfinance("INVALID")

        assert result is None

    @pytest.mark.asyncio
    @patch("app.services.stock_service.fetch_multiple_stocks")
    async def test_update_all_stocks_success(self, mock_fetch_multiple, stock_service, sample_stock):
        """测试更新所有股票成功."""
        # 先插入一些股票到数据库
        stocks = [
            {**sample_stock, "ticker": "AAPL"},
            {**sample_stock, "ticker": "GOOGL"},
            {**sample_stock, "ticker": "MSFT"},
        ]
        for stock in stocks:
            await stock_service.collection.insert_one(
                {
                    **stock,
                    "created_at": datetime.now(UTC),
                    "updated_at": datetime.now(UTC),
                    "last_updated": datetime.now(UTC),
                }
            )

        mock_fetch_multiple.return_value = {
            "AAPL": {"ticker": "AAPL", "name": "Apple Inc."},
            "GOOGL": {"ticker": "GOOGL", "name": "Google"},
            "MSFT": None,  # 一个失败
        }

        result = await stock_service.update_all_stocks()

        assert result["total"] == 3
        assert result["success"] == 2
        assert result["failed"] == 1

    @pytest.mark.asyncio
    @patch("app.services.stock_service.fetch_multiple_stocks")
    async def test_update_all_stocks_empty(self, mock_fetch_multiple, stock_service):
        """测试更新空列表."""
        mock_fetch_multiple.return_value = {}

        result = await stock_service.update_all_stocks()

        assert result["total"] == 0
        assert result["success"] == 0
        assert result["failed"] == 0

    @pytest.mark.asyncio
    @patch("app.services.stock_service.fetch_multiple_stocks")
    async def test_batch_update_stocks_success(
        self, mock_fetch_multiple, stock_service
    ):
        """测试批量更新指定股票成功."""
        mock_fetch_multiple.return_value = {
            "AAPL": {"ticker": "AAPL", "name": "Apple Inc."},
            "GOOGL": {"ticker": "GOOGL", "name": "Google"},
        }

        result = await stock_service.batch_update_stocks(["AAPL", "GOOGL"])

        assert result["total"] == 2
        assert result["success"] == 2
        assert result["failed"] == 0

    @pytest.mark.asyncio
    async def test_batch_update_stocks_empty(self, stock_service):
        """测试批量更新空列表."""
        result = await stock_service.batch_update_stocks([])

        assert result["total"] == 0
        assert result["success"] == 0
        assert result["failed"] == 0

    @pytest.mark.asyncio
    async def test_delete_stock_success(self, stock_service, sample_stock):
        """测试删除股票成功."""
        # 先插入
        await stock_service.upsert_stock(sample_stock)

        # 删除
        result = await stock_service.delete_stock("AAPL")

        assert result is True

        # 验证已删除
        count = await stock_service.collection.count_documents({"ticker": "AAPL"})
        assert count == 0

    @pytest.mark.asyncio
    async def test_delete_stock_not_found(self, stock_service):
        """测试删除不存在的股票."""
        result = await stock_service.delete_stock("INVALID")

        assert result is False

    @pytest.mark.asyncio
    @patch("app.services.stock_service.get_all_tickers_from_yahoo")
    @patch("app.services.stock_service.fetch_stock_info_async")
    async def test_fetch_and_save_all_stocks_from_yahoo_success(
        self, mock_fetch, mock_get_tickers, stock_service
    ):
        """测试从 Yahoo 抓取并保存所有股票成功."""
        # Mock 获取股票代码列表
        mock_get_tickers.return_value = ["AAPL", "GOOGL"]
        
        # Mock 抓取股票信息
        async def mock_fetch_side_effect(ticker):
            if ticker == "AAPL":
                return {"ticker": "AAPL", "name": "Apple Inc."}
            elif ticker == "GOOGL":
                return {"ticker": "GOOGL", "name": "Google"}
            return None
        
        mock_fetch.side_effect = mock_fetch_side_effect

        result = await stock_service.fetch_and_save_all_stocks_from_yahoo()

        assert result["total"] == 2
        assert result["fetch_success"] == 2
        assert result["fetch_failed"] == 0
        assert result["save_success"] == 2
        assert result["save_failed"] == 0

        # 验证已保存到数据库
        count = await stock_service.collection.count_documents({})
        assert count == 2

    @pytest.mark.asyncio
    async def test_query_stocks_with_market_type(self, stock_service, sample_stock):
        """测试按市场类型查询."""
        # 插入不同市场类型的股票
        stocks = [
            {**sample_stock, "ticker": "AAPL", "market_type": "美股"},
            {**sample_stock, "ticker": "000001", "market_type": "A股"},
            {**sample_stock, "ticker": "00700", "market_type": "港股"},
        ]
        for stock in stocks:
            await stock_service.collection.insert_one(
                {
                    **stock,
                    "created_at": datetime.now(UTC),
                    "updated_at": datetime.now(UTC),
                    "last_updated": datetime.now(UTC),
                }
            )

        # 按市场类型筛选
        params = StockQueryParams(market_type="A股")
        result = await stock_service.query_stocks(params)

        assert result["total"] == 1
        assert result["items"][0]["market_type"] == "A股"

    @pytest.mark.asyncio
    async def test_update_stock_from_provider_success(self, stock_service):
        """测试从数据源更新股票成功（多数据源）."""
        # Mock 路由器
        from unittest.mock import Mock, AsyncMock
        mock_router = Mock()
        mock_router.fetch_stock_info = AsyncMock(return_value={
            "ticker": "AAPL",
            "name": "Apple Inc.",
            "market": "NASDAQ",
            "market_type": "美股",
            "data_source": "yfinance",
        })
        stock_service.router = mock_router

        result = await stock_service.update_stock_from_provider("AAPL")

        assert result is not None
        assert result["ticker"] == "AAPL"
        assert result["name"] == "Apple Inc."
        mock_router.fetch_stock_info.assert_called_once_with("AAPL", market=None, preferred_provider=None)

    @pytest.mark.asyncio
    async def test_update_stock_from_provider_with_market(self, stock_service):
        """测试从数据源更新股票（指定市场类型）."""
        from unittest.mock import Mock, AsyncMock
        mock_router = Mock()
        mock_router.fetch_stock_info = AsyncMock(return_value={
            "ticker": "000001",
            "name": "平安银行",
            "market": "SZSE",
            "market_type": "A股",
            "data_source": "akshare",
        })
        stock_service.router = mock_router

        result = await stock_service.update_stock_from_provider("000001", market="A股")

        assert result is not None
        assert result["ticker"] == "000001"
        assert result["market_type"] == "A股"
        mock_router.fetch_stock_info.assert_called_once_with("000001", market="A股", preferred_provider=None)

    @pytest.mark.asyncio
    async def test_update_stock_from_provider_with_preferred_provider(self, stock_service):
        """测试从数据源更新股票（指定首选数据源）."""
        from unittest.mock import Mock, AsyncMock
        mock_router = Mock()
        mock_router.fetch_stock_info = AsyncMock(return_value={
            "ticker": "AAPL",
            "name": "Apple Inc.",
            "data_source": "akshare",
        })
        stock_service.router = mock_router

        result = await stock_service.update_stock_from_provider(
            "AAPL", preferred_provider="akshare"
        )

        assert result is not None
        mock_router.fetch_stock_info.assert_called_once_with(
            "AAPL", market=None, preferred_provider="akshare"
        )

    @pytest.mark.asyncio
    async def test_update_stock_from_provider_failed(self, stock_service):
        """测试从数据源更新股票失败（所有数据源都失败）."""
        from unittest.mock import Mock, AsyncMock
        mock_router = Mock()
        mock_router.fetch_stock_info = AsyncMock(return_value=None)
        stock_service.router = mock_router

        result = await stock_service.update_stock_from_provider("INVALID")

        assert result is None

    @pytest.mark.asyncio
    async def test_update_stock_from_provider_validate_if_new(self, stock_service):
        """测试从数据源更新股票（验证新股票数据有效性）."""
        from unittest.mock import Mock, AsyncMock
        mock_router = Mock()
        # 返回无效数据（缺少 name 字段）
        mock_router.fetch_stock_info = AsyncMock(return_value={
            "ticker": "INVALID",
            # 缺少 name 字段
        })
        stock_service.router = mock_router

        result = await stock_service.update_stock_from_provider(
            "INVALID", validate_if_new=True
        )

        assert result is None  # 应该被拒绝

    @pytest.mark.asyncio
    async def test_update_all_stocks_with_router(self, stock_service, sample_stock):
        """测试更新所有股票（使用路由器）."""
        from unittest.mock import Mock, AsyncMock
        # 先插入一些股票到数据库
        stocks = [
            {**sample_stock, "ticker": "AAPL"},
            {**sample_stock, "ticker": "GOOGL"},
        ]
        for stock in stocks:
            await stock_service.collection.insert_one(
                {
                    **stock,
                    "created_at": datetime.now(UTC),
                    "updated_at": datetime.now(UTC),
                    "last_updated": datetime.now(UTC),
                }
            )

        # Mock 路由器
        mock_router = Mock()
        async def mock_fetch(ticker):
            if ticker == "AAPL":
                return {"ticker": "AAPL", "name": "Apple Inc.", "data_source": "yfinance"}
            elif ticker == "GOOGL":
                return {"ticker": "GOOGL", "name": "Google", "data_source": "yfinance"}
            return None
        mock_router.fetch_stock_info = AsyncMock(side_effect=mock_fetch)
        stock_service.router = mock_router

        result = await stock_service.update_all_stocks()

        assert result["total"] == 2
        assert result["success"] == 2
        assert result["failed"] == 0

    @pytest.mark.asyncio
    async def test_batch_update_stocks_with_router(self, stock_service):
        """测试批量更新股票（使用路由器）."""
        from unittest.mock import Mock, AsyncMock
        mock_router = Mock()
        async def mock_fetch(ticker):
            if ticker == "AAPL":
                return {"ticker": "AAPL", "name": "Apple Inc.", "data_source": "yfinance"}
            elif ticker == "GOOGL":
                return {"ticker": "GOOGL", "name": "Google", "data_source": "akshare"}
            return None
        mock_router.fetch_stock_info = AsyncMock(side_effect=mock_fetch)
        stock_service.router = mock_router

        result = await stock_service.batch_update_stocks(["AAPL", "GOOGL"])

        assert result["total"] == 2
        assert result["success"] == 2
        assert result["failed"] == 0
