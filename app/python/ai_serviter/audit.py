from __future__ import annotations

from typing import Dict

from .database import ServiterDatabase


class AuditLog:
    def __init__(self, db: ServiterDatabase):
        self.db = db

    def record(self, actor: str, action: str, payload: Dict | None = None, task_id: str | None = None):
        data = {"actor": actor, "action": action, **(payload or {})}
        self.db.add_event(task_id, "audit", data)

    def recent(self, limit: int = 100):
        return self.db.query("SELECT * FROM events ORDER BY created_at DESC LIMIT ?", (limit,))
