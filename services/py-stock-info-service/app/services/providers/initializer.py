"""数据源初始化模块."""

import logging
from app.services.providers.router import get_stock_data_router
from app.services.providers.akshare_provider import AkshareProvider
from app.services.providers.yfinance_provider import YFinanceProvider
from app.services.providers.easyquotation_provider import EasyQuotationProvider
from app.services.providers.config_validator import validate_data_source_config

logger = logging.getLogger(__name__)


def initialize_providers(
    enable_akshare: bool = True,
    enable_yfinance: bool = True,
    enable_easyquotation: bool = False,
    # 第二优先级数据源（可选）
    enable_tushare: bool = False,
    tushare_token: str = "",
    enable_iex_cloud: bool = False,
    iex_cloud_api_key: str = "",
    enable_alpha_vantage: bool = False,
    alpha_vantage_api_key: str = "",
) -> None:
    """初始化并注册所有数据源.
    
    Args:
        enable_akshare: 是否启用 akshare（第一优先级，默认启用）
        enable_yfinance: 是否启用 yfinance（第一优先级，默认启用）
        enable_easyquotation: 是否启用 easyquotation（第一优先级，默认关闭）
        enable_tushare: 是否启用 Tushare（第二优先级，需要 token）
        tushare_token: Tushare token（如果启用 Tushare）
        enable_iex_cloud: 是否启用 IEX Cloud（第二优先级，需要 API Key）
        iex_cloud_api_key: IEX Cloud API Key（如果启用 IEX Cloud）
        enable_alpha_vantage: 是否启用 Alpha Vantage（第二优先级，需要 API Key）
        alpha_vantage_api_key: Alpha Vantage API Key（如果启用 Alpha Vantage）
    """
    router = get_stock_data_router()

    # 验证配置
    config_validation = validate_data_source_config()
    if config_validation["warnings"]:
        for warning in config_validation["warnings"]:
            logger.warning(f"⚠️  {warning}")
    if config_validation["errors"]:
        for error in config_validation["errors"]:
            logger.error(f"❌ {error}")
        raise ValueError("数据源配置验证失败，请检查配置")

    logger.info(f"✅ 数据源配置验证通过，将启用以下数据源: {', '.join(config_validation['enabled_providers'])}")

    # 第一优先级数据源（免费优先、无需认证）
    if enable_akshare:
        try:
            akshare_provider = AkshareProvider()
            router.register_provider(akshare_provider)
            logger.info("✅ 已注册数据源: akshare (第一优先级)")
        except Exception as e:
            logger.error(f"❌ 注册 akshare 数据源失败: {e}")

    if enable_yfinance:
        try:
            yfinance_provider = YFinanceProvider()
            router.register_provider(yfinance_provider)
            logger.info("✅ 已注册数据源: yfinance (第一优先级)")
        except Exception as e:
            logger.error(f"❌ 注册 yfinance 数据源失败: {e}")

    if enable_easyquotation:
        try:
            easyquotation_provider = EasyQuotationProvider()
            router.register_provider(easyquotation_provider)
            logger.info("✅ 已注册数据源: easyquotation (第一优先级)")
        except Exception as e:
            logger.error(f"❌ 注册 easyquotation 数据源失败: {e}")

    # 第二优先级数据源（需要注册 API Key，存在限制）
    if enable_tushare and tushare_token:
        try:
            # TushareProvider 将在后续实现
            # from app.services.providers.tushare_provider import TushareProvider
            # tushare_provider = TushareProvider(token=tushare_token)
            # router.register_provider(tushare_provider)
            logger.info("⏳ Tushare 数据源将在后续实现")
        except Exception as e:
            logger.error(f"❌ 注册 Tushare 数据源失败: {e}")

    if enable_iex_cloud and iex_cloud_api_key:
        try:
            # IEXCloudProvider 将在后续实现
            # from app.services.providers.iex_cloud_provider import IEXCloudProvider
            # iex_cloud_provider = IEXCloudProvider(api_key=iex_cloud_api_key)
            # router.register_provider(iex_cloud_provider)
            logger.info("⏳ IEX Cloud 数据源将在后续实现")
        except Exception as e:
            logger.error(f"❌ 注册 IEX Cloud 数据源失败: {e}")

    if enable_alpha_vantage and alpha_vantage_api_key:
        try:
            # AlphaVantageProvider 将在后续实现
            # from app.services.providers.alpha_vantage_provider import AlphaVantageProvider
            # alpha_vantage_provider = AlphaVantageProvider(api_key=alpha_vantage_api_key)
            # router.register_provider(alpha_vantage_provider)
            logger.info("⏳ Alpha Vantage 数据源将在后续实现")
        except Exception as e:
            logger.error(f"❌ 注册 Alpha Vantage 数据源失败: {e}")

    # 输出注册总结
    logger.info("=" * 80)
    logger.info("数据源注册总结:")
    if router.market_providers:
        for market, providers in router.market_providers.items():
            logger.info(f"  {market}: {', '.join(providers)}")
    else:
        logger.warning("⚠️  未注册任何数据源！")
    logger.info("=" * 80)
    
    # 验证至少有一个数据源已注册
    if len(router.providers) == 0:
        logger.error("❌ 错误：没有可用的数据源！请检查配置。")
        raise RuntimeError("没有可用的数据源，请检查数据源配置")
    
    logger.info(f"✅ 数据源初始化完成，共注册 {len(router.providers)} 个数据源")


def get_initialized_router():
    """获取已初始化的数据源路由器.
    
    Returns:
        已注册数据源的路由器实例
    """
    return get_stock_data_router()
