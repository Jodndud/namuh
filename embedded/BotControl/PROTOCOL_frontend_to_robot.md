# Frontend → Robot(App) MQTT 페이로드 명세 (분리된 토픽 버전)

본 문서는 `embedded/BotControl/tools/frontend_mqtt_sep_topic.html`이 발행하는(Frontend → Robots/App) 모든 JSON 페이로드를 정리합니다. App(예: `app_mqtt_sep_topic.py`)은 본 명세에 맞춰 수신/처리하면 됩니다.

- 기본 토픽
  - baseTopic: 화면 입력값(기본 예: `buriburi`)
  - Frontend → Robots(App) 전송 토픽:
    - 브로드캐스트: `${base}/robot/all/command`
    - 개별 로봇: `${base}/robot/{robot_id}/command`
  - Robots(App) → Frontend 수신 토픽:
    - 이벤트: `${base}/robot/event` (참고용)
    - 관절: `${base}/robot/joint` (참고용)
- 라우팅 규칙
  - `robot_id`가 `robot_left`/`robot_right`이면 해당 로봇 대상
  - `robot_id`가 `all`이면 브로드캐스트(양쪽 모두)
  - 일부 명령은 `robot_id`를 포함하지 않습니다(글로벌 명령)
- 공통 필드
  - `type`: 문자열. 일반적으로 `"command"` 또는 `"hello"`
  - `who`: 문자열. 프론트엔드에서 발행 시 `"frontend"`

---

## 1) 핸드셰이크: hello

Frontend가 브로커에 연결되면 1회 발행합니다.

```json
{
	"type": "hello",
	"agent": "frontend"
}
```

- 토픽: `${base}/robot/all/command`
- 비고: App이 필요시 ack 또는 info를 응답할 수 있습니다(선택).

---

## 2) 단일 관절 이동: set_joint

슬라이더 조작으로 개별 관절을 특정 각도로 보냅니다. 드래그 중 80ms 쓰로틀이 적용됩니다.

```json
{
	"type": "command",
	"command": "set_joint",
	"id": 1,
	"angle": 120,
	"time_ms": 160,
	"who": "frontend",
	"robot_id": "robot_left"
}
```

- 필드
  - `id`: 1..6 (관절 번호)
  - `angle`: 0..180 (각도)
  - `time_ms`: ≥ 0 (이동 시간 ms)
  - `robot_id`: `robot_left` | `robot_right`

---

## 3) 전체 관절 일괄 이동: set_joints

6개 관절 각도를 한 번에 보냅니다.

```json
{
	"type": "command",
	"command": "set_joints",
	"angles": [90, 150, 20, 20, 90, 30],
	"time_ms": 600,
	"who": "frontend",
	"robot_id": "robot_right"
}
```

- 필드
  - `angles`: 길이 6 배열, 각 요소 0..180
  - `time_ms`: ≥ 0
  - `robot_id`: `robot_left` | `robot_right`

---

## 4) 관절 미세 조정: nudge_joint

특정 관절 각도를 `delta`만큼 증/감합니다.

```json
{
	"type": "command",
	"command": "nudge_joint",
	"id": 3,
	"delta": -5,
	"who": "frontend",
	"robot_id": "robot_left"
}
```

- 필드
  - `id`: 1..6
  - `delta`: 정수(예: -5, +5)
  - `robot_id`: `robot_left` | `robot_right`

---

## 5) 브로드캐스트 동작/제스처 명령

두 로봇 모두에게 동일 동작을 지시합니다.

공통 포맷

```json
{
	"type": "command",
	"command": "<아래 중 하나>",
	"who": "frontend",
	"robot_id": "all"
}
```

- `command` 값 목록 (11가지)
  - `start_face_tracking`
  - `stop_face_tracking`
  - `init_pose`
  - `make_heart`
  - `make_hug`
  - `make_hello`
  - `scissors`
  - `rock`
  - `paper`
  - `good_morning`
  - `good_night`
  - `hungry`
  - `ate_all`

예시

```json
{ "type": "command", "command": "make_hello", "who": "frontend", "robot_id": "all" }
```

---

## 6) 팔로우 시작: start_follow

리더/팔로워를 명시하여 팔로우 동작을 시작합니다(글로벌 명령).

```json
{
	"type": "command",
	"command": "start_follow",
	"leader": "robot_left",
	"follower": "robot_right",
	"time_ms": 160,
	"who": "frontend"
}
```

- 필드
  - `leader`: `robot_left` | `robot_right`
  - `follower`: `robot_left` | `robot_right`
  - `time_ms`: ≥ 0
- 비고: `robot_id` 필드를 포함하지 않습니다.

---

## 7) 팔로우 종료: end_follow

팔로우 동작을 종료합니다(글로벌 명령).

```json
{
	"type": "command",
	"command": "end_follow",
	"who": "frontend"
}
```

- 비고: `robot_id` 필드를 포함하지 않습니다.

---

## 필드 제약/검증 요약

- `id`: 1..6
- `angle`: 0..180
- `angles`: 길이 6, 각 요소 0..180
- `time_ms`: 0 이상 정수 권장
- `robot_id`: `robot_left` | `robot_right` | `all` (명령 종류에 따라 필수/생략)
- `who`: 문자열, 프론트엔드에서는 `"frontend"` 사용

## 운영 팁/에지 케이스

- 쓰로틀: `set_joint`는 슬라이더 조작 시 80ms 쓰로틀로 빈도 제어
- 브로드캐스트: `robot_id = "all"`은 양쪽 로봇에 동일하게 전달됨
- 글로벌 명령: `start_follow`, `end_follow`는 `robot_id` 없이 동작(시스템 전역 상태)
- 유효성: App에서 각 필드 유효성 검사 후 `ack`/`progress`/`result`로 응답 권장
- 스케일: 고빈도 명령(`set_joint`) 수신 시 내부 큐/디바운싱 필요할 수 있음

---

문서 버전: 2025-11-07
