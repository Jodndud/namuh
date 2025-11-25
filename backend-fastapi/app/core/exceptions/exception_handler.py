from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.base_response import BaseResponse
from app.core.exceptions.base_exception import BaseException


async def app_exception_handler(request: Request, exc: BaseException):
    return JSONResponse(
        status_code=exc.status_code,
        content=BaseResponse.fail_response(
            message=exc.message,
            status_code=exc.status_code,
            error_code=exc.error_code,
        ).model_dump(),
    )


async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=BaseResponse.fail_response(
            message="알 수 없는 오류가 발생했습니다.",
            status_code=500,
            error_code=-1,
        ).model_dump(),
    )
