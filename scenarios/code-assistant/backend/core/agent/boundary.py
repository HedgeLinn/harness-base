"""边界校验：操作白名单 + 资源白名单。

demo 阶段用「配置 + 校验层」实现：执行任何工具调用前，先检查操作是否被允许、
目标资源（目录 / 命令 / 文件扩展名）是否在白名单内。越界抛 BoundaryError 并交由
executor 记录到归因链，而不是真正做进程级隔离。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class BoundaryError(Exception):
    """越界异常：表示某次工具调用超出了白名单允许的范围。"""


@dataclass
class Boundary:
    allow_dirs: list[str] = field(default_factory=list)
    allow_commands: list[str] = field(default_factory=list)
    allow_extensions: list[str] = field(default_factory=list)
    deny_commands: list[str] = field(default_factory=list)

    @classmethod
    def from_config(cls, cfg: dict[str, Any] | None) -> "Boundary":
        cfg = cfg or {}
        return cls(
            allow_dirs=list(cfg.get("allow_dirs", [])),
            allow_commands=list(cfg.get("allow_commands", [])),
            allow_extensions=list(cfg.get("allow_extensions", [])),
            deny_commands=list(cfg.get("deny_commands", [])),
        )

    def check_operation(self, tool_name: str) -> None:
        """操作白名单：工具名必须在允许的操作集合里。"""
        allowed = {"read_file", "list_dir", "run_cmd", "search"}
        if tool_name not in allowed:
            raise BoundaryError(f"操作未授权: {tool_name}")

    def check_path(self, path: str | Path) -> None:
        """资源白名单：路径必须落在某个允许目录内。"""
        if not self.allow_dirs:
            return
        target = Path(path).resolve()
        for d in self.allow_dirs:
            base = Path(d).resolve()
            try:
                target.relative_to(base)
                return
            except ValueError:
                continue
        raise BoundaryError(f"路径越界: {path}")

    def check_extension(self, path: str | Path) -> None:
        """资源白名单：文件扩展名必须在允许列表内（allow_extensions 为空则不限制）。"""
        if not self.allow_extensions:
            return
        suffix = Path(path).suffix.lower()
        if suffix not in self.allow_extensions:
            raise BoundaryError(f"文件类型不允许: {path}")

    def check_command(self, command: str) -> None:
        """资源白名单：命令必须命中 allow_commands 之一，且不在 deny_commands 内。"""
        tokens = command.split()
        if not tokens:
            raise BoundaryError("空命令")
        if tokens[0] in self.deny_commands:
            raise BoundaryError(f"命令被禁止: {tokens[0]}")
        if not self.allow_commands:
            raise BoundaryError("未配置命令白名单")
        if tokens[0] not in self.allow_commands:
            raise BoundaryError(f"命令未授权: {tokens[0]}")
