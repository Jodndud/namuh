import asyncio
import base64
import signal
import subprocess
import cv2
import numpy as np
import os
import time
import urllib.request
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
import dotenv

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

dotenv.load_dotenv()
OPENVIDU_URL = os.getenv("OPENVIDU_URL")
OPENVIDU_SECRET = os.getenv("OPENVIDU_SECRET")
SESSION_ID = os.getenv("SESSION_ID")
WEBSOCKET_PREV_URL = os.getenv("WEBSOCKET_PREV_URL")
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL")
CAMERA_URL = "http://localhost:8081/frame.jpg"

CAMERA_SERVER = os.path.join(os.path.dirname(__file__), "camera_server.py")
SYSTEM_PY = "/usr/bin/python3"
CAMERA_START_TIMEOUT = 5.0


class RaspberryPiVideoTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, frame_provider_func):
        super().__init__()
        self.start_time = time.time()
        self.frame_provider = frame_provider_func

    async def recv(self):
        try:
            frame_data = await asyncio.to_thread(self.frame_provider)

            if frame_data is None:
                # get_frame_from_server媛 None??諛섑솚??寃쎌슦
                print("!!! Frame data is None, returning blank frame...")
                await asyncio.sleep(1 / 30.0)
                return None

            pts = int((time.time() - self.start_time) * 90000)
            frame_data_rgb = cv2.cvtColor(frame_data, cv2.COLOR_BGR2RGB)

            frame = VideoFrame.from_ndarray(frame_data_rgb, format="rgb24")
            frame.pts = pts
            frame.time_base = Fraction(1, 90000)
            return frame

        except Exception as e:
            print(f"!!! EXCEPTION in recv task: {e}")
            import traceback

            traceback.print_exc()
            await asyncio.sleep(1.0)
            return None


def start_camera_server():
    if not os.path.exists(CAMERA_SERVER):
        raise FileNotFoundError("camera_server.py not found")
    if not os.path.exists(SYSTEM_PY):
        raise FileNotFoundError(f"System python not found at {SYSTEM_PY}")

    proc = subprocess.Popen(
        [SYSTEM_PY, CAMERA_SERVER], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    t0 = time.time()
    while time.time() - t0 < CAMERA_START_TIMEOUT:
        try:
            with urllib.request.urlopen(CAMERA_URL, timeout=1) as r:
                if r.status == 200:
                    print("Camera server ready")
                    return proc
        except Exception:
            time.sleep(0.2)

    print("Warning: Camera server may not be ready")
    return proc


def stop_process(proc):
    try:
        proc.send_signal(signal.SIGINT)
        time.sleep(0.2)
        proc.terminate()
        proc.wait(timeout=2)
    except Exception:
        try:
            proc.kill()
        except:
            pass


def get_frame_from_server(url=CAMERA_URL, timeout=2.0):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            data = resp.read()
        arr = np.frombuffer(data, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Frame fetch error: {e}")
        return None


def create_openvidu_token():
    auth_string = f"OPENVIDUAPP:{OPENVIDU_SECRET}"
    auth_bytes = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

    headers = {
        "Authorization": f"Basic {auth_bytes}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
    }

    print(f"Creating session: {SESSION_ID}")
    actual_session_id = SESSION_ID

    try:
        session_response = requests.post(
            f"{OPENVIDU_URL}/openvidu/api/sessions",
            headers=headers,
            json={"customSessionId": SESSION_ID},
            verify=False,
            timeout=10,
        )

        print(f"Session response status: {session_response.status_code}")

        if session_response.status_code == 409:
            print("Session already exists - fetching details")
            get_response = requests.get(
                f"{OPENVIDU_URL}/openvidu/api/sessions/{SESSION_ID}",
                headers=headers,
                verify=False,
                timeout=10,
            )
            if get_response.status_code == 200:
                session_data = get_response.json()
                actual_session_id = session_data.get("sessionId", SESSION_ID)
                print(f"Actual session ID: {actual_session_id}")
            else:
                actual_session_id = SESSION_ID

        elif session_response.status_code == 200:
            print("Session created successfully")
            session_data = session_response.json()
            actual_session_id = session_data.get("sessionId", SESSION_ID)
            print(f"Actual session ID: {actual_session_id}")
        else:
            print(f"Session response: {session_response.status_code}")
            print(f"Response body: {session_response.text}")
            session_response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Failed to create session: {e}")
        print(f"Continuing with session ID: {SESSION_ID}")
        actual_session_id = SESSION_ID

    print(f"Creating connection for session: {actual_session_id}")
    try:
        connection_payload = {
            "type": "WEBRTC",
            "data": None,
            "record": None,
            "role": "PUBLISHER",
            "serverData": '{"participantId": "publisher_robot"}',
            "kurentoOptions": None,
            "rtspUri": None,
            "adaptativeBitrate": None,
            "onlyPlayWithSubscribers": None,
            "networkCache": None,
            "customIceServers": None,
            "sessionId": actual_session_id,
        }

        connection_url = (
            f"{OPENVIDU_URL}/openvidu/api/sessions/{actual_session_id}/connection"
        )

        connection_response = requests.post(
            connection_url,
            headers=headers,
            json=connection_payload,
            verify=False,
            timeout=10,
        )

        print(f"Connection response status: {connection_response.status_code}")

        if connection_response.status_code != 200:
            print(f"Connection error: {connection_response.text}")
            connection_response.raise_for_status()

        connection_data = connection_response.json()

        # Print full connection data to debug
        print(f"Connection data: {json.dumps(connection_data, indent=2)}")

        token_url = connection_data["token"]
        session_id_from_connection = connection_data.get("sessionId", actual_session_id)

        print(f"Token created successfully")
        print(f"Connection ID: {connection_data.get('connectionId', 'N/A')}")
        print(f"Session ID from connection: {session_id_from_connection}")
        print(f"Token URL: {token_url}")

        return (
            token_url,
            connection_data.get("connectionId"),
            session_id_from_connection,
        )

    except requests.exceptions.RequestException as e:
        print(f"Failed to create connection: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        raise
    except json.JSONDecodeError as e:
        print(f"Failed to parse connection response: {e}")
        print(f"Response text: {connection_response.text}")
        raise


async def publish_to_openvidu(frame_provider):

    try:
        ws_token_url, connection_id, actual_session_id = create_openvidu_token()
    except Exception as e:
        print(f"Failed to get token: {e}")
        return

    # The WebSocket URL already contains the token
    if f"{WEBSOCKET_URL}" not in ws_token_url:
        ws_url = ws_token_url.replace(f"{WEBSOCKET_PREV_URL}?", f"{WEBSOCKET_URL}?")
    else:
        ws_url = ws_token_url

    print(f"\nConnecting to WebSocket: {ws_url}")

    pc = None
    ice_complete = asyncio.Event()

    try:
        # SSL context for WebSocket
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        async with websockets.connect(
            ws_url, ssl=ssl_context, ping_interval=20, open_timeout=10
        ) as ws:
            print("??WebSocket connected!")

            join_message = {
                "jsonrpc": "2.0",
                "method": "joinRoom",
                "params": {
                    "token": ws_token_url,
                    "session": actual_session_id,
                    "role": "PUBLISHER",
                    "serverData": '{"participantId": "publisher_robot"}',
                    "platform": "Python",
                    "metadata": "{}",
                    "secret": "",
                    "recorder": False,
                    "dataChannels": False,
                },
                "id": 1,
            }

            print(f"\nStep 1: Joining room...")
            print(f"Session: {actual_session_id}")
            await ws.send(json.dumps(join_message))

            join_data = None
            while join_data is None:
                response = await ws.recv()
                data = json.loads(response)

                if data.get("id") == 1:
                    join_data = data
                    print(f"Join response received")
                elif data.get("method"):
                    print(
                        f"[EVENT] Received (while waiting for join): {data.get('method')}"
                    )
                else:
                    print(
                        f"[WARN] Received unexpected message (while waiting for join): {response[:100]}"
                    )

            if "error" in join_data:
                print(f"??Join error: {join_data['error']}")
                return

            if "result" in join_data:
                # 1. Build ICE servers list from join response
                ice_servers = [
                    RTCIceServer(urls=["stun:stun.l.google.com:19302"]),
                    RTCIceServer(urls=["stun:stun1.l.google.com:19302"]),
                ]

                result = join_data["result"]
                if "customIceServers" in result and result["customIceServers"]:
                    for turn_server in result["customIceServers"]:
                        print(f"??Using TURN server: {turn_server.get('url', 'N/A')}")
                        ice_servers.append(
                            RTCIceServer(
                                urls=[turn_server["url"]],
                                username=turn_server.get("username"),
                                credential=turn_server.get("credential"),
                            )
                        )
                else:
                    print("\n?좑툘  No custom TURN servers provided by OpenVidu")
                    print("Ensure TURN is configured in OpenVidu .env if behind NAT")

                configuration = RTCConfiguration(iceServers=ice_servers)
                pc = RTCPeerConnection(configuration=configuration)

                @pc.on("icegatheringstatechange")
                async def on_ice_gathering_state_change():
                    print(f"ICE gathering state: {pc.iceGatheringState}")
                    if pc.iceGatheringState == "complete":
                        ice_complete.set()

                @pc.on("iceconnectionstatechange")
                async def on_ice_connection_state_change():
                    print(f"ICE connection state: {pc.iceConnectionState}")
                    if pc.iceConnectionState == "failed":
                        print("??ICE connection failed!")
                    elif pc.iceConnectionState == "connected":
                        print("??ICE connection established!")
                    elif pc.iceConnectionState == "checking":
                        print("??ICE checking candidates...")

                @pc.on("icecandidate")
                async def on_ice_candidate(event):
                    if event.candidate:
                        candidate = event.candidate
                        print(
                            f"[LOCAL ICE] New candidate: type={candidate.type}, ip={candidate.ip}, port={candidate.port}"
                        )

                        candidate_str = f"candidate:{candidate.foundation} {candidate.component} {candidate.protocol} {candidate.priority} {candidate.ip} {candidate.port} typ {candidate.type}"
                        if candidate.relatedAddress:
                            candidate_str += f" raddr {candidate.relatedAddress} rport {candidate.relatedPort}"

                        candidate_message = {
                            "jsonrpc": "2.0",
                            "method": "onIceCandidate",
                            "params": {
                                "endpointName": connection_id,
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
                            "id": 3,
                        }

                        try:
                            await ws.send(json.dumps(candidate_message))
                            print(f"[LOCAL ICE] ??Candidate sent to server")
                        except Exception as e:
                            print(f"[LOCAL ICE] ??Failed to send candidate: {e}")

                # 4. Add video track
                video_track = RaspberryPiVideoTrack(frame_provider)
                pc.addTrack(video_track)

            else:
                print(
                    f"??Unexpected join response structure: {json.dumps(join_data, indent=2)}"
                )
                return

            print("??Successfully joined room")

            print(f"\nStep 2: Creating WebRTC offer...")
            offer = await pc.createOffer()
            await pc.setLocalDescription(offer)

            print("Waiting for ICE gathering...")
            try:
                await asyncio.wait_for(ice_complete.wait(), timeout=10.0)
                print("??ICE gathering complete")
            except asyncio.TimeoutError:
                print("??ICE gathering timeout after 10s, continuing anyway...")

            publish_message = {
                "jsonrpc": "2.0",
                "method": "publishVideo",
                "params": {
                    "sdpOffer": pc.localDescription.sdp,
                    "doLoopback": False,
                    "hasAudio": False,
                    "hasVideo": True,
                    "audioActive": False,
                    "videoActive": True,
                    "typeOfVideo": "CAMERA",
                    "frameRate": 30,
                    "videoDimensions": '{"width":1920,"height":1080}',
                },
                "id": 2,
            }

            print("\nStep 3: Publishing video...")
            await ws.send(json.dumps(publish_message))
            print("Publish request sent, waiting for SDP answer...")

            publish_data = None
            while publish_data is None:
                response = await ws.recv()
                data = json.loads(response)

                if data.get("id") == 2:
                    publish_data = data
                elif data.get("method"):
                    print(
                        f"[EVENT] Received (while waiting for publish): {data.get('method')}"
                    )
                else:
                    print(
                        f"[WARN] Received unexpected message (while waiting for publish): {response[:100]}"
                    )

            if "error" in publish_data:
                print(f"??Publish error: {publish_data['error']}")
                await pc.close()
                return

            if "result" in publish_data and "sdpAnswer" in publish_data["result"]:
                answer_sdp = publish_data["result"]["sdpAnswer"]
                answer = RTCSessionDescription(sdp=answer_sdp, type="answer")
                await pc.setRemoteDescription(answer)
                print("??SDP answer received and set")
                print("\n" + "=" * 50)
                print("?렏 STREAMING STARTED - Waiting for ICE connection...")
                print("=" * 50)
                print("Press Ctrl+C to stop\n")
            else:
                print(f"??Unexpected response: {json.dumps(publish_data, indent=2)}")
                await pc.close()
                return

            try:
                ice_count = 0
                ice_connected = False
                while True:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        data = json.loads(message)

                        if "method" in data:
                            method = data["method"]

                            if method == "iceCandidate":
                                ice_count += 1
                                if ice_count <= 5 or ice_count % 10 == 0:
                                    print(
                                        f"[REMOTE ICE] Received candidate #{ice_count}"
                                    )

                                try:
                                    if "params" in data:
                                        candidate_data = data["params"]
                                        if "candidate" in candidate_data:
                                            candidate_str = candidate_data["candidate"]
                                            sdp_mid = candidate_data.get("sdpMid")
                                            sdp_mline_index = candidate_data.get(
                                                "sdpMLineIndex"
                                            )

                                            ice_candidate = candidate_from_sdp(
                                                candidate_str.split(":", 1)[1]
                                            )
                                            ice_candidate.sdpMid = sdp_mid
                                            ice_candidate.sdpMLineIndex = (
                                                sdp_mline_index
                                            )

                                            await pc.addIceCandidate(ice_candidate)
                                            if ice_count <= 5:
                                                print(
                                                    f"[REMOTE ICE] ??Added to peer connection"
                                                )
                                except Exception as e:
                                    if ice_count <= 5:
                                        print(f"[REMOTE ICE] ??Failed to add: {e}")

                            else:
                                print(f"[EVENT] {method}")
                    except asyncio.TimeoutError:
                        if pc.iceConnectionState == "connected" and not ice_connected:
                            ice_connected = True
                            print("\n" + "=" * 50)
                            print("??ICE CONNECTION ESTABLISHED - STREAMING ACTIVE!")
                            print("=" * 50 + "\n")
                        elif pc.iceConnectionState in ["disconnected", "failed"]:
                            print(f"?좑툘  ICE state: {pc.iceConnectionState}")
                            break
                        pass
                    except json.JSONDecodeError:
                        print("??Received non-JSON message")

                    await asyncio.sleep(0.1)

            except KeyboardInterrupt:
                print("\n\n?뱄툘  Stopping stream...")

    except websockets.exceptions.InvalidStatus as e:
        print(f"??WebSocket connection failed: {e}")
    except Exception as e:
        print(f"??Error: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("Closing peer connection...")
        if pc:
            await pc.close()


def main_openvidu():
    print("=" * 50)
    print("OpenVidu Video Publisher")
    print("=" * 50)

    print("\nStarting camera server...")
    proc = start_camera_server()

    try:
        asyncio.run(publish_to_openvidu(get_frame_from_server))
    except KeyboardInterrupt:
        print("\n\nShutdown requested by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("\nStopping camera server...")
        stop_process(proc)
        print("Cleanup complete")


if __name__ == "__main__":
    main_openvidu()
