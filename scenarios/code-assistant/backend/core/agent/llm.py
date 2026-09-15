"""LLM 客户端：走 new-api.mypy.cn，默认 deepseek-v4-pro，关闭思考模式。"""
from __future__ import annotations

import os
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "url": "http://new-api.mypy.cn/v1/chat/completions",
    "api_key": "",
    "model": "deepseek-v4-pro",
}


def build_config(cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    config = dict(DEFAULT_CONFIG)
    if cfg:
        config.update(cfg)
    config["api_key"] = os.environ.get("AGENT_LLM_API_KEY", config["api_key"])
    config["model"] = os.environ.get("AGENT_LLM_MODEL", config["model"])
    return config


def chat(messages: list[dict[str, str]], cfg: dict[str, Any] | None = None) -> str:
    """调用 LLM 补全，返回助手文本。失败抛异常，由 planner 降级兜底。"""
    import json
    import urllib.error
    import urllib.request

    config = build_config(cfg)
    payload = {
        "model": config["model"],
        "messages": messages,
        "extra_body": {"thinking": {"type": "disabled"}},
    }
    req = urllib.request.Request(
        config["url"],
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['api_key']}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]
