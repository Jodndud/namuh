# Robot 서비스 (분리된 토픽 버전)

참고: MQTT 통신 규격은 `MQTT_SPEC.md`를 참고하세요.

DOFBOT 로봇팔을 MQTT로 제어하는 애플리케이션입니다. `app_mqtt_sep_topic.py`가 MQTT 브로커에 연결하여 명령을 받아 실행합니다.

## 주요 기능

- **얼굴 추적**: 카메라에서 얼굴을 감지하고 S1(팬)/S3,S4(틸트)를 PID로 따라갑니다.
- **제스처 동작 (11가지)**:
  - 기본: `init_pose`, `make_heart`, `make_hug`, `make_hello`
  - 가위바위보: `scissors`, `rock`, `paper`
  - 일상 표현: `good_morning`, `good_night`, `hungry`, `ate_all`
- **수동 제어**: 단일 관절 설정(`set_joint`), 6관절 일괄 설정(`set_joints`), 미세 가감(`nudge_joint`)
- **팔로우 모드**: `start_follow`/`end_follow`로 한 팔이 다른 팔을 실시간 미러링
- **분리된 토픽 구조**:
  - 명령 수신: `{base}/robot/all/command` (브로드캐스트), `{base}/robot/{robot_id}/command` (개별)
  - 이벤트 발행: `{base}/robot/event`
  - 관절 상태: `{base}/robot/joint`
- **텔레메트리**: 주기적 `joint_state` 게시(각도 배열, 시퀀스)
- **선점(Preemption)**: 새 명령이 들어오면 진행 중 작업/얼굴추적을 먼저 중단 후 새 명령 수행
- **멀티 로봇**: `robot_id=robot_left|robot_right|all`로 인스턴스 구분

## 설정

`config.json` 편집(오직 이 파일의 설정만 사용합니다):

- `mqtt_host`: MQTT 브로커 호스트(예: `127.0.0.1`)
- `mqtt_port`: MQTT 브로커 포트(기본 `1883`)
- `mqtt_base`: 기본 토픽 베이스(기본 `robot`)
- `mqtt_qos`: QoS 레벨(0|1|2)
- `robot_id`: 이 인스턴스의 로봇 식별자(`robot_left` 또는 `robot_right` 등)
- `camera_index`: 기본(OpenCV 카메라 인덱스, 폴백)
- `camera_index_left`, `camera_index_right`: 좌/우 로봇 전용 카메라 인덱스(각 인스턴스에서 자동 선택)
- `update_interval_ms`: 얼굴/조인트 업데이트 주기(ms)
- `heart_move_ms`, `heart_hold_between_s`, `heart_hold_final_s`, `heart_hold_neutral_s`: 제스처 타이밍 조정
- `arm_port`: 단일 포트 지정 시 사용(Windows 예: `COM3`)
- `arm_port_left`, `arm_port_right`: 좌/우 전용 포트(by-path 권장, Linux)

참고: `haarcascade_frontalface_default.xml` 파일은 `robot` 폴더에 포함되어 있으며 자동으로 사용됩니다. 해당 파일이 없으면 OpenCV 내장 카스케이드로 대체됩니다.

LED 관련 키는 제거되었습니다(통신 간섭 방지 목적).

## 설치 (Windows cmd)

이미 환경이 준비되어 있다면 생략 가능합니다.

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

MQTT 모드를 사용할 경우 추가 패키지 설치가 필요합니다:

```cmd
pip install paho-mqtt
```

## 실행

```cmd
cd BotControl
python app_mqtt_sep_topic.py
```

기본값은 왼쪽 팔(`robot_left`)이며, 편의를 위해 실행 시 `robot_id`만 인자로 오버라이드할 수 있습니다.
예) `python app_mqtt_sep_topic.py`(왼쪽 기본), `python app_mqtt_sep_topic.py robot_id=robot_right`, 또는 `python app_mqtt_sep_topic.py which_arm=right`.

## 메시지 형식

들어오는 메시지(예시):

- `{ "command": "start_face_tracking" }`
- `{ "command": "stop_face_tracking" }`
- `{ "command": "make_heart" }`

나가는 메시지(예시):

- Ack: `{ "type": "ack", "command": "start_face_tracking", "status": "accepted", "ts": "..." }`
- Tracking update: `{ "type": "face_tracking", "status": "running", "detected": true, "bbox": {...}, "joints": [..], "ts": "..." }`
- Result: `{ "type": "result", "command": "make_heart", "status": "completed", "outcome": "heart_completed", "ts": "..." }`
- Errors: `{ "type": "error", "error": "unknown_command", "command": "...", "ts": "..." }`

### 지원 명령 전체 목록(공통)

**제스처/동작 명령 (11가지)**
- `start_face_tracking`: 얼굴 추적 시작
- `stop_face_tracking`: 얼굴 추적 중지
- `init_pose`: 초기/안전 자세로 이동
- `make_heart`: 하트 동작 수행(미러링 포함 로직은 팔에 따라 자동 처리)
- `make_hug`: 안기 동작 수행
- `make_hello`: 손 흔들며 인사하기
- `scissors`: 가위 제스처
- `rock`: 바위 제스처
- `paper`: 보 제스처
- `good_morning`: 좋은 아침 인사 동작
- `good_night`: 잘 자요 동작
- `hungry`: 배고파 표현 동작
- `ate_all`: 다 먹었어 동작

**수동 제어 명령**
- `set_joint`: 단일 관절 각도를 설정. 필드: `id(1..6)`, `angle(0..180)`, `time_ms(기본 500)`
- `set_joints`: 6관절 일괄 설정. 필드: `angles(6개 정수)`, `time_ms`
- `nudge_joint`: 현재 각도에서 증분 이동. 필드: `id`, `delta(±정수)`, `time_ms(기본 300)`

**팔로우 모드 명령**
- `start_follow`: 한 팔이 다른 팔을 실시간 미러링 시작. 필드: `leader`, `follower`, `time_ms`
- `end_follow`: 팔로우 모드 종료

### 이벤트/응답(공통)

- `hello`: 앱 시작/연결 시 기능 광고. `{agent:"robot", capabilities:[...]}`
- `ack`: 명령 수락 즉시 반환. `{command, status:"accepted"}`
- `progress`: 긴 동작 시작 알림. `{command, status:"started"}`
- `result`: 동작 완료/에러/취소 결과. `{command, status:"completed|cancelled|error", outcome?|error?}`
- `joint_state`: 주기적 조인트 각도 스냅샷. `{angles:[6], seq?, ts}`
- `face_tracking`: 주기적 얼굴 감지/추적 상태. `{detected, bbox?, joints?}`

추가적으로, robot이 전송하는 모든 페이로드에는 송신자 구분을 위한 `who:"robot"`가 포함되며, MQTT 모드에서는 `robot_id`도 항상 포함됩니다.

## MQTT 모드 연동 가이드 (Spring Boot 연동용)

MQTT 브로커와 통신하는 앱은 `app_mqtt.py`입니다. 스프링부트(또는 기타 백엔드)가 MQTT를 통해 명령을 발행하면 robot이 동작하고, robot은 결과/상태/텔레메트리를 MQTT로 다시 게시합니다.

### 토픽 (분리된 구조)

- 명령 수신(Subscribe by robot):
  - 브로드캐스트: `{base}/robot/all/command`
  - 개별 로봇: `{base}/robot/{robot_id}/command`
- 이벤트 발행(Publish by robot): `{base}/robot/event`
- 관절 상태 발행(Publish by robot): `{base}/robot/joint`

기본 `base`는 `buriburi`입니다. 예:
- `buriburi/robot/all/command` (모든 로봇에 명령)
- `buriburi/robot/robot_left/command` (왼쪽 로봇에만 명령)
- `buriburi/robot/event` (이벤트/ACK/결과)
- `buriburi/robot/joint` (관절 상태 텔레메트리)

### 멀티 로봇 스코핑

- 다중 로봇을 동시에 운용할 수 있도록 `robot_id` 필드를 사용합니다.
- 유효 값: `robot_left`, `robot_right`, 또는 브로드캐스트 `all`.
- robot은 수신한 메시지의 `robot_id`가 자기 것과 다르면 무시합니다(`all`은 예외적으로 수용).

### 메시지 공통 필드

- `ts`: ISO-8601 KST(+09:00, Asia/Seoul) 타임스탬프(예: `2024-05-13T21:34:56.789+09:00`)
- `who`: 송신자 식별자. robot이 보낼 때는 `robot`으로 설정됩니다.
- `robot_id`: robot이 응답/이벤트를 게시할 때 항상 포함됩니다.

### 명령 형식 (백엔드 → robot: `{base}/robot/rx`)

모든 명령은 다음 공통 구조를 가집니다:

```json
{
	"type": "command",
	"command": "<명령 문자열>",
	"robot_id": "robot_left" // 선택: 특정 로봇 지정, 생략/"all"은 브로드캐스트
}
```

지원 명령과 payload:

- `face_tracking` | `face_tracking_mode` | `face_tracking_모드`
  - payload: 공통 필드만
- `stop_face_tracking` | `stop_face_tracking_mode`
  - payload: 공통 필드만
- `init_pose` | `init` | `ready_pose`
  - payload: 공통 필드만
- `make_heart`
  - payload: 공통 필드만
- `hug` | `make_hug`
  - payload: 공통 필드만
- `set_joint`
  - payload 예:
    ```json
    {
    	"type": "command",
    	"command": "set_joint",
    	"robot_id": "robot_left",
    	"id": 1, // 1..6
    	"angle": 90, // 0..180
    	"time_ms": 500 // 선택, 기본 500
    }
    ```
- `set_joints`
  - payload 예:
    ```json
    {
    	"type": "command",
    	"command": "set_joints",
    	"robot_id": "robot_left",
    	"angles": [90, 135, 45, 45, 90, 30], // 6개 값, 정수; null 허용 안 함
    	"time_ms": 500 // 선택
    }
    ```
- `nudge_joint`
  - payload 예:
    ```json
    {
    	"type": "command",
    	"command": "nudge_joint",
    	"robot_id": "robot_left",
    	"id": 3, // 1..6
    	"delta": -5, // 각도 증분(정수)
    	"time_ms": 300 // 선택
    }
    ```

robot는 명령을 수신하면 즉시 `ack`를 게시하고, 필요한 경우 `progress`/`result`를 이어서 게시합니다.

### 이벤트/응답 형식 (robot → 백엔드: `{base}/robot/tx`)

- Ack
  ```json
  { "type": "ack", "ts": "...", "command": "make_heart", "status": "accepted", "robot_id": "robot_left", "who": "robot" }
  ```
- 진행
  ```json
  { "type": "progress", "ts": "...", "command": "make_heart", "status": "started", "robot_id": "robot_left", "who": "robot" }
  ```
- 결과
  ```json
  { "type": "result", "ts": "...", "command": "make_heart", "status": "completed", "outcome": "ok", "robot_id": "robot_left", "who": "robot" }
  ```
- 오류
  ```json
  { "type": "error", "ts": "...", "error": "unknown_command", "command": "...", "robot_id": "robot_left", "who": "robot" }
  ```
- 조인트 상태 텔레메트리
  ```json
  { "type": "joint_state", "angles": [90, 135, 45, 45, 90, 30], "seq": 12, "ts": "...", "robot_id": "robot_left", "who": "robot" }
  ```
  - 주기적으로 게시되며 각도 변화가 작으면 전송 생략 가능
- 얼굴 추적 업데이트
  ```json
  {
  	"type": "face_tracking",
  	"status": "running",
  	"detected": true,
  	"bbox": { "x": 100, "y": 120, "w": 80, "h": 80 },
  	"joints": [90, 135, 45, 45, 90, 30],
  	"ts": "...",
  	"robot_id": "robot_left",
  	"who": "robot"
  }
  ```
- 헬로/기능 광고(연결 시)
  ```json
  { "type": "hello", "agent": "robot", "robot_id": "robot_left", "capabilities": ["face_tracking", "make_heart", "make_hug", "init_pose", "manual_control"], "ts": "...", "who": "robot" }
  ```

### 실행 방법 (MQTT)

Windows(cmd) 예시:

```cmd
cd robot
python app_mqtt.py              # 기본: 왼팔(robot_left), arm_port_left 사용
python app_mqtt.py which_arm=right  # 오른팔(robot_right), arm_port_right 사용
```

두 대를 동시에 실행하려면 서로 다른 터미널에서 각각 실행하면서 `robot_id`를 다르게 넘기거나, 각 인스턴스의 `config.json`에서 `robot_id`와 시리얼 포트(`arm_port` 또는 좌/우 포트`)를 다르게 설정하세요.

### Spring Boot 연동 예시

아래는 Spring Integration MQTT를 이용한 최소 예시입니다. 브로커 주소와 토픽은 환경에 맞게 조정하세요.

application.yml 예시:

```yaml
spring:
	integration:
		mqtt:
			client-id: "backend-app"
			url: tcp://127.0.0.1:1883
			username: ""
			password: ""
robot:
	base: robot
```

구성 및 핸들러 스켈레톤:

```java
@Configuration
public class MqttConfig {
	@Bean
	public MqttPahoClientFactory mqttClientFactory() {
		DefaultMqttPahoClientFactory f = new DefaultMqttPahoClientFactory();
		MqttConnectOptions o = new MqttConnectOptions();
		o.setServerURIs(new String[]{"tcp://127.0.0.1:1883"});
		f.setConnectionOptions(o);
		return f;
	}

	@Bean
	public MessageProducer inbound(MqttPahoClientFactory factory) {
		String topic = "robot/robot/tx"; // robot → 백엔드
		MqttPahoMessageDrivenChannelAdapter adapter =
				new MqttPahoMessageDrivenChannelAdapter("spring-subscriber", factory, topic);
		adapter.setQos(0);
		adapter.setOutputChannel(mqttInputChannel());
		return adapter;
	}

	@Bean
	public MessageChannel mqttInputChannel() { return new DirectChannel(); }

	@Bean
	@ServiceActivator(inputChannel = "mqttInputChannel")
	public MessageHandler handler() {
		return message -> {
			String topic = (String) message.getHeaders().get("mqtt_receivedTopic");
			String json = message.getPayload().toString();
			// TODO: JSON 파싱하여 type/command/status 처리
		};
	}

	@Bean
	@ServiceActivator(inputChannel = "mqttOutboundChannel")
	public MessageHandler mqttOutbound(MqttPahoClientFactory factory) {
		MqttPahoMessageHandler handler = new MqttPahoMessageHandler("spring-publisher", factory);
		handler.setAsync(true);
		handler.setDefaultTopic("robot/robot/rx"); // 백엔드 → robot
		handler.setDefaultQos(0);
		return handler;
	}

	@Bean
	public MessageChannel mqttOutboundChannel() { return new DirectChannel(); }
}

// 사용 예: 명령 발행
@Service
public class robotService {
	private final MessageChannel mqttOutboundChannel;
	public robotService(@Qualifier("mqttOutboundChannel") MessageChannel ch) { this.mqttOutboundChannel = ch; }

	public void makeHeart(String robotId) {
		String payload = "{\"type\":\"command\",\"command\":\"make_heart\",\"robot_id\":\"" + robotId + "\"}";
		Message<String> msg = MessageBuilder.withPayload(payload)
				.setHeader(MqttHeaders.TOPIC, "robot/robot/rx")
				.build();
		mqttOutboundChannel.send(msg);
	}
}
```

이 스켈레톤을 기반으로 `ack`/`result`/`joint_state`/`face_tracking` 등 이벤트를 수신하여 상태 머신이나 UI를 업데이트하면 됩니다.

### 참고 사항

- LED 제어 코드는 모션 I/O 간섭을 피하기 위해 제거되었습니다.
- `set_joint` 등 수동 제어는 80~200ms 이상의 간격으로 발행하는 것을 권장합니다.
- 두 인스턴스를 동시에 실행할 때는 고유한 MQTT `clientId`가 자동 부여되며, 같은 ID를 중복 사용하면 기존 연결이 끊길 수 있습니다.

## 도구(테스트/디버깅)

- `tools/frontend_mqtt_sep_topic.html`: 분리된 토픽 구조용 MQTT WebSocket 기반 테스트 UI
  - 3x2 로그 패널 (Send, Status, Left, Right, Frontend, SpringBoot)
  - 11가지 제스처 명령 버튼 지원
  - 팔로우 모드 시작/종료 버튼
  - 좌/우 로봇 개별 슬라이더 제어

프론트엔드 슬라이더는 `set_joint`를 80ms 간격으로 쓰로틀링하여 발행하며, 드래그 중에는 수신된 `joint_state`에 의한 값 되돌림을 억제합니다.

## 신뢰성과 안전성 메모

- 모든 Arm_Lib I/O는 공유 락으로 직렬화하여 읽기/쓰기 충돌을 방지합니다.
- 6관절 일괄 쓰기 시 내부적으로 재시도 패턴을 사용하여 드문 실패를 보완합니다.
- 텔레메트리는 변화가 작을 때 생략하고, 주기적으로 강제 스냅샷을 보냅니다.
- MQTT 모드에서는 LED 제어를 제거해 시리얼 간섭을 원천 차단했습니다.

## 멀티 로봇 운용

- 서로 다른 포트/팔을 각각의 프로세스로 실행합니다.
  - 좌/우 별로 `config.json`의 `robot_id`와 `arm_port`(또는 `arm_port_left/right`)를 구분해 설정합니다.
- MQTT 클라이언트는 인스턴스마다 고유 `client_id`를 사용합니다(중복 접속 시 기존 연결이 끊김).

## 문제 해결(FAQ)

- 두 팔을 동시에 켰더니 한쪽이 끊겨요.
  - MQTT 클라이언트 ID 중복이 없는지 확인하세요. 본 앱은 PID/프로세스 기반으로 고유 ID를 부여합니다.
- 슬라이더를 움직여도 팔이 안 움직여요.
  - 프런트엔드가 올바른 토픽/경로로 발행 중인지 확인(`robot/robot/rx`)
  - 하드웨어 연결(시리얼 포트)과 권한을 확인하세요.
- 얼굴 추적이 안 돼요.
  - `camera_index`를 올바른 카메라로 설정하고, OpenCV에서 장치가 열리는지 확인하세요.
- 조인트 값이 튀어요.
  - 너무 잦은 명령 발행을 줄이고(>=80ms), `time_ms`를 적절히 늘려 부드럽게 이동하세요.
