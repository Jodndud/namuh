import os
import time
from typing import Optional
import threading

from .action_heart import ActionHeart
from .action_hug import ActionHug
from .action_init_pose import ActionInitPose
from .action_hello import ActionHello
from .action_scissors import ActionScissors
from .action_rock import ActionRock
from .action_paper import ActionPaper
from .action_good_morning import ActionGoodMorning
from .action_good_night import ActionGoodNight
from .action_hungry import ActionHungry
from .action_ate_all import ActionAteAll


class ArmActions:
    def __init__(
        self,
        arm_device,
        arm_lock: Optional[threading.Lock] = None,
        robot_id: Optional[str] = None,
        config: Optional[dict] = None,
        send_callback=None,
    ):
        """이미 초기화된 팔(arm) 디바이스 위에 고수준 액션을 감싸는 래퍼.

        arm_device는 Arm_Lib.Arm_Device()와 호환되는 인스턴스여야 합니다.
        send_callback: MQTT 메시지 전송 콜백 함수
        """
        if arm_device is None:
            raise RuntimeError("arm_device is required")
        self.arm = arm_device
        # Arm_Lib I/O(읽기/쓰기)를 직렬화하기 위한 공유 락
        self._arm_lock = arm_lock or threading.Lock()
        # 이 인스턴스가 제어하는 로봇 ID (robot_left / robot_right)
        self.robot_id = robot_id or os.getenv("CAREBOT_ROBOT_ID")
        # 전체 구성 전달(타이밍, 포트 등)
        self.config = config or {}
        # MQTT 메시지 전송 콜백
        self._send_callback = send_callback

    def set_ready_pose(self, time_ms: int = 1500):
        """팔을 뉴트럴/대기 자세로 이동시킵니다."""
        try:
            with self._arm_lock:
                self.arm.Arm_serial_servo_write6_array(
                    [90, 150, 20, 20, 90, 30], time_ms
                )
            time.sleep(max(0.0, time_ms / 1000.0))
        except Exception:
            # 하드웨어가 없더라도 호출 측 흐름을 막지 않습니다. (에러 리포팅은 상위에서 처리)
            pass

    def shutdown(self):
        """공유 arm 디바이스에 대해 별도 동작 없음(no-op).

        ArmActions는 arm 디바이스의 소유자가 아닙니다. 앱에서 관리하며 다른 컴포넌트와
        공유됩니다. 여기서 참조를 삭제/해제하면 다른 사용자의 동작을 방해할 수 있으니 피하세요.
        """
        pass

    def make_heart(self, cancel_event=None) -> str:
        """팔로 'heart' 제스처를 수행합니다.

        do_actions 노트북에서 가져온 동작을 기반으로 하며, 짧은 상태 문자열을 반환합니다.
        """
        return ActionHeart(
            self.arm,
            robot_id=self.robot_id,
            arm_lock=self._arm_lock,
            config=self.config,
            send_callback=self._send_callback,
        ).run(cancel_event=cancel_event)

    def hug(self, cancel_event=None) -> str:
        """부드러운 'hug' 제스처를 수행하고 상태를 반환합니다."""
        return ActionHug(
            self.arm,
            robot_id=self.robot_id,
            arm_lock=self._arm_lock,
            config=self.config,
            send_callback=self._send_callback,
        ).run(cancel_event=cancel_event)

    def init_pose(self, cancel_event=None) -> str:
        """팔을 보수적인 초기/대기 자세로 이동시킵니다.

        'init_completed' 또는 'init_cancelled'를 반환합니다.
        """
        return ActionInitPose(
            self.arm,
            robot_id=self.robot_id,
            arm_lock=self._arm_lock,
            config=self.config,
        ).run(cancel_event=cancel_event)

    def hello(self, cancel_event=None) -> str:
        """커스텀 'hello' 동작을 수행합니다.

        - robot_right: 제공된 4프레임 시퀀스를 재생
        - robot_left: [90,90,90,90,90,90] 뉴트럴로 이동
        """
        return ActionHello(
            self.arm,
            robot_id=self.robot_id,
            arm_lock=self._arm_lock,
            config=self.config,
            send_callback=self._send_callback,
        ).run(cancel_event=cancel_event)

    # -------- 수동 제어 헬퍼 --------
    def set_joint(self, sid: int, angle: int, time_ms: int = 500) -> str:
        """단일 관절을 지정 각도(0-180)로 이동시킵니다."""
        try:
            sid = int(sid)
            angle = max(0, min(180, int(angle)))
            t = max(0, int(time_ms))
            with self._arm_lock:
                self.arm.Arm_serial_servo_write(sid, angle, t)
            return "ok"
        except Exception as e:
            return f"error:{e}"

    def set_joints(self, angles: list, time_ms: int = 500) -> str:
        """6개 관절을 한 번에 설정합니다. angles 길이는 반드시 6이어야 합니다."""
        try:
            if not isinstance(angles, (list, tuple)) or len(angles) != 6:
                return "error:invalid_angles"
            arr = [max(0, min(180, int(a))) for a in angles]
            t = max(0, int(time_ms))
            with self._arm_lock:
                self.arm.Arm_serial_servo_write6_array(arr, t)
            return "ok"
        except Exception as e:
            return f"error:{e}"

    def nudge_joint(self, sid: int, delta: int, time_ms: int = 300) -> str:
        """특정 관절을 delta 만큼 증분(0..180 범위 내 클램프)합니다."""
        try:
            sid = int(sid)
            d = int(delta)
            # 현재 각도를 읽습니다. 읽지 못하면 이동하지 않습니다.
            raw = None
            try:
                with self._arm_lock:
                    raw = self.arm.Arm_serial_servo_read(sid)
            except Exception:
                return "error:read_failed"
            if raw is None:
                return "error:read_failed"
            try:
                current = int(raw)
            except Exception:
                return "error:read_failed"
            target = max(0, min(180, current + d))
            t = max(0, int(time_ms))
            with self._arm_lock:
                self.arm.Arm_serial_servo_write(sid, target, t)
            return "ok"
        except Exception as e:
            return f"error:{e}"

    # -------- 가위/바위/보 포즈(파일별 액션에 위임) --------
    def scissors(self, cancel_event=None) -> str:
        return ActionScissors(
            self.arm,
            robot_id=self.robot_id,
            arm_lock=self._arm_lock,
            config=self.config,
        ).run(cancel_event=cancel_event)

    def rock(self, cancel_event=None) -> str:
        return ActionRock(
            self.arm,
            robot_id=self.robot_id,
            arm_lock=self._arm_lock,
            config=self.config,
        ).run(cancel_event=cancel_event)

    def paper(self, cancel_event=None) -> str:
        return ActionPaper(
            self.arm,
            robot_id=self.robot_id,
            arm_lock=self._arm_lock,
            config=self.config,
        ).run(cancel_event=cancel_event)

    # -------- 신규 액션들 --------
    def good_morning(self, cancel_event=None) -> str:
        return ActionGoodMorning(
            self.arm,
            robot_id=self.robot_id,
            arm_lock=self._arm_lock,
            config=self.config,
            send_callback=self._send_callback,
        ).run(cancel_event=cancel_event)

    def good_night(self, cancel_event=None) -> str:
        return ActionGoodNight(
            self.arm,
            robot_id=self.robot_id,
            arm_lock=self._arm_lock,
            config=self.config,
            send_callback=self._send_callback,
        ).run(cancel_event=cancel_event)

    def hungry(self, cancel_event=None) -> str:
        return ActionHungry(
            self.arm,
            robot_id=self.robot_id,
            arm_lock=self._arm_lock,
            config=self.config,
            send_callback=self._send_callback,
        ).run(cancel_event=cancel_event)

    def ate_all(self, cancel_event=None) -> str:
        return ActionAteAll(
            self.arm,
            robot_id=self.robot_id,
            arm_lock=self._arm_lock,
            config=self.config,
            send_callback=self._send_callback,
        ).run(cancel_event=cancel_event)
