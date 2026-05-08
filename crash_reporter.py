from __future__ import annotations

from pathlib import Path
from typing import Dict
import json
import platform
import sys
import time
import traceback
import uuid


class CrashReporter:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.crash_dir = self.root / "logs" / "crashes"
        self.crash_dir.mkdir(parents=True, exist_ok=True)

    def report_exception(self, exc: BaseException, context: Dict | None = None) -> Dict:
        crash_id = str(uuid.uuid4())
        payload = {
            "id": crash_id,
            "created_at": time.time(),
            "python": sys.version,
            "platform": platform.platform(),
            "exception_type": exc.__class__.__name__,
            "exception": str(exc),
            "traceback": traceback.format_exc(),
            "context": context or {},
        }
        path = self.crash_dir / f"{crash_id}.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return {"crash_id": crash_id, "path": str(path)}

    def list_reports(self):
        return sorted(str(p) for p in self.crash_dir.glob("*.json"))
