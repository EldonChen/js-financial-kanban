"""数据质量服务单元测试."""

import pytest
from datetime import datetime, timedelta
from mongomock_motor import AsyncMongoMockClient

from app.services.data_quality.data_quality_service import DataQualityService
from app.services.data_quality.completeness_checker import CompletenessChecker
from app.services.data_quality.accuracy_checker import AccuracyChecker
from app.services.data_quality.consistency_checker import ConsistencyChecker
from app.services.data_quality.data_fixer import DataFixer


@pytest.fixture
async def mock_db():
    """创建 Mock 数据库."""
    client = AsyncMongoMockClient()
    db = client["test_db"]
    yield db
    client.close()


@pytest.fixture
async def data_quality_service(mock_db):
    """创建数据质量服务实例."""
    return DataQualityService(db=mock_db)


@pytest.mark.asyncio
async def test_data_quality_service_initialization(data_quality_service):
    """测试数据质量服务初始化."""
    assert data_quality_service is not None
    assert isinstance(data_quality_service.completeness_checker, CompletenessChecker)
    assert isinstance(data_quality_service.accuracy_checker, AccuracyChecker)
    assert isinstance(data_quality_service.consistency_checker, ConsistencyChecker)
    assert isinstance(data_quality_service.data_fixer, DataFixer)


@pytest.mark.asyncio
async def test_check_data_completeness(data_quality_service, mock_db):
    """测试数据完整性检查."""
    # 插入测试数据
    collection = mock_db["kline_data"]
    
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 1, 10)
    
    # 插入部分数据（缺失一些日期）
    test_data = []
    current_date = start_date
    skip_dates = [datetime(2025, 1, 5), datetime(2025, 1, 6)]  # 缺失的日期
    
    while current_date <= end_date:
        if current_date not in skip_dates and current_date.weekday() < 5:
            test_data.append({
                "timestamp": current_date,
                "metadata": {
                    "ticker": "AAPL",
                    "market": "NASDAQ",
                    "period": "1d"
                },
                "open": 150.0,
                "high": 152.0,
                "low": 149.0,
                "close": 151.0,
                "volume": 1000000,
                "data_source": "test"
            })
        current_date += timedelta(days=1)
    
    if test_data:
        await collection.insert_many(test_data)
    
    # 执行完整性检查
    result = await data_quality_service.check_data_completeness(
        ticker="AAPL",
        period="1d",
        start_date=start_date,
        end_date=end_date
    )
    
    assert result is not None
    assert result["ticker"] == "AAPL"
    assert result["period"] == "1d"
    assert "missing_count" in result
    assert "status" in result


@pytest.mark.asyncio
async def test_check_data_accuracy(data_quality_service, mock_db):
    """测试数据准确性检查."""
    # 插入测试数据（包含异常值）
    collection = mock_db["kline_data"]
    
    test_data = [
        {
            "timestamp": datetime(2025, 1, 1),
            "metadata": {
                "ticker": "AAPL",
                "market": "NASDAQ",
                "period": "1d"
            },
            "open": 150.0,
            "high": 152.0,
            "low": 149.0,
            "close": 151.0,
            "volume": 1000000,
            "data_source": "test"
        },
        {
            "timestamp": datetime(2025, 1, 2),
            "metadata": {
                "ticker": "AAPL",
                "market": "NASDAQ",
                "period": "1d"
            },
            "open": 150.0,
            "high": 152.0,
            "low": 149.0,
            "close": 500.0,  # 异常高的价格
            "volume": 1000000,
            "data_source": "test"
        },
        {
            "timestamp": datetime(2025, 1, 3),
            "metadata": {
                "ticker": "AAPL",
                "market": "NASDAQ",
                "period": "1d"
            },
            "open": 150.0,
            "high": 152.0,
            "low": 149.0,
            "close": 151.0,
            "volume": 100000000,  # 异常高的成交量
            "data_source": "test"
        }
    ]
    
    await collection.insert_many(test_data)
    
    # 执行准确性检查
    result = await data_quality_service.check_data_accuracy(
        ticker="AAPL",
        period="1d",
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 1, 3)
    )
    
    assert result is not None
    assert result["ticker"] == "AAPL"
    assert "abnormal_count" in result
    assert "unreasonable_count" in result


@pytest.mark.asyncio
async def test_check_data_consistency(data_quality_service, mock_db):
    """测试数据一致性检查."""
    # 插入测试数据（包含不一致的数据）
    collection = mock_db["kline_data"]
    
    test_data = [
        {
            "timestamp": datetime(2025, 1, 1),
            "metadata": {
                "ticker": "AAPL",
                "market": "NASDAQ",
                "period": "1d"
            },
            "open": 150.0,
            "high": 152.0,
            "low": 149.0,
            "close": 151.0,
            "volume": 1000000,
            "data_source": "test"
        },
        {
            "timestamp": datetime(2025, 1, 2),
            "metadata": {
                "ticker": "AAPL",
                "market": "NASDAQ",
                "period": "1d"
            },
            "open": 150.0,
            "high": 140.0,  # high < low，逻辑不一致
            "low": 149.0,
            "close": 151.0,
            "volume": 1000000,
            "data_source": "test"
        }
    ]
    
    await collection.insert_many(test_data)
    
    # 执行一致性检查
    result = await data_quality_service.check_data_consistency(
        ticker="AAPL",
        period="1d",
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 1, 2)
    )
    
    assert result is not None
    assert result["ticker"] == "AAPL"
    assert "inconsistent_count" in result
    assert result["inconsistent_count"] > 0


@pytest.mark.asyncio
async def test_run_quality_check(data_quality_service, mock_db):
    """测试完整的数据质量检查."""
    # 插入测试数据
    collection = mock_db["kline_data"]
    
    test_data = [
        {
            "timestamp": datetime(2025, 1, 1),
            "metadata": {
                "ticker": "AAPL",
                "market": "NASDAQ",
                "period": "1d"
            },
            "open": 150.0,
            "high": 152.0,
            "low": 149.0,
            "close": 151.0,
            "volume": 1000000,
            "data_source": "test"
        }
    ]
    
    await collection.insert_many(test_data)
    
    # 执行完整的质量检查
    result = await data_quality_service.run_quality_check(
        ticker="AAPL",
        period="1d",
        auto_fix=False
    )
    
    assert result is not None
    assert result["ticker"] == "AAPL"
    assert "completeness" in result
    assert "accuracy" in result
    assert "consistency" in result
    assert "duplicate" in result
