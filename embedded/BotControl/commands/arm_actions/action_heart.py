import time
import threading
from typing import Optional, Dict, Any
from .action_base import ActionBase


class ActionHeart(ActionBase):
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
        """'하트' 제스처 수행 (로봇 좌/우에 따라 미러링) 후 상태 문자열 반환.

        - robot_left: 왼팔 기준 동작
        - robot_right: S1/S5 미러링 적용

        cancel_event 가 설정되면 즉시 중단하고 'heart_cancelled' 반환.
        """
        try:
            # 왼팔 기준 하트 동작 단계
            # 1차: 팔 위로 올리기
            left_raise = [87, 131, 1, 22, 90, 1]
            
            # 2차: 팔 펼리기
            left_spread = [0, 55, 65, 97, 90, 1]
            
            # 3차: 팔로 하트 만들기
            left_heart = [0, 55, 44, 0, 0, 177]
            
            # 4차: 팔 펼리기 (2차와 동일)
            left_spread_return = [0, 55, 65, 97, 90, 1]

            def pick(p):
                return p if self.robot_id_lower == "robot_left" else self.mirror_s1_s5(p)

            move_ms = int(self._config.get("heart_move_ms", 1000))
            hold_heart_s = float(self._config.get("heart_hold_s", 3.0))

            # 1차: 팔 위로 올리기
            if not self.write6_with_overlap(pick(left_raise), move_ms, 100, cancel_event):
                return "heart_cancelled"

            # 2차: 팔 펼리기
            if not self.write6_with_overlap(pick(left_spread), move_ms, 100, cancel_event):
                return "heart_cancelled"

            # 3차: 팔로 하트 만들기
            if not self.write6_with_overlap(pick(left_heart), move_ms, 100, cancel_event):
                return "heart_cancelled"

            # 하트 자세 3초 유지
            if not self.sleep_interruptible(hold_heart_s, cancel_event):
                return "heart_cancelled"

            # 4차: 팔 펼리기
            if not self.write6_with_overlap(pick(left_spread_return), move_ms, 100, cancel_event):
                return "heart_cancelled"

            # 5차: 뉴트럴 복귀
            if not self.return_to_neutral_and_notify(move_ms, cancel_event):
                return "heart_cancelled"

        except Exception:
            # 하드웨어가 없더라도 상위 흐름을 막지 않음
            pass

        return "heart_completed"
