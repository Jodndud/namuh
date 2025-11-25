import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
from picamera2 import Picamera2
import cv2
import numpy as np

HOST = "localhost"
PORT = 8081
WIDTH, HEIGHT = 1920, 1080
JPEG_QUALITY = 80

latest_jpeg = None
jpeg_lock = threading.Lock()


def camera_loop():
    global latest_jpeg
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
        main={"size": (WIDTH, HEIGHT), "format": "BGR888"}
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(0.5)
    try:
        while True:
            arr = picam2.capture_array()  # RGB numpy array
            # convert to BGR and JPEG encode
            # bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            bgr = np.flip(arr, axis=2)
            ret, buf = cv2.imencode(
                ".jpg", bgr, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
            )
            if ret:
                data = buf.tobytes()
                with jpeg_lock:
                    latest_jpeg = data
            time.sleep(0.02)  # ~50 FPS capture loop; adjust as needed
    finally:
        picam2.stop()


class FrameHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/frame.jpg", "/"):
            self.send_error(404)
            return
        with jpeg_lock:
            data = latest_jpeg
        if data is None:
            # no frame yet
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b"No frame yet")
            return
        self.send_response(200)
        self.send_header("Content-type", "image/jpeg")
        self.send_header("Content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        return  # silence logging


def run_server():
    server = HTTPServer((HOST, PORT), FrameHandler)
    print(f"Camera server running at http://{HOST}:{PORT}/frame.jpg")
    server.serve_forever()


if __name__ == "__main__":
    t = threading.Thread(target=camera_loop, daemon=True)
    t.start()
    run_server()
