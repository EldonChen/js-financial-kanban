"""Items 路由."""

from datetime import datetime, UTC
from typing import List
from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from app.database import get_database
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse
from app.schemas.response import success_response, error_response

router = APIRouter(prefix="/api/v1/items", tags=["items"])


def item_from_dict(item_dict: dict) -> dict:
    """将 MongoDB 文档转换为响应格式."""
    item_dict["id"] = str(item_dict.pop("_id"))
    return item_dict


@router.get("", response_model=dict)
async def get_items():
    """获取所有 items."""
    try:
        db = get_database()
        items = []
        async for item in db.items.find():
            items.append(item_from_dict(item))
        return success_response(data=items)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取 items 失败: {str(e)}",
        )


@router.get("/{item_id}", response_model=dict)
async def get_item(item_id: str):
    """获取单个 item."""
    try:
        if not ObjectId.is_valid(item_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的 item ID",
            )

        db = get_database()
        item = await db.items.find_one({"_id": ObjectId(item_id)})

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item 不存在",
            )

        return success_response(data=item_from_dict(item))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取 item 失败: {str(e)}",
        )


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """创建 item."""
    try:
        db = get_database()
        now = datetime.now(UTC)
        item_dict = item.model_dump()
        item_dict["created_at"] = now
        item_dict["updated_at"] = now

        result = await db.items.insert_one(item_dict)
        created_item = await db.items.find_one({"_id": result.inserted_id})

        return success_response(
            data=item_from_dict(created_item),
            message="Item 创建成功",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建 item 失败: {str(e)}",
        )


@router.put("/{item_id}", response_model=dict)
async def update_item(item_id: str, item: ItemUpdate):
    """更新 item."""
    try:
        if not ObjectId.is_valid(item_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的 item ID",
            )

        db = get_database()
        existing_item = await db.items.find_one({"_id": ObjectId(item_id)})

        if existing_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item 不存在",
            )

        # 只更新提供的字段
        update_data = {k: v for k, v in item.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有提供要更新的字段",
            )

        update_data["updated_at"] = datetime.now(UTC)
        await db.items.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": update_data},
        )

        updated_item = await db.items.find_one({"_id": ObjectId(item_id)})
        return success_response(
            data=item_from_dict(updated_item),
            message="Item 更新成功",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新 item 失败: {str(e)}",
        )


@router.delete("/{item_id}", response_model=dict)
async def delete_item(item_id: str):
    """删除 item."""
    try:
        if not ObjectId.is_valid(item_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的 item ID",
            )

        db = get_database()
        result = await db.items.delete_one({"_id": ObjectId(item_id)})

        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item 不存在",
            )

        return success_response(message="Item 删除成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除 item 失败: {str(e)}",
        )
