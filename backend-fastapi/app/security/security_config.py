from typing import Iterable, List, Optional, Set, Tuple

ROOT_PATH_PREFIX = "/fastapi"


class SecurityConfig:
    def __init__(self) -> None:
        self.auth_whitelist: List[Tuple[str, Optional[Set[str]]]] = [
            # (f"{ROOT_PATH_PREFIX}/swagger-ui/index.html", None),
            # (f"{ROOT_PATH_PREFIX}/redoc/index.html", None),
            # (f"{ROOT_PATH_PREFIX}/openapi.json", None),
            # (f"{ROOT_PATH_PREFIX}/favicon.ico", None),
            # (f"{ROOT_PATH_PREFIX}/v1/health", None),
            ("/**", None),  # 모든 경로 허용 (테스트 용)
        ]

    @staticmethod
    def _path_matches(pattern: str, path: str) -> bool:
        if pattern.endswith("/**"):
            prefix = pattern[:-3]
            return path.startswith(prefix)
        return pattern == path

    @staticmethod
    def _normalize_methods(methods: Optional[Iterable[str]]) -> Optional[Set[str]]:
        if methods is None:
            return None
        return {method.upper() for method in methods}

    def is_auth_excluded_path(self, path: str, method: str | None = None) -> bool:
        """화이트리스트에 포함된 경우 인증을 제외한다 (경로 + 선택적 메서드 기준)."""
        method_upper = (method or "").upper()
        for pattern, allowed_methods in self.auth_whitelist:
            if self._path_matches(pattern, path):
                if allowed_methods is None:
                    return True
                if method_upper in allowed_methods:
                    return True
        return False

    def add_auth_whitelist(
        self, path_pattern: str, methods: Optional[Iterable[str]] = None
    ) -> None:
        """런타임 중 화이트리스트 규칙 추가 (테스트/확장 용)."""
        self.auth_whitelist.append((path_pattern, self._normalize_methods(methods)))

    def clear_auth_whitelist(self) -> None:
        """화이트리스트를 모두 비운다 (테스트 용)."""
        self.auth_whitelist.clear()
