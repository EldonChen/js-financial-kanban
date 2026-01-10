"""数据源配置验证器."""

import logging
from typing import Dict, Any, List
from app.config import settings

logger = logging.getLogger(__name__)


def validate_data_source_config() -> Dict[str, Any]:
    """验证数据源配置.
    
    Returns:
        验证结果字典，包含：
        - valid: 是否有效
        - enabled_providers: 已启用的数据源列表
        - warnings: 警告信息列表
        - errors: 错误信息列表
    """
    result = {
        "valid": True,
        "enabled_providers": [],
        "warnings": [],
        "errors": [],
    }

    # 检查第一优先级数据源
    if settings.enable_akshare:
        result["enabled_providers"].append("akshare (第一优先级)")
    
    if settings.enable_yfinance:
        result["enabled_providers"].append("yfinance (第一优先级)")
    
    if settings.enable_easyquotation:
        result["enabled_providers"].append("easyquotation (第一优先级)")

    # 检查第二优先级数据源配置
    if settings.enable_tushare:
        if not settings.tushare_token:
            result["warnings"].append(
                "Tushare 已启用但未配置 token，将跳过注册"
            )
        else:
            result["enabled_providers"].append("tushare (第二优先级)")

    if settings.enable_iex_cloud:
        if not settings.iex_cloud_api_key:
            result["warnings"].append(
                "IEX Cloud 已启用但未配置 API Key，将跳过注册"
            )
        else:
            result["enabled_providers"].append("iex_cloud (第二优先级)")

    if settings.enable_alpha_vantage:
        if not settings.alpha_vantage_api_key:
            result["warnings"].append(
                "Alpha Vantage 已启用但未配置 API Key，将跳过注册"
            )
        else:
            result["enabled_providers"].append("alpha_vantage (第二优先级)")

    # 验证至少有一个第一优先级数据源启用
    first_priority_enabled = (
        settings.enable_akshare
        or settings.enable_yfinance
        or settings.enable_easyquotation
    )

    if not first_priority_enabled:
        result["errors"].append(
            "至少需要启用一个第一优先级数据源（akshare、yfinance 或 easyquotation）"
        )
        result["valid"] = False

    return result


def get_data_source_status() -> Dict[str, Any]:
    """获取数据源状态信息.
    
    Returns:
        数据源状态字典
    """
    from app.services.providers.router import get_stock_data_router

    router = get_stock_data_router()
    
    status = {
        "total_providers": len(router.providers),
        "providers": {},
        "market_coverage": {},
    }

    # 获取每个数据源的状态
    for name, provider in router.providers.items():
        status["providers"][name] = {
            "name": provider.name,
            "supported_markets": provider.supported_markets,
            "priority": provider.priority,
        }

    # 获取市场覆盖情况
    for market, providers in router.market_providers.items():
        status["market_coverage"][market] = providers

    return status
