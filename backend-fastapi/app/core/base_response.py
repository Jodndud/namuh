from typing import Generic, Optional, TypeVar, Any
from pydantic import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    status_code: int
    error_code: Optional[int] = None

    @classmethod
    def success_response(
        cls, message: str, data: Optional[T] = None, status_code: int = 200
    ) -> "BaseResponse[T]":
        return cls(
            success=True,
            message=message,
            data=data,
            status_code=status_code,
            error_code=None,
        )

    @classmethod
    def fail_response(
        cls, message: str, status_code: int, error_code: int, data: Optional[Any] = None
    ) -> "BaseResponse[Any]":
        return cls(
            success=False,
            message=message,
            data=data,
            status_code=status_code,
            error_code=error_code,
        )
