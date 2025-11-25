import json

from fastapi.middleware.cors import CORSMiddleware

from ..core.exceptions.custom_exception import InternalServerException


class CORSConfigMiddleware(CORSMiddleware):
    def __init__(self, app, settings):
        origins = self.get_cors_origins(settings)
        allow_credentials = "*" not in origins

        super().__init__(
            app,
            allow_origins=origins,
            allow_credentials=allow_credentials,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @staticmethod
    def get_cors_origins(settings):
        profile = settings.profile.lower()
        origins = settings.cors_allow_origins_list or []

        if not origins and profile == "local":
            origins = ["*"]

        if profile == "production" and "*" in origins:
            raise InternalServerException()

        return origins
