"""稳健下载 FLUX.2-klein-4B 到 HF 缓存：超时即抛错、自动重试、断点续传。
HF 的流式下载偶尔挂死不超时，这里用 etag_timeout + 外层重试兜底。

跑之前：
  cp .env.example .env   # 按需填 HF_TOKEN / HF_HOME 等
  # 或: export HF_TOKEN=... HF_HOME=... HF_HUB_DISABLE_XET=1
  python dl.py
"""
import os
import sys
import time

from huggingface_hub import snapshot_download

from envfile import load_env

load_env()

REPO = os.environ.get("BLINKFACE_MODEL", "black-forest-labs/FLUX.2-klein-4B")
# 跳过 diffusers 用不到的：原始单文件 checkpoint + 样例图
IGNORE = ["flux-2-klein-4b.safetensors", "*.jpg"]
for i in range(50):
    try:
        p = snapshot_download(REPO, max_workers=8, etag_timeout=15, ignore_patterns=IGNORE)
        print("DOWNLOAD DONE", p, flush=True)
        break
    except Exception as e:
        print(f"retry {i}: {type(e).__name__}: {e}", flush=True)
        time.sleep(2)
else:
    print("GAVE UP", flush=True)
    sys.exit(1)
