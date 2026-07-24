#!/usr/bin/env python3
# blinkface 前端: python3 web-serve.py [端口，默认 8080]
# 静态托管 web/ + 同源转发 /generate /health 到 GPU 后端。
# 本机: http://localhost:8080
# 摄像头远程访问需要 HTTPS（例如 tailscale serve --bg 8080）。
# 后端：BLINKFACE_HOST；若设了 BLINKFACE_TOKEN 会由本代理注入，浏览器无需知道密钥。
import os
import sys
import urllib.error
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from envfile import load_env

load_env()
UPSTREAM = os.environ.get("BLINKFACE_HOST", "http://127.0.0.1:8000").rstrip("/")
TOKEN = os.environ.get("BLINKFACE_TOKEN", "").strip()
WEB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
BIND = os.environ.get("BLINKFACE_WEB_BIND", "127.0.0.1")


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?", 1)[0] == "/health":
            self.proxy("GET", "/", timeout=2)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.split("?", 1)[0] == "/generate":
            self.proxy("POST", "/generate", timeout=180)
        else:
            self.send_error(404)

    def proxy(self, method, path, timeout):
        try:
            n = int(self.headers.get("Content-Length") or 0)
            if n > 25 * 1024 * 1024:
                self.send_error(413, "body too large")
                return
            body = self.rfile.read(n) if n else None
            headers = {"Content-Type": self.headers.get("Content-Type", "application/json")}
            if TOKEN:
                headers["Authorization"] = f"Bearer {TOKEN}"
            req = urllib.request.Request(
                UPSTREAM + path, data=body, method=method, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
                self.send_response(r.status)
                for k in ("Content-Type", "X-Gen-Seconds"):
                    if r.headers.get(k):
                        self.send_header(k, r.headers[k])
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            detail = e.read()[:300]
            self.send_error(e.code, detail.decode("utf-8", "replace"))
        except Exception as e:
            self.send_error(502, f"upstream: {e}")

    def log_message(self, *a):
        pass


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
print(f"http://{BIND if BIND != '0.0.0.0' else 'localhost'}:{port}  (web/ → {UPSTREAM})"
      f"{'  auth=on' if TOKEN else ''}")
ThreadingHTTPServer((BIND, port), partial(Handler, directory=WEB)).serve_forever()
