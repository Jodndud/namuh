from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.core.containers import Container
from app.services.mqtt_service import MQTTService
from app.schemas.mqtt_dto import *
from app.core.base_response import BaseResponse


@inject
def mqtt_controller(
    mqtt_service: MQTTService = Depends(Provide[Container.mqtt_service]),
) -> APIRouter:
    router = APIRouter(prefix="/mqtt", tags=["MQTT"])

    @router.post("/publish", summary="메시지 발행")
    async def publish_message(request: MQTTPublishRequest):
        await mqtt_service.publish_message(request)
        return BaseResponse.success_response(
            message="메시지 발행 성공",
            data={"topic": request.topic, "payload": request.payload},
        )

    @router.post(
        "/subscribe",
        summary="토픽 구독",
        include_in_schema=False,
    )
    async def subscribe_topic(request: MQTTSubscribeRequest):
        await mqtt_service.subscribe_topic(topic=request.topic)
        return BaseResponse.success_response(
            message="토픽 구독 성공",
            data={"topic": request.topic},
        )

    return router
