"""技术指标路由测试."""

import pytest
from unittest.mock import AsyncMock, patch


class TestIndicatorsRouter:
    """技术指标路由测试类."""

    @pytest.mark.asyncio
    async def test_get_supported_indicators(self, client):
        """测试获取支持的指标列表."""
        mock_indicators = [
            {
                "name": "MA5",
                "display_name": "5日均线",
                "type": "MA",
                "category": "trend",
                "params": {"period": 5},
            },
            {
                "name": "RSI14",
                "display_name": "14日相对强弱指标",
                "type": "RSI",
                "category": "momentum",
                "params": {"period": 14},
            },
        ]

        with patch("app.routers.indicators.get_indicator_service") as mock_service:
            mock_service.return_value.get_supported_indicators = MagicMock(
                return_value=mock_indicators
            )

            response = await client.get("/api/v1/indicators/supported")
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert len(data["data"]) == 2

    @pytest.mark.asyncio
    async def test_calculate_indicator(self, client):
        """测试计算技术指标."""
        mock_indicator_info = {
            "type": "MA",
            "params": {"period": 5},
        }

        mock_data = [
            {
                "date": "2024-01-01",
                "timestamp": "2024-01-01T00:00:00",
                "indicator_name": "MA5",
                "value": 100.0,
            }
        ]

        with patch("app.routers.indicators.get_indicator_service") as mock_service:
            mock_service.return_value._parse_indicator_name = MagicMock(
                return_value=mock_indicator_info
            )
            mock_service.return_value.calculate_indicator = AsyncMock(
                return_value=mock_data
            )

            response = await client.post(
                "/api/v1/indicators/AAPL/calculate?indicator_name=MA5"
            )
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert len(data["data"]) == 1

    @pytest.mark.asyncio
    async def test_calculate_indicator_with_params(self, client):
        """测试计算技术指标（带参数）."""
        mock_indicator_info = {
            "type": "MA",
            "params": {"period": 5},
        }

        mock_data = [
            {
                "date": "2024-01-01",
                "timestamp": "2024-01-01T00:00:00",
                "indicator_name": "MA10",
                "value": 100.0,
            }
        ]

        with patch("app.routers.indicators.get_indicator_service") as mock_service:
            mock_service.return_value._parse_indicator_name = MagicMock(
                return_value=mock_indicator_info
            )
            mock_service.return_value.calculate_indicator = AsyncMock(
                return_value=mock_data
            )

            response = await client.post(
                "/api/v1/indicators/AAPL/calculate?indicator_name=MA10",
                json={"indicator_params": {"period": 10}},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200

    @pytest.mark.asyncio
    async def test_calculate_indicator_unsupported(self, client):
        """测试计算不支持的指标."""
        with patch("app.routers.indicators.get_indicator_service") as mock_service:
            mock_service.return_value._parse_indicator_name = MagicMock(return_value=None)

            response = await client.post(
                "/api/v1/indicators/AAPL/calculate?indicator_name=INVALID"
            )
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_indicator_data_list_mode(self, client):
        """测试查询指标数据（列表模式）."""
        mock_data = [
            {
                "date": "2024-01-01",
                "timestamp": "2024-01-01T00:00:00",
                "indicator_name": "MA5",
                "value": 100.0,
            }
        ]

        with patch("app.routers.indicators.get_indicator_service") as mock_service:
            mock_service.return_value.query_indicator_data = AsyncMock(
                return_value=mock_data
            )

            response = await client.get("/api/v1/indicators/AAPL?indicator_name=MA5")
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert data["data"]["count"] == 1

    @pytest.mark.asyncio
    async def test_get_indicator_data_pagination_mode(self, client):
        """测试查询指标数据（分页模式）."""
        mock_data = [
            {
                "date": f"2024-01-{i:02d}",
                "timestamp": f"2024-01-{i:02d}T00:00:00",
                "indicator_name": "MA5",
                "value": 100.0,
            }
            for i in range(1, 51)
        ]

        with patch("app.routers.indicators.get_indicator_service") as mock_service:
            mock_service.return_value.query_indicator_data = AsyncMock(
                return_value=mock_data
            )

            response = await client.get(
                "/api/v1/indicators/AAPL?indicator_name=MA5&page=1&page_size=20"
            )
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert data["data"]["total"] == 50
            assert data["data"]["page"] == 1
            assert len(data["data"]["items"]) == 20

    @pytest.mark.asyncio
    async def test_get_indicator_data_missing_name(self, client):
        """测试查询指标数据但缺少指标名称."""
        response = await client.get("/api/v1/indicators/AAPL")
        # 缺少必填参数 indicator_name，应该返回 422
        assert response.status_code == 422

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="SSE 测试需要特殊处理")
    async def test_batch_calculate_sse(self, client):
        """测试批量计算（SSE）."""
        # SSE 测试比较复杂，需要特殊的客户端设置
        pass


class TestIndicatorsRouterEdgeCases:
    """技术指标路由边界测试类."""

    @pytest.mark.asyncio
    async def test_calculate_indicator_invalid_date(self, client):
        """测试无效日期参数."""
        mock_indicator_info = {
            "type": "MA",
            "params": {"period": 5},
        }

        with patch("app.routers.indicators.get_indicator_service") as mock_service:
            mock_service.return_value._parse_indicator_name = MagicMock(
                return_value=mock_indicator_info
            )

            response = await client.post(
                "/api/v1/indicators/AAPL/calculate?indicator_name=MA5&start_date=invalid"
            )
            # 日期解析错误会被 calculate_indicator 捕获并返回 500
            assert response.status_code in [400, 500]

    @pytest.mark.asyncio
    async def test_get_indicator_data_large_limit(self, client):
        """测试超大 limit 参数."""
        response = await client.get(
            "/api/v1/indicators/AAPL?indicator_name=MA5&limit=99999"
        )
        # 应该返回 422（参数验证失败）
        assert response.status_code == 422


# 补充 MagicMock 导入（用于同步 mock）
from unittest.mock import MagicMock
