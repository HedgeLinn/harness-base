from core.agent.trace import Trace


def test_trace_serializes() -> None:
    trace = Trace()
    trace.add("intent", "意图识别", detail={"name": "file"})
    trace.add("boundary", "越界拦截", status="denied")
    data = trace.as_dict()
    assert data["id"]
    assert len(data["steps"]) == 2
    assert data["steps"][1]["status"] == "denied"
