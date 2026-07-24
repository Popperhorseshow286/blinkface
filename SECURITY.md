# Security

## 威胁模型

blinkface 的 GPU API **默认无强隔离**，定位是：个人 / 小团队在受信网络里遥控本机或局域网显卡。

## 默认安全点

- `BLINKFACE_BIND` 默认 `127.0.0.1`（不进局域网）
- 可选 `BLINKFACE_TOKEN`：开启后 `/generate` 需要 `Authorization: Bearer …`
- `web-serve.py` 可注入 token，浏览器端不驻留密钥
- `width` / `height` / `steps` 有服务器端上限，体积过大的 POST 会被代理拒绝

## 不要做的事

- 不要把 GPU 端口直接 DNAT / 映射到公网
- 不要在未设 `BLINKFACE_TOKEN` 时把 `BLINKFACE_BIND=0.0.0.0` 暴露到不可信网络
- 不要把 `.env`、含真实 IP 的截图、或带 token 的日志提交到 git

## 报告漏洞

若发现可在默认配置下被未授权远程利用的问题，请通过 GitHub Security Advisory 或维护者邮箱私下联系，不要公开 issue 贴 exploit。
