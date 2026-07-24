"""GPU 端：FLUX.2 [klein] 4B 生图 API（blinkface）。
- 文生图：只给 prompt
- 图生图 / 风格转换：给 prompt + 输入图（base64），prompt 是"编辑指令"
运行：python server.py

监听：BLINKFACE_BIND / BLINKFACE_PORT（可写在 .env），默认 127.0.0.1:8000
可选鉴权：BLINKFACE_TOKEN
"""
from __future__ import annotations

import base64
import binascii
import io
import os
import secrets
import threading
import time

import torch
from diffusers import Flux2KleinPipeline
from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field

from envfile import load_env

load_env()

MODEL = os.environ.get("BLINKFACE_MODEL", "black-forest-labs/FLUX.2-klein-4B")
BIND = os.environ.get("BLINKFACE_BIND", "127.0.0.1")
PORT = int(os.environ.get("BLINKFACE_PORT", "8000"))
TOKEN = os.environ.get("BLINKFACE_TOKEN", "").strip()
MAX_SIDE = int(os.environ.get("BLINKFACE_MAX_SIDE", "1280"))
MAX_STEPS = int(os.environ.get("BLINKFACE_MAX_STEPS", "28"))
MAX_EMB = int(os.environ.get("BLINKFACE_MAX_EMB", "64"))
# 输入图像上限（base64 字符数 / 解码后字节），防直连打满内存
MAX_IMAGE_BYTES = int(os.environ.get("BLINKFACE_MAX_IMAGE_BYTES", str(20 * 1024 * 1024)))
MAX_IMAGE_B64 = int(os.environ.get("BLINKFACE_MAX_IMAGE_B64", str(28 * 1024 * 1024)))

# 底层开关：cuDNN 自动选最快卷积核(VAE)、允许 TF32、启用 flash attention
torch.backends.cudnn.benchmark = True
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
torch.backends.cuda.enable_flash_sdp(True)

print(f"loading {MODEL} ...")
# 13GB bf16 全量塞进 4090 显存，不用 cpu_offload。爆显存就换成 .enable_model_cpu_offload()
pipe = Flux2KleinPipeline.from_pretrained(MODEL, torch_dtype=torch.bfloat16).to("cuda")
lock = threading.Lock()  # 单卡推理非线程安全，串行即可

SEQ = 128       # 提示词很短，默认 512 token 太浪费 → 砍到 128 加速每步注意力
EMB: dict = {}  # prompt -> 缓存编码，跳过每次重跑文本编码器（固定开销的大头）


def _token_ok(value: str | None) -> bool:
    if not value:
        return False
    # compare_digest 要求同类型；长度不同直接拒，避免抛错
    try:
        return secrets.compare_digest(value, TOKEN)
    except (TypeError, ValueError):
        return False


def _authorized(authorization: str | None, x_token: str | None) -> bool:
    if not TOKEN:
        return True
    if _token_ok(x_token):
        return True
    if authorization:
        scheme, _, value = authorization.partition(" ")
        if scheme.lower() == "bearer" and _token_ok(value.strip()):
            return True
    return False


def _clamp_side(v: int | None, default: int) -> int:
    n = default if v is None else int(v)
    n = max(16, min(n, MAX_SIDE))
    return (n // 16) * 16


def _clamp_steps(v: int | None) -> int:
    n = 4 if v is None else int(v)
    return max(1, min(n, MAX_STEPS))


@torch.no_grad()
def embed(prompt: str):
    if prompt not in EMB:
        if len(EMB) >= MAX_EMB:
            EMB.pop(next(iter(EMB)))  # 简单 FIFO，防止缓存无限涨
        e = pipe.encode_prompt(prompt, device="cuda", max_sequence_length=SEQ)
        if isinstance(e, tuple):
            e = e[0]
        EMB[prompt] = e.detach().clone()  # detach+clone: 切断计算图、独立持有
    return EMB[prompt]


def _fit(img, cap=1024):
    """输入图按长边缩到 cap、对齐 16 的倍数，作为输出尺寸。"""
    w, h = img.size
    s = min(cap / max(w, h), 1.0)
    return max(16, round(w * s / 16) * 16), max(16, round(h * s / 16) * 16)


def _load_image(img_b64: str) -> Image.Image:
    if len(img_b64) > MAX_IMAGE_B64:
        raise HTTPException(status_code=413, detail="image too large")
    try:
        raw = base64.b64decode(img_b64, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(status_code=400, detail="invalid image encoding")
    if len(raw) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="image too large")
    try:
        return Image.open(io.BytesIO(raw)).convert("RGB")
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="invalid image")


def render(prompt, img_b64, width, height, steps, seed):
    img = None
    steps = _clamp_steps(steps)
    if img_b64:                                    # 给了图 = 图生图/风格转换
        img = _load_image(img_b64)
        if not width or not height:                # 没指定尺寸就跟输入图比例走
            width, height = _fit(img, cap=min(1024, MAX_SIDE))
    width = _clamp_side(width, 1024)
    height = _clamp_side(height, 1024)
    g = torch.Generator("cuda").manual_seed(seed) if seed is not None else None
    out = pipe(prompt_embeds=embed(prompt), image=img,
               width=width, height=height,
               guidance_scale=1.0, num_inference_steps=steps, generator=g).images[0]
    buf = io.BytesIO()
    out.save(buf, "JPEG", quality=95)
    return buf.getvalue()


print("warmup ...")
render("warmup", None, 1024, 1024, 4, 0)
print("ready.")

app = FastAPI(title="blinkface", docs_url=None, redoc_url=None)
# 默认只在本机；跨设备时改 BLINKFACE_BIND 并务必设 BLINKFACE_TOKEN。
# CORS * 方便浏览器调试；有 token 时仍要带请求头。
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"], expose_headers=["X-Gen-Seconds"])


class Req(BaseModel):
    prompt: str = Field(..., max_length=2000)
    image: str | None = Field(None, max_length=MAX_IMAGE_B64)  # base64 输入图
    width: int | None = Field(None, ge=16, le=4096)
    height: int | None = Field(None, ge=16, le=4096)
    steps: int = Field(4, ge=1, le=64)
    seed: int | None = None


@app.get("/")
def health():
    return {"ok": True, "model": MODEL, "auth": bool(TOKEN), "name": "blinkface"}


@app.post("/generate")
def generate(
    r: Req,
    authorization: str | None = Header(default=None),
    x_blinkface_token: str | None = Header(default=None, alias="X-Blinkface-Token"),
):
    if not _authorized(authorization, x_blinkface_token):
        raise HTTPException(status_code=401, detail="unauthorized")
    t = time.time()
    with lock:
        data = render(r.prompt, r.image, r.width, r.height, r.steps, r.seed)
    return Response(content=data, media_type="image/jpeg",
                    headers={"X-Gen-Seconds": f"{time.time() - t:.2f}"})


if __name__ == "__main__":
    import uvicorn
    print(f"bind {BIND}:{PORT}  auth={'on' if TOKEN else 'off'}")
    uvicorn.run(app, host=BIND, port=PORT)
