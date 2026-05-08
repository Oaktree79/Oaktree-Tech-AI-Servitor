from __future__ import annotations

from pathlib import Path
from typing import Dict

from .database import ServiterDatabase


class OverrideControls:
    def __init__(self, db: ServiterDatabase, root: str | Path = "."):
        self.db = db
        self.root = Path(root).resolve()
        self.pause_file = self.root / ".serviter" / "PAUSED"

    def pause(self, reason: str = "") -> Dict:
        self.pause_file.parent.mkdir(parents=True, exist_ok=True)
        self.pause_file.write_text(reason or "paused", encoding="utf-8")
        self.db.add_event(None, "system_paused", {"reason": reason})
        return {"paused": True, "reason": reason}

    def resume(self) -> Dict:
        if self.pause_file.exists():
            self.pause_file.unlink()
        self.db.add_event(None, "system_resumed", {})
        return {"paused": False}

    def is_paused(self) -> bool:
        return self.pause_file.exists()

    def cancel_task(self, task_id: str) -> Dict:
        self.db.execute("UPDATE tasks SET status='cancelled' WHERE id=?", (task_id,))
        self.db.add_event(task_id, "task_cancelled", {})
        return {"task_id": task_id, "status": "cancelled"}
