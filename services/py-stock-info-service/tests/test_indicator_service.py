"""技术指标服务单元测试."""

import pytest
from datetime import datetime, UTC, timedelta
from app.services.indicators import IndicatorService


@pytest.fixture
def indicator_service(setup_test_db):
    """创建技术指标服务实例."""
    return IndicatorService(setup_test_db)


@pytest.fixture
def sample_kline_data():
    """生成测试用K线数据."""
    base_date = datetime(2025, 1, 1, tzinfo=UTC)
    data = []
    
    # 生成50天的K线数据（足够计算各种指标，包括 MACD）
    for i in range(50):
        date = base_date + timedelta(days=i)
        # 简单的价格模拟（上涨趋势）
        price = 100 + i * 0.5
        data.append({
            "timestamp": date,
            "open": price,
            "high": price + 1,
            "low": price - 1,
            "close": price + 0.5,
            "volume": 1000000 + i * 10000,
        })
    
    return data


@pytest.mark.asyncio
async def test_get_supported_indicators(indicator_service):
    """测试获取支持的指标列表."""
    indicators = indicator_service.get_supported_indicators()
    
    assert len(indicators) > 0
    assert any(ind["type"] == "MA" for ind in indicators)
    assert any(ind["type"] == "EMA" for ind in indicators)
    assert any(ind["type"] == "RSI" for ind in indicators)
    assert any(ind["type"] == "MACD" for ind in indicators)
    assert any(ind["type"] == "BOLL" for ind in indicators)


@pytest.mark.asyncio
async def test_calculate_ma(indicator_service, sample_kline_data):
    """测试计算 MA 指标."""
    # 先保存K线数据
    await indicator_service.historical_data_service.storage.save_kline_data(
        ticker="TEST",
        market="TEST",
        period="1d",
        kline_data=sample_kline_data,
        data_source="test"
    )
    
    # 计算 MA5
    result = await indicator_service.calculate_indicator(
        ticker="TEST",
        indicator_type="MA",
        indicator_name="MA5",
        period="1d",
        params={"period": 5},
        use_cache=False
    )
    
    assert len(result) > 0
    assert all("timestamp" in item for item in result)
    assert all("value" in item for item in result)
    assert all("params" in item for item in result)


@pytest.mark.asyncio
async def test_calculate_ema(indicator_service, sample_kline_data):
    """测试计算 EMA 指标."""
    # 先保存K线数据
    # HistoricalDataService is already available
    # Use indicator_service.historical_data_service
    await indicator_service.historical_data_service.storage.save_kline_data(
        ticker="TEST",
        market="TEST",
        period="1d",
        kline_data=sample_kline_data,
        data_source="test"
    )
    
    # 计算 EMA12
    result = await indicator_service.calculate_indicator(
        ticker="TEST",
        indicator_type="EMA",
        indicator_name="EMA12",
        period="1d",
        params={"period": 12},
        use_cache=False
    )
    
    assert len(result) > 0
    assert all("timestamp" in item for item in result)
    assert all("value" in item for item in result)


@pytest.mark.asyncio
async def test_calculate_rsi(indicator_service, sample_kline_data):
    """测试计算 RSI 指标."""
    # 先保存K线数据
    # HistoricalDataService is already available
    # Use indicator_service.historical_data_service
    await indicator_service.historical_data_service.storage.save_kline_data(
        ticker="TEST",
        market="TEST",
        period="1d",
        kline_data=sample_kline_data,
        data_source="test"
    )
    
    # 计算 RSI14
    result = await indicator_service.calculate_indicator(
        ticker="TEST",
        indicator_type="RSI",
        indicator_name="RSI14",
        period="1d",
        params={"period": 14},
        use_cache=False
    )
    
    assert len(result) > 0
    assert all("timestamp" in item for item in result)
    assert all("value" in item for item in result)
    # RSI 值应该在 0-100 之间
    assert all(0 <= item["value"] <= 100 for item in result)


@pytest.mark.asyncio
async def test_calculate_macd(indicator_service, sample_kline_data):
    """测试计算 MACD 指标."""
    # 先保存K线数据
    # HistoricalDataService is already available
    # Use indicator_service.historical_data_service
    await indicator_service.historical_data_service.storage.save_kline_data(
        ticker="TEST",
        market="TEST",
        period="1d",
        kline_data=sample_kline_data,
        data_source="test"
    )
    
    # 计算 MACD_DIF
    result = await indicator_service.calculate_indicator(
        ticker="TEST",
        indicator_type="MACD",
        indicator_name="MACD_DIF",
        period="1d",
        params={"fast": 12, "slow": 26, "signal": 9},
        use_cache=False
    )
    
    assert len(result) > 0
    assert all("timestamp" in item for item in result)
    assert all("value" in item for item in result)


@pytest.mark.asyncio
async def test_calculate_boll(indicator_service, sample_kline_data):
    """测试计算布林带指标."""
    # 先保存K线数据
    # HistoricalDataService is already available
    # Use indicator_service.historical_data_service
    await indicator_service.historical_data_service.storage.save_kline_data(
        ticker="TEST",
        market="TEST",
        period="1d",
        kline_data=sample_kline_data,
        data_source="test"
    )
    
    # 计算 BOLL_UP
    result_up = await indicator_service.calculate_indicator(
        ticker="TEST",
        indicator_type="BOLL",
        indicator_name="BOLL_UP",
        period="1d",
        params={"period": 20, "std_dev": 2.0},
        use_cache=False
    )
    
    # 计算 BOLL_MID
    result_mid = await indicator_service.calculate_indicator(
        ticker="TEST",
        indicator_type="BOLL",
        indicator_name="BOLL_MID",
        period="1d",
        params={"period": 20, "std_dev": 2.0},
        use_cache=False
    )
    
    # 计算 BOLL_LOW
    result_low = await indicator_service.calculate_indicator(
        ticker="TEST",
        indicator_type="BOLL",
        indicator_name="BOLL_LOW",
        period="1d",
        params={"period": 20, "std_dev": 2.0},
        use_cache=False
    )
    
    assert len(result_up) > 0
    assert len(result_mid) > 0
    assert len(result_low) > 0
    
    # 检查布林带逻辑：上轨 > 中轨 > 下轨
    for i in range(len(result_up)):
        assert result_up[i]["value"] >= result_mid[i]["value"]
        assert result_mid[i]["value"] >= result_low[i]["value"]


@pytest.mark.asyncio
async def test_indicator_cache(indicator_service, sample_kline_data):
    """测试指标计算缓存机制."""
    # 先保存K线数据
    # HistoricalDataService is already available
    # Use indicator_service.historical_data_service
    await indicator_service.historical_data_service.storage.save_kline_data(
        ticker="TEST_CACHE",
        market="TEST",
        period="1d",
        kline_data=sample_kline_data,
        data_source="test"
    )
    
    # 第一次计算（不使用缓存）
    result1 = await indicator_service.calculate_indicator(
        ticker="TEST_CACHE",
        indicator_type="MA",
        indicator_name="MA5",
        period="1d",
        params={"period": 5},
        use_cache=False
    )
    
    # 等待数据保存完成
    import asyncio
    await asyncio.sleep(0.5)
    
    # 第二次计算（使用缓存）
    result2 = await indicator_service.calculate_indicator(
        ticker="TEST_CACHE",
        indicator_type="MA",
        indicator_name="MA5",
        period="1d",
        params={"period": 5},
        use_cache=True
    )
    
    # 验证结果相同
    assert len(result1) == len(result2)
    assert result1[0]["value"] == result2[0]["value"]


@pytest.mark.asyncio
async def test_query_indicator_data(indicator_service, sample_kline_data):
    """测试查询指标数据."""
    # 先保存K线数据
    # HistoricalDataService is already available
    # Use indicator_service.historical_data_service
    await indicator_service.historical_data_service.storage.save_kline_data(
        ticker="TEST_QUERY",
        market="TEST",
        period="1d",
        kline_data=sample_kline_data,
        data_source="test"
    )
    
    # 计算指标并直接保存（不使用异步）
    result = await indicator_service.calculate_indicator(
        ticker="TEST_QUERY",
        indicator_type="MA",
        indicator_name="MA5",
        period="1d",
        params={"period": 5},
        use_cache=False
    )
    
    # 直接同步保存到数据库
    await indicator_service.storage.save_indicator_data(
        ticker="TEST_QUERY",
        period="1d",
        indicator_type="MA",
        indicator_name="MA5",
        indicator_data=result
    )
    
    # 等待数据保存完成
    import asyncio
    await asyncio.sleep(0.1)
    
    # 查询指标数据
    result = await indicator_service.query_indicator_data(
        ticker="TEST_QUERY",
        indicator_name="MA5",
        period="1d"
    )
    
    assert len(result) > 0
    assert all("timestamp" in item for item in result)
    assert all("value" in item for item in result)


@pytest.mark.asyncio
async def test_batch_calculate_indicators(indicator_service, sample_kline_data):
    """测试批量计算指标."""
    # 先保存K线数据
    # HistoricalDataService is already available
    # Use indicator_service.historical_data_service
    await indicator_service.historical_data_service.storage.save_kline_data(
        ticker="TEST_BATCH",
        market="TEST",
        period="1d",
        kline_data=sample_kline_data,
        data_source="test"
    )
    
    # 批量计算多个指标
    indicator_names = ["MA5", "MA10", "EMA12", "RSI14"]
    
    progress_updates = []
    
    async def progress_callback(progress_data):
        """进度回调函数."""
        progress_updates.append(progress_data)
    
    result = await indicator_service.calculate_batch_indicators(
        ticker="TEST_BATCH",
        indicator_names=indicator_names,
        period="1d",
        progress_callback=progress_callback
    )
    
    # 验证结果
    assert result["total"] == len(indicator_names)
    assert result["success"] > 0
    assert "results" in result
    
    # 验证进度更新
    assert len(progress_updates) > 0
    assert any(p["stage"] == "init" for p in progress_updates)
    assert any(p["stage"] == "calculating" for p in progress_updates)
    assert any(p["stage"] == "completed" for p in progress_updates)
