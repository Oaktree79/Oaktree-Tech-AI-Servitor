from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List
import json


@dataclass
class CodingTask:
    title: str
    goal: str
    files_to_inspect: List[str]
    files_to_modify: List[str]
    test_command: str
    risk_level: str
    steps: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


class CodingTaskPlanner:
    """
    Deterministic planning layer for an AI coding assistant.

    This planner does not call an external model. It creates a reliable baseline plan
    that can be passed to an LLM, a human engineer, or an automated patch module.
    """

    def plan(self, request: str, matrix_summary: Dict, symbol_hits: List[Dict]) -> CodingTask:
        request_lower = request.lower()

        files_to_inspect = sorted({hit["path"] for hit in symbol_hits})[:10]
        files_to_modify: List[str] = []

        if "test" in request_lower:
            files_to_modify.append("tests/")
        if "plugin" in request_lower or "module" in request_lower:
            files_to_modify.append("plugins/")
        if "api" in request_lower:
            files_to_modify.append("src/api/")

        if not files_to_modify:
            files_to_modify = files_to_inspect[:3] or ["<new-file-to-be-created>"]

        risk = "medium"
        if any(word in request_lower for word in ["security", "auth", "payment", "database", "delete"]):
            risk = "high"
        elif any(word in request_lower for word in ["readme", "docs", "comment"]):
            risk = "low"

        test_command = "python -m pytest -q"
        languages = matrix_summary.get("languages", {})
        if "typescript" in languages and "python" not in languages:
            test_command = "npm test"

        return CodingTask(
            title=self._title(request),
            goal=request,
            files_to_inspect=files_to_inspect,
            files_to_modify=files_to_modify,
            test_command=test_command,
            risk_level=risk,
            steps=[
                "Scan filesystem matrix and identify affected files.",
                "Inspect matching symbols and nearby tests.",
                "Create minimal patch that satisfies the request.",
                "Run formatter, static checks, and tests.",
                "Run security scan before finalizing.",
            ],
        )

    def _title(self, request: str) -> str:
        clean = " ".join(request.strip().split())
        return clean[:80] or "Untitled coding task"

    def to_json(self, task: CodingTask) -> str:
        return json.dumps(task.to_dict(), indent=2)
