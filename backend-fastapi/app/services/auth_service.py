from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class AuthService(ABC):
    @abstractmethod
    def authenticate(self, token: str) -> bool:
        pass

    @abstractmethod
    def validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        pass
