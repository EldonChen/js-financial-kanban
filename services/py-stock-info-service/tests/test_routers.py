"""路由测试."""

import pytest
from httpx import AsyncClient
from bson import ObjectId
from datetime import datetime, UTC


class TestStocksRouter:
    """股票路由测试类."""

    @pytest.mark.asyncio
    async def test_get_stocks_empty(self, client):
        """测试获取空股票列表."""
        response = await client.get("/api/v1/stocks")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["total"] == 0
        assert data["data"]["items"] == []

    @pytest.mark.asyncio
    async def test_get_stocks_with_data(self, client, sample_stock, setup_test_db):
        """测试获取股票列表."""
        # 插入测试数据
        await setup_test_db.stocks.insert_one(
            {
                **sample_stock,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
                "last_updated": datetime.now(UTC),
            }
        )

        response = await client.get("/api/v1/stocks")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["total"] >= 1

    @pytest.mark.asyncio
    async def test_get_stocks_with_filter(self, client, sample_stock, setup_test_db):
        """测试带筛选条件的查询."""
        # 插入多个股票
        stocks = [
            {**sample_stock, "ticker": "AAPL", "market": "NASDAQ"},
            {**sample_stock, "ticker": "GOOGL", "market": "NASDAQ"},
            {**sample_stock, "ticker": "MSFT", "market": "NYSE"},
        ]
        for stock in stocks:
            await setup_test_db.stocks.insert_one(
                {
                    **stock,
                    "created_at": datetime.now(UTC),
                    "updated_at": datetime.now(UTC),
                    "last_updated": datetime.now(UTC),
                }
            )

        # 按市场筛选
        response = await client.get("/api/v1/stocks?market=NASDAQ")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 2

    @pytest.mark.asyncio
    async def test_get_stock_by_ticker_success(
        self, client, sample_stock, setup_test_db
    ):
        """测试获取单个股票成功."""
        # 插入测试数据
        await setup_test_db.stocks.insert_one(
            {
                **sample_stock,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
                "last_updated": datetime.now(UTC),
            }
        )

        response = await client.get("/api/v1/stocks/AAPL")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["ticker"] == "AAPL"

    @pytest.mark.asyncio
    async def test_get_stock_by_ticker_not_found(self, client):
        """测试获取不存在的股票."""
        response = await client.get("/api/v1/stocks/INVALID")
        assert response.status_code == 404

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需要 mock yfinance，避免实际网络请求")
    async def test_update_stock(self, client):
        """测试手动更新股票."""
        # 这个测试需要 mock yfinance，暂时跳过
        pass

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需要 mock yfinance，避免实际网络请求")
    async def test_update_all_stocks(self, client):
        """测试更新所有股票."""
        # 这个测试需要 mock yfinance，暂时跳过
        pass

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需要 mock yfinance，避免实际网络请求")
    async def test_batch_update_stocks(self, client):
        """测试批量更新股票."""
        # 这个测试需要 mock yfinance，暂时跳过
        pass


class TestSchedulesRouter:
    """更新计划路由测试类."""

    @pytest.mark.asyncio
    async def test_get_schedules_empty(self, client):
        """测试获取空更新计划列表."""
        response = await client.get("/api/v1/schedules")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["total"] == 0

    @pytest.mark.asyncio
    async def test_create_schedule_success(self, client, sample_schedule):
        """测试创建更新计划成功."""
        response = await client.post("/api/v1/schedules", json=sample_schedule)
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["schedule_type"] == "cron"
        assert "id" in data["data"]

    @pytest.mark.asyncio
    async def test_create_schedule_invalid(self, client):
        """测试创建无效的更新计划."""
        invalid_schedule = {
            "schedule_type": "invalid",
            "schedule_config": {},
        }
        response = await client.post("/api/v1/schedules", json=invalid_schedule)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_schedule_by_id_success(
        self, client, sample_schedule, setup_test_db
    ):
        """测试获取单个更新计划成功."""
        # 先创建
        create_response = await client.post("/api/v1/schedules", json=sample_schedule)
        schedule_id = create_response.json()["data"]["id"]

        # 获取
        response = await client.get(f"/api/v1/schedules/{schedule_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["id"] == schedule_id

    @pytest.mark.asyncio
    async def test_get_schedule_by_id_not_found(self, client):
        """测试获取不存在的更新计划."""
        fake_id = str(ObjectId())
        response = await client.get(f"/api/v1/schedules/{fake_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_schedule_status(self, client, sample_schedule):
        """测试获取更新状态统计."""
        # 创建一些计划
        await client.post("/api/v1/schedules", json=sample_schedule)
        await client.post(
            "/api/v1/schedules",
            json={**sample_schedule, "is_active": False},
        )

        response = await client.get("/api/v1/schedules/status")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "total" in data["data"]
        assert "active" in data["data"]
        assert "inactive" in data["data"]

    @pytest.mark.asyncio
    async def test_update_schedule_success(
        self, client, sample_schedule, sample_schedule_update
    ):
        """测试更新更新计划成功."""
        # 先创建
        create_response = await client.post("/api/v1/schedules", json=sample_schedule)
        schedule_id = create_response.json()["data"]["id"]

        # 更新
        response = await client.put(
            f"/api/v1/schedules/{schedule_id}", json=sample_schedule_update
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["schedule_type"] == "interval"

    @pytest.mark.asyncio
    async def test_delete_schedule_success(self, client, sample_schedule):
        """测试删除更新计划成功."""
        # 先创建
        create_response = await client.post("/api/v1/schedules", json=sample_schedule)
        schedule_id = create_response.json()["data"]["id"]

        # 删除
        response = await client.delete(f"/api/v1/schedules/{schedule_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        # 验证已删除
        get_response = await client.get(f"/api/v1/schedules/{schedule_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_toggle_schedule_success(self, client, sample_schedule):
        """测试切换更新计划激活状态成功."""
        # 先创建
        create_response = await client.post("/api/v1/schedules", json=sample_schedule)
        schedule_id = create_response.json()["data"]["id"]
        original_active = create_response.json()["data"]["is_active"]

        # 切换
        response = await client.post(f"/api/v1/schedules/{schedule_id}/toggle")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["is_active"] != original_active

    @pytest.mark.asyncio
    async def test_get_schedules_with_filter(self, client, sample_schedule):
        """测试带筛选条件的查询."""
        # 创建激活和未激活的计划
        await client.post("/api/v1/schedules", json=sample_schedule)
        await client.post(
            "/api/v1/schedules",
            json={**sample_schedule, "is_active": False},
        )

        # 只查询激活的
        response = await client.get("/api/v1/schedules?is_active=true")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert all(item["is_active"] is True for item in data["data"]["items"])
