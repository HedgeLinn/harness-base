from core.agent.intent import classify_intent


def test_command_intent() -> None:
    intent = classify_intent("运行 git status 看看")
    assert intent.name == "command"


def test_file_intent() -> None:
    intent = classify_intent("读取 core/math_ops.py 的内容")
    assert intent.name == "file"


def test_search_intent() -> None:
    intent = classify_intent("搜索 add 函数")
    assert intent.name == "search"


def test_chat_fallback() -> None:
    intent = classify_intent("你好，介绍一下你自己")
    assert intent.name == "chat"
