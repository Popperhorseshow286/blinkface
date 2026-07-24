#!/usr/bin/env python3
"""blinkface CLI 遥控器。纯标准库。
文生图:   python3 gen.py "提示词" [输出.jpg]
风格转换: python3 gen.py "编辑指令" 输出.jpg --img 输入.jpg
（风格转换的 prompt 怎么写见 prompts.md）

后端：BLINKFACE_HOST（可写在 .env），默认 http://127.0.0.1:8000
鉴权：若设了 BLINKFACE_TOKEN，自动带 Authorization: Bearer …
"""
from __future__ import annotations

import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

from envfile import load_env

load_env()
HOST = os.environ.get("BLINKFACE_HOST", "http://127.0.0.1:8000").rstrip("/")
TOKEN = os.environ.get("BLINKFACE_TOKEN", "").strip()

args = sys.argv[1:]
img_path = None
if "--img" in args:
    i = args.index("--img")
    if i + 1 >= len(args):
        sys.exit("error: --img requires a file path")
    img_path = args[i + 1]
    del args[i:i + 2]

if not args:
    sys.exit('usage: gen.py "prompt" [out.jpg] [--img in.jpg]')

prompt = args[0]
out = args[1] if len(args) > 1 else "out.jpg"

payload: dict = {"prompt": prompt}
if img_path:
    try:
        payload["image"] = base64.b64encode(open(img_path, "rb").read()).decode()
    except OSError as e:
        sys.exit(f"error: cannot read --img {img_path}: {e}")

headers = {"Content-Type": "application/json"}
if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"

body = json.dumps(payload).encode()
req = urllib.request.Request(HOST + "/generate", body, headers)
t = time.time()
try:
    with urllib.request.urlopen(req, timeout=120) as r:
        open(out, "wb").write(r.read())
        print(f"saved {out}  (生成 {r.headers.get('X-Gen-Seconds', '?')}s, 含传输共 {time.time() - t:.2f}s)")
except urllib.error.HTTPError as e:
    detail = e.read().decode("utf-8", "replace")[:300]
    sys.exit(f"error: HTTP {e.code} from {HOST}: {detail}")
except urllib.error.URLError as e:
    sys.exit(f"error: cannot reach {HOST}: {e.reason}\n"
             f"hint: set BLINKFACE_HOST in .env and ensure server.py is running")
