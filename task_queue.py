from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Optional
import json
import time
import uuid

from .database import ServiterDatabase


VALID_TRANSITIONS = {
    "queued": {"waiting_approval", "running", "cancelled"},
    "waiting_approval": {"approved", "rejected", "cancelled"},
    "approved": {"running", "cancelled"},
    "running": {"succeeded", "failed", "cancelled"},
    "succeeded": set(),
    "failed": {"queued"},
    "rejected": set(),
    "cancelled": set(),
}


@dataclass
class TaskRecord:
    id: str
    instruction: str
    status: str
    priority: int
    requires_approval: bool
    approval_status: str
    result: Dict | None
    error: str | None
    created_at: float
    updated_at: float


class TaskQueue:
    def __init__(self, db: ServiterDatabase):
        self.db = db

    def submit(self, instruction: str, priority: int = 100, requires_approval: bool = True) -> TaskRecord:
        now = time.time()
        task_id = str(uuid.uuid4())
        status = "waiting_approval" if requires_approval else "queued"
        approval_status = "pending" if requires_approval else "approved"

        self.db.execute(
            """
            INSERT INTO tasks(id,instruction,status,priority,requires_approval,approval_status,created_at,updated_at)
            VALUES(?,?,?,?,?,?,?,?)
            """,
            (task_id, instruction, status, priority, int(requires_approval), approval_status, now, now),
        )
        self.db.add_event(task_id, "task_submitted", {"instruction": instruction, "requires_approval": requires_approval})
        return self.get(task_id)

    def transition(self, task_id: str, new_status: str, result: Dict | None = None, error: str | None = None):
        task = self.get(task_id)
        if new_status not in VALID_TRANSITIONS.get(task.status, set()):
            raise ValueError(f"Invalid transition {task.status} -> {new_status}")

        self.db.execute(
            "UPDATE tasks SET status=?, result_json=?, error=?, updated_at=? WHERE id=?",
            (new_status, json.dumps(result) if result is not None else None, error, time.time(), task_id),
        )
        self.db.add_event(task_id, "task_transition", {"from": task.status, "to": new_status})

    def next_runnable(self) -> Optional[TaskRecord]:
        rows = self.db.query(
            """
            SELECT * FROM tasks
            WHERE status='queued' OR status='approved'
            ORDER BY priority ASC, created_at ASC
            LIMIT 1
            """
        )
        return self._row_to_record(rows[0]) if rows else None

    def get(self, task_id: str) -> TaskRecord:
        rows = self.db.query("SELECT * FROM tasks WHERE id=?", (task_id,))
        if not rows:
            raise KeyError(f"Task not found: {task_id}")
        return self._row_to_record(rows[0])

    def list(self, limit: int = 50):
        rows = self.db.query("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,))
        return [self._row_to_record(r) for r in rows]

    def _row_to_record(self, row: Dict) -> TaskRecord:
        return TaskRecord(
            id=row["id"],
            instruction=row["instruction"],
            status=row["status"],
            priority=row["priority"],
            requires_approval=bool(row["requires_approval"]),
            approval_status=row["approval_status"],
            result=json.loads(row["result_json"]) if row.get("result_json") else None,
            error=row.get("error"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
