from fastapi import status


class BaseException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_505_HTTP_VERSION_NOT_SUPPORTED,
        error_code: int = 0,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
