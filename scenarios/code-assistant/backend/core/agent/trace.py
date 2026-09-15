"""归因审计：记录 agent 执行全链路的每一步。"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Step:
    kind: str  # intent / plan / tool / boundary / result
    label: str
    detail: dict[str, Any] = field(default_factory=dict)
    status: str = "ok"  # ok / denied / error
    ts: float = field(default_factory=time.time)

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "label": self.label,
            "detail": self.detail,
            "status": self.status,
            "ts": self.ts,
        }


@dataclass
class Trace:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    steps: list[Step] = field(default_factory=list)

    def add(
        self,
        kind: str,
        label: str,
        *,
        detail: dict[str, Any] | None = None,
        status: str = "ok",
    ) -> Step:
        step = Step(kind=kind, label=label, detail=detail or {}, status=status)
        self.steps.append(step)
        return step

    def as_dict(self) -> dict[str, Any]:
        return {"id": self.id, "steps": [s.as_dict() for s in self.steps]}
