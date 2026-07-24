# blinkface

**Changing your face in the blink of an eye with AI.**

[中文文档](./README-zh.md)

Gesture viewfinder + real-time AI restyle. One CUDA GPU runs a [FLUX.2 [klein] 4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B) image API; Mac / browser act as the remote: text-to-image, image-to-image, and a two-hand frame for live styled preview.

## Preview

Frame your face with both hands → the region restyles live (anime, Ghibli, cyberpunk, …). Close the frame to jump to the next style.

▶️ **[Demo video (X / Twitter)](https://x.com/Lumosous/status/2080430080371941882)**

## Credits

- **Idea**: [this LinkedIn post](https://www.linkedin.com/feed/update/urn:li:activity:7476225577184669696/) — gesture framing + local model restyle inspired this project.
- **Model**: [Black Forest Labs FLUX.2 [klein] 4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B)
- **Hands**: [MediaPipe Hand Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker)

## Components

- **GPU**: `server.py` (FastAPI + diffusers)
- **CLI**: `gen.py` (stdlib only)
- **Web**: `web/` + `web-serve.py` (static page + same-origin proxy)
- **Network**: Tailscale / LAN / SSH tunnel — **no private addresses in the repo**

> **License**  
> Code: [MIT](./LICENSE)  
> Default model [FLUX.2 [klein] 4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B): **Apache-2.0** (commercial use OK)  
> If you set `BLINKFACE_MODEL` to another weight, that **model card’s** license applies (some FLUX variants are Non-Commercial).  
> Follow Black Forest Labs / the model card [Acceptable Use](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B) policy.

> **Usage boundary**  
> Only process **your own** image or people who **explicitly consented**. Do not use for unauthorized face-swap, impersonation, or anything illegal. Style names (Ghibli, Pixar, …) are descriptive prompt words only — no affiliation with rightsholders.

---

## Requirements

| Role | Needs |
|------|--------|
| GPU server | Python **≥ 3.10**, CUDA GPU, **≥ 16GB VRAM** recommended |
| Client | Python ≥ 3.10, no third-party deps |
| Frontend | Modern browser; camera needs **HTTPS** or localhost |

---

## Config

```bash
cp .env.example .env
```

| Variable | Used by | Meaning |
|----------|---------|---------|
| `BLINKFACE_HOST` | `gen.py` / `web-serve.py` / `restart.sh` | API base URL |
| `BLINKFACE_BIND` / `BLINKFACE_PORT` | `server.py` | default `127.0.0.1:8000` |
| `BLINKFACE_TOKEN` | all three | optional shared secret |
| `BLINKFACE_SSH_*` / `BLINKFACE_REMOTE_*` | `restart.sh` | remote restart (optional) |
| `HF_TOKEN` / `HF_HOME` | `dl.py` / first model pull | Hugging Face |

Existing environment variables win over `.env`. `.env` is gitignored.

---

## 1. GPU server

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install torch --index-url https://download.pytorch.org/whl/cu124   # match your CUDA
pip install -r requirements-server.txt
# if your pip diffusers build lacks FLUX.2-klein:
pip install git+https://github.com/huggingface/diffusers.git

# optional pre-download
python dl.py

python server.py
# ready. then:
curl http://127.0.0.1:8000/
```

On Windows, only open the port you need (e.g. 8000) in the firewall — no need to disable it.

For cross-device access:

```bash
# .env
BLINKFACE_BIND=0.0.0.0
BLINKFACE_TOKEN=replace-with-a-long-random-string
```

### Security

- **Do not** DNAT / expose the GPU port to the public internet.
- Default bind is localhost; without `BLINKFACE_TOKEN`, do not set `BLINKFACE_BIND=0.0.0.0` on untrusted networks.
- `web-serve.py` injects the token upstream: `BLINKFACE_WEB_BIND=0.0.0.0` exposes an unauthenticated generate entry to anyone who can reach that port.
- Details: [SECURITY.md](./SECURITY.md).

---

## 2. CLI

```bash
cp .env.example .env
# BLINKFACE_HOST=http://<gpu-reachable-host>:8000
# BLINKFACE_TOKEN=…   # if the server requires it

curl "$BLINKFACE_HOST/" 

python3 gen.py "a cat holding a sign that says hello world" cat.jpg
python3 gen.py "Transform this person into a Japanese anime character..." out.jpg --img face.jpg
```

More style prompts: [prompts.md](./prompts.md).

---

## 3. Web viewfinder

```bash
python3 web-serve.py        # default 127.0.0.1:8080, proxies to BLINKFACE_HOST
open http://127.0.0.1:8080
```

- Browser only hits same-origin `/generate` and `/health`; the proxy injects the token (browser never holds the secret).
- Remote camera: put an HTTPS reverse proxy in front (e.g. `tailscale serve --bg 8080`).
- To let others on the LAN open the page: `BLINKFACE_WEB_BIND=0.0.0.0 python3 web-serve.py` (see Security — this exposes the free generate entry).
- Frontend loads scripts/models from jsDelivr / Google Fonts / MediaPipe CDN by default; fully offline needs your own mirrors.

---

## Speed (4090 + klein 4B)

- 1024px / 4 steps ≈ ~1s  
- Web defaults to `672×384`, 2 steps — tuned for live preview  

---

## Layout

| Path | Role |
|------|------|
| `server.py` | GPU image API |
| `gen.py` | CLI |
| `web-serve.py` + `web/` | frontend + same-origin proxy |
| `dl.py` | resilient model download |
| `restart.sh` | optional: SSH-restart service on a **remote Windows GPU host** (PowerShell) |
| `prompts.md` | style prompts |
| `envfile.py` | `.env` loader |
| `.env.example` | config template |
| `SECURITY.md` | security notes |
| `README-zh.md` | Chinese docs |

---

## License

- Code: [MIT](./LICENSE)
- Default model weights ([FLUX.2 [klein] 4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B)): **Apache-2.0**
- Other models via `BLINKFACE_MODEL`: see that model’s card (separate from this repo’s code license)
