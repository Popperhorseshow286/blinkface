#!/bin/sh
# 清理 + 重启远端 blinkface GPU 服务。: sh restart.sh
# 配置来自环境变量或同目录 .env（见 .env.example）。不开机自启。
set -e
cd "$(dirname "$0")"

if [ -f .env ]; then
  # shellcheck disable=SC1091
  set -a
  . ./.env
  set +a
fi

SSH_HOST="${BLINKFACE_SSH_HOST:-}"
REMOTE_DIR="${BLINKFACE_REMOTE_DIR:-}"
REMOTE_PY="${BLINKFACE_REMOTE_PYTHON:-}"
REMOTE_HF="${BLINKFACE_REMOTE_HF_HOME:-}"
HOST="${BLINKFACE_HOST:-http://127.0.0.1:8000}"

missing=
[ -n "$SSH_HOST" ] || missing="$missing BLINKFACE_SSH_HOST"
[ -n "$REMOTE_DIR" ] || missing="$missing BLINKFACE_REMOTE_DIR"
[ -n "$REMOTE_PY" ] || missing="$missing BLINKFACE_REMOTE_PYTHON"
[ -n "$REMOTE_HF" ] || missing="$missing BLINKFACE_REMOTE_HF_HOME"
if [ -n "$missing" ]; then
  echo "缺少远端配置:$missing" >&2
  echo "请复制 .env.example → .env 并填写，或 export 这些变量。" >&2
  exit 1
fi

# Windows 路径在远程 PowerShell 里用反斜杠更稳
win_path() { printf '%s' "$1" | sed 's|/|\\|g'; }

REMOTE_DIR_WIN=$(win_path "$REMOTE_DIR")
REMOTE_PY_WIN=$(win_path "$REMOTE_PY")
REMOTE_HF_WIN=$(win_path "$REMOTE_HF")
SERVER_PY_WIN=$(win_path "$REMOTE_DIR/server.py")

echo "① 清理残留 python + 释放显存…"
ssh "$SSH_HOST" "Get-Process python -EA SilentlyContinue | Where-Object {\$_.Path -like '${REMOTE_DIR_WIN}*'} | Stop-Process -Force; Start-Sleep 2; 'GPU: '+(nvidia-smi --query-gpu=memory.used --format=csv,noheader)"

echo "② 启动服务(后台)…"
nohup ssh "$SSH_HOST" "\$env:HF_HOME='${REMOTE_HF_WIN}'; \$env:HF_HUB_OFFLINE='1'; & '${REMOTE_PY_WIN}' -u '${SERVER_PY_WIN}'" \
  >/tmp/blinkface-srv.log 2>&1 &

echo "③ 约 1 分钟后就绪。检查: curl -s ${HOST%/}/"
