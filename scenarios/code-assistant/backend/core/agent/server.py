"""FastAPI 入口：把 agent 内核暴露为 HTTP 接口。

用法（backend/ 目录下）：
    python -m uvicorn core.agent.server:app --reload
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .boundary import Boundary
from .executor import execute
from .intent import classify_intent
from .planner import make_plan
from .trace import Trace

_AGENT_ROOT = Path(__file__).resolve().parents[3]  # 场景根 code-assistant/
_SCENARIO_PATH = _AGENT_ROOT / "scenario.json"

app = FastAPI(title="harness-agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 最近的归因链，demo 阶段存内存即可。
_recent_traces: list[dict[str, Any]] = []


def _load_scenario() -> dict[str, Any]:
    if _SCENARIO_PATH.exists():
        return json.loads(_SCENARIO_PATH.read_text(encoding="utf-8"))
    return {}


class ChatRequest(BaseModel):
    message: str
    use_llm: bool = True


@app.post("/api/chat")
def chat(req: ChatRequest) -> dict[str, Any]:
    global _recent_traces
    scenario = _load_scenario()
    intents = scenario.get("intents")
    boundary = Boundary.from_config(scenario.get("boundary"))
    boundary.allow_dirs = [str((_AGENT_ROOT / d).resolve()) for d in boundary.allow_dirs]
    llm_cfg = scenario.get("llm")

    intent = classify_intent(req.message, intents)
    plan = make_plan(
        req.message,
        intent,
        root=str(_AGENT_ROOT),
        cfg=llm_cfg,
        use_llm=req.use_llm,
    )

    trace = Trace()
    trace.add("intent", f"意图识别: {intent.name}", detail=intent.as_dict())
    trace.add("plan", f"计划编排: {plan.source}", detail=plan.as_dict())

    results = execute(plan, boundary, trace)
    trace.add("result", "执行完成", detail={"results": results})

    response = {
        "message": req.message,
        "intent": intent.as_dict(),
        "plan": plan.as_dict(),
        "results": results,
        "trace": trace.as_dict(),
    }
    _recent_traces.insert(0, trace.as_dict())
    _recent_traces = _recent_traces[:20]
    return response


@app.get("/api/trace")
def latest_trace() -> dict[str, Any]:
    return {"traces": _recent_traces}
