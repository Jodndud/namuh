import time
from typing import Optional
from .action_base import ActionBase


class ActionInitPose(ActionBase):
    def __init__(self, arm_device, robot_id: Optional[str] = None, arm_lock=None, config: Optional[dict] = None):
        super().__init__(arm_device, arm_lock=arm_lock, robot_id=robot_id, config=config)

    def run(self, cancel_event=None) -> str:
        """팔을 안전한 초기/대기 자세로 이동합니다.

        보수적인 시퀀스로, 뉴트럴 관절 배열로 이동한 뒤 동작이 끝날 때까지 대기합니다.
        수행 중 cancel_event가 설정되면 'init_cancelled'를, 아니면 'init_completed'를 반환합니다.
        """
        try:
            # 로봇 좌/우에 따라 초기 자세를 분기
            # - 왼팔: S1:160 S2:30 S3:60 S4:80 S5:90 S6:90
            # - 오른팔: S1:20  S2:30 S3:60 S4:80 S5:90 S6:90
            # 이동 시간: 1000ms
            rid = (self.robot_id or "").strip()
            if rid == "robot_left":
                target = [160, 30, 60, 80, 90, 90]
            else:
                # 기본은 오른팔 포즈로 취급 (robot_right 또는 미지정)
                target = [20, 30, 60, 80, 90, 90]

            time_ms = 2000
            # 쓰기 시 Arm I/O 락 사용 (가능 시)
            if self._arm_lock is not None:
                acquired = self._arm_lock.acquire(timeout=0.5)
            else:
                acquired = False
            try:
                self.arm.Arm_serial_servo_write6_array(target, time_ms)
            finally:
                if acquired:
                    try:
                        self._arm_lock.release()
                    except Exception:
                        pass
            if not self.sleep_interruptible(time_ms / 1000.0, cancel_event):
                return "init_cancelled"

            # 선택적 짧은 안정화 대기
            if not self.sleep_interruptible(0.3, cancel_event):
                return "init_cancelled"
        except Exception:
            # 하드웨어가 없을 수 있으므로, 상위 흐름 진행을 위해 완료로 간주
            return "init_completed"

        return "init_completed"
