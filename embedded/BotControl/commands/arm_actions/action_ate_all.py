import time
from typing import Optional, Dict, Any, List
from .action_base import ActionBase


class ActionAteAll(ActionBase):
    """"다 먹었어!" 제스처: 팔을 들고 배를 두들기며 만족감을 표현.

    - 팔을 살짝 들어 올린 후 배를 톡톡 두들기는 동작을 4회 반복합니다.
    - 브로드캐스트 시 양팔이 동시에 배를 두들기는 귀여운 동작을 수행합니다.
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
            move_ms = int(self.config.get("ate_move_ms", 800))
            pat_ms = int(self.config.get("ate_pat_ms", 400))
            pat_repeat = int(self.config.get("ate_pat_repeat", 4))

            # 1차: 팔 조금 들기 (왼팔 기준)
            left_raise = [138, 5, 91, 60, 90, 90]

            # 배 두들기기 - 뗀 상태 (왼팔/오른팔 별도)
            left_pat_off = [123, 18, 61, 40, 111, 180]
            right_pat_off = [57, 18, 61, 40, 66, 178]

            # 배 두들기기 - 두들기는 상태 (왼팔/오른팔 별도)
            left_pat_on = [132, 23, 53, 23, 111, 83]
            right_pat_on = [45, 24, 56, 17, 68, 89]

            # 로봇별 포즈 선택 헬퍼
            def pick_symmetric(left_pose: List[int]) -> List[int]:
                """S1/S5 미러링 적용"""
                return left_pose if self.robot_id_lower == "robot_left" else self.mirror_s1_s5(left_pose)

            def pick_asymmetric(left_pose: List[int], right_pose: List[int]) -> List[int]:
                """왼팔/오른팔 전용 포즈 선택"""
                return left_pose if self.robot_id_lower == "robot_left" else right_pose

            # 1차: 팔 조금 들기
            if not self.write6_with_overlap(pick_symmetric(left_raise), move_ms, 100, cancel_event):
                return "ate_all_cancelled"

            # 두들기기 반복 4번
            for _ in range(max(1, pat_repeat)):
                # 뗀 상태
                if not self.write6_with_overlap(pick_asymmetric(left_pat_off, right_pat_off), pat_ms, 80, cancel_event):
                    return "ate_all_cancelled"
                # 두들기는 상태
                if not self.write6_with_overlap(pick_asymmetric(left_pat_on, right_pat_on), pat_ms, 80, cancel_event):
                    return "ate_all_cancelled"

            # 2차: 팔 조금 들기
            if not self.write6_with_overlap(pick_symmetric(left_raise), move_ms, 100, cancel_event):
                return "ate_all_cancelled"

            # 3차: 뉴트럴
            if not self.return_to_neutral_and_notify(move_ms, cancel_event):
                return "ate_all_cancelled"

            return "ate_all_completed"
        except Exception as e:
            return f"error:{e}"
