"""意图识别：基于规则的关键词分流。

第一层意图识别，不调用 LLM。把用户输入归类为 file / command / search / chat 四类之一，
后续计划编排与执行都依赖这个分类。规则来自场景配置的 intents 表。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Intent:
    name: str
    confidence: float
    matched: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "confidence": self.confidence,
            "matched": list(self.matched),
        }


DEFAULT_INTENTS: dict[str, dict[str, Any]] = {
    "command": {"keywords": ["运行", "run", "执行", "git", "npm", "pytest", "python", "命令", "构建", "测试"]},
    "file": {"keywords": ["读取", "read", "打开", "看", "cat", "内容", "文件", "列出", "list"]},
    "search": {"keywords": ["搜索", "search", "查找", "grep", "找", "检索"]},
    "chat": {"keywords": []},
}


def classify_intent(
    text: str,
    intents: dict[str, dict[str, Any]] | None = None,
    *,
    default: str = "chat",
) -> Intent:
    """按关键词命中数把文本归类到某个意图。

    command 优先级最高（避免"运行 git 命令"落到 file），其次 file、search；
    都未命中则回落到 default（通常是 chat）。
    """
    table = intents if intents is not None else DEFAULT_INTENTS
    lowered = text.lower()

    priority = ["command", "file", "search"]
    best: Intent | None = None

    for name in priority:
        keywords = table.get(name, {}).get("keywords", [])
        matched = tuple(k for k in keywords if k.lower() in lowered)
        if matched:
            confidence = min(1.0, 0.5 + 0.1 * len(matched))
            best = Intent(name=name, confidence=confidence, matched=matched)
            break

    if best is not None:
        return best
    return Intent(name=default, confidence=0.5, matched=())
