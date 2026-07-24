"""极简 .env 加载：不覆盖已有环境变量；无第三方依赖。"""
from __future__ import annotations

import os
from pathlib import Path


def load_env(path: str | os.PathLike[str] | None = None) -> None:
    p = Path(path) if path else Path(__file__).resolve().parent / ".env"
    try:
        text = p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.lower().startswith("export "):
            line = line[7:].strip()
        key, _, val = line.partition("=")
        key = key.strip()
        if not key:
            continue
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        os.environ.setdefault(key, val)
