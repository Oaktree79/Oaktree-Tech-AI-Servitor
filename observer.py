from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import time

from .runtime import ServiterRuntime


class FileObserver:
    """
    Polling observer that watches file mtimes and submits tasks when changes occur.
    """

    def __init__(self, root: str | Path, runtime: ServiterRuntime, interval_seconds: float = 2.0):
        self.root = Path(root).resolve()
        self.runtime = runtime
        self.interval_seconds = interval_seconds
        self.snapshot: Dict[str, float] = {}

    def take_snapshot(self) -> Dict[str, float]:
        snap = {}
        for path in self.root.rglob("*"):
            if path.is_dir():
                continue
            if any(part in {".git", ".serviter", ".venv", "venv", "node_modules", "__pycache__"} for part in path.parts):
                continue
            try:
                snap[str(path.relative_to(self.root))] = path.stat().st_mtime
            except OSError:
                pass
        return snap

    def changed_files(self) -> List[str]:
        current = self.take_snapshot()
        changes = [p for p, m in current.items() if self.snapshot.get(p) != m]
        self.snapshot = current
        return changes

    def watch(self):
        self.snapshot = self.take_snapshot()
        print("FileObserver running. Press Ctrl+C to stop.")
        try:
            while True:
                changes = self.changed_files()
                if changes:
                    instruction = f"analyze changed files: {', '.join(changes[:10])}"
                    task = self.runtime.submit(instruction, priority=50)
                    print(f"submitted observer task {task.id}")
                time.sleep(self.interval_seconds)
        except KeyboardInterrupt:
            print("FileObserver stopped.")
