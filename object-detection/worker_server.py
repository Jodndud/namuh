import asyncio
import base64
import signal
import cv2
import numpy as np
import os
import time
import ssl
from aiortc import (
    RTCConfiguration,
    RTCIceServer,
    RTCPeerConnection,
    RTCSessionDescription,
    RTCIceCandidate,
)
from aiortc.contrib.media import MediaStreamTrack
from aiortc.sdp import candidate_from_sdp
import requests
from av import VideoFrame
from fractions import Fraction
import websockets
import json
import warnings
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

import httpx
from collections import deque
from datetime import datetime

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2

import aiomqtt as mqtt

import dotenv

warnings.filterwarnings("ignore", message="Unverified HTTPS request")
dotenv.load_dotenv()

SESSION_ID = os.getenv("SESSION_ID")
WORKER_PARTICIPANT_ID = os.getenv(
    "WORKER_PARTICIPANT_ID", "mediapipe_worker_subscriber"
)
OPENVIDU_URL = os.getenv("OPENVIDU_URL")
OPENVIDU_USER = os.getenv("OPENVIDU_USER")
OPENVIDU_SECRET = os.getenv("OPENVIDU_SECRET")
API_UPLOAD_URL = os.getenv("API_UPLOAD_URL")
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_SECRET = os.getenv("MQTT_SECRET")
MQTT_REQUEST_TOPIC = os.getenv("MQTT_REQUEST_TOPIC")
MQTT_RESPONSE_TOPIC = os.getenv("MQTT_RESPONSE_TOPIC")

SMILE_THRESHOLD = 0.3
COOLDOWN_SECONDS = 3.0
SAVING_PRE_POST_SECONDS = 5.0
FPS = 30.0
VIDEO_DIR = "smile_videos"

pre_buffer = deque(maxlen=int(FPS * SAVING_PRE_POST_SECONDS))
is_saving = False
post_frames_remaining = 0
video_writer = None
last_smile_trigger_time = 0.0
current_video_path = None
face_landmarker = None
pose_detector = None
rsp_detector = None
last_frame_for_rsp = None

mp_pose = mp.solutions.pose


class RSPDetector:
    def calculate_angle(self, a_coord, b_coord, c_coord):
        vec_ba = a_coord - b_coord
        vec_bc = c_coord - b_coord

        dot_product = np.dot(vec_ba, vec_bc)
        norm_ba = np.linalg.norm(vec_ba)
        norm_bc = np.linalg.norm(vec_bc)

        if norm_ba == 0 or norm_bc == 0:
            return 0.0

        cosine_angle = dot_product / (norm_ba * norm_bc)
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)

        angle = np.degrees(np.arccos(cosine_angle))
        return angle

    def _get_coords(self, landmarks, lm_enum):
        lm = landmarks.landmark[lm_enum]
        return np.array([lm.x, lm.y, lm.z])

    def classify_pose(self, landmarks):
        L_SH = self._get_coords(landmarks, mp_pose.PoseLandmark.LEFT_SHOULDER)
        R_SH = self._get_coords(landmarks, mp_pose.PoseLandmark.RIGHT_SHOULDER)
        L_EL = self._get_coords(landmarks, mp_pose.PoseLandmark.LEFT_ELBOW)
        R_EL = self._get_coords(landmarks, mp_pose.PoseLandmark.RIGHT_ELBOW)
        L_WR = self._get_coords(landmarks, mp_pose.PoseLandmark.LEFT_WRIST)
        R_WR = self._get_coords(landmarks, mp_pose.PoseLandmark.RIGHT_WRIST)
        L_HIP = self._get_coords(landmarks, mp_pose.PoseLandmark.LEFT_HIP)
        R_HIP = self._get_coords(landmarks, mp_pose.PoseLandmark.RIGHT_HIP)

        left_elbow_angle = self.calculate_angle(L_SH, L_EL, L_WR)
        right_elbow_angle = self.calculate_angle(R_SH, R_EL, R_WR)

        left_shoulder_angle = self.calculate_angle(L_HIP, L_SH, L_EL)
        right_shoulder_angle = self.calculate_angle(R_HIP, R_SH, R_EL)

        left_z_diff = L_WR[2] - L_SH[2]
        right_z_diff = R_WR[2] - R_SH[2]

        left_x_diff = abs(L_WR[0] - L_SH[0])
        right_x_diff = abs(R_WR[0] - R_SH[0])

        ELBOW_STRAIGHT_TH = 90.0
        SHOULDER_ROCK_TH = 45.0
        X_WIDTH_THRESHOLD = 0.15
        Z_FORWARD_TH = -0.15

        is_rock = (
            left_shoulder_angle < SHOULDER_ROCK_TH
            and right_shoulder_angle < SHOULDER_ROCK_TH
        )

        if is_rock:
            return "Rock"

        are_arms_straight_enough = (
            left_elbow_angle > ELBOW_STRAIGHT_TH
            and right_elbow_angle > ELBOW_STRAIGHT_TH
        )
        if not are_arms_straight_enough:
            return "Unknown"

        is_wide = left_x_diff > X_WIDTH_THRESHOLD and right_x_diff > X_WIDTH_THRESHOLD
        if is_wide:
            return "Paper"

        is_narrow = left_x_diff < X_WIDTH_THRESHOLD and right_x_diff < X_WIDTH_THRESHOLD
        is_forward = left_z_diff < Z_FORWARD_TH and right_z_diff < Z_FORWARD_TH

        if is_narrow and is_forward:
            return "Scissors"

        return "Unknown"


print("MediaPipe 모델 로드 중...")
try:
    BaseOptions = mp.tasks.BaseOptions
    FaceLandmarker = vision.FaceLandmarker
    FaceLandmarkerOptions = vision.FaceLandmarkerOptions
    VisionRunningMode = vision.RunningMode
    face_options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path="face_landmarker.task"),
        running_mode=VisionRunningMode.IMAGE,
        output_face_blendshapes=True,
        num_faces=1,
    )
    face_landmarker = FaceLandmarker.create_from_options(face_options)
    print("✓ Face Landmarker (스마일) 로드 완료.")

    pose_detector = mp_pose.Pose(
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    )
    rsp_detector = RSPDetector()
    print("✓ RSP Detector (가위바위보) 로드 완료.")
except Exception as e:
    print(f"❌ MediaPipe 모델 로드 실패: {e}")
    exit()


def create_worker_token() -> str:
    print(f"OpenVidu 원본 API에 'SUBSCRIBER' 토큰 요청 중... (URL: {OPENVIDU_URL})")
    auth_string = f"{OPENVIDU_USER}:{OPENVIDU_SECRET}"
    auth_bytes = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {auth_bytes}",
        "Content-Type": "application/json",
    }
    try:
        session_response = requests.post(
            f"{OPENVIDU_URL}/openvidu/api/sessions",
            headers=headers,
            json={"customSessionId": SESSION_ID},
            verify=False,
            timeout=10,
        )
        if session_response.status_code not in [200, 409]:
            print(
                f"❌ 세션 생성/확인 실패: {session_response.status_code} - {session_response.text}"
            )
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ 세션 생성/확인 중 예외 발생: {e}")
        return None
    connection_payload = {
        "role": "SUBSCRIBER",
        "serverData": f'{{"participantId": "{WORKER_PARTICIPANT_ID}"}}',
    }
    connection_url = f"{OPENVIDU_URL}/openvidu/api/sessions/{SESSION_ID}/connection"
    try:
        connection_response = requests.post(
            connection_url,
            headers=headers,
            json=connection_payload,
            verify=False,
            timeout=10,
        )
        if connection_response.status_code != 200:
            print(
                f"❌ 커넥션 생성 실패: {connection_response.status_code} - {connection_response.text}"
            )
            return None
        token_url = connection_response.json()["token"]
        print(f"✓ OpenVidu 원본 API 통해 워커 토큰 확보")
        return token_url
    except requests.exceptions.RequestException as e:
        print(f"❌ 커넥션 생성 중 예외 발생: {e}")
        return None


def start_video_writer(first_frame, fps, idx):
    global current_video_path
    if not os.path.exists(VIDEO_DIR):
        os.makedirs(VIDEO_DIR)
    h, w = first_frame.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{VIDEO_DIR}/smile_{timestamp}_{idx}.mp4"
    current_video_path = path
    writer = cv2.VideoWriter(path, fourcc, fps, (w, h))
    if not writer.isOpened():
        print(
            f"❌ ERROR: VideoWriter initialization failed for FourCC='avc1'. Check FFmpeg installation."
        )
        current_video_path = None
        return None, None

    print(f"Smile Detected! (Idx: {idx}) 녹화 시작... -> {path}")
    return writer, path


async def upload_video_file(file_path):
    if not file_path or not os.path.exists(file_path):
        print(f"Upload Error: 파일 없음 {file_path}")
        return
    if not API_UPLOAD_URL:
        print(f"Upload Error: API_UPLOAD_URL이 .env에 설정되지 않았습니다.")
        try:
            os.remove(file_path)
        except OSError:
            pass
        return

    print(f"파일 업로드 시도: {file_path}")
    try:
        async with httpx.AsyncClient() as client:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, "video/mp4")}
                params = {"directory": "smile_videos"}
                response = await client.post(
                    API_UPLOAD_URL, files=files, params=params, timeout=30.0
                )
            if 200 <= response.status_code < 300:
                print(f"✓ (Upload Success) {file_path}")
            else:
                print(
                    f"❌ (Upload Failed) {file_path} -> {response.status_code} - {response.text}"
                )
    except Exception as e:
        print(f"❌ (Upload Exception) {file_path} -> {e}")
    finally:
        try:
            os.remove(file_path)
        except OSError:
            pass


def execute_rsp_detection():
    global last_frame_for_rsp, pose_detector, rsp_detector

    if last_frame_for_rsp is None:
        return "NoFrame"

    try:
        image_for_pose = cv2.cvtColor(last_frame_for_rsp, cv2.COLOR_BGR2RGB)
        pose_results = pose_detector.process(image_for_pose)
        rsp_status = "Unknown"
        if pose_results.pose_landmarks:
            rsp_status = rsp_detector.classify_pose(pose_results.pose_landmarks)
            print(f"RSP Detector 실행됨: {rsp_status}")
            return rsp_status
        else:
            print("RSP Detector 실행됨: NoLandmarks")
            return "NoLandmarks"

    except Exception as e:
        print(f"RSP Detector 실행 중 오류: {e}")
        return "Error"


async def mqtt_listener_worker(client):
    print(f"✓ MQTT 리스너 시작, 토픽 구독: {MQTT_REQUEST_TOPIC}")

    try:
        await client.subscribe(MQTT_REQUEST_TOPIC)

        async for message in client.messages:
            try:
                topic = message.topic
                print(f"[MQTT] Request received on topic: {topic}")

                if not message.topic.matches(MQTT_REQUEST_TOPIC):
                    continue

                rsp_result = await asyncio.to_thread(execute_rsp_detection)

                response_message = {
                    "response": "RSP_DETECT_RESULT",
                    "result": rsp_result,
                }

                await client.publish(
                    MQTT_RESPONSE_TOPIC, json.dumps(response_message), qos=0
                )
                print(f"[MQTT] Response sent. Result: {rsp_result}")
            except Exception as e:
                print(f"[MQTT] Internal Error: {e}")
    except Exception as e:
        print(f"MQTT 리스너 워커 오류: {e}")


def process_frame_and_manage_buffer(
    frame: VideoFrame, upload_queue: asyncio.Queue, main_loop: asyncio.AbstractEventLoop
):
    global last_smile_trigger_time, is_saving, post_frames_remaining, video_writer, current_video_path, last_frame_for_rsp

    try:
        frame_bgr = frame.to_ndarray(format="bgr24")
        pre_buffer.append(frame_bgr)
        last_frame_for_rsp = frame_bgr
        smile_triggered = False

        if not is_saving:
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            face_result = face_landmarker.detect(mp_image)

            if face_result and face_result.face_blendshapes:
                smile_l_score = 0.0
                smile_r_score = 0.0
                for category in face_result.face_blendshapes[0]:
                    if category.category_name == "mouthSmileLeft":
                        smile_l_score = category.score
                    elif category.category_name == "mouthSmileRight":
                        smile_r_score = category.score

                now = time.time()
                if (
                    smile_l_score > SMILE_THRESHOLD
                    and smile_r_score > SMILE_THRESHOLD
                    and (now - last_smile_trigger_time > COOLDOWN_SECONDS)
                ):
                    smile_triggered = True
                    last_smile_trigger_time = now

        if smile_triggered and not is_saving:
            if len(pre_buffer) > 0:
                video_writer, _ = start_video_writer(
                    pre_buffer[0], FPS, int(last_smile_trigger_time)
                )

                if video_writer is None:
                    return

                for bf in pre_buffer:
                    video_writer.write(bf)
                post_frames_remaining = int(FPS * SAVING_PRE_POST_SECONDS)
                is_saving = True

        if is_saving and video_writer is not None:
            video_writer.write(frame_bgr)
            post_frames_remaining -= 1
            if post_frames_remaining <= 0:
                print(f"녹화 완료: {current_video_path}")
                video_writer.release()
                video_writer = None
                is_saving = False
                if current_video_path:
                    try:
                        asyncio.run_coroutine_threadsafe(
                            upload_queue.put(current_video_path), main_loop
                        )
                        print(f"Upload task submitted to queue: {current_video_path}")
                    except Exception as e:
                        print(f"Failed to submit upload task to queue: {e}")
                current_video_path = None
    except Exception as e:
        print(f"!!! EXCEPTION in process_frame_and_manage_buffer: {e}")
        if video_writer is not None:
            video_writer.release()
        is_saving = False
        video_writer = None


def add_tcp_transport(turn_url: str) -> str:
    url_parts = list(urlparse(turn_url))
    query = parse_qs(url_parts[4])
    query["transport"] = ["tcp"]
    url_parts[4] = urlencode(query, doseq=True)
    return urlunparse(url_parts)


async def upload_worker(queue: asyncio.Queue):
    while True:
        file_path = await queue.get()
        if file_path is None:
            break
        await upload_video_file(file_path)
        queue.task_done()


async def run_worker():
    print("MediaPipe 워커(aiortc) 시작 중...")
    pc = None
    mqtt_task = None
    upload_task = None
    try:
        mqtt_ssl_context = ssl.create_default_context()
        mqtt_ssl_context.check_hostname = False
        mqtt_ssl_context.verify_mode = ssl.CERT_NONE

        async with mqtt.Client(
            hostname=MQTT_BROKER_HOST,
            port=MQTT_BROKER_PORT,
            username=MQTT_USERNAME,
            password=MQTT_SECRET,
            tls_context=mqtt_ssl_context,
        ) as mqtt_client:

            print("✓ MQTT Connected successfully.")

            mqtt_task = asyncio.create_task(mqtt_listener_worker(mqtt_client))

            ws_token_url = create_worker_token()

            if not ws_token_url:
                print("토큰 발급 실패. 30초 후 재시도합니다.")
                await asyncio.sleep(30)
                return

            if "/openvidu" not in ws_token_url:
                ws_url = ws_token_url.replace(f"?", f"/openvidu?")
            else:
                ws_url = ws_token_url

            print(f"\nConnecting to WebSocket: {ws_url}")

            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            BROWSER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"

            async with websockets.connect(
                ws_url,
                ssl=ssl_context,
                ping_interval=20,
                open_timeout=10,
                user_agent_header=BROWSER_USER_AGENT,
            ) as ws:

                print("✓ WebSocket connected!")
                rpc_id = 1
                join_message = {
                    "jsonrpc": "2.0",
                    "method": "joinRoom",
                    "id": rpc_id,
                    "params": {
                        "token": ws_token_url,
                        "session": SESSION_ID,
                        "role": "SUBSCRIBER",
                        "serverData": f'{{"participantId": "{WORKER_PARTICIPANT_ID}"}}',
                        "platform": "Python_aiortc",
                        "metadata": "{}",
                        "secret": "",
                        "recorder": False,
                        "dataChannels": True,
                    },
                }
                rpc_id_join = rpc_id
                rpc_id += 1
                await ws.send(json.dumps(join_message))

                ice_servers = [
                    RTCIceServer(urls=["stun:stun.l.google.com:19302"]),
                    RTCIceServer(urls=["stun:stun1.l.google.com:19302"]),
                ]

                join_data = None
                early_ice_candidates = []
                while join_data is None:
                    response = await ws.recv()
                    data = json.loads(response)
                    if data.get("id") == rpc_id_join:
                        join_data = data
                        print(f"✓ 'joinRoom' 응답 (ID: {rpc_id_join}) 수신.")
                    elif data.get("method") == "iceCandidate":
                        early_ice_candidates.append(data)
                    elif data.get("method"):
                        print(
                            f"[EVENT] Received (while waiting for join): {data.get('method')}"
                        )

                if "error" in join_data:
                    print(f"❌ Join error: {join_data['error']}")
                    return
                if not join_data.get("result") or not join_data["result"].get("id"):
                    print(
                        f"❌ 'joinRoom' 응답에 'result.id' (connectionId)가 없습니다: {join_data}"
                    )
                    return

                worker_connection_id = join_data["result"]["id"]
                print(f"✓ 'joinRoom' 성공. (ConnectionId: {worker_connection_id})")

                result = join_data["result"]
                if "customIceServers" in result and result["customIceServers"]:
                    for turn_server in result["customIceServers"]:
                        turn_url = turn_server.get("url")
                        if not turn_url:
                            continue

                        ice_servers.append(
                            RTCIceServer(
                                urls=[turn_url],
                                username=turn_server.get("username"),
                                credential=turn_server.get("credential"),
                            )
                        )

                configuration = RTCConfiguration(iceServers=ice_servers)

                pc = RTCPeerConnection(configuration=configuration)
                upload_queue = asyncio.Queue()
                main_loop = asyncio.get_event_loop()

                pc.addTransceiver("video", direction="recvonly")

                @pc.on("iceconnectionstatechange")
                async def on_ice_connection_state_change():
                    print(f"ICE connection state: {pc.iceConnectionState}")
                    if pc.iceConnectionState == "failed":
                        print("❌ ICE connection failed!")
                    elif pc.iceConnectionState == "connected":
                        print("✅ ICE connection established! (미디어 수신 시작)")

                @pc.on("icecandidate")
                async def on_ice_candidate(event):
                    if event.candidate:
                        candidate = event.candidate
                        candidate_str = f"candidate:{candidate.foundation} {candidate.component} {candidate.protocol} {candidate.priority} {candidate.ip} {candidate.port} typ {candidate.type}"
                        if candidate.relatedAddress:
                            candidate_str += f" raddr {candidate.relatedAddress} rport {candidate.relatedPort}"
                        candidate_message = {
                            "jsonrpc": "2.0",
                            "method": "onIceCandidate",
                            "params": {
                                "endpointName": worker_connection_id,
                                "candidate": candidate_str,
                                "sdpMid": (
                                    str(candidate.sdpMid) if candidate.sdpMid else "0"
                                ),
                                "sdpMLineIndex": (
                                    candidate.sdpMLineIndex
                                    if candidate.sdpMLineIndex is not None
                                    else 0
                                ),
                            },
                        }
                        print(f"[LOCAL ICE] Sending candidate: {candidate.type}")
                        try:
                            await ws.send(json.dumps(candidate_message))
                        except Exception as e:
                            print(f"[LOCAL ICE] ❌ Failed to send candidate: {e}")

                @pc.on("track")
                async def on_track(track):
                    print(f"✓ Track received (kind: {track.kind})")
                    while True:
                        try:
                            frame = await track.recv()
                            await asyncio.to_thread(
                                process_frame_and_manage_buffer,
                                frame,
                                upload_queue,
                                main_loop,
                            )
                        except Exception as e:
                            print(f"!!! EXCEPTION in on_track: {e}")
                            break

                if early_ice_candidates:
                    print(
                        f"--- Adding {len(early_ice_candidates)} early ICE candidates ---"
                    )
                    for data in early_ice_candidates:
                        try:
                            params = data["params"]
                            candidate_str = params["candidate"].split(":", 1)[1]
                            candidate = candidate_from_sdp(candidate_str)
                            candidate.sdpMid = params.get("sdpMid")
                            candidate.sdpMLineIndex = params.get("sdpMLineIndex")
                            await pc.addIceCandidate(candidate)
                            print(f"Added early ICE candidate: {params['candidate']}")
                        except Exception as e:
                            print(f"Failed to add early ICE candidate: {e}")

                found_stream = False
                for participant in join_data.get("result", {}).get("value", []):
                    if participant.get(
                        "id"
                    ) != worker_connection_id and participant.get("streams"):
                        stream_id = participant["streams"][0]["id"]
                        print(f"✓ 'publisher_robot' 스트림 발견: {stream_id}")
                        found_stream = True

                        subscribe_offer = await pc.createOffer()
                        await pc.setLocalDescription(subscribe_offer)
                        subscribe_message = {
                            "jsonrpc": "2.0",
                            "method": "receiveVideoFrom",
                            "id": rpc_id,
                            "params": {
                                "sender": stream_id,
                                "sdpOffer": pc.localDescription.sdp,
                            },
                        }
                        rpc_id_subscribe = rpc_id
                        rpc_id += 1

                        print(f"... 'receiveVideoFrom' ({stream_id}) 요청 중 ...")
                        await ws.send(json.dumps(subscribe_message))

                        subscribe_response = None
                        while subscribe_response is None:
                            response = await ws.recv()
                            data = json.loads(response)
                            if data.get("id") == rpc_id_subscribe:
                                subscribe_response = data
                                print(
                                    f"✓ 'receiveVideoFrom' 응답 (ID: {rpc_id_subscribe}) 수신."
                                )
                            elif data.get("method") == "iceCandidate":
                                print(
                                    f"[EVENT] (During subscribe) Received iceCandidate"
                                )
                            elif data.get("method"):
                                print(
                                    f"[EVENT] Received (while waiting for subscribe): {data.get('method')}"
                                )

                        if "error" in subscribe_response:
                            print(f"❌ Subscribe error: {subscribe_response['error']}")
                            return

                        answer_sdp = subscribe_response["result"]["sdpAnswer"]
                        answer = RTCSessionDescription(sdp=answer_sdp, type="answer")
                        await pc.setRemoteDescription(answer)
                        print(f"✓ 'receiveVideoFrom' ({stream_id}) 성공.")
                        break

                if not found_stream:
                    print(
                        "⚠️ 'joinRoom' 응답에 'publisher_robot'의 스트림이 없습니다. 대기합니다..."
                    )

                upload_task = asyncio.create_task(upload_worker(upload_queue))

                print("\n" + "=" * 30)
                print("✅ MediaPipe 워커 (스마일 감지) 활성화 완료")
                print("=" * 30)

                try:
                    while True:
                        message = await ws.recv()
                        data = json.loads(message)
                        if data.get("method") == "iceCandidate":
                            try:
                                params = data["params"]
                                candidate_str = params["candidate"].split(":", 1)[1]
                                candidate = candidate_from_sdp(candidate_str)
                                candidate.sdpMid = params.get("sdpMid")
                                candidate.sdpMLineIndex = params.get("sdpMLineIndex")
                                await pc.addIceCandidate(candidate)
                                print(
                                    f"[REMOTE ICE] Added candidate: {params['candidate']}"
                                )
                            except Exception as e:
                                print(
                                    f"[REMOTE ICE] Failed to add remote candidate: {e}"
                                )

                except websockets.exceptions.ConnectionClosed as e:
                    print(f"WebSocket connection closed: {e}")
                except Exception as e:
                    print(f"WebSocket loop error: {e}")

    except mqtt.exceptions.MqttError as e:
        print(f"❌ MQTT connection failed: {e}")
        await asyncio.sleep(30)
    except websockets.exceptions.InvalidStatus as e:
        print(f"❌ WebSocket 연결 실패 (서버 거부): {e}")
    except Exception as e:
        print(f"❌ 치명적인 오류 발생: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if face_landmarker:
            face_landmarker.close()
        if "pose_detector" in globals() and pose_detector:
            pose_detector.close()
        if mqtt_task and not mqtt_task.done():
            mqtt_task.cancel()
        if upload_task and not upload_task.done():
            upload_task.cancel()

        if pc:
            await pc.close()
        print("워커 종료.")


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop_policy().get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_worker())
    except KeyboardInterrupt:
        print("\n⏹️ 중지 요청됨...")
    finally:
        print("리소스 정리 중...")
