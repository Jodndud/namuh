import logging
from typing import Optional
from fastapi import UploadFile, File
from ..s3_service import S3Service
from ...core.s3 import S3Client
from app.repositories.media_repository import MediaRepository


class S3ServiceImpl(S3Service):
    def __init__(
        self,
        s3_client: S3Client,
        logger: logging.Logger,
        media_repository: MediaRepository,
    ) -> None:
        self.s3_client = s3_client
        self.logger = logger
        self.media_repository = media_repository

    def upload_file(
        self,
        file: UploadFile = File(...),
        directory: Optional[str] = "smile_videos",
        owner_id: int = 1,
        seq_no: Optional[int] = None,
    ) -> str:
        try:
            file_url, thumbnail_url = self.s3_client.upload_file(file, directory)

            if seq_no is None:
                max_seq = self.media_repository.get_max_seq_no(
                    owner_id=owner_id, media_type="ROBOT_VIDEO"
                )
                seq_no = (max_seq or 0) + 1

            self.media_repository.create(
                mime_type=file.content_type or "video/mp4",
                owner_id=owner_id,
                s3key_or_url=file_url,
                seq_no=seq_no,
                media_type="ROBOT_VIDEO",
            )
            self.media_repository.create(
                mime_type="image/png",
                owner_id=owner_id,
                s3key_or_url=thumbnail_url,
                seq_no=seq_no,
                media_type="ROBOT_VIDEO_THUMBNAIL",
            )

            self.media_repository.commit()

            return file_url, thumbnail_url
        except Exception as e:
            self.media_repository.rollback()
            self.logger.error(f"S3 파일 업로드 및 DB 저장 실패: {e}")
            raise

    def download_file(self, file_key: str) -> bytes:
        return self.s3_client.download_file(file_key)

    def delete_file(self, file_key: str) -> bool:
        return self.s3_client.delete_file(file_key)

    def get_file_url(self, file_key: str) -> str:
        return self.s3_client.get_file_url(file_key)

    def file_exists(self, file_key: str) -> bool:
        return self.s3_client.file_exists(file_key)
