import time
from typing import Optional, Dict, Any, List
from .action_base import ActionBase


class ActionHungry(ActionBase):
    """"배고파" 제스처: 배를 가리키거나 문지르는 느낌의 짧은 동작.

    - 복부 근처로 팔을 당긴 뒤, S4(팔꿈치) 각도를 살짝 오가며 2회 문지르는 느낌을 냅니다.
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
            # 타이밍 파라미터 (기존 키 유지 + 추가)
            raise_ms = int(self.config.get("hungry_raise_ms", self.config.get("hungry_move_ms", 900)))
            overlap_ms = int(self.config.get("hungry_overlap_ms", 140))
            rub_ms = int(self.config.get("hungry_rub_ms", 420))
            rub_repeat = int(self.config.get("hungry_rub_repeat", 2))
            hold_between_rub_s = float(self.config.get("hungry_hold_between_s", 0.0))
            return_hold_s = float(self.config.get("hungry_return_hold_s", 0.0))

            # 순서:
            # 1) 팔 올리기 (배 가리키는 위치)
            # 2) rub_a / rub_b 교대 반복
            # 3) 잠시 유지 후 뉴트럴 복귀

            # 왼팔 기준 제공된 각도
            left_raise = [147, 36, 40, 52, 90, 16]
            left_rub_a = [138, 0, 52, 54, 144, 17]
            left_rub_b = [141, 4, 79, 21, 144, 76]

            def pick(p: List[int]) -> List[int]:
                # 오른팔이면 S1,S5 미러링 적용
                return p if self.robot_id_lower == "robot_left" else self.mirror_s1_s5(p)

            # 1) 팔 올리기 (오버랩 스케줄로 부드럽게 시작)
            if not self.write6_with_overlap(pick(left_raise), raise_ms, overlap_ms, cancel_event):
                return "hungry_cancelled"

            # 2) 문지르기 반복 (rub_ms 사용, 각 프레임 오버랩 100ms 기본)
            rub_overlap_ms = int(min(rub_ms - 20, 100)) if rub_ms > 40 else 0
            for i in range(max(1, rub_repeat)):
                if not self.write6_with_overlap(pick(left_rub_a), rub_ms, rub_overlap_ms, cancel_event):
                    return "hungry_cancelled"
                if hold_between_rub_s > 0:
                    if not self.sleep_interruptible(hold_between_rub_s, cancel_event):
                        return "hungry_cancelled"
                if not self.write6_with_overlap(pick(left_rub_b), rub_ms, rub_overlap_ms, cancel_event):
                    return "hungry_cancelled"
                if hold_between_rub_s > 0 and i < rub_repeat - 1:
                    if not self.sleep_interruptible(hold_between_rub_s, cancel_event):
                        return "hungry_cancelled"

            # 3) 다시 팔 올리기 포즈로 복귀 (지정 시퀀스: raise -> [rub_a, rub_b] -> raise -> neutral)
            if not self.write6_with_overlap(pick(left_raise), raise_ms, overlap_ms, cancel_event):
                return "hungry_cancelled"

            # 4) 뉴트럴 복귀 후 선택적 추가 유지
            if not self.return_to_neutral_and_notify(raise_ms, cancel_event):
                return "hungry_cancelled"
            if return_hold_s > 0:
                if not self.sleep_interruptible(return_hold_s, cancel_event):
                    return "hungry_cancelled"
            return "hungry_completed"
        except Exception as e:
            return f"error:{e}"
