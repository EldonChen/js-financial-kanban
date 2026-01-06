"""Pytest 配置和共享 fixtures."""

import pytest
from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient
from app.main import app
import app.database as db_module


@pytest.fixture(scope="function", autouse=True)
async def setup_test_db():
    """为每个测试设置 mock 数据库."""
    # 使用 mongomock_motor 创建 mock 数据库
    mock_client = AsyncMongoMockClient()
    mock_database = mock_client["test_financial_kanban"]
    
    # 替换全局数据库连接
    db_module.client = mock_client
    db_module.database = mock_database
    
    # 清理测试数据
    await mock_database.items.delete_many({})
    
    yield mock_database
    
    # 测试后清理
    await mock_database.items.delete_many({})
    # mongomock_motor 的 close 是同步的
    if hasattr(mock_client, 'close'):
        try:
            mock_client.close()
        except:
            pass


@pytest.fixture
async def client():
    """创建异步测试客户端."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_item():
    """示例 item 数据."""
    return {
        "name": "测试 Item",
        "description": "这是一个测试 Item",
        "price": 99.99,
    }


@pytest.fixture
def sample_item_update():
    """示例 item 更新数据."""
    return {
        "name": "更新后的 Item",
        "price": 199.99,
    }
