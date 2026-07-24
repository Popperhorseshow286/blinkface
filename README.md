# blinkface

**Changing your face in the blink of an eye with AI.**

手势取景框 + 实时 AI 风格化。一台 CUDA GPU 跑 [FLUX.2 [klein] 4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B) 生图 API，Mac / 浏览器当遥控器：文生图、图生图，双手围框即时预览。

- **GPU 端**：`server.py`（FastAPI + diffusers）
- **CLI**：`gen.py`（纯标准库）
- **Web**：`web/` + `web-serve.py`（静态页 + 同源反代）
- **网络**：Tailscale / 局域网 / SSH 隧道均可；**仓库不含私人地址**

> **License**  
> 代码：[MIT](./LICENSE)  
> 模型：Black Forest Labs 权重，另有许可 —— 使用前阅读  
> [模型卡](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B) 与 BFL 条款（常见非商用等限制，以原文为准）。

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

- 默认只听本机；无 token 时不要把端口暴露到不可信网络。
- 详见 [SECURITY.md](./SECURITY.md)。

---

## 二、CLI（Mac / 其它）

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

- 浏览器只打同源 `/generate`、`/health`；token 由代理注入。
- 远程摄像头：用 HTTPS 反代（如 `tailscale serve --bg 8080`）。
- 局域网要让别人打开页面时：`BLINKFACE_WEB_BIND=0.0.0.0 python3 web-serve.py`

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
| `restart.sh` | SSH 重启远端服务 |
| `prompts.md` | 风格提示词 |
| `envfile.py` | 读 `.env` |
| `.env.example` | 配置模板 |
| `SECURITY.md` | 安全说明 |

---

## License

- Code: [MIT](./LICENSE)
- Model weights: Black Forest Labs / Hugging Face model license（与本仓库分离）
