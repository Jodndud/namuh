import time
import random
from typing import Optional
from .action_base import ActionBase


class ActionHello(ActionBase):
    def __init__(
        self,
        arm_device,
        robot_id: Optional[str] = None,
        arm_lock=None,
        config: Optional[dict] = None,
        send_callback=None,
    ):
        super().__init__(
            arm_device, robot_id=robot_id, arm_lock=arm_lock, config=config, send_callback=send_callback
        )

    def run(self, cancel_event=None) -> str:
        try:
            # 타이밍 설정 (오버랩 기반으로 부드럽게)
            raise_ms = int(self.config.get("hello_raise_ms", 900))
            wave_ms = int(self.config.get("hello_wave_ms", 420))
            overlap_ms = int(self.config.get("hello_overlap_ms", 140))
            wave_repeat = int(self.config.get("hello_wave_repeat", 10))
            jitter_deg = int(self.config.get("hello_wave_jitter", 6))  # 각도 랜덤 변형 폭
            hold_neutral_s = float(self.config.get("hello_hold_neutral_s", 0.0))
            return_ms = int(self.config.get("hello_return_ms", max(1200, raise_ms)))

            # 왼팔 기준 포즈 정의
            left_raise = [0, 25, 60, 90, 0, 90]
            seed_waves = [
                [0, 15, 65, 50, 0, 125],
                [0, 27, 88, 105, 0, 29],
                [0, 20, 93, 92, 0, 70],
                [4, 31, 75, 80, 0, 40],
            ]

            def clamp(v: int) -> int:
                return max(0, min(180, int(v)))

            def jitter_pose(base):
                # S2,S3,S4,S6에만 소폭 지터 적용해 자연스런 흔들기 생성
                p = list(base)
                for idx in (1, 2, 3, 5):  # S2,S3,S4,S6
                    j = random.randint(-jitter_deg, jitter_deg)
                    p[idx] = clamp(p[idx] + j)
                return p

            def pick(p):
                # 오른팔은 S1,S5 미러링
                return p if self.robot_id_lower == "robot_left" else self.mirror_s1_s5(p)

            # 1) 팔 올리기
            if not self.write6_with_overlap(pick(left_raise), raise_ms, overlap_ms, cancel_event):
                return "hello_cancelled"

            # 2) 흔들기: 시드에서 랜덤 선택 + 지터 적용하여 매번 다른 프레임 생성
            for _ in range(max(1, wave_repeat)):
                base = random.choice(seed_waves)
                pose = jitter_pose(base)
                if not self.write6_with_overlap(pick(pose), wave_ms, min(overlap_ms, max(0, wave_ms - 20)), cancel_event):
                    return "hello_cancelled"

            # 3) 뉴트럴 복귀 (사이드별) - 조금 더 천천히 복귀
            if not self.return_to_neutral_and_notify(return_ms, cancel_event):
                return "hello_cancelled"
            if hold_neutral_s > 0:
                if not self.sleep_interruptible(hold_neutral_s, cancel_event):
                    return "hello_cancelled"
            return "hello_completed"
        except Exception as e:
            return f"error:{e}"
