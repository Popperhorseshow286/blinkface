# blinkface

**一眨眼，换张脸。**  
*Changing your face in the blink of an eye with AI.*

[English](./README.md)

手势取景框 + 实时 AI 风格化。一台 CUDA GPU 跑 [FLUX.2 [klein] 4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B) 生图 API，Mac / 浏览器当遥控器：文生图、图生图，双手围框即可即时预览风格化后的自己。

## 效果预览

[![blinkface 演示：双手围框，框内动漫风格化](./docs/preview-anime.jpg)](https://x.com/Lumosous/status/2080430080371941882)

双手比出取景框 → 框内实时变成动漫 / 吉卜力 / 赛博朋克等风格；收起双手切换下一个风格。

▶️ **[视频演示（X / Twitter）](https://x.com/Lumosous/status/2080430080371941882)**

## 灵感与致谢

- **灵感来源**：[LinkedIn 上的相关分享](https://www.linkedin.com/feed/update/urn:li:activity:7476225577184669696/)——手势取景 + 本地大模型实时改风格的玩法启发了本项目。
- **模型**：[Black Forest Labs FLUX.2 [klein] 4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B)
- **手部追踪**：[MediaPipe Hand Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker)

## 组成

- **GPU 端**：`server.py`（FastAPI + diffusers）
- **命令行**：`gen.py`（纯标准库，无第三方依赖）
- **网页**：`web/` + `web-serve.py`（静态页 + 同源反代）
- **组网**：Tailscale / 局域网 / SSH 隧道均可；**仓库不含私人地址**

> **许可**  
> 代码：[MIT](./LICENSE)  
> 默认模型 [FLUX.2 [klein] 4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B)：**Apache-2.0**（可商用）  
> 若设置 `BLINKFACE_MODEL` 指向其它权重，以**该模型卡**许可为准（例如部分 FLUX 变体为 Non-Commercial）。  
> 使用模型时请同时遵守 Black Forest Labs / 模型卡的 [Acceptable Use](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B) 政策。

> **使用边界**  
> 仅限处理**你自己**或**已明确同意**的人的影像。不要用于未授权换脸、冒充或任何违法用途。风格名称（吉卜力、皮克斯等）仅为描述性提示词，与各权利方无关。

---

## 要求

| 端 | 要求 |
|----|------|
| GPU 服务 | Python **≥ 3.10**，CUDA GPU，建议 **≥ 16GB 显存** |
| 客户端 | Python ≥ 3.10，无第三方依赖 |
| 前端 | 现代浏览器；摄像头需 **HTTPS** 或 localhost |

---

## 配置

```bash
cp .env.example .env
```

| 变量 | 谁用 | 含义 |
|------|------|------|
| `BLINKFACE_HOST` | `gen.py` / `web-serve.py` / `restart.sh` | API 根 URL |
| `BLINKFACE_BIND` / `BLINKFACE_PORT` | `server.py` | 默认 `127.0.0.1:8000` |
| `BLINKFACE_TOKEN` | 三端 | 可选共享密钥 |
| `BLINKFACE_SSH_*` / `BLINKFACE_REMOTE_*` | `restart.sh` | 远端重启（可选） |
| `HF_TOKEN` / `HF_HOME` | `dl.py` / 首次拉模 | Hugging Face |

已有环境变量优先于 `.env`。`.env` 已被 gitignore。

---

## 一、GPU 机器

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install torch --index-url https://download.pytorch.org/whl/cu124   # 按本机 CUDA 改
pip install -r requirements-server.txt
# 若 pip 版 diffusers 尚无 FLUX.2-klein：
pip install git+https://github.com/huggingface/diffusers.git

# 可选预下载
python dl.py

python server.py
# ready. 之后：
curl http://127.0.0.1:8000/
```

Windows 防火墙只需放行你要暴露的端口（示例 8000），不必关防火墙。

跨设备访问时：

```bash
# .env
BLINKFACE_BIND=0.0.0.0
BLINKFACE_TOKEN=请换成足够长的随机串
```

### 安全

- **不要**把 GPU 端口 DNAT / 映射到公网。
- 默认只听本机；无 `BLINKFACE_TOKEN` 时不要把 `BLINKFACE_BIND=0.0.0.0` 暴露到不可信网络。
- `web-serve.py` 会向上游注入 token：若 `BLINKFACE_WEB_BIND=0.0.0.0`，等于把免密生图入口暴露给能访问该端口的人。
- 详见 [SECURITY.md](./SECURITY.md)。

---

## 二、CLI

```bash
cp .env.example .env
# BLINKFACE_HOST=http://<gpu可达地址>:8000
# BLINKFACE_TOKEN=…   # 若服务端开了

curl "$BLINKFACE_HOST/" 

python3 gen.py "a cat holding a sign that says hello world" cat.jpg
python3 gen.py "Transform this person into a Japanese anime character..." out.jpg --img face.jpg
```

更多风格指令见 [prompts.md](./prompts.md)。

---

## 三、Web 手势取景框

```bash
python3 web-serve.py        # 默认 127.0.0.1:8080，反代到 BLINKFACE_HOST
open http://127.0.0.1:8080
```

- 浏览器只打同源 `/generate`、`/health`；token 由代理注入（浏览器不持有密钥）。
- 远程摄像头：用 HTTPS 反代（如 `tailscale serve --bg 8080`）。
- 局域网要让别人打开页面时：`BLINKFACE_WEB_BIND=0.0.0.0 python3 web-serve.py`（见上方安全说明：此举会暴露免密入口）。
- 前端默认从 jsDelivr / Google Fonts / MediaPipe CDN 加载脚本与模型；完全离线需自行镜像。

---

## 速度参考（4090 + klein 4B）

- 1024px / 4 step ≈ 1s 级  
- Web 默认 `672×384`、2 step，偏向实时预览  

---

## 目录

| 路径 | 作用 |
|------|------|
| `server.py` | GPU 生图 API |
| `gen.py` | CLI |
| `web-serve.py` + `web/` | 前端 + 同源反代 |
| `dl.py` | 稳健拉模型 |
| `restart.sh` | 可选：SSH 重启**远端 Windows GPU 主机**上的服务（PowerShell） |
| `prompts.md` | 风格提示词 |
| `envfile.py` | 读 `.env` |
| `.env.example` | 配置模板 |
| `SECURITY.md` | 安全说明 |
| `docs/` | README 预览图 |
| `README.md` | English docs |

---

## 许可

- 代码：[MIT](./LICENSE)
- 默认模型权重（[FLUX.2 [klein] 4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B)）：**Apache-2.0**
- 通过 `BLINKFACE_MODEL` 更换的其它模型：以对应模型卡为准（与本仓库代码许可分离）
