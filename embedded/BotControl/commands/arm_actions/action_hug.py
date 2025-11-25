import time
import threading
from typing import Optional, Dict, Any
from .action_base import ActionBase


class ActionHug(ActionBase):
    def __init__(
        self,
        arm_device,
        robot_id: Optional[str] = None,
        arm_lock: Optional[threading.Lock] = None,
        config: Optional[Dict[str, Any]] = None,
        send_callback=None,
    ):
        super().__init__(
            arm_device, robot_id=robot_id, arm_lock=arm_lock, config=config, send_callback=send_callback
        )

    def run(self, cancel_event=None) -> str:
        """포옹 동작: 왼팔 기준 시퀀스에 맞춰 수행하고, 오른팔은 좌우 미러로 수행.

        시퀀스(왼팔 기준):
          1) 팔 벌리기 (1800ms)
          2) 살짝 껴안기 (3000ms)
          3) 진짜 껴안기 (4000ms)
          4) 다시 살짝 껴안기로 복귀 (3000ms)
          5) 뉴트럴 복귀 (4000ms)
        """
        try:
            # 왼팔 기준 포즈들
            left_open = [90, 90, 85, 65, 90, 30]        # 1차: 팔 벌리기
            left_light_hug = [90, 27, 78, 70, 90, 80]   # 2차: 살짝 껴안기
            left_full_hug = [90, 26, 66, 58, 90, 110]   # 3차: 진짜 껴안기

            def pick(p: list) -> list:
                return p if self.robot_id_lower == "robot_left" else self.mirror_s1_s5(p)

            # 1차: 팔 벌리기 (1800ms)
            if not self.write6_with_overlap(pick(left_open), 1800, 100, cancel_event):
                return "hug_cancelled"

            # 2차: 살짝 껴안기 (3000ms)
            if not self.write6_with_overlap(pick(left_light_hug), 3000, 150, cancel_event):
                return "hug_cancelled"

            # 3차: 진짜 껴안기 (3000ms)
            if not self.write6_with_overlap(pick(left_full_hug), 3000, 150, cancel_event):
                return "hug_cancelled"

            # 4차: 다시 살짝 껴안기로 복귀 (3000ms)
            if not self.write6_with_overlap(pick(left_light_hug), 3000, 150, cancel_event):
                return "hug_cancelled"

            # 5차: 뉴트럴 복귀 (2000ms)
            if not self.return_to_neutral_and_notify(2000, cancel_event):
                return "hug_cancelled"

        except Exception:
            pass

        return "hug_completed"
