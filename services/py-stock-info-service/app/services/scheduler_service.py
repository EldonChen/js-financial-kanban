"""定时任务服务."""

import logging
from datetime import datetime, UTC
from typing import Optional, Dict, Any
from bson import ObjectId

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.database import get_database
from app.models.schedule import schedule_from_dict, prepare_schedule_document
from app.services.stock_service import get_stock_service

logger = logging.getLogger(__name__)


class SchedulerService:
    """定时任务调度服务."""

    def __init__(self):
        """初始化调度服务."""
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.db = get_database()
        self.collection = self.db.update_schedules

    def start(self):
        """启动调度器."""
        if self.scheduler is None:
            self.scheduler = AsyncIOScheduler()
            self.scheduler.start()
            logger.info("✅ 定时任务调度器已启动")

    def shutdown(self):
        """关闭调度器."""
        if self.scheduler:
            self.scheduler.shutdown()
            self.scheduler = None
            logger.info("✅ 定时任务调度器已关闭")

    async def load_schedules(self):
        """从数据库加载所有激活的更新计划并注册任务."""
        if not self.scheduler:
            logger.warning("调度器未启动，无法加载计划")
            return

        # 查询所有激活的计划
        async for schedule in self.collection.find({"is_active": True}):
            await self.register_schedule(schedule)

        logger.info("✅ 已加载所有激活的更新计划")

    async def register_schedule(self, schedule: Dict[str, Any]):
        """注册一个更新计划到调度器.

        Args:
            schedule: 更新计划文档
        """
        if not self.scheduler:
            logger.warning("调度器未启动，无法注册计划")
            return

        schedule_id = str(schedule["_id"])
        schedule_type = schedule["schedule_type"]
        schedule_config = schedule["schedule_config"]

        try:
            # 创建触发器
            if schedule_type == "cron":
                cron_expr = schedule_config.get("cron")
                if not cron_expr:
                    logger.error(f"计划 {schedule_id} 的 cron 表达式为空")
                    return
                trigger = CronTrigger.from_crontab(cron_expr)
            elif schedule_type == "interval":
                interval_seconds = schedule_config.get("interval")
                if not interval_seconds:
                    logger.error(f"计划 {schedule_id} 的间隔时间为空")
                    return
                trigger = IntervalTrigger(seconds=interval_seconds)
            else:
                logger.error(f"计划 {schedule_id} 的调度类型无效: {schedule_type}")
                return

            # 注册任务
            self.scheduler.add_job(
                self._execute_schedule,
                trigger=trigger,
                id=schedule_id,
                replace_existing=True,
                args=[schedule_id],
            )

            logger.info(f"✅ 已注册更新计划: {schedule_id} ({schedule_type})")

        except Exception as e:
            logger.error(f"注册更新计划 {schedule_id} 失败: {str(e)}")

    async def unregister_schedule(self, schedule_id: str):
        """从调度器移除一个更新计划.

        Args:
            schedule_id: 更新计划 ID
        """
        if not self.scheduler:
            return

        try:
            self.scheduler.remove_job(schedule_id)
            logger.info(f"✅ 已移除更新计划: {schedule_id}")
        except Exception as e:
            logger.warning(f"移除更新计划 {schedule_id} 失败: {str(e)}")

    async def _execute_schedule(self, schedule_id: str):
        """执行更新计划（更新所有股票）.

        Args:
            schedule_id: 更新计划 ID
        """
        logger.info(f"开始执行更新计划: {schedule_id}")

        try:
            # 更新计划的执行记录
            now = datetime.now(UTC)
            await self.collection.update_one(
                {"_id": ObjectId(schedule_id)},
                {
                    "$set": {
                        "last_run": now,
                        "updated_at": now,
                    },
                    "$inc": {"run_count": 1},
                },
            )

            # 执行更新所有股票
            result = await get_stock_service().update_all_stocks()

            # 更新计划的执行结果
            await self.collection.update_one(
                {"_id": ObjectId(schedule_id)},
                {
                    "$set": {
                        "updated_at": datetime.now(UTC),
                        "last_error": None,
                    },
                },
            )

            logger.info(
                f"更新计划 {schedule_id} 执行完成: 总数 {result['total']}, "
                f"成功 {result['success']}, 失败 {result['failed']}"
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"更新计划 {schedule_id} 执行失败: {error_msg}")

            # 更新错误记录
            try:
                await self.collection.update_one(
                    {"_id": ObjectId(schedule_id)},
                    {
                        "$set": {
                            "last_error": error_msg,
                            "updated_at": datetime.now(UTC),
                        },
                        "$inc": {"error_count": 1},
                    },
                )
            except Exception as update_error:
                logger.error(f"更新计划 {schedule_id} 错误记录失败: {str(update_error)}")

    async def create_schedule(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新的更新计划.

        Args:
            schedule_data: 更新计划数据

        Returns:
            创建的更新计划
        """
        # 准备文档
        document = prepare_schedule_document(schedule_data)

        # 插入数据库
        result = await self.collection.insert_one(document)
        schedule_id = str(result.inserted_id)

        # 如果计划是激活的，立即注册到调度器
        if document.get("is_active", True):
            schedule = await self.collection.find_one({"_id": result.inserted_id})
            await self.register_schedule(schedule)

        logger.info(f"✅ 已创建更新计划: {schedule_id}")
        schedule = await self.collection.find_one({"_id": result.inserted_id})
        return schedule_from_dict(schedule)

    async def update_schedule(
        self, schedule_id: str, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新更新计划.

        Args:
            schedule_id: 更新计划 ID
            update_data: 更新数据

        Returns:
            更新后的计划，如果不存在返回 None
        """
        # 获取原计划
        old_schedule = await self.collection.find_one({"_id": ObjectId(schedule_id)})
        if not old_schedule:
            return None

        # 准备更新文档
        update_doc = {}
        if "schedule_type" in update_data:
            update_doc["schedule_type"] = update_data["schedule_type"]
        if "schedule_config" in update_data:
            update_doc["schedule_config"] = update_data["schedule_config"]
        if "is_active" in update_data:
            update_doc["is_active"] = update_data["is_active"]

        update_doc["updated_at"] = datetime.now(UTC)

        # 更新数据库
        await self.collection.update_one(
            {"_id": ObjectId(schedule_id)},
            {"$set": update_doc},
        )

        # 重新注册任务（如果计划是激活的）
        if update_doc.get("is_active", old_schedule.get("is_active", True)):
            new_schedule = await self.collection.find_one({"_id": ObjectId(schedule_id)})
            await self.register_schedule(new_schedule)
        else:
            # 如果计划被停用，移除任务
            await self.unregister_schedule(schedule_id)

        logger.info(f"✅ 已更新更新计划: {schedule_id}")
        new_schedule = await self.collection.find_one({"_id": ObjectId(schedule_id)})
        return schedule_from_dict(new_schedule)

    async def delete_schedule(self, schedule_id: str) -> bool:
        """删除更新计划.

        Args:
            schedule_id: 更新计划 ID

        Returns:
            是否删除成功
        """
        # 先从调度器移除
        await self.unregister_schedule(schedule_id)

        # 从数据库删除
        result = await self.collection.delete_one({"_id": ObjectId(schedule_id)})
        logger.info(f"✅ 已删除更新计划: {schedule_id}")
        return result.deleted_count > 0

    async def toggle_schedule(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """切换更新计划的激活状态.

        Args:
            schedule_id: 更新计划 ID

        Returns:
            更新后的计划，如果不存在返回 None
        """
        schedule = await self.collection.find_one({"_id": ObjectId(schedule_id)})
        if not schedule:
            return None

        new_is_active = not schedule.get("is_active", False)

        # 更新状态
        await self.collection.update_one(
            {"_id": ObjectId(schedule_id)},
            {
                "$set": {
                    "is_active": new_is_active,
                    "updated_at": datetime.now(UTC),
                }
            },
        )

        # 注册或移除任务
        if new_is_active:
            updated_schedule = await self.collection.find_one(
                {"_id": ObjectId(schedule_id)}
            )
            await self.register_schedule(updated_schedule)
        else:
            await self.unregister_schedule(schedule_id)

        logger.info(f"✅ 已切换更新计划 {schedule_id} 的激活状态: {new_is_active}")
        updated_schedule = await self.collection.find_one({"_id": ObjectId(schedule_id)})
        return schedule_from_dict(updated_schedule)


# 创建全局服务实例（延迟初始化）
_scheduler_service: SchedulerService | None = None


def get_scheduler_service() -> SchedulerService:
    """获取调度服务实例（延迟初始化）."""
    global _scheduler_service
    if _scheduler_service is None:
        _scheduler_service = SchedulerService()
    return _scheduler_service


# 为了向后兼容，提供一个属性访问
class SchedulerServiceProxy:
    """调度服务代理，支持延迟初始化."""

    def __getattr__(self, name):
        return getattr(get_scheduler_service(), name)


scheduler_service = SchedulerServiceProxy()
