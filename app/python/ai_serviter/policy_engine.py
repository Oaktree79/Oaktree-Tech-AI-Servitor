from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List
import fnmatch

from .patch_engine import ManagedEdit


@dataclass
class PolicyDecision:
    allowed: bool
    risk: str
    reasons: List[str]


class PolicyEngine:
    def __init__(self, root: str | Path, config: Dict | None = None):
        self.root = Path(root).resolve()
        self.config = config or {}
        self.allowed_paths = self.config.get("allowed_paths", ["**"])
        self.blocked_paths = self.config.get("blocked_paths", [
            ".git/**", ".serviter/secrets/**", "**/.env", "**/id_rsa", "**/id_ed25519"
        ])
        self.auto_apply_max_risk = self.config.get("auto_apply_max_risk", "low")

    def risk_for_instruction(self, instruction: str) -> str:
        lower = instruction.lower()
        if any(x in lower for x in ["auth", "secret", "credential", "payment", "delete", "deploy", "database"]):
            return "high"
        if any(x in lower for x in ["patch", "execute", "test", "code", "modify"]):
            return "medium"
        return "low"

    def path_allowed(self, path: str) -> bool:
        blocked = any(fnmatch.fnmatch(path, p) for p in self.blocked_paths)
        allowed = any(fnmatch.fnmatch(path, p) for p in self.allowed_paths)
        return allowed and not blocked

    def evaluate_edits(self, instruction: str, edits: Iterable[ManagedEdit], auto_apply: bool = False) -> Dict:
        reasons: List[str] = []
        risk = self.risk_for_instruction(instruction)

        for edit in edits:
            if not self.path_allowed(edit.path):
                reasons.append(f"Path blocked by policy: {edit.path}")

        if auto_apply and self._risk_rank(risk) > self._risk_rank(self.auto_apply_max_risk):
            reasons.append(f"Auto-apply blocked for {risk} risk task")

        return {
            "allowed": not reasons,
            "risk": risk,
            "reasons": reasons,
        }

    def _risk_rank(self, risk: str) -> int:
        return {"low": 1, "medium": 2, "high": 3}.get(risk, 3)
