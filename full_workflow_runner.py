from __future__ import annotations

from pathlib import Path
from typing import Dict

from .runtime import ServiterRuntime
from .git_integration import GitIntegration


class FullWorkflowRunner:
    """
    Runs a complete local workflow:
    submit -> approve if needed -> worker -> optional git status.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.runtime = ServiterRuntime(self.root)

    def run(self, instruction: str, approve: bool = True) -> Dict:
        task = self.runtime.submit(instruction)
        approved = None

        if task.requires_approval and approve:
            self.runtime.approvals.approve(task.id, approved_by="workflow-runner", reason="automated test workflow")
            approved = self.runtime.queue.get(task.id).__dict__

        worker = self.runtime.run_once()
        git_status = GitIntegration(self.root).status()

        return {
            "submitted": task.__dict__,
            "approved": approved,
            "worker": worker,
            "git_status": git_status,
            "ok": worker.get("status") in {"succeeded", "idle"},
        }
