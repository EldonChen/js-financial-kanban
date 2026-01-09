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
    await mock_database.stocks.delete_many({})
    await mock_database.update_schedules.delete_many({})

    yield mock_database

    # 测试后清理
    await mock_database.stocks.delete_many({})
    await mock_database.update_schedules.delete_many({})
    # mongomock_motor 的 close 是同步的
    if hasattr(mock_client, "close"):
        try:
            mock_client.close()
        except Exception:
            pass


@pytest.fixture
async def client():
    """创建异步测试客户端."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_stock():
    """示例股票数据."""
    return {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "market": "NASDAQ",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "currency": "USD",
        "exchange": "NMS",
        "country": "United States",
        "data_source": "yfinance",
    }


@pytest.fixture
def sample_stock_update():
    """示例股票更新数据."""
    return {
        "name": "Apple Inc. Updated",
        "sector": "Technology",
    }


@pytest.fixture
def sample_schedule():
    """示例更新计划数据."""
    return {
        "schedule_type": "cron",
        "schedule_config": {"cron": "0 9 * * 1-5"},
        "is_active": True,
    }


@pytest.fixture
def sample_schedule_update():
    """示例更新计划更新数据."""
    return {
        "schedule_type": "interval",
        "schedule_config": {"interval": 3600},
        "is_active": False,
    }
