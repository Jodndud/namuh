from typing import Any, Dict, Optional

import jwt

from app.core.load_settings import Settings
from ..core.exceptions.custom_exception import (
    InvalidTokenException,
    ExpiredTokenException,
)


class JwtProvider:
    def __init__(self, settings: Settings):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenException()
        except jwt.InvalidTokenError:
            raise InvalidTokenException()

    def get_payload(self, token: str) -> Optional[Dict[str, Any]]:
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
