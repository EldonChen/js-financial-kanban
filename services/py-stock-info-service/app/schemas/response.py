"""统一响应格式."""

from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应格式."""

    code: int = 200
    message: str = "success"
    data: Optional[T] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": 200,
                "message": "success",
                "data": {},
            }
        }
    )


def success_response(data=None, message: str = "success") -> dict:
    """成功响应."""
    return {"code": 200, "message": message, "data": data}


def error_response(message: str = "error", code: int = 400) -> dict:
    """错误响应."""
    return {"code": code, "message": message, "data": None}
