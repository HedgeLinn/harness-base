from core.math_ops import add, reverse_text


def test_add() -> None:
    assert add(2, 3) == 5


def test_reverse_text() -> None:
    assert reverse_text("abc") == "cba"
