# Carebot 테스트 도구 (MQTT)

이 폴더에는 Carebot 앱을 테스트하기 위한 MQTT 허브 스크립트와 브라우저 프론트엔드 페이지가 들어 있습니다. 브라우저는 MQTT over WebSocket(WS/WSS)으로 브로커에 연결합니다.

## 기능

- MQTT 허브(`backend_server_mqtt.py`)는 TCP MQTT 브로커에 연결해 라우팅합니다.
  - 기본 토픽(base)은 `buriburi`이며, `{base}/frontend/tx|rx`, `{base}/robot/tx|rx`를 사용합니다.
  - 프런트엔드에서 온 `type:"command"` 메시지만 로봇 토픽으로 전달하며, 로봇에서 온 모든 메시지는 프런트엔드로 전달합니다.
  - follow(미러링) 모드는 로봇 앱이 직접 처리하며, 허브는 단순 전달만 합니다.
- 프론트엔드(`frontend_mqtt.html`)는 브로커의 WebSocket 포트로 직접 연결합니다.
  - `{base}/robot/tx` 구독과 `{base}/robot/rx` 발행으로 로봇과 직접 통신합니다(허브 없이도 사용 가능).

## 요구 사항

- Python 3.9+
- 의존성 설치:

```bash
pip install -r requirements.txt
```

## 실행 방법

1. (선택) MQTT 허브 실행:

```bash
python backend_server_mqtt.py
```

1. 프론트엔드 열기:

- `frontend_mqtt.html`을 브라우저에서 열고, Broker WS URL(예: `ws://<broker-host>:9001`), Base Topic(예: `buriburi`)을 맞게 입력한 뒤 Connect를 누릅니다.

1. Carebot 로봇 앱 실행(다른 터미널/장치에서):

- `BotControl/config.json`의 `mqtt_host`, `mqtt_port`, `mqtt_base` 값을 브로커 설정에 맞게 지정합니다.
- 앱을 실행하면 `{base}/robot/tx`로 텔레메트리를 발행하고 `{base}/robot/rx`의 명령을 수신합니다.

1. 프론트엔드에서:

- Start Tracking / Stop Tracking / Make Heart / Make Hug / Init Pose 등의 버튼으로 명령을 보냅니다.
- Start Follow / End Follow 버튼으로 팔 미러링 모드를 토글합니다(팔로워 로봇이 리더의 joint_state를 따라갑니다).

## 참고

- 허브 스크립트는 테스트용 라우터이며, 인증/영속성은 MQTT 브로커(Mosquitto 등) 설정을 사용하세요.
- 프론트엔드를 여러 개 띄워도 모두 동일한 이벤트 스트림을 수신합니다.
- 브라우저는 TCP MQTT(1883)가 아닌 MQTT over WebSocket(예: 9001)만 사용할 수 있습니다.
