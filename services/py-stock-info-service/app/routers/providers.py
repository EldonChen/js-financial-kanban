"""数据源管理路由."""

from fastapi import APIRouter, HTTPException, status
from app.services.providers.config_validator import get_data_source_status
from app.schemas.response import success_response

router = APIRouter(prefix="/api/v1/providers", tags=["providers"])


@router.get("/status", response_model=dict)
async def get_provider_status():
    """获取数据源状态信息.
    
    返回当前已注册的数据源信息，包括：
    - 数据源列表
    - 支持的市场
    - 市场覆盖情况
    """
    try:
        status_info = get_data_source_status()
        return success_response(data=status_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据源状态失败: {str(e)}",
        )
