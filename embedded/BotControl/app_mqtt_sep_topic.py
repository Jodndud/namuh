import json
import logging
import os
import sys
import threading
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional
import ssl
from urllib.parse import urlparse

from commands.arm_actions.actions import ArmActions
from commands.face_tracking.controller import FaceTrackingController

try:
    import Arm_Lib  # type: ignore
except Exception:
    Arm_Lib = None  # type: ignore

try:
    import paho.mqtt.client as mqtt  # type: ignore
except Exception as e:  # pragma: no cover
    raise SystemExit(
        "paho-mqtt is required. Install with: pip install paho-mqtt"
    ) from e


try:  # Python 3.9+
    from zoneinfo import ZoneInfo  # type: ignore
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore


def now_iso() -> str:
    """Return ISO-8601 string in Asia/Seoul (UTC+09:00)."""
    if ZoneInfo is not None:
        try:
            return datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
        except Exception:
            pass
    # Fallback to fixed offset +09:00 if zoneinfo unavailable
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst).isoformat()


class RobotAppMQTT_SeparatedTopics:
    """
    MQTT 토픽을 역할별로 분리한 버전.

    - 명령 수신(백엔드/프론트엔드 -> 로봇): {base}/robot/all/command
    - 이벤트/결과/ACK(로봇 -> 백엔드/프론트엔드): {base}/robot/event
    - 관절 각도 텔레메트리(로봇 -> 백엔드/프론트엔드): {base}/robot/joint

    robot_id는 메시지 페이로드에 포함하여 구분합니다.
    """

    def __init__(self, config_path: str, robot_id_override: Optional[str] = None):
        # 로깅 설정
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            )
        self.log = logging.getLogger("Robot.app.mqtt.sep")

        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        # 전체 구성 보관 (하위 모듈로 전달)
        self._config = dict(cfg)

        # MQTT 구성
        self.mqtt_host = cfg.get("mqtt_host", "192.168.91.1")
        self.mqtt_port = int(cfg.get("mqtt_port", 1883))
        self.mqtt_base = cfg.get("mqtt_base", "robot")
        self.mqtt_qos = int(cfg.get("mqtt_qos", 0))

        # 구성 파일(URL) 기반 MQTT 설정 오버라이드 (TLS/웹소켓/계정 지원)
        self._mqtt_transport = "tcp"  # 'tcp' or 'websockets'
        self._mqtt_ws_path = str(cfg.get("mqtt_ws_path") or "/")
        self.mqtt_username = cfg.get("mqtt_username")
        self.mqtt_password = cfg.get("mqtt_password")
        url_cfg = cfg.get("mqtt_url") or cfg.get("mqtt_broken_url")
        topic_cfg = cfg.get("mqtt_topic")
        if topic_cfg:
            self.mqtt_base = topic_cfg
        # 기본 TLS 설정값 (config 또는 URL 스킴으로 덮어씀)
        self.mqtt_tls = bool(cfg.get("mqtt_tls", False))
        self.mqtt_tls_insecure = bool(cfg.get("mqtt_tls_insecure", False))
        self._mqtt_ca_certs = cfg.get("mqtt_ca_certs")
        if url_cfg:
            try:
                u = urlparse(url_cfg)
                scheme = (u.scheme or "").lower()
                host = u.hostname or self.mqtt_host
                port = u.port
                if scheme in ("ws", "wss"):
                    self._mqtt_transport = "websockets"
                    self.mqtt_host = host
                    self.mqtt_port = port or (443 if scheme == "wss" else 80)
                    self.mqtt_tls = scheme == "wss"
                    if u.path:
                        self._mqtt_ws_path = u.path
                elif scheme in ("ssl", "mqtts"):
                    self._mqtt_transport = "tcp"
                    self.mqtt_host = host
                    self.mqtt_port = port or 8883
                    self.mqtt_tls = True
                elif scheme in ("mqtt", "tcp", ""):
                    self._mqtt_transport = "tcp"
                    self.mqtt_host = host
                    self.mqtt_port = port or 1883
                    self.mqtt_tls = False
                else:
                    # 알 수 없는 스킴: 기본값 유지, TLS 여부만 추론
                    self.mqtt_host = host
                    if port:
                        self.mqtt_port = port
                    self.mqtt_tls = scheme in ("ssl", "mqtts")
            except Exception as e:
                logging.getLogger("Robot.app.mqtt.sep").warning(
                    "invalid mqtt_url in cfg '%s': %s", url_cfg, e
                )

        # 다중 로봇 구분용 ID
        self.robot_id = robot_id_override or str(cfg.get("robot_id") or "robot_left")

        # Arm 시리얼 포트
        if self.robot_id == "robot_left":
            self.arm_port = cfg.get("arm_port_left") or cfg.get("arm_port")
        else:
            self.arm_port = cfg.get("arm_port_right") or cfg.get("arm_port")
        if isinstance(self.arm_port, str):
            self.arm_port = self.arm_port.strip() or None

        # 분리된 MQTT 토픽 (instance attributes)
        self.topic_command = f"{self.mqtt_base}/robot/all/command"          # 브로드캐스트 명령
        self.topic_command_direct = f"{self.mqtt_base}/robot/{self.robot_id}/command"  # 개별 로봇 명령
        self.topic_event = f"{self.mqtt_base}/robot/event"                  # 이벤트/결과/ACK
        self.topic_joint = f"{self.mqtt_base}/robot/joint"                  # 관절 텔레메트리

        # 카메라 인덱스
        if self.robot_id == "robot_left":
            camera_index = int(cfg.get("camera_index_left", cfg.get("camera_index", 0)))
        else:
            camera_index = int(cfg.get("camera_index_right", cfg.get("camera_index", 0)))
        update_interval_ms = int(cfg.get("update_interval_ms", 200))

        # Follow mode defaults (peer-to-peer without backend routing)
        self._follow_default_leader = str(cfg.get("follow_leader", "robot_left"))
        self._follow_default_follower = str(cfg.get("follow_follower", "robot_right"))
        self._follow_default_time_ms = int(cfg.get("follow_time_ms", 160))
        self._follow_active = False
        self._follow_leader: Optional[str] = None
        self._follow_time_ms = self._follow_default_time_ms

        # 로봇팔 및 컨트롤러 초기화
        self.arm = None
        self._arm_io_lock = threading.Lock()
        self._last_manual_ts = 0.0
        try:
            if Arm_Lib is not None:
                if self.arm_port:
                    try:
                        self.arm = Arm_Lib.Arm_Device(port=self.arm_port)  # type: ignore[arg-type]
                    except TypeError:
                        try:
                            self.arm = Arm_Lib.Arm_Device(self.arm_port)  # type: ignore[misc]
                        except Exception:
                            self.arm = Arm_Lib.Arm_Device()
                else:
                    self.arm = Arm_Lib.Arm_Device()
        except Exception:
            self.arm = None

        try:
            self.actions = (
                ArmActions(
                    arm_device=self.arm,
                    arm_lock=self._arm_io_lock,
                    robot_id=self.robot_id,
                    config=self._config,
                    send_callback=self._send,
                )
                if self.arm is not None
                else None
            )
            if self.actions is not None:
                self.actions.set_ready_pose()
        except Exception:
            self.actions = None

        self._cmd_lock = threading.Lock()
        self._current_cmd = None
        self._action_thread = None
        self._action_cancel = None

        self.face_tracking: Optional[FaceTrackingController] = None
        if self.arm is not None:
            self.face_tracking = FaceTrackingController(
                arm_device=self.arm,
                camera_index=camera_index,
                update_interval_ms=update_interval_ms,
            )
            self.face_tracking.set_callback(self._on_face_tracking_event)
            try:
                self.face_tracking.set_arm_io_lock(self._arm_io_lock)
            except Exception:
                pass

        self.log.info(
            "initialized(sep) | mqtt=%s:%s base=%s, cam=%s, interval_ms=%s, arm=%s, port=%s",
            self.mqtt_host,
            self.mqtt_port,
            self.mqtt_base,
            camera_index,
            update_interval_ms,
            "yes" if self.arm is not None else "no",
            self.arm_port or "default",
        )
        if self.arm is not None:
            self._start_joint_stream(interval_ms=update_interval_ms)

        # MQTT 클라이언트
        client_id = f"robot-app-sep-{self.robot_id}-{os.getpid()}"
        try:
            self.client = mqtt.Client(
                client_id=client_id,
                clean_session=True,
                protocol=getattr(mqtt, "MQTTv311", 4),
                transport=self._mqtt_transport,
                callback_api_version=getattr(getattr(mqtt, "CallbackAPIVersion", None), "VERSION2", None),  # type: ignore[arg-type]
            )
        except TypeError:
            self.client = mqtt.Client(
                client_id=client_id,
                clean_session=True,
            )
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        # 웹소켓 경로 옵션 (websockets 사용 시)
        if getattr(self, "_mqtt_transport", "tcp") == "websockets":
            try:
                self.client.ws_set_options(path=self._mqtt_ws_path or "/")
            except Exception:
                pass

        # 인증/보안 설정 (connect 이전에 적용)
        try:
            if getattr(self, "mqtt_username", None):
                self.client.username_pw_set(self.mqtt_username, self.mqtt_password)
        except Exception:
            pass
        if getattr(self, "mqtt_tls", False):
            try:
                if getattr(self, "_mqtt_ca_certs", None):
                    context = ssl.create_default_context(cafile=self._mqtt_ca_certs)
                else:
                    context = ssl.create_default_context()
                if getattr(self, "mqtt_tls_insecure", False):
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                else:
                    context.check_hostname = True
                    context.verify_mode = ssl.CERT_REQUIRED
                try:
                    self.client.tls_set_context(context)
                except Exception:
                    self.client.tls_set()
                if getattr(self, "mqtt_tls_insecure", False):
                    try:
                        self.client.tls_insecure_set(True)
                    except Exception:
                        pass
            except Exception as e:
                self.log.warning("TLS setup failed: %s", e)

    # -------------- 명령어 constants (snake_case) --------------
    CMD_INIT_POSE = "init_pose"           # 초기 자세로 이동
    CMD_MAKE_HEART = "make_heart"         # 하트 제스처
    CMD_MAKE_HUG = "make_hug"             # 포옹(허그) 제스처
    CMD_MAKE_HELLO = "make_hello"         # 안녕(손인사) 제스처
    CMD_SCISSORS = "scissors"             # 가위 제스처
    CMD_ROCK = "rock"                     # 바위 제스처
    CMD_PAPER = "paper"                   # 보 제스처
    CMD_GOOD_MORNING = "good_morning"     # 좋은 아침 제스처
    CMD_GOOD_NIGHT = "good_night"         # 잘 자요 제스처
    CMD_ATE_ALL = "ate_all"               # 다 먹었어 제스처
    CMD_HUNGRY = "hungry"                 # 배고파 제스처
    # ----------------------- 테스트용 명령어 -----------------------
    CMD_START_FT = "start_face_tracking"  # 얼굴 추적 시작
    CMD_STOP_FT = "stop_face_tracking"    # 얼굴 추적 중지
    CMD_SET_JOINT = "set_joint"           # 단일 관절 각도 설정
    CMD_SET_JOINTS = "set_joints"         # 6개 관절 각도 일괄 설정
    CMD_NUDGE_JOINT = "nudge_joint"       # 단일 관절 미세 이동
    CMD_START_FOLLOW = "start_follow"     # 따라하기 시작(리더 미러링)
    CMD_END_FOLLOW = "end_follow"         # 따라하기 종료

    # -------------- MQTT 콜백 --------------
    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: dict,
        rc: int,
        properties: Optional[Any] = None,
    ):
        self.log.info("mqtt connected(sep) rc=%s", rc)
        # 명령 수신 채널 (브로드캐스트 + 개별 로봇)
        client.subscribe(self.topic_command, qos=self.mqtt_qos)
        try:
            client.subscribe(self.topic_command_direct, qos=self.mqtt_qos)
        except Exception:
            pass
        # 팔로우 모드용 모든 로봇의 joint 수신
        try:
            client.subscribe(self.topic_joint, qos=self.mqtt_qos)
        except Exception:
            pass
        # hello + capabilities 전송
        capabilities = []
        if self.face_tracking is not None:
            capabilities.append("face_tracking")
        if self.actions is not None:
            capabilities += [
                self.CMD_MAKE_HEART,
                self.CMD_MAKE_HUG,
                self.CMD_INIT_POSE,
                self.CMD_MAKE_HELLO,
                self.CMD_SCISSORS,
                self.CMD_ROCK,
                self.CMD_PAPER,
                self.CMD_GOOD_MORNING,
                self.CMD_GOOD_NIGHT,
                self.CMD_HUNGRY,
                self.CMD_ATE_ALL,
                "manual_control",
            ]
        self._send({
            "type": "hello",
            "ts": now_iso(),
            "agent": "robot",
            "robot_id": self.robot_id,
            "capabilities": capabilities,
        })

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: Any,
        rc: Any = None,
        properties: Optional[Any] = None,
        *args: Any,
        **kwargs: Any,
    ):
        try:
            rc_repr = getattr(rc, "value", rc)
        except Exception:
            rc_repr = rc
        self.log.info("mqtt disconnected rc=%s", rc_repr)

    def _on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage):
        try:
            data = json.loads(msg.payload.decode("utf-8"))
        except Exception:
            self._send({"type": "error", "ts": now_iso(), "error": "invalid_json"})
            return
        self.log.info("mqtt recv(sep) on %s: %s", msg.topic, data)

        # 텔레메트리: follow 모드 시 리더 joint를 미러링
        if msg.topic == self.topic_joint:
            try:
                if (
                    self._follow_active
                    and data.get("type") == "joint_state"
                    and isinstance(data.get("angles"), list)
                    and len(data.get("angles")) == 6
                    and data.get("robot_id") == self._follow_leader
                    and self.actions is not None
                ):
                    angles_in = data.get("angles")
                    t = int(self._follow_time_ms)
                    a = list(angles_in)
                    try:
                        leader_id = str(self._follow_leader or "").lower()
                        follower_id = str(self.robot_id or "").lower()
                        if (leader_id, follower_id) in (("robot_left", "robot_right"), ("robot_right", "robot_left")):
                            for idx in (0, 4):
                                try:
                                    v = a[idx]
                                    if v is not None:
                                        a[idx] = max(0, min(180, 180 - int(v)))
                                except Exception:
                                    pass
                    except Exception:
                        pass
                    try:
                        self._last_manual_ts = time.time()
                    except Exception:
                        pass
                    self.actions.set_joints(a, t)
            except Exception as e:
                self.log.warning("follow mirror error: %s", e)
            return

        # 명령 처리: 브로드캐스트/개별 토픽
        if msg.topic not in (self.topic_command, getattr(self, "topic_command_direct", None)):
            return

        # 다중 로봇: robot_id가 지정되어 있고, 내 로봇이 아니면 무시 (broadcast: 'all' 허용)
        rid = data.get("robot_id")
        if rid not in (None, "", self.robot_id, "all"):
            return

        # 명령만 수락
        msg_type = data.get("type")
        if msg_type is not None and msg_type != "command":
            if msg_type == "error":
                self.log.warning("mqtt error payload: %s", data)
            elif msg_type == "server_dispatch":
                self.log.debug("ignore server_dispatch: %s", data)
            return

        cmd = (data.get("command") or "").strip()
        if not cmd:
            self._send({"type": "error", "ts": now_iso(), "error": "missing_command"})
            return

        # strict snake_case commands only
        valid = {
            self.CMD_START_FT,
            self.CMD_STOP_FT,
            self.CMD_INIT_POSE,
            self.CMD_MAKE_HEART,
            self.CMD_MAKE_HUG,
            self.CMD_MAKE_HELLO,
            self.CMD_SCISSORS,
            self.CMD_ROCK,
            self.CMD_PAPER,
            self.CMD_GOOD_MORNING,
            self.CMD_GOOD_NIGHT,
            self.CMD_HUNGRY,
            self.CMD_ATE_ALL,
            self.CMD_SET_JOINT,
            self.CMD_SET_JOINTS,
            self.CMD_NUDGE_JOINT,
            self.CMD_START_FOLLOW,
            self.CMD_END_FOLLOW,
        }
        if cmd not in valid:
            self._send({"type": "error", "ts": now_iso(), "error": "unknown_command", "command": cmd})
            return

        # ack 전송
        self._send({"type": "ack", "ts": now_iso(), "command": cmd, "status": "accepted"})

        # 선점(기존 동작 중단)
        self.log.info("preempt then dispatch | command=%s", cmd)
        self._preempt_current()

        if cmd == self.CMD_START_FT:
            self._cmd_start_face_tracking(cmd); return
        if cmd == self.CMD_STOP_FT:
            self._cmd_stop_face_tracking(cmd); return
        if cmd == self.CMD_MAKE_HEART:
            self._cmd_make_heart(cmd); return
        if cmd == self.CMD_MAKE_HUG:
            self._cmd_hug(cmd); return
        if cmd == self.CMD_MAKE_HELLO:
            self._cmd_hello(cmd); return
        if cmd == self.CMD_SCISSORS:
            self._cmd_scissors(cmd); return
        if cmd == self.CMD_ROCK:
            self._cmd_rock(cmd); return
        if cmd == self.CMD_PAPER:
            self._cmd_paper(cmd); return
        if cmd == self.CMD_INIT_POSE:
            self._cmd_init_pose(cmd); return
        if cmd == self.CMD_GOOD_MORNING:
            self._cmd_good_morning(cmd); return
        if cmd == self.CMD_GOOD_NIGHT:
            self._cmd_good_night(cmd); return
        if cmd == self.CMD_HUNGRY:
            self._cmd_hungry(cmd); return
        if cmd == self.CMD_ATE_ALL:
            self._cmd_ate_all(cmd); return
        if cmd == self.CMD_SET_JOINT:
            self._cmd_set_joint(self.CMD_SET_JOINT, data); return
        if cmd == self.CMD_SET_JOINTS:
            self._cmd_set_joints(self.CMD_SET_JOINTS, data); return
        if cmd == self.CMD_NUDGE_JOINT:
            self._cmd_nudge_joint(self.CMD_NUDGE_JOINT, data); return
        if cmd == self.CMD_START_FOLLOW:
            self._cmd_start_follow(data); return
        if cmd == self.CMD_END_FOLLOW:
            self._cmd_end_follow(); return

        self._send({"type": "error", "ts": now_iso(), "error": "unknown_command", "command": cmd})

    # -------------- 명령 헬퍼 --------------
    def _preempt_current(self):
        with self._cmd_lock:
            try:
                if self.face_tracking is not None and self.face_tracking.is_running():
                    self.log.info("stopping face_tracking for preemption")
                    self.face_tracking.stop()
            except Exception:
                pass
            try:
                if self._action_thread is not None and self._action_thread.is_alive():
                    if self._action_cancel is None:
                        self._action_cancel = threading.Event()
                    self.log.info("cancelling running action thread")
                    self._action_cancel.set()
                    self._action_thread.join(timeout=2.0)
            except Exception:
                pass
            self._action_thread = None
            self._action_cancel = None
            self._current_cmd = None

    def _cmd_start_face_tracking(self, cmd: str):
        if self.face_tracking is None:
            self.log.warning("face_tracking unavailable")
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "arm_or_tracker_unavailable"})
            return
        self.log.info("starting face_tracking")
        started = self.face_tracking.start()
        self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": ("running" if started or self.face_tracking.is_running() else "already_running")})

    def _cmd_stop_face_tracking(self, cmd: str):
        if self.face_tracking is None:
            self.log.warning("stop face_tracking but tracker unavailable")
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "tracker_unavailable"})
            return
        self.log.info("stopping face_tracking")
        stopped = self.face_tracking.stop()
        self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": ("stopped" if stopped else "not_running")})

    def _cmd_make_heart(self, cmd: str):
        if self.actions is None:
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "arm_unavailable"})
            return
        self._start_action(cmd, lambda cancel: self.actions.make_heart(cancel_event=cancel))

    def _cmd_hug(self, cmd: str):
        if self.actions is None:
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "arm_unavailable"})
            return
        self._start_action(cmd, lambda cancel: self.actions.hug(cancel_event=cancel))

    def _cmd_init_pose(self, cmd: str):
        if self.actions is None:
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "arm_unavailable"})
            return
        self._start_action(cmd, lambda cancel: self.actions.init_pose(cancel_event=cancel))

    def _cmd_hello(self, cmd: str):
        if self.actions is None:
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "arm_unavailable"})
            return
        self._start_action(cmd, lambda cancel: self.actions.hello(cancel_event=cancel))

    def _cmd_good_morning(self, cmd: str):
        if self.actions is None:
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "arm_unavailable"})
            return
        self._start_action(cmd, lambda cancel: self.actions.good_morning(cancel_event=cancel))

    def _cmd_good_night(self, cmd: str):
        if self.actions is None:
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "arm_unavailable"})
            return
        self._start_action(cmd, lambda cancel: self.actions.good_night(cancel_event=cancel))

    def _cmd_hungry(self, cmd: str):
        if self.actions is None:
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "arm_unavailable"})
            return
        self._start_action(cmd, lambda cancel: self.actions.hungry(cancel_event=cancel))

    def _cmd_ate_all(self, cmd: str):
        if self.actions is None:
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "arm_unavailable"})
            return
        self._start_action(cmd, lambda cancel: self.actions.ate_all(cancel_event=cancel))

    def _cmd_scissors(self, cmd: str):
        if self.actions is None:
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "arm_unavailable"})
            return
        self._start_action(cmd, lambda cancel: self.actions.scissors(cancel_event=cancel))

    def _cmd_rock(self, cmd: str):
        if self.actions is None:
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "arm_unavailable"})
            return
        self._start_action(cmd, lambda cancel: self.actions.rock(cancel_event=cancel))

    def _cmd_paper(self, cmd: str):
        if self.actions is None:
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "arm_unavailable"})
            return
        self._start_action(cmd, lambda cancel: self.actions.paper(cancel_event=cancel))

    def _cmd_set_joint(self, cmd: str, data: Dict[str, Any]):
        if self.actions is None:
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "arm_unavailable"})
            return
        sid = data.get("id") or data.get("sid")
        angle = data.get("angle")
        t = data.get("time_ms", 500)
        try:
            sid_i = int(sid)
            if not 1 <= sid_i <= 6:
                raise ValueError("sid_out_of_range")
        except Exception:
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "invalid_sid"})
            return
        if angle is None:
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "missing_angle"})
            return
        try:
            self._last_manual_ts = time.time()
        except Exception:
            pass
        self.log.info("set_joint request | sid=%s angle=%s t=%s", sid, angle, t)
        outcome = self.actions.set_joint(sid, angle, t)
        self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": ("ok" if outcome == "ok" else "error"), "outcome": outcome})
        self.log.info("set_joint outcome | %s", outcome)

    def _cmd_set_joints(self, cmd: str, data: Dict[str, Any]):
        if self.actions is None:
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "arm_unavailable"})
            return
        angles = data.get("angles")
        t = data.get("time_ms", 500)
        try:
            self._last_manual_ts = time.time()
        except Exception:
            pass
        outcome = self.actions.set_joints(angles, t)
        self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": ("ok" if outcome == "ok" else "error"), "outcome": outcome})

    def _cmd_nudge_joint(self, cmd: str, data: Dict[str, Any]):
        if self.actions is None:
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "arm_unavailable"})
            return
        sid = data.get("id") or data.get("sid")
        delta = data.get("delta", 0)
        t = data.get("time_ms", 300)
        try:
            sid_i = int(sid)
            if not 1 <= sid_i <= 6:
                raise ValueError("sid_out_of_range")
        except Exception:
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "invalid_sid"})
            return
        try:
            int(delta)
        except Exception:
            self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": "error", "error": "invalid_delta"})
            return
        try:
            self._last_manual_ts = time.time()
        except Exception:
            pass
        outcome = self.actions.nudge_joint(sid, delta, t)
        self._send({"type": "result", "ts": now_iso(), "command": cmd, "status": ("ok" if outcome == "ok" else "error"), "outcome": outcome})

    # ---- Local follow mode (no-backend) ----
    def _cmd_start_follow(self, data: Dict[str, Any]):
        leader = str(data.get("leader") or self._follow_default_leader)
        follower = str(data.get("follower") or self._follow_default_follower)
        t = int(data.get("time_ms") or self._follow_default_time_ms)
        if self.robot_id != follower:
            self.log.info("start_follow ignored: not follower | me=%s follower=%s", self.robot_id, follower)
            self._send({"type": "result", "ts": now_iso(), "command": self.CMD_START_FOLLOW, "status": "ignored", "outcome": "not_follower"})
            return
        self._follow_active = True
        self._follow_leader = leader
        self._follow_time_ms = max(0, t)
        self.log.info("start_follow | leader=%s follower=%s t=%s", leader, follower, t)
        self._send({
            "type": "result",
            "ts": now_iso(),
            "command": self.CMD_START_FOLLOW,
            "status": "started",
            "outcome": {"leader": leader, "follower": follower, "time_ms": self._follow_time_ms},
        })

    def _cmd_end_follow(self):
        if not self._follow_active:
            self._send({"type": "result", "ts": now_iso(), "command": self.CMD_END_FOLLOW, "status": "not_running"})
            return
        self._follow_active = False
        self._follow_leader = None
        self._send({"type": "result", "ts": now_iso(), "command": self.CMD_END_FOLLOW, "status": "stopped"})

    def _start_action(self, cmd_name: str, action_callable):
        with self._cmd_lock:
            cancel_event = threading.Event()
            self._action_cancel = cancel_event
            self._current_cmd = cmd_name

            def _runner():
                try:
                    self.log.info("action start | %s", cmd_name)
                    outcome = action_callable(cancel_event)
                    status = "completed" if not cancel_event.is_set() else "cancelled"
                    self._send({"type": "result", "ts": now_iso(), "command": cmd_name, "status": status, "outcome": outcome})
                    self.log.info("action result | %s | %s (%s)", cmd_name, status, outcome)
                except Exception as e:
                    self.log.exception("action error | %s | %s", cmd_name, e)
                    self._send({"type": "result", "ts": now_iso(), "command": cmd_name, "status": "error", "error": str(e)})
                finally:
                    with self._cmd_lock:
                        self._action_thread = None
                        self._action_cancel = None
                        self._current_cmd = None

            self._send({"type": "progress", "ts": now_iso(), "command": cmd_name, "status": "started"})
            t = threading.Thread(target=_runner, name=f"Action-{cmd_name}", daemon=True)
            self._action_thread = t
            t.start()

    def _on_face_tracking_event(self, event: dict):
        event = dict(event)
        event.setdefault("ts", now_iso())
        self._send(event)

    def _send(self, obj: Dict[str, Any]):
        """이벤트/결과/ACK/hello 등을 event 토픽으로, joint_state는 joint 토픽으로 발행."""
        try:
            payload = dict(obj)
            payload["who"] = payload.get("who") or "robot"
            payload["robot_id"] = self.robot_id
            js = json.dumps(payload)
            ttype = str(payload.get("type") or "")
            if ttype == "joint_state":
                topic = self.topic_joint
            else:
                topic = self.topic_event
            self.client.publish(topic, js, qos=self.mqtt_qos)
        except Exception:
            pass

    def _start_joint_stream(self, interval_ms: int = 200):
        if getattr(self, "_telemetry_thread", None):
            return
        self._telemetry_stop = threading.Event()
        self._telemetry_seq = 0

        def _loop():
            last = [None] * 6
            first_sent = False
            force_interval_s = 1.0
            last_force = 0.0
            min_delta = 1.0
            while not self._telemetry_stop.is_set():
                now_t = time.time()
                is_active = (now_t - getattr(self, "_last_manual_ts", 0.0)) < 3.0
                sleep_sec = ((interval_ms / 1000.0) if is_active else max(0.3, (interval_ms * 2) / 1000.0))
                if self.arm is not None:

                    def _read_angles(force: bool = False) -> Optional[list]:
                        try:
                            res = []
                            acquired = False
                            if force:
                                acquired = self._arm_io_lock.acquire(timeout=0.2)
                            else:
                                acquired = self._arm_io_lock.acquire(blocking=False)
                            if not acquired:
                                return None
                            try:
                                for i in range(6):
                                    val = self.arm.Arm_serial_servo_read(i + 1)
                                    res.append(int(val) if val is not None else None)
                                    time.sleep(0.003)
                            finally:
                                try:
                                    self._arm_io_lock.release()
                                except Exception:
                                    pass
                            return res
                        except Exception:
                            return None

                    force = (now_t - last_force) >= force_interval_s
                    angles = _read_angles(force=force)
                    if angles is not None:
                        should_send = False
                        if not first_sent:
                            should_send = True
                        else:
                            for i in range(6):
                                a_new = angles[i]
                                a_old = last[i]
                                if a_new is None or a_old is None:
                                    if a_new != a_old:
                                        should_send = True
                                        break
                                else:
                                    if abs(a_new - a_old) >= min_delta:
                                        should_send = True
                                        break
                            if not should_send and force:
                                should_send = True
                        if should_send:
                            payload = {
                                "type": "joint_state",
                                "angles": angles,
                                "ts": now_iso(),
                                "robot_id": self.robot_id,
                                "seq": self._telemetry_seq,
                            }
                            self._send(payload)
                            self._telemetry_seq += 1
                            last = list(angles)
                            last_force = now_t
                            first_sent = True
                time.sleep(max(0.08, sleep_sec))

        t = threading.Thread(target=_loop, name="JointTelemetrySep", daemon=True)
        self._telemetry_thread = t
        t.start()

    def run(self):
        if getattr(self, "_mqtt_transport", "tcp") == "websockets":
            scheme = "wss" if getattr(self, "mqtt_tls", False) else "ws"
        else:
            scheme = "mqtts" if getattr(self, "mqtt_tls", False) else "mqtt"
        self.log.info(
            "connecting(sep) to %s://%s:%s base=%s user=%s",
            scheme,
            self.mqtt_host,
            self.mqtt_port,
            self.mqtt_base,
            (self.mqtt_username or "-"),
        )
        while True:
            try:
                self.client.connect(self.mqtt_host, self.mqtt_port, keepalive=30)
                break
            except Exception as e:
                self.log.warning("mqtt connect failed: %s | retry in 2s", e)
                time.sleep(2.0)
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            try:
                if self.face_tracking is not None:
                    self.face_tracking.stop()
            except Exception:
                pass
            try:
                if getattr(self, "_telemetry_stop", None) is not None:
                    self._telemetry_stop.set()
            except Exception:
                pass


if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    rid_override: Optional[str] = None
    for arg in sys.argv[1:]:
        if "=" not in arg:
            continue
        k, v = arg.split("=", 1)
        k = (k or "").strip().lower()
        v = (v or "").strip()
        if not k:
            continue
        if k == "robot_id":
            rid_override = v
        elif k in {"which_arm", "arm"}:
            vv = v.lower()
            if vv in {"left", "robot_left"}:
                rid_override = "robot_left"
            elif vv in {"right", "robot_right"}:
                rid_override = "robot_right"

    app = RobotAppMQTT_SeparatedTopics(
        config_path=os.path.join(base, "config.json"), robot_id_override=rid_override
    )
    app.run()
