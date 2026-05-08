from __future__ import annotations

import time
from .database import ServiterDatabase
from .task_queue import TaskQueue


class ApprovalPolicy:
    """
    Simple policy:
    - read-only analysis can run without approval
    - patch, execute, delete, auth, database, deploy need approval
    """

    high_risk_terms = {"patch", "apply", "delete", "remove", "execute", "shell", "database", "auth", "deploy", "rollback"}

    def requires_approval(self, instruction: str) -> bool:
        lower = instruction.lower()
        return any(term in lower for term in self.high_risk_terms)


class ApprovalManager:
    def __init__(self, db: ServiterDatabase, queue: TaskQueue):
        self.db = db
        self.queue = queue

    def approve(self, task_id: str, approved_by: str = "local-admin", reason: str = ""):
        now = time.time()
        self.db.execute(
            """
            INSERT INTO approvals(task_id,approved_by,approved_at,status,reason)
            VALUES(?,?,?,?,?)
            ON CONFLICT(task_id) DO UPDATE SET
              approved_by=excluded.approved_by,
              approved_at=excluded.approved_at,
              status=excluded.status,
              reason=excluded.reason
            """,
            (task_id, approved_by, now, "approved", reason),
        )
        self.db.execute(
            "UPDATE tasks SET approval_status='approved', status='approved', updated_at=? WHERE id=?",
            (now, task_id),
        )
        self.db.add_event(task_id, "task_approved", {"approved_by": approved_by, "reason": reason})

    def reject(self, task_id: str, rejected_by: str = "local-admin", reason: str = ""):
        now = time.time()
        self.db.execute(
            """
            INSERT INTO approvals(task_id,approved_by,approved_at,status,reason)
            VALUES(?,?,?,?,?)
            ON CONFLICT(task_id) DO UPDATE SET
              approved_by=excluded.approved_by,
              approved_at=excluded.approved_at,
              status=excluded.status,
              reason=excluded.reason
            """,
            (task_id, rejected_by, now, "rejected", reason),
        )
        self.db.execute(
            "UPDATE tasks SET approval_status='rejected', status='rejected', updated_at=? WHERE id=?",
            (now, task_id),
        )
        self.db.add_event(task_id, "task_rejected", {"rejected_by": rejected_by, "reason": reason})
