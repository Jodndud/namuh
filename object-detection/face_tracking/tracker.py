# tracker.py
# 미디어파이프에 감지된 사람 얼굴 좌표 변환
import time
import json

class FaceTracker:
    def __init__(self):
        self.last_sent_time = 0
        self.send_interval = 0.15  # 0.15초마다 전송 (너무 자주 보내면 렉 걸림)

    def get_tracking_payload(self, face_result):
        """
        MediaPipe 결과를 받아 MQTT로 보낼 JSON 문자열을 반환
        보낼 필요가 없거나(시간 안 됨), 얼굴이 없으면 None을 반환
        """
        now = time.time()
        
        # 전송 주기 체크 (너무 빠르면 스킵)
        if now - self.last_sent_time < self.send_interval:
            return None

        # 얼굴 감지 여부 확인
        if not face_result or not face_result.face_landmarks:
            # 얼굴을 놓쳤을 때 'track_lost' 명령 전송
            # print("[Tracker] ❌ 놓침 (Face Lost) -> 'track_lost' 전송")
            
            self.last_sent_time = now 
            return json.dumps({
                "type": "command",
                "command": "track_lost"
            })

        # 좌표 추출 (첫 번째 얼굴의 1번 랜드마크 = 코 끝)
        try:
            # 첫 번째 얼굴의 1번 랜드마크 = 코 끝
            # (MediaPipe 버전에 따라 접근 방식이 다를 수 있어 안전하게 처리)
            if hasattr(face_result.face_landmarks[0], 'landmark'):
                nose_tip = face_result.face_landmarks[0].landmark[6] # 최신 Task API 객체 방식
            else:
                nose_tip = face_result.face_landmarks[0][1] # 리스트/딕셔너리 방식

            x = nose_tip.x
            y = nose_tip.y
            
            # 로그: 얼굴 감지됨 (좌표 출력)
            print(f"[Tracker] 🎯 감지됨 (Tracking) - X: {x:.3f}, Y: {y:.3f}")

            self.last_sent_time = now

            # JSON 생성
            return json.dumps({
                "type": "command",
                "command": "track_face",
                "x": round(x, 3),
                "y": round(y, 3)
            })
            
        except Exception as e:
            print(f"[Tracker] ⚠️ 좌표 계산 중 에러 발생: {e}")
            return None
