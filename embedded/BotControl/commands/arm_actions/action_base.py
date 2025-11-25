import time
import threading
from typing import Optional, Dict, Any, Iterable, List


class ActionBase:
    """팔 동작을 위한 통합 베이스 클래스.

    제공 기능:
    - 공통 생성자: arm, robot_id(원본/소문자), lock, config 보관
    - write6: 6축 각도를 기본 방식으로 쓰기(옵션 락)
    - write6_reliable: 드롭 방지를 위해 짧은 간격으로 2회 전송
    - sleep_interruptible: cancel_event을 지원하는 협조적 대기
    - mirror_all: 모든 관절을 180-각도로 미러링
    - mirror_s1_s5: S1(베이스), S5(손목 yaw)만 도메인 특화 미러링
    - neutral_pose(): 자주 쓰는 뉴트럴 포즈 제공(좌/우 로봇별 반환)
    - run_pose(left_angles, result_prefix, cancel_event): 단일 포즈 액션 템플릿
    """

    def __init__(
        self,
        arm_device,
        robot_id: Optional[str] = None,
        arm_lock: Optional[threading.Lock] = None,
        config: Optional[Dict[str, Any]] = None,
        send_callback=None,
    ):
        if arm_device is None:
            raise RuntimeError("arm_device는 필수입니다")
        self.arm = arm_device
        self.robot_id = robot_id
        self.robot_id_lower = (robot_id or "robot_left").lower()
        self._arm_lock = arm_lock or threading.Lock()
        # 과거 액션들과 호환성을 위해 두 이름(config/_config)을 모두 유지
        self.config: Dict[str, Any] = dict(config or {})
        self._config = self.config
        # MQTT 메시지 전송 콜백
        self._send_callback = send_callback

    # ---- 쓰기 유틸 ----
    def write6(self, arr: List[int], t: int):
        if self._arm_lock is not None:
            self._arm_lock.acquire()
        try:
            self.arm.Arm_serial_servo_write6_array(arr, int(t))
        finally:
            try:
                if self._arm_lock is not None:
                    self._arm_lock.release()
            except Exception:
                pass

    def write6_reliable(self, angles: List[int], time_ms: int):
        try:
            with self._arm_lock:
                self.arm.Arm_serial_servo_write6_array(angles, int(time_ms))
        except Exception:
            pass
        try:
            time.sleep(0.03)
        except Exception:
            pass
        try:
            if self._arm_lock.acquire(timeout=0.05):
                try:
                    self.arm.Arm_serial_servo_write6_array(angles, int(time_ms))
                finally:
                    try:
                        self._arm_lock.release()
                    except Exception:
                        pass
        except Exception:
            pass

    def write6_with_overlap(
        self, angles: List[int], move_ms: int, overlap_ms: int, cancel_event
    ) -> bool:
        """연속 프레임을 자연스럽게 연결하기 위한 보조 함수.

        - 현재 프레임을 write6_reliable로 시작하고,
        - (move_ms - overlap_ms) 만큼만 대기한 뒤 호출자에게 제어를 반환합니다.
          호출자는 즉시 다음 프레임을 전송하여 끊김 없이 이어지게 할 수 있습니다.

        반환값: 취소되지 않으면 True, cancel_event로 중단되면 False.
        """
        try:
            self.write6_reliable(angles, move_ms)
        except Exception:
            pass
        wait_s = max(0.0, (int(move_ms) - max(0, int(overlap_ms))) / 1000.0)
        return self.sleep_interruptible(wait_s, cancel_event)

    # ---- 취소 지원 대기 ----
    def sleep_interruptible(self, seconds: float, cancel_event) -> bool:
        if cancel_event is None:
            time.sleep(seconds)
            return True
        end = time.time() + seconds
        step = 0.05
        while time.time() < end:
            if cancel_event.is_set():
                return False
            time.sleep(min(step, max(0.0, end - time.time())))
        return True

    # ---- 미러링 유틸 ----
    @staticmethod
    def mirror_all(angles: Iterable[int]) -> List[int]:
        res: List[int] = []
        for a in angles:
            try:
                ai = int(a)
            except Exception:
                ai = 0
            res.append(max(0, min(180, 180 - ai)))
        return res

    @staticmethod
    def mirror_s1_s5(pose: List[int]) -> List[int]:
        q = list(pose)
        try:
            q[0] = max(0, min(180, 180 - int(q[0])))
            q[4] = max(0, min(180, 180 - int(q[4])))
        except Exception:
            pass
        return q

    # ---- 뉴트럴 포즈 ----
    def neutral_pose(self) -> List[int]:
        """현재 로봇 기준 뉴트럴 포즈를 반환합니다.

        - robot_left: [160, 30, 60, 80, 90, 90]
        - robot_right (기본): [20, 30, 60, 80, 90, 90]
        """
        rid = self.robot_id_lower
        if rid == "robot_left":
            return [160, 30, 60, 80, 90, 90]
        # 기본은 오른팔 기준
        return [20, 30, 60, 80, 90, 90]

    def return_to_neutral_and_notify(self, time_ms: int, cancel_event) -> bool:
        """뉴트럴 포즈로 복귀하고 init_completed 메시지를 전송합니다.
        
        Args:
            time_ms: 이동 시간 (밀리초)
            cancel_event: 취소 이벤트
        
        Returns:
            취소되지 않으면 True, 취소되면 False
        """
        neutral = self.neutral_pose()
        self.write6_reliable(neutral, time_ms)
        if not self.sleep_interruptible(time_ms / 1000.0, cancel_event):
            return False
        
        # init_completed 메시지 전송
        if self._send_callback is not None:
            try:
                self._send_callback({
                    "type": "result",
                    "command": "init_pose",
                    "status": "completed",
                    "outcome": "init_completed"
                })
            except Exception:
                pass
        
        return True

    # ---- 단일 포즈 액션 템플릿 ----
    def run_pose(
        self, left_angles: List[int], result_prefix: str, cancel_event=None
    ) -> str:
        try:
            arr = (
                left_angles
                if self.robot_id_lower == "robot_left"
                else self.mirror_all(left_angles)
            )
            if cancel_event is not None and cancel_event.is_set():
                return f"{result_prefix}_cancelled"
            t = int(self.config.get("gesture_time_ms", 600))
            self.write6(arr, t)
            time.sleep(max(0.0, t / 1000.0))
            return f"{result_prefix}_completed"
        except Exception as e:
            return f"error:{e}"
