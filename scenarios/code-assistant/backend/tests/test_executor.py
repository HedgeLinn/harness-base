from core.agent.boundary import Boundary
from core.agent.executor import execute
from core.agent.intent import classify_intent
from core.agent.planner import Plan, PlanStep, make_plan
from core.agent.trace import Trace


def test_execute_list_dir_within_boundary() -> None:
    intent = classify_intent("列出 core 下的文件")
    plan = make_plan("列出 core 下的文件", intent, root=".", use_llm=False)
    # 覆盖为确定性步骤（测试 cwd 为 backend/，路径相对该目录）
    plan.steps = [PlanStep(tool="list_dir", args={"path": "core"})]
    trace = Trace()
    results = execute(plan, Boundary(allow_dirs=["core"]), trace)
    assert results[0]["status"] == "ok"
    assert "agent" in results[0]["output"]


def test_execute_denied_on_boundary() -> None:
    plan = Plan(
        intent=classify_intent("读取前端文件"),
        steps=[PlanStep(tool="read_file", args={"path": "core/math_ops.py"})],
    )
    trace = Trace()
    results = execute(plan, Boundary(allow_dirs=["frontend"]), trace)
    assert results[0]["status"] == "denied"
    assert any(s.status == "denied" for s in trace.steps)
