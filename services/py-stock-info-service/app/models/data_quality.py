"""数据质量日志模型."""

from datetime import datetime, UTC
from typing import Optional
from app.database import get_database


async def init_data_quality_logs_collection():
    """初始化数据质量日志集合."""
    db = get_database()
    collection = db.data_quality_logs
    
    # 创建索引：按股票、周期、检查类型、状态、检查日期查询
    await collection.create_index([
        ("ticker", 1),
        ("period", 1),
        ("check_type", 1),
        ("status", 1),
        ("check_date", -1)
    ])
    
    # 创建索引：按状态查询（查询待修复的问题）
    await collection.create_index("status")
    
    print("✅ 数据质量日志集合索引初始化完成")


def data_quality_log_from_dict(log_dict: dict) -> dict:
    """将 MongoDB 文档转换为响应格式."""
    if "_id" in log_dict:
        log_dict["id"] = str(log_dict.pop("_id"))
    return log_dict


def prepare_data_quality_log(
    ticker: str,
    period: str,
    check_type: str,
    status: str = "pending",
    description: Optional[str] = None,
    fix_action: Optional[str] = None
) -> dict:
    """准备数据质量日志文档.
    
    Args:
        ticker: 股票代码
        period: 时间周期
        check_type: 检查类型（missing_data, abnormal_value, inconsistent_data, duplicate_data）
        status: 状态（pending, fixed, failed）
        description: 问题描述
        fix_action: 修复操作
        
    Returns:
        dict: 格式化后的文档
    """
    now = datetime.now(UTC)
    
    document = {
        "ticker": ticker,
        "period": period,
        "check_type": check_type,
        "check_date": now,
        "status": status,
        "description": description,
        "fix_action": fix_action,
        "created_at": now,
        "updated_at": now
    }
    
    # 移除 None 值
    document = {k: v for k, v in document.items() if v is not None}
    
    return document


# 检查类型常量
class CheckType:
    """数据质量检查类型."""
    MISSING_DATA = "missing_data"           # 缺失数据
    ABNORMAL_VALUE = "abnormal_value"       # 异常值
    INCONSISTENT_DATA = "inconsistent_data" # 不一致数据
    DUPLICATE_DATA = "duplicate_data"       # 重复数据


# 状态常量
class CheckStatus:
    """数据质量检查状态."""
    PENDING = "pending"   # 待修复
    FIXED = "fixed"       # 已修复
    FAILED = "failed"     # 修复失败
