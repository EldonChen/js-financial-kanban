"""MongoDB 数据库连接."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

# 全局数据库客户端
client: AsyncIOMotorClient | None = None
database: AsyncIOMotorDatabase | None = None


async def connect_to_mongo():
    """连接到 MongoDB."""
    global client, database
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.database_name]
    print(f"✅ 已连接到 MongoDB: {settings.database_name}")


async def close_mongo_connection():
    """关闭 MongoDB 连接."""
    global client
    if client:
        client.close()
        print("✅ 已关闭 MongoDB 连接")


def get_database() -> AsyncIOMotorDatabase:
    """获取数据库实例."""
    if database is None:
        raise RuntimeError("数据库未初始化，请先调用 connect_to_mongo()")
    return database
