from __future__ import annotations

from pathlib import Path
from typing import Dict

from .agent_loop import ClosedLoopCodingAgent
from .approval import ApprovalManager, ApprovalPolicy
from .auto_patcher import AutoPatcher
from .database import ServiterDatabase
from .git_integration import GitIntegration
from .override import OverrideControls
from .serviter import AIServiter
from .task_queue import TaskQueue
from .test_runner import TestRunner


class ServiterRuntime:
    def __init__(self, root: str | Path = ".", db_path: str | None = None):
        self.root = Path(root).resolve()
        self.db = ServiterDatabase(db_path or (self.root / ".serviter" / "serviter.db"))
        self.queue = TaskQueue(self.db)
        self.policy = ApprovalPolicy()
        self.approvals = ApprovalManager(self.db, self.queue)
        self.serviter = AIServiter(self.root)
        self.tests = TestRunner(self.root)
        self.patcher = AutoPatcher(self.root)
        self.agent = ClosedLoopCodingAgent(self.root)
        self.overrides = OverrideControls(self.db, self.root)
        self.git = GitIntegration(self.root)

    def submit(self, instruction: str, priority: int = 100):
        needs_approval = self.policy.requires_approval(instruction)
        return self.queue.submit(instruction, priority=priority, requires_approval=needs_approval)

    def run_once(self) -> Dict:
        if self.overrides.is_paused():
            return {"status": "paused"}

        task = self.queue.next_runnable()
        if not task:
            return {"status": "idle"}

        self.queue.transition(task.id, "running")
        try:
            result = self.fulfill(task.instruction)
            self.queue.transition(task.id, "succeeded", result=result)
            return {"status": "succeeded", "task_id": task.id, "result": result}
        except Exception as exc:
            self.queue.transition(task.id, "failed", error=str(exc))
            return {"status": "failed", "task_id": task.id, "error": str(exc)}

    def fulfill(self, instruction: str) -> Dict:
        lower = instruction.lower()
        if lower.startswith("analyze") or "analyze" in lower:
            return self.serviter.analyze()
        if lower.startswith("plan") or "plan" in lower:
            return self.serviter.plan(instruction)
        if "closed-loop" in lower or "autonomous edit" in lower:
            return self.agent.run(instruction, auto_apply=False)
        if "propose" in lower or "patch" in lower or "code" in lower:
            return self.serviter.propose(instruction)
        if "test" in lower:
            return self.tests.run()
        if "git status" in lower:
            return self.git.status()
        return self.serviter.plan(instruction)
