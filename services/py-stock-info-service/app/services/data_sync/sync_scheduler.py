"""同步调度器（管理定时任务）."""

import logging
from typing import Optional, Callable
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class SyncScheduler:
    """同步调度器（管理定时任务）."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """初始化同步调度器.
        
        Args:
            db: MongoDB 数据库实例
        """
        self.db = db
        self.scheduler = AsyncIOScheduler()
    
    def start(self):
        """启动定时任务调度器."""
        logger.info("启动定时任务调度器")
        self.scheduler.start()
        logger.info("定时任务调度器已启动")
    
    def shutdown(self, wait: bool = True):
        """关闭定时任务调度器.
        
        Args:
            wait: 是否等待所有任务完成
        """
        logger.info("关闭定时任务调度器")
        self.scheduler.shutdown(wait=wait)
        logger.info("定时任务调度器已关闭")
    
    def add_daily_sync_job(
        self,
        job_func: Callable,
        market: str,
        hour: int,
        minute: int = 0,
        job_id: Optional[str] = None
    ):
        """添加每日同步任务.
        
        Args:
            job_func: 任务函数
            market: 市场（A股、美股等）
            hour: 小时（0-23）
            minute: 分钟（0-59）
            job_id: 任务ID（可选）
        """
        if job_id is None:
            job_id = f"daily_sync_{market}_{hour}_{minute}"
        
        logger.info(f"添加每日同步任务：{job_id}（{hour}:{minute}）")
        
        trigger = CronTrigger(hour=hour, minute=minute)
        
        self.scheduler.add_job(
            job_func,
            trigger=trigger,
            id=job_id,
            kwargs={"market": market},
            replace_existing=True,
            misfire_grace_time=3600  # 1小时的容错时间
        )
        
        logger.info(f"每日同步任务已添加：{job_id}")
    
    def add_quality_check_job(
        self,
        job_func: Callable,
        day_of_week: str,
        hour: int,
        minute: int = 0,
        job_id: Optional[str] = None
    ):
        """添加数据质量检查任务.
        
        Args:
            job_func: 任务函数
            day_of_week: 星期几（mon, tue, wed, thu, fri, sat, sun）
            hour: 小时（0-23）
            minute: 分钟（0-59）
            job_id: 任务ID（可选）
        """
        if job_id is None:
            job_id = f"quality_check_{day_of_week}_{hour}_{minute}"
        
        logger.info(f"添加质量检查任务：{job_id}（{day_of_week} {hour}:{minute}）")
        
        trigger = CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute)
        
        self.scheduler.add_job(
            job_func,
            trigger=trigger,
            id=job_id,
            replace_existing=True,
            misfire_grace_time=3600  # 1小时的容错时间
        )
        
        logger.info(f"质量检查任务已添加：{job_id}")
    
    def remove_job(self, job_id: str):
        """移除定时任务.
        
        Args:
            job_id: 任务ID
        """
        logger.info(f"移除定时任务：{job_id}")
        self.scheduler.remove_job(job_id)
        logger.info(f"定时任务已移除：{job_id}")
    
    def get_jobs(self):
        """获取所有定时任务."""
        return self.scheduler.get_jobs()
