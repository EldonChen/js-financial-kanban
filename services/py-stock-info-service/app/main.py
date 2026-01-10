"""FastAPI 应用入口."""

import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.models.stock import init_stock_indexes
from app.models.schedule import init_schedule_indexes
from app.routers import stocks, schedules, providers
from app.services.scheduler_service import get_scheduler_service
from app.services.providers.initializer import initialize_providers

# 配置日志系统
def setup_logging():
    """配置应用日志系统."""
    # 获取日志级别（从配置或环境变量）
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # 配置日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # 配置根日志记录器
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True,  # 强制重新配置，避免被其他模块覆盖
    )
    
    # 设置第三方库的日志级别（避免过多噪音）
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"✅ 日志系统已配置，日志级别: {settings.log_level}")

# 在导入其他模块之前配置日志
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理."""
    # 启动时连接数据库
    await connect_to_mongo()

    # 初始化索引
    await init_stock_indexes()
    await init_schedule_indexes()

    # 初始化数据源提供者
    initialize_providers(
        enable_akshare=settings.enable_akshare,
        enable_yfinance=settings.enable_yfinance,
        enable_easyquotation=settings.enable_easyquotation,
        enable_tushare=settings.enable_tushare,
        tushare_token=settings.tushare_token,
        enable_iex_cloud=settings.enable_iex_cloud,
        iex_cloud_api_key=settings.iex_cloud_api_key,
        enable_alpha_vantage=settings.enable_alpha_vantage,
        alpha_vantage_api_key=settings.alpha_vantage_api_key,
    )

    # 启动定时任务调度器
    scheduler = get_scheduler_service()
    scheduler.start()

    # 加载激活的更新计划
    await scheduler.load_schedules()

    yield

    # 关闭时关闭调度器
    scheduler.shutdown()

    # 关闭时断开数据库连接
    await close_mongo_connection()


app = FastAPI(
    title="Financial Kanban - Stock Info Service",
    description="Python FastAPI 服务，提供股票基本信息管理和定时更新功能",
    version="0.1.0",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(stocks.router)
app.include_router(schedules.router)
app.include_router(providers.router)


@app.get("/")
async def root():
    """根路径."""
    return {
        "message": "Financial Kanban - Stock Info Service",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """健康检查."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
    )
