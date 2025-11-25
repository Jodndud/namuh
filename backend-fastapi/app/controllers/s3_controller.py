from fastapi import APIRouter, Depends, UploadFile, File
from dependency_injector.wiring import Provide, inject

from app.core.base_response import BaseResponse
from app.core.containers import Container
from app.services.s3_service import S3Service

from app.schemas.s3_dto import *


@inject
def s3_controller(
    s3_service: S3Service = Depends(Provide[Container.s3_service]),
) -> APIRouter:
    router = APIRouter(prefix="/s3", tags=["S3"])

    @router.post(
        "",
        summary="파일 업로드",
        description="파일을 S3에 업로드합니다.",
        response_model=S3UploadResponseDTO,
        include_in_schema=False,
    )
    async def upload_file(
        file: UploadFile = File(..., description="업로드할 파일"),
        directory: str = "smile_videos",
    ):
        file_url, thumbnail_url = s3_service.upload_file(file=file, directory=directory)
        return S3UploadResponseDTO(file_url=file_url, thumbnail_url=thumbnail_url)

    @router.delete(
        "",
        summary="파일 삭제",
        description="S3에서 파일을 삭제합니다.",
        include_in_schema=False,
    )
    async def delete_file(file_key: str):
        result = s3_service.delete_file(file_key=file_key)
        return S3DeleteResponseDTO(deleted=result)

    return router
