import logging
from app.security.jwt_provider import JwtProvider
from ..auth_service import AuthService


class AuthServiceImpl(AuthService):
    def __init__(self, jwt_provider: JwtProvider, logger: logging.Logger):
        self.jwt_provider = jwt_provider
        self.logger = logger

    def authenticate(self, token: str) -> bool:
        payload = self.jwt_provider.verify_token(token)
        if payload is None:
            self.logger.warning("Invalid or expired token.")
            return False
        self.logger.info(f"Authenticated user with payload: {payload}")
        return True

    def validate_jwt_token(self, token):
        payload = self.jwt_provider.verify_token(token)
        if payload is None:
            self.logger.warning("Invalid or expired JWT token.")
            return None
        self.logger.info(f"Valid JWT token with payload: {payload}")
        return payload
