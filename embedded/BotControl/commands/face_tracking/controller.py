import threading
import time
import os
from typing import Callable, Optional, Tuple
import cv2 as cv
from . import PID


class FaceTrackingController:
    """
    얼굴을 검출하고 팔을 움직여 따라가도록 제어하는 페이스 트래킹 컨트롤러.

    레퍼런스 구현과 유사한 PID 제어기를 사용하며, 콜백을 통해 주기적으로
    상태 업데이트를 발행합니다.

    콜백 시그니처: callback(event: dict)
    이벤트 예시: {
        "type": "face_tracking", "detected": bool, "bbox": {x,y,w,h}?,
        "joints": [s1..s6], "ts": "..."
    }
    """

    def __init__(
        self,
        arm_device,  # Arm_Lib.Arm_Device()
        camera_index: int = 0,
        update_interval_ms: int = 200,
    ):
        self._arm = arm_device
        self._camera_index = camera_index
        self._update_interval_ms = max(50, update_interval_ms)
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        # 외부에서 Arm I/O 공유 락을 주입(setter)할 수 있습니다. 미제공 시 내부 락 사용.
        self._arm_lock: Optional[threading.Lock] = None
        self._callback: Optional[Callable[[dict], None]] = None

        # PID 및 타깃 상태값
        self._target_servox = 90
        self._target_servoy = 45
        # 공용 PID 구현 사용(face_follow.py와 일관)
        self._pid_x = PID.PositionalPID(0.25, 0.1, 0.05)
        self._pid_y = PID.PositionalPID(0.25, 0.1, 0.05)

        # 이 컨트롤러와 같은 폴더의 캐스케이드를 우선 로드하고, 없으면 cv2 기본 경로 사용
        local_dir = os.path.dirname(os.path.abspath(__file__))
        local_cascade = os.path.join(local_dir, "haarcascade_frontalface_default.xml")
        if os.path.isfile(local_cascade):
            self._face_cascade = cv.CascadeClassifier(local_cascade)
        else:
            self._face_cascade = cv.CascadeClassifier(
                cv.data.haarcascades + "haarcascade_frontalface_default.xml"
            )

    def set_callback(self, callback: Callable[[dict], None]):
        self._callback = callback

    def set_arm_io_lock(self, lock: threading.Lock):
        """컴포넌트 간 Arm_Lib 접근을 직렬화하기 위해 공유 Arm I/O 락을 주입합니다."""
        self._arm_lock = lock

    def start(self) -> bool:
        with self._lock:
            if self._thread and self._thread.is_alive():
                return False
            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._run, name="FaceTrackingThread", daemon=True
            )
            self._thread.start()
            return True

    def stop(self) -> bool:
        with self._lock:
            if not self._thread:
                return False
            self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        with self._lock:
            self._thread = None
        return True

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _emit(self, event: dict):
        cb = self._callback
        if cb:
            try:
                cb(event)
            except Exception:
                pass

    def _run(self):
        cap = cv.VideoCapture(self._camera_index)
        try:
            if not cap.isOpened():
                self._emit(
                    {
                        "type": "face_tracking",
                        "status": "error",
                        "error": "camera_open_failed",
                    }
                )
                return
            last_emit = 0.0
            last_cmd = 0.0
            last_servox: Optional[int] = None
            last_servoy: Optional[int] = None
            min_cmd_interval = 0.15  # 초 단위. 서보 명령 빈도를 제한
            min_angle_delta = 1  # 도(degree) 단위. 미세 조정은 무시
            interval_s = self._update_interval_ms / 1000.0

            while not self._stop_event.is_set():
                ok, frame = cap.read()
                if not ok:
                    time.sleep(0.02)
                    continue
                frame = cv.resize(frame, (640, 480))
                gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                faces = self._face_cascade.detectMultiScale(
                    gray, scaleFactor=1.3, minNeighbors=5
                )

                bbox: Optional[Tuple[int, int, int, int]] = None
                if len(faces) > 0:
                    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                    if w >= 10 and h >= 10:
                        bbox = (int(x), int(y), int(w), int(h))
                        # 얼굴 중심 좌표
                        cx = x + w / 2.0
                        cy = y + h / 2.0

                        # 중심 주변 데드존(dead zone)
                        dead_x = (260, 380)
                        dead_y = (180, 300)

                        # X축(팬) 갱신
                        if not (
                            (self._target_servox >= 180 and cx <= 320)
                            or (self._target_servox <= 0 and cx >= 320)
                        ):
                            if not (dead_x[0] <= cx <= dead_x[1]):
                                self._pid_x.SystemOutput = cx
                                self._pid_x.SetStepSignal(320)
                                self._pid_x.SetInertiaTime(0.01, 0.1)
                                target_valuex = int(1500 + self._pid_x.SystemOutput)
                                self._target_servox = int((target_valuex - 500) / 10)
                                if self._target_servox > 180:
                                    self._target_servox = 180
                                if self._target_servox < 0:
                                    self._target_servox = 0

                        # Y축(틸트) 갱신
                        if not (
                            (self._target_servoy >= 180 and cy <= 240)
                            or (self._target_servoy <= 0 and cy >= 240)
                        ):
                            if not (dead_y[0] <= cy <= dead_y[1]):
                                self._pid_y.SystemOutput = cy
                                self._pid_y.SetStepSignal(240)
                                self._pid_y.SetInertiaTime(0.01, 0.1)
                                target_valuey = int(1500 + self._pid_y.SystemOutput)
                                self._target_servoy = (
                                    int((target_valuey - 500) / 10) - 45
                                )
                                if self._target_servoy > 360:
                                    self._target_servoy = 360
                                if self._target_servoy < 0:
                                    self._target_servoy = 0

                        joints = [
                            self._target_servox / 1.0,
                            135,
                            self._target_servoy / 2.0,
                            self._target_servoy / 2.0,
                            90,
                            30,
                        ]
                        # 서보 명령에 레이트 리밋을 적용하고, 미세한 변경은 무시하여 떨림(jitter) 방지
                        now_cmd = time.time()
                        sx = int(joints[0])
                        sy = int(joints[2]) * 2  # 절반 적용 전의 원래 servoy를 근사
                        should_send = False
                        if last_servox is None or last_servoy is None:
                            should_send = True
                        else:
                            if (
                                abs(sx - last_servox) >= min_angle_delta
                                or abs(sy - last_servoy) >= min_angle_delta
                            ):
                                should_send = True
                        if should_send and (now_cmd - last_cmd) >= min_cmd_interval:
                            try:
                                if self._arm_lock is not None:
                                    with self._arm_lock:
                                        self._arm.Arm_serial_servo_write6_array(
                                            joints, 500
                                        )
                                else:
                                    self._arm.Arm_serial_servo_write6_array(joints, 500)
                            except Exception:
                                pass
                            last_cmd = now_cmd
                            last_servox = sx
                            last_servoy = sy
                else:
                    joints = None

                now = time.time()
                if (now - last_emit) >= interval_s:
                    payload = {
                        "type": "face_tracking",
                        "status": "running",
                        "detected": bbox is not None,
                    }
                    if bbox is not None:
                        x, y, w, h = bbox
                        payload["bbox"] = {"x": x, "y": y, "w": w, "h": h}
                    if "joints" in locals() and joints is not None:
                        payload["joints"] = [int(j) for j in joints]
                    self._emit(payload)
                    last_emit = now

                time.sleep(0.01)
        finally:
            try:
                cap.release()
            except Exception:
                pass
