from fastapi import status

from app.core.exceptions.base_exception import BaseException

"""
General Exceptions
-1500
"""


class InternalServerException(BaseException):
    def __init__(self, message: str = "서버 내부 오류가 발생했습니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=-1501,
        )


class InvalidInputException(BaseException):
    def __init__(self, message: str = "입력 데이터가 올바르지 않습니다."):
        super().__init__(
            message=message, status_code=status.HTTP_400_BAD_REQUEST, error_code=-1502
        )


"""
Authentication Exceptions
-2500
"""


class UnauthorizedException(BaseException):
    def __init__(self, message: str = "인증이 필요합니다."):
        super().__init__(
            message=message, status_code=status.HTTP_401_UNAUTHORIZED, error_code=-2501
        )


class InvalidTokenException(BaseException):
    def __init__(self, message: str = "유효하지 않은 토큰입니다."):
        super().__init__(
            message=message, status_code=status.HTTP_401_UNAUTHORIZED, error_code=-2502
        )


class ExpiredTokenException(BaseException):
    def __init__(self, message: str = "만료된 토큰입니다."):
        super().__init__(
            message=message, status_code=status.HTTP_401_UNAUTHORIZED, error_code=-2503
        )


"""
STT/TTS Exceptions
-3500
"""


class STTServiceException(BaseException):
    def __init__(self, message: str = "음성 인식 서비스에 오류가 발생했습니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=-3501,
        )


class TTSServiceException(BaseException):
    def __init__(self, message: str = "텍스트 음성 변환 서비스에 오류가 발생했습니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=-3502,
        )


"""
Database Exceptions
-4500
"""


class DatabaseConnectionException(BaseException):
    def __init__(self, message: str = "데이터베이스 연결에 실패했습니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=-4501,
        )


class DatabaseQueryException(BaseException):
    def __init__(self, message: str = "데이터베이스 쿼리 실행에 실패했습니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=-4502,
        )


class DataNotFoundException(BaseException):
    def __init__(self, message: str = "요청한 데이터를 찾을 수 없습니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=-4503,
        )


class DataRedisOperationException(BaseException):
    def __init__(self, message: str = "REDIS TOPIC_LIST 저장에 실패했습니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=-4504,
        )

"""
S3 Exceptions
-5500
"""


class S3ServiceException(BaseException):
    def __init__(self, message: str = "S3 서비스에 오류가 발생했습니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=-5501,
        )


class S3FileNotFoundException(BaseException):
    def __init__(self, message: str = "S3에서 파일을 찾을 수 없습니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=-5502,
        )


class S3UploadException(BaseException):
    def __init__(self, message: str = "S3 파일 업로드에 실패했습니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=-5503,
        )


class S3DownloadException(BaseException):
    def __init__(self, message: str = "S3 파일 다운로드에 실패했습니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=-5504,
        )


class S3DeleteException(BaseException):
    def __init__(self, message: str = "S3 파일 삭제에 실패했습니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=-5505,
        )


class S3FileExistsException(BaseException):
    def __init__(self, message: str = "S3 파일 존재 여부 확인에 실패했습니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=-5506,
        )


"""
MQTT Exceptions
-6500
"""


class MQTTServiceException(BaseException):
    def __init__(self, message: str = "MQTT 서비스에 오류가 발생했습니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=-6501,
        )


class MQTTConnectionException(BaseException):
    def __init__(self, message: str = "MQTT 연결에 실패했습니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=-6502,
        )


class MQTTSubscriptionException(BaseException):
    def __init__(self, message: str = "MQTT 토픽 구독에 실패했습니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=-6503,
        )


class MQTTUnsubscriptionException(BaseException):
    def __init__(self, message: str = "MQTT 토픽 구독 해제에 실패했습니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=-6504,
        )


class MQTTPublishException(BaseException):
    def __init__(self, message: str = "MQTT 메시지 발행에 실패했습니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=-6505,
        )
