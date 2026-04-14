"""
Boilerplate: camera capture, MJPEG HTTP server, FPS display.

Usage:
    import stream
    stream.run(process_fn)

process_fn(frame, prev_frame) -> output
    - np.ndarray: displayed as-is
    - dict: tiled into grid (keys become labels), each tile = frame size
    - (dict, scale): scale is a float multiplier for tile size (e.g., 0.5, 2)
    - (dict, (w, h)): explicit size per tile
"""

import io
import math
import socket
import socketserver
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import cv2
import numpy as np
from picamera2 import Picamera2
from PIL import Image

PORT = 8080
WIDTH, HEIGHT = 640, 480

_lock = threading.Lock()
_state = {"jpeg": b"", "fps": 0}


def _encode_jpeg(arr):
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="JPEG", quality=75)
    return buf.getvalue()


def _to_rgb(img):
    if len(img.shape) == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    return img


def _tile(images, tile_w, tile_h):
    """Tile a dict of images into a grid."""
    items = list(images.items())
    n = len(items)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    grid = np.zeros((rows * tile_h, cols * tile_w, 3), dtype=np.uint8)

    for i, (label, img) in enumerate(items):
        r, c = divmod(i, cols)
        resized = cv2.resize(_to_rgb(img), (tile_w, tile_h))
        cv2.putText(resized, label, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        grid[r * tile_h:(r + 1) * tile_h, c * tile_w:(c + 1) * tile_w] = resized

    return grid


def _camera_loop(process_fn):
    cam = Picamera2()
    cam.configure(cam.create_preview_configuration(
        main={"size": (WIDTH, HEIGHT), "format": "RGB888"}
    ))
    cam.start()

    prev = None
    frame_times = []

    while True:
        frame = cam.capture_array()

        out = process_fn(frame, prev) if prev is not None else np.zeros_like(frame)

        if isinstance(out, tuple):
            images, size = out
            if isinstance(size, (int, float)):
                tile_w, tile_h = int(WIDTH * size), int(HEIGHT * size)
            else:
                tile_w, tile_h = size
            result = _tile(images, tile_w, tile_h)
        elif isinstance(out, dict):
            result = _tile(out, WIDTH, HEIGHT)
        else:
            result = out

        now = time.monotonic()
        frame_times.append(now)
        frame_times[:] = [t for t in frame_times if now - t < 1.0]

        with _lock:
            _state["jpeg"] = _encode_jpeg(result)
            _state["fps"] = len(frame_times)

        prev = frame


_PAGE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"><title>Live Vision</title>
  <style>
    body {{ background:#111; color:#eee; font-family:monospace;
            display:flex; flex-direction:column; align-items:center; padding:16px; margin:0 }}
    img  {{ max-width:100%; border:1px solid #444 }}
    #info {{ margin-top:6px; color:#666; font-size:13px }}
  </style>
</head>
<body>
  <img src="/stream">
  <div id="info"></div>
  <script>
    setInterval(async () => {{
      const j = await (await fetch('/fps')).json();
      document.getElementById('info').textContent = j.fps + ' fps';
    }}, 1000);
  </script>
</body></html>"""


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self._send(200, "text/html", _PAGE.encode())

        elif self.path == "/stream":
            self.send_response(200)
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
            self.end_headers()
            try:
                while True:
                    with _lock:
                        jpeg = _state["jpeg"]
                    if jpeg:
                        self.wfile.write(b"--frame\r\nContent-Type: image/jpeg\r\n\r\n")
                        self.wfile.write(jpeg)
                        self.wfile.write(b"\r\n")
                    time.sleep(0.033)
            except (BrokenPipeError, ConnectionResetError):
                pass

        elif self.path == "/fps":
            with _lock:
                fps = _state["fps"]
            self._send(200, "application/json", f'{{"fps":{fps}}}'.encode())

        else:
            self.send_error(404)

    def _send(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


class _Server(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True


def run(process_fn, port=PORT):
    threading.Thread(target=_camera_loop, args=(process_fn,), daemon=True).start()
    print(f"http://{socket.gethostname()}.local:{port}")
    _Server(("0.0.0.0", port), _Handler).serve_forever()
