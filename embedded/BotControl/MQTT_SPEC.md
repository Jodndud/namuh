# Robot MQTT 통신 규격 (분리된 토픽 버전)

본 문서는 robot(로봇팔)과 백엔드 간 MQTT 메시지 형식을 한눈에 볼 수 있도록 정리한 명세입니다.

## 브로커/토픽 (분리된 구조)

- 기본 base: `buriburi`
- Back → Robot(명령 발행):
  - 브로드캐스트: `{base}/robot/all/command` (예: `buriburi/robot/all/command`)
  - 개별 로봇: `{base}/robot/{robot_id}/command` (예: `buriburi/robot/robot_left/command`)
- Robot → Back(이벤트/응답):
  - 이벤트: `{base}/robot/event` (예: `buriburi/robot/event`)
  - 관절 상태: `{base}/robot/joint` (예: `buriburi/robot/joint`)

## 공통 규칙

- `ts`: ISO-8601 KST(+09:00, Asia/Seoul) 문자열(예: `2024-05-13T21:34:56.789+09:00`)
- `robot_id`: `robot_left` | `robot_right` | `all`
  - Back→Robot에서:
    - 브로드캐스트 명령은 `{base}/robot/all/command` 토픽으로 발행 (모든 로봇이 수신)
    - 개별 명령은 `{base}/robot/{robot_id}/command` 토픽으로 발행 (해당 로봇만 수신)
  - Robot→Back 이벤트에는 항상 `robot_id` 포함
- `who`: 송신자 식별자. Robot→Back에서는 항상 `"robot"`
- QoS: 시스템 설정값 사용(README의 `mqtt_qos` 참고)

## type 목록

메시지는 방향에 따라 사용하는 type이 다릅니다. 요약은 다음과 같습니다.

- Back → Robot

  - `"command"`: 명령 전송 전용
    - 필수: `command`(snake_case)
    - 토픽: `{base}/robot/all/command` (브로드캐스트) 또는 `{base}/robot/{robot_id}/command` (개별)

- Robot → Back
  - `"hello"`: 연결/시작 시 기능 광고 (토픽: `{base}/robot/event`)
    - 필수: `agent`("robot"), `capabilities`(string[])
  - `"ack"`: 명령 수락 알림 (토픽: `{base}/robot/event`)
    - 필수: `command`, `status`("accepted")
  - `"progress"`: 긴 동작 시작 등 중간 진행 알림 (토픽: `{base}/robot/event`)
    - 필수: `command`, `status`("started")
  - `"result"`: 완료/취소/에러 결과 (토픽: `{base}/robot/event`)
    - 필수: `command`, `status`("completed"|"cancelled"|"error")
    - 선택: `outcome`(성공 요약), `error`(에러 코드)
  - `"error"`: 즉시 에러 통지 (토픽: `{base}/robot/event`)
    - 필수: `error`
    - 선택: `command`
  - `"joint_state"`: 주기 조인트 상태 텔레메트리 (토픽: `{base}/robot/joint`)
    - 필수: `angles`(길이 6의 정수 배열)
    - 선택: `seq`
  - `"face_tracking"`: 얼굴 추적 상태/감지 결과 (토픽: `{base}/robot/event`)
    - 필수: `status`("running" 등), `detected`(bool)
    - 선택: `bbox`({x,y,w,h}), `joints`([6])

공통 규칙

- 모든 Robot→Back 메시지에는 `robot_id`와 `who:"robot"`, `ts`(ISO-8601)가 포함됩니다.
- Back→Robot은 오직 `type:"command"`만 사용합니다(명령 이름은 모두 snake_case).

---

## Back → Robot (명령)

### 명령 공통 필드

- `type`: `"command"`
- `command`: 명령 문자열
- `robot_id`: 선택(특정 로봇 지정; 생략/`"all"`은 브로드캐스트)

### start_face_tracking

- 필드: 공통만

예시

```json
{
	"type": "command",
	"command": "start_face_tracking",
	"robot_id": "all"
}
```

### stop_face_tracking

- 필드: 공통만

예시

```json
{
	"type": "command",
	"command": "stop_face_tracking",
	"robot_id": "all"
}
```

### init_pose

- 필드: 공통만

예시

```json
{
	"type": "command",
	"command": "init_pose",
	"robot_id": "all"
}
```

### make_heart

- 필드: 공통만

예시

```json
{
	"type": "command",
	"command": "make_heart",
	"robot_id": "all"
}
```

### make_hug

- 필드: 공통만

예시

```json
{
	"type": "command",
	"command": "make_hug",
	"robot_id": "all"
}
```

### make_hello

- 필드: 공통만

예시

```json
{
	"type": "command",
	"command": "make_hello",
	"robot_id": "all"
}
```

### scissors

- 필드: 공통만

예시

```json
{
	"type": "command",
	"command": "scissors",
	"robot_id": "all"
}
```

### rock

- 필드: 공통만

예시

```json
{
	"type": "command",
	"command": "rock",
	"robot_id": "all"
}
```

### paper

- 필드: 공통만

예시

```json
{
	"type": "command",
	"command": "paper",
	"robot_id": "all"
}
```

### good_morning

- 필드: 공통만

예시

```json
{
	"type": "command",
	"command": "good_morning",
	"robot_id": "all"
}
```

### good_night

- 필드: 공통만

예시

```json
{
	"type": "command",
	"command": "good_night",
	"robot_id": "all"
}
```

### hungry

- 필드: 공통만

예시

```json
{
	"type": "command",
	"command": "hungry",
	"robot_id": "all"
}
```

### ate_all

- 필드: 공통만

예시

```json
{
	"type": "command",
	"command": "ate_all",
	"robot_id": "all"
}
```

### start_follow

- 설명: 팔 미러링 모드 시작. 기본값으로 `robot_left`(리더) 각도를 `robot_right`(팔로워)가 따라갑니다. 이 명령은 로봇 앱(팔로워)이 처리하며 백엔드는 단순 전달만 합니다.
- 필드: 공통 + 선택
  - `leader`: 기본 `"robot_left"`
  - `follower`: 기본 `"robot_right"`
  - `time_ms`: 미러링에 사용할 이동 시간(ms), 기본 160

예시

```json
{
	"type": "command",
	"command": "start_follow",
	"leader": "robot_left",
	"follower": "robot_right",
	"time_ms": 160
}
```

### end_follow

- 설명: 팔 미러링 모드 종료. 이 명령은 로봇 앱(팔로워)이 처리하며 백엔드는 단순 전달만 합니다.
- 필드: 공통만

예시

```json
{
	"type": "command",
	"command": "end_follow"
}
```

### set_joint

- 필드
  - `id`: 1..6 (필수)
  - `angle`: 0..180 (정수, 필수)
  - `time_ms`: 이동 시간(ms, 선택, 기본 500)

예시

```json
{
	"type": "command",
	"command": "set_joint",
	"robot_id": "robot_left",
	"id": 3,
	"angle": 90,
	"time_ms": 500
}
```

### set_joints

- 필드
  - `angles`: 길이 6의 정수 배열(필수, null 불가)
  - `time_ms`: 이동 시간(ms, 선택)

예시

```json
{
	"type": "command",
	"command": "set_joints",
	"robot_id": "robot_left",
	"angles": [90, 135, 45, 45, 90, 30],
	"time_ms": 500
}
```

### nudge_joint

- 필드
  - `id`: 1..6 (필수)
  - `delta`: 각도 증분(정수, ±, 필수)
  - `time_ms`: 이동 시간(ms, 선택, 기본 300)

예시

```json
{
	"type": "command",
	"command": "nudge_joint",
	"robot_id": "robot_left",
	"id": 2,
	"delta": -5,
	"time_ms": 300
}
```

권장 사항

- `set_*` 계열(수동 제어)은 최소 80ms 이상의 간격으로 발행 권장

---

## Robot → Back (이벤트/응답)

### 모든 메시지 공통

- `robot_id`: 항상 포함
- `who`: `"robot"`
- `ts`: ISO-8601 KST(+09:00)

### hello (연결/시작 시 기능 광고)

- 필드
  - `type`: `"hello"`
  - `agent`: `"robot"`
  - `capabilities`: 문자열 배열

예시

```json
{
	"type": "hello",
	"agent": "robot",
	"robot_id": "robot_left",
	"capabilities": ["face_tracking", "make_heart", "make_hug", "init_pose", "manual_control"],
	"ts": "...",
	"who": "robot"
}
```

### ack (명령 수락)

- 필드
  - `type`: `"ack"`
  - `command`: 원 요청 명령
  - `status`: `"accepted"`

예시

```json
{
	"type": "ack",
	"ts": "...",
	"command": "make_heart",
	"status": "accepted",
	"robot_id": "robot_left",
	"who": "robot"
}
```

### progress (긴 동작 시작)

- 필드
  - `type`: `"progress"`
  - `command`: 원 요청 명령
  - `status`: `"started"`

예시

```json
{
	"type": "progress",
	"ts": "...",
	"command": "make_heart",
	"status": "started",
	"robot_id": "robot_left",
	"who": "robot"
}
```

### result (동작 완료/취소/에러 결과)

- 필드
  - `type`: `"result"`
  - `command`: 원 요청 명령
  - `status`: `"completed" | "cancelled" | "error"`
  - `outcome`: 선택(성공 시 결과 요약)
  - `error`: 선택(에러 코드/메시지)

예시(성공)

```json
{
	"type": "result",
	"ts": "2025-11-05T11:19:41.352202+09:00",
	"command": "make_heart",
	"status": "completed",
	"outcome": "ok",
	"robot_id": "robot_left",
	"who": "robot"
}
```

예시(에러)

```json
{
	"type": "result",
	"ts": "2025-11-05T11:19:41.352202+09:00",
	"command": "set_joint",
	"status": "error",
	"error": "out_of_range",
	"robot_id": "robot_left",
	"who": "robot"
}
```

### error (즉시 에러 통지)

- 필드
  - `type`: `"error"`
  - `error`: 에러 코드(예: `"unknown_command"`)
  - `command`: 선택(관련 명령이 있는 경우)

예시

```json
{
	"type": "error",
	"ts": "2025-11-05T11:19:41.352202+09:00",
	"error": "unknown_command",
	"command": "nudge_joint",
	"robot_id": "robot_left",
	"who": "robot"
}
```

### joint_state (주기적 조인트 상태)

- 필드
  - `type`: `"joint_state"`
  - `angles`: 길이 6의 정수 배열
  - `seq`: 선택(증분 시퀀스)

예시

```json
{
	"type": "joint_state",
	"angles": [90, 135, 45, 45, 90, 30],
	"seq": 12,
	"ts": "2025-11-05T11:18:59.824113+09:00",
	"robot_id": "robot_left",
	"who": "robot"
}
```

### face_tracking (얼굴 추적 업데이트)

- 필드
  - `type`: `"face_tracking"`
  - `status`: `"running"` (필요 시 내부 상태 확장 가능)
  - `detected`: boolean
  - `bbox`: 선택 `{ x, y, w, h }`
  - `joints`: 선택 `[6]` (추적에 따른 관절 제안/상태)

예시

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

---

## 치트시트

### Back→Robot(명령 기본형)

```json
{
	"type": "command",
	"command": "<cmd>",
	"robot_id": "all"
}
```

### Robot→Back(ACK)

```json
{
	"type": "ack",
	"command": "<cmd>",
	"status": "accepted",
	"robot_id": "robot_left",
	"ts": "...",
	"who": "robot"
}
```
