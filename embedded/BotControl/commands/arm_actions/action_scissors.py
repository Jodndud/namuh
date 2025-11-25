from .action_base import ActionBase


class ActionScissors(ActionBase):
    def run(self, cancel_event=None) -> str:
        try:
            # 1차: 준비 동작 (왼팔 기준, 오른팔은 미러링)
            left_ready = [46, 45, 90, 45, 89, 90]
            
            # 2차: 가위 (기존과 동일)
            #  - 왼팔: S5=180
            #  - 오른팔: S5=0 (그 외 동일)
            left_scissors = [90, 0, 90, 90, 180, 180]
            right_scissors = [90, 0, 90, 90, 0, 180]

            def pick_ready(p):
                return p if self.robot_id_lower == "robot_left" else self.mirror_s1_s5(p)
            
            def pick_scissors():
                return left_scissors if self.robot_id_lower == "robot_left" else right_scissors

            # 1차: 준비 동작 (1500ms)
            if not self.write6_with_overlap(pick_ready(left_ready), 1500, 100, cancel_event):
                return "scissors_cancelled"

            # 2차: 가위 (400ms)
            if not self.write6_with_overlap(pick_scissors(), 400, 80, cancel_event):
                return "scissors_cancelled"

            return "scissors_completed"
        except Exception as e:
            return f"error:{e}"
