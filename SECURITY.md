# Security

## 威胁模型

blinkface 的 GPU API **默认无强隔离**，定位是：个人 / 小团队在受信网络里遥控本机或局域网显卡。  
它不是多租户公网推理服务；摄像头画面会发到你自己配置的 GPU 端做推理。

## 默认安全点

- `BLINKFACE_BIND` 默认 `127.0.0.1`（不进局域网）
- 可选 `BLINKFACE_TOKEN`：开启后 `/generate` 需要 `Authorization: Bearer …` 或 `X-Blinkface-Token`
- Token 使用 `secrets.compare_digest` 比较
- `web-serve.py` 可注入 token，浏览器端不驻留密钥
- `width` / `height` / `steps` 有服务器端上限
- 输入图：服务端限制 base64 长度与解码后字节数；`web-serve.py` 拒绝过大 POST body（默认 25MB）

## 不要做的事

- 不要把 GPU 端口直接 DNAT / 映射到公网
- 不要在未设 `BLINKFACE_TOKEN` 时把 `BLINKFACE_BIND=0.0.0.0` 暴露到不可信网络
- 不要在不可信网络把 `BLINKFACE_WEB_BIND=0.0.0.0` 当作“已鉴权”：代理会代填 token，访达该端口的人等于免密调用 GPU
- 不要把 `.env`、含真实 IP 的截图、或带 token 的日志提交到 git

## 报告漏洞

若发现可在**默认配置**下被未授权远程利用的问题，请优先使用 GitHub Security Advisory（private vulnerability report）私下联系，不要公开 issue 贴 exploit。

维护者：仓库 Issues / Security 入口（GitHub）。若 Advisory 不可用，可通过 GitHub 上本仓库维护者资料中的公开联系方式私信，并在标题标明 `SECURITY`。
