from __future__ import annotations

from pathlib import Path
from typing import Dict

from .agent_loop import ClosedLoopCodingAgent


class SelfCorrectionLoop:
    """
    Thin wrapper around ClosedLoopCodingAgent for explicit repair requests.
    """

    def __init__(self, root: str | Path, max_attempts: int = 3):
        self.agent = ClosedLoopCodingAgent(root, max_attempts=max_attempts)

    def repair(self, instruction: str, failing_output: Dict, auto_apply: bool = False) -> Dict:
        return self.agent.run(
            instruction=f"Repair failing task: {instruction}",
            context={"failing_output": failing_output},
            auto_apply=auto_apply,
        )
