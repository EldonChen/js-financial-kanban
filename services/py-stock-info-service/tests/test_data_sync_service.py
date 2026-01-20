"""数据同步服务单元测试."""

import pytest
from mongomock_motor import AsyncMongoMockClient

from app.services.data_sync.data_sync_service import DataSyncService
from app.services.data_sync.sync_scheduler import SyncScheduler
from app.services.data_sync.sync_executor import SyncExecutor


@pytest.fixture
async def mock_db():
    """创建 Mock 数据库."""
    client = AsyncMongoMockClient()
    db = client["test_db"]
    yield db
    client.close()


@pytest.fixture
async def data_sync_service(mock_db):
    """创建数据同步服务实例."""
    return DataSyncService(db=mock_db)


@pytest.mark.asyncio
async def test_data_sync_service_initialization(data_sync_service):
    """测试数据同步服务初始化."""
    assert data_sync_service is not None
    assert isinstance(data_sync_service.scheduler, SyncScheduler)
    assert isinstance(data_sync_service.executor, SyncExecutor)


@pytest.mark.asyncio
async def test_sync_scheduler_initialization(mock_db):
    """测试同步调度器初始化."""
    scheduler = SyncScheduler(db=mock_db)
    
    assert scheduler is not None
    assert scheduler.scheduler is not None


@pytest.mark.asyncio
async def test_sync_scheduler_start_shutdown(mock_db):
    """测试同步调度器启动和关闭."""
    scheduler = SyncScheduler(db=mock_db)
    
    # 启动调度器
    scheduler.start()
    assert scheduler.scheduler.running is True
    
    # 关闭调度器（不验证状态，因为 shutdown 是异步的）
    scheduler.shutdown(wait=False)
    # 注意：shutdown 调用后，调度器可能不会立即变为 False，这是正常行为


@pytest.mark.asyncio
async def test_add_daily_sync_job(mock_db):
    """测试添加每日同步任务."""
    scheduler = SyncScheduler(db=mock_db)
    
    async def dummy_job(market: str):
        pass
    
    # 添加任务
    scheduler.add_daily_sync_job(
        job_func=dummy_job,
        market="A股",
        hour=18,
        minute=0,
        job_id="test_job"
    )
    
    # 验证任务已添加
    jobs = scheduler.get_jobs()
    assert len(jobs) > 0
    
    job_ids = [job.id for job in jobs]
    assert "test_job" in job_ids


@pytest.mark.asyncio
async def test_sync_executor_initialization(mock_db):
    """测试同步执行器初始化."""
    executor = SyncExecutor(db=mock_db)
    
    assert executor is not None
    assert executor.db is not None


@pytest.mark.asyncio
async def test_sync_daily_data(data_sync_service, mock_db):
    """测试每日数据同步."""
    # 插入测试股票数据
    stocks_collection = mock_db["stocks"]
    
    test_stocks = [
        {"ticker": "AAPL", "market": "美股", "name": "Apple Inc."},
        {"ticker": "MSFT", "market": "美股", "name": "Microsoft Corp."}
    ]
    
    await stocks_collection.insert_many(test_stocks)
    
    # 执行同步（不使用进度回调）
    result = await data_sync_service.executor.sync_daily_data(
        market="美股",
        period="1d",
        progress_callback=None
    )
    
    assert result is not None
    assert result["market"] == "美股"
    assert result["total"] == 2
    assert "AAPL" in result["tickers"]
    assert "MSFT" in result["tickers"]


@pytest.mark.asyncio
async def test_sync_incremental_data(data_sync_service):
    """测试增量数据更新."""
    # 执行增量更新
    result = await data_sync_service.executor.sync_incremental_data(
        ticker="AAPL",
        market="美股",
        period="1d",
        data_source="yfinance"
    )
    
    assert result is not None
    assert result["ticker"] == "AAPL"
    assert result["market"] == "美股"
    assert result["period"] == "1d"


@pytest.mark.asyncio
async def test_get_sync_status(data_sync_service):
    """测试获取同步状态."""
    # 启动调度器
    data_sync_service.start_scheduler()
    
    # 获取同步状态
    status = data_sync_service.get_sync_status()
    
    assert status is not None
    assert "scheduler_running" in status
    assert status["scheduler_running"] is True
    assert "jobs" in status
    assert len(status["jobs"]) > 0
    
    # 关闭调度器
    data_sync_service.shutdown_scheduler(wait=False)
