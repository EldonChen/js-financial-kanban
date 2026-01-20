"""历史数据路由测试."""

import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, patch, MagicMock


class TestHistoricalDataRouter:
    """历史数据路由测试类."""

    @pytest.mark.asyncio
    async def test_get_kline_data_empty(self, client):
        """测试获取空K线数据."""
        with patch(
            "app.routers.historical_data.get_historical_data_service"
        ) as mock_service:
            mock_service.return_value.query_kline_data = AsyncMock(return_value=[])

            response = await client.get("/api/v1/historical-data/AAPL")
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert data["data"]["count"] == 0
            assert data["data"]["ticker"] == "AAPL"

    @pytest.mark.asyncio
    async def test_get_kline_data_with_data(self, client):
        """测试获取K线数据（列表模式）."""
        mock_data = [
            {
                "date": "2024-01-01",
                "timestamp": "2024-01-01T00:00:00",
                "open": 100.0,
                "high": 105.0,
                "low": 99.0,
                "close": 103.0,
                "volume": 1000000.0,
                "data_source": "yfinance",
            }
        ]

        with patch(
            "app.routers.historical_data.get_historical_data_service"
        ) as mock_service:
            mock_service.return_value.query_kline_data = AsyncMock(return_value=mock_data)

            response = await client.get("/api/v1/historical-data/AAPL?period=1d")
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert data["data"]["count"] == 1
            assert len(data["data"]["data"]) == 1

    @pytest.mark.asyncio
    async def test_get_kline_data_with_pagination(self, client):
        """测试获取K线数据（分页模式）."""
        mock_data = [
            {
                "date": f"2024-01-{i:02d}",
                "timestamp": f"2024-01-{i:02d}T00:00:00",
                "open": 100.0,
                "high": 105.0,
                "low": 99.0,
                "close": 103.0,
                "volume": 1000000.0,
                "data_source": "yfinance",
            }
            for i in range(1, 51)
        ]

        with patch(
            "app.routers.historical_data.get_historical_data_service"
        ) as mock_service:
            mock_service.return_value.query_kline_data = AsyncMock(return_value=mock_data)

            response = await client.get(
                "/api/v1/historical-data/AAPL?page=1&page_size=20"
            )
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert data["data"]["total"] == 50
            assert data["data"]["page"] == 1
            assert data["data"]["page_size"] == 20
            assert len(data["data"]["items"]) == 20

    @pytest.mark.asyncio
    async def test_get_kline_data_statistics(self, client):
        """测试获取统计信息."""
        mock_stats = {
            "total_count": 100,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "missing_dates": [],
            "coverage_rate": 1.0,
        }

        with patch(
            "app.routers.historical_data.get_historical_data_service"
        ) as mock_service:
            mock_service.return_value.get_kline_data_statistics = AsyncMock(
                return_value=mock_stats
            )

            response = await client.get("/api/v1/historical-data/AAPL/statistics")
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert data["data"]["total_count"] == 100

    @pytest.mark.asyncio
    async def test_update_kline_data_incremental(self, client):
        """测试增量更新K线数据."""
        mock_stock = {
            "ticker": "AAPL",
            "name": "Apple Inc.",
            "market": "NASDAQ",
        }

        mock_result = {
            "ticker": "AAPL",
            "inserted": 5,
            "updated": 0,
        }

        with patch("app.routers.historical_data.get_stock_service") as mock_stock_svc, patch(
            "app.routers.historical_data.get_historical_data_service"
        ) as mock_hist_svc:
            mock_stock_svc.return_value.get_stock_by_ticker = AsyncMock(
                return_value=mock_stock
            )
            mock_hist_svc.return_value.update_kline_data_incremental = AsyncMock(
                return_value=mock_result
            )

            response = await client.post(
                "/api/v1/historical-data/AAPL/update?incremental=true"
            )
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert data["data"]["ticker"] == "AAPL"

    @pytest.mark.asyncio
    async def test_update_kline_data_stock_not_found(self, client):
        """测试更新不存在的股票."""
        with patch("app.routers.historical_data.get_stock_service") as mock_stock_svc:
            mock_stock_svc.return_value.get_stock_by_ticker = AsyncMock(return_value=None)

            response = await client.post("/api/v1/historical-data/INVALID/update")
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_kline_data(self, client):
        """测试删除K线数据."""
        with patch(
            "app.routers.historical_data.get_historical_data_service"
        ) as mock_service:
            mock_service.return_value.delete_kline_data = AsyncMock(return_value=10)

            response = await client.delete("/api/v1/historical-data/AAPL?period=1d")
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert data["data"]["deleted_count"] == 10

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="SSE 测试需要特殊处理")
    async def test_batch_update_sse(self, client):
        """测试批量更新（SSE）."""
        # SSE 测试比较复杂，需要特殊的客户端设置
        pass

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="SSE 测试需要特殊处理")
    async def test_full_update_sse(self, client):
        """测试全量更新（SSE）."""
        # SSE 测试比较复杂，需要特殊的客户端设置
        pass


class TestHistoricalDataRouterEdgeCases:
    """历史数据路由边界测试类."""

    @pytest.mark.asyncio
    async def test_get_kline_data_invalid_date(self, client):
        """测试无效日期参数."""
        response = await client.get(
            "/api/v1/historical-data/AAPL?start_date=invalid"
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_kline_data_large_limit(self, client):
        """测试超大 limit 参数."""
        response = await client.get("/api/v1/historical-data/AAPL?limit=99999")
        # 应该返回 422（参数验证失败）
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_kline_data_negative_page(self, client):
        """测试负数页码."""
        response = await client.get("/api/v1/historical-data/AAPL?page=-1")
        assert response.status_code == 422
