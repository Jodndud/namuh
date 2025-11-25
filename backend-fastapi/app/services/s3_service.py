from abc import ABC, abstractmethod
from typing import Optional
from fastapi import UploadFile, File


class S3Service(ABC):
    @abstractmethod
    def upload_file(
        self,
        file: UploadFile = File(...),
        directory: Optional[str] = "test",
        owner_id: int = 1,
        seq_no: int = 1,
    ) -> str:
        pass

    @abstractmethod
    def download_file(self, file_key: str) -> bytes:
        pass

    @abstractmethod
    def delete_file(self, file_key: str) -> bool:
        pass

    @abstractmethod
    def get_file_url(self, file_key: str) -> str:
        pass

    @abstractmethod
    def file_exists(self, file_key: str) -> bool:
        pass
