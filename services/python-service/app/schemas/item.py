"""Item 数据模式."""

from datetime import datetime, UTC
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ItemBase(BaseModel):
    """Item 基础模式."""

    name: str = Field(..., description="Item 名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Item 描述", max_length=500)
    price: Optional[float] = Field(None, description="价格", ge=0)


class ItemCreate(ItemBase):
    """创建 Item 的模式."""

    pass


class ItemUpdate(BaseModel):
    """更新 Item 的模式."""

    name: Optional[str] = Field(None, description="Item 名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Item 描述", max_length=500)
    price: Optional[float] = Field(None, description="价格", ge=0)


class ItemResponse(ItemBase):
    """Item 响应模式."""

    id: str = Field(..., description="Item ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "示例 Item",
                "description": "这是一个示例 Item",
                "price": 99.99,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
    )
