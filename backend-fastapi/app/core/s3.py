import boto3
import subprocess
import tempfile
import os
from botocore.exceptions import ClientError
from fastapi import File, UploadFile
from app.core.load_settings import Settings
from app.core.exceptions.custom_exception import *
from typing import Optional
import uuid
import logging


class S3Client:
    def __init__(self, settings: Settings, logger: logging.Logger) -> None:
        self.settings = settings
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region_static,
        )
        self.logger = logger
        self.BASE_S3_URL = f"https://{settings.s3_bucket}.s3.{settings.s3_region_static}.amazonaws.com/"

    def _is_bucket_accessible(self) -> bool:
        try:
            self.s3.head_bucket(Bucket=self.settings.s3_bucket)
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            raise S3ServiceException(message=f"S3 버킷 접근 실패: {error_code}")

    def _extract_thumbnail(
        self, video_file: UploadFile = File(...), thumbnail_time: int = 5
    ) -> bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            video_bytes = video_file.file.read()
            temp_video.write(video_bytes)
            temp_video_path = temp_video.name

        thumbnail_path = temp_video_path.replace(".mp4", "_thumbnail.png")

        try:
            command = [
                "ffmpeg",
                "-ss",
                str(thumbnail_time),  # 시작 시간
                "-i",
                temp_video_path,  # 입력 파일
                "-vframes",
                "1",  # 1프레임만 추출
                "-f",
                "image2",  # 이미지 포맷
                "-y",  # 덮어쓰기
                thumbnail_path,
            ]

            result = subprocess.run(command, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                raise ValueError(f"FFmpeg 오류: {result.stderr}")

            if not os.path.exists(thumbnail_path):
                raise ValueError("썸네일 파일이 생성되지 않았습니다.")

            with open(thumbnail_path, "rb") as f:
                thumbnail_bytes = f.read()

            return thumbnail_bytes

        except subprocess.TimeoutExpired:
            raise ValueError("썸네일 추출 시간이 초과되었습니다.")
        except Exception as e:
            raise ValueError(f"썸네일 추출에 실패했습니다: {str(e)}")
        finally:
            if os.path.exists(temp_video_path):
                os.unlink(temp_video_path)
            if os.path.exists(thumbnail_path):
                os.unlink(thumbnail_path)
            video_file.file.seek(0)

    def upload_file(
        self, file: UploadFile = File(...), directory: Optional[str] = "smile_videos"
    ) -> str:
        try:
            file_extension = (
                file.filename.split(".")[-1] if "." in file.filename else ""
            )
            unique_filename = str(uuid.uuid4())
            file_key = f"{directory}/{unique_filename}.{file_extension}"

            file_content = file.file.read()
            file.file.seek(0)

            processed_bytes = None
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_in:
                tmp_in.write(file_content)
                input_path = tmp_in.name

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_out:
                output_path = tmp_out.name

            try:
                subprocess.run(
                    [
                        "ffmpeg",
                        "-i",
                        input_path,
                        "-movflags",
                        "faststart",
                        "-c",
                        "copy",
                        "-y",
                        output_path,
                    ],
                    check=True,
                    capture_output=True,
                )
                with open(output_path, "rb") as f:
                    processed_bytes = f.read()

            except subprocess.CalledProcessError as e:
                # FFmpeg 처리 실패 시 원본 파일 사용 (임시 방편)
                processed_bytes = file_content
                self.logger.error(
                    f"FFmpeg faststart 실패. 원본 업로드 시도: {e.stderr.decode()}"
                )
            except FileNotFoundError:
                # FFmpeg가 환경에 설치되지 않은 경우
                processed_bytes = file_content
                self.logger.error("FFmpeg가 설치되지 않았습니다. 원본 업로드 시도.")
            finally:
                os.remove(input_path)
                os.remove(output_path)

            from io import BytesIO

            file_obj = BytesIO(processed_bytes)

            self.s3.upload_fileobj(
                file_obj,
                Bucket=self.settings.s3_bucket,
                Key=file_key,
                ExtraArgs={
                    "ContentType": (
                        file.content_type if file.content_type else "video/mp4"
                    )
                },
            )

            file.file = BytesIO(file_content)

            thumbnail_bytes = self._extract_thumbnail(video_file=file)
            thumbnail_key = f"{directory}/thumbnail_{unique_filename}.png"
            self.s3.put_object(
                Bucket=self.settings.s3_bucket,
                Key=thumbnail_key,
                Body=thumbnail_bytes,
                ContentType="image/png",
            )

            file_thumbnail_url = self.BASE_S3_URL + thumbnail_key
            file_url = self.BASE_S3_URL + file_key

            return [file_url, file_thumbnail_url]
        except ClientError as e:
            raise S3UploadException(message=f"S3 파일 업로드 실패: {e}")
        except Exception as e:
            raise S3UploadException(message=f"S3 파일 업로드 중 오류 발생: {e}")

    def file_exists(self, file_key: str) -> bool:
        try:
            self.s3.head_object(Bucket=self.settings.s3_bucket, Key=file_key)
            return True
        except ClientError:
            return False

    def download_file(self, file_key: str) -> bytes:
        try:
            response = self.s3.get_object(Bucket=self.settings.s3_bucket, Key=file_key)
            return response["Body"].read()
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "NoSuchKey":
                raise S3DownloadException(
                    message=f"파일을 찾을 수 없습니다: {file_key}"
                )
            else:
                error_message = e.response.get("Error", {}).get("Message", str(e))
                raise S3DownloadException(
                    message=f"S3 파일 다운로드 실패 [{error_code}]: {error_message}"
                )
        except Exception as e:
            raise S3DownloadException(
                message=f"파일 다운로드 중 예상치 못한 오류: {str(e)}"
            )

    def delete_file(self, file_key: str) -> bool:
        try:
            self.s3.delete_object(Bucket=self.settings.s3_bucket, Key=file_key)
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))
            raise S3DeleteException(
                message=f"S3 파일 삭제 실패 [{error_code}]: {error_message}"
            )
        except Exception as e:
            raise S3DeleteException(message=f"파일 삭제 중 예상치 못한 오류: {str(e)}")

    def get_file_url(self, file_key: str) -> str:
        return self.BASE_S3_URL + file_key
