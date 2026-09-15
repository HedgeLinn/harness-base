import pytest

from core.agent.boundary import Boundary, BoundaryError


def test_path_within_allow_dir() -> None:
    b = Boundary(allow_dirs=["backend/core"])
    b.check_path("backend/core/math_ops.py")


def test_path_outside_allow_dir() -> None:
    b = Boundary(allow_dirs=["backend/core"])
    with pytest.raises(BoundaryError):
        b.check_path("frontend/src/greeting.ts")


def test_command_whitelist() -> None:
    b = Boundary(allow_commands=["git", "pytest"])
    b.check_command("git status")


def test_command_denied() -> None:
    b = Boundary(allow_commands=["git"], deny_commands=["rm"])
    with pytest.raises(BoundaryError):
        b.check_command("rm -rf .")


def test_command_not_whitelisted() -> None:
    b = Boundary(allow_commands=["git"])
    with pytest.raises(BoundaryError):
        b.check_command("shutdown now")


def test_operation_not_allowed() -> None:
    b = Boundary()
    with pytest.raises(BoundaryError):
        b.check_operation("delete_file")
