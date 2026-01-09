"""定时任务服务测试."""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, UTC
from bson import ObjectId
from app.services.scheduler_service import SchedulerService
from app.services.stock_service import get_stock_service


class TestSchedulerService:
    """定时任务服务测试类."""

    @pytest.fixture
    def scheduler_service(self):
        """创建调度服务实例."""
        service = SchedulerService()
        # Mock scheduler，避免实际启动
        service.scheduler = MagicMock()
        return service

    @pytest.mark.asyncio
    async def test_create_schedule_success(
        self, scheduler_service, sample_schedule, setup_test_db
    ):
        """测试创建更新计划成功."""
        scheduler_service.db = setup_test_db
        scheduler_service.collection = setup_test_db.update_schedules

        result = await scheduler_service.create_schedule(sample_schedule)

        assert result is not None
        assert result["schedule_type"] == "cron"
        assert result["is_active"] is True
        assert "id" in result

        # 验证已插入数据库
        count = await scheduler_service.collection.count_documents({})
        assert count == 1

    @pytest.mark.asyncio
    async def test_create_schedule_inactive(
        self, scheduler_service, sample_schedule, setup_test_db
    ):
        """测试创建未激活的更新计划."""
        scheduler_service.db = setup_test_db
        scheduler_service.collection = setup_test_db.update_schedules
        schedule_data = {**sample_schedule, "is_active": False}

        result = await scheduler_service.create_schedule(schedule_data)

        assert result["is_active"] is False
        # 未激活的计划不应该注册到调度器
        scheduler_service.scheduler.add_job.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_schedule_success(
        self, scheduler_service, sample_schedule, setup_test_db
    ):
        """测试更新更新计划成功."""
        scheduler_service.db = setup_test_db
        scheduler_service.collection = setup_test_db.update_schedules

        # 先创建
        created = await scheduler_service.create_schedule(sample_schedule)
        schedule_id = created["id"]

        # 更新
        update_data = {
            "schedule_type": "interval",
            "schedule_config": {"interval": 3600},
            "is_active": True,
        }

        result = await scheduler_service.update_schedule(schedule_id, update_data)

        assert result is not None
        assert result["schedule_type"] == "interval"
        assert result["schedule_config"]["interval"] == 3600

    @pytest.mark.asyncio
    async def test_update_schedule_not_found(
        self, scheduler_service, setup_test_db
    ):
        """测试更新不存在的更新计划."""
        scheduler_service.db = setup_test_db
        scheduler_service.collection = setup_test_db.update_schedules

        fake_id = str(ObjectId())
        result = await scheduler_service.update_schedule(fake_id, {"is_active": False})

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_schedule_success(
        self, scheduler_service, sample_schedule, setup_test_db
    ):
        """测试删除更新计划成功."""
        scheduler_service.db = setup_test_db
        scheduler_service.collection = setup_test_db.update_schedules

        # 先创建
        created = await scheduler_service.create_schedule(sample_schedule)
        schedule_id = created["id"]

        # 删除
        result = await scheduler_service.delete_schedule(schedule_id)

        assert result is True

        # 验证已删除
        count = await scheduler_service.collection.count_documents({})
        assert count == 0

        # 验证已从调度器移除
        scheduler_service.scheduler.remove_job.assert_called_once_with(schedule_id)

    @pytest.mark.asyncio
    async def test_delete_schedule_not_found(self, scheduler_service, setup_test_db):
        """测试删除不存在的更新计划."""
        scheduler_service.db = setup_test_db
        scheduler_service.collection = setup_test_db.update_schedules

        fake_id = str(ObjectId())
        result = await scheduler_service.delete_schedule(fake_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_toggle_schedule_activate(
        self, scheduler_service, sample_schedule, setup_test_db
    ):
        """测试切换更新计划为激活状态."""
        scheduler_service.db = setup_test_db
        scheduler_service.collection = setup_test_db.update_schedules

        # 创建未激活的计划
        schedule_data = {**sample_schedule, "is_active": False}
        created = await scheduler_service.create_schedule(schedule_data)
        schedule_id = created["id"]

        # 切换为激活
        result = await scheduler_service.toggle_schedule(schedule_id)

        assert result is not None
        assert result["is_active"] is True

    @pytest.mark.asyncio
    async def test_toggle_schedule_deactivate(
        self, scheduler_service, sample_schedule, setup_test_db
    ):
        """测试切换更新计划为停用状态."""
        scheduler_service.db = setup_test_db
        scheduler_service.collection = setup_test_db.update_schedules

        # 创建激活的计划
        created = await scheduler_service.create_schedule(sample_schedule)
        schedule_id = created["id"]

        # 切换为停用
        result = await scheduler_service.toggle_schedule(schedule_id)

        assert result is not None
        assert result["is_active"] is False

        # 验证已从调度器移除
        scheduler_service.scheduler.remove_job.assert_called_once_with(schedule_id)

    @pytest.mark.asyncio
    async def test_toggle_schedule_not_found(self, scheduler_service, setup_test_db):
        """测试切换不存在的更新计划."""
        scheduler_service.db = setup_test_db
        scheduler_service.collection = setup_test_db.update_schedules

        fake_id = str(ObjectId())
        result = await scheduler_service.toggle_schedule(fake_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_execute_schedule_success(
        self, scheduler_service, sample_schedule, setup_test_db
    ):
        """测试执行更新计划成功."""
        scheduler_service.db = setup_test_db
        scheduler_service.collection = setup_test_db.update_schedules

        # 创建计划
        created = await scheduler_service.create_schedule(sample_schedule)
        schedule_id = created["id"]

        # Mock 更新结果
        # Mock get_stock_service
        mock_stock_service = Mock()
        mock_stock_service.update_all_stocks = AsyncMock(
            return_value={"total": 10, "success": 8, "failed": 2}
        )
        
        with patch("app.services.scheduler_service.get_stock_service", return_value=mock_stock_service):
            # 执行计划
            await scheduler_service._execute_schedule(schedule_id)

        # 验证更新了执行记录
        updated = await scheduler_service.collection.find_one(
            {"_id": ObjectId(schedule_id)}
        )
        assert updated["run_count"] == 1
        assert updated["last_run"] is not None
        assert updated["last_error"] is None

        mock_stock_service.update_all_stocks.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_schedule_error(
        self, scheduler_service, sample_schedule, setup_test_db
    ):
        """测试执行更新计划时发生错误."""
        scheduler_service.db = setup_test_db
        scheduler_service.collection = setup_test_db.update_schedules

        # 创建计划
        created = await scheduler_service.create_schedule(sample_schedule)
        schedule_id = created["id"]

        # Mock get_stock_service
        mock_stock_service = Mock()
        mock_stock_service.update_all_stocks = AsyncMock(side_effect=Exception("Update failed"))
        
        with patch("app.services.scheduler_service.get_stock_service", return_value=mock_stock_service):
            # 执行计划
            await scheduler_service._execute_schedule(schedule_id)

        # 验证错误记录
        updated = await scheduler_service.collection.find_one(
            {"_id": ObjectId(schedule_id)}
        )
        assert updated["error_count"] == 1
        assert updated["last_error"] is not None

    @pytest.mark.asyncio
    async def test_register_schedule_cron(
        self, scheduler_service, sample_schedule, setup_test_db
    ):
        """测试注册 Cron 类型的更新计划."""
        scheduler_service.db = setup_test_db
        scheduler_service.collection = setup_test_db.update_schedules

        # 插入计划
        schedule_doc = {
            **sample_schedule,
            "_id": ObjectId(),
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        await scheduler_service.collection.insert_one(schedule_doc)

        await scheduler_service.register_schedule(schedule_doc)

        # 验证已注册到调度器
        scheduler_service.scheduler.add_job.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_schedule_interval(
        self, scheduler_service, setup_test_db
    ):
        """测试注册间隔类型的更新计划."""
        scheduler_service.db = setup_test_db
        scheduler_service.collection = setup_test_db.update_schedules

        schedule_doc = {
            "schedule_type": "interval",
            "schedule_config": {"interval": 3600},
            "is_active": True,
            "_id": ObjectId(),
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        await scheduler_service.collection.insert_one(schedule_doc)

        await scheduler_service.register_schedule(schedule_doc)

        # 验证已注册到调度器
        scheduler_service.scheduler.add_job.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_schedules(
        self, scheduler_service, sample_schedule, setup_test_db
    ):
        """测试加载所有激活的更新计划."""
        scheduler_service.db = setup_test_db
        scheduler_service.collection = setup_test_db.update_schedules

        # 创建激活和未激活的计划
        active_schedule = {**sample_schedule, "is_active": True}
        inactive_schedule = {**sample_schedule, "is_active": False, "schedule_config": {"cron": "0 10 * * *"}}

        await scheduler_service.create_schedule(active_schedule)
        await scheduler_service.create_schedule(inactive_schedule)

        # 加载计划
        await scheduler_service.load_schedules()

        # 验证只注册了激活的计划
        # add_job 应该被调用一次（只有激活的计划）
        assert scheduler_service.scheduler.add_job.call_count >= 1
