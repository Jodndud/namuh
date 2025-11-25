# BackboneControl (ESP32 + Servo + MQTT)

> 🔎 **ESP32**를 사용하여 로봇의 **목과 허리**를 제어하는 서보모터 제어 시스템입니다.
>
> 모든 제어는 MQTT를 통해 원격으로 이루어지며, 단순한 움직임을 넘어 부드러운 가속/감속이 적용된 **애니메이션 엔진**을 탑재하여 로봇이 훨씬 자연스럽고 생동감 있게 움직이도록 설계되었습니다.

## 주요 기능

- **3축 서보모터 제어**: 목 회전(Yaw), 목 끄덕임(Pitch), 허리 회전(Waist)을 담당하는 3개의 서보모터를 제어합니다.
- **`MQTT` 기반 원격 제어**: WiFi를 통해 `MQTT` 브로커에 접속하고, 특정 토픽으로 들어오는 `JSON` 형식의 명령을 수행합니다.
- **고급 애니메이션 엔진**:
  - 모든 움직임에 **Easing(가속/감속) 함수**를 적용하여 딱딱하지 않고 부드러운 움직임을 구현했습니다.
  - 여러 개의 서보가 각기 다른 시간과 각도로 움직이는 복합적인 애니메이션을 손쉽게 생성하고 관리하고자 했습니다.
- **다채로운 액션 라이브러리**: `hello`, `nod`, `make_heart` 등 사전 정의된 여러 동작의 실제 구현은 `actions/` 폴더 내에서 모듈식으로 관리합니다.
- **실시간 얼굴 추적**: MQTT로 `track_face` 명령과 함께 (x, y) 좌표를 지속적으로 수신하여, 로봇이 특정 대상을 바라보도록 실시간으로 목 각도를 제어합니다.
- **자연스러운 IDLE 상태**: 명령이 없을 때는 가만히 멈춰 있는 것이 아니라, 주변을 둘러보거나 위아래를 살피는 등 살아있는 생물처럼 자연스러운 임의 동작을 수행합니다.
- **하드웨어 보호 기능**:
  - **각도 제한**: `config.h`에 설정된 물리적 한계치를 넘는 각도로 서보가 움직이지 않도록 하여 파손을 방지합니다.
  - **과열 방지**: IDLE 상태이거나 동작이 끝나면 허리 서보의 전원을 자동으로 차단(`detach`)하여 불필요한 발열과 손상을 예방합니다.
- **높은 설정 편의성**:
  - WiFi 및 MQTT 접속 정보는 `secrets.h` 파일에 분리하여 안전하게 관리합니다.
  - 서보모터 연결 핀, 각도 제한, 초기 자세 등 대부분의 하드웨어 및 동작 설정을 `config.h` 파일 한 곳에서 쉽게 변경 가능합니다.

## 설정 및 설치 방법

### (1) 필요 라이브러리

Arduino IDE의 라이브러리 매니저를 통해 아래 라이브러리들을 설치해야 합니다.

- `PubSubClient`
- `ArduinoJson`
- `ESP32Servo`

### (2) 설정 파일 작성

#### `secrets.h`

`BackboneControl.ino` 파일이 있는 동일한 폴더에 `secrets.h` 파일을 직접 생성하고, 아래와 같이 WiFi 및 MQTT 브로커 접속 정보를 입력해야 합니다. 이 파일은 `.gitignore`에 의해 버전 관리에서 제외됩니다.

```cpp
#pragma once

#define WIFI_SSID       "YOUR_WIFI_SSID"
#define WIFI_PASS       "YOUR_WIFI_PASSWORD"

#define MQTT_HOST       "YOUR_MQTT_BROKER_IP"
#define MQTT_PORT       1883 // or 8883 for TLS
#define MQTT_USERNAME   "YOUR_MQTT_USERNAME" // Optional
#define MQTT_PASSWORD   "YOUR_MQTT_PASSWORD" // Optional
```

#### `config.h`

로봇의 하드웨어 구성 및 동작 특성은 이 파일에서 모두 설정할 수 있습니다.

- **서보모터 핀 번호**: `SERVO_PIN_*` 값들을 실제 ESP32에 연결된 GPIO 핀 번호로 수정합니다.
- **물리적 각도 제한**: `SERVO_*_MIN`, `SERVO_*_MAX` 값들을 조절하여 로봇의 구조물에 부딪히지 않도록 서보의 최대/최소 각도를 설정합니다.
- **초기 자세**: `SERVO_*_INIT` 값들을 조절하여 부팅 시 또는 `init_pose` 명령 시 로봇이 취할 기본 자세를 설정합니다.

### (3) 컴파일 및 업로드

Arduino IDE에서 보드를 `ESP32 Dev Module` (또는 사용하는 보드에 맞게)로 설정한 뒤, 코드를 컴파일하고 업로드합니다.

## (4) MQTT API 명세

- **구독(Subscribe) 토픽**:
  - `buriburi/robot/all/command`
  - `buriburi/robot/robot_backbone/command`
- **발행(Publish) 토픽**:
  - `buriburi/robot/joint`: 로봇이 현재 자신의 관절 각도 상태를 주기적으로 발행합니다.

### 명령 형식 (JSON)

모든 명령은 아래와 같은 JSON 형식을 따라야 합니다.

```json
{
  "type": "command",
  "command": "COMMAND_NAME",
  ... (추가 파라미터)
}
```

### 주요 명령 목록

- **기본 동작**:

  - `{"type": "command", "command": "hello"}`
  - `{"type": "command", "command": "nod"}`
  - `{"type": "command", "command": "shake"}`
  - `{"type": "command", "command": "make_heart"}`
  - `{"type": "command", "command": "scissors"}`
  - `{"type": "command", "command": "rock"}`
  - `{"type": "command", "command": "paper"}`
  - ... (그 외 `command_mapper.h`에 정의된 모든 액션)

- **초기 자세로 이동**:

  - `{"type": "command", "command": "init_pose"}`

- **개별 관절 제어 (`set_joint`)**:

  - `id`: `0`(목 Yaw), `1`(목 Pitch), `2`(허리 Waist)
  - `angle`: 목표 각도
  - `time_ms`: 목표 각도까지 도달하는 데 걸리는 시간 (밀리초)
  - 예시: `{"type": "command", "command": "set_joint", "id": 0, "angle": 120, "time_ms": 500}`

- **얼굴 추적 (`track_face`)**:

  - `x`, `y`: 화면상 대상의 좌표 (0.0 ~ 1.0)
  - 예시: `{"type": "command", "command": "track_face", "x": 0.3, "y": 0.6}`

- **얼굴 추적 종료 (`track_lost`)**:
  - `{"type": "command", "command": "track_lost"}`

## 소스코드 구조

```text
.
├── BackboneControl.ino   # 메인 setup(), loop() 함수 / 전체 프로그램의 시작점
├── config.h              # 하드웨어 및 동작 관련 핵심 설정
├── secrets.h             # (직접 생성 필요) WiFi/MQTT 접속 정보 등 민감한 정보 관리
├── globals.h             # 전역 변수 및 공용 타입(enum, struct) 선언
├── mqtt_helpers.h        # WiFi/MQTT 연결 및 메시지 수신 처리
├── servo_actions.h       # 서보 제어와 관련된 핵심 함수, 애니메이션 엔진, 액션 분기 처리
├── command_mapper.h      # MQTT로 수신한 명령어 문자열과 실제 실행할 액션을 연결
├── Animation.h           # 부드러운 움직임을 위한 Easing 함수
└── actions/              # 개별 동작의 실제 구현이 담긴 파일 모음
    ├── action_hello.h
    └── ... (기타 액션 파일들)
```
