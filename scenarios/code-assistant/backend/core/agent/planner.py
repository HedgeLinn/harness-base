"""计划编排：LLM 生成分步计划，失败时降级为规则计划。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from . import llm
from .intent import Intent


@dataclass
class PlanStep:
    tool: str
    args: dict[str, Any]
    note: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {"tool": self.tool, "args": self.args, "note": self.note}


@dataclass
class Plan:
    intent: Intent
    steps: list[PlanStep] = field(default_factory=list)
    source: str = "llm"  # llm / fallback

    def as_dict(self) -> dict[str, Any]:
        return {
            "intent": self.intent.as_dict(),
            "source": self.source,
            "steps": [s.as_dict() for s in self.steps],
        }


def _fallback_plan(text: str, intent: Intent, root: str) -> Plan:
    """规则兜底计划：根据意图生成一到两步简单计划。"""
    steps: list[PlanStep] = []
    if intent.name == "file":
        if "列" in text or "list" in text.lower() or "ls" in text.lower():
            steps.append(PlanStep(tool="list_dir", args={"path": root}))
        else:
            steps.append(PlanStep(tool="read_file", args={"path": f"{root}/AGENTS.md"}))
    elif intent.name == "command":
        steps.append(PlanStep(tool="run_cmd", args={"command": "git status", "cwd": root}))
    elif intent.name == "search":
        steps.append(PlanStep(tool="search", args={"keyword": text, "path": root}))
    else:
        steps.append(PlanStep(tool="read_file", args={"path": f"{root}/README.md"}))
    return Plan(intent=intent, steps=steps, source="fallback")


def make_plan(
    text: str,
    intent: Intent,
    *,
    root: str,
    cfg: dict[str, Any] | None = None,
    use_llm: bool = True,
) -> Plan:
    """生成执行计划。LLM 可用则让 LLM 规划，否则走规则兜底。"""
    if use_llm:
        try:
            prompt = (
                "你是代码仓库助手的规划器。用户意图已识别为："
                f"{intent.name}（置信度 {intent.confidence:.2f}）。\n"
                f"用户输入：{text}\n"
                f"可用工具：read_file(path)、list_dir(path)、run_cmd(command, cwd)、search(keyword, path)。\n"
                "只输出 JSON 数组，每个元素形如 {\"tool\": \"...\", \"args\": {...}}，"
                "不要输出任何解释。"
            )
            raw = llm.chat(
                [{"role": "user", "content": prompt}],
                cfg,
            )
            steps = _parse_steps(raw)
            if steps:
                return Plan(intent=intent, steps=steps, source="llm")
        except Exception:
            pass
    return _fallback_plan(text, intent, root)


def _parse_steps(raw: str) -> list[PlanStep]:
    import json
    import re

    m = re.search(r"\[[\s\S]*\]", raw)
    if not m:
        return []
    data = json.loads(m.group(0))
    steps: list[PlanStep] = []
    for item in data:
        if not isinstance(item, dict) or "tool" not in item:
            continue
        steps.append(
            PlanStep(tool=item["tool"], args=item.get("args", {}), note=item.get("note", ""))
        )
    return steps
