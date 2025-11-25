from pydantic import BaseModel, Field
from fastapi import UploadFile, File


class S3UploadResponseDTO(BaseModel):

    file_url: str = Field(..., description="업로드된 비디오의 URL")
    thumbnail_url: str = Field(..., description="업로드된 썸네일의 URL")

    class Config:
        json_schema_extra = {
            "example": {
                "file_url": "https://bucket-name.s3.region.amazonaws.com/test/filename.mp4",
                "thumbnail_url": "https://bucket-name.s3.region.amazonaws.com/test/thumbnail_filename.jpg",
            }
        }


class S3DeleteResponseDTO(BaseModel):
    deleted: bool = Field(..., description="파일 삭제 성공 여부")

    class Config:
        json_schema_extra = {"example": {"deleted": True}}
