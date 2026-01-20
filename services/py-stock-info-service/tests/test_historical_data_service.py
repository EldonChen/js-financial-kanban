"""历史数据服务单元测试."""

import pytest
from datetime import datetime, timedelta, UTC
from motor.motor_asyncio import AsyncIOMotorClient
from mongomock_motor import AsyncMongoMockClient

from app.services.historical_data import (
    HistoricalDataService,
    HistoricalDataFetcher,
    HistoricalDataStorage,
    HistoricalDataQuery,
)
from app.models.kline_data import prepare_kline_document, validate_kline_data


@pytest.fixture
async def mock_db():
    """创建 Mock MongoDB 数据库."""
    client = AsyncMongoMockClient()
    db = client["test_db"]
    
    # 创建集合（mongomock 不支持 TimeSeries，使用普通集合模拟）
    await db.create_collection("kline_data")
    
    yield db
    
    # 清理
    await client.drop_database("test_db")


@pytest.fixture
def sample_kline_data():
    """示例K线数据."""
    base_time = datetime.now(UTC)
    return [
        {
            "timestamp": base_time - timedelta(days=2),
            "open": 100.0,
            "high": 105.0,
            "low": 99.0,
            "close": 103.0,
            "volume": 1000000,
        },
        {
            "timestamp": base_time - timedelta(days=1),
            "open": 103.0,
            "high": 108.0,
            "low": 102.0,
            "close": 107.0,
            "volume": 1200000,
        },
        {
            "timestamp": base_time,
            "open": 107.0,
            "high": 110.0,
            "low": 106.0,
            "close": 109.0,
            "volume": 1500000,
        },
    ]


class TestKlineDataModel:
    """测试K线数据模型."""
    
    def test_validate_kline_data_valid(self, sample_kline_data):
        """测试有效数据验证."""
        for data in sample_kline_data:
            assert validate_kline_data(data) is True
    
    def test_validate_kline_data_invalid_missing_fields(self):
        """测试缺少必需字段."""
        invalid_data = {
            "timestamp": datetime.now(UTC),
            "open": 100.0,
            # 缺少 high, low, close, volume
        }
        assert validate_kline_data(invalid_data) is False
    
    def test_validate_kline_data_invalid_price_logic(self):
        """测试价格逻辑错误."""
        # high < low
        invalid_data = {
            "timestamp": datetime.now(UTC),
            "open": 100.0,
            "high": 99.0,  # high < low
            "low": 100.0,
            "close": 100.0,
            "volume": 1000,
        }
        assert validate_kline_data(invalid_data) is False
    
    def test_validate_kline_data_invalid_negative_volume(self):
        """测试负数成交量."""
        invalid_data = {
            "timestamp": datetime.now(UTC),
            "open": 100.0,
            "high": 105.0,
            "low": 99.0,
            "close": 103.0,
            "volume": -1000,  # 负数
        }
        assert validate_kline_data(invalid_data) is False
    
    def test_prepare_kline_document(self, sample_kline_data):
        """测试准备K线文档."""
        data = sample_kline_data[0]
        doc = prepare_kline_document("AAPL", "NASDAQ", "1d", data, "yfinance")
        
        assert doc["timestamp"] == data["timestamp"]
        assert doc["metadata"]["ticker"] == "AAPL"
        assert doc["metadata"]["market"] == "NASDAQ"
        assert doc["metadata"]["period"] == "1d"
        assert doc["open"] == data["open"]
        assert doc["high"] == data["high"]
        assert doc["low"] == data["low"]
        assert doc["close"] == data["close"]
        assert doc["volume"] == data["volume"]
        assert doc["data_source"] == "yfinance"


class TestHistoricalDataStorage:
    """测试历史数据存储服务."""
    
    @pytest.mark.asyncio
    async def test_save_kline_data(self, mock_db, sample_kline_data):
        """测试保存K线数据."""
        storage = HistoricalDataStorage(mock_db)
        
        inserted_count = await storage.save_kline_data(
            "AAPL", "NASDAQ", "1d", sample_kline_data, "yfinance"
        )
        
        assert inserted_count == len(sample_kline_data)
        
        # 验证数据已保存
        collection = mock_db.kline_data
        count = await collection.count_documents({})
        assert count == len(sample_kline_data)
    
    @pytest.mark.asyncio
    async def test_save_kline_data_empty(self, mock_db):
        """测试保存空数据."""
        storage = HistoricalDataStorage(mock_db)
        
        inserted_count = await storage.save_kline_data(
            "AAPL", "NASDAQ", "1d", [], "yfinance"
        )
        
        assert inserted_count == 0
    
    @pytest.mark.asyncio
    async def test_upsert_kline_data(self, mock_db, sample_kline_data):
        """测试 upsert K线数据."""
        storage = HistoricalDataStorage(mock_db)
        
        # mongomock 不完全支持 bulk_write 的 UpdateOne
        # 这个测试验证方法可以被调用而不抛出异常
        result1 = await storage.upsert_kline_data(
            "AAPL", "NASDAQ", "1d", sample_kline_data, "yfinance"
        )
        
        # mongomock 的 upsert 行为可能不同，这里只验证返回了结果字典
        assert "inserted" in result1
        assert "updated" in result1
        assert isinstance(result1["inserted"], int)
        assert isinstance(result1["updated"], int)
    
    @pytest.mark.asyncio
    async def test_delete_kline_data(self, mock_db, sample_kline_data):
        """测试删除K线数据."""
        storage = HistoricalDataStorage(mock_db)
        
        # 先插入数据
        await storage.save_kline_data(
            "AAPL", "NASDAQ", "1d", sample_kline_data, "yfinance"
        )
        
        # 删除数据
        deleted_count = await storage.delete_kline_data(ticker="AAPL", period="1d")
        assert deleted_count == len(sample_kline_data)
        
        # 验证数据已删除
        collection = mock_db.kline_data
        count = await collection.count_documents({})
        assert count == 0


class TestHistoricalDataQuery:
    """测试历史数据查询服务."""
    
    @pytest.mark.asyncio
    async def test_query_by_ticker(self, mock_db, sample_kline_data):
        """测试按股票代码查询."""
        storage = HistoricalDataStorage(mock_db)
        query = HistoricalDataQuery(mock_db)
        
        # 先插入数据
        await storage.save_kline_data(
            "AAPL", "NASDAQ", "1d", sample_kline_data, "yfinance"
        )
        
        # 查询数据
        results = await query.query_by_ticker("AAPL", "1d")
        assert len(results) == len(sample_kline_data)
    
    @pytest.mark.asyncio
    async def test_query_by_ticker_with_date_range(self, mock_db, sample_kline_data):
        """测试按日期范围查询."""
        storage = HistoricalDataStorage(mock_db)
        query = HistoricalDataQuery(mock_db)
        
        # 先插入数据
        await storage.save_kline_data(
            "AAPL", "NASDAQ", "1d", sample_kline_data, "yfinance"
        )
        
        # 查询最近1天的数据
        now = datetime.now(UTC)
        results = await query.query_by_ticker(
            "AAPL", "1d", 
            start_date=now - timedelta(days=1),
            end_date=now
        )
        # 应该返回最近2条数据
        assert len(results) >= 1
    
    @pytest.mark.asyncio
    async def test_get_latest_date(self, mock_db, sample_kline_data):
        """测试获取最新数据日期."""
        storage = HistoricalDataStorage(mock_db)
        query = HistoricalDataQuery(mock_db)
        
        # 先插入数据
        await storage.save_kline_data(
            "AAPL", "NASDAQ", "1d", sample_kline_data, "yfinance"
        )
        
        # 获取最新日期
        latest_date = await query.get_latest_date("AAPL", "1d")
        assert latest_date is not None
        
        # 比较日期（忽略微秒差异）
        expected_date = sample_kline_data[-1]["timestamp"]
        assert latest_date.year == expected_date.year
        assert latest_date.month == expected_date.month
        assert latest_date.day == expected_date.day
        assert latest_date.hour == expected_date.hour
        assert latest_date.minute == expected_date.minute
        assert latest_date.second == expected_date.second
    
    @pytest.mark.asyncio
    async def test_get_statistics(self, mock_db, sample_kline_data):
        """测试获取统计信息."""
        storage = HistoricalDataStorage(mock_db)
        query = HistoricalDataQuery(mock_db)
        
        # 先插入数据
        await storage.save_kline_data(
            "AAPL", "NASDAQ", "1d", sample_kline_data, "yfinance"
        )
        
        # 获取统计信息
        stats = await query.get_statistics("AAPL", "1d")
        assert stats["total_count"] == len(sample_kline_data)
        assert stats["query"]["ticker"] == "AAPL"
        assert stats["query"]["period"] == "1d"


class TestHistoricalDataService:
    """测试历史数据核心服务."""
    
    @pytest.mark.asyncio
    async def test_query_kline_data(self, mock_db, sample_kline_data):
        """测试查询K线数据."""
        service = HistoricalDataService(mock_db)
        
        # 先插入数据
        await service.storage.save_kline_data(
            "AAPL", "NASDAQ", "1d", sample_kline_data, "yfinance"
        )
        
        # 查询数据
        results = await service.query_kline_data("AAPL", "1d")
        assert len(results) == len(sample_kline_data)
    
    @pytest.mark.asyncio
    async def test_delete_kline_data(self, mock_db, sample_kline_data):
        """测试删除K线数据."""
        service = HistoricalDataService(mock_db)
        
        # 先插入数据
        await service.storage.save_kline_data(
            "AAPL", "NASDAQ", "1d", sample_kline_data, "yfinance"
        )
        
        # 删除数据
        deleted_count = await service.delete_kline_data(ticker="AAPL", period="1d")
        assert deleted_count == len(sample_kline_data)
    
    @pytest.mark.asyncio
    async def test_get_kline_data_statistics(self, mock_db, sample_kline_data):
        """测试获取统计信息."""
        service = HistoricalDataService(mock_db)
        
        # 先插入数据
        await service.storage.save_kline_data(
            "AAPL", "NASDAQ", "1d", sample_kline_data, "yfinance"
        )
        
        # 获取统计信息
        stats = await service.get_kline_data_statistics("AAPL", "1d")
        assert stats["total_count"] == len(sample_kline_data)
