"""Items API 测试."""

import pytest
from httpx import AsyncClient, ASGITransport
from bson import ObjectId
from app.main import app


@pytest.fixture
async def client():
    """创建异步测试客户端."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestItemsAPI:
    """Items API 测试类."""

    @pytest.mark.asyncio
    async def test_create_item_success(self, client, sample_item):
        """测试成功创建 item."""
        response = await client.post("/api/v1/items", json=sample_item)
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "Item 创建成功"
        assert data["data"]["name"] == sample_item["name"]
        assert data["data"]["description"] == sample_item["description"]
        assert data["data"]["price"] == sample_item["price"]
        assert "id" in data["data"]
        assert "created_at" in data["data"]
        assert "updated_at" in data["data"]

    @pytest.mark.asyncio
    async def test_create_item_missing_required_field(self, client):
        """测试缺少必填字段时创建 item."""
        response = await client.post("/api/v1/items", json={"description": "缺少 name"})
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_all_items_empty(self, client):
        """测试获取空列表."""
        response = await client.get("/api/v1/items")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"] == []

    @pytest.mark.asyncio
    async def test_get_all_items(self, client, sample_item):
        """测试获取所有 items."""
        # 先创建几个 items
        await client.post("/api/v1/items", json=sample_item)
        await client.post("/api/v1/items", json={**sample_item, "name": "Item 2"})
        
        response = await client.get("/api/v1/items")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]) >= 2

    @pytest.mark.asyncio
    async def test_get_item_by_id_success(self, client, sample_item):
        """测试成功获取单个 item."""
        # 先创建 item
        create_response = await client.post("/api/v1/items", json=sample_item)
        item_id = create_response.json()["data"]["id"]
        
        # 获取 item
        response = await client.get(f"/api/v1/items/{item_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["id"] == item_id
        assert data["data"]["name"] == sample_item["name"]

    @pytest.mark.asyncio
    async def test_get_item_by_id_not_found(self, client):
        """测试获取不存在的 item."""
        fake_id = str(ObjectId())
        response = await client.get(f"/api/v1/items/{fake_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_item_by_id_invalid_format(self, client):
        """测试使用无效格式的 ID."""
        response = await client.get("/api/v1/items/invalid-id")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_update_item_success(self, client, sample_item, sample_item_update):
        """测试成功更新 item."""
        # 先创建 item
        create_response = await client.post("/api/v1/items", json=sample_item)
        item_id = create_response.json()["data"]["id"]
        
        # 更新 item
        response = await client.put(f"/api/v1/items/{item_id}", json=sample_item_update)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "Item 更新成功"
        assert data["data"]["name"] == sample_item_update["name"]
        assert data["data"]["price"] == sample_item_update["price"]

    @pytest.mark.asyncio
    async def test_update_item_partial(self, client, sample_item):
        """测试部分更新 item."""
        # 先创建 item
        create_response = await client.post("/api/v1/items", json=sample_item)
        item_id = create_response.json()["data"]["id"]
        
        # 只更新 price
        response = await client.put(f"/api/v1/items/{item_id}", json={"price": 299.99})
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["price"] == 299.99
        # 其他字段应该保持不变
        assert data["data"]["name"] == sample_item["name"]

    @pytest.mark.asyncio
    async def test_update_item_not_found(self, client, sample_item_update):
        """测试更新不存在的 item."""
        fake_id = str(ObjectId())
        response = await client.put(f"/api/v1/items/{fake_id}", json=sample_item_update)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_item_no_fields(self, client, sample_item):
        """测试更新时没有提供任何字段."""
        # 先创建 item
        create_response = await client.post("/api/v1/items", json=sample_item)
        item_id = create_response.json()["data"]["id"]
        
        # 尝试更新但不提供任何字段
        response = await client.put(f"/api/v1/items/{item_id}", json={})
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_delete_item_success(self, client, sample_item):
        """测试成功删除 item."""
        # 先创建 item
        create_response = await client.post("/api/v1/items", json=sample_item)
        item_id = create_response.json()["data"]["id"]
        
        # 删除 item
        response = await client.delete(f"/api/v1/items/{item_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "Item 删除成功"
        
        # 验证 item 已被删除
        get_response = await client.get(f"/api/v1/items/{item_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_item_not_found(self, client):
        """测试删除不存在的 item."""
        fake_id = str(ObjectId())
        response = await client.delete(f"/api/v1/items/{fake_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_item_invalid_format(self, client):
        """测试使用无效格式的 ID 删除 item."""
        response = await client.delete("/api/v1/items/invalid-id")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_item_validation_name_too_long(self, client):
        """测试 name 字段过长."""
        long_name = "a" * 101  # 超过 100 字符限制
        response = await client.post("/api/v1/items", json={"name": long_name})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_item_validation_price_negative(self, client):
        """测试 price 为负数."""
        response = await client.post("/api/v1/items", json={"name": "Test", "price": -10})
        assert response.status_code == 422
