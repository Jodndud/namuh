# FaceControl (ESP32 + FastLED + MQTT)

ESP32 보드와 16x16 LED 매트릭스(WS2812B 등)로 로봇의 명령을 표정으로 표현합니다.

- 라이브러리: FastLED, PubSubClient, ArduinoJson
- 보드: ESP32 계열 (WiFi 내장)
- 매트릭스: 16x16, 지그재그(Serpentine) 배선 가정

## 설치

1. Arduino IDE에서 다음 라이브러리 설치
   - FastLED
   - PubSubClient
   - ArduinoJson
2. `embedded/FaceControl/config.example.h`를 복사해 `config.h`로 이름 변경하고 값을 수정합니다.
3. 보드 매니저에서 ESP32 보드를 설치한 후 업로드합니다.

## MQTT 토픽

- 기본값(baseTopic): `buriburi`
- 구독: `${baseTopic}/robot/rx`
  - 기존 프런트엔드가 브로드캐스트로 보내는 명령을 그대로 수신합니다.
- 필요하면 `config.h`에서 `SUB_TOPIC_FACE`를 활성화해 `${baseTopic}/face/rx`를 구독하도록 바꿀 수 있습니다.

## 명령 → 표정 매핑

- start_face_tracking → Tracking (눈동자 스캔 애니메이션)
- stop_face_tracking → Neutral
- init_pose → Neutral/약한 Smile
- make_heart → 중앙 Heart 펄스
- make_hug → 볼 하트(양 볼에 작은 하트)
- set_joint / set_joints / nudge_joint → Busy(Thinking 스피너)
- start_follow → Follow On (별눈/반짝)
- end_follow → Neutral

연결 상태

- WiFi/MQTT 연결 실패: Sad/Error 표정

## 핀/하드웨어

- 기본 LED 데이터 핀: 5 (변경은 config.h)
- LED 타입: WS2812B, GRB, 밝기 64 (변경 가능)

## 파일 구성

- `FaceControl.ino` 메인 스케치 (WiFi, MQTT, 루프)
- `expressions.h` 표정/애니메이션 렌더러
- `config.example.h` 사용자 설정 샘플 (복사해 `config.h`로 사용)
