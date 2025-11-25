import time
from typing import Optional, Dict, Any, List
from .action_base import ActionBase


class ActionGoodMorning(ActionBase):
    """"굿모닝" 제스처: 기지개를 켜듯 팔을 하늘로 쭉 뻗으며 스트레칭합니다.

    - 손을 위로 회전시켜 들어 올린 후, 하늘로 쭉 뻗으며 살짝 펼치는 동작
    - 자연스럽게 팔을 내린 후 뉴트럴 포즈로 복귀
    - 왼팔/오른팔 전용 각도로 비대칭 동작 구현
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
            # 1차: 손을 위로 들기 위한 회전
            left_rotate = [50, 103, 0, 18, 76, 67]
            right_rotate = [180, 180, 15, 0, 123, 90]
            
            # 2차: 하늘로 뻗으며 펼치기 (3단계)
            left_stretch1 = [0, 66, 56, 19, 76, 66]
            left_stretch2 = [0, 34, 73, 76, 0, 1]
            left_stretch3 = [0, 18, 108, 94, 0, 55]
            
            right_stretch1 = [180, 65, 52, 60, 90, 0]
            right_stretch2 = [179, 27, 48, 74, 179, 36]
            right_stretch3 = [179, 29, 85, 83, 179, 57]
            
            # 3차: 팔 내리기 연결 동작 (왼팔 기준)
            left_lower1 = [57, 143, 1, 1, 89, 54]

            def pick(left_pose: List[int], right_pose: List[int]) -> List[int]:
                """왼팔/오른팔 전용 포즈 선택"""
                return left_pose if self.robot_id_lower == "robot_left" else right_pose
            
            def pick_symmetric(left_pose: List[int]) -> List[int]:
                """S1/S5 미러링 적용"""
                return left_pose if self.robot_id_lower == "robot_left" else self.mirror_s1_s5(left_pose)

            # 1차: 손 회전 (왼팔 1600ms, 오른팔 1800ms)
            rotate_ms = 1600 if self.robot_id_lower == "robot_left" else 1800
            if not self.write6_with_overlap(pick(left_rotate, right_rotate), rotate_ms, 100, cancel_event):
                return "good_morning_cancelled"

            # 2차: 하늘로 뻗으며 펼치기 (3단계, 각 1200ms)
            stretch_ms = 1200   
            if not self.write6_with_overlap(pick(left_stretch1, right_stretch1), stretch_ms, 100, cancel_event):
                return "good_morning_cancelled"
            if not self.write6_with_overlap(pick(left_stretch2, right_stretch2), stretch_ms, 100, cancel_event):
                return "good_morning_cancelled"
            if not self.write6_with_overlap(pick(left_stretch3, right_stretch3), stretch_ms, 100, cancel_event):
                return "good_morning_cancelled"

            # 3차: 팔 내리기 (왼팔 기준, 미러링 적용)
            # lower_ms = 900
            # if not self.write6_with_overlap(pick_symmetric(left_lower1), lower_ms, 100, cancel_event):
            #     return "good_morning_cancelled"

            # 4차: 뉴트럴 복귀 (1800ms)
            if not self.return_to_neutral_and_notify(1800, cancel_event):
                return "good_morning_cancelled"
            
            return "good_morning_completed"
        except Exception as e:
            return f"error:{e}"
