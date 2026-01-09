"""FastAPI 应用入口."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.models.stock import init_stock_indexes
from app.models.schedule import init_schedule_indexes
from app.routers import stocks, schedules
from app.services.scheduler_service import get_scheduler_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理."""
    # 启动时连接数据库
    await connect_to_mongo()

    # 初始化索引
    await init_stock_indexes()
    await init_schedule_indexes()

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
