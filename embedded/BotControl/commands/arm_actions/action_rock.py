from .action_base import ActionBase


class ActionRock(ActionBase):
    def run(self, cancel_event=None) -> str:
        try:
            # 1차: 준비 동작 (왼팔 기준, 오른팔은 미러링)
            left_ready = [46, 45, 90, 45, 89, 90]
            
            # 2차: 바위 (왼팔 기준)
            left_rock = [180, 45, 80, 0, 90, 90]

            def pick(p):
                return p if self.robot_id_lower == "robot_left" else self.mirror_s1_s5(p)

            # 1차: 준비 동작 (1500ms)
            if not self.write6_with_overlap(pick(left_ready), 1500, 100, cancel_event):
                return "rock_cancelled"

            # 2차: 바위 (400ms)
            if not self.write6_with_overlap(pick(left_rock), 400, 80, cancel_event):
                return "rock_cancelled"

            return "rock_completed"
        except Exception as e:
            return f"error:{e}"
