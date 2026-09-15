"""白名单工具集：agent 可执行的受限操作。

每个工具都接收 boundary 并在实际操作前做校验，越界抛 BoundaryError。
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ..boundary import Boundary


def read_file(path: str, boundary: Boundary) -> str:
    boundary.check_operation("read_file")
    boundary.check_path(path)
    boundary.check_extension(path)
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"文件不存在: {path}")
    return p.read_text(encoding="utf-8", errors="replace")


def list_dir(path: str, boundary: Boundary) -> list[str]:
    boundary.check_operation("list_dir")
    boundary.check_path(path)
    p = Path(path)
    if not p.is_dir():
        raise NotADirectoryError(f"目录不存在: {path}")
    return sorted(entry.name for entry in p.iterdir())


def run_cmd(command: str, cwd: str, boundary: Boundary) -> str:
    import subprocess

    boundary.check_operation("run_cmd")
    boundary.check_command(command)
    boundary.check_path(cwd)
    completed = subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return (completed.stdout or "") + (completed.stderr or "")


def search(keyword: str, path: str, boundary: Boundary) -> list[str]:
    boundary.check_operation("search")
    boundary.check_path(path)
    base = Path(path)
    if not base.is_dir():
        raise NotADirectoryError(f"目录不存在: {path}")
    hits: list[str] = []
    for entry in sorted(base.rglob("*")):
        if not entry.is_file():
            continue
        try:
            text = entry.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if keyword.lower() in text.lower():
            hits.append(str(entry.relative_to(base)))
    return hits


TOOL_REGISTRY: dict[str, Any] = {
    "read_file": read_file,
    "list_dir": list_dir,
    "run_cmd": run_cmd,
    "search": search,
}
