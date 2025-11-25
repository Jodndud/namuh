import time
from typing import Optional, Dict, Any, List
from .action_base import ActionBase


class ActionGoodNight(ActionBase):
    """"굿나잇" 제스처: 오른팔로 입에 손을 가져가 하품하는 동작.

    - 오른팔만 사용하는 비대칭 동작 (왼팔은 뉴트럴 유지)
    - 입에 손을 가져간 후 손목을 살짝 움직이며 하품 표현
    """

    def __init__(
        self,
        arm_device,
        robot_id: Optional[str] = None,
        arm_lock=None,
        config: Optional[Dict[str, Any]] = None,
        send_callback=None,
    ):
        super().__init__(arm_device, robot_id=robot_id, arm_lock=arm_lock, config=config, send_callback=send_callback)

    def run(self, cancel_event=None) -> str:
        try:
            # 오른팔만 동작 (왼팔은 이 동작을 수행하지 않음)
            if self.robot_id_lower == "robot_left":
                # 왼팔은 뉴트럴 유지만 하고 종료
                neutral = self.neutral_pose()
                self.write6_reliable(neutral, 800)
                if not self.sleep_interruptible(0.8, cancel_event):
                    return "good_night_cancelled"
                return "good_night_completed"

            # 오른팔 동작
            # 1차: 입에 손 가져가기 (하품 느낌)
            right_yawn = [135, 34, 0, 80, 119, 40]
            
            # 2차: 입에 가져간 팔 조금 움직이기
            right_move1 = [134, 29, 3, 81, 133, 91]
            right_move2 = [134, 29, 3, 81, 133, 120]

            # 1차: 입에 손 가져가기 (1800ms)
            if not self.write6_with_overlap(right_yawn, 1800, 100, cancel_event):
                return "good_night_cancelled"

            # 2차: 손목 움직이기 3회 반복 (천천히)
            move_ms = 600
            for _ in range(3):
                if not self.write6_with_overlap(right_move1, move_ms, 80, cancel_event):
                    return "good_night_cancelled"
                if not self.write6_with_overlap(right_move2, move_ms, 80, cancel_event):
                    return "good_night_cancelled"

            # 뉴트럴 복귀
            if not self.return_to_neutral_and_notify(1200, cancel_event):
                return "good_night_cancelled"
            
            return "good_night_completed"
        except Exception as e:
            return f"error:{e}"
