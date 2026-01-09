"""更新计划数据模型."""

from datetime import datetime, UTC
from typing import Optional
from app.database import get_database


async def init_schedule_indexes():
    """初始化更新计划集合索引."""
    db = get_database()
    collection = db.update_schedules

    # 创建普通索引：is_active
    await collection.create_index("is_active")

    # 创建普通索引：next_run（用于查询待执行任务）
    await collection.create_index("next_run")

    print("✅ 更新计划集合索引初始化完成")


def schedule_from_dict(schedule_dict: dict) -> dict:
    """将 MongoDB 文档转换为响应格式."""
    if "_id" in schedule_dict:
        schedule_dict["id"] = str(schedule_dict.pop("_id"))
    return schedule_dict


def prepare_schedule_document(schedule_data: dict) -> dict:
    """准备更新计划文档用于存储."""
    now = datetime.now(UTC)
    document = {
        "schedule_type": schedule_data["schedule_type"],
        "schedule_config": schedule_data["schedule_config"],
        "is_active": schedule_data.get("is_active", True),
        "run_count": schedule_data.get("run_count", 0),
        "error_count": schedule_data.get("error_count", 0),
        "last_error": schedule_data.get("last_error"),
        "last_run": schedule_data.get("last_run"),
        "next_run": schedule_data.get("next_run"),
        "updated_at": now,
    }

    # 如果是新文档，设置 created_at
    if "created_at" not in schedule_data:
        document["created_at"] = now

    return document
