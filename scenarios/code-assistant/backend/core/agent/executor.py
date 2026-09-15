"""执行器：按计划逐步调用白名单工具，每步过边界并写归因链。"""
from __future__ import annotations

from typing import Any

from .boundary import Boundary, BoundaryError
from .planner import Plan, PlanStep
from .tools import TOOL_REGISTRY
from .trace import Trace


def execute(plan: Plan, boundary: Boundary, trace: Trace) -> list[dict[str, Any]]:
    """执行计划，返回每步结果。越界步骤被拒绝但记录到 trace，不中断整个链路。"""
    results: list[dict[str, Any]] = []
    for step in plan.steps:
        results.append(_execute_step(step, boundary, trace))
    return results


def _execute_step(step: PlanStep, boundary: Boundary, trace: Trace) -> dict[str, Any]:
    tool = step.tool
    trace.add("plan", f"执行步骤: {tool}", detail={"args": step.args})
    try:
        fn = TOOL_REGISTRY[tool]
        output = fn(**step.args, boundary=boundary)
        trace.add("tool", f"工具调用: {tool}", detail={"args": step.args, "output": output})
        return {"tool": tool, "status": "ok", "output": output}
    except BoundaryError as exc:
        trace.add(
            "boundary",
            f"越界拦截: {tool}",
            detail={"args": step.args, "error": str(exc)},
            status="denied",
        )
        return {"tool": tool, "status": "denied", "error": str(exc)}
    except Exception as exc:  # noqa: BLE001 - 工具执行异常需记录
        trace.add(
            "tool",
            f"工具失败: {tool}",
            detail={"args": step.args, "error": str(exc)},
            status="error",
        )
        return {"tool": tool, "status": "error", "error": str(exc)}
