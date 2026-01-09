"""更新计划模式."""

from datetime import datetime, UTC
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class ScheduleConfigBase(BaseModel):
    """调度配置基础模式."""

    pass


class CronScheduleConfig(ScheduleConfigBase):
    """Cron 调度配置."""

    cron: str = Field(..., description="Cron 表达式，如 '0 9 * * 1-5'（工作日 9:00）")


class IntervalScheduleConfig(ScheduleConfigBase):
    """间隔调度配置."""

    interval: int = Field(..., description="间隔秒数", gt=0)


class ScheduleBase(BaseModel):
    """更新计划基础模式."""

    schedule_type: Literal["cron", "interval"] = Field(..., description="调度类型")
    schedule_config: CronScheduleConfig | IntervalScheduleConfig = Field(
        ..., description="调度配置"
    )
    is_active: bool = Field(default=True, description="是否激活")


class ScheduleCreate(BaseModel):
    """创建更新计划的模式."""

    schedule_type: Literal["cron", "interval"] = Field(..., description="调度类型")
    schedule_config: dict = Field(..., description="调度配置（cron 或 interval）")
    is_active: bool = Field(default=True, description="是否激活")


class ScheduleUpdate(BaseModel):
    """更新更新计划的模式."""

    schedule_type: Optional[Literal["cron", "interval"]] = Field(
        None, description="调度类型"
    )
    schedule_config: Optional[dict] = Field(None, description="调度配置")
    is_active: Optional[bool] = Field(None, description="是否激活")


class ScheduleResponse(ScheduleBase):
    """更新计划响应模式."""

    id: str = Field(..., description="更新计划 ID")
    last_run: Optional[datetime] = Field(None, description="最后执行时间")
    next_run: Optional[datetime] = Field(None, description="下次执行时间")
    run_count: int = Field(default=0, description="执行次数")
    error_count: int = Field(default=0, description="错误次数")
    last_error: Optional[str] = Field(None, description="最后错误信息")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "schedule_type": "cron",
                "schedule_config": {"cron": "0 9 * * 1-5"},
                "is_active": True,
                "last_run": "2024-01-01T09:00:00Z",
                "next_run": "2024-01-02T09:00:00Z",
                "run_count": 100,
                "error_count": 2,
                "last_error": None,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }
    )


class ScheduleQueryParams(BaseModel):
    """更新计划查询参数."""

    is_active: Optional[bool] = Field(None, description="是否激活")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")


class ScheduleStatusResponse(BaseModel):
    """更新计划状态统计响应."""

    total: int = Field(..., description="总计划数")
    active: int = Field(..., description="激活数")
    inactive: int = Field(..., description="未激活数")
    next_run_count: int = Field(..., description="待执行数")
